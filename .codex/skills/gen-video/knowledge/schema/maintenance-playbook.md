# Maintenance Playbook

## Ingest

1. 为新来源创建 `raw/sources/*.source.md`
2. 如有原始副本，放进 `raw/captures/`
3. 在 `log.md` 记一条来源登记
4. 把可持续跟踪的来源加入 `../source-registry.json`

## Distill

1. 更新对应 wiki 页面
2. 补 `Sources`
3. 写清这次变化会影响什么执行判断

## Write Back

1. 把高价值 recurring question 登记进 `../query-log.json`
2. 用 `writeback-queue.md` 看哪些问题还没沉淀
3. 决定是新建 wiki，还是补已有页面

## Discover

1. `discovery-registry.json` 负责扫描更广的官方页和 bloger 页
2. 新发现先进入 `candidates.md`
3. 只有确认值得长期跟踪的来源，才提升到 `source-registry.json`

## Issue Inbox

1. 用带 `knowledge-source` label 的 GitHub issue 当手工收藏夹
2. `github-issue-inbox.json` 决定读取本仓库 issue，还是读取分配给账号的 issue
3. `ingest_github_issue_sources.py` 提取 issue 里的 URL、做轻量摘要，并在成功处理后评论 / 关闭 issue
4. 处理后的线索进入 `issue-inbox.md`，再由 `suggestions.md` 决定是否晋升到主 registry

## Nightly Review

1. `nightly-review-registry.json` 定义夜间采集入口
2. `build_nightly_review.py` 聚合 HN 与 watched feeds
3. `synthesize_nightly_review.py` 用 LLM 或 prompt-pack 生成 nightly review brief
4. 维护者只根据 review 做 admit / defer / reject，不直接让夜间抓取结果自动入库

## Compile

1. 只把可直接执行的结论写进 `profiles/`
2. 不要把高波动事实写进 `core/`
3. 如果只是试探性判断，先留在 wiki

## Validate

1. 用 `benchmarks/` 里的样题验证
2. 记录失败点和模式选择变化
3. 决定是晋升、保留观察，还是退役旧规则

## Lint

1. 运行 `semantic_lint_knowledge.py`
2. 先修结构问题，例如缺 `Sources`、断链、孤儿页
3. 再处理判断本身的更新

## Suggest

1. 运行 `build_knowledge_suggestions.py`
2. 先处理高优先级 tracked source 和 query writeback
3. 再处理 candidate promotion 和 discovery gap

## Log

1. 在 `knowledge/log.md` 写入日期、事项、动作、下次复查时间
2. 如果更新了 `profiles/` 或 `core/`，在 log 里写明编译目标

## CI

1. `.github/workflows/knowledge-refresh.yml` 按计划运行 refresh 脚本
2. CI 负责维护来源卡、metadata capture、status 面板、candidates 队列、issue inbox、nightly review、LLM review、lint、suggestions、writeback queue 和 index 摘要
3. `wiki/` 的综合判断仍由人工更新，再决定是否编译到 `profiles/` 或 `core/`
