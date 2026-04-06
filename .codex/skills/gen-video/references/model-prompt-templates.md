# 模型提示词模板

这个文件用于两件事：

1. 开场先问用户选模型
2. 给不同模型提供首版提示词骨架

## 1. 开场模型选择问题

当用户没有明确指定模型栈时，用下面这个问题：

```text
先确认一下你要出的模型栈：
1. Veo 3.1 + Nano Banana 2（默认推荐，适合大多数剧情短视频）
2. Veo 3.1 + Nano Banana Pro（更适合文字多、排版复杂、成片要求高的素材）
3. Seedance 风格分镜输出
4. 自定义模型栈
```

更短的版本：

```text
先选一下目标模型栈：Veo 3.1 + Nano Banana 2、Veo 3.1 + Nano Banana Pro、Seedance，或者自定义。
```

当模型栈未指定时，默认应先只发这类选择问题。  
不要在同一条回复里一边问模型，一边提前给剧情、分镜或提示词。

如果用户说不确定，可以这样回答：

```text
如果你主要做剧情短视频，先用 Veo 3.1 + Nano Banana 2。只有在画面里文字很多、排版复杂、需要高分辨率终稿时，再把图片侧升级到 Nano Banana Pro。
```

只有当用户明确表示“直接开始”“不用问”“默认推荐即可”“你定就行”时，才可以跳过提问，直接采用 `Veo 3.1 + Nano Banana 2`，并明确说出这个默认假设。普通的“开始吧”“来做吧”“继续”不应默认视为跳过模型选择。

## 2. 中性场景描述模板

先写这份，再按模型重写：

```markdown
场景编号：[Sxx]
用途：[这一镜的剧情作用]
主体：[谁在画面里]
动作：[正在发生什么]
情绪：[主导情绪]
环境：[发生地点]
灯光：[光线特征]
镜头意图：[近景、远景、俯拍、跟拍等]
连续性锚点：[服装、道具、地点、天气、时间]
结尾钩子：[下一镜要继承什么]
```

## 3. Nano Banana 2 模板

```markdown
A [style] [shot type] of [subject], [action or expression], in [environment]. The scene is lit by [lighting], creating a [mood] atmosphere. Captured with a [camera or lens look]. Preserve [continuity anchors]. [Aspect ratio]. No text, no watermark, no subtitles.
```

文字较多时使用：

```markdown
A [style] [composition] of [subject or layout], in [environment or design context]. Render the text "[exact text]" in a [font feel] style, placed [placement]. Lighting: [lighting]. Materials: [materials]. [Aspect ratio].
```

改图时使用：

```markdown
Using the provided image, change only [target element] to [new element]. Keep identity, lighting, composition, background, wardrobe, camera angle, and aspect ratio exactly the same.
```

## 4. Nano Banana Pro 模板

结构和 Nano Banana 2 一样，但允许更密集的约束：

```markdown
A high-fidelity [style] [composition] featuring [subject], [action], and [secondary elements]. Environment: [environment]. Lighting: [lighting]. Camera: [camera or lens look]. Materials: [materials]. Render the text "[exact text]" in [font feel], placed [placement]. Preserve [continuity anchors]. [Aspect ratio]. Final output should be production-ready and text-accurate.
```

## 5. Nano Banana 旧版模板

写法比 Nano Banana 2 更简单：

```markdown
A [style] [shot type] of [subject] in [environment], [action or expression], lit by [lighting]. [Aspect ratio]. Preserve the same identity and composition as the reference image.
```

如果画幅比例非常重要，要在提示词和 API 配置里都重复写。

## 6. Veo 3.1 模板

单节拍镜头：

```markdown
[cinematography] of [subject] [action] in [context], with [style and ambiance].
Dialogue: "[spoken line if any]"
SFX: [key effects]
Ambient: [room tone or ambience]
```

多节拍镜头：

```markdown
[00:00-00:02] [establishing shot and action]
[00:02-00:04] [reaction or movement]
[00:04-00:06] [reveal, escalation, or turn]
[00:06-00:08] [ending beat and continuity hook]

Dialogue: "[spoken line if any]"
SFX: [key effects]
Ambient: [room tone or ambience]
```

带参考图的版本：

```markdown
Use the provided character and scene references. Keep the same identity, wardrobe, props, and lighting style. [cinematography] of [subject] [action] in [context]. Dialogue: "[spoken line if any]". SFX: [key effects]. Ambient: [room tone or ambience].
```

## 7. Seedance 兼容分镜模板

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
