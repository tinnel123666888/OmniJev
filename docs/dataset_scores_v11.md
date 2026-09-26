# v1.1: dataset and subset score audit / 逐数据集与子集成绩审计

The old headline table grouped **task families**, not individual datasets. Its per-family question caps also skipped later source subsets. This audit rejoins every existing raw decision-model prediction to its source stratum and reconciles all **90 family reports** exactly (three sizes × 30 families). It does not rerun inference or turn these numbers into official benchmark scores.

旧表按任务族汇总，而且每族题数上限导致后面的部分数据集根本没有进入评测。本页已把原始预测逐条关联回来源，并与 90 份报告核对一致。4B 在冻结题池的 **96 个来源子集/分层中只实际评到 41 个**；其余明确标为未评测。这 96 行并不等于 96 个独立数据集。

## Findings that change how to read the results / 必须纠正的解读

- **Mario:** the old 56.05% combines next-action and yes/no questions. Next-action accuracy is only **43.52% (193 questions)**, with reported balanced accuracy **20.20%**. No closed-loop completion rate was measured. In the published demo, 24/28 action predictions match the recording, but the recording itself contains 24 `right_B` labels; always predicting `right_B` also gets 24/28. That demo does not establish gameplay ability.
- **OK-VQA:** 93.47% is top-1 accuracy over six supplied answers (including the gold) plus abstention, **not official open-ended VQA accuracy**.
- **POPE:** the 4B 84.73% report covers only 1,500 random-subset questions. Adversarial and popular subsets were not included in that capped report.
- **Atari/JAT:** the Atari cap reaches Alien and Bank Heist only; JAT reaches Enduro only. Scores cannot be advertised as covering all games in the source pool.
- **Safety:** 99.53% in the old safety row is HaGRID gestures only; CCTV-fire and weapons questions were not scored in that report.
- **General understanding:** the genmcq cap reaches A-OKVQA only; ScienceQA and OK-VQA-train holdouts were not scored.
- **Splits:** the training loader uses row-ID hashes, even where builders record episode/clip holdouts in metadata. Those metadata flags do not prove episode separation. Continuing from v1.1 cannot undo historical exposure; genuinely new episodes are required for new closed-loop evaluation.

## All source subsets / 全部来源子集

Each cell is **top-1 accuracy % (number of questions)** under the project conversion. `— 未评测` is missing coverage, never zero accuracy. All reported values below are the historical raw output reports, not a fresh evaluation after serving calibration. The original base/SFT family comparisons use different samples and remain in the [historical results](results_v11_zh.md); they are not silently copied onto these dataset-specific rows.

| Dataset / 来源 | Subset / 子集 | 0.8B % (n) | 2B % (n) | 4B % (n) |
| --- | --- | ---: | ---: | ---: |
| AndroidControl | androidcontrol | 71.70 (1,502) | 71.84 (1,502) | 77.30 (1,502) |
| Atari-HEAD (TESS 15 Hz conversion) | alien | 73.01 (415) | 62.41 (415) | 66.75 (415) |
| Atari-HEAD (TESS 15 Hz conversion) | bank_heist | 71.15 (1,085) | 63.78 (1,085) | 62.76 (1,085) |
| Atari-HEAD (TESS 15 Hz conversion) | breakout | — 未评测 | — 未评测 | — 未评测 |
| Atari-HEAD (TESS 15 Hz conversion) | freeway | — 未评测 | — 未评测 | — 未评测 |
| Atari-HEAD (TESS 15 Hz conversion) | frostbite | — 未评测 | — 未评测 | — 未评测 |
| Atari-HEAD (TESS 15 Hz conversion) | seaquest | — 未评测 | — 未评测 | — 未评测 |
| ESC-50 (spectrogram conversion) | esc50 | 51.07 (795) | 42.01 (795) | 53.08 (795) |
| Lichess chess positions (custom questions) | chess2 | 61.80 (1,500) | 61.67 (1,500) | 62.40 (1,500) |
| Lichess chess positions (region questions) | chess3 | 20.00 (1,500) | 15.13 (1,500) | 22.67 (1,500) |
| Charades-STA (custom event questions) | charades_events | 85.87 (1,500) | 86.47 (1,500) | 89.13 (1,500) |
| Synthetic Catch game | catch | 83.51 (1,504) | 80.32 (1,504) | 90.36 (1,504) |
| General-understanding training-source holdout | A-OKVQA train-source holdout | 77.60 (1,500) | 83.80 (1,500) | 88.20 (1,500) |
| General-understanding training-source holdout | ScienceQA train-source holdout | — 未评测 | — 未评测 | — 未评测 |
| General-understanding training-source holdout | OK-VQA train-source holdout | — 未评测 | — 未评测 | — 未评测 |
| Gomoku trajectories (custom questions) | gomoku | 69.80 (1,500) | 68.27 (1,500) | 70.60 (1,500) |
| JAT Atari trajectories | enduro | 63.73 (1,500) | 63.00 (1,500) | 65.87 (1,500) |
| JAT Atari trajectories | skiing | — 未评测 | — 未评测 | — 未评测 |
| JAT Atari trajectories | pong | — 未评测 | — 未评测 | — 未评测 |
| BridgeData / Bridge (jog questions) | bridge | 43.84 (1,501) | 48.43 (1,501) | 45.97 (1,501) |
| LIBERO-10 (jog questions) | libero10 | 49.24 (1,507) | 49.04 (1,507) | 51.56 (1,507) |
| LexGLUE (typed-question conversion) | CaseHOLD | 67.95 (964) | 69.29 (964) | 72.82 (964) |
| LexGLUE (typed-question conversion) | ECtHR | 91.62 (537) | 92.74 (537) | 93.67 (537) |
| LexGLUE (typed-question conversion) | SCOTUS | — 未评测 | — 未评测 | — 未评测 |
| LexGLUE (typed-question conversion) | LEDGAR | — 未评测 | — 未评测 | — 未评测 |
| LexGLUE (typed-question conversion) | Unfair-ToS | — 未评测 | — 未评测 | — 未评测 |
| LongVideoBench (sampled MCQ) | 15-second bucket | 59.20 (125) | 60.00 (125) | 66.40 (125) |
| LongVideoBench (sampled MCQ) | 3600-second bucket | 36.00 (125) | 38.40 (125) | 48.80 (125) |
| LongVideoBench (sampled MCQ) | 60-second bucket | 49.60 (125) | 59.20 (125) | 68.00 (125) |
| LongVideoBench (sampled MCQ) | 600-second bucket | 44.00 (125) | 42.40 (125) | 44.00 (125) |
| OpenGenGAME Super Mario Bros 1-1 | World 1-1; custom row holdout | 53.88 (735) | 54.69 (735) | 56.05 (735) |
| Music genre collection (custom spectrogram questions) | Electronic | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | International | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Hip-Hop | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Instrumental | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Rock | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Chiptune / Glitch | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Punk | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Country | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Experimental | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Old-Time / Historic | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Pop | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Folk | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Spoken | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Classical | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Jazz | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Blues | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Soul-RnB | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Ambient Electronic | — 未评测 | — 未评测 | — 未评测 |
| Music genre collection (custom spectrogram questions) | Easy Listening | — 未评测 | — 未评测 | — 未评测 |
| UT Austin MUTEX (custom questions) | mutex | 73.33 (1,500) | 70.73 (1,500) | 79.07 (1,500) |
| Historical mixed typed-question pool | multi | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | abstain | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | disagree | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | clean | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | alien | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | cua_nonclick | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | cua_click | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | chess | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | chess_check | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | chess_mate | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | video | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | gui | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | coco | — 未评测 | — 未评测 | — 未评测 |
| Historical mixed typed-question pool | web | 67.54 (1,491) | 66.06 (1,491) | 70.76 (1,491) |
| Web grounding (custom 8×12 / fine grid) | point_web | 67.30 (627) | 67.62 (627) | 75.76 (627) |
| Web grounding (custom 8×12 / fine grid) | point_web_fine | 67.01 (873) | 65.64 (873) | 75.83 (873) |
| Phone / own-screen grounding (custom grid) | point_cua | 63.41 (123) | 63.41 (123) | 66.67 (123) |
| Phone / own-screen grounding (custom grid) | point_cua_fine | 57.08 (240) | 53.33 (240) | 65.42 (240) |
| Phone / own-screen grounding (custom grid) | point_own | 58.22 (213) | 61.50 (213) | 74.65 (213) |
| Phone / own-screen grounding (custom grid) | point_own_fine | 64.35 (345) | 64.35 (345) | 78.26 (345) |
| POPE (sampled questions) | adversarial | — 未评测 | — 未评测 | — 未评测 |
| POPE (sampled questions) | popular | — 未评测 | — 未评测 | — 未评测 |
| POPE (sampled questions) | random | 66.73 (1,500) | 66.87 (1,500) | 84.73 (1,500) |
| RoboArena (wrist-view questions) | mid | 65.42 (1,044) | 64.85 (1,044) | 67.05 (1,044) |
| RoboArena (wrist-view questions) | end | 73.44 (384) | 74.48 (384) | 75.26 (384) |
| RoboArena (wrist-view questions) | pref | 34.67 (75) | 44.00 (75) | 40.00 (75) |
| LIBERO-10 (long-horizon frame questions) | libero10 | 79.79 (1,504) | 78.46 (1,504) | 85.04 (1,504) |
| HaGRID / CCTV fire / weapons mixture | HaGRID gestures | 97.73 (1,500) | 99.07 (1,500) | 99.53 (1,500) |
| HaGRID / CCTV fire / weapons mixture | CCTV fire | — 未评测 | — 未评测 | — 未评测 |
| HaGRID / CCTV fire / weapons mixture | Weapons images | — 未评测 | — 未评测 | — 未评测 |
| Synthetic Snake trajectories | snake | 83.60 (1,500) | 82.87 (1,500) | 84.47 (1,500) |
| COIN / long video / spatial / robot mixture | coin | 57.51 (1,511) | 59.10 (1,511) | 62.81 (1,511) |
| COIN / long video / spatial / robot mixture | lvr | — 未评测 | — 未评测 | — 未评测 |
| COIN / long video / spatial / robot mixture | spatial_spacellava | — 未评测 | — 未评测 | — 未评测 |
| COIN / long video / spatial / robot mixture | spatial_openspaces | — 未评测 | — 未评测 | — 未评测 |
| COIN / long video / spatial / robot mixture | spatial_vsr | — 未评测 | — 未评测 | — 未评测 |
| COIN / long video / spatial / robot mixture | robot | — 未评测 | — 未评测 | — 未评测 |
| OK-VQA (gold-included answer pool) | 6 supplied answers + abstain; gold included | 63.87 (1,500) | 79.60 (1,500) | 93.47 (1,500) |
| Mind2Web train-source custom holdout | web_train | 66.87 (1,500) | 67.53 (1,500) | 76.80 (1,500) |
| Mind2Web official test splits | test-task | 67.13 (1,500) | 67.87 (1,500) | 77.40 (1,500) |
| Mind2Web official test splits | test-website | — 未评测 | — 未评测 | — 未评测 |
| Mind2Web official test splits | test-domain | — 未评测 | — 未评测 | — 未评测 |
| SimpleWiki navigation | wikinav | 68.00 (1,500) | 68.53 (1,500) | 72.13 (1,500) |
| Xiangqi positions (custom questions) | jsonl | 22.27 (1,500) | 18.07 (1,500) | 23.67 (1,500) |
| Xiangqi positions (custom questions) | jsonl-test | — 未评测 | — 未评测 | — 未评测 |

## Mario question breakdown / 马里奥逐问题

| Question | 4B accuracy % | n |
| --- | ---: | ---: |
| `mario_act` | 43.52 | 193 |
| `mario_hold` | 44.23 | 156 |
| `mario_jump` | 60.10 | 193 |
| `mario_run` | 74.09 | 193 |

[Machine-readable audit, per-question breakdown and source-score hashes](dataset_scores_v11.json). Official VQA soft scoring, full POPE subsets and closed-loop game/robot metrics must be reported separately; unavailable results remain unavailable.
