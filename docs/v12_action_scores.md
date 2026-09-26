# v1.2 action development scores

**Experimental checkpoints; not a released v1.2.** These sampled, action-balanced offline scores are not gameplay completion rates. The inspected holdout is development data. Atari has historical source exposure; fixed-map games have limited diversity. A dash means unmeasured or no eligible head, never zero.

不同阶段抽样规模不同，不应把下表的数值差直接当成同卷提升。连续控制误差是归一化动作空间的均方误差，越低越好；分类准确率不是闭环成功率。

## Stage 1: discrete actions

Checkpoint selection step: **1600**. [Full raw metrics, including validation, NLL, Brier and ECE](v12_action_offline_stage1.json).

| Dataset / environment | Questions | Accuracy | Balanced accuracy | Train-majority baseline | ECE (10 bins) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Atari-alien | 64 | 21.88% | 19.03% | 9.38% | 0.0514 |
| Atari-asterix | 64 | 17.19% | 20.48% | 6.25% | 0.0781 |
| Atari-bank_heist | 64 | 12.50% | 11.29% | 9.38% | 0.0634 |
| Atari-breakout | 64 | 17.19% | 38.39% | 29.69% | 0.2947 |
| Atari-demon_attack | 64 | 18.75% | 21.34% | 14.06% | 0.0496 |
| Atari-freeway | — | — | — | — | — |
| Atari-frostbite | — | — | — | — | — |
| Atari-hero | 64 | 9.38% | 9.76% | 1.56% | 0.0760 |
| Atari-ms_pacman | 64 | 15.62% | 12.22% | 3.12% | 0.0303 |
| Atari-road_runner | 64 | 18.75% | 18.06% | 3.12% | 0.0521 |
| Atari-seaquest | 64 | 9.38% | 6.19% | 4.69% | 0.0508 |
| Mario-Pygame-1-1 | 64 | 28.12% | 23.40% | 9.38% | 0.0582 |
| MiniGrid-DoorKey-6x6-v0 | 64 | 59.38% | 23.95% | 12.50% | 0.0745 |
| MiniGrid-DoorKey-8x8-v0 | 64 | 62.50% | 24.00% | 59.38% | 0.1661 |
| MiniGrid-Empty-8x8-v0 | — | — | — | — | — |
| MiniGrid-Empty-Random-6x6-v0 | 49 | 61.22% | 34.38% | 65.31% | 0.3591 |
| MiniGrid-FourRooms-v0 | 64 | 84.38% | 33.33% | 84.38% | 0.1186 |
| MiniGrid-LavaGapS7-v0 | 64 | 53.12% | 61.11% | 87.50% | 0.2799 |

## Stage 1: continuous actions

| Environment | States | First-command MSE | Constant train-mean MSE | Four-command chunk MSE |
| --- | ---: | ---: | ---: | ---: |
| arm_pickplace | 64 | 0.347073 | 0.411630 | 0.343430 |
| arm_push | 64 | 0.145685 | 0.170840 | 0.141682 |
| arm_reach | 64 | 0.163609 | 0.285309 | 0.158677 |
| drive_dense | 64 | 0.040932 | 0.032142 | 0.028453 |
| drive_fast | — | — | — | — |
| drive_highway | 64 | 0.005581 | 0.003849 | 0.005146 |

## Coverage and interpretation

Freeway has no validation/test trials in this split. Frostbite has no selected test rows. Fixed-map Empty 8x8 has no eligible trained head after deduplication. The manifest reports every source and split, including zeros. Fetch supplies privileged object and goal state, not vision-only observations. Driving scenarios share HighwayEnv and are not independent external datasets.

[Data manifest](v12_data_manifest_stage2.json) · [Closed-loop results and development status](v12_development.md) · [Corrected v1.1 dataset scores](dataset_scores_v11.md)
