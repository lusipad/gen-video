# Video Review Loop

这个页面回答一个具体问题：

`生成后的视频，怎样进入一条可执行的审片闭环。`

## 当前目标

当前版本先把“自动审片”拆成三步，而不是假装仓库已经能完全自动看懂视频：

1. 先提取并整理证据
2. 再根据这些证据产出 verdict
3. 再把 verdict 编译成 `Act` 队列

这样做的原因是：

- 更稳
- 更容易复核
- 更容易定位失败镜头
- 更容易接进前台 PDCA

## 当前链路

### 1. 原始证据

进入 `benchmarks/raw/video-review/` 的内容包括：

- `mp4`
- `metadata.json`
- `transcript / subtitle`
- `frames.md`
- `review.md`

这层不直接出 verdict，只负责留下证据。

### 2. Evidence Bundle

- `../../../../benchmarks/video-evidence-registry.json`
  定义有哪些原始视频证据需要被标准化。

- `../../../../scripts/build_video_evidence_bundle.py`
  把原始证据整理成统一 bundle。

- `../../../../benchmarks/video-evidence.md`
  给人看的证据面板。

- `../../../../benchmarks/video-evidence.json`
  给脚本读的结构化证据。

这一步回答的是：

- 有没有足够证据能继续审
- 当前缺什么
- transcript 和 marker 是否已经整理出来

### 3. Review Verdict

- `../../../../scripts/build_video_review_report.py`
  对照验收条件做 heuristic checks，并在配置了模型时生成 LLM review。

- `../../../../benchmarks/video-review.md`
  输出最终 `pass / fail / uncertain`。

这一层回答的是：

- 这条视频现在能不能过
- 哪些要求已经满足
- 哪些要求失败
- 哪些证据不足，只能判 `uncertain`

### 4. Act Queue

- `../../../../scripts/build_video_review_action_queue.py`
  把 `video-review.json` 编译成结构化 `Act` 队列。

- `../../../../benchmarks/video-review-actions.md`
  给人看的后续动作面板。

- `../../../../benchmarks/video-review-actions.json`
  给脚本读的结构化动作队列。

这一层回答的是：

- 失败后先重做什么
- 证据不足时先补什么
- 通过样例要不要写回 benchmark / knowledge
- 哪些动作应该继续进入 `knowledge/suggestions.md`

## 它会如何影响执行

- 对前台 PDCA
  `Check` 不再只有“看文档像不像”，而是可以针对成片做结构化复核。

- 对镜头重做
  当 `frames.md` 或 `review.md` 里有时间段 marker 时，可以更明确地指出失败镜头，而不是整条片盲目重跑。

- 对 benchmark
  审片 verdict 可以反过来作为 benchmark 证据，决定是保留现有规则，还是该更新 profile / mode。

- 对后台建议队列
  `video-review-actions.json` 可以继续被 `build_knowledge_suggestions.py` 吸收，把高信号失败项、证据缺口和通过样例写回动作推到后台维护优先级里。

## 当前边界

- 不是完整的视觉理解系统
- 还不自动下载视频、抽帧、做 ASR
- 本机没有 `ffprobe` 时，需要 sidecar `metadata.json`
- 审美判断和情绪强度仍要保留人工终审

## 推荐顺序

1. 先生成视频
2. 把证据放进 `benchmarks/raw/video-review/`
3. 跑 `build_video_evidence_bundle.py`
4. 确认证据够不够
5. 再跑 `build_video_review_report.py`
6. 再跑 `build_video_review_action_queue.py`
7. 根据 action queue 决定是重做镜头、补证据，还是回写 benchmark / knowledge

Compiled into:

- ../../../../benchmarks/README.md
- ../../../../core/pdca-loop.md

Sources:

- [../../../../benchmarks/raw/video-review/README.md](../../../../benchmarks/raw/video-review/README.md)
- [../../../../benchmarks/video-evidence-registry.json](../../../../benchmarks/video-evidence-registry.json)
- [../../../../benchmarks/video-review-registry.json](../../../../benchmarks/video-review-registry.json)
- [../../../../core/pdca-loop.md](../../../../core/pdca-loop.md)
