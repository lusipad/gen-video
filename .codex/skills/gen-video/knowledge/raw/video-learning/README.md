# Video Learning Raw Inputs

这个目录存放“视频学习”链路的原始输入，而不是综合判断。

推荐放这里的内容：

- `*.srt`
  字幕文件
- `*.vtt`
  字幕或 transcript
- `*.txt`
  纯文本转录
- `*.md`
  人工补充的拆解笔记、镜头观察、重点摘录

建议命名：

- `YYYY-MM-DD_<platform>_<slug>.vtt`
- `YYYY-MM-DD_<platform>_<slug>.srt`
- `YYYY-MM-DD_<platform>_<slug>.notes.md`

把文件放进这里后，再去更新 `../../video-learning-registry.json` 的对应 entry。

每条 entry 建议显式区分学习目标：

- `content`
  学视频内容、人物、情绪和结构
- `craft`
  学分镜、镜头、脚本组织、提示词和工作流

当前第一版视频学习链路是 `transcript / subtitle / notes` 驱动，而不是直接解码 `mp4`。  
也就是说，它先解决：

- 如何把视频内容拆成可复查的文本片段
- 如何从文本片段里提炼 highlights / takeaways
- 如何把这些结果接进导演后台学习链路

而不是直接替代完整的视频本体理解模型。

它的目标是先给导演后台提供低成本、可审阅、可 diff 的学习材料。
