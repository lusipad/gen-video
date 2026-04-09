# Knowledge

`knowledge/` 是 `gen-video` 的导演后台记忆层，参考 Andrej Karpathy 提出的 `raw knowledge base + LLM wiki` 思路组织。

它不是独立产品，也不直接承担最终交付，而负责三件事：

- 给前台导演判断提供事实、证据和可复查经验
- 保存原始资料，避免事实只活在聊天上下文里
- 维护可持续重写的 wiki 页面，沉淀模型 / 平台 / workflow 判断
- 把已经验证过的结论编译到 `profiles/`、`benchmarks/` 和少量 `core/` 规则里

后台学习同样必须走 `PDCA`：

- `Plan`
  先定义当前到底在学什么问题
- `Do`
  再由 CI 和脚本收集 nightly review、video learning、issue inbox、query writeback 等信号
- `Check`
  用审阅模板决定 `admit / defer / reject`
- `Act`
  把结论写回 `wiki/`、`profiles/`、`benchmarks/`、`core/` 或 `log.md`

## 目录

- `raw/`
  原始来源层。只存来源卡、截图、导出的原文、会议记录、官方文档快照。新版本新增，不覆盖旧版本。

- `wiki/`
  综合判断层。这里的页面允许持续重写，但必须带来源指向。

- `schema/`
  维护规则层。定义页面模板、引用方式、freshness 级别、promotion / retirement 规则。

- `source-registry.json`
  CI 跟踪的来源注册表，定义复查节奏、作用范围和自动 metadata capture。

- `discovery-registry.json`
  CI 发现层注册表，用来扫描官方博客、模型发布页和知名 bloger 入口，找出尚未纳入主 registry 的候选项。

- `index.md`
  当前优先入口。用于快速找到最新、最重要、最该先读的页面。

- `log.md`
  时间日志。记录来源新增、能力变化、benchmark 结论和规则退役。

- `status.md`
  CI 生成的健康面板，显示到期复查、upstream metadata 变化和缺失的 compiled target。

- `candidates.md`
  CI 生成的候选队列，显示新发现但尚未晋升进 `source-registry.json` 的模型发布、官方文章和经验帖。

- `suggestions.md`
  CI 生成的优先级建议队列，把 `status + candidates + query-log` 编译成“下一步该更新什么”。

- `lint.md`
  CI 生成的语义 lint 报告，用来找 wiki、source card、registry 和 query-resolution 之间的不一致。

- `query-log.json`
  显式记录高价值 recurring question，避免问题只存在于聊天上下文。

- `writeback-queue.md`
  由 `query-log.json` 编译出的回写队列，提示哪些问题还没沉淀进长期知识。

- `github-issue-inbox.json`
  GitHub issue 收藏夹入口配置。可以把本仓库 issue 或分配给你账号的 issue 当作手工收藏队列。

- `issue-inbox.md`
  CI 生成的 issue 收藏夹处理结果，展示 issue 中提取出的新来源摘要，以及哪些 issue 已处理并关闭。

如果要读取“分配给你个人账号”的跨仓库 issue，而不只是当前仓库的 issue，建议在 GitHub Actions 里配置 `GH_ISSUE_INBOX_TOKEN`，并把 `github-issue-inbox.json` 的 `mode` 改成 `assigned`。

- `nightly-review-registry.json`
  夜间情报采集入口配置。用于定义 HN 扫描和 watched feeds，例如 YouTube RSS、手工桥接的 Bilibili/X feeds 等。

- `nightly-review.md`
  每晚自动生成的情报审阅包。这里先汇总新模型、新工作流、新 creator 经验，再交给人工决定是否入库。

- `nightly-review-llm.md`
  夜间情报的 LLM 综合审阅稿。没有配置 LLM key 时，会退化为一份可直接喂给 LLM 的 review prompt。

- `video-learning-registry.json`
  视频学习入口配置。用于登记要拆解的 creator 视频、教程视频或参考视频，以及对应的 transcript / notes 路径。当前显式支持：
  - `content`
    学内容、主题、人物、情绪、结构
  - `craft`
    学分镜、镜头、脚本、提示词、工作流和剪接

- `video-learning.md`
  视频学习 digest。把 transcript / subtitle / notes 里的 highlights、优先 takeaways、内容要点和拍法要点整理成可复查材料。

## 与其他层的关系

- `knowledge/raw`
  保存事实和证据。

- `knowledge/wiki`
  做可更新的综合判断。

- `profiles/`
  只放当前仍有效、能直接指导执行的能力卡。

- `benchmarks/`
  用样题验证 profile 和 mode 判断是否仍然成立。

- `core/`
  只接收经过多轮验证后仍然稳定的规则。

## 推荐更新节奏

- 高频变化项：模型能力、平台 UI、工作流支持矩阵
  建议每周或每两周刷新一次

- 中频变化项：组合工作流、提示词写法、交付组织方式
  建议每月整理一次

- 低频变化项：叙事结构、真实性锚点、质量门
  只有在 benchmark 长期失真时才调整

## 最小导演学习回路

1. 新来源先进入 `raw/`
2. 结论整理进 `wiki/`
3. 可直接执行的判断再编译进 `profiles/`
4. benchmark 验证是否应保留、弱化或退役
5. 决定写入 `log.md`

新信号发现补充：

1. `discovery-registry.json` 先扫描更广的官方页和 bloger 页
2. 新链接进入 `candidates.md / candidates.json`
3. 人工确认后，再提升到 `source-registry.json`
4. 进入主 registry 后，后续复查、状态面板和 CI 提交都由 `refresh_knowledge.py` 接手

后台维护管线补充：

1. `semantic_lint_knowledge.py` 检查结构不一致
2. `build_nightly_review.py` 生成夜间情报审阅包
3. `synthesize_nightly_review.py` 做 LLM 综合审阅
4. `build_knowledge_suggestions.py` 生成优先级建议
5. `ingest_github_issue_sources.py` 处理 GitHub issue 收藏夹
6. `build_video_learning_digest.py` 把视频 transcript / notes 变成学习 digest
7. `build_query_writeback_queue.py` 把 recurring question 变成 backlog
8. 维护者据此更新 `wiki/`、`profiles/`、`benchmarks/` 或 `core/`
9. 再把动作记录进 `log.md`

建议审阅时直接套用：

- [`schema/knowledge-review-template.md`](schema/knowledge-review-template.md)

## CI Refresh

仓库里的 [`.github/workflows/knowledge-refresh.yml`](../../../../.github/workflows/knowledge-refresh.yml) 会按计划运行 `scripts/refresh_knowledge.py`：

- 为 `source-registry.json` 中的来源自动补来源卡
- 抓取 HTTP metadata 并保存到 `raw/captures/http-metadata/`
- 刷新 `status.md` 与 `status.json`
- 扫描 `discovery-registry.json` 中的官方和 bloger watchlist，生成 `candidates.md` 与 `candidates.json`
- 读取 `github-issue-inbox.json` 指定的 issue 收藏夹，生成 `issue-inbox.md` 与 `issue-inbox.json`
- 读取 `nightly-review-registry.json`，聚合 HN 与 watched feeds，生成 `nightly-review.md` 与 `nightly-review.json`
- 读取 `video-learning-registry.json`，把 transcript / subtitle / notes 生成 `video-learning.md` 与 `video-learning.json`
- 如果配置了 LLM key，则进一步生成 `nightly-review-llm.md`
- 运行 semantic lint，生成 `lint.md` 与 `lint.json`
- 生成 `suggestions.md` 与 `suggestions.json`
- 生成 `writeback-queue.md` 与 `writeback-queue.json`
- 更新 `index.md` 里的自动 watchlist 摘要

这个 CI 默认不改写 `wiki/` 的人工判断，只负责把 `watchlist + nightly review + video learning digest + LLM review + issue inbox + lint + suggestion + writeback` 这些后台信号整理出来，供导演人工复核。

也就是说，CI 主要承担 `Plan / Do` 的一部分，而 `Check / Act` 仍然是闭环中不可省略的人控层。
