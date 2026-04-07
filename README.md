# 镜界.SKILL

把 `故事概念` 变成 `可执行的生成式视频制作包`。  
这个项目是一个面向 Codex 的 Skill，覆盖从 `剧本`、`分镜`、`素材清单` 到 `图片提示词`、`视频提示词`、`Google Flow 操作包` 的完整链路。
它现在也包含一套 `nightly intelligence + knowledge review` 闭环，用来持续跟踪模型、平台和创作工作流变化。
仓库本体不是独立 Web 产品，而是一个 `Codex skill package + knowledge automation repo`。

> 为 `Veo 3.1`、`Nano Banana`、`Seedance` 和 `Google Flow` 准备的结构化生成式视频工作流。

Skill 调用名：`$gen-video`

## Why

大多数“视频提示词”方案的问题，不是不会写 prompt，而是缺少制作流程。

常见失败点通常出在这里：

- 模型没选，先开始写
- 平台没分流，交付物形态不对
- 长片还在用“一条万能 prompt”的思路
- 真实题材没有核验，最后变成泛化国风
- 情绪片把 AI 写成主角，故事反而空了

这个项目的目标，是把这些容易失控的环节前置成规则。

## 这个仓库实际是什么

如果只看仓库名，很容易误以为它是一个“直接生成视频”的产品。

实际不是。

这个仓库当前实际包含四类东西：

- `Skill 定义`
  也就是 `$gen-video` 的行为约束、输出结构、分流规则和默认交付方式。

- `参考资料与执行模板`
  也就是 `references/` 和 `examples/`，用于承接 `Google Flow`、`Veo`、`Nano Banana`、`Seedance` 等不同路线的实操资料。

- `知识闭环`
  也就是 `knowledge/`，负责来源卡、wiki、候选队列、nightly review、query writeback 和人工入库闸门。

- `自动化脚本与 CI`
  也就是 `scripts/` 和 `.github/workflows/knowledge-refresh.yml`，负责把知识库的巡检、发现、lint 和 nightly review 跑起来。

所以 README 需要同时服务两种读者：

- 使用 skill 的人
- 维护 skill 和知识闭环的人

## 它解决什么问题

很多“视频提示词”项目只给一段 prompt，但真实制作通常需要更多：

- 先选模型，而不是一上来就乱写
- 先定平台，再决定交付形态
- 先把故事拆成镜头，再谈生成
- 真实题材要先核验，不然很容易写成空泛国风
- 在 `Google Flow` 里做长片时，真正需要的是 `素材图 -> 镜头 -> 存帧 -> 回灌 -> 拼接` 的操作包

这个 Skill 的目标，就是把这些前置判断变成固定流程。

## Features

- `模型选择门`
  模型未明确时，先停在选择问题，不抢跑。

- `模型 / 平台双分流`
  不只区分 `Veo / Nano Banana / Seedance`，也区分 `Google Flow` 与纯提示词交付。

- `真实题材锚点`
  对非遗、地方风貌、真实职业和现实人物题材，先提炼不可漂移的真实性约束。

- `Flow 操作包`
  输出不止是 prompt，还包括素材图顺序、镜头表、存帧、回灌和 `Scenebuilder` 拼接建议。

- `情绪片约束`
  对催泪现实题材，限制 AI 抢戏，要求高潮从真实物件和真实动作长出来。

- `知识库驱动`
  采用 `raw source -> wiki -> profiles / benchmarks` 的知识分层，持续刷新信息并支持旧规则退役。

- `CI 自动巡检`
  用 GitHub Actions 定时刷新来源卡、metadata watchlist 和复查状态，不让知识库只靠手工维护。

- `发现层`
  额外扫描官方博客、模型发布页和知名 bloger 入口，把未纳入主 registry 的候选项单独排队。

- `语义 lint`
  自动找 wiki、source card、registry 和 query-resolution 之间的不一致，而不是只看来源有没有更新。

- `query writeback`
  把用户反复问的问题显式登记成长期 backlog，避免知识只活在聊天上下文里。

- `issue 收藏夹入口`
  可以把 GitHub issue 当作手工收藏夹补充入口，但它不再是主情报路径。

- `夜间情报审阅`
  每天晚上自动聚合 HN、watched feeds 和 creator 线索，先生成 review 包，再由人决定是否入库。

- `人工入库闸门`
  所有夜间情报先进入 review，不直接改写 wiki 或主 registry。

- `可选 LLM 综合`
  如果配置了模型密钥，CI 会把夜间情报和现有知识对照后压成一份 review brief；没配时退化为 prompt-pack。

- `API-first 思路`
  能走 `API / feed / batch` 的环节尽量不绑死在网页等待里；只有供应商没开放稳定可编程入口的步骤，才保留在 UI 中人工执行。

- `视频来源分层处理`
  `YouTube` 优先 `feed / transcript`，`Bilibili` 优先 `metadata / 字幕 / ASR / 必要时切片上传`，不假设站内 URL 能直接像开放平台链接一样喂给模型。

- `分层架构`
  把稳定规则、模型档案、执行模式和 benchmark 分开，避免 skill 因模型升级快速过时。

## 能力范围

| 维度 | 支持内容 |
| --- | --- |
| 图片模型 | `Nano Banana 2`、`Nano Banana Pro`、`Nano Banana` |
| 视频模型 | `Veo 3.1`、`Seedance` |
| 执行平台 | `Google Flow`、纯提示词交付 |
| 适合题材 | 剧情短视频、非遗、地方文化、现实人物、催泪亲情向 |
| 交付形式 | 剧本、分镜、素材表、图片提示词、视频提示词、Flow 操作清单 |

## 输出内容

根据任务不同，Skill 会产出以下内容中的一部分或全部：

- 剧情结构与四幕 beat
- 单镜头或单集分镜
- 角色 / 场景 / 道具资产表
- 图片生成提示词
- 视频生成提示词
- `Google Flow` 镜头表
- `Google Flow` 关键帧 / 回灌 / 拼接建议
- 项目级交付文件建议

## Workflow

一个典型项目通常按下面的顺序展开：

1. 选择模型栈
2. 明确执行平台
3. 读取对应 `profile`
4. 选择 `native / hybrid / manual`
5. 提炼故事与 beat
6. 锁定真实性锚点
7. 建立角色 / 场景 / 道具资产表
8. 生成图片提示词
9. 生成视频提示词
10. 如果目标是 `Flow`，继续拆成镜头执行包
11. 补充存帧、回灌与拼接建议

## Architecture

这个项目现在按 `一个技能面 + 一个知识层 + 四个运行层 + 一组自动化脚本` 组织：

- `SKILL.md`
  技能入口，决定用户请求如何被分流、约束和组织。

- `knowledge`
  长期知识层，参考 Karpathy 提出的 `raw knowledge base + LLM wiki` 思路，负责沉淀原始资料、综合判断和更新日志。

- `core`
  稳定规则，不随单个模型短期能力波动而频繁变化。

- `profiles`
  模型 / 平台能力档案，用来判断某个模型原生已经会多少。

- `modes`
  `native / hybrid / manual` 三种执行方式，用来决定 skill 该接管多少。

- `benchmarks`
  样题与评测模板，用来持续判断哪些旧规则已经可以退役。

- `scripts`
  知识自动化脚本，负责 refresh、discovery、lint、nightly review、suggestions 和 writeback。

- `references`
  实际写作和执行时会被高频引用的模型说明、模板库和工作流笔记。

关系是：

- `knowledge/raw`
  保存原始来源和快照，不覆盖旧版本。

- `knowledge/wiki`
  维护可重写的能力判断、工作流经验和退役建议。

- `profiles / modes`
  把当前仍然有效、可直接执行的判断编译成工作流分流规则。

- `benchmarks`
  反过来验证这些判断还准不准，并把结果回写知识库。

这套结构的目标不是“写更多规则”，而是让 skill 在模型变强时学会后退。

## Knowledge Loop

知识库不是附属文档，而是这个 skill 的上游记忆系统。

最小闭环如下：

1. 新来源先进入 `knowledge/raw`
2. 重要结论整理进 `knowledge/wiki`
3. 与执行直接相关的结论再编译到 `profiles`
4. 用 `benchmarks` 跑样题，检查这些规则是否仍然成立
5. 把更新、失败点和退役决定写回 `knowledge/log.md`

现在这条链路还多了一层自动化：

- `source-registry.json` 维护可跟踪来源
- CI 定时抓取来源 metadata，刷新 `knowledge/status.md`
- 当上游页面变化或来源到期复查时，知识库会自动出现 watchlist 信号
- `discovery-registry.json` 扫描更广的官方和 bloger 入口，把新模型 / 新经验帖写进 `knowledge/candidates.md`
- `semantic_lint_knowledge.py` 把结构不一致写进 `knowledge/lint.md`
- `build_knowledge_suggestions.py` 把各种信号压成 `knowledge/suggestions.md`
- `ingest_github_issue_sources.py` 把 GitHub issue 收藏夹写进 `knowledge/issue-inbox.md`
- `build_nightly_review.py` 把 HN 和 watched feeds 写进 `knowledge/nightly-review.md`
- `synthesize_nightly_review.py` 把夜间情报压成 `knowledge/nightly-review-llm.md`
- `query-log.json` 与 `writeback-queue.md` 负责把 recurring question 回写成长期知识任务

当前主路径已经是：

1. nightly discovery
2. nightly review
3. optional LLM synthesis
4. human admit / defer / reject
5. 再决定是否进入 `source-registry`、`wiki` 或下游文档

`issue inbox` 现在是补充入口，不是主入口。

推荐节奏：

- 高频项：模型能力、平台 UI、工作流支持矩阵
  建议每周或每两周刷新一次

- 中频项：最佳实践、交付结构、组合工作流
  建议每月整理一次

- 低频项：叙事结构、真实性锚点、质量门
  只有在 benchmark 长期失真时才调整

## 核心规则

- 先锁模型，再写提示词
- 模型没选时，先停在选择问题，不抢跑
- 平台和模型分流，不把两者混为一谈
- 真实题材先核验，再创作
- AI / 特效在现实题材中是工具，不应抢主角位置
- 高潮必须从真实物件或真实动作长出来
- 收尾优先回到最细的情感动作

## 快速开始

在 Codex 中调用：

```text
$gen-video
```

如果你是“用这个 skill 产出视频生产包”的使用者，通常只需要这一层入口。

## 双入口

这个仓库现在有两个真实入口，不应该混成一个理解。

### 1. 使用者入口

- 在 Codex 里调用 `$gen-video`
- 给出故事、平台、模型栈和目标时长
- 获取剧本、素材表、提示词和 `Flow` 操作包

### 2. 维护者入口

- 查看 [`SKILL.md`](./.codex/skills/gen-video/SKILL.md)
- 查看 [`knowledge/index.md`](./.codex/skills/gen-video/knowledge/index.md)
- 本地运行 `scripts/*.py`
- 或直接依赖 [knowledge-refresh.yml](./.github/workflows/knowledge-refresh.yml) 的 nightly CI

如果你现在关注的是“知识库怎么更新、nightly review 怎么跑、CI 在做什么”，应该优先走第 2 条入口，而不是只看 prompt 示例。

示例 1：

```text
使用 $gen-video，把这个故事改写成适合 Google Flow 的完整操作包。
```

示例 2：

```text
使用 $gen-video，把这个非遗题材改写成 Veo 3.1 + Nano Banana 2 的剧本、分镜和提示词。
```

示例 3：

```text
使用 $gen-video，把这个现实题材催泪短片拆成剧本、素材图清单、视频镜头表和 Flow 拼接步骤。
```

## Flow 路线怎么理解

如果用户明确说会在 `Google Flow` 中执行，这个 Skill 不会只给一组 prompt，而会倾向于输出：

1. 项目设置建议
2. Nano Banana 素材图清单
3. 按镜头拆分的视频提示词
4. 每条镜头建议的 Flow 工作流
5. 存帧与回灌点
6. `Scenebuilder` 拼接顺序
7. 后期音频补配建议

这也是它和普通“提示词生成器”最大的区别。

如果目标是 `Flow UI` 里直接复制粘贴，提示词可以直接给 `全中文版本`，不需要机械坚持英文优先。

## 执行现实

这个 Skill 的核心是 `编排`，不是假装所有平台都已经有完美稳定的 API executor。

- 能自动化的环节，优先走 `API / RSS / feed / transcript / batch job`
- 还没有稳定程序化入口、或者 UI 能力明显强于 API 的环节，保留 `human-in-the-loop`
- 目标不是“完全无人值守”，而是尽量减少 `长时间等网页、反复点按钮、失败后重跑整条链路` 的浪费

当前更适合 API 化的环节通常包括：

- 知识抓取与夜间情报聚合
- 标题、简介、feed 和 source metadata 收集
- 字幕、转录、ASR 与摘要
- 已开放接口的图片生成、视频理解、批量任务

当前仍常常需要人工盯控的环节通常包括：

- `Google Flow` 里的镜头编排、存帧、回灌与 `Scenebuilder` 拼接
- 某些模型最新功能先在网页首发、API 还没跟上时的实验期工作流
- 需要主观审美判断和连续性判断的最终镜头取舍

## 视频理解与来源处理现状

这个项目已经把“发现视频经验”与“理解视频内容”区分开了，不再混成一个动作。

- `YouTube`
  当前推荐路径是 `feed -> metadata -> transcript / subtitle -> 摘要 -> 必要时视频文件理解`

- `Bilibili`
  当前更稳的路径是 `链接发现 -> metadata -> 字幕或 ASR -> 摘要 -> 必要时导出片段再做视频理解`

- `X / Twitter`
  更适合做 `创作者线索、线程经验、外链发现`，不是当前版本里最稳的视频主入口

这意味着当前仓库已经支持：

- 把 `YouTube RSS / watched feeds / HN / GitHub issue inbox` 纳入 nightly review
- 把“视频相关经验帖”纳入知识闭环
- 把“是否值得入库”留给人工最终判断

当前仓库还没有完整做完的是：

- `YouTube` 视频本体级理解的正式流水线
- `Bilibili / X` 的稳定原生 adapter
- 从 nightly review 直接投递到你的外部通知面

## 成本分层

这套体系默认不应该把所有新来源都直接丢给最贵的模型。

- `低成本`
  `HN / RSS / issue inbox / 标题 / 简介 / metadata / nightly review`

- `中成本`
  `字幕抓取 / transcript / ASR / 摘要整合`

- `高成本`
  `完整视频文件理解 / 关键帧提取 / 生成式视频 API / 大规模批量重跑`

推荐策略是：

- 先用低成本层做发现和粗筛
- 再把高价值候选送进中成本层
- 只有确认值得深挖时，才进入高成本视频理解或生成链路

## Mode Selection

`gen-video` 不再默认走最重的手工拆解。

- `native`
  模型原生能力已经足够强，skill 只补目标、锚点和交付整理。

- `hybrid`
  模型先做主生成，skill 补连续性、真实性、平台执行顺序和整理。

- `manual`
  只有在强控制度需求下，skill 才深度手工拆镜头、资产和 prompt。

默认推荐：`hybrid`

## Example Use Cases

- 把一个非遗题材改成 `3 分钟` 的现实向催泪短片
- 把一个小说梗概改成 `Veo 3.1 + Nano Banana 2` 的分镜包
- 把一个广告概念拆成 `Google Flow` 可直接执行的镜头表
- 把一个粗略故事扩成包含 `素材图 + 视频镜头 + 拼接步骤` 的完整生产资料

## 仓库结构

```text
.
├─ .codex/
│  └─ skills/
│     └─ gen-video/
│        ├─ agents/
│        │  └─ openai.yaml
│        ├─ SKILL.md
│        ├─ benchmarks/
│        ├─ core/
│        ├─ knowledge/
│        ├─ modes/
│        ├─ profiles/
│        ├─ references/
│        └─ scripts/
├─ .github/
│  ├─ ISSUE_TEMPLATE/
│  │  └─ knowledge-source.yml
│  └─ workflows/
│     └─ knowledge-refresh.yml
├─ examples/
│  ├─ README.md
│  ├─ Flow_现实题材操作包.md
│  ├─ Flow_完整操作清单样例.md
│  ├─ Veo_NanoBanana_剧情短片提示词包.md
│  └─ Seedance_分镜输出示例.md
├─ 最后一班放映机_剧本.md
└─ README.md
```

## 关键文件

- [`agents/openai.yaml`](./.codex/skills/gen-video/agents/openai.yaml)
  Skill 在宿主中的展示名、简述和默认调用提示。

- [`SKILL.md`](./.codex/skills/gen-video/SKILL.md)
  主技能说明，定义模型选择门、平台分流、真实性要求、输出结构和质量检查。

- [`references/`](./.codex/skills/gen-video/references)
  高密度参考资料目录，包含 `Google Flow`、`Veo + Nano Banana`、`Seedance`、模板库、交付模板和工作流决策树。

- [`core/output-contract.md`](./.codex/skills/gen-video/core/output-contract.md)
  稳定输出契约，定义无论走哪种生成路径，最后都应尽量交付什么。

- [`knowledge/README.md`](./.codex/skills/gen-video/knowledge/README.md)
  长期知识层入口，说明 `raw / wiki / schema / log` 之间的职责分工。

- [`knowledge/index.md`](./.codex/skills/gen-video/knowledge/index.md)
  当前知识库的优先入口，适合先看最新变化和高价值页面。

- [`knowledge/status.md`](./.codex/skills/gen-video/knowledge/status.md)
  CI 生成的 watchlist，总结到期复查、upstream metadata 变化和缺失目标。

- [`knowledge/candidates.md`](./.codex/skills/gen-video/knowledge/candidates.md)
  CI 生成的候选队列，显示发现层抓到但尚未纳入主 registry 的新来源。

- [`knowledge/suggestions.md`](./.codex/skills/gen-video/knowledge/suggestions.md)
  CI 生成的更新优先级队列，用来回答“下一步最该改什么”。

- [`knowledge/lint.md`](./.codex/skills/gen-video/knowledge/lint.md)
  CI 生成的语义 lint 报告，用来找知识层内部的不一致。

- [`knowledge/github-issue-inbox.json`](./.codex/skills/gen-video/knowledge/github-issue-inbox.json)
  GitHub issue 收藏夹配置，决定读取哪类 issue。适合手工补充，不是主情报路径。

- [`knowledge/issue-inbox.md`](./.codex/skills/gen-video/knowledge/issue-inbox.md)
  GitHub issue 收藏夹的处理结果，展示提取出的新来源摘要和关闭动作。

如果你想让 CI 读取“分配给你个人账号”的跨仓库 issue，而不是只读当前仓库 issue，需要在仓库 secret 中配置 `GH_ISSUE_INBOX_TOKEN`，并把 `github-issue-inbox.json` 的 `mode` 改成 `assigned`。

- [`knowledge/nightly-review-registry.json`](./.codex/skills/gen-video/knowledge/nightly-review-registry.json)
  夜间情报入口配置，用来定义 HN 和 watched feeds。当前更适合 `HN + YouTube RSS + 自备的 Bilibili/X feed bridge`。

- [`knowledge/nightly-review.md`](./.codex/skills/gen-video/knowledge/nightly-review.md)
  每晚自动生成的情报审阅包，作为人工最终入库前的 review gate。

- [`knowledge/nightly-review-llm.md`](./.codex/skills/gen-video/knowledge/nightly-review-llm.md)
  LLM 综合后的 nightly review brief；如果没配 LLM key，则输出可直接投喂模型的 prompt-pack。

- [`knowledge/nightly-review.json`](./.codex/skills/gen-video/knowledge/nightly-review.json)
  夜间审阅包的结构化数据版本，便于后续接 admit / defer / reject 工作流。

- [`knowledge/query-log.json`](./.codex/skills/gen-video/knowledge/query-log.json)
  显式记录 recurring question，避免闭环只围绕来源刷新而不围绕真实使用问题。

- [`knowledge/writeback-queue.md`](./.codex/skills/gen-video/knowledge/writeback-queue.md)
  query memory 生成的 backlog 队列，提示哪些问题还没沉淀进 wiki 或下游文档。

- [`knowledge/wiki/operations/knowledge-automation-surface.md`](./.codex/skills/gen-video/knowledge/wiki/operations/knowledge-automation-surface.md)
  解释 `自动复核 / 新来源发现 / 找出不一致 / suggestions / writeback` 分别在哪个脚本和哪一层做。

- [`knowledge/wiki/concepts/karpathy-gap-analysis.md`](./.codex/skills/gen-video/knowledge/wiki/concepts/karpathy-gap-analysis.md)
  解释当前实现和 Karpathy 风格 `raw knowledge base + LLM wiki` 之间已经补上的部分，以及还没完全做到的部分。

- [`scripts/refresh_knowledge.py`](./.codex/skills/gen-video/scripts/refresh_knowledge.py)
  刷新 tracked sources、source card、metadata capture、`status.md/json` 和 index 状态摘要。

- [`scripts/build_nightly_review.py`](./.codex/skills/gen-video/scripts/build_nightly_review.py)
  聚合 `HN + watched feeds + issue inbox/candidates 对照`，生成 `nightly-review.md/json`。

- [`scripts/synthesize_nightly_review.py`](./.codex/skills/gen-video/scripts/synthesize_nightly_review.py)
  在配置 LLM key 时生成审阅稿；未配置时退化成 prompt-pack。

- [`scripts/build_knowledge_suggestions.py`](./.codex/skills/gen-video/scripts/build_knowledge_suggestions.py)
  把 `status / candidates / nightly review / query log / issue inbox` 压成更新优先级。

- [`knowledge/source-registry.json`](./.codex/skills/gen-video/knowledge/source-registry.json)
  持续跟踪的官方来源注册表，用来驱动自动刷新。

- [`knowledge/discovery-registry.json`](./.codex/skills/gen-video/knowledge/discovery-registry.json)
  发现层注册表，用来巡检新模型、新官方文章和知名 bloger 经验帖。

- [`profiles/README.md`](./.codex/skills/gen-video/profiles/README.md)
  模型 / 平台能力档案入口，用来判断 skill 应该退后还是接管。

- [`modes/README.md`](./.codex/skills/gen-video/modes/README.md)
  `native / hybrid / manual` 三种执行模式的说明。

- [`benchmarks/README.md`](./.codex/skills/gen-video/benchmarks/README.md)
  benchmark 入口，用来持续比较不同模式和不同模型路径的效果。

- [`references/google-flow-notes.md`](./.codex/skills/gen-video/references/google-flow-notes.md)
  `Google Flow` 专项说明，强调 `素材图 -> 镜头 -> 存帧 -> 回灌 -> Scenebuilder` 的执行路径，以及 `Flow` 直贴场景下中文提示词也可直接使用。

- [`examples/README.md`](./examples/README.md)
  最小可复制示例入口，按 `Flow / Veo + Nano Banana / Seedance` 三条主路组织。

- [`examples/Flow_完整操作清单样例.md`](./examples/Flow_完整操作清单样例.md)
  面向 `Google Flow` 的一步一步执行模板，适合已经拿到剧本和镜头表后的落地阶段。

- [`最后一班放映机_剧本.md`](./最后一班放映机_剧本.md)
  当前项目中的样例剧本，基于老电影院放映员与现实题材催泪短片方向整理。

## 适合什么

- 需要结构化交付的剧情短视频项目
- 需要同时兼顾模型与平台差异的多模型工作流
- 真实地点 / 非遗 / 地方文化 / 现实人物题材
- 想直接在 `Google Flow` 中执行的生成式视频项目

## 不适合什么

- 只要一句超短 prompt 的极简任务
- 与结构化交付无关的随手创意片段
- 纯图片海报、纯排版设计、纯剪辑工程说明

## 当前状态

目前这个项目已经完成这些增强：

- 根入口已经明确分成 `skill 使用面` 与 `knowledge automation 维护面`
- 现有视频生成主路径仍在，`knowledge / nightly review` 是增强层，不是替换层
- 模型选择门已经收紧，避免未选模型就直接开写
- `Google Flow` 已经从普通提示词输出升级为专项工作流
- 真实题材与非遗题材增加了真实性锚点要求
- 儿童角色场景增加了平台内语音依赖限制说明
- Skill 调用名已统一保持为 `gen-video`
- skill 已扩成 `knowledge + core / profiles / modes / benchmarks` 结构
- 已接入 nightly review 主路径，开始做夜间情报聚合与人工入库闸门
- 已支持 HN 和 watched feeds 审阅包生成
- 已支持可选 LLM 审阅稿生成
- 已明确 `API-first + human gate` 的执行边界，用来减少网页等待和失败重跑成本
- 已明确 `YouTube / Bilibili / X` 的分层来源处理思路

当前还没有完成的是：

- 可直接替代网页操作的大一统 vendor executor
- Bilibili / X 的稳定原生 source adapter
- 视频本体级理解闭环
  目前更偏向识别标题、简介、feed 元信息和外部链接，还不是完整的视频内容理解流水线

## 本地维护命令

如果你要在本地复核这套知识闭环，常用命令是这些：

```powershell
python .codex/skills/gen-video/scripts/refresh_knowledge.py
python .codex/skills/gen-video/scripts/discover_knowledge_candidates.py
python .codex/skills/gen-video/scripts/ingest_github_issue_sources.py
python .codex/skills/gen-video/scripts/build_nightly_review.py
python .codex/skills/gen-video/scripts/synthesize_nightly_review.py
python .codex/skills/gen-video/scripts/semantic_lint_knowledge.py
python .codex/skills/gen-video/scripts/build_query_writeback_queue.py
python .codex/skills/gen-video/scripts/build_knowledge_suggestions.py
```

只做一致性校验时，对应加 `--check` 即可。

## Roadmap

- 增加官方文档、发布说明和 benchmark 结果的定期刷新机制
- 增加 `API-first` 的批处理 / executor 路线，尽量把可程序化环节从网页等待里剥离出来
- 增加 YouTube 视频级理解
  优先走字幕 / transcript，再补视频理解
- 增加 Bilibili / X 的稳定 feed bridge 或 source adapter
- 增加 nightly review 的对外投递面
  例如 issue / 邮件 / 消息通知等 review 出口
- 增加 admit / defer / reject 的正式 review workflow
- 增加更多 `Flow` 实操模板
- 增加更多长片结构案例
- 增加不同情绪类型的剧本骨架
- 增加更细的镜头语言模板和镜头时长建议

## Repository Status

当前仓库更准确的定位是 `Codex skill package + references + knowledge automation`，而不是完整产品化工具。  
现阶段重点在于：

- 固化可复用的工作流规则
- 建立可持续更新的知识库和规则退役机制
- 用 CI 自动维护来源 watchlist 和复查节奏
- 用夜间情报系统持续扫新模型、新技能、新经验分享来源
- 用 nightly review + LLM synthesis + human gate 控制入库节奏
- 用 lint / suggestions / writeback 把知识维护补成真正闭环
- 积累参考资料与模板
- 验证真实题材、长片结构和 Flow 路线下的稳定输出方式
- 为后续 `API-first executor` 和更稳的多平台视频理解打地基
