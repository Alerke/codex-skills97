---
name: ltd-top-nav-builder
description: 创建、重构、审查或排查 LTD 建站平台顶部导航代码模块。适用于 Header、主菜单、navList、多级下拉、移动端汉堡菜单、搜索、登录、语言切换、吸顶与滚动态、/api/navCat、可导入配置 JSON、多实例、编辑器适配和旧版 Safari/Chromium/WebView 兼容任务。
---

# LTD 顶部导航 Skill

## 边界

- 只处理页面顶部 Header、主导航及其下拉、搜索、登录、语言、联系方式、吸顶和移动端菜单。
- 页脚链接区使用独立的底部导航 Skill。
- 移动端底部固定 Tab 不属于本 Skill。
- 创建任务默认交付完整模块 HTML 和可直接导入 LTD 的 26 项 JSON。
- 只有用户明确说“只要代码”或“不要 JSON”时才省略 JSON。

## 必读顺序

开始实现前完整读取：

1. [`references/platform.md`](references/platform.md)：LTD 宿主、原生 CSS、响应式、多实例和旧浏览器。
2. [`references/data.md`](references/data.md)：`/api/navCat`、`navList`、递归字段和安全渲染。
3. [`references/config.md`](references/config.md)：固定 26 项配置和可导入 JSON。
4. [`references/module-spec.md`](references/module-spec.md)：默认功能、交互、sticky 和验收。
5. [`references/navigation-example-20260728.md`](references/navigation-example-20260728.md)：新版真实导航示例中提取的数据与交互边界。

创建完整模块时以以下文件为实现基线：

- [`references/sample-module/top-nav-sample.html`](references/sample-module/top-nav-sample.html)
- [`references/sample-module/top-nav-sample.config.json`](references/sample-module/top-nav-sample.config.json)

发生冲突时按以下优先级处理：

`SKILL.md` → `platform.md` → `data.md` → `config.md` → `module-spec.md` → 示例文件。

## 输出合同

导航模块代码固定使用：

```html
<style data-nav-initial>原生首屏 CSS</style>
<style data-nav-styles>原生业务 CSS</style>
<!-- HTML -->
<script>JavaScript</script>
```

随后同步交付完整 JSON 数组：

- 顶层为数组。
- 包含全部 26 个唯一 key。
- 每项包含 `key`、`label`、`value`、`default_value`、`input_type`。
- 不使用注释、省略号、字段表或伪代码代替真实 JSON。
- `nav`、`language_nav`、`logo_link`、`search_link`、`i18n` 内嵌字符串可再次 `JSON.parse`。

## 硬规则

### 样式

- 初始状态和业务样式都使用标准 CSS，不使用样式预处理器或运行时编译器。
- 根类使用 `.topNavYYYYMMDD`，子级使用 `.nav-*`。
- 所有业务选择器从当前根类开始。
- 平台规则从真实模块名称 `.gw-browse-module[name="顶部导航"]` 或 `.gw-browse-module.top-nav-host-YYYYMMDD` 开始。
- 不裸写 `html`、`body`、`:root`、标签选择器、`.nav-*` 或平台通用类。
- 默认断点为 `1024px`；PC 端使用 `display:none !important` 隐藏移动端结构。

### 平台与实例

- 用 `document.currentScript` 定位实例。
- 普通 DOM 查询限制在当前容器。
- 给当前平台模块注入 `.top-nav-host-YYYYMMDD`。
- 只有吸顶状态允许给宿主添加 `.top-nav-host-floating` 并归零 `.code-html-content`。
- 编辑器始终保留可选中的真实高度。
- 不依赖 `:has()`、`:scope`、`replaceChildren()` 或固定 id。

### 数据

- 默认接口为 `/api/navCat`。
- 固定传 `position: 1`，成功码为 `code === 0`。
- 携带 `website_id: localStorage.getItem("websiteId")` 和当前 `language_type`。
- 后台维护时使用 `$[nav]`，对应 `input_type: "navList"`。
- 每一级递归过滤 `hidden/status`。
- 名称、备注和图标使用 DOM 属性安全渲染。
- 拦截 `javascript:`、`data:`、`vbscript:`；空链接兜底除外。
- `_blank` 链接补 `rel="noopener noreferrer"`。

### 配置

只使用以下 26 个 key：

`nav`、`use_custom_language_jump`、`language_nav`、`logo`、`stickyLogo`、`logo_link`、`phone`、`email`、`address`、`sticky_mode`、`sticky_scroll_distance`、`theme_color`、`nav_background_color`、`nav_blur`、`nav_text_color`、`i18n`、`show_search`、`search_link`、`show_login`、`sticky_nav_background_color`、`sticky_nav_text_color`、`logo_height_percent`、`company_name`、`company_name_color`、`sticky_company_name_color`、`mobile_menu_company_name_color`。

HTML 不得引用 JSON 中不存在的 key。修改任一 key 时同步修改 `references/sample-module/` 中的示例 HTML 和示例 JSON。

### 默认功能

- PC 和移动端两套结构。
- PC 二级/三级下拉，移动端递归手风琴。
- 当前页与祖先高亮。
- 搜索、登录、语言和联系方式。
- `use_custom_language_jump = 1` 时递归过滤 `language_nav` 的隐藏节点并使用其跳转；关闭时才请求平台语言列表。
- `sticky_mode` 控制是否吸顶。
- `sticky_scroll_distance` 控制滚动态 Logo 和颜色切换。
- 浮层打开时锁定背景滚动，关闭、Escape 或切回 PC 时恢复。

默认不实现超长导航自动收缩、“更多”菜单、宽度测量或菜单 clone。只有用户明确要求或页面已经真实溢出时才增加。

## 工作流

1. 检查现有模块、真实模块名称和数据来源。
2. 确定时间戳根类和宿主类。
3. 先完成 `data-nav-initial`。
4. 完成业务 CSS、PC/移动端 HTML 和配置解析。
5. 实现安全递归渲染、多实例、搜索、登录、语言、sticky 和移动端交互。
6. 同步生成完整 26 项 JSON。
7. 验证脚本语法、占位符与 JSON 一致性、嵌套 JSON、CSS 作用域和本地引用。
8. 能实测时在 LTD 前台和编辑器检查；无法实测时明确说明。

## 禁止

- 不修改自动生成的 `.merge.html`。
- 不引入与顶部导航无关的后端、数据库或工程设施。
- 不手动重复引入平台已有的 jQuery、Vue、Swiper。
- 不复制旧接口 `/api/website/navigation` 或 `code === 1` 写法。
- 不默认加载 GSAP、整套 polyfill、搜索历史、热门词或 mega menu。
- 不把 API 失败处理为隐藏整个导航。
- 不生成只有 PC 或只有移动端的半成品，除非用户明确要求极简。

## 最终验收

- [ ] HTML 与完整 26 项 JSON 同时交付。
- [ ] 页面无需样式编译即可正确显示。
- [ ] PC、移动端、多级菜单、搜索、登录、语言和 sticky 正常。
- [ ] 平台高度、编辑器状态和旧浏览器 fallback 正确。
- [ ] 两个实例的事件、状态和动态 id 互不影响。
- [ ] API、配置解析或增强能力失败时保留基础导航。
- [ ] 默认产物不包含超长导航自动收缩逻辑。
