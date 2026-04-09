# Video Review Raw Inputs

这个目录存放“生成后自动审片”所需的原始证据。

推荐放这里的内容：

- `*.mp4`
  生成后的视频文件
- `*.metadata.json`
  视频元数据；当本地没有 `ffprobe` 时，用它补 duration / width / height
- `*.vtt` / `*.srt` / `*.txt`
  视频 transcript、字幕或 ASR 结果
- `*.frames.md`
  关键帧、镜头切分、画面观察笔记
- `*.review.md`
  额外的人工或外部模型审片笔记

建议命名：

- `YYYY-MM-DD_<platform>_<slug>.mp4`
- `YYYY-MM-DD_<platform>_<slug>.metadata.json`
- `YYYY-MM-DD_<platform>_<slug>.vtt`
- `YYYY-MM-DD_<platform>_<slug>.frames.md`
- `YYYY-MM-DD_<platform>_<slug>.review.md`

然后把对应路径优先登记到 `../../video-evidence-registry.json`。
如果你已经准备直接审片，也可以在 `../../video-review-registry.json` 中保留同一个 `evidence_id` 作为下游引用。

推荐顺序：

1. 准备这些原始证据
2. 运行 `build_video_evidence_bundle.py`
3. 确认 `video-evidence.md/json` 没有明显缺证
4. 再运行 `build_video_review_report.py`

## 最小可运行组合

最稳的最小组合不是“只有一个 mp4”，而是：

1. `metadata.json`
2. `transcript / subtitle`
3. `frames.md` 或其他镜头观察文本

这样即使本地没有 `ffprobe`，`build_video_review_report.py` 也能生成结构化 `verdict`。

## metadata.json 示例

```json
{
  "duration_seconds": 182.4,
  "width": 1080,
  "height": 1920
}
```

## frames.md 建议写法

```md
## 00:00-00:08
- 老人坐在桌前修滚灯骨架，动作明显吃力
- 背景是奉贤老宅，不是泛化古镇

## 00:48-00:58
- 孙女在电脑前做 AI 方案
- 画面里有滚灯结构参考图
```
