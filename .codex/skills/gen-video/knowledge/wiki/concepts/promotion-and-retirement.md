# Promotion And Retirement

知识进入不同层级的标准应当不同。

## 放置原则

- `raw/`
  原始来源、快照、记录

- `wiki/`
  基于来源做的可重写综合判断

- `profiles/`
  当前仍然有效、能直接指导模型 / 平台分流的结论

- `benchmarks/`
  用于验证结论是否仍然成立的样题与结果

- `core/`
  经过多轮验证后仍稳定的规则

## 晋升条件

一个结论从 wiki 晋升到 `profiles/` 或 `core/` 前，至少满足：

1. 有可追溯来源或实测依据
2. 能直接改变执行方式，而不只是“有点启发”
3. 预计能撑过至少一个更新周期

## 退役条件

以下情况应优先考虑退役旧规则：

- benchmark 连续显示 `native` 或 `hybrid` 已优于旧手工流程
- 平台原生支持覆盖了原来 skill 的补丁逻辑
- 用户真实使用中频繁出现“skill 比平台本身更繁琐”的反馈

所有晋升和退役决定，都应写入 `../../log.md`。

Sources:

- [../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md](../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md)
