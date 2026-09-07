---
name: ltd-code-module-builder
description: 创建、重构、审查或排查 LTD 建站平台的通用前端代码模块。适用于文本、图片、按钮、图标、背景层、分割线、富文本、视频、地图、搜索、滚动公告、跑马灯、悬浮组件、静态内容区、媒体展示和尚未形成独立领域 Skill 的代码模块，以及变量配置 JSON、DOM 隔离、多实例、点击操作、多语言、接口请求和旧版 Safari/Chromium/WebView 兼容；导航、表单、Banner 和内容列表应优先路由到对应独立 Skill。
---

# LTD 通用代码模块

## 边界与路由

- 处理没有独立领域 Skill 的纯前端代码模块。
- 顶部/底部导航、表单、Banner、文章、案例、产品商品和自定义内容列表优先使用对应独立 Skill。
- 文本、图片、按钮、图标、背景层、分割线、富文本、视频、地图、搜索、滚动公告、跑马灯和悬浮组件可直接使用本 Skill。
- 数据查询、属性搜索、门店筛选等接口型模块先检查真实接口和响应；没有证据时不猜字段、URL 或业务规则。
- 只生成 HTML、原生 CSS 和 JavaScript，不创建 Python、后端、数据库或构建工程。

## 必读参考

按任务读取：

1. [`references/platform-runtime.md`](references/platform-runtime.md)：宿主、原生 CSS、多实例、成熟 ES6 和请求边界。
2. [`references/module-routing.md`](references/module-routing.md)：编辑器模块类型与领域 Skill 路由。
3. [`references/config-controls.md`](references/config-controls.md)：新编辑器配置控件、点号语法和错误处理。
4. [`references/rendering-and-actions.md`](references/rendering-and-actions.md)：安全渲染、媒体、点击操作和状态。

## 输出合同

新建模块默认同时交付：

```html
<style data-module-initial>原生首屏 CSS</style>
<style data-module-styles>原生业务 CSS</style>
<!-- 当前模块 HTML -->
<script>JavaScript</script>
```

以及可直接导入的配置 JSON 数组：

- 每项包含 `key/label/value/default_value/input_type`。
- key 唯一，并与 HTML 的占位符根 key 一一对应。
- 复合控件的导入值是 JSON 字符串，必须能再次 `JSON.parse`。
- 不用注释、伪代码、省略号或字段表代替完整 JSON。
- 可从 [`通用模块基础配置.json`](通用模块基础配置.json) 选取实际使用项，不为凑数量保留无用配置。

## 硬规则

### 样式与实例

- 初始状态和业务样式均使用标准 CSS，不使用 Less、Sass 或运行时样式编译器。
- 根类使用“项目缩写 + 功能 + YYYYMMDD”，所有业务选择器从根类开始。
- 平台规则从真实 `.gw-browse-module[name="模块名称"]` 或当前实例宿主类开始。
- 不裸写 `html/body/:root`、通用标签、`.container/.wrapper/.content` 等全局规则。
- 使用 `document.currentScript` 定位当前模块实例，DOM 查询、事件、状态和请求序号限制在实例闭包内。
- 不使用固定 id、`getElementById`、全局重复绑定或修改 `.merge.html`。

### JavaScript 与兼容

- 使用普通 `<script>` 可运行的成熟 ES6：`const/let`、箭头函数、模板字面量、数组迭代、解构和默认参数。
- 多行结构优先模板字面量；动态文本、属性和 URL 必须先转义或校验。
- 未确认环境时避免可选链、空值合并、`async/await`、动态 `import()`、对象展开等更高版本能力。
- 不依赖 `:has()`、`:scope`、`replaceChildren()`、`Array.prototype.flat()`、`Object.fromEntries()`。
- 增强 API 使用前做特性检测；能力缺失时保留基础内容和链接。

### 配置与可靠性

- 所有配置独立归一化；未替换占位符、空值、错误 JSON、错误类型和越界值不得抛出未捕获异常。
- `switch` 显式识别 `"1"/1/true/"true"` 和 `"0"/0/false/"false"`，不使用 `Boolean("0")`。
- 筛选配置为空或未传时表示不增加该筛选条件，从当前数据源获取全部数据。
- 多语言使用 `key/input_type: "i18n"`，运行时 `$[i18n]` 标准输出是对象，不盲目重复解析。
- 分类使用 `input_type: "category"`，运行时用点号语法读取，不把 `$[cat]` 的 ID 字符串当完整 JSON。
- 单项配置错误只回退该项；接口失败显示局部错误/重试或保留静态 fallback，不隐藏整个宿主。

### 数据与安全

- LTD 接口优先使用页面已有 `r()`，并按接口要求携带 `website_id` 与当前语言。
- 没有真实接口证据时不创建请求；静态展示模块不需要假接口。
- 接口型模块至少实现 loading、success、empty、error 四种互斥状态，并防止旧请求覆盖新请求。
- 动态文本用 `textContent`，属性用 DOM API；富文本只有在来源可信并经过平台净化时才注入。
- 动态链接拒绝任意 `javascript:`、`data:`、`vbscript:`；平台明确的 jump 类型按平台运行时处理。
- `_blank` 补 `rel="noopener noreferrer"`。
- 图标优先使用作用域内联 SVG 和 `currentColor`；需要大量统一图标时才复用页面已有 Font Awesome。

## 工作流

1. 判断是否已有更具体的领域 Skill；有则切换，不重复实现。
2. 检查真实模块名称、现有 DOM、配置、数据源和目标浏览器。
3. 确定根类、宿主类、状态、配置 key 和安全渲染边界。
4. 完成原生初始 CSS、业务 CSS、HTML 和实例脚本。
5. 同步生成只包含实际使用项的完整配置 JSON。
6. 校验 JavaScript 语法、JSON、占位符一致性、CSS 作用域、多实例、空配置和失败降级。

## 验收

- [ ] 任务已正确路由，没有与导航、表单、Banner 或列表 Skill 重复。
- [ ] HTML 与可直接导入 JSON 同步交付。
- [ ] 页面无需样式编译即可显示。
- [ ] 配置缺失或错误不阻塞当前实例和同页其他模块。
- [ ] 动态文本、富文本、媒体 URL 和点击操作安全。
- [ ] 多实例、移动端、键盘操作和旧浏览器降级正确。
- [ ] 没有与模块无关的 Python、后端、数据库或工程内容。
