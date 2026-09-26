<div align="center">

# OmniJev

**全模态 Jev · An omni-modal Jev**

*一次前向、零生成 token：对图片、视频、屏幕和机器人画面提出带类型的问题，得到校准过的概率。*

[![Website](https://img.shields.io/badge/website-omnijev.net-4F46E5)](https://omnijev.net/)
[![Weights](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-tinnel123%2FOmniJev-yellow)](https://huggingface.co/tinnel123/OmniJev)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

**北京中关村学院 · 中国科学院自动化研究所 · 智进化**

[项目首页](https://omnijev.net/) · [在线试用](https://omnijev.net/try.html) · [权重](https://huggingface.co/tinnel123/OmniJev) · [English](README.md)

</div>

---

## 它能干什么

OmniJev 基于 Qwen3.5 视觉语言底座，以 LoRA、决策头和序数头微调为多模态决策模型。v1.1 覆盖网页与手机操作、机器人画面、视频、游戏、棋类、音频频谱图和文本等任务；当前训练清单仍在审计，不沿用旧版本的 27 万记录作为本轮精确规模。

一个 4B 的模型，**能看图、看视频**，并据此做决策：**操作手机和电脑**、**实时玩游戏**、**操控机器人**、**实时监控摄像头画面**（危险、手势、事件）。它把画面、你的问题和文本上下文一起读，回答是**校准过的概率**而不是生成的文字，并且可以回答"都不是"。

## 它是什么

OmniJev 是一个 *System One* 决策模型。你不是让它写字，而是给它一个"状态"（图片、视频帧、截图、摄像头画面，可附带文本上下文）和一组**带类型的问题**，它在**一次前向、0 个生成 token** 内给每个问题返回一个概率分布：

| 类型 | 问的是 | 返回 |
|---|---|---|
| `choice` | 在这些选项里选哪个（或都不是）？ | 每个选项的概率、`abstain`（都不是的概率）、所选的 key |
| `noul` | 这个陈述对当前状态成立吗？ | 一个校准过的概率 |
| `score` | 在一个有序量表上到哪一级？ | 等级及各级概率 |

同一张截图问十二个问题，代价和问一个差不多。选项还可以是**图中的区域**（`box: [x1, y1, x2, y2]`，坐标 0–1000），"点哪个元素 / 哪一格 / 危险在哪"都是普通的选择题；视频会取 16 帧带时间戳的画面，模型看到的就是这些。

## 已发布的模型

三个尺寸，同一套代码（`mso.infer`）、同一个接口，全部 Apache-2.0，底座都是 Qwen3.5：

| 模型 | 底座 | 权重 | 下载 |
|---|---|---|---|
| **OmniJev-4B** | Qwen3.5-4B | [tinnel123/OmniJev](https://huggingface.co/tinnel123/OmniJev) · 镜像 [tinnel123/OmniJev-4B](https://huggingface.co/tinnel123/OmniJev-4B) | `hf download tinnel123/OmniJev --revision v1.1 --local-dir ckpt` · `hf download Qwen/Qwen3.5-4B --local-dir base` |
| **OmniJev-2B** | Qwen3.5-2B | [tinnel123/OmniJev-2B](https://huggingface.co/tinnel123/OmniJev-2B) | `hf download tinnel123/OmniJev-2B --revision v1.1 --local-dir ckpt` · `hf download Qwen/Qwen3.5-2B --local-dir base` |
| **OmniJev-0.8B** | Qwen3.5-0.8B | [tinnel123/OmniJev-0.8B](https://huggingface.co/tinnel123/OmniJev-0.8B) | `hf download tinnel123/OmniJev-0.8B --revision v1.1 --local-dir ckpt` · `hf download Qwen/Qwen3.5-0.8B --local-dir base` |

生成式 SFT 对照另见 [tinnel123/OmniJev-SFT-0.8B](https://huggingface.co/tinnel123/OmniJev-SFT-0.8B)。

下面的所有示例对三个模型都适用：`MSO1("ckpt", "base")` 会根据权重自动选择推理路径。`pip install fla-core` 可选，开启线性注意力快速内核。

四个权重压缩包和 SHA-256 校验清单也可从 [GitHub v1.1 Release](https://github.com/tinnel123666888/OmniJev/releases/tag/v1.1) 下载。

## 它能做什么

以下动图来自历史版本，用于展示接口和任务形式；它们不是 v1.1 权重的新演示或新延迟测量。

<table>
<tr>
<td width="50%"><img src="docs/media/web_task.gif" width="100%"><br><sub><b>二十一步网页任务，逐页决策</b> — 每一页模型都判断点哪个元素、做什么操作、是不是最后一步、任务进行到哪。</sub></td>
<td width="50%"><img src="docs/media/robots.gif" width="100%"><br><sub><b>四个机器人任务同时看</b> — 四段 LIBERO-10 任务以视频速度并行；每一帧判断子任务、夹爪下一步方向、是否该抓、是否拿住、第一阶段完成没有。</sub></td>
</tr>
<tr>
<td><img src="docs/media/game.gif" width="100%"><br><sub><b>实时玩游戏</b> — 挡板往哪动、下一个球落在哪格、炸弹要不要砸到、比分如何。每帧一次前向，没有搜索、没有规划器。</sub></td>
<td><img src="docs/media/cua_trace.gif" width="100%"><br><sub><b>一步步操作手机</b> — 下一步做什么动作、多不可逆、屏幕上有没有报错弹窗。</sub></td>
</tr>
<tr>
<td><img src="docs/media/robot_task.gif" width="100%"><br><sub><b>一段长程机器人任务</b> — 两阶段操作任务的 276 帧：指令、子任务、方向、抓取、是否拿住、第一阶段完成没有。</sub></td>
<td><img src="docs/media/robot_monitor.gif" width="100%"><br><sub><b>盯着机器人，逐帧判断</b> — 每帧五个判断；轨道上的琥珀色刻度是真实的抓取时刻。</sub></td>
</tr>
<tr>
<td><img src="docs/media/pointing.gif" width="100%"><br><sub><b>在网格上指点，不需要任何人画框</b> — 在截图和照片上铺一张 96 格的网格；模型先选格子，再放大，再选一次。</sub></td>
<td><img src="docs/media/navigation.gif" width="100%"><br><sub><b>沿着链接一步步走向目标页</b> — 每一跳选哪个链接、每个候选都有概率、到了就停。</sub></td>
</tr>
<tr>
<td><img src="docs/media/hazard.gif" width="100%"><br><sub><b>盯着摄像头看危险</b> — 有没有火或烟、哪种危险、多紧急、在哪个区域。报警条就是模型自己给的概率。</sub></td>
<td><img src="docs/media/gesture.gif" width="100%"><br><sub><b>手势控制</b> — 摄像头前的一个手势变成一条设备指令，只在模型足够有把握时才触发。</sub></td>
</tr>
<tr>
<td><img src="docs/media/events.gif" width="100%"><br><sub><b>判断视频里发生了什么</b> — 事情发生了没有、从哪一帧开始、人还在不在画面里、在做什么。</sub></td>
<td><img src="docs/media/stopwatch.gif" width="100%"><br><sub><b>十个留出样例，一个秒表</b> — 一张照片、一个手机屏幕、一盘棋、一个机器人视角、一整段视频；秒表走的就是模型实际用的时间。</sub></td>
</tr>
<tr>
<td colspan="2"><img src="docs/media/audio.gif" width="100%"><br><sub><b>用看的方式听</b> — 五秒声音画成频谱图和波形：这是什么声音、是不是人发出的、有没有突发的响声、有多响。仓库里另有<a href="docs/media/audio.mp4">带真实声音的那一版</a>。</sub></td>
</tr>
</table>

## 成绩 — v1.1，2026-09-26

[每家族完整指标与样本数](docs/results_v11_zh.md) · [聚合原始报告](docs/results_v11.json) · [发布清单](docs/release_v11.json)

### 共同 30 家族总览

家族等权平均让每个家族权重相同；按题加权按各自实际题数计算。家族平均 ECE 不是将全部预测合并后重新计算的全局 ECE。

| 模型 | 共同家族数 | 实际题数 | 家族等权准确率 % | 按题加权准确率 % | 家族平均 ECE % ↓ |
| --- | ---: | ---: | ---: | ---: | ---: |
| 基模 0.8B | 30 | 21,456 | 40.07 | 40.04 | 20.83 |
| SFT 0.8B | 30 | 41,951 | 47.86 | 48.09 | — |
| v1.1 0.8B | 30 | 41,975 | 64.52 | 65.40 | 4.30 |
| 基模 2B | 30 | 21,456 | 36.30 | 35.94 | 34.21 |
| v1.1 2B | 30 | 41,975 | 64.46 | 65.42 | 6.27 |
| 基模 4B | 30 | 21,456 | 40.12 | 39.79 | 30.04 |
| v1.1 4B | 30 | 41,975 | 70.00 | 70.82 | 5.89 |

### 全部家族准确率（%）

| 家族 | 基模 0.8B | SFT 0.8B | v1.1 0.8B | 基模 2B | v1.1 2B | 基模 4B | v1.1 4B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| androidcontrol | 29.49 | 40.73 | 71.70 | 21.54 | 71.84 | 28.81 | 77.30 |
| atari | 45.68 | 45.07 | 71.67 | 7.82 | 63.40 | 34.29 | 63.87 |
| audio | 20.71 | 44.53 | 51.07 | 35.39 | 42.01 | 34.16 | 53.08 |
| chess2 | 24.01 | 38.93 | 61.80 | 20.99 | 61.67 | 16.74 | 62.40 |
| chess3 | 5.62 | 13.00 | 20.00 | 6.17 | 15.13 | 5.49 | 22.67 |
| events | 39.09 | 48.53 | 85.87 | 48.56 | 86.47 | 55.56 | 89.13 |
| game | 41.15 | 47.33 | 83.51 | 17.15 | 80.32 | 15.36 | 90.36 |
| genmcq | 57.06 | 79.87 | 77.60 | 60.08 | 83.80 | 73.25 | 88.20 |
| gomoku | 52.54 | 45.67 | 69.80 | 18.24 | 68.27 | 16.60 | 70.60 |
| jat | 36.90 | 50.33 | 63.73 | 27.71 | 63.00 | 25.79 | 65.87 |
| jog_bridge | 28.12 | 28.80 | 43.84 | 24.14 | 48.43 | 29.36 | 45.97 |
| jog_full | 24.69 | 27.60 | 49.24 | 32.24 | 49.04 | 28.26 | 51.56 |
| longtext | 21.26 | 62.53 | 76.42 | 36.21 | 77.68 | 59.40 | 80.28 |
| lvb | 41.80 | 52.60 | 47.20 | 57.38 | 50.00 | 59.02 | 56.80 |
| mario | 27.43 | 40.14 | 53.88 | 52.13 | 54.69 | 46.78 | 56.05 |
| music | 34.98 | — | — | 32.92 | — | 34.71 | — |
| mutex | 47.33 | 50.73 | 73.33 | 25.10 | 70.73 | 25.24 | 79.07 |
| old | 53.91 | 61.60 | 67.54 | 58.44 | 66.06 | 58.02 | 70.76 |
| pilot_web | 39.51 | 37.20 | 67.13 | 37.04 | 66.47 | 42.80 | 75.80 |
| point_phone | 40.27 | 37.68 | 60.91 | 39.09 | 60.69 | 46.61 | 72.53 |
| pope | 85.46 | 84.20 | 66.73 | 82.44 | 66.87 | 86.42 | 84.73 |
| roboarena_wrist | 38.55 | 55.87 | 65.93 | 32.92 | 66.27 | 33.20 | 67.80 |
| robot_long | 54.87 | 49.80 | 79.79 | 29.77 | 78.46 | 29.36 | 85.04 |
| safety | 52.81 | 68.93 | 97.73 | 58.44 | 99.07 | 67.90 | 99.53 |
| snake | 44.03 | 47.00 | 83.60 | 34.57 | 82.87 | 44.86 | 84.47 |
| video | 39.09 | 43.47 | 57.51 | 38.41 | 59.10 | 49.11 | 62.81 |
| vqa | 79.15 | 76.47 | 63.87 | 83.26 | 79.60 | 85.73 | 93.47 |
| web | 41.02 | 48.27 | 66.87 | 31.55 | 67.53 | 31.28 | 76.80 |
| webtest | 40.47 | 48.40 | 67.13 | 26.20 | 67.87 | 30.45 | 77.40 |
| wiki | 41.84 | 47.80 | 68.00 | 39.78 | 68.53 | 33.74 | 72.13 |
| xiangqi | 8.09 | 12.87 | 22.27 | 6.31 | 18.07 | 10.15 | 23.67 |

### 评测口径与限制

以下是已有报告的描述性汇总，**不是严格同题、同输入的消融实验**。基模按候选答案概率评测（A1_raw），每家族最多先取 1000 题，再分 dev/test；v1.1 和 SFT 通常每家族约 1500 题。取样、候选截取和图像处理不同。共同 30 家族汇总不包含只有基模结果的 music。

本轮 SFT 只有 0.8B。41,951 条生成已完成 judge 和审计：原始 LLM judge 错误放行了 97 个明确错误标签，审计后准确率为 **48.0894%**（与 parser 一致），不采用未经更正的 48.3207%。

v1.1 决策模型使用多图拼板，历史 SFT 和基模评测只取第一张静态图。修复后的完整多图 SFT 重训、272,561 题全量复测尚未完成；20 步分布式验证权重不在本次发布中。

这些是项目家族评测，不能混称官方完整 benchmark 分数。POPE、LongVideoBench 未进入训练；Mind2Web 使用官方切分。其余包含自建行级留出，events 使用 Charades-STA train 视频构造题目；行级留出不证明整个 episode 未见过。

主表为原始评测报告，**不是对线上校准输出的重新测量**。发布的温度来自独立校准集，4B 还带有 `biases.noul=0.0531085661`，会移动是非题决策边界，所以原始 POPE 分数不能直接当作服务输出分数。

4B 的共同 30 家族平均准确率最高，但 POPE（84.73% 对基模 86.42%）和 LVB（56.80% 对基模 59.02%）仍回退；0.8B、2B 的 POPE 回退更大。表中保留所有结果。

### 校准

ECE 是按置信度分箱后，置信度与实际正确率的平均差距，越低越好；它不保证每一个置信度点都落在该误差范围内。完整结果还报告 Brier 和 NLL。SFT 生成报告没有保存校准后的答案概率，因此 ECE 缺失。

独立校准集包含 7,767 道 dev 和 17,754 道 test 题。温度缩放保持 argmax 准确率不变，4B 的额外是非题偏置则可能改变准确率。以下元数据只报告温度校准结果。

| 规模 | 题型 | n | 温度 T | 准确率 % | 原 ECE % | 校准 ECE % | 原 Brier | 校准 Brier | 原 NLL | 校准 NLL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.8B | noul | 5566 | 0.9574 | 86.58 | 1.94 | 1.33 | 0.1862 | 0.1864 | 0.2962 | 0.2961 |
| 0.8B | choice | 9226 | 0.9983 | 52.92 | 1.34 | 1.39 | 0.5512 | 0.5512 | 1.3374 | 1.3374 |
| 0.8B | score | 2962 | 1.0642 | 66.41 | 3.15 | 2.90 | 0.4266 | 0.4270 | 0.7694 | 0.7712 |
| 2B | noul | 5566 | 1.0181 | 86.74 | 0.93 | 0.89 | 0.1881 | 0.1881 | 0.3012 | 0.3010 |
| 2B | choice | 9226 | 1.1253 | 51.08 | 1.60 | 2.31 | 0.5612 | 0.5613 | 1.4139 | 1.4123 |
| 2B | score | 2962 | 1.0173 | 64.28 | 3.11 | 3.21 | 0.4507 | 0.4510 | 0.8170 | 0.8178 |
| 4B | noul | 5566 | 1.1991 | 89.17 | 2.35 | 1.00 | 0.1545 | 0.1530 | 0.2524 | 0.2484 |
| 4B | choice | 9226 | 1.1199 | 56.33 | 2.20 | 1.44 | 0.5155 | 0.5153 | 1.2547 | 1.2517 |
| 4B | score | 2962 | 1.1909 | 66.91 | 5.24 | 3.42 | 0.4260 | 0.4221 | 0.7504 | 0.7445 |

### 延迟

上一版在同一张空闲 A800-SXM4-40GB 上测得 1/3/6/12 问延迟：4B 为 294/292/344/436 ms，2B 为 217/220/243/277 ms，0.8B 为 216/216/218/236 ms。这是历史数据，不是 v1.1 新测的服务延迟。完整表保留 v1.1 原报告逐家族延迟，但未构成统一硬件的速度对照。三个 Qwen3.5 尺寸都走前缀分支路径。

## 快速开始

```bash
git clone https://github.com/tinnel123666888/OmniJev && cd OmniJev
python -m venv venv && ./venv/bin/pip install -r requirements.txt     # torch, transformers>=5, pillow

hf download tinnel123/OmniJev --revision v1.1 --local-dir ckpt                       # OmniJev 权重
hf download Qwen/Qwen3.5-4B --local-dir base               # 底座（或软链本地副本）
```

**图片。** questions 是 `id -> 问题` 的字典，答案按同样的 id 返回。

```python
from mso.infer import MSO1

m = MSO1("ckpt", "base")
answers = m.system_one(
    {"images": ["screen.png"]},
    {"op":   {"type": "choice", "instructions": "Which operation comes next?",
              "criteria": {"click": "tap an element", "type text": "", "scroll": ""}},
     "risk": {"type": "score",  "instructions": "How irreversible is the next action?",
              "levels": ["harmless", "needs care", "irreversible"]},
     "err":  {"type": "noul",   "instructions": "This screen shows an error dialog."}})
# answers["op"]   -> {"choice": "click", "probabilities": {"click": 0.81, ...}, "abstain": 0.02, "confidence": 0.81}
# answers["risk"] -> {"score": "needs care", "probabilities": {...}, "confidence": 0.7}
# answers["err"]  -> {"noul": 0.01}
```

**视频。** `video_state` 把 16 帧带时间戳的画面拼成一张图（需要 PATH 里有 ffmpeg 和 ffprobe），模型整体判断这段视频。

```python
from mso.video import video_state

answers = m.system_one(
    video_state("clip.mp4"),                                  # 在视频旁边写出 clip.mosaic.jpg
    {"happened": {"type": "noul",   "instructions": "The person opens the door."},
     "doing":    {"type": "choice", "instructions": "What is the person doing?",
                  "criteria": {"cooking": "", "cleaning": "", "reading": "", "eating": ""}},
     "progress": {"type": "score",  "instructions": "How much of the action is shown?",
                  "levels": ["none of it", "the beginning", "most of it", "all of it"]}})
```

**文本上下文。** 放在问题前面即可，模型会和画面一起读（线上 API 对 `state.text` 就是这么做的）。

```python
task = "Task: book a table for two at 7 pm on the restaurant's website."
answers = m.system_one(
    {"images": ["page.png"]},
    {"op":   {"type": "choice", "instructions": task + "\nWhich operation comes next?",
              "criteria": {"click": "tap an element", "type text": "", "select": "", "scroll down": ""}},
     "done": {"type": "noul",   "instructions": task + "\nThe task is finished."}})
```

**区域。** 选项可以是区域而不是名字：`"options": [{"key": "a", "region": {"box": [120, 40, 380, 90]}}, ...]`（坐标 0–1000）。`mso/templates.py` 里有浏览器、手机、机器人、游戏、网格等现成的问题模板（`templates.questions("libero", instruction=...)`），`mso/infer.py` 也可以当命令行用（`--ckpt --model --image --questions`）。问题用英文效果最好。

## 它是怎么训的

v1.1 在 Qwen3.5 的 0.8B、2B、4B 底座上使用 LoRA rank 32、决策头和序数 Score 头，启用 LM 特征、前缀分支推理和多图拼板。本轮续训分别为 5,000 / 4,000 / 3,000 步，三个尺寸前序训练历史不同，不能当作相同累计训练预算。损失采用概率评分规则；独立留出数据用于温度校准。

SFT 对照为 0.8B 的生成式 LoRA 微调，12,500 步、学习率 1e-4、accum=4；它生成文本答案，不使用 OmniJev 决策头，也不支持 `MSO1` 接口。其旧训练路径只取第一张静态图。完整训练记录清单和累计训练量尚未统一，不将本轮结果称为严格同数据对照。

## 许可与引用

**Apache-2.0**（见 [LICENSE](LICENSE)），代码和权重均适用；底座沿用其自身许可。

```bibtex
@misc{omnijev2026,
  title  = {OmniJev: an omni-modal System One decision model},
  author = {Xu, Tianrun and Fan, Hongbang and Lin, Jiahao and Zhu, Zilin and Diao, Zhenxin and Guo, Longteng and Liu, Jing},
  note   = {Beijing Zhongguancun Academy; Institute of Automation, Chinese Academy of Sciences; Zevo},
  year   = {2026},
  url    = {https://github.com/tinnel123666888/OmniJev}
}
```

## 团队与联系

OmniJev 由 **北京中关村学院**、**中国科学院自动化研究所**、**智进化** 联合研发。

主要贡献者

- 徐添润 (Tianrun Xu) · Core Developer
- 范红榜 (Hongbang Fan)
- 林佳豪 (Jiahao Lin)
- 朱子林 (Zilin Zhu)
- 刁镇薪 (Zhenxin Diao)
- 郭龙腾 (Longteng Guo) · Project Lead
- 刘静 (Jing Liu) · Corresponding Author

联系我们——学术交流、项目合作：s-xtr24@bza.edu.cn

<div align="center"><sub>北京中关村学院 · 中国科学院自动化研究所 · 智进化 · <a href="https://omnijev.net/">omnijev.net</a></sub></div>
