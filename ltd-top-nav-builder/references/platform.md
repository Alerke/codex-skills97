# LTD 顶部导航平台与兼容规范

本文件定义顶部导航在 LTD 前台、编辑器和旧版 Safari/Chromium/WebView 中必须成立的平台规则。

## 输出结构

导航模块固定按以下顺序输出：

```html
<style data-nav-initial>首屏关键原生 CSS</style>
<style data-nav-styles>完整业务原生 CSS</style>
<!-- HTML -->
<script>JavaScript</script>
```

- 两个样式块都使用浏览器可直接解析的标准 CSS。
- 不使用样式预处理器、运行时样式编译器或与导航无关的工程依赖。
- `data-nav-initial` 必须独立保证宿主高度、基础背景、PC/移动端初始显隐和浮层关闭态。

## 命名与作用域

- 根类使用 `topNav + YYYYMMDD`，例如 `.topNav20260716`。
- 子级类使用 `.nav-*`。
- 平台宿主类使用 `.top-nav-host-YYYYMMDD`。
- 所有业务选择器从 `.topNavYYYYMMDD` 开始。
- 平台选择器只能从真实模块名称或时间戳宿主类开始：

```css
.gw-browse-module[name="顶部导航"],
.gw-browse-module.top-nav-host-20260716 {
  overflow: visible !important;
}
```

禁止顶层裸写 `html`、`body`、`:root`、标签选择器、`.nav-*`、`.gw-browse-module`、`.container`、`.wrapper`、`.content`。

## 宿主高度与吸顶

```css
.gw-browse-module[name="顶部导航"],
.gw-browse-module.top-nav-host-20260716 {
  --nav-h: 72px;
  height: auto !important;
  overflow: visible !important;
  position: relative;
  z-index: 9999 !important;
}

.gw-browse-module[name="顶部导航"] .code-html-content,
.gw-browse-module.top-nav-host-20260716 .code-html-content {
  height: var(--nav-h, 72px) !important;
  min-height: var(--nav-h, 72px) !important;
}

.gw-browse-module.top-nav-host-20260716.top-nav-host-floating .code-html-content,
.gw-browse-module[name="顶部导航"].top-nav-host-floating .code-html-content {
  height: 0 !important;
  min-height: 0 !important;
}

.gw-browse-module.top-nav-host-20260716.top-nav-host-floating,
.gw-browse-module[name="顶部导航"].top-nav-host-floating {
  height: var(--nav-h, 72px) !important;
  position: relative;
  position: -webkit-sticky;
  position: sticky;
  top: var(--nav-sticky-top-offset, 0px);
  z-index: 10000 !important;
}

.gw-browse-module[name="顶部导航"].code-component.gw-editor-component .code-html-content,
.gw-browse-module.code-component.gw-editor-component.top-nav-host-20260716 .code-html-content {
  height: var(--nav-h, 72px) !important;
  min-height: var(--nav-h, 72px) !important;
}
```

- 只有 `sticky_mode` 开启时添加 `.nav-floating` 和 `.top-nav-host-floating`。
- `sticky_mode` 关闭时使用 `.nav-static`，不得归零 `.code-html-content`。
- 编辑器始终保留真实高度，避免模块无法选中。
- 平台父级必须允许下拉菜单和移动端浮层溢出显示。

## 响应式

默认断点：

```text
移动端：max-width: 1024px
PC：min-width: 1025px
```

PC 端必须真实隐藏全部移动端结构：

```css
@media (min-width: 1025px) {
  .topNav20260716 .nav-header-mb,
  .topNav20260716 .nav-mb-menu,
  .topNav20260716 .nav-mb-backdrop,
  .topNav20260716 .nav-mb-search-panel,
  .topNav20260716 .nav-mb-search-backdrop {
    display: none !important;
  }
}
```

不能用屏幕外位移、负 `left`、透明度或 `visibility:hidden` 代替 `display:none`。

## 多实例定位

使用 `document.currentScript` 定位当前实例；普通查询限制在当前容器：

```javascript
const matchesElement = (element, selector) => {
  if (!element || element.nodeType !== 1) return false;
  const matches =
    element.matches ||
    element.webkitMatchesSelector ||
    element.msMatchesSelector;
  return matches ? matches.call(element, selector) : false;
};

const closestElement = (element, selector) => {
  let current =
    element && element.nodeType === 1
      ? element
      : element && element.parentElement;
  while (current) {
    if (matchesElement(current, selector)) return current;
    current = current.parentElement;
  }
  return null;
};

const qs = (selector) => container.querySelector(selector);
const qsa = (selector) => container.querySelectorAll(selector);
```

- 不使用固定 id 或 `getElementById` 绑定实例。
- 全局查询只用于寻找当前脚本对应容器、平台宿主和编辑器顶部提示。
- 搜索历史 key、`aria-controls` 和动态 id 必须带实例标识。

## 旧浏览器降级

- 不依赖 `:has()`、`:scope`、`replaceChildren()`。
- 清空节点使用 `removeChild` 循环。
- sticky 同时写 `-webkit-sticky` 和标准声明。
- `backdrop-filter` 同时写前缀，并用 `CSS.supports` 检测；不支持时将模糊值降为 `0`。
- `ResizeObserver`、`MutationObserver`、`document.fonts` 使用前检查能力。
- 新 CSS 值前提供基础 fallback，例如先写 `width:320px`，再写 `width:min(320px, 80vw)`。
- 不承诺 IE 或纯 ES5 环境，不默认加载整套 polyfill。

## 检查清单

- [ ] 初始 CSS 无需 JavaScript 或编译即可保证正确首屏。
- [ ] 业务选择器和平台选择器作用域正确。
- [ ] 编辑器有真实高度，前台吸顶状态才允许内容区归零。
- [ ] PC 端移动端结构使用 `display:none !important`。
- [ ] 两个实例的事件、状态和动态 id 互不影响。
- [ ] 缺少增强 API 时导航仍可见、可点击和可展开。
