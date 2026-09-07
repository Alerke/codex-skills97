# 新版顶部导航示例提炼

本参考来自 2026-07-28 提供的真实导航代码与 26 项配置。示例用于确认平台能力和数据结构，不直接复制其中的 Less、全局选择器、可选链或超长导航收缩实现。

## 已确认配置变化

- 在原有 `nav` 后新增 `use_custom_language_jump` 和 `language_nav`。
- 两个导航列表都使用新编辑器 `navList` 控件。
- 主导航节点包含 `id/title/jump/children/remark/icon/hoverIcon/hidden/isBackend`。
- 语言节点沿用同一结构，并可能包含编辑器状态字段 `collapsed`；运行时无需依赖该字段。
- `i18n` 的 `input_type` 为 `i18n`。

## 可复用实现精髓

- 主导航优先使用可视化配置，并保留 `/api/navCat` 作为未配置时的数据来源。
- 自定义语言开关开启时，语言代码取节点 `id`，显示名取 `title`，跳转取 `jump`。
- 自定义语言开关关闭时，平台语言列表来自 `/shop/frontend/languageList`。
- 登录态可读取 `GwShopUserToken`，但登录页和用户中心路径仍需按当前站点确认。
- 搜索热词可由 `/shop/frontend/search/getSearchbar` 提供，但搜索历史、热词和占位词轮播属于可选增强。
- 编辑器和 sticky 状态必须保留模块可选中高度，不能因为浮动导航把宿主高度永久归零。

## 不作为默认能力

- 示例中的超长导航宽度测量、“更多”菜单和节点 clone 不进入默认产物。
- 示例中的 Less 只用于理解视觉层级；新生成模块使用两个原生 CSS 样式块。
- 示例中的 `async/await`、可选链和高版本 API 需要按目标浏览器降级，默认仍执行 Skill 的成熟 ES6 约束。
- 热词、搜索历史、复杂动画、mega menu 仅在用户明确要求时增加，失败不得影响基础导航。
