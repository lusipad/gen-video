# Refresh Loop

建议用一个轻量但固定的刷新循环维护这个 skill：

1. 收来源
   官方文档、产品发布说明、实测记录、benchmark 结果先进入 `raw/`

2. 写 wiki
   把“这次变化意味着什么”整理进对应 wiki 页面

3. 编译 profile
   只有会直接影响执行路线的结论，才更新 `profiles/`

4. 跑 benchmark
   用代表性样题验证当前 `native / hybrid / manual` 判断是否还对

5. 退役规则
   如果旧规则已经比平台原生更累赘，就弱化、删除或降级

6. 写 log
   记录变更、证据、结论和下次复查日期

## 触发条件

- 模型或平台发布新版本
- benchmark 失败率明显上升
- 用户反馈现有工作流变得累赘
- 新增重要执行平台或模型组合

## 刷新优先级

- A 类：模型能力、平台 UI、支持矩阵
  每周或每两周

- B 类：组合工作流、提示词组织方式、交付模板
  每月

- C 类：叙事结构、真实性规则、质量门
  按需

Compiled into:

- `../../profiles/README.md`
- `../../benchmarks/README.md`

Sources:

- [../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md](../../raw/sources/2026-04-06_karpathy-llm-wiki.source.md)
