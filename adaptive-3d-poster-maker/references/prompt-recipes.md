# 图像生成提示词配方

## 主配方

```text
Use case: ads-marketing
Asset type: <用途 + 比例 + 海报类型>
Primary request: 将提供的文案设计成白色主调、彩色点缀的 2026 3D 极简宣传海报；内容优先，不复制固定模板
Scene/backdrop: <暖白/冷白/珍珠白>背景，大面积留白，轻微空间地面或编辑式网格
Subject: <与主题相关的 3D 英雄物体>；<根据文案选择的布局原型>
Style/medium: 高端 3D 产品视觉，编辑式排版，克制的未来感
Composition/framing: <比例>；<标题区、主视觉区、信息区的大致占比>；明确安全边距
Lighting/mood: 明亮高调棚拍，柔和接触阴影，清晰、可信、乐观
Color palette: 白色占 70%–90%；石墨黑文字；<辅助配色>
Materials/textures: <一个主材质> + <一个辅材质>
Text (verbatim): "<必须逐字保留的文字>"
Constraints: 中文准确；只出现指定文字；移动端可读；无 Logo、二维码、水印和随机英文
Avoid: 深色赛博背景、霓虹泛滥、廉价科技蓝模板、文字墙、低对比度、重复模块
```

## 按内容切换布局

- 并列指标：轨道系统、模块画廊或数据核心。
- 流程步骤：路径叙事或层叠卡片。
- 短标题宣传：3D 字体雕塑或非对称编辑分栏。
- 产品功能：3D 英雄物体 + 信息舱。
- 长文摘要：先分成 3–5 个一级组，再选择平衡型或信息图型。

## 文案准确性

- 把必须准确的文字逐条加引号，并要求“exactly once”。
- 中英文混排时明确保留大小写、斜杠、连字符和数字。
- 生成后逐字核对。单处错误只做定向编辑，并重申其他元素保持不变。
- 如果文案超过单张海报的可读容量，给出压缩建议或拆分系列，不擅自缩成不可读小字。

## 变体提示

同一内容的第二版应显式替换至少两个变量，例如：

```text
Change layout from a 3D hero object with a card grid to an asymmetric editorial split.
Change materials from pearl ceramic + iridescent glass to white paper relief + restrained chrome.
Keep the content, white-dominant palette, exact text and requested canvas unchanged.
```

不要只写“再高级一点”或“换个颜色”；应说明变化发生在哪些设计轴上。
