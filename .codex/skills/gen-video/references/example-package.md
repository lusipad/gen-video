# 小样示例

这是一份最小可用示例，用于说明本技能最终应该产出什么，不要求每次都照抄。

## 示例前提

- 目标模型栈：Veo 3.1 + Nano Banana 2
- 风格：黑色电影 + 都市悬疑
- 画幅：9:16
- 输出：3 个关键镜头的小样

## 故事概念

雨夜，一名年轻女侦探在旧城区追查失踪案。她在一家关门的照相馆门口发现一张被雨水浸湿的老照片，照片里出现了和自己长得极像的人。

## 1. 剧情拆解

### 镜头 1
- 用途：建立人物和环境
- 情节：女侦探走进旧城区小巷
- 情绪：警惕、压抑
- 开场画面：雨夜远景，小巷积水反光
- 结尾画面：她停在照相馆门口，低头看见地上的东西

### 镜头 2
- 用途：发现线索
- 情节：她弯腰捡起老照片
- 情绪：疑惑、紧张
- 开场画面：鞋尖旁边是一张浸湿照片
- 结尾画面：她看清照片内容，瞳孔微缩

### 镜头 3
- 用途：制造悬念
- 情节：镜头切到她手中的照片，照片里的人与她极像
- 情绪：震惊、悬疑
- 开场画面：她举起照片，雨滴沿边缘滑落
- 结尾画面：她猛然抬头，看向街对面黑暗中的橱窗

## 2. 素材资产表

### C01 - 女侦探
- 中文设定：二十多岁，瘦高，短发，黑色风衣，冷峻、疲惫但警觉
- 连续性锚点：黑色长风衣、湿发贴额、右手银戒指、深灰衬衫
- 英文出图提示词：
  A young female detective, slim build, short dark wet hair, wearing a long black trench coat over a dark gray shirt, a silver ring on her right hand, tired but sharp eyes, cinematic noir realism.

### S01 - 旧城区雨巷
- 中文设定：老城区窄巷，霓虹灯反射在积水地面，墙面斑驳，气氛压抑
- 连续性锚点：蓝红霓虹倒影、湿漉漉路面、旧招牌、深夜
- 英文出图提示词：
  A narrow old-city alley at night, wet pavement reflecting blue and red neon lights, worn concrete walls, old shop signs, noir urban atmosphere, damp air, cinematic realism.

### P01 - 老照片
- 中文设定：一张被雨水浸湿的黑白旧照片，边角卷曲，表面有轻微划痕
- 连续性锚点：黑白、卷角、湿痕、人物半身像
- 英文出图提示词：
  A rain-soaked vintage black-and-white photograph with curled corners, subtle scratches, visible water stains, showing a half-body portrait, realistic texture detail.

## 3. Nano Banana 2 关键帧提示词

### 镜头 1 关键帧

```markdown
A cinematic photorealistic wide shot of a young female detective walking into a narrow old-city alley at night, her black trench coat moving slightly in the rain. The scene is lit by blue and red neon reflections on wet pavement, creating a tense noir atmosphere. Captured with a 35mm lens look. Preserve black trench coat, wet short hair, silver ring on the right hand, and the old shop signs. 9:16. No text, no watermark, no subtitles.
```

### 镜头 2 关键帧

```markdown
A cinematic photorealistic medium close-up of a young female detective bending down to pick up a rain-soaked vintage photograph from the wet ground outside an old photo studio. The scene is illuminated by cold neon spill and dim street light, creating a suspicious and tense mood. Captured with a 50mm lens look. Preserve black trench coat, wet short hair, silver ring on the right hand, rain reflections, and the old storefront. 9:16. No text, no watermark, no subtitles.
```

### 镜头 3 关键帧

```markdown
A cinematic photorealistic close-up of a wet vintage black-and-white photograph held in a young female detective's hand, rain droplets sliding across the edge, revealing a portrait of someone who looks almost identical to her. The scene is lit by cold blue neon and soft street light, creating a shocking noir atmosphere. Captured with an 85mm lens look. Preserve silver ring, wet fingertips, curled photo corners, and the dark rainy street background. 9:16. No text, no watermark, no subtitles.
```

## 4. Veo 3.1 运动提示词

### 镜头 1

```markdown
Wide tracking shot of a young female detective walking carefully into a narrow rainy alley at night, with wet neon reflections on the ground and a tense noir atmosphere. She slows down as she notices something near the entrance of an old photo studio.
Dialogue: ""
SFX: soft footsteps in shallow water, distant thunder
Ambient: steady rain, faint city hum
```

### 镜头 2

```markdown
[00:00-00:02] Medium shot as the detective stops and looks down near the old photo studio entrance.
[00:02-00:04] Closer shot as she crouches and reaches toward a rain-soaked photograph on the ground.
[00:04-00:06] Close-up of her fingers lifting the wet photo.
[00:06-00:08] Ending beat as her expression freezes with growing alarm.

Dialogue: ""
SFX: fabric rustle, water drip, fingers lifting wet paper
Ambient: rain, low urban night ambience
```

### 镜头 3

```markdown
Close-up of the detective holding a rain-soaked vintage photograph under neon light, revealing a portrait that looks almost identical to her. The camera slowly pushes in as rain runs across the photo edge, then she sharply lifts her gaze toward the darkness across the street.
Dialogue: "..."
SFX: rain tapping on paper, faint electrical buzz from the sign
Ambient: rainy alley night, distant traffic
```

## 5. 这个示例体现的原则

- 图片提示词负责定义画面长相
- Veo 提示词负责定义画面如何运动
- 人物、服装、戒指、雨夜巷子、照片状态这些连续性锚点在每个镜头里都重复出现
- 每个镜头只承担一个主要叙事动作，不把整段剧情塞进一条 prompt
