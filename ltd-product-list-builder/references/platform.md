# LTD 产品列表平台规范

## 1. 宿主结构

LTD 代码会被插入 `.gw-browse-module`。模块既可能直接位于纯净模式宿主，也可能处于 `.gw-browse-module-content .gw-browse-component-content .code-html-content` 内。不要依赖固定层级向上查找业务元素。

推荐结构：

```html
<style data-product-list-initial>/* 原生 CSS */</style>
<style data-product-list-styles>/* 原生 CSS */</style>
<section class="productListYYYYMMDD" aria-busy="true">
  <!-- 工具栏、状态区、列表与分页 -->
</section>
<script>/* 当前实例逻辑 */</script>
```

初始 CSS 必须先出现，至少定义根节点、列表骨架、状态显隐和移动端基础布局，避免接口返回前出现无样式内容。

## 2. 样式作用域

- 根类：`.productListYYYYMMDD`。
- 子类：使用项目缩写或 `pl-` 前缀，例如 `.pl-card`、`.pl-state`。
- 业务样式必须以根类开头，例如 `.productList20260722 .pl-card`。
- 宿主修正规则必须以真实名称或当前实例宿主类开头，例如 `.gw-browse-module[name="产品列表"] .productList20260722` 或 `.gw-browse-module[name="商品列表"] .productList20260722`。
- 不改变页面全局字体、背景、滚动条或 `body` 溢出。
- 不使用固定的通用 id；需要 aria 关联时为当前实例生成唯一 id。

## 3. 多实例定位

```js
(() => {
  const script = document.currentScript;
  const scope = script && script.parentElement ? script.parentElement : document;
  const root = scope.querySelector('.productList20260722');
  if (!root || root.getAttribute('data-mounted') === '1') return;
  root.setAttribute('data-mounted', '1');
  // 当前实例的状态、查询和事件均从 root 开始。
})();
```

- 优先通过 `document.currentScript` 找到当前代码组件。
- 所有状态放在当前闭包或模块实例中。
- 动态内容使用根节点内的事件委托，重复初始化必须可被识别。
- 文档级事件确有需要时，在销毁或重建前解除；产品列表默认不需要全局事件。

## 4. 响应式

- PC 默认使用卡片网格；列数必须来自设计或配置，不根据内容猜测。
- `1024px` 下调整工具栏和列数，`768px` 下允许控件换行，`576px` 下保证触控按钮和分页可操作。
- 卡片图片使用稳定比例容器，避免图片加载导致布局跳动。
- 文本截断不得破坏标题的 `title`/辅助说明，也不要把关键信息仅放在 hover 中。
- 列表模式只有在用户要求或现有模块已有时实现。

## 5. 兼容性与可访问性

- JavaScript 默认必须以成熟的 ES6 核心语法编写，继续使用普通 `<script>`，不要求 `type="module"` 或构建工具。除非用户或目标环境明确要求 ES5，不得自行降级。
- 使用 `const`/`let`、箭头函数、模板字面量（template literals）、数组迭代、解构和默认参数；只有需要动态 `this`、构造函数语义或明确的兼容点时才使用普通 `function`。
- 多行静态 HTML、卡片批量模板和包含少量已处理变量的字符串必须优先使用模板字面量，不使用大量 `+` 拼接。插值前必须按上下文分别执行文本转义、属性转义或 URL 校验；不能因为使用模板字面量就把接口原始值直接写入 `innerHTML`。
- 兼容 LTD 常见旧 Safari、Chromium 与 WebView 时，不默认使用可选链 `?.`、空值合并 `??`、`async/await`、动态 `import()`、对象展开等 ES2017+ 语法。等价逻辑使用显式空值判断、Promise 链、属性赋值或局部辅助函数。
- 不依赖 `:has()`、`:scope`、`replaceChildren()`、`structuredClone()`、`Array.prototype.flat()`、`Array.prototype.flatMap()`、`Object.fromEntries()`、`String.prototype.replaceAll()` 等旧环境风险能力。
- `Element.closest`、`Object.assign`、`URL`、`URLSearchParams` 等能力若目标 WebView 不稳定，先做特性检测，再使用局部兼容函数或等价写法。
- 不用 user-agent 字符串推断语法或 API 支持，不为了少数能力引入整套 polyfill。
- ES6 语法无法通过运行时 polyfill 修复。若项目明确覆盖不能解析 ES6 的浏览器，应把整段脚本转译为 ES5，或按用户要求额外交付 ES5 版本；不要在同一脚本里零散混用两套风格并声称已兼容。
- ES5 是明确兼容目标下的例外交付，不是默认实现风格；交付说明必须标明为何降级。
- 核心列表不依赖动画；`prefers-reduced-motion` 下关闭非必要过渡。
- 搜索控件有可见或屏幕阅读器标签，按钮使用真实 `<button>`。
- 加载时设置 `aria-busy="true"`，结果数量变化可通过 `aria-live="polite"` 提示。
- 错误态和空状态必须提供可键盘操作的重试或重置按钮。

## 6. 图标与 Font Awesome

- 搜索、清空、布局切换、分页箭头、展开/收起和状态图标默认使用内联 SVG。SVG 必须提供 `viewBox`，尺寸由当前根类内 CSS 控制，`fill`/`stroke` 优先使用 `currentColor`。
- 不用 Emoji、Unicode 箭头或依赖操作系统字体的字符替代正式功能图标；它们在不同系统、浏览器和 WebView 中外观不稳定。
- 纯装饰 SVG 设置 `aria-hidden="true"` 和 `focusable="false"`。图标按钮使用真实 `<button>`，由 `aria-label` 或可见文本提供名称，不能只依赖 SVG `<title>`。
- 不把接口返回的原始 SVG 字符串直接写入 `innerHTML`。动态 SVG 只使用可信预设；接口图标 URL 按图片 URL 规则校验后用 `<img>`。
- 如果模块已有大量同风格图标，可使用 Font Awesome。先检查宿主是否已经加载兼容版本；已加载时只复用类名，不再插入 `<link>`、`<script>` 或 kit。
- 只有页面未加载、用户/项目允许外部依赖且内联 SVG 不适合时，才引入固定版本的 Font Awesome。优先使用项目已有静态地址或自托管资源；外部 CDN 必须固定版本，不能使用不锁版本的 latest 地址。
- 同一模块只使用一个 Font Awesome 版本和一套图标前缀，不混用旧 `fa`、新版 `fas/far/fab` 或不同 major 版本。加载失败时核心按钮仍保留文本或可用的内联 SVG 回退。
- 不裸写全局 `svg`、`.fa`、`.fas` 等选择器；所有尺寸、颜色、间距和 hover 状态从 `.productListYYYYMMDD` 开始限定。

## 7. 禁止

- 不使用 Less、Sass 或运行时编译器。
- 不修改 `.merge.html`。
- 不覆盖平台通用 `.row`、`.container`、`.pagination` 等类。
- 不把产品详情、购物车或登录弹窗逻辑塞入默认列表。
- 不为了视觉效果加载大型动效库。
