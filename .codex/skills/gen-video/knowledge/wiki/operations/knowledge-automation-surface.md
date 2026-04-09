# Knowledge Automation Surface

这个页面回答一个具体问题：`自动复核、找出不一致、建议更新，到底分别在哪里做。`

它们共同组成 `镜界.SKILL` 的导演后台，而不是另一个独立产品。

脚本本身并不等于闭环。闭环成立的前提，是这些自动化产物后面还有明确的 `Check` 和 `Act`。

## 当前导演后台分工

### 1. 自动复核

- `../../scripts/refresh_knowledge.py`
  负责复查已进入 `source-registry.json` 的长期来源。
- `../../../../../../.github/workflows/knowledge-refresh.yml`
  负责按计划运行刷新脚本，并把生成结果写回仓库。

这层做的事包括：

- 来源卡自动补齐
- HTTP metadata capture
- 到期复查状态计算
- 缺失 compiled target 检查
- `status.md / status.json` 刷新

### 2. 新来源发现

- `../../scripts/discover_knowledge_candidates.py`
  负责扫描 `discovery-registry.json` 里的官方页和 blogger 页入口。

这层做的事包括：

- 扫描 watchlists
- 过滤已在主 registry 里的来源
- 输出 `candidates.md / candidates.json`
- 把发现层摘要回写到 `../../index.md`

### 3. 找出不一致

- `../../scripts/semantic_lint_knowledge.py`
  负责检查知识层自己的结构一致性。

当前 lint 会检查：

- wiki 页面是否缺 `Sources`
- source card frontmatter 是否缺字段
- `compiled_into` / `promote_into` 目标是否存在
- wiki 页面是否变成孤儿页
- 已标记 `resolved` 的 query 是否缺少有效落点

### 3.5 GitHub 收藏夹入口

- `../../scripts/ingest_github_issue_sources.py`
  负责把 GitHub issue 当成手工收藏夹入口。
- `../../github-issue-inbox.json`
  决定读取哪一类 issue。

这层做的事包括：

- 读取带指定 label 的 issue，或读取分配给指定账号的 issue
- 提取 issue 标题、正文、评论里的 URL
- 抓取轻量页面标题和描述
- 生成 `issue-inbox.md / issue-inbox.json`
- 在配置允许时评论并关闭已处理 issue

### 3.8 夜间情报审阅

- `../../scripts/build_nightly_review.py`
  负责夜间聚合新信息。
- `../../scripts/synthesize_nightly_review.py`
  负责把夜间情报包压缩成一份 review brief。
- `../../nightly-review-registry.json`
  决定 nightly sources 的范围。

这层做的事包括：

- 聚合 HN
- 聚合 watched feeds，例如 YouTube RSS 和用户自备的 Bilibili / X feed bridge
- 对照 `source-registry`、`candidates`、`issue-inbox`
- 生成 `nightly-review.md`
- 可选生成 `nightly-review-llm.md`
- 明确保留人工 admit / reject gate

### 3.9 视频学习 digest

- `../../scripts/build_video_learning_digest.py`
  负责把视频 transcript / subtitle / notes 压成学习 digest。
- `../../video-learning-registry.json`
  决定要处理哪些视频学习条目。

这层做的事包括：

- 读取本地 transcript / subtitle / notes
- 提取 highlights
- 提取 actionable takeaways
- 统计术语和工作流命中
- 生成 `video-learning.md / video-learning.json`

### 4. 建议下一步更新

- `../../scripts/build_knowledge_suggestions.py`
  负责把 `status + candidates + query-log` 编译成优先级队列。

这层不是自动改 wiki，而是告诉维护者：

- 哪些 tracked source 该优先复审
- 哪些候选来源该人工判断是否晋升
- 哪些 recurring question 该写回长期知识
- 哪些 discovery 缺口正在拖慢后台校准

### 5. 把会话问题写回长期知识

- `../../scripts/build_query_writeback_queue.py`
  负责把反复出现、值得沉淀的问题整理成 backlog。
- `../../query-log.json`
  是显式的 query memory，而不是让这些问题只活在聊天里。

## 什么还是人工完成

自动化现在只做到 `监控 -> 检查 -> 排队 -> 提醒`，没有直接重写 wiki。

仍然需要人工判断的环节：

- 候选来源是否值得晋升进 `source-registry.json`
- 某次 upstream 变化会如何改变执行策略
- 某条经验应留在 wiki，还是晋升到 `profiles/`、`benchmarks/` 或 `core/`
- benchmark 失败时，是该补规则，还是该退役旧规则
- 某条学习信号最终应 `admit / defer / reject`

这是刻意保留的人控层，不是缺陷。因为当前目标是让后台保持 `低噪声、可追责、可 diff`，而不是让自动化在没有证据的情况下重写结论。

## 真正的导演后台怎么闭环

当前闭环已经不是单点巡检，而是九段式：

1. `refresh_knowledge.py`
   复查已知来源
2. `discover_knowledge_candidates.py`
   发现未知来源
3. `ingest_github_issue_sources.py`
   处理手工收藏的 issue 来源
4. `build_nightly_review.py`
   做夜间情报汇总
5. `synthesize_nightly_review.py`
   生成 nightly review brief
6. `build_video_learning_digest.py`
   把视频 transcript / notes 变成学习 digest
7. `semantic_lint_knowledge.py`
   找结构不一致
8. `build_knowledge_suggestions.py`
   生成更新优先级
9. `build_query_writeback_queue.py`
   把用户问题转成长期 backlog

然后才进入人工 distill：

1. 改 `wiki/`
2. 需要时编译到 `profiles/` / `benchmarks/` / `core/`
3. 在 `log.md` 记录这次判断

这就是当前版本里“后台自动做什么、人工做什么”的边界。

换句话说：

- 脚本主要负责 `Plan / Do`
- 人工审阅负责真正的 `Check / Act`

少了后半段，就不叫 PDCA，只能叫半自动采集。

Compiled into:

- `../../schema/maintenance-playbook.md`

Sources:

- [../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md](../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md)
- [../../schema/maintenance-playbook.md](../../schema/maintenance-playbook.md)
- [../../../../../../.github/workflows/knowledge-refresh.yml](../../../../../../.github/workflows/knowledge-refresh.yml)
