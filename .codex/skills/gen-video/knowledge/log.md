# Knowledge Log

| Date | Type | Item | Action | Next Review |
| --- | --- | --- | --- | --- |
| 2026-04-06 | bootstrap | 建立 `knowledge/raw/wiki/schema/index/log` | 把知识层接入 `gen-video` 架构，作为 `profiles`、`benchmarks` 和 `core` 的上游记忆系统 | 2026-04-20 |
| 2026-04-06 | automation | 建立 `source-registry + refresh script + GitHub Actions` | 给知识库补定时巡检、来源卡生成、metadata watchlist 和状态面板 | 2026-04-13 |
| 2026-04-06 | discovery | 建立 `discovery-registry + candidates queue` | 给知识库补官方模型页、平台博客和 bloger 入口的发现层，把未纳入主 registry 的新来源先排入候选队列 | 2026-04-13 |
| 2026-04-06 | lint | 建立 `semantic_lint_knowledge.py + lint.md` | 给知识层补结构一致性检查，自动找缺 Sources、断目标、孤儿页和失效 query resolution | 2026-04-13 |
| 2026-04-06 | writeback | 建立 `query-log + writeback-queue` | 把高价值 recurring question 从聊天上下文转成长期 backlog，补 query memory | 2026-04-13 |
| 2026-04-06 | suggestions | 建立 `build_knowledge_suggestions.py + suggestions.md` | 把 status、candidates 和 query signal 编译成优先级更新队列，让维护动作有顺序 | 2026-04-13 |
| 2026-04-06 | inbox | 建立 `github issue inbox + issue-inbox.md` | 把 GitHub issue 作为手工收藏夹入口接进知识闭环，处理后自动评论并关闭 issue | 2026-04-13 |
| 2026-04-06 | nightly-review | 建立 `nightly-review + nightly-review-llm` | 把 HN、watched feeds 和现有知识对照成夜间审阅包，并保留人工最终入库闸门 | 2026-04-07 |
| 2026-04-06 | source | Karpathy LLM wiki pattern | 作为知识库分层方法的外部参考，并据此建立 `raw -> wiki -> compiled docs` 路径 | 2026-05-06 |
| 2026-04-07 | source | SentrySearch local video retrieval | 记录本地视频语义检索这条补充路线，作为后续 `API-first` 视频理解前置召回层的外部参考 | 2026-05-07 |

## Open Queue

- 刷新 `Google Flow` 官方帮助与产品更新，补第一批平台来源卡
- 刷新 `Seedance` 自动分镜相关资料，判断 `manual` 规则需要退役的部分
- 刷新 `Veo / Nano Banana` 官方能力说明，并与现有 `profiles/` 对齐
- 强化 blogger / creator watchlist，提升 discovery 的经验帖覆盖率
