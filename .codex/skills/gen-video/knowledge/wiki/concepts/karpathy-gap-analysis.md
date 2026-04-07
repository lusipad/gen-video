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

- [../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md](../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md)
- [../operations/knowledge-automation-surface.md](../operations/knowledge-automation-surface.md)
