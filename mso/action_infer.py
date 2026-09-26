"""Inference for an experimental action sidecar over a frozen MSO1 backbone."""
import hashlib
import json
from pathlib import Path

from PIL import Image
import torch

from .action import ActionExpert, ActionSpace


class ActionPolicy:
    def __init__(self, general_model, sidecar, *, general_checkpoint):
        self.general = general_model
        self.dev = general_model.dev
        sidecar = Path(sidecar)
        self.config = json.loads((sidecar / "config.json").read_text())
        # The sidecar's features depend on this exact adapter/head/tokenizer.
        for name, expected in self.config["frozen_checkpoint_sha256"].items():
            if Path(name).name != name:
                raise ValueError("Invalid checkpoint manifest path")
            path = Path(general_checkpoint) / name
            digest = hashlib.sha256()
            with path.open("rb") as f:
                for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
                    digest.update(block)
            if digest.hexdigest() != expected:
                raise ValueError(f"Frozen checkpoint mismatch: {name}")
        self.model = ActionExpert(
            self.config["feature_dim"], self.config["proprio_dim"],
            [ActionSpace(**s) for s in self.config["continuous"]],
            self.config["discrete"], hidden=self.config["hidden"],
            components=self.config["components"],
        ).to(self.dev).eval()
        ck = torch.load(sidecar / "action_best.pt", map_location=self.dev, weights_only=True)
        self.model.load_state_dict(ck["state_dict"], strict=True)
        self.model.requires_grad_(False)

    @torch.inference_mode()
    def __call__(self, state, *, mode, action_space, instruction):
        if mode not in ("continuous", "choice"):
            raise ValueError("Explicit continuous or choice mode required")
        spaces = self.model.continuous if mode == "continuous" else self.model.discrete
        if action_space not in spaces:
            raise ValueError("Action space does not match the requested mode")
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError("An action instruction is required")
        paths = state.get("images", [])
        if not paths or len(paths) > 2:
            raise ValueError("This candidate expects one or two ordered RGB frames")
        ims = []
        for path in paths:
            with Image.open(path) as im:
                ims.append(im.convert("RGB"))
        content = [{"type": "image", "image": im} for im in ims] + [{"type": "text", "text": instruction}]
        proc = self.general.proc
        prompt = proc.apply_chat_template([{"role": "user", "content": content}], tokenize=False, add_generation_prompt=True)
        recipe = self.config["feature_recipe"]
        enc = proc(text=[prompt], images=ims, return_tensors="pt", max_pixels=recipe["max_pixels"], min_pixels=recipe["min_pixels"])
        enc = {k: v.to(self.dev) if torch.is_tensor(v) else v for k, v in enc.items()}
        out = self.general.model.backbone(**enc, use_cache=False, output_hidden_states=True, logits_to_keep=1)
        features = out.hidden_states[-1][:, -1].float()
        stats = self.config["normalization"][action_space]
        values = state.get("proprio", [])
        if len(values) != stats["input_dim"]:
            raise ValueError(f"Expected {stats['input_dim']} proprioceptive values for {action_space}")
        p = torch.zeros(1, self.model.proprio_dim, device=self.dev)
        mask = torch.zeros_like(p, dtype=torch.bool)
        if values:
            p[0, :len(values)] = torch.tensor(values, device=self.dev)
            mask[0, :len(values)] = True
        if not torch.isfinite(p[mask]).all():
            raise ValueError("Proprioception must be finite")
        mu = torch.tensor(stats["mean"], device=self.dev)
        sd = torch.tensor(stats["std"], device=self.dev)
        p = ((p - mu) / sd).clamp(-10, 10) * mask
        pred = self.model(features, p, mask, action_space, mode)
        if mode == "choice":
            probabilities = pred.softmax(-1)[0].tolist()
            keys = self.model.options[action_space]
            winner = max(range(len(keys)), key=probabilities.__getitem__)
            return {"mode": mode, "action_space": action_space, "choice": keys[winner], "probabilities": dict(zip(keys, probabilities)), "experimental": True}
        head = self.model.continuous[action_space]
        command = head.command(pred)[0].tolist()
        return {"mode": mode, "action_space": action_space, "action": command[0], "chunk": command,
                "schema": head.space.metadata(), "mixture_weights": pred["logits"].softmax(-1)[0].tolist(),
                "execution": "execute first command, observe, then replan", "experimental": True}
