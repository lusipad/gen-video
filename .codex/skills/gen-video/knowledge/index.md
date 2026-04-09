# Knowledge Index

这里是 `镜界.SKILL` 的后台入口。

如果前台负责把片子做出来，这里负责让下一次导演判断更准。

建议按这个顺序进入知识库：

1. [log.md](log.md)
2. [schema/knowledge-schema.md](schema/knowledge-schema.md)
3. [status.md](status.md)
4. [candidates.md](candidates.md)
5. [suggestions.md](suggestions.md)
6. [lint.md](lint.md)
7. [nightly-review.md](nightly-review.md)
8. [nightly-review-llm.md](nightly-review-llm.md)
9. [video-learning.md](video-learning.md)
10. [issue-inbox.md](issue-inbox.md)
11. [writeback-queue.md](writeback-queue.md)
12. [wiki/workflows/refresh-loop.md](wiki/workflows/refresh-loop.md)
13. 对应主题的 wiki 页面
14. 对应的 `profiles/*.md`

<!-- AUTO:STATUS:START -->
- [status.md](status.md) is the CI-generated watchlist for review cadence and upstream metadata changes.
- Overdue reviews: 0
- Due soon: 0
- Upstream metadata changes detected: 0
<!-- AUTO:STATUS:END -->

<!-- AUTO:CANDIDATES:START -->
- [candidates.md](candidates.md) contains 11 unseen candidate links from discovery watchlists.
  - `luma-news` -> [Introducing Camera Angle Concepts](https://lumalabs.ai/news/camera-angle-concepts)
  - `luma-news` -> [Introducing Camera Motion Concepts](https://lumalabs.ai/news/camera-motion-concepts)
  - `luma-news` -> [Introducing Modify Video](https://lumalabs.ai/news/introducing-modify-video)
  - `luma-news` -> [Introducing Ray3 Modify](https://lumalabs.ai/news/ray3-modify)
  - `luma-news` -> [Luma AI launches Ray3](https://lumalabs.ai/news/ray3)
- Discovery watchlist fetch failures: 0
<!-- AUTO:CANDIDATES:END -->

<!-- AUTO:SUGGESTIONS:START -->
- [suggestions.md](suggestions.md) contains 15 actionable update suggestions.
- High priority items: 2
  - `high` -> Strengthen blogger discovery coverage
  - `high` -> Write back recurring question `blogger-watchlist-coverage`
  - `medium` -> Review discovery candidate: Introducing Camera Angle Concepts
<!-- AUTO:SUGGESTIONS:END -->

<!-- AUTO:LINT:START -->
- [lint.md](lint.md) reports 0 errors and 0 warnings across the knowledge layer.
<!-- AUTO:LINT:END -->

<!-- AUTO:WRITEBACK:START -->
- [writeback-queue.md](writeback-queue.md) contains 1 query-derived follow-up items.
  - `blogger-watchlist-coverage` -> 其他新模型、著名 bloger 分享经验等，怎么持续补进来并形成闭环
<!-- AUTO:WRITEBACK:END -->

<!-- AUTO:ISSUE-INBOX:START -->
- [issue-inbox.md](issue-inbox.md) captures bookmarked GitHub issues after ingestion.
<!-- AUTO:ISSUE-INBOX:END -->

<!-- AUTO:NIGHTLY-REVIEW:START -->
- [nightly-review.md](nightly-review.md) contains 2 nightly intelligence items.
- New review items: 2
- Human gate: `manual-admit`
<!-- AUTO:NIGHTLY-REVIEW:END -->

<!-- AUTO:VIDEO-LEARNING:START -->
- [video-learning.md](video-learning.md) contains 0 transcript-driven video learning items.
- Pending distillation items: 0
- Modes: content=0, craft=0
- Digest errors: 0
<!-- AUTO:VIDEO-LEARNING:END -->

<!-- AUTO:NIGHTLY-LLM:START -->
- [nightly-review-llm.md](nightly-review-llm.md) is the synthesized review brief for the nightly intelligence packet.
- LLM synthesis status: `skipped`
<!-- AUTO:NIGHTLY-LLM:END -->

## 当前重点页面

- [wiki/concepts/skill-as-orchestrator.md](wiki/concepts/skill-as-orchestrator.md)
  为什么这个 skill 的长期价值应该是编排、约束和评测，而不是不断变厚的 prompt 库。

- [wiki/concepts/promotion-and-retirement.md](wiki/concepts/promotion-and-retirement.md)
  什么信息留在 wiki，什么信息晋升到 profile、benchmark 或 core。

- [wiki/workflows/refresh-loop.md](wiki/workflows/refresh-loop.md)
  定期刷新、编译和退役的维护流程。

- [wiki/workflows/video-learning-loop.md](wiki/workflows/video-learning-loop.md)
  解释如何把视频 transcript / notes 转成可审阅的学习 digest，再决定是否写回长期知识。

- [wiki/workflows/video-review-loop.md](wiki/workflows/video-review-loop.md)
  解释生成后视频如何先整理证据，再产出 `pass / fail / uncertain` 审片 verdict，并继续编译出 `Act` 队列。

- [wiki/operations/knowledge-automation-surface.md](wiki/operations/knowledge-automation-surface.md)
  解释自动复核、lint、suggestion 和 query writeback 分别在哪一层执行。

- [wiki/concepts/karpathy-gap-analysis.md](wiki/concepts/karpathy-gap-analysis.md)
  对齐当前实现与 Karpathy 思路的重合点、保守点和还没补上的部分。

- [wiki/workflows/local-video-retrieval.md](wiki/workflows/local-video-retrieval.md)
  记录 `SentrySearch` 这类本地视频语义检索工具为什么值得作为 `API-first` 路线的前置召回层。

- [nightly-review-registry.json](nightly-review-registry.json)
  定义夜间情报采集入口，包括 HN 与 watched feeds。

- [video-learning-registry.json](video-learning-registry.json)
  定义视频学习条目、transcript / notes 路径和 distill 落点。

## 已登记来源

- [raw/sources/2026-04-06_karpathy-llm-wiki.source.md](raw/sources/2026-04-06_karpathy-llm-wiki.source.md)
  知识库分层设计的外部参考来源卡。

- [raw/sources/2026-04-07_sentrysearch.source.md](raw/sources/2026-04-07_sentrysearch.source.md)
  本地视频语义检索来源卡，用来跟踪 `先检索、后理解` 的本地召回路线。

- [source-registry.json](source-registry.json)
  当前 CI 跟踪的官方资料与更新节奏。

- [discovery-registry.json](discovery-registry.json)
  当前 CI 用来发现新模型、新官方文章和新经验帖的 watchlist。

## 下游编译目标

- [../profiles/README.md](../profiles/README.md)
- [../benchmarks/README.md](../benchmarks/README.md)
- [../core/README.md](../core/README.md)
