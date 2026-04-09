# Query Writeback Queue

Generated from `query-log.json` by `scripts/build_query_writeback_queue.py`.

## Action Queue

### blogger-watchlist-coverage

- importance: `high`
- status: `pending`
- source: `user-conversation`
- question: 其他新模型、著名 bloger 分享经验等，怎么持续补进来并形成闭环
- next_action: distill this recurring question into wiki guidance
- promote_into: [`knowledge/wiki/concepts/karpathy-gap-analysis.md`](wiki/concepts/karpathy-gap-analysis.md), [`knowledge/discovery-registry.json`](discovery-registry.json)
- resolved_by: `n/a`
- tags: `discovery`, `blogger`, `watchlist`
- notes: 发现层已接上 blogger watchlists，但当前候选输出仍偏官方，后续需要扩 watchlist 质量和筛选规则。

## Resolved Questions

- `automation-surface` -> 这套机制的自动复核、找出不一致、更新是在哪里做呢
  resolved_by: [`knowledge/wiki/operations/knowledge-automation-surface.md`](wiki/operations/knowledge-automation-surface.md), [`knowledge/schema/maintenance-playbook.md`](schema/maintenance-playbook.md)
- `karpathy-gap` -> 现在的做法和卡帕西的思路还有什么不同吗
  resolved_by: [`knowledge/wiki/concepts/karpathy-gap-analysis.md`](wiki/concepts/karpathy-gap-analysis.md)
- `video-learning-loop` -> 继续增加学习的能力，让其可以拆解视频、提炼要点，作为后续参考的依据
  resolved_by: [`knowledge/wiki/workflows/video-learning-loop.md`](wiki/workflows/video-learning-loop.md), [`knowledge/video-learning-registry.json`](video-learning-registry.json), [`knowledge/video-learning.md`](video-learning.md)
