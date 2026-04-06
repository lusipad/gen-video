# Veo 与 Nano Banana 模型说明

当目标栈包含 Google 的图片或视频模型时，使用这份说明。目标不是写一套万能提示词，而是把同一个场景改写成适合不同模型的版本。

## 1. 模型选择

### 默认选择

- 默认静态图模型：Nano Banana 2（`gemini-3.1-flash-image-preview`）
- 默认高质量静态图模型：Nano Banana Pro（`gemini-3-pro-image-preview`）
- 默认旧版快速静态图模型：Nano Banana（`gemini-2.5-flash-image`）
- 默认视频模型：Veo 3.1

### 什么时候用哪个

- 大多数关键帧、角色设定图、场景图、道具图、改图任务，使用 Nano Banana 2。
- 文字很多、排版复杂、需要高分辨率终稿、需要更强遵循时，使用 Nano Banana Pro。
- 只有在吞吐优先、成本优先、且 1024 级输出可接受时，才使用 Nano Banana。
- 涉及动作、镜头、时间推进、对白、环境音时，使用 Veo 3.1。不要直接把静态图提示词拿去做 Veo 提示词。

### 会影响结果的核心能力差异

- Nano Banana 2 支持原生画幅、512、1K、2K、4K，多图组合、文字渲染和指令遵循都比旧版 Flash Image 更强。
- Nano Banana Pro 自带更强推理，更适合复杂版式、信息图、海报、本地化文字、以及高分辨率交付。
- Nano Banana 仍然可用，但它更接近 1024 级模型，社区里关于宽高比控制和 API 稳定性的坑更多。
- Veo 3.1 支持 4、6、8 秒片段，支持 16:9 和 9:16，支持音频、图生视频、ingredients-to-video，以及首尾帧工作流。

## 1.1 Veo 工作流边界

Veo 3.1 里最容易混淆的是下面四种工作流：

- `image-to-video`：输入一张图，再补文字提示词
- `first-and-last-frame`：输入首帧图和尾帧图，再补文字提示词
- `ingredients-to-video`：输入多张图片素材，再补文字提示词
- `extend video`：对已有视频继续生成

关键规则：

- `first-and-last-frame` 不是“首尾帧 + 参考视频”
- 如果用户说“参考这个视频的运镜/动作”，这更像 `Seedance 参考视频` 或 `extend video`
- 如果用户说“我只想用两张图控制开头和结尾”，这才是 `first-and-last-frame`
- 如果用户说“我要继续上一段已经生成好的视频”，这才是 `extend video`

## 2. 各模型的提示词写法

### Nano Banana 2 与 Nano Banana Pro

写法以最终静态画面为中心，优先写完整描述，不要只堆标签。

建议至少包含：

- 主体
- 动作或表情
- 环境
- 灯光
- 镜头感或镜头焦段
- 材质细节
- 画幅比例
- 需要渲染的准确文字
- 版式或位置要求

推荐模板：

```markdown
A photorealistic [shot type] of [subject], [action or expression], set in [environment]. The scene is illuminated by [lighting], creating a [mood] atmosphere. Captured with a [camera or lens look], emphasizing [textures or details]. [Aspect ratio]. [If needed: render the text "...", in a ... font, placed ...].
```

改图时必须强约束：

```markdown
Using the provided image, change only [specific element] to [new element]. Keep everything else exactly the same, including identity, lighting, composition, background, and aspect ratio.
```

多图合成时：

```markdown
Create a new image by combining the provided references. Take [element from image 1] and place it on or in [element from image 2]. Match the final lighting, shadows, perspective, and material realism to [target scene].
```

### Nano Banana（Gemini 2.5 Flash Image）

结构与上面相同，但写法要更克制：

- 尽量保证一个明确主体、一个明确场景
- 不要一次塞太多排版和构图约束
- 画幅比例要显式写
- 如果输入图比例必须保留，也要显式写

这个模型适合高频迭代，但连续改图太多轮后很容易漂移，要更早重置。

### Veo 3.1

写法以过程为中心。要像导演和声音设计师一样描述，而不是像静态摄影提示词。

建议结构：

```markdown
[cinematography] + [subject] + [action] + [context] + [style and ambiance]

Dialogue: "[spoken line if any]"
SFX: [key effects]
Ambient: [room tone, weather, crowd, room noise, silence, etc.]
```

可复用的镜头语言：

- wide shot
- close-up
- medium shot
- low angle
- POV shot
- tracking shot
- dolly shot
- crane shot
- slow pan
- shallow depth of field

只有在 8 秒片段里确实有多个节拍时，才写时间戳块：

```markdown
[00:00-00:02] 建立镜头与进入动作。
[00:02-00:04] 反应镜头或推进。
[00:04-00:06] 揭示、升级或转折。
[00:06-00:08] 结尾动作与续接钩子。
```

Veo 各工作流的写法重点不同：

- `image-to-video`：重点写这一张图之后如何动起来
- `first-and-last-frame`：重点写从首帧状态如何过渡到尾帧状态
- `ingredients-to-video`：重点写多张图片素材各自承担什么角色
- `extend video`：重点写新生成部分如何接上旧视频

## 3. Veo 3.1 + Nano Banana 2 的推荐工作流

默认流程如下：

1. 先写一份中性的场景标准描述。
2. 用 Nano Banana 2 产出角色、场景、道具参考图。
3. 用 Nano Banana 2 或 Nano Banana Pro 产出关键帧。
4. 把这些参考图喂给 Veo 3.1，走以下工作流之一：
   - image-to-video
   - ingredients-to-video
   - first-and-last-frame
5. 单独写一份 Veo 运动提示词，只描述动作、节奏、镜头和声音。

核心原则：

- 静态图提示词定义世界长什么样。
- Veo 提示词定义这个世界在时间里发生什么变化。

## 4. 具体问题与处理方法

### A. Nano Banana 2 与 Nano Banana Pro

#### 文字渲染

- 这两代模型的文字渲染和本地化能力明显强于旧版 Flash Image。
- 如果文字很重要，必须写清楚准确内容、位置和字体感觉。
- 如果画面里不能出现文字，也要明确写：`No text, no subtitles, no watermark, no logo lockup, no labels.`

#### 参考图质量会直接影响结果

- 清晰、不模糊的参考图明显更稳定。
- API 单图任务里，通常先放图片 part，再放文字 prompt。
- 当请求超过 20MB，或者同一张图会反复使用时，优先走 Files API。

#### 连续改图太多轮会漂移

- 如果人物身份、构图或风格开始漂移，直接回到最后一张好的图重开一轮。
- 不要在已经坏掉的分支上继续打补丁。

#### 改图提示词必须控制范围

- 如果你只改一个局部，就明确写 `change only`。
- 同时重复声明必须保持不变的内容：身份、灯光、构图、背景、服装、机位、画幅比例。

#### 什么时候升级到 Nano Banana Pro

- 海报、字幕卡、信息图、排版复杂页面、多语言文字、UI 风格画面、高分辨率终稿，直接升 Pro。
- 如果 Nano Banana 2 经常只执行了复杂要求的一部分，也应切到 Pro。

### B. Nano Banana（Gemini 2.5 Flash Image）

#### 分辨率上限

- 把它当作 1024 级模型看待。
- 不要承诺用它直接出 2K 或 4K 成片素材。

#### 画幅比例问题

- 官方文档现在支持用配置指定画幅比例。
- 但 2025 年末社区反馈较多，早期 preview 和部分 API 路径里会忽略比例要求，返回方图或质量异常。
- 如果比例不稳定，要同时在 `image_config` 和提示词正文里写比例，必要时再提供同样比例的参考图。

#### SDK 与 API 版本错配

- 社区里有过旧版 SDK 找不到 `ImageConfig` 或相关配置字段的问题。
- 如果配置字段不存在，优先升级 Google GenAI SDK，不要先怀疑提示词。

#### 稳定性与重试

- 社区反馈过随机不返回图片、内部错误、`IMAGE_OTHER` 之类的问题。
- 如果是生产流程，必须准备重试和 fallback，关键素材最好能切到 Nano Banana 2 或 Pro。

### C. Veo 3.1

#### 先判断是不是用错工作流

- 如果用户提供的是参考视频，不要直接往 `first-and-last-frame` 里套
- 如果用户需要的是“参考某段视频的运镜和动作”，更接近 Seedance 的参考视频写法
- 如果用户需要的是“已有视频继续往后生成”，更接近 `extend video`
- 如果用户只有首尾两张图，并希望模型自己补中间过程，这才是 `first-and-last-frame`

#### 音频在真实产品里不总是稳定

- 官方说明支持完整音轨、对白、音效和环境音。
- 但社区反馈中仍然存在无音频、乱加背景乐、对白唱出来等问题。
- 如果音频很重要，把音频要求拆成单独块，描述尽量简洁。
- 如果平台仍然忽略音频，拆成两步：
  - 第一步先出纯运动视频或只保留简单环境音
  - 第二步再单独补声音或后期处理

#### 参考图与竖屏限制

- Veo 3.1 核心支持 16:9 和 9:16。
- 但开发者论坛曾明确提到，`referenceImages` 在当时只支持 16:9，9:16 仍在补。
- 如果你发现竖屏加参考图失败，可以：
  - 先走 16:9 生成，再二次裁切或重构图
  - 先单独生成竖屏关键帧，再走不依赖参考图的 Veo 流程

#### 首尾帧中间幻觉

- 如果模型在首尾帧过渡中途突然换人、换景、换物，先缩小首尾帧之间的视觉差距。
- 在首尾帧里固定服装、场景、焦段和灯光。
- 如果仍不稳定，拆成两个更短的过渡片段。
- 不要误以为再加参考视频就能解决首尾帧问题；首尾帧工作流本身不是视频参考工作流。

#### 真人脸误判

- 社区里出现过普通真人照片被误判成名人肖像，导致图生视频失败。
- 遇到这种情况，可以尝试：
  - 换一张相似度更低的图
  - 降低与公众人物的相似特征
  - 用合成参考图替代真实照片

#### 保持一致性的写法

- 跨镜头重复使用同一套角色、服装、道具、地点描述。
- 同一个角色不要在不同镜头里频繁换叫法。
- 尽量使用 Nano Banana 系列先产出的参考图，而不是每次都重新从零描述角色。

## 5. 在本技能中的推荐输出层次

当目标栈是 Veo 3.1 + Nano Banana 2 时，优先输出四层：

1. 标准化故事与镜头拆解
2. 标准化素材资产表
3. Nano Banana 2 的关键帧提示词
4. Veo 3.1 的运动提示词

可选第五层：

5. 只有在用户要求时，再补 Seedance 风格时间轴分镜

## 6. 来源说明

用于形成这份说明的官方资料包括：

- Google AI 文档中的 Nano Banana 图片生成说明
- Google Developers Blog 的 Gemini 2.5 Flash Image 提示词指南
- Google blog 的 Nano Banana 2 构建说明
- Google Cloud blog 的 Veo 3.1 提示词指南
- Vertex AI 文档中的 Veo 视频生成说明
- Google AI 文档中的图片输入最佳实践

用于补充实际坑位的社区资料包括：

- Google AI Developers Forum 中关于 Gemini 2.5 Flash Image 的比例、稳定性、SDK 配置问题
- Google AI Developers Forum 中关于 Veo 3.1 的比例、参考图限制、一致性漂移、真人误判问题
- Reddit 中关于 Veo 3.1 音频不稳定和 Nano Banana 2 产品回归的讨论
