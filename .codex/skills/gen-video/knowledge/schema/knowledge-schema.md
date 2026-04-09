# Knowledge Schema

这个文件定义 `knowledge/` 的维护契约。

它的目标不是堆文档，而是保证导演后台能稳定服务前台的导演判断。

## 层级定义

- `raw/`
  证据层。原始来源、快照、导出文件和 provenance。

- `wiki/`
  综合层。围绕一个主题形成可重写判断。

- `schema/`
  规则层。定义知识库自己的写法和维护流程。

- `index.md`
  导航层。指向当前最值得先读的页面。

- `log.md`
  时间层。记录所有重要更新和复查日期。

- `source-registry.json`
  主监控层。定义已纳入长期追踪的来源。

- `discovery-registry.json`
  发现层。定义更广的官方页和 bloger 页扫描入口。

- `status.md`
  已追踪来源的自动复核结果。

- `candidates.md`
  发现层产生的候选队列，等待人工提升到主 registry。

- `suggestions.md`
  建议层。把 status、candidate 和 query signal 编译成优先级更新队列。

- `lint.md`
  一致性层。检查 wiki、source card、registry 和 query-resolution 的结构问题。

- `query-log.json`
  记忆层。显式记录高价值 recurring question。

- `writeback-queue.md`
  回写层。把 query memory 转成待沉淀 backlog。

- `github-issue-inbox.json`
  收藏夹入口层。定义 GitHub issue inbox 的读取模式、label 和关闭策略。

- `issue-inbox.md`
  inbox 层。保存 issue 中提取出的来源摘要和处理动作。

- `nightly-review-registry.json`
  夜间情报入口层。定义 HN 与 watched feeds 的采集规则。

- `nightly-review.md`
  夜间审阅层。先汇总、去重、对照现有知识，再等待人工 admit / reject。

- `nightly-review-llm.md`
  LLM 综合层。把 nightly review 压成一份高信号 review brief。

- `video-learning-registry.json`
  视频学习入口层。定义要拆解的视频、transcript / notes 路径、状态和 review 目标。

- `video-learning.md`
  视频学习审阅层。把 transcript / subtitle / notes 压成 highlights、takeaways 和术语命中。

## 页面要求

### Source Card

最少字段：

- `title`
- `author`
- `url`
- `source_type`
- `captured_at`
- `volatility`
- `scope`
- `status`

### Wiki Page

建议至少包含：

- 页面目标
- 当前判断
- 这会如何影响执行
- `Compiled into`（如果有）
- `Sources`

### Discovery Watchlist

最少字段：

- `id`
- `title`
- `owner_type`
- `url`
- `mode`
- `allowed_domains`
- `include_url_patterns`
- `exclude_url_patterns`
- `keywords`
- `max_candidates`
- `promote_into`

### Query Log Entry

最少字段：

- `id`
- `asked_at`
- `source`
- `question`
- `importance`
- `status`
- `resolved_by`
- `promote_into`
- `tags`
- `notes`

### GitHub Issue Inbox Config

最少字段：

- `enabled`
- `mode`
- `repo`
- `labels`
- `include_issue_comments`
- `close_processed_issues`
- `comment_on_close`
- `max_issues_per_run`
- `assigned_repo_allowlist`
- `assigned_repo_blocklist`

### Nightly Review Config

最少字段：

- `enabled`
- `keywords`
- `hackernews`
- `feeds`
- `review`

### Video Learning Config

最少字段：

- `enabled`
- `default_extract`
- `term_vocab`
- `entries`

每个 entry 额外建议至少包含：

- `learning_mode`
  `content` 或 `craft`
- `focus`
  当前更想提炼的学习维度

### Knowledge Review Record

建议至少包含：

- `signal`
- `question`
- `evidence`
- `review_verdict`
- `impact_scope`
- `act_targets`
- `next_review_at` 或 `defer_reason`

## Freshness 级别

- `hot`
  变化很快，默认每周或每两周复查

- `warm`
  中速变化，默认每月复查

- `cold`
  变化较慢，按需复查

## 维护原则

- `knowledge/` 服务导演判断，不把后台维护误当成独立产品
- 新学习信号必须先过 `Check`，再进入 `Act`
- 来源先入 `raw/`，不要跳过证据层
- 新发现先入 `candidates.md`，不要直接跳到 `source-registry.json`
- 新 query 先入 `query-log.json`，不要只停留在聊天记录里
- 新 issue 收藏先入 `issue-inbox.md`，不要直接跳到 `source-registry.json`
- 新的夜间情报先入 `nightly-review.md`，不要绕过人工闸门直接入库
- wiki 可以改写，但要保留来源指向
- 先用 `lint.md` 找结构问题，再决定是否更新结论
- 用 `suggestions.md` 排优先级，而不是凭感觉决定先改什么
- 只有能直接改变执行的判断才编译进 `profiles/`
- 只有长期稳定的判断才晋升到 `core/`
- benchmark 结果必须回写 `log.md`

推荐直接使用：

- [knowledge-review-template.md](knowledge-review-template.md)
