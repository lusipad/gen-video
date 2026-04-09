# Video Learning Loop

这个页面回答一个具体问题：

`怎么把视频经验拆开、提炼要点，并作为后续导演判断更新的依据。`

## 当前目标

当前第一版不是“自动看懂所有视频”，而是先建立一条可维护的学习链路：

1. 拿到视频来源
2. 准备 transcript / subtitle / notes
3. 自动提炼 highlights、takeaways 和术语命中
4. 把结果作为 review 材料进入导演后台
5. 再决定哪些值得写进 wiki、profile 或 source registry，用来改进下一次导演判断

## 两种学习方式

这条链路现在应明确分成两种 mode，而不是把“看懂视频”和“学拍法”混成一类：

- `content`
  学视频内容本身。
  重点是：
  - 主题
  - 人物关系
  - 情绪推进
  - 结构与高潮

- `craft`
  学视频怎么被做出来。
  重点是：
  - 分镜
  - 镜头与运镜
  - 脚本组织
  - 提示词和工作流
  - 回灌、剪接、节奏

同一条视频可以主要偏一种，也可以把另一种作为辅助观察面，但 registry 里应显式指定主模式。

## 当前入口

- `../../video-learning-registry.json`
  定义要学习的视频条目，以及 transcript / notes 路径、状态和目标落点。

- `../../../../scripts/build_video_learning_digest.py`
  读取 registry 和原始文本，生成 `video-learning.md / video-learning.json`。

- `../../video-learning.md`
  面向维护者的人类可读审阅面板。

- `../../video-learning.json`
  面向自动化脚本的结构化输出。

## 为什么先走 transcript / subtitle

当前仓库最需要的，不是再加一条昂贵且脆弱的“黑盒视频理解”。

更需要的是：

- 低成本
- 可审阅
- 可 diff
- 能和现有知识库结构接起来

所以第一版先走：

- `字幕 / transcript`
- `人工笔记`
- `视频拆解文字稿`

而不是直接要求仓库自己去解码 `mp4`。

## 当前判断

- 它适合 `学习型输入`
  也就是从创作者视频、经验视频、教程视频里抽出方法论和可执行要点。

- 它适合 `先拆解、再蒸馏`
  先把视频里的口播和字幕变成片段，再提炼出 highlights、takeaways 和术语命中。

- 它现在应同时回答两类问题
  - `这条视频内容上在讲什么，为什么有效`
  - `这条视频技术上是怎么拍、怎么组织、怎么执行的`

- 它适合 `作为知识依据`
  输出不直接改 wiki，而是先进入 review 面板，供人工决定是否写回长期知识，进而改进导演判断。

- 它不等于 `完整视频理解`
  这一层更偏向“从视频学习经验”，而不是镜头级视觉识别或故事级自动分析。

## 这会如何影响执行

- 对 creator 学习
  后续可以把 YouTube / Bilibili 的经验视频先转成 transcript，再统一进入同一套 review surface。

- 对剧本 / 分镜学习
  `content` 模式可以把“为什么这个故事成立”沉淀下来。

- 对拍法 / 工作流学习
  `craft` 模式可以把“这个视频是怎么拍出来的”沉淀下来。

- 对导演后台
  “视频学习结果”不再只是聊天记忆，而会以 `video-learning.md/json` 的形式留痕，成为可复查的导演学习材料。

- 对 suggestions
  pending 的视频学习条目可以被自动提升成后续 distill 任务，而不是依赖人工回想。

- 对本地检索层
  它和 `local-video-retrieval.md` 互补：本地检索负责召回片段，video learning 负责从片段或 transcript 中提炼方法。

## 当前边界

- 第一版不直接分析 `mp4`
- 第一版不自动下载 YouTube / Bilibili 字幕
- 第一版不自动改写 wiki
- 第一版只做 `文本驱动的视频学习 digest`

后续如果继续扩展，再往下接：

1. 字幕抓取
2. ASR
3. 关键帧/镜头级理解
4. admit / defer / reject 后的正式入库流程

Compiled into:

- `../../schema/maintenance-playbook.md`

Sources:

- [../../raw/video-learning/README.md](../../raw/video-learning/README.md)
- [../../raw/sources/2026-04-07_sentrysearch.source.md](../../raw/sources/2026-04-07_sentrysearch.source.md)
