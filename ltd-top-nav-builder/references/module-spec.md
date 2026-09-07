# 顶部导航模块规格

## 默认能力

完整顶部导航默认包含：

- PC 顶部栏与移动端顶部栏。
- Logo、公司名、主导航、搜索、登录、语言入口。
- PC 二级/三级下拉。
- 移动端侧滑菜单和递归手风琴。
- 当前页及祖先高亮。
- 联系电话、邮箱、地址。
- `sticky_mode` 吸顶开关。
- 达到 `sticky_scroll_distance` 后切换 Logo、背景、文字和公司名颜色。

默认不实现导航项超长自动收缩、“更多”菜单、宽度测量或菜单 clone。只有用户明确要求，或现有页面真实发生溢出时才增加。

## HTML 区域

根节点内保留：

- `.nav-header-pc`
- `.nav-search-pc`
- `.nav-header-mb`
- `.nav-mb-search-backdrop`
- `.nav-mb-search-panel`
- `.nav-mb-backdrop`
- `.nav-mb-menu`

浮层优先保留在当前根节点内，以维持多实例隔离。

## PC 导航

- 顶层渲染到 `.nav-list-pc`。
- 二级使用 `.nav-dropdown`。
- 三级使用 `.nav-dropdown-third`。
- hover 和键盘 focus 都能展开。
- 有真实链接的父级保持可跳转。
- 三级菜单靠近右侧视口时向左展开。

## 移动端

- 链接负责跳转，`.nav-mb-toggle` 只负责展开。
- active 子项的祖先默认展开。
- 打开菜单或搜索时暂存并锁定 `document.body.style.overflow`。
- 关闭、Escape 或切回 PC 时恢复原值。
- 汉堡、关闭按钮、菜单和搜索面板同步 `aria-expanded`、`aria-hidden`、`aria-controls`。

## 搜索

- `show_search` 控制 PC 和移动端入口。
- 表单使用 `role="search"`，参数名使用 `keywords`。
- 跳转基于 `search_link`，保留 `_self/_blank`。
- 空输入不跳转；可以使用当前占位词作为 fallback。
- 搜索历史和热门搜索属于可选增强，不是默认必需能力。

## 登录

- `show_login` 控制入口显示。
- 可用 `localStorage.getItem("GwShopUserToken")` 判断登录状态。
- 未登录显示 i18n `loginText`，已登录显示 `loginUserName`。
- 登录页和用户中心路径是模块内部常量，不增加新的导入配置 key。

## 语言

- `i18n` 负责导航界面文案。
- `use_custom_language_jump = 1` 时使用 `language_nav` 的可见节点及其 `jump`。
- `use_custom_language_jump = 0` 时请求 `/shop/frontend/languageList`。
- 0/1 个语言时隐藏语言区；2 个语言可直接切换；3 个以上使用下拉。
- 切换前写入 `localStorage.lang`。
- 自定义语言列表为空或错误时只隐藏语言区，不得阻塞主导航初始化。

## Sticky 与视觉

- `sticky_mode = 1`：从初始状态吸顶。
- `sticky_mode = 0`：普通文档流。
- `sticky_scroll_distance` 只决定滚动态皮肤切换时机。
- 常态使用 `logo`、`nav_background_color`、`nav_text_color`、`company_name_color`。
- 滚动态使用 `stickyLogo`、`sticky_nav_background_color`、`sticky_nav_text_color`、`sticky_company_name_color`。
- 移动端弹出菜单公司名使用 `mobile_menu_company_name_color`。
- `nav_blur` 经过能力检测后写入 `backdrop-filter`。

视觉风格可调整颜色、阴影、圆角、间距、字体和布局，但不得改变数据、安全、多实例和平台高度规则。

## 初始化顺序

1. 定位当前根节点和平台宿主。
2. 标记当前实例并生成唯一 id。
3. 解析 26 项配置并注入 CSS 变量。
4. 设置平台高度、编辑器顶部偏移和 sticky 状态。
5. 初始化 Logo、公司名、搜索、登录、语言、移动端菜单。
6. 渲染配置导航或 fallback。
7. 未配置导航时请求 `/api/navCat` 并更新当前实例。
8. 绑定 Escape、resize、scroll 和必要的能力检测。

## 可选增强

仅在用户明确要求时增加：

- GSAP 或复杂入场动画。
- 搜索历史、热门词和占位词轮播。
- mega menu。
- 超长导航自动折叠。
- 特殊透明首屏覆盖布局。

增强失败不能影响基础导航。

## 验收

- [ ] PC 和移动端初始显隐正确。
- [ ] 二级/三级菜单、移动端递归和当前页高亮正确。
- [ ] 搜索、登录、语言和联系方式按配置显示。
- [ ] sticky 开关、滚动态 Logo 和颜色切换正确。
- [ ] Escape、遮罩和切回 PC 都能关闭浮层并恢复滚动。
- [ ] 两个实例互不影响。
- [ ] API、配置解析或增强能力失败时保留基础导航。
- [ ] HTML 与完整 26 项 JSON 同时交付。
