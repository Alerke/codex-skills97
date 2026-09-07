# 产品列表点击操作样式

本规范只处理产品/商品卡片和点击触发器的结构及视觉反馈。点击类型与点号字段见 [`click-action-type.md`](click-action-type.md)，模块跳转、表单与弹窗运行时见 [`click-action-runtime.md`](click-action-runtime.md)。

## 1. 卡片结构选择

### 整卡只有一个详情操作

可使用整卡 `<a>`，但卡片内不得再出现 `<a>` 或 `<button>`。标题、图片和辅助信息全部位于该锚点内。

### 卡片内还有独立操作

使用 `<article>` 作为卡片，在卡片上保存主操作属性，并用明确的详情链接或局部事件委托处理主操作。以下元素不得触发整卡主操作：

```text
a, button, input, select, textarea, label, [data-no-card-jump]
```

不要用透明绝对定位链接覆盖整张卡片，这会遮挡内部按钮、文本选择和辅助技术焦点顺序。

## 2. 状态命名

- 有效操作：添加 `.is-clickable`。
- 当前按下或选择：按设计使用 `.is-active`，不能与分页或筛选状态混淆。
- 禁止操作：使用原生 `disabled` 或 `.is-disabled`，并同步 `aria-disabled="true"`。
- `data-gw-jump-type="none"`、空地址或危险地址：不要添加 `.is-clickable`。

只有有效操作才显示手型、hover、focus 和 active 反馈。

## 3. 当前模块内的基础样式

```css
.productList20260722 .pl-card.is-clickable {
  cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.productList20260722 .pl-card.is-clickable:hover {
  transform: translateY(-2px);
  border-color: var(--pl-theme);
  box-shadow: 0 12px 30px rgba(15, 23, 42, .10);
}

.productList20260722 .pl-card.is-clickable:active {
  transform: translateY(0);
}

.productList20260722 .pl-card-link:focus-visible,
.productList20260722 .pl-card.is-clickable:focus-visible {
  outline: 2px solid var(--pl-theme);
  outline-offset: 3px;
}

.productList20260722 .pl-card.is-disabled,
.productList20260722 .pl-card[aria-disabled="true"] {
  cursor: default;
  transform: none;
  box-shadow: none;
}

@media (prefers-reduced-motion: reduce) {
  .productList20260722 .pl-card.is-clickable {
    transition: none;
  }
}
```

视觉参数必须服从用户设计；示例只规定状态层级。

## 4. 样式约束

- hover 不改变卡片尺寸，不导致网格重排。
- 键盘 focus 与鼠标 hover 同等清晰。
- active 反馈短促，不使用大幅缩放。
- 禁用或无操作状态移除 pointer、位移和阴影反馈。
- 触屏设备不依赖 hover 传达关键信息。
- `color-mix()`、`backdrop-filter` 等新能力只能作为增强，必须保留普通颜色或不透明背景 fallback。
- 所有卡片状态样式从当前 `.productListYYYYMMDD` 根类开始，不写全局 `.is-clickable`。

## 5. 平台弹窗视觉参考

LTD 点击运行时的视觉基线：

- 遮罩：黑色约 50% 透明度；玻璃模式约 25% 并使用约 `12px` blur。
- 对话框：白色背景、约 `12px` 圆角、多层轻阴影、最大约 `95vw × 92vh`。
- 打开动画：约 `0.2–0.25s` 淡入与 `scale(.96 → 1)`。
- 关闭按钮：约 `32–34px` 圆形白色按钮，hover 轻微放大。
- 内容区：独立滚动，二维码、页面 iframe 和表单由平台运行时按类型适配。

这些值用于对齐平台视觉，不要求产品列表重新注入 `.gw-dialog-*`。只有脱离 LTD 的独立预览明确需要模拟时，才在预览作用域内复刻。

## 6. 样式验收

- Tab 焦点清晰，Enter/Space 行为与元素语义一致。
- hover、active、disabled 和无操作状态可以区分。
- 卡片内部按钮不会被整卡覆盖或遮挡。
- 320px 触屏环境不依赖 hover，点击区域尺寸合理。
- `prefers-reduced-motion` 下无非必要位移动画。
- LTD 全局弹窗样式未被模块样式覆盖。
