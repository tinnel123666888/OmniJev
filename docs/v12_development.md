# Experimental action interface

v1.2 is under development. The released model remains v1.1. Experimental training and evaluation records are maintained privately; this page describes the interface only and makes no gameplay or manipulation performance claim.

## Explicit output routes

- `mode="continuous"`: a domain-specific mixture head predicts four future normalized commands. Each action space records dimensions, bounds, units, horizon and control frequency. The decoder selects one mixture component; the controller executes the first command, observes the new state and replans.
- `mode="choice"`: a domain-specific categorical head returns probabilities over an ordered action vocabulary, including simultaneous controller buttons.
- `mode="general"`: preserves the existing MSO question interface, including `choice`, `noul` and `score`. General inference remains the default.

The action sidecar receives detached features from the frozen backbone. Its training cannot update the original general checkpoint. [Action heads and routing](../mso/action.py) · [Checkpoint and input-schema validation](../mso/action_infer.py).

Continuous action spaces have explicit units and bounds; they are not interchangeable across simulators or robots. Mixture weights are not calibrated physical-safety guarantees. Simulator control frequency is not measured inference throughput.

The sidecar is experimental and is not included in the v1.1 weight download. General-route integration checks are distinct from a complete official VQA benchmark. The implementation does not establish reliable closed-loop control.

For the released model's score definitions and coverage, see the [v1.1 per-dataset audit](dataset_scores_v11.md).
