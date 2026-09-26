# v1.1: dataset and subset score audit / 逐数据集与子集成绩审计

The old headline table grouped **task families**, not individual datasets. Its per-family question caps also skipped later source subsets. This audit rejoins every existing raw decision-model prediction to its source stratum and reconciles all **90 family reports** exactly (three sizes × 30 families). It does not rerun inference or turn these numbers into official benchmark scores.

旧表按任务族汇总，而且每族题数上限导致后面的部分数据集根本没有进入评测。本页已把原始预测逐条关联回来源，并与 90 份报告核对一致。4B 在冻结题池的 **96 个来源子集/分层中只实际评到 41 个**；其余明确标为未评测。这 96 行并不等于 96 个独立数据集。

## Findings that change how to read the results / 必须纠正的解读

- **Mario:** the old 56.05% combines next-action and yes/no questions. Next-action accuracy is only **43.52% (193 questions)**, with reported balanced accuracy **20.20%**. No closed-loop completion rate was measured. In the published demo, 24/28 action predictions match the recording, but the recording itself contains 24 `right_B` labels; always predicting `right_B` also gets 24/28. That demo does not establish gameplay ability.
- **OK-VQA:** 93.47% is top-1 accuracy over six supplied answers (including the gold) plus abstention, **not official open-ended VQA accuracy**.
- **POPE:** the 4B 84.73% report covers only 1,500 random-subset questions. Adversarial and popular subsets were not included in that capped report.
- **Atari/JAT:** the Atari cap reaches Alien and Bank Heist only; JAT reaches Enduro only. Scores cannot be advertised as covering all games in the source pool.
- **Safety:** 99.53% in the old safety row is HaGRID gestures only; CCTV-fire and weapons questions were not scored in that report.
- **A-OKVQA label defect:** `direct_answers` was a serialized list string; the converter sampled individual characters and marked them as correct answers. All 654 positive synthesized yes/no labels in the frozen A-OKVQA pool are invalid. The old 88.20% mixed score is withdrawn as an understanding metric. Retaining only the existing multiple-choice predictions gives **77.07% (750 questions)** for 4B, still under this project's custom abstention protocol. [Label audit](aokvqa_label_audit_v11.json). ScienceQA and OK-VQA-train holdouts were not scored.
- **Splits:** the training loader uses row-ID hashes, even where builders record episode/clip holdouts in metadata. Those metadata flags do not prove episode separation. Continuing from v1.1 cannot undo historical exposure; genuinely new episodes are required for new closed-loop evaluation.

## All source subsets / 全部来源子集

Each cell is **top-1 accuracy % (number of questions)** under the project conversion. `— 未评测` is missing coverage, never zero accuracy. Except for the explicitly filtered A-OKVQA row, reported values below are the historical raw output reports, not a fresh evaluation after serving calibration. The original base/SFT family comparisons use different samples and remain in the [historical results](results_v11_zh.md); they are not silently copied onto these dataset-specific rows.

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
| A-OKVQA train-source holdout | Multiple choice only; defective synthesized yes/no excluded | 56.67 (750) | 68.40 (750) | 77.07 (750) |
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

## Scores separated by question type / 逐题型拆分

Each row uses the same saved predictions as the source table. These are custom question conversions, not official benchmark scores. Invalid A-OKVQA yes/no results are excluded here; the original raw aggregate remains in the JSON for auditability.

| Source / subset | Question id | 0.8B % (n) | 2B % (n) | 4B % (n) |
| --- | --- | ---: | ---: | ---: |
| androidcontrol/androidcontrol | `ac_act` | 81.80 (401) | 84.54 (401) | 88.28 (401) |
| androidcontrol/androidcontrol | `ac_cell` | 33.60 (253) | 33.60 (253) | 47.83 (253) |
| androidcontrol/androidcontrol | `ac_done` | 98.25 (401) | 98.25 (401) | 98.25 (401) |
| androidcontrol/androidcontrol | `ac_prog` | 57.36 (401) | 53.87 (401) | 61.85 (401) |
| androidcontrol/androidcontrol | `ac_scroll` | 86.96 (46) | 97.83 (46) | 95.65 (46) |
| atari/alien | `at_act` | 37.35 (83) | 16.87 (83) | 24.10 (83) |
| atari/alien | `at_fire` | 100.00 (83) | 100.00 (83) | 100.00 (83) |
| atari/alien | `at_move` | 39.76 (83) | 7.23 (83) | 21.69 (83) |
| atari/alien | `at_reward` | 87.95 (83) | 87.95 (83) | 87.95 (83) |
| atari/alien | `at_score` | 100.00 (83) | 100.00 (83) | 100.00 (83) |
| atari/bank_heist | `at_act` | 29.49 (217) | 11.98 (217) | 23.50 (217) |
| atari/bank_heist | `at_fire` | 98.16 (217) | 98.16 (217) | 98.16 (217) |
| atari/bank_heist | `at_move` | 29.95 (217) | 21.20 (217) | 25.81 (217) |
| atari/bank_heist | `at_reward` | 98.16 (217) | 98.16 (217) | 98.16 (217) |
| atari/bank_heist | `at_score` | 100.00 (217) | 89.40 (217) | 68.20 (217) |
| audio/esc50 | `au_burst` | 93.08 (159) | 89.31 (159) | 87.42 (159) |
| audio/esc50 | `au_class` | 25.79 (159) | 28.93 (159) | 50.94 (159) |
| audio/esc50 | `au_group` | 31.45 (159) | 27.67 (159) | 27.67 (159) |
| audio/esc50 | `au_human` | 81.13 (159) | 33.33 (159) | 67.92 (159) |
| audio/esc50 | `au_loud` | 23.90 (159) | 30.82 (159) | 31.45 (159) |
| chess2/chess2 | `ch_cap` | 77.67 (300) | 77.67 (300) | 77.67 (300) |
| chess2/chess2 | `ch_check` | 95.67 (300) | 95.67 (300) | 95.67 (300) |
| chess2/chess2 | `ch_mat` | 65.33 (300) | 65.33 (300) | 64.67 (300) |
| chess2/chess2 | `ch_move` | 39.67 (300) | 42.00 (300) | 45.67 (300) |
| chess2/chess2 | `ch_piece` | 30.67 (300) | 27.67 (300) | 28.33 (300) |
| chess3/chess3 | `ch_from` | 18.80 (500) | 14.40 (500) | 26.40 (500) |
| chess3/chess3 | `ch_legal` | 20.00 (500) | 19.20 (500) | 22.40 (500) |
| chess3/chess3 | `ch_to` | 21.20 (500) | 11.80 (500) | 19.20 (500) |
| events/charades_events | `e1` | 82.33 (300) | 81.33 (300) | 85.00 (300) |
| events/charades_events | `e2` | 78.00 (300) | 79.00 (300) | 83.67 (300) |
| events/charades_events | `e3` | 96.00 (300) | 98.00 (300) | 97.00 (300) |
| events/charades_events | `e4` | 91.67 (300) | 90.33 (300) | 93.67 (300) |
| events/charades_events | `e5` | 81.33 (300) | 83.67 (300) | 86.33 (300) |
| game/catch | `g_act` | 66.56 (302) | 55.30 (302) | 71.52 (302) |
| game/catch | `g_ball` | 80.41 (296) | 63.18 (296) | 93.24 (296) |
| game/catch | `g_bomb` | 99.67 (302) | 99.67 (302) | 99.67 (302) |
| game/catch | `g_miss` | 73.18 (302) | 83.11 (302) | 87.42 (302) |
| game/catch | `g_score` | 97.68 (302) | 100.00 (302) | 100.00 (302) |
| genmcq/aokvqa | `gu_mcq` | 56.67 (750) | 68.40 (750) | 77.07 (750) |
| genmcq/aokvqa | `gu_yes` | INVALID / 标签错误 | INVALID / 标签错误 | INVALID / 标签错误 |
| gomoku/gomoku | `gm_block` | 85.33 (300) | 85.33 (300) | 85.33 (300) |
| gomoku/gomoku | `gm_count` | 93.67 (300) | 94.00 (300) | 96.67 (300) |
| gomoku/gomoku | `gm_lead` | 49.00 (300) | 45.00 (300) | 52.00 (300) |
| gomoku/gomoku | `gm_move` | 22.00 (300) | 18.00 (300) | 20.00 (300) |
| gomoku/gomoku | `gm_win` | 99.00 (300) | 99.00 (300) | 99.00 (300) |
| jat/enduro | `jat_act` | 28.67 (300) | 25.67 (300) | 28.00 (300) |
| jat/enduro | `jat_game` | 100.00 (300) | 100.00 (300) | 100.00 (300) |
| jat/enduro | `jat_hold` | 91.33 (300) | 91.33 (300) | 91.33 (300) |
| jat/enduro | `jat_move` | 37.67 (300) | 38.33 (300) | 38.67 (300) |
| jat/enduro | `jat_reward` | 61.00 (300) | 59.67 (300) | 71.33 (300) |
| jog_bridge/bridge | `jg_axis` | 20.11 (179) | 23.46 (179) | 21.79 (179) |
| jog_bridge/bridge | `jg_closed` | 67.60 (179) | 73.74 (179) | 71.51 (179) |
| jog_bridge/bridge | `jg_grip` | 56.52 (69) | 55.07 (69) | 55.07 (69) |
| jog_bridge/bridge | `jg_hold` | 45.25 (179) | 48.60 (179) | 46.93 (179) |
| jog_bridge/bridge | `jg_rot` | 32.40 (179) | 31.28 (179) | 32.96 (179) |
| jog_bridge/bridge | `jg_step` | 45.25 (179) | 53.07 (179) | 49.16 (179) |
| jog_bridge/bridge | `jg_x` | 44.13 (179) | 50.84 (179) | 48.04 (179) |
| jog_bridge/bridge | `jg_y` | 49.16 (179) | 50.84 (179) | 47.49 (179) |
| jog_bridge/bridge | `jg_z` | 41.90 (179) | 53.07 (179) | 46.37 (179) |
| jog_full/libero10 | `jg_axis` | 38.76 (178) | 38.20 (178) | 43.82 (178) |
| jog_full/libero10 | `jg_closed` | 82.02 (178) | 85.96 (178) | 74.72 (178) |
| jog_full/libero10 | `jg_grip` | 68.67 (83) | 68.67 (83) | 67.47 (83) |
| jog_full/libero10 | `jg_hold` | 41.01 (178) | 45.51 (178) | 44.94 (178) |
| jog_full/libero10 | `jg_rot` | 20.79 (178) | 15.73 (178) | 21.35 (178) |
| jog_full/libero10 | `jg_step` | 42.70 (178) | 40.45 (178) | 45.51 (178) |
| jog_full/libero10 | `jg_x` | 61.24 (178) | 59.55 (178) | 60.11 (178) |
| jog_full/libero10 | `jg_y` | 53.37 (178) | 50.00 (178) | 58.99 (178) |
| jog_full/libero10 | `jg_z` | 44.94 (178) | 47.75 (178) | 55.62 (178) |
| longtext/case_hold | `lt_hold` | 67.95 (964) | 69.29 (964) | 72.82 (964) |
| longtext/ecthr | `lt_any` | 93.30 (179) | 93.30 (179) | 93.30 (179) |
| longtext/ecthr | `lt_art0` | 90.50 (179) | 89.94 (179) | 92.74 (179) |
| longtext/ecthr | `lt_art1` | 91.06 (179) | 94.97 (179) | 94.97 (179) |
| lvb/lvb15 | `q` | 59.20 (125) | 60.00 (125) | 66.40 (125) |
| lvb/lvb3600 | `q` | 36.00 (125) | 38.40 (125) | 48.80 (125) |
| lvb/lvb60 | `q` | 49.60 (125) | 59.20 (125) | 68.00 (125) |
| lvb/lvb600 | `q` | 44.00 (125) | 42.40 (125) | 44.00 (125) |
| mario/smb_1_1 | `mario_act` | 44.04 (193) | 44.04 (193) | 43.52 (193) |
| mario/smb_1_1 | `mario_hold` | 44.23 (156) | 42.31 (156) | 44.23 (156) |
| mario/smb_1_1 | `mario_jump` | 51.30 (193) | 55.96 (193) | 60.10 (193) |
| mario/smb_1_1 | `mario_run` | 74.09 (193) | 74.09 (193) | 74.09 (193) |
| mutex/mutex | `r3_dir` | 50.40 (250) | 48.00 (250) | 60.00 (250) |
| mutex/mutex | `r3_done` | 92.40 (250) | 92.00 (250) | 93.60 (250) |
| mutex/mutex | `r3_grasp` | 79.20 (250) | 78.40 (250) | 78.80 (250) |
| mutex/mutex | `r3_hold` | 71.60 (250) | 64.00 (250) | 83.20 (250) |
| mutex/mutex | `r3_instr` | 86.80 (250) | 89.20 (250) | 84.00 (250) |
| mutex/mutex | `r3_prog` | 59.60 (250) | 52.80 (250) | 74.80 (250) |
| old/web | `a0` | 87.22 (133) | 92.48 (133) | 90.23 (133) |
| old/web | `a1` | 76.47 (119) | 79.83 (119) | 82.35 (119) |
| old/web | `a10` | 55.56 (18) | 61.11 (18) | 55.56 (18) |
| old/web | `a11` | 50.00 (16) | 75.00 (16) | 56.25 (16) |
| old/web | `a12` | 38.46 (13) | 38.46 (13) | 61.54 (13) |
| old/web | `a13` | 55.56 (9) | 44.44 (9) | 77.78 (9) |
| old/web | `a14` | 71.43 (7) | 57.14 (7) | 42.86 (7) |
| old/web | `a15` | 66.67 (6) | 50.00 (6) | 33.33 (6) |
| old/web | `a16` | 50.00 (6) | 66.67 (6) | 50.00 (6) |
| old/web | `a17` | 40.00 (5) | 60.00 (5) | 40.00 (5) |
| old/web | `a18` | 80.00 (5) | 60.00 (5) | 60.00 (5) |
| old/web | `a19` | 80.00 (5) | 60.00 (5) | 60.00 (5) |
| old/web | `a2` | 67.62 (105) | 71.43 (105) | 72.38 (105) |
| old/web | `a20` | 80.00 (5) | 80.00 (5) | 60.00 (5) |
| old/web | `a21` | 50.00 (4) | 50.00 (4) | 75.00 (4) |
| old/web | `a22` | 50.00 (4) | 50.00 (4) | 75.00 (4) |
| old/web | `a23` | 75.00 (4) | 75.00 (4) | 50.00 (4) |
| old/web | `a24` | 50.00 (4) | 75.00 (4) | 50.00 (4) |
| old/web | `a25` | 25.00 (4) | 50.00 (4) | 25.00 (4) |
| old/web | `a26` | 100.00 (4) | 75.00 (4) | 100.00 (4) |
| old/web | `a27` | 100.00 (4) | 75.00 (4) | 100.00 (4) |
| old/web | `a28` | 75.00 (4) | 100.00 (4) | 50.00 (4) |
| old/web | `a29` | 100.00 (4) | 75.00 (4) | 100.00 (4) |
| old/web | `a3` | 59.21 (76) | 67.11 (76) | 75.00 (76) |
| old/web | `a30` | 75.00 (4) | 50.00 (4) | 75.00 (4) |
| old/web | `a31` | 66.67 (3) | 33.33 (3) | 66.67 (3) |
| old/web | `a32` | 66.67 (3) | 33.33 (3) | 66.67 (3) |
| old/web | `a33` | 66.67 (3) | 33.33 (3) | 66.67 (3) |
| old/web | `a34` | 66.67 (3) | 33.33 (3) | 66.67 (3) |
| old/web | `a35` | 50.00 (2) | 0.00 (2) | 50.00 (2) |
| old/web | `a36` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a37` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a38` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a39` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a4` | 66.15 (65) | 61.54 (65) | 78.46 (65) |
| old/web | `a40` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a41` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a42` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a43` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a44` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a45` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a46` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a47` | 100.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a48` | 100.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a49` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a5` | 65.45 (55) | 61.82 (55) | 72.73 (55) |
| old/web | `a50` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a51` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a52` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a53` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a54` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a55` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a56` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a57` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a58` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a59` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a6` | 64.58 (48) | 47.92 (48) | 70.83 (48) |
| old/web | `a60` | 100.00 (1) | 100.00 (1) | 0.00 (1) |
| old/web | `a61` | 100.00 (1) | 100.00 (1) | 100.00 (1) |
| old/web | `a62` | 0.00 (1) | 100.00 (1) | 100.00 (1) |
| old/web | `a63` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a64` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a65` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a66` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a67` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a68` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a69` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a7` | 60.00 (40) | 62.50 (40) | 62.50 (40) |
| old/web | `a70` | 0.00 (1) | 100.00 (1) | 0.00 (1) |
| old/web | `a71` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a72` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a73` | 100.00 (1) | 100.00 (1) | 0.00 (1) |
| old/web | `a74` | 100.00 (1) | 100.00 (1) | 100.00 (1) |
| old/web | `a75` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a76` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a77` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a78` | 0.00 (1) | 100.00 (1) | 0.00 (1) |
| old/web | `a79` | 0.00 (1) | 100.00 (1) | 0.00 (1) |
| old/web | `a8` | 51.52 (33) | 57.58 (33) | 66.67 (33) |
| old/web | `a80` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a81` | 100.00 (1) | 100.00 (1) | 0.00 (1) |
| old/web | `a82` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a83` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a84` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a85` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a86` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a87` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a88` | 100.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a89` | 100.00 (1) | 100.00 (1) | 100.00 (1) |
| old/web | `a9` | 40.74 (27) | 40.74 (27) | 44.44 (27) |
| old/web | `a90` | 100.00 (1) | 100.00 (1) | 100.00 (1) |
| old/web | `a91` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a92` | 0.00 (1) | 0.00 (1) | 0.00 (1) |
| old/web | `a93` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `a94` | 0.00 (1) | 0.00 (1) | 100.00 (1) |
| old/web | `b0` | 7.07 (99) | 18.18 (99) | 32.32 (99) |
| old/web | `b1` | 90.59 (85) | 64.71 (85) | 35.29 (85) |
| old/web | `c0` | 83.46 (133) | 85.71 (133) | 88.72 (133) |
| old/web | `c1` | 80.30 (132) | 83.33 (132) | 83.33 (132) |
| old/web | `d0` | 73.68 (133) | 70.68 (133) | 75.94 (133) |
| pilot_web/point_web | `pt_coarse` | 24.76 (210) | 28.57 (210) | 51.90 (210) |
| pilot_web/point_web | `pt_in_coarse` | 91.90 (210) | 81.90 (210) | 81.43 (210) |
| pilot_web/point_web | `pt_out_coarse` | 85.51 (207) | 92.75 (207) | 94.20 (207) |
| pilot_web/point_web_fine | `pt_coarse` | 22.60 (146) | 21.23 (146) | 49.32 (146) |
| pilot_web/point_web_fine | `pt_fine` | 26.71 (146) | 28.08 (146) | 54.11 (146) |
| pilot_web/point_web_fine | `pt_in_coarse` | 93.84 (146) | 79.45 (146) | 80.14 (146) |
| pilot_web/point_web_fine | `pt_in_fine` | 94.52 (146) | 86.99 (146) | 88.36 (146) |
| pilot_web/point_web_fine | `pt_out_coarse` | 82.76 (145) | 91.03 (145) | 93.79 (145) |
| pilot_web/point_web_fine | `pt_out_fine` | 81.94 (144) | 87.50 (144) | 89.58 (144) |
| point_phone/point_cua | `pt_coarse` | 29.27 (41) | 31.71 (41) | 34.15 (41) |
| point_phone/point_cua | `pt_in_coarse` | 92.68 (41) | 73.17 (41) | 78.05 (41) |
| point_phone/point_cua | `pt_out_coarse` | 68.29 (41) | 85.37 (41) | 87.80 (41) |
| point_phone/point_cua_fine | `pt_coarse` | 20.00 (40) | 17.50 (40) | 30.00 (40) |
| point_phone/point_cua_fine | `pt_fine` | 2.50 (40) | 10.00 (40) | 30.00 (40) |
| point_phone/point_cua_fine | `pt_in_coarse` | 95.00 (40) | 57.50 (40) | 75.00 (40) |
| point_phone/point_cua_fine | `pt_in_fine` | 80.00 (40) | 75.00 (40) | 92.50 (40) |
| point_phone/point_cua_fine | `pt_out_coarse` | 65.00 (40) | 77.50 (40) | 82.50 (40) |
| point_phone/point_cua_fine | `pt_out_fine` | 80.00 (40) | 82.50 (40) | 82.50 (40) |
| point_phone/point_own | `pt_coarse` | 16.90 (71) | 19.72 (71) | 46.48 (71) |
| point_phone/point_own | `pt_in_coarse` | 71.83 (71) | 76.06 (71) | 81.69 (71) |
| point_phone/point_own | `pt_out_coarse` | 85.92 (71) | 88.73 (71) | 95.77 (71) |
| point_phone/point_own_fine | `pt_coarse` | 24.14 (58) | 22.41 (58) | 53.45 (58) |
| point_phone/point_own_fine | `pt_fine` | 34.48 (58) | 25.86 (58) | 58.62 (58) |
| point_phone/point_own_fine | `pt_in_coarse` | 74.14 (58) | 81.03 (58) | 86.21 (58) |
| point_phone/point_own_fine | `pt_in_fine` | 84.48 (58) | 82.76 (58) | 82.76 (58) |
| point_phone/point_own_fine | `pt_out_coarse` | 89.29 (56) | 87.50 (56) | 92.86 (56) |
| point_phone/point_own_fine | `pt_out_fine` | 80.70 (57) | 87.72 (57) | 96.49 (57) |
| pope/random | `pope` | 66.73 (1,500) | 66.87 (1,500) | 84.73 (1,500) |
| roboarena_wrist/end | `ra_instr` | 88.28 (128) | 91.41 (128) | 91.41 (128) |
| roboarena_wrist/end | `ra_score` | 40.62 (128) | 40.62 (128) | 42.97 (128) |
| roboarena_wrist/end | `ra_succ` | 91.41 (128) | 91.41 (128) | 91.41 (128) |
| roboarena_wrist/mid | `ra_dir` | 25.29 (261) | 26.44 (261) | 22.99 (261) |
| roboarena_wrist/mid | `ra_grip` | 84.67 (261) | 80.08 (261) | 90.42 (261) |
| roboarena_wrist/mid | `ra_instr` | 87.74 (261) | 88.89 (261) | 90.80 (261) |
| roboarena_wrist/mid | `ra_prog` | 63.98 (261) | 63.98 (261) | 63.98 (261) |
| roboarena_wrist/pref | `ra_pref` | 34.67 (75) | 44.00 (75) | 40.00 (75) |
| robot_long/libero10 | `r2_dir` | 38.83 (188) | 31.91 (188) | 52.66 (188) |
| robot_long/libero10 | `r2_done` | 95.74 (188) | 95.74 (188) | 97.87 (188) |
| robot_long/libero10 | `r2_first` | 87.23 (188) | 85.64 (188) | 93.62 (188) |
| robot_long/libero10 | `r2_grasp` | 87.77 (188) | 87.77 (188) | 87.77 (188) |
| robot_long/libero10 | `r2_hold` | 71.28 (188) | 71.28 (188) | 82.45 (188) |
| robot_long/libero10 | `r2_instr` | 97.34 (188) | 98.94 (188) | 96.28 (188) |
| robot_long/libero10 | `r2_phase` | 85.11 (188) | 88.83 (188) | 90.96 (188) |
| robot_long/libero10 | `r2_prog` | 75.00 (188) | 67.55 (188) | 78.72 (188) |
| safety/hagrid | `hg1` | 98.40 (500) | 99.00 (500) | 99.60 (500) |
| safety/hagrid | `hg2` | 98.80 (500) | 99.20 (500) | 99.80 (500) |
| safety/hagrid | `hg3` | 96.00 (500) | 99.00 (500) | 99.20 (500) |
| snake/snake | `sn_act` | 75.33 (300) | 73.67 (300) | 78.00 (300) |
| snake/snake | `sn_crash` | 71.00 (300) | 71.67 (300) | 72.33 (300) |
| snake/snake | `sn_food` | 90.33 (300) | 90.67 (300) | 94.33 (300) |
| snake/snake | `sn_len` | 91.00 (300) | 90.67 (300) | 88.67 (300) |
| snake/snake | `sn_reach` | 90.33 (300) | 87.67 (300) | 89.00 (300) |
| video/coin | `c1_0` | 18.82 (85) | 27.06 (85) | 23.53 (85) |
| video/coin | `c1_1` | 21.18 (85) | 25.88 (85) | 34.12 (85) |
| video/coin | `c1_neg` | 87.10 (31) | 80.65 (31) | 96.77 (31) |
| video/coin | `c2_n0` | 81.18 (85) | 84.71 (85) | 87.06 (85) |
| video/coin | `c2_n1` | 76.47 (85) | 76.47 (85) | 77.65 (85) |
| video/coin | `c2_p0` | 75.29 (85) | 80.00 (85) | 84.71 (85) |
| video/coin | `c2_p1` | 77.78 (81) | 81.48 (81) | 77.78 (81) |
| video/coin | `c3_n` | 83.53 (85) | 78.82 (85) | 85.88 (85) |
| video/coin | `c3_p` | 83.53 (85) | 85.88 (85) | 80.00 (85) |
| video/coin | `c4` | 67.74 (62) | 77.42 (62) | 75.81 (62) |
| video/coin | `c5` | 100.00 (85) | 100.00 (85) | 98.82 (85) |
| video/coin | `c6` | 58.82 (85) | 61.18 (85) | 65.88 (85) |
| video/coin | `c7` | 36.47 (85) | 40.00 (85) | 38.82 (85) |
| video/coin | `p1_0` | 27.06 (85) | 32.94 (85) | 24.71 (85) |
| video/coin | `p1_1` | 16.47 (85) | 10.59 (85) | 12.94 (85) |
| video/coin | `p2_0` | 28.24 (85) | 23.53 (85) | 71.76 (85) |
| video/coin | `p2_1` | 90.59 (85) | 92.94 (85) | 82.35 (85) |
| video/coin | `p4` | 21.18 (85) | 20.00 (85) | 28.24 (85) |
| video/coin | `p5` | 66.13 (62) | 64.52 (62) | 75.81 (62) |
| vqa/okvqa_pool | `vqa` | 63.87 (1,500) | 79.60 (1,500) | 93.47 (1,500) |
| web/web_train | `w1` | 36.23 (276) | 34.42 (276) | 61.59 (276) |
| web/web_train | `w1a` | 0.00 (24) | 4.17 (24) | 8.33 (24) |
| web/web_train | `w2` | 87.33 (300) | 88.00 (300) | 88.00 (300) |
| web/web_train | `w3` | 72.67 (300) | 79.00 (300) | 84.67 (300) |
| web/web_train | `w4` | 84.67 (300) | 84.67 (300) | 89.67 (300) |
| web/web_train | `w5` | 56.33 (300) | 54.00 (300) | 64.33 (300) |
| webtest/web_test_task | `w1` | 30.51 (272) | 35.29 (272) | 60.29 (272) |
| webtest/web_test_task | `w1a` | 0.00 (28) | 0.00 (28) | 7.14 (28) |
| webtest/web_test_task | `w2` | 82.00 (300) | 81.67 (300) | 86.33 (300) |
| webtest/web_test_task | `w3` | 80.67 (300) | 83.00 (300) | 88.33 (300) |
| webtest/web_test_task | `w4` | 86.00 (300) | 86.00 (300) | 89.67 (300) |
| webtest/web_test_task | `w5` | 59.33 (300) | 56.67 (300) | 67.33 (300) |
| wiki/wikinav | `n1` | 26.13 (375) | 26.93 (375) | 37.87 (375) |
| wiki/wikinav | `n2` | 100.00 (375) | 100.00 (375) | 100.00 (375) |
| wiki/wikinav | `n3` | 81.33 (375) | 80.53 (375) | 80.53 (375) |
| wiki/wikinav | `n4` | 64.53 (375) | 66.67 (375) | 70.13 (375) |
| xiangqi/jsonl | `xq_from` | 24.00 (375) | 17.60 (375) | 24.53 (375) |
| xiangqi/jsonl | `xq_legal` | 11.73 (375) | 12.27 (375) | 13.60 (375) |
| xiangqi/jsonl | `xq_piece` | 37.87 (375) | 31.73 (375) | 36.80 (375) |
| xiangqi/jsonl | `xq_to` | 15.47 (375) | 10.67 (375) | 19.73 (375) |
