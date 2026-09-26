"""Experimental v1.2 action expert, separate from the frozen general MSO route.

Inputs are detached visual/language features and normalized proprioception.
Continuous commands use a mixture over entire action chunks: selecting one
component avoids averaging mutually exclusive trajectories. Mixture weights and
standard deviations are model outputs, not calibrated safety guarantees.
"""
from dataclasses import asdict, dataclass
import math

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(frozen=True)
class ActionSpace:
    name: str
    dimensions: tuple[str, ...]
    low: tuple[float, ...]
    high: tuple[float, ...]
    control_hz: float
    horizon: int = 4
    units: str = "normalized simulator command"

    def __post_init__(self):
        if not self.name or "." in self.name:
            raise ValueError("Action-space names must be nonempty and contain no dots")
        if not self.dimensions or len(self.low) != len(self.dimensions) or len(self.high) != len(self.low):
            raise ValueError("Every action dimension needs explicit bounds")
        if any(not math.isfinite(a) or not math.isfinite(b) or a >= b for a, b in zip(self.low, self.high)):
            raise ValueError("Action bounds must be finite and increasing")
        if self.horizon < 1 or not math.isfinite(self.control_hz) or self.control_hz <= 0:
            raise ValueError("Positive horizon and control frequency required")

    def metadata(self):
        return asdict(self)


class ChunkMixture(nn.Module):
    def __init__(self, hidden, space: ActionSpace, components=5):
        super().__init__()
        if components < 1:
            raise ValueError("At least one mixture component is required")
        self.space, self.components = space, components
        self.proj = nn.Linear(hidden, components * (1 + 2 * space.horizon * len(space.dimensions)))
        self.register_buffer("low", torch.tensor(space.low, dtype=torch.float32))
        self.register_buffer("high", torch.tensor(space.high, dtype=torch.float32))

    def forward(self, x):
        b, k, h, d = x.shape[0], self.components, self.space.horizon, len(self.space.dimensions)
        raw = self.proj(x).float().reshape(b, k, 1 + 2 * h * d)
        means = raw[:, :, 1:1 + h * d].reshape(b, k, h, d).tanh()
        log_std = raw[:, :, 1 + h * d:].reshape(b, k, h, d).clamp(-4.0, 1.0)
        return {"logits": raw[:, :, 0], "means": means, "log_std": log_std}

    def command(self, prediction):
        component = prediction["logits"].argmax(-1)
        normalized = prediction["means"][torch.arange(len(component), device=component.device), component]
        return self.low + (normalized + 1) * 0.5 * (self.high - self.low)


def chunk_nll(prediction, normalized_target, mask):
    """Joint diagonal Gaussian mixture likelihood with explicit time/dimension masks.

    Each batch item must contain at least one valid target. Padding values may be
    arbitrary, including NaN, because masking happens before arithmetic. Loss is
    normalized by the number of valid scalar targets after marginalizing modes.
    """
    mu, ls = prediction["means"], prediction["log_std"]
    y = normalized_target.float()
    if y.shape != mu.shape[:1] + mu.shape[2:]:
        raise ValueError("Target must have shape [batch, horizon, dimensions]")
    mask = mask.bool()
    if mask.shape == y.shape[:2]:
        mask = mask.unsqueeze(-1).expand_as(y)
    if mask.shape != y.shape or not mask.reshape(len(y), -1).any(-1).all():
        raise ValueError("Every example needs a correctly shaped nonempty mask")
    if not torch.isfinite(y[mask]).all() or (y[mask].abs() > 1.00001).any():
        raise ValueError("Valid targets must be finite and normalized to [-1, 1]")
    y = torch.where(mask, y, torch.zeros_like(y))
    terms = -0.5 * ((y[:, None] - mu) * (-ls).exp()).square() - ls - 0.5 * math.log(2 * math.pi)
    log_likelihood = (terms * mask[:, None]).sum((-1, -2))
    log_likelihood = torch.logsumexp(F.log_softmax(prediction["logits"], -1) + log_likelihood, -1)
    return (-log_likelihood / mask.sum((-1, -2))).mean()


class ActionExpert(nn.Module):
    """A trainable sidecar with explicit action-space routing; no general weights.

    Discrete domains map to fixed ordered option keys. Existing open-ended option
    scoring stays in the original MSO object and is never changed by this module.
    """
    def __init__(self, feature_dim, proprio_dim, continuous=(), discrete=None, hidden=256, components=5):
        super().__init__()
        self.feature_dim, self.proprio_dim = feature_dim, proprio_dim
        self.spaces = {s.name: s for s in continuous}
        self.options = {k: tuple(v) for k, v in (discrete or {}).items()}
        if len(self.spaces) != len(continuous) or set(self.spaces) & set(self.options):
            raise ValueError("Action-space ids must be unique across routes")
        if any(not k or "." in k or len(v) < 2 or len(set(v)) != len(v) for k, v in self.options.items()):
            raise ValueError("Discrete domains need distinct keys and at least two unique options")
        self.visual = nn.Sequential(nn.LayerNorm(feature_dim), nn.Linear(feature_dim, hidden), nn.SiLU())
        self.trunk = nn.Sequential(nn.Linear(hidden + 2 * proprio_dim, hidden), nn.SiLU(), nn.Linear(hidden, hidden), nn.SiLU())
        self.continuous = nn.ModuleDict({s.name: ChunkMixture(hidden, s, components) for s in continuous})
        self.discrete = nn.ModuleDict({k: nn.Linear(hidden, len(v)) for k, v in self.options.items()})

    def forward(self, features, proprio, proprio_mask, action_space, mode):
        if features.shape[-1] != self.feature_dim or proprio.shape != proprio_mask.shape or proprio.shape != (len(features), self.proprio_dim):
            raise ValueError("Feature/proprioception schema mismatch")
        if mode not in ("continuous", "choice"):
            raise ValueError("Explicit continuous or choice mode required")
        heads = self.continuous if mode == "continuous" else self.discrete
        if action_space not in heads:
            raise ValueError(f"Unknown {mode} action space: {action_space}")
        mask = proprio_mask.bool()
        if not torch.isfinite(features).all() or not torch.isfinite(proprio[mask]).all():
            raise ValueError("Nonfinite input")
        p = torch.where(mask, proprio, torch.zeros_like(proprio))
        z = self.visual(features.detach().float())
        z = self.trunk(torch.cat((z, p.detach().float(), mask.float()), -1))
        return heads[action_space](z)


class DualRoute:
    """Keep the general callable intact; route actions only on explicit request.

    The action callable is responsible for encoding observations, applying the
    saved train-only normalization, and decoding its declared action schema.
    """
    def __init__(self, general, action):
        self.general, self.action = general, action

    def __call__(self, state, questions=None, *, mode="general", action_space=None, instruction=None):
        if mode == "general":
            if action_space is not None or instruction is not None:
                raise ValueError("Action arguments cannot alter the general route")
            return self.general(state, questions)
        if mode not in ("continuous", "choice") or not action_space or not instruction:
            raise ValueError("Action requests require mode, action_space and instruction")
        if questions is not None:
            raise ValueError("Send general questions separately from an action request")
        return self.action(state, mode=mode, action_space=action_space, instruction=instruction)
