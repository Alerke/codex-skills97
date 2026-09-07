# Banner 配置规范

## 配置档位选择

- **18 项平台基线**：适合已有模块修复、极简 Banner、文案完全来自列表字段的情况。
- **32 项标准三张增强档**：新建三张营销/品牌 Banner 的默认档位，包含三张独立文案、统一 CTA、悬浮色和分段指示器颜色。
- **逐张 CTA 高级档**：只有参考设计或用户明确要求每张按钮颜色/渐变不同才增加；不要把所有高级变量强制塞进普通 Banner。
- 用户指定张数不是三张时，不得假装 32 项能覆盖全部内容。列表字段可编辑则使用列表字段；否则先确认最大张数再扩展独立变量。

## 18 项平台基线

| key | input_type | 默认值 | 说明 |
| --- | --- | --- | --- |
| `media_type` | `text` | `image` | 图片或视频模式 |
| `slides` | `imageList` | 三条示例或 `[]` | 图片列表 |
| `video_slides` | `videoList` | `[]` | 视频、封面与播放设置 |
| `autoplay` | `switch` | `1` | 自动轮播 |
| `autoplay_delay` | `number` | `6000` | 轮播间隔，毫秒 |
| `title_font_size` | `number` | `48` | 标题字号 |
| `subtitle_font_size` | `number` | `16` | 副标题字号 |
| `title_font_weight` | `number` | `500` | 标题字重 |
| `text_color` | `color` | `#ffffff` | 标题颜色 |
| `subtitle_color` | `color` | `#ffffff` | 副标题颜色 |
| `overlay_opacity` | `number` | `0.55` | 渐变遮罩透明度 |
| `content_bottom` | `number` | `80` | PC 内容距底 |
| `content_left` | `number` | `60` | PC 内容距左 |
| `mobile_ratio_mode` | `switch` | `0` | 移动端比例模式 |
| `mobile_aspect_ratio` | `text` | `4/5` | 移动端比例 |
| `pc_ratio_mode` | `switch` | `1` | PC 比例模式 |
| `pc_aspect_ratio` | `text` | `21/9` | PC 比例，避免过高 |
| `show_overlay` | `switch` | `1` | 显示遮罩 |

现有基线示例见 Skill 根目录 [`../Banner配置.json`](../Banner配置.json)。它是历史 18 项模板；新建标准三张 Banner 优先复用 [`../Banner增强配置.json`](../Banner增强配置.json)，并根据设计替换文案、颜色和已获授权的媒体。增强模板故意把 `slides` 留空以避免夹带第三方图片；实际交付可见 Banner 时必须填入用户素材、明确许可素材或生成素材，并记录素材状态。

## 14 项标准扩展：总计 32 项

| key | input_type | 建议默认值 | 说明 |
| --- | --- | --- | --- |
| `slide_1_title` | `text` | 中文主标题 1 | 第一张主标题 |
| `slide_1_subtitle` | `text` | 中文副标题 1 | 第一张副标题 |
| `slide_2_title` | `text` | 中文主标题 2 | 第二张主标题 |
| `slide_2_subtitle` | `text` | 中文副标题 2 | 第二张副标题 |
| `slide_3_title` | `text` | 中文主标题 3 | 第三张主标题 |
| `slide_3_subtitle` | `text` | 中文副标题 3 | 第三张副标题 |
| `button_text` | `text` | `立即探索` | 所有 slide 的 CTA 文案 |
| `button_link` | `jump` | `none` 对象 | CTA 跳转 |
| `button_background_color` | `color` | `#ffffff` | CTA 常态背景 |
| `button_text_color` | `color` | `#1a1a1a` | CTA 常态文字 |
| `button_hover_background_color` | `color` | `#1a1a1a` | CTA 悬浮/焦点背景 |
| `button_hover_text_color` | `color` | `#ffffff` | CTA 悬浮/焦点文字 |
| `indicator_color` | `color` | `rgba` 不一定被 color 控件支持，优先十六进制 | 分段线基础色 |
| `indicator_active_color` | `color` | `#ffffff` | 活动段填充色 |

每项必须包含：

```json
{
  "key": "button_text",
  "label": "按钮文字",
  "value": "立即探索",
  "default_value": "立即探索",
  "input_type": "text"
}
```

`button_link` 的 value/default_value 使用平台 jump 对象；若当前平台导出结构已知，沿用真实结构，不自行发明字段。常见形态：

```json
{
  "type": "none",
  "href": "",
  "target": "_self"
}
```

## 占位符与 jump 注入

18 项基线使用对应根占位符。标准增强再加入六个独立文案和七个普通 CTA/颜色占位符；`button_link` 必须拆成嵌套属性：

```text
$[slide_1_title] ... $[slide_3_subtitle]
$[button_text]
$[button_link.type]
$[button_link.href]
$[button_link.target]
$[button_background_color]
$[button_text_color]
$[button_hover_background_color]
$[button_hover_text_color]
$[indicator_color]
$[indicator_active_color]
```

禁止：

```js
const buttonLink = $[button_link];
```

允许：

```html
<section
  data-button-link-type="$[button_link.type]"
  data-button-link-href="$[button_link.href]"
  data-button-link-target="$[button_link.target]">
</section>
```

验证器提取占位符 key 时应把 `button_link.type/href/target` 归并为 `button_link`。正确的 32 项配置会有 34 个嵌套/普通占位符文本出现，但仍只有 32 个根 key。

## 逐张 CTA 高级档

当设计要求每张按钮独立文案、跳转、颜色或流体描边渐变时，以 `N` 为 1..已确认最大张数，按需增加：

```text
slide_N_button_text
slide_N_button_link
slide_N_button_background_start
slide_N_button_background_end
slide_N_button_text_color
slide_N_button_border_start
slide_N_button_border_end
slide_N_button_hover_background_start
slide_N_button_hover_background_end
slide_N_button_hover_text_color
slide_N_button_hover_border_start
slide_N_button_hover_border_end
```

可再加全局 `button_gradient_angle`、`button_border_width`、`button_flow_duration`、`button_hover_scale`、`button_hover_lift`。规则：

- 逐张变量为空或非法时回退全局 CTA 变量。
- jump 仍必须用 `slide_N_button_link.type/href/target` 属性注入，不能直接插进 JavaScript。
- 动态流体描边只使用 CSS 渐变、背景位置或伪元素；减弱动效时停止流动，悬浮/焦点状态仍可辨识。
- 颜色、角度、边框、时长、缩放和位移都要限制范围。
- 变量数量会明显增加，交付时报告实际总数，不能继续宣称是 32 项。

## 读取与校验

```js
const readSwitch = (value, fallback) => {
  if (value === true || value === 1 || value === '1' || value === 'true') return true;
  if (value === false || value === 0 || value === '0' || value === 'false') return false;
  return fallback;
};

const readNumber = (value, fallback, min, max) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return fallback;
  return Math.min(max, Math.max(min, number));
};

const readEnum = (value, allowed, fallback) => {
  const text = String(value == null ? '' : value).trim();
  return allowed.indexOf(text) >= 0 ? text : fallback;
};
```

建议范围：delay 1500–20000；标题 16–120；副标题 10–60；字重 100–900；遮罩 0–1；偏移 0–1000。`0` 是遮罩和偏移的有效值。

颜色先去空格，再通过 `CSS.supports('color', value)` 或严格白名单验证。比例解析后统一输出 `width / height`。`title_font_weight` 使用 `number` 并限制 100–900，不自行发明未知 select options。

## 导入与更新保护

- `slides` 和 `video_slides` 的 `value/default_value` 必须是合法 JSON 数组字符串，不是直接数组对象。
- 不得把参考网站的品牌图片、Logo 或字体文件直接复制到列表默认值；参考站仅用于视觉分析。
- 新建模块先保存 HTML，再导入 JSON；已有模块只修改 HTML 时，不要无必要重导配置。
- 重导 JSON 前提醒导出/备份当前配置，因为导入可能覆盖已经上传的 Banner 图片和用户修改过的文案。
- 导入后检查变量面板中 input_type 是否正确：图片列表应显示媒体列表，jump 应显示跳转控件，color 应显示颜色控件。
- 保存模块、保存页面、发布是不同状态；必须分别验证，不能把编辑器即时画面当作发布结果。

## 配置验收

- JSON 可解析，所有 key 唯一。
- 每项五个必需字段齐全，value/default_value 类型与 input_type 兼容。
- HTML 占位符根 key 与 JSON key 双向匹配；嵌套 jump 正确归并。
- 没有未解析占位符、旧 key、直接 `$[button_link]` JavaScript 注入或发布后 `return #...`。
- 标准三张增强档实际为 32 项；高级档报告真实总数。
