# 控件样式覆盖

## 适用场景

当表单使用代码模块样式时，模块需要自行提供完整视觉样式。此时不能只写表单外壳、文本框和按钮样式，而应覆盖所有支持字段类型的控件外观、交互状态、错误状态和移动端表现。

系统预设样式可直接使用目标环境已有 preset；只有代码模块样式才需要按本文件补齐样式覆盖。

## preset class

代码模块样式优先复用 preset class，这样 `$[变量.body] + $[变量.script]` 和自定义样式可以保持同一套行为。

至少覆盖：

- `.gw-fit-form-dom`
- `.gw-fit-form-field`
- `.gw-fit-form-field-shell`
- `.gw-fit-form-field-content`
- `.gw-fit-form-label`
- `.gw-fit-form-required`
- `.gw-fit-form-control-wrap`
- `.gw-fit-form-control`
- `.gw-fit-form-button`
- `.gw-fit-form-actions`
- `.gw-fit-form-captcha`
- `.gw-fit-form-options`
- `.gw-fit-form-option`
- `.gw-fit-form-select-wrap`
- `.gw-fit-form-upload`
- `.gw-fit-form-address`
- `.gw-fit-form-cascader`

## 通用样式状态

每个可输入控件至少覆盖：

- 默认状态
- hover 状态
- focus / focus-visible 状态
- disabled / readonly 状态
- 错误状态
- 必填标记
- placeholder
- help / description 文案
- loading / submitting 状态
- 移动端单列和触控尺寸

通用字段结构应包含：

- 字段容器
- 标签区
- 控件区
- 辅助说明区

当前 runtime 的字段错误文案统一通过 `Utils.Toast` 展示，DOM 中通常只写状态属性：

```html
<div class="gw-fit-form-field is-error" data-gw-fit-form-error="请先填写正确的手机号">
  <input class="gw-fit-form-control is-error" aria-invalid="true" data-gw-fit-field-error="1">
</div>
```

样式应消费 `.is-error`、`[aria-invalid="true"]`、`[data-gw-fit-field-error="1"]`，不要依赖 runtime 自动插入错误文案节点。

## 类型样式清单

| 类型 | 样式要求 |
| --- | --- |
| `text` / `email` / `phone` / `idcard` / `password` | 统一 input 高度、边框、圆角、背景、聚焦环、错误边框、禁用态。 |
| `textarea` | 覆盖最小高度、行高、resize 策略、滚动条、错误态。 |
| `number` | 覆盖数字输入宽度、浏览器默认 spinner 兼容、错误态。 |
| `counter` | 覆盖减号按钮、加号按钮、数字输入、按钮禁用态、组合边框。 |
| `captcha` | 覆盖输入框和验证码按钮组合、`.is-counting` 倒计时态、`.is-loading` 发送中态、禁用态。 |
| `description` | 覆盖说明块背景、边框、文字层级、长文本换行。 |
| `select` | 覆盖下拉高度、箭头、占位色、禁用态、错误态。 |
| `cascader` | 覆盖多级选择布局、层级间距、空选项态。 |
| `address` | 覆盖省市区选择布局、详细地址输入、移动端堆叠。 |
| `radio` | 覆盖单选圆点、选中态、禁用态、横向/纵向间距。 |
| `checkbox` | 覆盖复选框、选中态、半选态、禁用态、选项换行。 |
| `switch` | 覆盖轨道、圆点、开关动画、开启/关闭文本、禁用态。 |
| `slider` | 覆盖轨道、已选进度、滑块、数值展示、禁用态。 |
| `time` / `date` | 覆盖原生输入高度、图标空间、聚焦态、移动端宽度。 |
| `timeRange` / `dateRange` | 覆盖两个输入的组合布局、分隔符、移动端堆叠。 |
| `rate` | 覆盖星级大小、间距、选中态、hover 态、只读/禁用态。 |
| `color` | 覆盖颜色预览、触发按钮、颜色值文本、透明背景格、面板触发态。 |
| `upload` | 覆盖上传按钮、文件卡片、图片预览、删除按钮、上传中、失败态。 |

## 控件样式与运行时边界

- 样式只负责视觉，不应改变字段值格式。
- 控件行为优先复用已有运行时，例如颜色面板、地址联动、上传状态、滑块进度和计数器步进。
- 若运行时会写入类名或状态属性，样式应消费这些状态，而不是另写一套行为逻辑。
- 不要为了样式覆盖重新实现提交、校验或字段取值。

## 视觉一致性

代码模块样式应通过模块级 CSS 变量维护视觉系统：

```css
.xxFormModule {
  --form-text: #111827;
  --form-muted: #6b7280;
  --form-border: #d1d5db;
  --form-focus: #2563eb;
  --form-danger: #dc2626;
  --form-radius: 8px;
  --form-control-height: 42px;
}
```

所有控件应共享：

- 字体
- 控件高度
- 边框颜色
- 圆角
- 聚焦环
- 错误色
- 间距节奏

避免每种控件各自定义一套无关颜色、圆角和阴影。

## 移动端

移动端必须检查：

- 字段是否单列展示。
- label 与控件是否不重叠。
- range、upload、captcha、address、dateRange 等复合控件是否可点击。
- 按钮文字是否不溢出。
- 上传图片预览和文件卡片是否不撑破容器。
