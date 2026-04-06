# 中文模板库

这份模板库用于直接复制。优先覆盖三类场景：

1. `Veo 3.1 + Nano Banana 2`
2. `Veo 3.1 + Nano Banana Pro`
3. `Seedance` 风格分镜

## 1. 开场模型选择模板

```text
先确认一下你要出的模型栈：
1. Veo 3.1 + Nano Banana 2（默认推荐，适合大多数剧情短视频）
2. Veo 3.1 + Nano Banana Pro（更适合文字多、排版复杂、成片要求高的素材）
3. Seedance 风格分镜输出
4. 自定义模型栈
```

如果用户只说“我要 Veo”，追问：

```text
视频侧我先按 Veo 3.1 处理。图片侧你要配 Nano Banana 2、Nano Banana Pro，还是你有别的图像模型？
```

## 2. 标准素材表模板

```markdown
## 角色

### C01 - [角色名]
- 中文设定：[一句中文设定]
- 连续性锚点：[发型] / [服装] / [主色] / [配饰]
- 英文出图提示词：
  [英文角色设定提示词]

## 场景

### S01 - [场景名]
- 中文设定：[一句中文设定]
- 连续性锚点：[时间] / [天气] / [光线] / [主色调]
- 英文出图提示词：
  [英文场景设定提示词]

## 道具

### P01 - [道具名]
- 中文设定：[一句中文设定]
- 连续性锚点：[材质] / [磨损程度] / [颜色] / [标记]
- 英文出图提示词：
  [英文道具设定提示词]
```

## 3. Nano Banana 2 关键帧模板

适合大多数剧情镜头：

```markdown
A cinematic photorealistic [shot type] of [subject], [action or expression], in [environment]. The scene is lit by [lighting], creating a [mood] atmosphere. Captured with a [camera or lens look]. Preserve [continuity anchors]. [Aspect ratio]. No text, no watermark, no subtitles.
```

示例变量说明：

- `shot type`：close-up / medium shot / wide shot / over-the-shoulder
- `continuity anchors`：black trench coat, silver ring on right hand, wet hair, blue neon reflections

## 4. Nano Banana Pro 海报/标题卡模板

适合文字多、版式复杂、要高保真时：

```markdown
A high-fidelity cinematic poster featuring [subject], [action], and [secondary elements]. Environment: [environment]. Lighting: [lighting]. Camera: [camera or lens look]. Materials: [materials]. Render the text "[exact text]" in [font feel], placed [placement]. Preserve [continuity anchors]. [Aspect ratio]. Final output should be production-ready and text-accurate.
```

## 5. Nano Banana 改图模板

适合局部替换：

```markdown
Using the provided image, change only [target element] to [new element]. Keep identity, lighting, composition, background, wardrobe, camera angle, and aspect ratio exactly the same.
```

如果是多局部改动，不要一次全改。拆成多轮，每轮只改一类元素。

## 6. Veo 3.1 单镜头模板

适合一个镜头只有一个主要动作时：

```markdown
[cinematography] of [subject] [action] in [context], with [style and ambiance].
Dialogue: "[spoken line if any]"
SFX: [key effects]
Ambient: [room tone or ambience]
```

中文规划示例：

```text
镜头语言：雨夜街头中景跟拍
主体：女侦探
动作：快步穿过积水路面，抬头看向霓虹招牌
上下文：她刚发现新的线索，正赶往目标地点
风格和氛围：黑色电影、潮湿反光、悬疑压迫感
```

## 7. Veo 3.1 image-to-video 模板

适合只有一张关键图时：

```text
输入：
- 1 张关键图
- 1 条 Veo 提示词

写法重点：
- 明确这一张图里的主体如何开始运动
- 明确镜头如何跟随
- 明确结尾停在哪里
```

```markdown
[cinematography] of [subject] starting from the provided image and moving through [action] in [context], with [style and ambiance].
Dialogue: "[spoken line if any]"
SFX: [key effects]
Ambient: [room tone or ambience]
```

## 8. Veo 3.1 首尾帧模板

适合明确控制起点和终点状态时：

```text
输入：
- 首帧图
- 尾帧图
- 1 条 Veo 提示词

注意：
- 这里不是“首尾帧 + 参考视频”
- 重点是描述从首帧状态如何过渡到尾帧状态
```

```markdown
[cinematography] of [subject] moving from the first-frame pose to the final-frame pose in the same [environment]. Keep identity, wardrobe, props, focal length, and lighting consistent. Describe movement only.
```

## 9. Veo 3.1 extend video 模板

适合已有视频往后接：

```text
输入：
- 1 段已有视频
- 1 条新增部分提示词

写法重点：
- 明确“新增部分”发生什么
- 强调和原视频风格、主体、动作逻辑无缝衔接
```

```markdown
Extend the provided video by [X seconds]. Continue the same subject, environment, lighting, and motion logic. In the new segment, [describe only the newly added action and ending beat].
```

## 10. Seedance 参考视频模板

适合“参考这个视频的运镜/动作/节奏”：

```markdown
【参考】@视频1 参考运镜方式，@视频2 参考动作节奏
【要求】整体风格与参考素材一致，但主体替换为[主体]，剧情改为[剧情]
```

## 11. Seedance 分镜模板

```markdown
图片1: [角色参考]
图片2: [场景参考]
图片3: [道具参考]

[风格]，[画幅比例]，[整体氛围]

0-3s画面：[镜头运动]，[场景建立]，[主体引入]
3-6s画面：[镜头运动]，[情节发展]，[动作描述]
6-9s画面：[镜头运动]，[高潮或冲突]，[情绪]
9-12s画面：[镜头运动]，[转场]
12-15s画面：[镜头运动]，[结尾画面]

【声音】[配乐风格] + [音效] + [对白或旁白]

【参考】@图片1 [用途]，@图片2 [用途]，@图片3 [用途]
```

## 12. 常用故障回退模板

### 出图漂移

```text
这轮开始出现身份或构图漂移，停止在当前线程继续修改。回到上一张稳定图，重新发起一轮局部修改。
```

### 比例不稳定

```text
在 prompt 里重复声明画幅比例，并在 API 配置里再次设置比例；必要时补一张同画幅参考图。
```

### Veo 音频不稳定

```text
先生成运动画面或仅保留简单环境音，再单独补对白或后期声音，不要把复杂音频要求和复杂动作同时压进第一轮。
```

### Veo 工作流用错

```text
如果你手里是参考视频，不要写成 Veo 首尾帧。先判断你是要续拍已有视频，还是要参考视频里的运镜与动作；前者走 extend video，后者更接近 Seedance 参考视频写法。
```
