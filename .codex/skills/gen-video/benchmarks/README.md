# Benchmarks

`benchmarks/` 用来避免这个 skill 变成静态经验包。

目标不是追求“规则越来越多”，而是持续比较：

- `native` 是否已经比 `manual` 更好
- `hybrid` 是否比纯手工更轻更稳
- 某个平台升级后，哪些旧规则已经可以退役

benchmark 不是终点。它同时承担前台 `Check` 和后台 `Act` 的桥接作用。

结果要回写 `../knowledge/log.md`，并决定是否更新 `../profiles/` 或退役旧规则。

如果你在复核一轮具体交付物，先用 [output-review-template.md](output-review-template.md)。

如果你要做“生成视频后自动审片”，再看：

- [video-evidence-registry.json](video-evidence-registry.json)
- [video-evidence.md](video-evidence.md)
- [video-review-registry.json](video-review-registry.json)
- [video-review.md](video-review.md)
- [video-review-actions.md](video-review-actions.md)
- [raw/video-review/README.md](raw/video-review/README.md)

## benchmark 的最小结构

每一条 benchmark 至少记录：

- 任务类型
- 模型 / 平台
- 使用模式
- 产出质量
- 失败点
- 是否应更新 skill
- `Check verdict`
- `Act`

## 建议覆盖的样题

- 现实题材
- 催泪亲情片
- 非遗 / 地方文化
- 广告短片
- `Google Flow` 中长片
- `Seedance` 自动分镜

## 自动审片命令

```powershell
python .codex/skills/gen-video/scripts/build_video_evidence_bundle.py
python .codex/skills/gen-video/scripts/build_video_review_report.py
python .codex/skills/gen-video/scripts/build_video_review_action_queue.py
```

只做一致性校验时：

```powershell
python .codex/skills/gen-video/scripts/build_video_evidence_bundle.py --check
python .codex/skills/gen-video/scripts/build_video_review_report.py --check
python .codex/skills/gen-video/scripts/build_video_review_action_queue.py --check
```
