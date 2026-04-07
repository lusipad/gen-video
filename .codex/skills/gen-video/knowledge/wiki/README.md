# Wiki

`wiki/` 是可维护的综合判断层。

这里的页面允许重写，但应遵守以下规则：

- 每页都应在结尾列出 `Sources`
- 结论要面向执行，不要写成长篇资料堆叠
- 如果页面已经编译进 `profiles/`、`benchmarks/` 或 `core/`，应显式写出目标
- 当来源失效或 benchmark 反证时，优先改 wiki，再决定是否改下游文档
- 高频用户问题应先登记到 `../query-log.json`，再决定写成哪一页
- 写完或改完页面后，应用 `../lint.md` 和 `../suggestions.md` 回看结构一致性与优先级
