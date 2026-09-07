# 官网文章配色库

准确颜色值以 [color-palettes.json](color-palettes.json) 为单一来源。每套方案都包含相同的 12 个语义令牌，因此只换颜色，不改变文章结构、字号和间距。

## 八套可选方案

| ID | 名称 | 优先适用 |
| --- | --- | --- |
| `olive-gold` | 墨绿暖金 | 企业案例、经营复盘、品牌观点 |
| `ocean-copper` | 海蓝铜棕 | AI 工具、科技教程、数字化 |
| `indigo-amber` | 靛紫琥珀 | 创新趋势、专业洞察、知识服务 |
| `burgundy-brass` | 酒红黄铜 | 人物故事、品牌文化、高端服务 |
| `pine-clay` | 松绿陶土 | 制造业、可持续经营、生活方式 |
| `graphite-blue` | 石墨蓝灰 | 研究报告、B2B 方案、数据分析 |
| `teal-coral` | 青黛珊瑚 | 用户案例、增长实践、轻量教程 |
| `midnight-gold` | 午夜蓝金 | 战略观点、企业管理、商业分析 |

## 语义令牌

| 令牌 | 用途 |
| --- | --- |
| `background` | 正文和按钮的基础背景 |
| `body` | 正文主文字 |
| `secondary` | 导语后的次级正文 |
| `heading` | 导语、章节标题和来源标题 |
| `emphasis` | 链接、重点句和强调线 |
| `accent` | 章节编号等小面积锚点 |
| `label` | CTA 标签与辅助说明 |
| `url` | 来源 URL 辅助文字 |
| `border` | 章节分隔线 |
| `strong_border` | 结论强调条边线 |
| `cta` | 主按钮背景与次按钮描边 |
| `soft` | 少量提示区的柔和背景 |

## 选择规则

1. 用户指定 ID 或中文名称时直接使用。
2. 用户只描述题材时，可按表格的“优先适用”选择。
3. 用户没有偏好时，运行 `scripts/select_palette.py --title "文章标题"`，由标题稳定选出一套；相同标题会得到相同结果，便于重排复现。
4. 批量排版时，把上一篇采用的 ID 传给 `--avoid`；需要避免最近多套时可重复传入。若所有方案都被排除，脚本会恢复完整候选集。
5. 只替换语义令牌对应的颜色值，不调整文本、链接、图片位置和内容层级。

## 使用示例

```powershell
python scripts/select_palette.py --title "文章标题"
python scripts/select_palette.py --title "下一篇文章" --avoid olive-gold
python scripts/select_palette.py --palette ocean-copper
python scripts/select_palette.py --list
```
