# Nightly LLM Review

LLM synthesis was skipped because `OPENAI_API_KEY` or `KNOWLEDGE_REVIEW_MODEL` is not configured.

## Manual Review Prompt

```text
You are reviewing a nightly knowledge intelligence packet for the gen-video skill.

Goal:
1. Compare nightly discoveries against current knowledge.
2. Identify what is genuinely new, what overlaps with existing knowledge, and what should be admitted, deferred, or rejected.
3. Produce a human review brief, not an auto-merge decision.

Output structure:
- Executive Summary
- Highest-Signal New Items
- Conflicts Or Gaps Against Existing Knowledge
- Recommended Actions
- Final Human Gate

Current context follows.

## Nightly Review
# Nightly Knowledge Review

Generated from `nightly-review-registry.json` by `scripts/build_nightly_review.py`.

- total_items: 2
- new_items: 2
- human_gate: `manual-admit`

## Review Required

### An experiment in voice text editing with Gemini Live

- source: `Hacker News` (`hackernews` / `community`)
- url: https://public.grugnotes.com/keizo/blog/text-editing-at-the-speed-of-thought/
- known_state: `new`
- matched_keywords: `gemini`
- review_into: `knowledge/wiki/concepts/karpathy-gap-analysis.md` <wiki/concepts/karpathy-gap-analysis.md>, `knowledge/source-registry.json` <source-registry.json>

### I Deploy Apps to My Homelab (A Love Story in 9 Acts)

- source: `Hacker News` (`hackernews` / `community`)
- url: https://blog.laurentcharignon.com/post/2025-12-14-homelab-deployment-flow/
- known_state: `new`
- matched_keywords: `flow`
- review_into: `knowledge/wiki/concepts/karpathy-gap-analysis.md` <wiki/concepts/karpathy-gap-analysis.md>, `knowledge/source-registry.json` <source-registry.json>

## Already Seen

- None.


## Knowledge Index
# Knowledge Index

建议按这个顺序进入知识库：

1. log.md <log.md>
2. schema/knowledge-schema.md <schema/knowledge-schema.md>
3. status.md <status.md>
4. candidates.md <candidates.md>
5. suggestions.md <suggestions.md>
6. lint.md <lint.md>
7. nightly-review.md <nightly-review.md>
8. nightly-review-llm.md <nightly-review-llm.md>
9. issue-inbox.md <issue-inbox.md>
10. writeback-queue.md <writeback-queue.md>
11. wiki/workflows/refresh-loop.md <wiki/workflows/refresh-loop.md>
12. 对应主题的 wiki 页面
13. 对应的 `profiles/*.md`

<!-- AUTO:STATUS:START -->
- status.md <status.md> is the CI-generated watchlist for review cadence and upstream metadata changes.
- Overdue reviews: 0
- Due soon: 0
- Upstream metadata changes detected: 0
<!-- AUTO:STATUS:END -->

<!-- AUTO:CANDIDATES:START -->
- candidates.md <candidates.md> contains 11 unseen candidate links from discovery watchlists.
  - `luma-news` -> Introducing Camera Angle Concepts <https://lumalabs.ai/news/camera-angle-concepts>
  - `luma-news` -> Introducing Camera Motion Concepts <https://lumalabs.ai/news/camera-motion-concepts>
  - `luma-news` -> Introducing Modify Video <https://lumalabs.ai/news/introducing-modify-video>
  - `luma-news` -> Introducing Ray3 Modify <https://lumalabs.ai/news/ray3-modify>
  - `luma-news` -> Luma AI launches Ray3 <https://lumalabs.ai/news/ray3>
- Discovery watchlist fetch failures: 0
<!-- AUTO:CANDIDATES:END -->

<!-- AUTO:SUGGESTIONS:START -->
- suggestions.md <suggestions.md> contains 15 actionable update suggestions.
- High priority items: 2
  - `high` -> Strengthen blogger discovery coverage
  - `high` -> Write back recurring question `blogger-watchlist-coverage`
  - `medium` -> Review discovery candidate: Introducing Camera Angle Concepts
<!-- AUTO:SUGGESTIONS:END -->

<!-- AUTO:LINT:START -->
- lint.md <lint.md> reports 0 errors and 0 warnings across the knowledge layer.
<!-- AUTO:LINT:END -->

<!-- AUTO:WRITEBACK:START -->
- writeback-queue.md <writeback-queue.md> contains 1 query-derived follow-up items.
  - `blogger-watchlist-coverage` -> 其他新模型、著名 bloger 分享经验等，怎么持续补进来并形成闭环
<!-- AUTO:WRITEBACK:END -->

<!-- AUTO:ISSUE-INBOX:START -->
- issue-inbox.md <issue-inbox.md> captures bookmarked GitHub issues after ingestion.
<!-- AUTO:ISSUE-INBOX:END -->

<!-- AUTO:NIGHTLY-REVIEW:START -->
- nightly-review.md <nightly-review.md> contains 2 nightly intelligence items.
- New review items: 2
- Human gate: `manual-admit`
<!-- AUTO:NIGHTLY-REVIEW:END -->

<!-- AUTO:NIGHTLY-LLM:START -->
- nightly-review-llm.md <nightly-review-llm.md> is the synthesized review brief for the nightly intelligence packet.
- LLM synthesis status: `skipped`
<!-- AUTO:NIGHTLY-LLM:END -->

## 当前重点页面

- wiki/concepts/skill-as-orchestrator.md <wiki/concepts/skill-as-orchestrator.md>
  为什么这个 skill 的长期价值应该是编排、约束和评测，而不是不断变厚的 prompt 库。

- wiki/concepts/promotion-and-retirement.md <wiki/concepts/promotion-and-retirement.md>
  什么信息留在 wiki，什么信息晋升到 profile、benchmark 或 core。

- wiki/workflows/refresh-loop.md <wiki/workflows/refresh-loop.md>
  定期刷新、编译和退役的维护流程。

- wiki/operations/knowledge-automation-surface.md <wiki/operations/knowledge-automation-surface.md>
  解释自动复核、lint、suggestion 和 query writeback 分别在哪一层执行。

- wiki/concepts/karpathy-gap-analysis.md <wiki/concepts/karpathy-gap-analysis.md>
  对齐当前实现与 Karpathy 思路的重合点、保守点和还没补上的部分。

- wiki/workflows/local-video-retrieval.md <wiki/workflows/local-video-retrieval.md>
  记录 `SentrySearch` 这类本地视频语义检索工具为什么值得作为 `API-first` 路线的前置召回层。

- nightly-review-registry.json <nightly-review-registry.json>
  定义夜间情报采集入口，包括 HN 与 watched feeds。

## 已登记来源

- raw/sources/2026-04-06_karpathy-llm-wiki.source.md <raw/sources/2026-04-06_karpathy-llm-wiki.source.md>
  知识库分层设计的外部参考来源卡。

- raw/sources/2026-04-07_sentrysearch.source.md <raw/sources/2026-04-07_sentrysearch.source.md>
  本地视频语义检索来源卡，用来跟踪 `先检索、后理解` 的本地召回路线。

- source-registry.json <source-registry.json>
  当前 CI 跟踪的官方资料与更新节奏。

- discovery-registry.json <discovery-registry.json>
  当前 CI 用来发现新模型、新官方文章和新经验帖的 watchlist。

## 下游编译目标

- ../profiles/README.md <../profiles/README.md>
- ../benchmarks/README.md <../benchmarks/README.md>
- ../core/README.md <../core/README.md>


## Status
# Knowledge Status

Generated from `source-registry.json` by `scripts/refresh_knowledge.py`.

## Review Summary

- `overdue`: 0
- `due-soon`: 0
- `healthy`: 8

## Upstream Change Watch

- No upstream metadata changes detected in the latest refresh.

## Tracked Sources

| ID | Scope | Volatility | Due | State | Source Card | Capture |
| --- | --- | --- | --- | --- | --- | --- |
| `gemini-31-flash-image-model-card` | nano-banana-2 | hot | 2026-04-13 | healthy | `raw/sources/2026-04-06_gemini-31-flash-image-model-card.source.md` <raw/sources/2026-04-06_gemini-31-flash-image-model-card.source.md> | `raw/captures/http-metadata/gemini-31-flash-image-model-card.json` <raw/captures/http-metadata/gemini-31-flash-image-model-card.json> |
| `google-flow-home` | google-flow | hot | 2026-04-13 | healthy | `raw/sources/2026-04-06_google-flow-home.source.md` <raw/sources/2026-04-06_google-flow-home.source.md> | `raw/captures/http-metadata/google-flow-home.json` <raw/captures/http-metadata/google-flow-home.json> |
| `seedance-20-launch` | seedance | hot | 2026-04-13 | healthy | `raw/sources/2026-04-06_seedance-20-launch.source.md` <raw/sources/2026-04-06_seedance-20-launch.source.md> | `raw/captures/http-metadata/seedance-20-launch.json` <raw/captures/http-metadata/seedance-20-launch.json> |
| `seedance-home` | seedance | hot | 2026-04-13 | healthy | `raw/sources/2026-04-06_seedance-home.source.md` <raw/sources/2026-04-06_seedance-home.source.md> | `raw/captures/http-metadata/seedance-home.json` <raw/captures/http-metadata/seedance-home.json> |
| `veo-model-home` | veo | hot | 2026-04-13 | healthy | `raw/sources/2026-04-06_veo-model-home.source.md` <raw/sources/2026-04-06_veo-model-home.source.md> | `raw/captures/http-metadata/veo-model-home.json` <raw/captures/http-metadata/veo-model-home.json> |
| `gemini-25-flash-image-blog` | nano-banana | warm | 2026-04-27 | healthy | `raw/sources/2026-04-06_gemini-25-flash-image-blog.source.md` <raw/sources/2026-04-06_gemini-25-flash-image-blog.source.md> | `raw/captures/http-metadata/gemini-25-flash-image-blog.json` <raw/captures/http-metadata/gemini-25-flash-image-blog.json> |
| `karpathy-llm-wiki` | knowledge-management | cold | 2026-05-06 | healthy | `raw/sources/2026-04-06_karpathy-llm-wiki.source.md` <raw/sources/2026-04-06_karpathy-llm-wiki.source.md> | `raw/captures/http-metadata/karpathy-llm-wiki.json` <raw/captures/http-metadata/karpathy-llm-wiki.json> |
| `sentrysearch` | local-video-search | warm | 2026-05-07 | healthy | `raw/sources/2026-04-07_sentrysearch.source.md` <raw/sources/2026-04-07_sentrysearch.source.md> | `raw/captures/http-metadata/sentrysearch.json` <raw/captures/http-metadata/sentrysearch.json> |

## Missing Compiled Targets

- None.


## Candidates
# Knowledge Candidates

Generated from `discovery-registry.json` by `scripts/discover_knowledge_candidates.py`.

## Promotion Queue

### Introducing Camera Angle Concepts

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/camera-angle-concepts
- matched_keywords: `camera`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Introducing Camera Motion Concepts

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/camera-motion-concepts
- matched_keywords: `camera`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Introducing Modify Video

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/introducing-modify-video
- matched_keywords: `video`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Introducing Ray3 Modify

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/ray3-modify
- matched_keywords: `ray3`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Luma AI launches Ray3

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/ray3
- matched_keywords: `ray3`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Ray3 Evaluation Report – State-of-the-Art Performance for Pro Video Generation

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/ray3-eval
- matched_keywords: `ray3`, `video`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Ray3.14 is here: Native 1080p, 3x cheaper and 4x faster.

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/ray3_14
- matched_keywords: `ray3`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Serviceplan Group Deploys Creative AI Across Global Operations in Partnership with Luma AI

- watchlist: `luma-news`
- owner_type: `official`
- url: https://lumalabs.ai/news/serviceplan-group-deploys-creative-ai-across-global-operations-in-partnership-with-luma-ai
- matched_keywords: `creative`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Introducing the Gen-4 Image API Runway / May 16, 2025

- watchlist: `runway-news`
- owner_type: `official`
- url: https://runwayml.com/news/introducing-runway-api-for-gen-4-images
- matched_keywords: `gen-4`, `image`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Introducing the Runway API for Gen-3 Alpha Turbo Runway / September 16, 2024

- watchlist: `runway-news`
- owner_type: `official`
- url: https://runwayml.com/news/introducing-the-runway-api
- matched_keywords: `gen-3`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

### Runway Advances Video Generation and World Models With NVIDIA Rubin Platform Runway / January 5, 2026

- watchlist: `runway-news`
- owner_type: `official`
- url: https://runwayml.com/news/runway-partners-with-nvidia
- matched_keywords: `video`
- promote_into: `knowledge/wiki/concepts/promotion-and-retirement.md`

## Watchlist Health

- All discovery watchlists fetched successfully.


## Suggestions
# Knowledge Suggestions

Generated from `status.json`, `candidates.json`, `issue-inbox.json`, `nightly-review.json`, `query-log.json`, and discovery/source registries by `scripts/build_knowledge_suggestions.py`.

## High Priority

### Strengthen blogger discovery coverage

- kind: `discovery-gap`
- reason: blogger watchlists exist, but the latest discovery run surfaced 0 blogger candidates
- update_targets: `knowledge/discovery-registry.json` <discovery-registry.json>, `knowledge/wiki/concepts/karpathy-gap-analysis.md` <wiki/concepts/karpathy-gap-analysis.md>, `knowledge/log.md` <log.md>
- evidence: `knowledge/candidates.md` <candidates.md>, `knowledge/discovery-registry.json` <discovery-registry.json>

### Write back recurring question `blogger-watchlist-coverage`

- kind: `query-writeback`
- reason: high-value user question is still pending distillation into persistent knowledge
- update_targets: `knowledge/wiki/concepts/karpathy-gap-analysis.md` <wiki/concepts/karpathy-gap-analysis.md>, `knowledge/discovery-registry.json` <discovery-registry.json>
- evidence: `knowledge/query-log.json` <query-log.json>

## Medium Priority

### Review discovery candidate: Introducing Camera Angle Concepts

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched camera
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Introducing Camera Motion Concepts

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched camera
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Introducing Modify Video

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched video
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Introducing Ray3 Modify

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Introducing the Gen-4 Image API Runway / May 16, 2025

- kind: `candidate-promotion`
- reason: untracked official candidate from `runway-news` matched gen-4, image
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Introducing the Runway API for Gen-3 Alpha Turbo Runway / September 16, 2024

- kind: `candidate-promotion`
- reason: untracked official candidate from `runway-news` matched gen-3
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Luma AI launches Ray3

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Ray3 Evaluation Report – State-of-the-Art Performance for Pro Video Generation

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3, video
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Ray3.14 is here: Native 1080p, 3x cheaper and 4x faster.

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched ray3
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Runway Advances Video Generation and World Models With NVIDIA Rubin Platform Runway / January 5, 2026

- kind: `candidate-promotion`
- reason: untracked official candidate from `runway-news` matched video
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review discovery candidate: Serviceplan Group Deploys Creative AI Across Global Operations in Partnership with Luma AI

- kind: `candidate-promotion`
- reason: untracked official candidate from `luma-news` matched creative
- update_targets: `knowledge/source-registry.json` <source-registry.json>, `knowledge/wiki/concepts/promotion-and-retirement.md` <wiki/concepts/promotion-and-retirement.md>
- evidence: `knowledge/candidates.md` <candidates.md>

### Review nightly intelligence item: An experiment in voice text editing with Gemini Live

- kind: `nightly-review`
- reason: nightly review surfaced a new community item from `Hacker News`
- update_targets: `knowledge/wiki/concepts/karpathy-gap-analysis.md` <wiki/concepts/karpathy-gap-analysis.md>, `knowledge/source-registry.json` <source-registry.json>
- evidence: `knowledge/nightly-review.md` <nightly-review.md>, https://public.grugnotes.com/keizo/blog/text-editing-at-the-speed-of-thought/

### Review nightly intelligence item: I Deploy Apps to My Homelab (A Love Story in 9 Acts)

- kind: `nightly-review`
- reason: nightly review surfaced a new community item from `Hacker News`
- update_targets: `knowledge/wiki/concepts/karpathy-gap-analysis.md` <wiki/concepts/karpathy-gap-analysis.md>, `knowledge/source-registry.json` <source-registry.json>
- evidence: `knowledge/nightly-review.md` <nightly-review.md>, https://blog.laurentcharignon.com/post/2025-12-14-homelab-deployment-flow/

## Low Priority

- None.


## Karpathy Gap
# Karpathy Gap Analysis

这个项目已经明显靠近 `raw knowledge base + LLM wiki` 思路，但还没有完全走到 Karpathy 那种形态。

## 已经对齐的部分

- 有 `raw/`
  原始来源、来源卡和 metadata capture 没有直接混进执行层。
- 有 `wiki/`
  判断先留在可重写页面里，而不是一开始就写死成 prompt 或硬规则。
- 有编译层
  `profiles/`、`modes/`、`benchmarks/`、`core/` 只接收更稳定的判断。
- 有 refresh 机制
  `source-registry + status` 让已知来源能够持续复查。
- 有 discovery 机制
  `discovery-registry + candidates` 让系统不只盯着既有来源。
- 有 issue inbox
  `github-issue-inbox + issue-inbox` 让人工收藏的新线索也能进入同一套闭环。
- 有 nightly review
  `nightly-review + nightly-review-llm` 让系统先做夜间聚合和对照，再交给人工做最终入库决定。

这些已经让 skill 从“静态 prompt 模板”转成了“知识驱动的编排系统”。

## 现在仍然和 Karpathy 思路不同的地方

### 1. 还没有自动改写 wiki

Karpathy 的方向更接近：原始资料持续进入，wiki 作为工作中的动态综合层，不断被重写。

现在这套实现仍然偏保守：

- 自动化只负责 `监控 + lint + suggestions + writeback queue`
- wiki 改写仍然由人工完成

这是一个刻意的收敛设计。原因不是做不到，而是当前阶段更优先 `低噪声` 和 `可追责`。

### 2. 还没有把 benchmark 结果自动压回知识层

Karpathy 式系统更强调“工作中产生的证据会持续反哺知识层”。

当前项目虽然已经有 `benchmarks/` 结构，但 benchmark 结果回写还主要停留在流程约定，没有形成自动产物链路。

这意味着：

- 规则退役仍偏人工
- `native / hybrid / manual` 的切换证据还不够系统化

### 3. query memory 刚接上，还不够厚

现在新增了 `query-log.json` 和 `writeback-queue`，但这只是第一层。

当前方式仍然更像：

- 把显式的高价值问题登记下来
- 再人工决定写成哪篇 wiki

同时现在也支持把 GitHub issue 当成收藏夹入口，但这仍然只是 `手工采样入口`，不是更深的语义聚类。

还没有做到：

- 自动聚类大量相似问题
- 基于长期查询分布自动重排知识结构
- 用真实使用频次直接驱动知识页权重

### 4. discovery 的 blogger 侧还偏弱

官方发现层已经有用，但 blogger 侧虽然接上 watchlist，当前产出仍接近 0。

这说明差距不在“有没有入口”，而在：

- watchlist 种子是否够对
- keyword 策略是否够贴合创作经验帖
- 哪些作者真的值得长期跟踪

所以现在更像“半闭环发现系统”，而不是已经成熟的开放知识雷达。

## 为什么当前设计没有直接更激进

如果现在一步走到“自动抓取 + 自动重写 + 自动晋升”，副作用会很大：

- CI 噪声会上升
- diff 可读性会下降
- wiki 可能被大量低信噪比变化污染
- 对 skill 的执行判断会变得不稳定

所以当前路线是：

1. 先把 `监控`
2. 再把 `发现`
3. 再把 `lint`
4. 再把 `suggestions`
5. 再把 `query writeback`
6. 最后才考虑更深的自动 distill

这不是反对 Karpathy，而是在保留他的方法论骨架的同时，按当前项目体量做更稳的落地版本。

## 当前版本最真实的定位

如果用一句话概括：

`它已经是 Karpathy 风格知识库的保守实现版，但还不是 fully self-refreshing wiki。`

已经补上的是：

- 原始证据层
- 可重写 wiki 层
- 编译层
- CI refresh
- discovery queue
- issue inbox
- nightly review
- semantic lint
- query writeback

还没完全补上的是：

- benchmark 自动回写
- 更强的 blogger / creator 发现质量
- 更深的 query aggregation
- 自动 distill 后的人工审核工作流

## 对这个 skill 的实际意义

这也解释了为什么 `gen-video` 不该继续靠堆 prompt 变厚。

真正长期有效的部分应该是：

- 跟踪模型原生能力变化
- 判断 skill 什么时候该退后
- 用知识层而不是对话上下文保存判断
- 让新的模型、新的经验帖、新的失败案例能持续进入同一个闭环

只有这样，skill 才不会因为下一波模型升级就重新变成累赘。

Sources:

- ../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md <../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md>
- ../operations/knowledge-automation-surface.md <../operations/knowledge-automation-surface.md>


```
