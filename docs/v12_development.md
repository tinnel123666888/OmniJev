# v1.2 development / 开发记录

**Experimental work, not a released v1.2 model.** The v1.1 general checkpoint remains the default. Offline action accuracy is not a game-completion or robot-success rate.

**这是实验候选，不是已发布的 v1.2。** v1.1 演示没有证明模型会玩马里奥；旧汇总成绩还存在覆盖不足、混合题型和错误标签问题。逐来源和逐题型的修正见 [v1.1 score audit](dataset_scores_v11.md)。

## Two explicit output routes

- `mode="continuous"`: a domain-specific mixture head predicts four future normalized commands. Highway control uses acceleration and steering; Fetch uses Cartesian displacement and gripper control. Each action space records dimensions, bounds, units, horizon and control frequency. The decoder chooses a mixture component rather than averaging incompatible trajectories. Only valid time steps contribute to the training loss.
- `mode="choice"`: a domain-specific categorical head returns probabilities over an ordered action vocabulary, including simultaneous Mario button combinations and the 18 ALE controller actions.
- `mode="general"`: calls the existing MSO question interface unchanged, including `choice`, `noul` and `score`. The action sidecar receives detached features and cannot update the general checkpoint. It does not reinterpret ordinary VQA questions as control requests.

The first implementation is in [action.py](../mso/action.py), with checkpoint/schema validation in [action_infer.py](../mso/action_infer.py). Four unit checks passed: masked future targets, selection of distinct action modes, detached feature gradients, and unchanged general-route arguments/results. Mixture weights are not calibrated physical-safety guarantees. Simulator control frequency is not a measured inference rate.

```python
from mso.action import DualRoute
from mso.action_infer import ActionPolicy

# general is an existing MSO1 instance loaded from the exact frozen checkpoint.
policy = ActionPolicy(general, "experimental_sidecar", general_checkpoint="v1.1_checkpoint")
system = DualRoute(general.system_one, policy)

answer = system(state, questions)  # original general interface
command = system(robot_state, mode="continuous", action_space="arm_push",
                 instruction="Push the cube to the target marker.")
buttons = system(game_state, mode="choice", action_space="Mario-Pygame-1-1",
                 instruction="Avoid obstacles and reach the flag.")
```

The sidecar requires its saved normalization and exact input schema. It is not part of the v1.1 weight download.

## Expanded data

These are collected/converted records **before exact-observation deduplication**, not independent successful model executions.

| Source | Scope | Records | Collector / source outcome |
| --- | --- | ---: | --- |
| HighwayEnv | Highway, dense traffic, faster traffic | 30,720 | 384 scripted-teacher episodes without collisions |
| MuJoCo / Fetch | Reach, push, pick-and-place | 23,047 | 1,517 of 1,536 teacher episodes successful; 19 failed episodes excluded from imitation |
| MiniGrid | Empty, random start, two DoorKey sizes, FourRooms, LavaGap | 18,265 | 1,536 planner episodes successful; fixed maps contain many repeated observations |
| FeiyanZhou Mario recordings | Pygame Super Mario level 1-1 | 20,524 | Selected from 521,937 source frames in 130 recording sessions; mixed-quality human/RL play |
| TESS Atari conversion | Alien, Asterix, Bank Heist, Breakout, Demon Attack, Freeway, Frostbite, Hero, Ms. Pac-Man, Road Runner, Seaquest | 23,283 | Per-game/action sampling; no successful-episode claim |
| **Total** | | **115,839** | Not a count of unique observations |

The first driving render attempt was black despite valid simulator actions. Those frames were replaced before training; image variance is checked during collection and bundle preparation. Mario's recorder captures the screen **after** applying its key command, so the builder uses the next contiguous live frame's action label. Pygame Mario and NES Mario have different action encodings and are not reported as the same environment.

Sources: [HighwayEnv](https://highway-env.farama.org/), [Fetch environments](https://robotics.farama.org/envs/fetch/), [MiniGrid](https://minigrid.farama.org/), [Mario dataset](https://huggingface.co/datasets/FeiyanZhou/mario_data), [pinned Mario recorder](https://github.com/zhoufeiyn/super-mario1_1env/tree/c6c43609f6f1bf60f69d75f70154150f84e663cd), [Atari dataset](https://huggingface.co/datasets/TESS-Computer/atari-vla-stage1-15hz).

## Splits and limits

- Split whole simulator episodes, whole Mario recording sessions and whole Atari trials before sampling. Remove exact duplicate ordered observations across the selected splits. Do not rely on the old row-hash holdout mechanism.
- Some Atari source data existed in v1.1. Its new offline split is useful for development comparisons, but does not certify absence of historical exposure.
- The NES TAS archive was downloaded but excluded: the flattened archive lacks a trustworthy per-playthrough mapping and its action timing is not sufficiently specified.
- A-OKVQA's old synthesized `gu_yes` questions are excluded because the converter sampled characters from a serialized answer list. The original evidence is retained, not silently relabeled to improve a score.
- Fetch's `state.proprio` currently contains full simulator observations, including object and target information. This is a continuous-control prototype with privileged state, **not evidence of vision-only manipulation**. A separately trained state-only baseline is needed to measure the visual contribution.
- Small fixed MiniGrid maps have very few distinct observations after deduplication. Episode counts must not be used to imply thousands of independent planning situations.

## Training and release gate

The first 8-device MLU590 run trained a frozen-backbone sidecar on a 10,331-state development bundle for 1,600 optimizer steps. It produced a real candidate checkpoint while preserving all v1.1 checkpoint file hashes. Its offline action results were insufficient for release; for example, Pygame Mario action accuracy was 28.13% on 64 sampled states, and some grid/driving results failed simple baseline comparisons. This score is not comparable to the old NES Mario row.

The expanded second bundle contains 44,046 states, with a 16,000-step continuation prepared from the first action checkpoint. Domain-specific train-only normalization is retained when continuing an existing head; rare discrete actions receive inverse-square-root frequency sampling. Previously inspected offline holdouts are identified as development data, not a new untouched final test.

Release requires paired general-route checks on the same questions, per-dataset coverage and question counts, calibration statistics for choices, and real closed-loop outcomes on fresh simulator episodes. Model rollouts must be compared with fixed-action baselines. A stopped simulator waiting for inference does not establish real-time control. A failed candidate does not replace v1.1 or justify a new capability claim.

The stage-one general-route integration check passed on **152 states / 393 questions / 19 source subsets**. Returned answers, probabilities and confidence matched before and after calling the action sidecar; maximum returned-value difference was **0**. Only the two latency fields were excluded. The existing API rounds its returned probabilities, so this is an equality check at the API's output precision. [Per-subset regression results](v12_general_regression_stage1.json).
