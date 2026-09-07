---
name: ltd-bottom-nav-builder
description: 创建、改造、审查或排查 LTD 建站平台页脚/底部导航代码模块。适用于 Footer 栏目、页脚链接区、底部链接、多列分组、移动端折叠、/api/navCat position 2、navList、响应式、多语言、多实例、安全链接和旧版 Safari/Chromium/WebView 兼容任务；不用于顶部 Header 或移动端固定 Tab。
---

# LTD 页脚/底部导航组件规范

## 任务边界

- 处理站点 Footer 中的栏目分组、页脚链接区和底部导航链接。
- 不处理顶部 Header、主菜单、搜索、吸顶或透明首屏；这些任务使用 `ltd-top-nav-builder`。
- “移动端底部固定 Tab”不是本 Skill 的默认 bottom-nav。只有用户明确要求时才作为独立固定组件设计。
- 改造或排查任务先读取现有页脚结构，保留已有品牌、版权、联系方式和布局，只调整导航相关部分。

## 执行流程

1. 确认页脚导航的数据源、分组层级、移动端折叠方式和交付文件。
2. 完整读取 [`navigation.md`](navigation.md) 和 [`references/bottom-nav.md`](references/bottom-nav.md)。
3. 检查真实模块容器、现有 Footer 结构、配置变量和样式作用域；禁止修改 `.merge.html`。
4. 使用原生 CSS 实现分组渲染、递归链接、移动端折叠和失败降级。
5. 在浏览器或 LTD 编辑器中完成纯前端验收，并说明未实测场景。

## 前端硬规则

本 Skill 只设计 HTML、原生 CSS 和 JavaScript 前端产物。不要引入 Python、后端服务、数据库或与页脚导航无关的工程设施。

### 样式与实例隔离

```html
<style data-nav-initial>原生初始 CSS</style>
<style data-nav-styles>原生业务 CSS</style>
<!-- HTML -->
<script>JavaScript</script>
```

- 两个样式块都只写浏览器可直接执行的标准 CSS，不使用 Less、Sass 或运行时样式编译器。
- 初始 CSS 至少负责根节点基础背景、链接区布局、分组可见状态和移动端折叠初态。
- 顶层类名使用 `bottomNav + 时间戳`，如 `.bottomNav20260716`；子级统一使用 `.footer-*`。
- 所有样式限制在当前根节点内；不要给 `body` 写全局 `padding-bottom`，页脚链接区保持正常文档流。
- 使用 `document.currentScript` 定位实例，查询限制在当前模块；不使用固定 id 或 `getElementById` 绑定实例。
- 使用成熟 ES6、箭头函数和模板字面量；未确认环境时避免可选链、空值合并、`async/await`、对象展开等更高版本能力。

### 数据与安全

- 默认调用 `/api/navCat`，固定传 `position: 2`，以 `code === 0` 判断成功。
- 携带 `website_id: localStorage.getItem("websiteId")` 和当前 `language_type`。
- 明确要求后台维护时使用 `$[nav_list]`，并兼容 API 与配置两套字段。
- 每一级递归过滤 `hidden/status`，使用 DOM API、`textContent` 和属性赋值安全渲染。
- 拦截配置中的 `javascript:`、`data:`、`vbscript:`；新窗口链接补 `rel="noopener noreferrer"`。
- 请求失败、空数据或配置解析失败时保留页脚结构、品牌和 fallback，不隐藏整个 Footer。

### 默认能力

- PC 端使用多列分组，支持二级或多级链接。
- 移动端切换为单列或可折叠分组，标题使用 `<button>` 并同步 `aria-expanded`。
- 只折叠链接区，不删除链接 DOM；可默认展开当前页所在分组。
- 支持当前页高亮、`remark` 辅助文案、多态图标和多语言。
- 避免 `replaceChildren()`、`:scope` 等旧浏览器兼容风险；增强能力缺失时保留基本链接访问。

### 配置交付

- 新建模块默认同步交付完整 HTML 和可直接导入的配置 JSON。
- 可从同目录 [`底部导航配置.json`](底部导航配置.json) 复制基线，再按实际占位符增删。
- `nav_list` 使用 `input_type: "navList"`；`i18n` 使用 `key/input_type: "i18n"`。
- 每项包含 `key/label/value/default_value/input_type`，根 key 唯一且与 HTML 占位符一一对应。
- `nav_list`、`i18n` 的配置字符串必须能再次 `JSON.parse`；运行时解析失败只回退该项。

## 前端验收

- 确认页面无需样式编译即可显示根节点、基础背景、分组布局和移动端折叠初态。
- 检查 PC 多列、移动端单列/折叠、二级与多级链接、当前页和键盘操作。
- 使用至少两个实例检查折叠状态、事件和动态属性互不干扰。
- 模拟 API 成功、空数据、失败和 `navList` 解析失败。
- 检查递归隐藏、图标、`remark`、危险协议、`target` 和 `rel`。
- 确认没有顶部导航专属的 sticky、搜索、汉堡侧滑、“更多”菜单或宿主高度归零逻辑。
- 检查完整配置 JSON、占位符一致性和内嵌 JSON。
- 无法运行目标浏览器或 LTD 编辑器时明确说明，不把代码阅读称为实机测试。
