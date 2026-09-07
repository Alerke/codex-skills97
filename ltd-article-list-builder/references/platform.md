# LTD 文章列表平台约束

## 模块定位

- 用 `document.currentScript` 保存当前脚本节点，再通过 `closest()` 或相邻结构定位当前 `.gw-browse-module` 与文章列表根节点。
- 若 `closest` 不可用，提供实例内的父级遍历函数；不要污染原型。
- 所有查询从当前根节点开始，不遍历整页同名模块。
- 每个实例维护独立 state、事件解绑函数、请求序号和销毁标记。

## 样式

- 使用两个原生 CSS 块：首屏状态 CSS 与完整业务 CSS。
- 业务选择器从唯一根类 `.articleListYYYYMMDD` 开始。
- 编辑器/浏览态差异规则从真实宿主类或 `[name="真实模块名"]` 开始。
- 不修改页面根字号，不向 `html/body/:root` 写变量，不使用 Less。
- 默认检查 1024px、768px、576px；响应式只调整本模块。

## 依赖

- 优先使用页面已有 `r()` 请求封装。
- 默认使用原生 DOM；不要为了文章列表重复加载 Vue、jQuery、Swiper 或图标库。
- 只有现有模块明确依赖且页面已提供时才复用第三方库。
- 不硬编码本地代理、`tg-url`、测试站域名或用户 token。

## 浏览器

- 输出普通 `<script>` 的成熟 ES6。
- 避免无法通过局部 polyfill 修复的高版本语法。
- 用特性检测代替 user-agent 判断。
- 不依赖 `URLSearchParams` 时，可提供小型 query 解析降级；不得因 URL 同步失败阻塞列表。

## 可访问性

- 文章卡片用真实 `<article>`，有效详情地址使用真实 `<a>`。
- 搜索框必须有 label 或 `aria-label`。
- 图标按钮必须有可访问名称；装饰 SVG 使用 `aria-hidden="true"`。
- 加载区可用 `aria-live="polite"`，错误重试使用真实 `<button>`。
