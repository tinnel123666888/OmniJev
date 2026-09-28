# 🗓️ OmniJev version history / 版本更新

[English README](README.md) · [中文首页](README_zh.md) · [Current release / 当前发布](https://github.com/tinnel123666888/OmniJev/releases/tag/v1.1)

`v0.8`–`v1.1` below name development and release milestones; `0.8B`, `2B` and `4B` name model sizes. Earlier development milestones did not each receive a separate public release or downloadable tag.

下列版本号表示开发与发布阶段，`0.8B / 2B / 4B` 表示参数规模。v0.9、v1.0 为开发迭代记录，没有独立的公开发布标签；不要将它们理解为可直接下载的同名正式版本。

| Version / 版本 | Status / 状态 | Main changes / 主要更新 |
| --- | --- | --- |
| 🚀 **v1.1** · 2026-09-26 | Current release / 当前正式发布 | Multi-image training and inference, three model sizes, SFT baseline and detailed results / 多图训练与推理、三尺寸权重、SFT 基线和详细评测 |
| 🛠️ **v1.0** · 2026-09-24–25 | Development milestone / 开发迭代 | Broader training mix, robot jog questions and input-pipeline repairs / 扩展混合数据、机器人点动题、输入链路修复 |
| 🧩 **v0.9** · 2026-09-24 | Development milestone / 开发迭代 | General multiple choice with abstention, two-stage grids and rebalanced sampling / 通用选择与弃权、两阶段网格定位、重平衡采样 |
| 🌱 **v0.8** · 2026-09-24 | Historical public 4B release / 历史 4B 发布 | Qwen3.5-based 4B, broader decision tasks and a shared API / Qwen3.5 4B、多领域决策任务与统一接口 |

## 🚀 v1.1 — multi-image release / 多图正式发布

- **Models / 模型：** Released the 0.8B, 2B and 4B decision adapters and heads, plus a separate generative SFT 0.8B baseline. / 发布三尺寸决策模型的适配器与预测头，以及独立的生成式 SFT 0.8B 基线。
- **Inputs / 输入：** Enabled ordered multi-image panels throughout the v1.1 decision-model training stage, evaluation and serving; repaired the VQA and LongVideoBench image-path handling. This fixes which images reach the model, without attributing all score changes to the panel mechanism. / v1.1 决策模型训练阶段、评测及服务统一启用按顺序编号的多图拼板，修复 VQA 与 LongVideoBench 图片路径；输入修复与性能归因分别记录。
- **Inference / 推理：** Shipped compatible inference code, per-type temperatures and optional binary `noul` bias applied before temperature scaling. Old metadata without that bias retains its zero-bias behavior. / 同步兼容推理代码、按题型温度和可选的是非题偏置；先偏置、后温度，旧元数据缺省偏置为零。
- **Results / 评测：** Published base/SFT/decision-model comparisons, calibration and latency reports, and audited all 41,951 SFT judgments. Later documentation separates dataset/subset and question-type scores, records missing coverage, and withdraws the defective A-OKVQA yes/no aggregate. / 发布基膜、SFT、决策模型对照、校准与延迟报告，核查全部 41,951 条 SFT 判分；随后补充逐数据集、子集及题型分数，标明未测项，撤回有标签缺陷的 A-OKVQA 是非题汇总。
- **Downloads / 下载：** Version-pinned Hub weights and GitHub archives with checksums. / 提供固定版本的 Hub 权重、GitHub 下载包与校验和。

[Release and weights / 发布与权重](https://github.com/tinnel123666888/OmniJev/releases/tag/v1.1) · [Dataset scores / 逐数据集得分](docs/dataset_scores_v11.md) · [Detailed historical reports / 历史详细报告](docs/results_v11_zh.md) · [Replay gallery / 回放演示](docs/demos_v11.md)

The comparisons preserve their sample and input limitations; they are not a matched-input ablation. The SFT and base-model paths did not share the decision model's multi-image input handling. Recorded-trajectory demos do not establish closed-loop gameplay or robot success rates.

这些对照保留各自样本和输入差异，不是严格同输入消融。SFT 与基膜路径未采用决策模型相同的多图处理；轨迹回放也不代表游戏或机器人的闭环成功率。

## 🛠️ v1.0 — broader inputs and robot jog questions / 扩展输入与机器人点动

- Added LIBERO and Bridge robot jog questions: translation/rotation axes, move size, gripper state and action duration. These are typed decision labels, not a released continuous-control head. / 新增 LIBERO、Bridge 的平移轴、旋转轴、步长、夹爪和持续时间题目；当时仍是类型化决策标签。
- Connected previously built but unpackaged long-text, TextVQA, expanded audio, video, safety and phone data to the training mix. / 将此前已构建但未打包的长文本、TextVQA，以及扩展的音频、视频、安全和手机数据接入训练混合。
- Added RoboArena wrist-camera inputs and diagnosed the separate bug that discarded all but the first image. The complete multi-image training path became the next version's focus. / 补充 RoboArena 腕部相机，并发现多图只读首图的独立问题；完整多图训练随后成为 v1.1 的重点。
- Bounded long-text inputs to resolve repeatable training failures; identified empty VQA/LVB evaluations caused by missing media paths and reran those evaluations. / 限制长文本输入长度以修复重复训练崩溃，定位并补跑图片路径缺失导致的空评测。

This was an intermediate training iteration, not a separate public GitHub/Hub release tag. / 这是中间训练迭代，没有独立的 GitHub/Hub 正式发布标签。

## 🧩 v0.9 — general decisions and two-stage pointing / 通用判断与分步定位

- Introduced general visual multiple-choice questions with an explicit “none of the above” target. / 引入通用视觉选择题和明确的“以上都不是”目标。
- Added coarse-to-fine pointing: select one of 12 blocks, then one of 8 cells, covering the original 96-cell grid. / 将 96 格定位拆成“12 个区域选一，再从 8 个格子选一”。
- Rebalanced replay sampling across general understanding, operation, embodied tasks and games. / 调整通用理解、操作、具身与游戏的重放采样比例。
- Built further data expansions; several were only connected to training in v1.0. Planned pool sizes are not treated as verified training counts. / 继续构建扩展数据，其中部分直到 v1.0 才实际接入；计划数据规模不等于已核验训练条数。

This was a development milestone; no standalone v0.9 public weights tag is available. / 本阶段为开发迭代，没有独立的 v0.9 公开权重标签。

## 🌱 v0.8 — Qwen3.5 public 4B line / Qwen3.5 4B 发布线

- Replaced the earlier Qwen3-VL public 4B checkpoint with a Qwen3.5-4B-based decision model. / 将早期公开的 Qwen3-VL 4B 权重更新为基于 Qwen3.5-4B 的决策模型。
- Expanded the game, robot-scene and board-game task mix, including region-based from-square/to-square chess decisions. / 扩展游戏、机器人场景和棋类题目，加入基于棋盘区域的起点、终点分步选择。
- Kept the shared `choice`, `noul` and `score` API: probabilities in one forward pass, with no generated answer tokens. / 延续 `choice`、`noul`、`score` 统一接口，一次前向输出概率，不生成答案 token。
- Unified the public Qwen3.5 size names and remeasured latency on a common card. The public 4B checkpoint at this stage was the v0.8 line; the smaller sizes retained their own checkpoint histories. / 统一公开 Qwen3.5 尺寸命名，并在同一卡上重测延迟；该阶段公开 4B 属于 v0.8 发布线，小尺寸保留各自的权重沿革。

The historical v0.8 numbers used the first-image-only path. They should not be presented as a controlled comparison with v1.1 multi-image results. Earlier public weights are preserved at [pre-v1.1-20260926](https://huggingface.co/tinnel123/OmniJev/tree/pre-v1.1-20260926).

历史 v0.8 分数使用只读首图的路径，不能与 v1.1 多图结果包装成严格受控对照。此前公开权重保存在上述历史快照中。

## 📝 2026-09-28 — documentation and demo maintenance / 文档与演示维护

- Added this v0.8–v1.1 history and links from both READMEs. / 补充版本沿革与中英文首页入口。
- Withdrew the Mario demo from the current gallery, media files, compilation and Release download pack. Kept the historical dataset scores and their limitations in the score audit. / 从当前画廊、媒体文件、合集及 Release 下载包撤下马里奥演示；保留成绩审计中的历史分数与局限说明。
- Retained seven original clips, with 181 states and 527 questions; rebuilt the compilation from their saved outputs. This is a presentation update, not new inference, training or a new model release. / 保留原有七支短片、181 个状态和 527 个问题，用已保存输出重做合集；此次是展示更新，没有新增推理、训练或模型发布。
