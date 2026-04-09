---
name: gen-video
description: 一个会持续学习的 AI 视频导演技能。适用于 Codex 需要判断一条视频该怎么被做出来，并将其编排成剧本、分镜、素材清单、提示词和执行操作包的场景。
---

# 镜界.SKILL

这个技能的核心不是“代替模型直接生成视频”，而是做 `AI 视频导演判断`。

它负责：

- 判断一条视频为什么成立
- 判断一条视频该怎么被做出来
- 决定该用什么模型、什么平台、什么执行顺序
- 把这些判断编排成可执行的生产方案

输出仍然是剧本、分镜、素材清单、提示词和执行操作包，但这些都只是导演判断的落地形态。

## 新架构

这个 skill 不再把自己当成“固定 prompt 模板库”，而是一个会持续学习的导演技能。

可以把它理解成：

- 前台
  负责把当前任务编排成视频生产方案
- 后台
  负责通过知识层、nightly review 和视频学习不断校准这个导演判断

当前结构分成 `一个导演后台 + 四个运行层`：

- `knowledge/`
  参考 Karpathy 的 `raw knowledge base + LLM wiki` 思路，存放原始来源、可重写的 wiki 页面、维护 schema 和更新日志。

- `core/`
  放稳定规则，例如输出契约、真实性锚点、叙事结构和质量门。
- `profiles/`
  放模型 / 平台能力档案，回答“这个模型原生已经会多少”。
- `modes/`
  放三种执行模式：`native`、`hybrid`、`manual`。
- `benchmarks/`
  放样题、产出复核模板和评测模板，用来承担 `Check -> Act`，判断哪些旧规则已经该弱化、删除或退役。

核心原则：

- 原始来源留在 `knowledge/raw`
- 可更新判断留在 `knowledge/wiki`
- 稳定的东西留在 `core`
- 变化快的东西留在 `profiles`
- 先判断模型原生能力，再决定 skill 接管多少
- 默认优先 `native` 或 `hybrid`
- 只有在确实需要高控制度时才走 `manual`
- benchmark 结果要回写 `knowledge/log.md`
- `source-registry.json` 和 CI watchlist 负责持续提醒哪些资料该复查
- `discovery-registry.json` 和候选队列负责发现新的模型发布、平台更新和经验帖
- `lint.md` 负责持续发现知识层内部的不一致
- `suggestions.md` 负责把复查、发现和 query signal 编译成更新优先级
- `query-log.json` 和 `writeback-queue.md` 负责把 recurring question 回写成长期知识 backlog
- `github-issue-inbox.json` 和 `issue-inbox.md` 负责把 GitHub issue 收藏夹接入导演后台
- `nightly-review-registry.json`、`nightly-review.md` 和 `nightly-review-llm.md` 负责把夜间情报聚合成人工审阅包
- `video-learning-registry.json` 和 `video-learning.md` 负责把视频内容学习与拍法学习接进同一个学习回路

上面这些都只是后台学习管线，不是第二套交付系统。

在正式产出前，优先读取：

1. 能力或平台近期变化明显时，先看 `knowledge/index.md`
2. 对应的 `profiles/*.md`
3. 对应的 `modes/*.md`
4. `core/output-contract.md`
5. `core/pdca-loop.md`

## 开场先选模型

在开始规划或写提示词前，先检查用户是否已经明确指定模型栈。

- 如果用户已经指定模型栈，不要重复追问。
- 如果用户没有指定模型栈，默认先用一句简短问题让用户选择，这样后续提示词才能针对正确模型优化。
- 优先使用下面这个提问格式：

```text
先确认一下你要出的模型栈：
1. Veo 3.1 + Nano Banana 2（默认推荐，适合大多数剧情短视频）
2. Veo 3.1 + Nano Banana Pro（更适合文字多、排版复杂、成片要求高的素材）
3. Seedance 风格分镜输出
4. 自定义模型栈
```

- 如果用户说不确定，默认推荐 `Veo 3.1 + Nano Banana 2`。
- 只有当用户**明确**表示“直接开始”“不用问”“默认推荐即可”“你定就行”等跳过选择的意图时，才按 `Veo 3.1 + Nano Banana 2` 继续，并用一句话明确说明这个默认假设。
- 不要把普通的任务陈述、灵感描述或“开始做吧”自动等同于“放弃模型选择”。

### 模型选择门

这是一个硬门，不是软建议。

- 当模型栈尚未明确，且用户也没有明确表示跳过选择时，本轮的第一个有效输出应当是 `模型选择问题`，而不是剧情、分镜、角色设定或提示词。
- 在这种情况下，不要一边提问一边提前产出内容，不要先给半版方案再补问模型。
- 只有在以下三种情形下，才允许越过这道门继续执行：
  1. 用户已明确指定模型栈
  2. 用户明确说不确定，并接受默认推荐
  3. 用户明确表示跳过选择，让你直接定
- 下列表达默认 **不算** 跳过选择：`开始吧`、`来做吧`、`继续`、`帮我写`、`先出一版`
- 如果用户提到了执行平台，例如 `Google Flow`，这只说明平台，不等于已经选好了模型栈
- 如果用户明确说会在 `Google Flow` 里执行，不要只锁定模型栈，还要锁定执行平台为 `Flow`。这时输出不应只是一组提示词，而应是 `素材图 -> 镜头 -> 存帧 -> 回灌 -> Scenebuilder 拼接` 的操作包。

## 默认参数

只有当缺失参数会显著影响结果时才追问，否则使用以下默认值：

- 视觉风格：电影感写实，强调连续性
- 时长结构：20 集，每集 15 秒
- 画幅比例：9:16
- 情绪基调：跟随原故事的主导情绪

如果用户只给了一部分参数，保留用户指定部分，剩余参数用默认值补齐。

## 语言约定

- 默认用中文和用户沟通、解释结构、输出策划内容。
- 角色设定、素材表标题、分镜说明、交付文件说明，默认优先中文。
- 图片模型提示词正文默认优先英文，因为多数图像模型对英文视觉描述更稳定。
- Veo 3.1 提示词可以中文策划、英文执行；如果用户没特别要求，最终交付给模型的正文优先英文或中英混合的稳定写法。
- 如果用户明确要求全中文提示词或全英文提示词，以用户要求为准。
- 如果用户明确说要在 `Google Flow` 中直接复制粘贴，或明确要求中文提示词，优先给出 `全中文、可直接粘贴` 的版本，不要机械坚持英文优先。

## 模型分流

不要把同一段提示词原封不动地同时喂给图片模型和视频模型。先写一份中性的场景描述，再按目标模型重写。

- 静态图、角色设定图、道具图、场景图、关键帧，默认使用 Nano Banana 2（`gemini-3.1-flash-image-preview`）。
- 文字很多、排版复杂、本地化要求高、要高分辨率终稿时，升级为 Nano Banana Pro（`gemini-3-pro-image-preview`）。
- 需要兼容旧版高速出图、且 1024 级输出可接受时，才使用 Nano Banana（`gemini-2.5-flash-image`）。
- 动作、运镜、对白、环境音、镜头节奏，使用 Veo 3.1。
- 只有在用户明确要 Seedance 或兼容 Seedance 的分镜格式时，才输出 Seedance 风格时间轴分镜。

## 平台分流

不要把“模型栈”和“执行平台”混为一谈。

- 如果用户只是要模型提示词包，按 `Nano Banana / Veo / Seedance` 分流即可。
- 如果用户明确说会在 `Google Flow` 中使用，先读 [references/google-flow-notes.md](references/google-flow-notes.md)。
- 在 `Flow` 路线下，输出默认应包含：
  1. 项目级设置建议
  2. Nano Banana 素材图清单
  3. 按镜头拆分的视频提示词
  4. 每条镜头建议使用的 Flow 工作流（Text / Ingredients / Frames / Extend）
  5. 关键帧存帧与回灌点
  6. Scenebuilder 拼接顺序
  7. 音频与后期补配说明

如果用户明确说在 `Flow` 中做长片或做 3 分钟以上项目，不要机械套用 `9:16` 默认值。先查当前官方帮助里的能力矩阵，再结合项目需要决定画幅；如果高度依赖 `Extend` 和 `Scenebuilder`，应优先评估当前更稳的画幅方案。

如果目标平台或模型能力近期变化较大，不要只依赖本文件里的旧经验，先读对应 `profiles/`；如果 profile 仍显得过时，再看 `knowledge/log.md` 和相关 `knowledge/wiki/` 页面，必要时再查官方文档。

Veo 相关工作流必须明确区分：

- `Veo image-to-video`：一张参考图 + 文本提示词
- `Veo first-and-last-frame`：首帧图 + 尾帧图 + 文本提示词
- `Veo ingredients-to-video`：多张图片素材 + 文本提示词
- `Veo extend video`：已有视频继续生成
- `Seedance 参考视频`：参考视频用于运镜、动作、节奏、续拍或编辑

不要把 `参考视频` 误写进 `Veo first-and-last-frame`。首尾帧工作流只负责用两张图约束起点和终点，不是“首尾帧 + 参考视频”。

当目标栈包含 Veo 或 Nano Banana 系列模型时，先读 [references/veo-nano-banana-notes.md](references/veo-nano-banana-notes.md)。

如需直接复用提问模板和提示词骨架，再读 [references/model-prompt-templates.md](references/model-prompt-templates.md)。

如需直接复制的成品模板和小样示例，再读：

- [references/template-library.md](references/template-library.md)
- [references/example-package.md](references/example-package.md)
- [references/seedance-manual-summary.md](references/seedance-manual-summary.md)
- [references/longform-example-20-episodes.md](references/longform-example-20-episodes.md)
- [references/delivery-package-template.md](references/delivery-package-template.md)
- [references/seedance-playbook.md](references/seedance-playbook.md)
- [references/workflow-decision-tree.md](references/workflow-decision-tree.md)

## 工作流

### 1. 确认模型栈

- 在写任何提示词前先锁定模型栈。
- 如果任务同时包含图片和视频，分别锁定图片模型和视频模型。
- 所有提示词都必须针对该模型栈重写，不要拿一版通用提示词四处复用。
- 如果视频侧是 Veo 或 Seedance，先用 [references/workflow-decision-tree.md](references/workflow-decision-tree.md) 判断当前任务该走哪条视频工作流。
- 如果模型栈还没锁定，而且用户也没有明确授权跳过选择，就停在这里先问，不要继续到剧情分析、资产表或提示词阶段。

### 1.1 读取 profile

模型和平台一旦锁定，先读取对应 profile，而不是立刻开始手工拆分。

- `Google Flow` -> `profiles/google-flow.md`
- `Seedance` -> `profiles/seedance.md`
- `Veo + Nano Banana` -> `profiles/veo-nano-banana.md`

profile 的任务是回答：

- 当前模型 / 平台原生强项是什么
- 现在最适合 `native`、`hybrid` 还是 `manual`
- skill 应该补约束，还是应该深度接管

### 1.2 选择 mode

在读取 profile 后，显式判断当前任务应走哪一种 mode：

- `native`
  模型原生已经很强，skill 只补目标、锚点和交付整理
- `hybrid`
  模型先做主生成，skill 补连续性、真实性和执行结构
- `manual`
  skill 进行高控制拆解

默认原则：

- 不要默认 `manual`
- 当模型原生能力明显足够时，skill 应后退
- 当用户真正要的是交付整理而不是手工镜头控制时，优先 `hybrid`

### 2. 分析原始素材

- 判断输入是全文、简介、大纲，还是一个粗略概念。
- 提取主角、配角、核心冲突、世界观、关键转折、高潮和结局。
- 对长文本先压缩出因果清晰的 beat list，再开始分集。
- 缺失信息可以保守补全，但不要擅自改类型、改主题或改结局。
- 如果题材涉及 `真实地点`、`非遗`、`地方风貌`、`真实职业/技艺`，先核验再创作。优先查官方或权威来源，提炼不可乱改的真实性锚点，再写剧情和提示词。
- 对真实题材，先抽出三类锚点：`环境锚点`、`人物气质锚点`、`道具/技艺锚点`。后续所有画面和提示词都必须回扣这三类锚点。

### 3. 锁定制作参数

- 在写提示词前先冻结视觉风格、总时长、集数、画幅比例和情绪基调。
- 同时冻结目标模型栈，确保图片提示词和视频提示词彼此兼容。
- 角色、场景、道具、视频镜头必须共享同一套美术方向。
- 如果用户要连载感，尽量让每集结尾都能自然接下一集。

### 4. 搭建剧集结构

默认使用四幕结构：

- 第一幕（起）：第 1 到 5 集
- 第二幕（承）：第 6 到 10 集
- 第三幕（转）：第 11 到 15 集
- 第四幕（合）：第 16 到 20 集

每一集至少要包含：

- 集数和标题
- 时长
- 情绪
- 关键剧情点
- 开场画面
- 结尾画面

如果用户只要单集或短篇，就沿用同样逻辑，但按目标时长压缩结构。

### 4.1 现实题材催泪片补充规则

如果用户要的是 `先抑后扬`、`催泪`、`现实题材`、`亲情` 或类似方向，不要把重点写成“技术很厉害”。

- 先用一个具体的小失败建立疼痛感，不要空喊“老了”“失传了”。
- AI、特效、赛博化在这类故事里通常只是工具，不应该抢主角位置。
- 情绪弧线优先使用：`细小失去 -> 忍着不说 -> 关系冲突 -> 真实物件点亮 -> 宏大爆发 -> 极小动作收尾`。
- 高潮必须从一个 `真实物件` 或 `真实动作` 长出来，不能凭空起奇观。
- 收尾优先回到一个最细的亲情动作，而不是停在大场面上。
- 对白尽量像家里人真的会说的话；如果一句话过于“口号化”或“文艺腔”，优先改成朴素表达。

### 5. 建立素材资产表

在写分镜提示词前，先建立可复用的素材资产表，并统一编号：

| 类别 | 前缀 | 示例 |
| --- | --- | --- |
| 角色 | `C01-C99` | `C01 主角正面全身` |
| 场景 | `S01-S99` | `S01 废弃山门` |
| 道具 | `P01-P99` | `P01 主角佩剑` |

每个资产都要提供：

- 资产编号和名称
- 一段中性的标准描述，便于后续按模型重写
- 与整体美术一致的风格前缀
- 一段适合图片模型使用的英文提示词
- 能稳定角色识别和连续性的外观锚点

如果题材基于真实地点或非遗，每个关键资产还应额外提供：

- `真实性来源或依据`
- `不可漂移的结构/风貌要点`

如果用户要求中文输出，章节名、编号说明、素材表都用中文；除非用户另有要求，图片生成提示词正文仍优先保留英文。

推荐格式：

```markdown
### [编号] - [名称]

[风格前缀]，[英文视觉描述]，[技术要求]
```

### 6. 生成按模型拆分的提示词

每一集至少输出：

1. 目标图片模型的关键帧提示词
2. 目标视频模型的运动提示词
3. 参考图清单或素材上传清单
4. 用于续接下一集的结尾画面描述

针对 Nano Banana 2 或 Nano Banana Pro：

- 写法要以最终静态画面为中心，不要写成镜头时间轴。
- 优先写成一段完整描述，不要堆散乱关键词。
- 内容至少包含：主体、动作或表情、环境、灯光、镜头感、材质细节、画幅比例，以及必要时的文字内容与排版位置。

如果是改图任务，必须显式约束修改范围：

```markdown
基于提供的图片，只修改 [目标元素]。其余保持不变，包括人物身份、灯光、构图、背景和画幅比例。
```

针对 Veo 3.1，使用以下结构：

```markdown
[镜头语言] + [主体] + [动作] + [上下文] + [风格和氛围]

对白："[如果有对白]"
音效：[关键音效]
环境音：[环境底噪或氛围]
```

只有当一个片段内部确实包含多个节拍时，才使用时间戳块：

```markdown
[00:00-00:02] [镜头与动作]
[00:02-00:04] [镜头与动作]
[00:04-00:06] [镜头与动作]
[00:06-00:08] [镜头与动作]
```

在 Veo 3.1 下，先判断你走的是哪一种视频工作流：

- 如果只有一张关键图，走 `image-to-video`
- 如果要严格控制起点和终点姿态，走 `first-and-last-frame`
- 如果要强化角色、场景、道具一致性，走 `ingredients-to-video`
- 如果手里已经有一段视频要往后接，走 `extend video`
- 如果用户给的是参考视频并强调“参考这个视频的运镜/动作/节奏”，优先判断为 `Seedance` 或 `Veo extend video`，不要误写成 Veo 首尾帧

如果用户明确说目标平台是 `Google Flow`：

- 不要承诺“逐帧控制”；Flow 更适合 `按镜头/按片段` 规划。
- 提示词要写得适合复制到 Flow UI 中，必要时可完全中文。
- 明确标注每条镜头更适合 `Text`、`Ingredients`、`Frames` 还是 `Extend`。
- 如果涉及儿童角色，不要把核心情绪押在平台内生语音上；优先把对白或旁白规划为后期补配。
- 如果镜头连续性很重要，要主动规划 `存帧 -> 回灌 -> 重做关键镜头`，而不是只给一次性 prompt。

只有在用户明确要求 Seedance 输出时，才使用下面这种 Seedance 兼容格式：

```markdown
图片1: C01
图片2: S03
图片3: P01

[风格]，[画幅比例]，[整体氛围]

0-3s画面：[镜头运动]，[场景建立]，[主体引入]
3-6s画面：[镜头运动]，[情节发展]，[动作描述]
6-9s画面：[镜头运动]，[高潮或冲突]，[情绪爆发]
9-12s画面：[镜头运动]，[转折或过渡]
12-15s画面：[镜头运动]，[结尾画面]

【声音】[配乐风格] + [音效] + [对白或旁白]

【参考】@图片1 [用途]，@图片2 [用途]，@图片3 [用途]
```

可复用的运镜词：

- 推镜头
- 拉镜头
- 摇镜头
- 移镜头
- 跟镜头
- 环绕镜头
- 升降镜头
- 变焦
- 一镜到底
- 手持晃动

如果是连续剧集，第 2 集及以后要优先保持连续性，必要时使用平台支持的续接语法。具体写法参考模型说明和 Seedance 手册。

### 6.1 按 mode 控制输出重量

不要无条件输出同样厚重的一套材料。

#### `native`

- 轻量输出
- 重点给目标、锚点、质量要求和整理结构
- 不主动手工拆满镜头

#### `hybrid`

- 中等输出
- 给模型一个清晰的主任务
- skill 负责补素材资产、连续性和平台执行说明

#### `manual`

- 重量级输出
- 明确镜头、资产、提示词、回灌和衔接
- 只在高控制度需求下使用

### 7. 打包交付物

如果用户要文件，默认拆成：

1. `[Title]_剧本.md`
2. `[Title]_素材清单.md`
3. `[Title]_图片提示词.md`
4. `[Title]_视频提示词.md`
5. `[Title]_E[XX]_分镜.md`

如果用户明确说在 `Google Flow` 中执行，额外补：

6. `[Title]_Flow操作清单.md`

如果任务很小，也可以直接内联输出，不强制落文件。

### 8. 做 PDCA 复核

打包完不算结束，必须做一轮 `Check`。

- 先用 `core/output-contract.md` 回看这轮交付是否真的成立
- 再用 `benchmarks/output-review-template.md` 组织最小复核结论
- 如果 `Check verdict = fail`，继续改，不能直接停
- 如果 `Check verdict = pass` 但暴露系统性问题，把问题写回 `benchmark`、`profile` 或 `knowledge/log.md`

如果手里已经有生成后的视频、字幕和关键帧说明，优先再跑一轮结构化审片：

- 先用 `scripts/build_video_evidence_bundle.py` 整理证据
- 再用 `scripts/build_video_review_report.py` 读取 `benchmarks/video-review-registry.json`
- 先确认 `benchmarks/video-evidence.md/json` 里的证据是否足够
- 输出 `benchmarks/video-review.md/json`
- 再用 `scripts/build_video_review_action_queue.py` 把 verdict 编译成 `benchmarks/video-review-actions.md/json`
- 把结论整理成 `pass / fail / uncertain` 后，继续落到下一步 `Act`
- `fail` 优先只重做失败镜头，`uncertain` 先补证据，`pass` 再写回 benchmark / knowledge

如果这轮工作本身包含 `nightly review`、`video learning`、`issue inbox` 或其他知识学习动作，再额外做一轮后台 `PDCA`：

- 用 `knowledge/schema/knowledge-review-template.md` 判断新信号该 `admit / defer / reject`
- 不要把“脚本已经抓到了”当成“已经学会了”
- 只有经过 `Check` 的内容，才允许进入 `wiki`、`profiles`、`benchmarks` 或 `core`
- 如果前台视频审片已经生成 `video-review-actions.md/json`，再用 `build_knowledge_suggestions.py` 把高信号失败项或证据缺口推入后台建议队列

## 质量检查

完成前至少检查：

- 所有 `@imageX` 或 `@图片X` 引用都能在素材表里找到
- 每集结尾画面和下一集开场画面能够顺接
- 视频提示词覆盖了完整时长
- 运镜逻辑合理，不互相打架
- 角色、服装、道具、场景在多集间保持稳定
- 节奏符合目标时长，而不是把长剧情粗暴压缩
- 图片提示词和视频提示词确实针对对应模型，而不是同一版改几个词
- 真实题材中的地点、技艺、道具结构没有被写成泛化“国风”或“古镇”模板
- 如果目标平台是 Flow，已经明确哪些镜头要存帧、回灌、重做
- 如果出现儿童角色，关键情绪并未错误依赖平台内生成对白
- 如果用户起初没有给模型栈，已经完成了下面三者之一：`用户明确选择`、`用户明确接受默认推荐`、`用户明确授权跳过选择`
- 已给出本轮 `Check verdict` 和下一步 `Act`

## 常见问题

- 避免使用容易触发审查的问题词，必要时换一种更安全的表述。
- 避免把过多信息塞进一条提示词，导致主体被埋没。
- 避免中途新增关键道具或换装却不更新素材表。
- 避免让图片提示词和视频提示词在风格上脱节。
- 不要假设 Veo 3.1 和 Nano Banana 2 会按同一种方式理解同一句描述。
- 如果连续改图已经明显漂移，不要硬修，回到上一张好的图重新开一轮。

## 参考资料

架构说明优先读：

- [knowledge/README.md](knowledge/README.md)
- [knowledge/index.md](knowledge/index.md)
- [knowledge/status.md](knowledge/status.md)
- [knowledge/candidates.md](knowledge/candidates.md)
- [knowledge/suggestions.md](knowledge/suggestions.md)
- [knowledge/lint.md](knowledge/lint.md)
- [knowledge/github-issue-inbox.json](knowledge/github-issue-inbox.json)
- [knowledge/issue-inbox.md](knowledge/issue-inbox.md)
- [knowledge/nightly-review-registry.json](knowledge/nightly-review-registry.json)
- [knowledge/nightly-review.md](knowledge/nightly-review.md)
- [knowledge/nightly-review-llm.md](knowledge/nightly-review-llm.md)
- [knowledge/schema/knowledge-review-template.md](knowledge/schema/knowledge-review-template.md)
- [knowledge/query-log.json](knowledge/query-log.json)
- [knowledge/writeback-queue.md](knowledge/writeback-queue.md)
- [knowledge/source-registry.json](knowledge/source-registry.json)
- [knowledge/discovery-registry.json](knowledge/discovery-registry.json)
- [knowledge/schema/knowledge-schema.md](knowledge/schema/knowledge-schema.md)
- [core/README.md](core/README.md)
- [core/pdca-loop.md](core/pdca-loop.md)
- [profiles/README.md](profiles/README.md)
- [modes/README.md](modes/README.md)
- [benchmarks/README.md](benchmarks/README.md)
- [benchmarks/output-review-template.md](benchmarks/output-review-template.md)
- [benchmarks/video-evidence-registry.json](benchmarks/video-evidence-registry.json)
- [benchmarks/video-review-registry.json](benchmarks/video-review-registry.json)
- [benchmarks/video-evidence.md](benchmarks/video-evidence.md)
- [benchmarks/video-review.md](benchmarks/video-review.md)
- [benchmarks/video-review-actions.md](benchmarks/video-review-actions.md)
- [benchmarks/raw/video-review/README.md](benchmarks/raw/video-review/README.md)
- [knowledge/wiki/workflows/video-review-loop.md](knowledge/wiki/workflows/video-review-loop.md)

Seedance 模板、语法和分镜格式，见 [references/seedance-manual.md](references/seedance-manual.md)。

如果只想快速掌握 Seedance 的限制、语法和工作流，优先看 [references/seedance-manual-summary.md](references/seedance-manual-summary.md)。

如果要直接开始产出正式交付物，先套 [references/delivery-package-template.md](references/delivery-package-template.md)。

如果要在 Seedance 路线下做更稳的执行决策，读 [references/seedance-playbook.md](references/seedance-playbook.md)。

Google 系列模型的分流规则、提示词模板和常见问题，见 [references/veo-nano-banana-notes.md](references/veo-nano-banana-notes.md)。
