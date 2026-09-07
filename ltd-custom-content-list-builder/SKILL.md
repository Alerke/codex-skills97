---
name: ltd-custom-content-list-builder
description: 创建、重构、审查或排查 LTD 建站平台的自定义内容列表模块。适用于 moduleType 为 customContent、category 分类配置、自定义内容分类树、父子分类聚合、关键词、排序、分页或轮播、动态 attrs、images、content、defined_link、多语言、可导入配置 JSON、多实例和旧版 Safari/Chromium/WebView 兼容任务；不用于文章、案例、产品商品列表或后台自定义内容管理。
---

# LTD 自定义内容列表 Skill

## 边界

- 只处理 LTD 前台自定义内容分类、列表和动态字段渲染。
- `moduleType` 固定为 `customContent`，不得因视觉像产品、文章或案例而切换接口。
- 自定义内容没有统一详情页；只使用真实安全链接，不虚构 `/custom/{id}`。
- 新建任务默认同步交付模块 HTML 和可直接导入配置 JSON。
- 只生成前端 HTML、原生 CSS 和 JavaScript。

## 必读参考

1. [`references/platform-runtime.md`](references/platform-runtime.md)
2. [`references/category.md`](references/category.md)
3. [`references/api-response.md`](references/api-response.md)
4. [`references/dynamic-fields.md`](references/dynamic-fields.md)
5. [`references/config.md`](references/config.md)

响应字段高度可配置。用户提供真实字段样本后，将其写入响应适配器和动态字段映射；不得从项目名称猜测字段。

## 输出合同

```html
<style data-custom-content-initial>原生首屏 CSS</style>
<style data-custom-content-styles>原生业务 CSS</style>
<!-- 当前模块 HTML -->
<script>JavaScript</script>
```

随后输出完整配置 JSON：

- 每项包含 `key/label/value/default_value/input_type`。
- 分类根 key 默认 `cat`，`input_type: "category"`。
- 多语言根 key 和类型均为 `i18n`。
- `cat/i18n` 的导入值可再次 `JSON.parse`。

## 硬规则

### 分类和接口

- 读取 `$[cat]` 及点号字段；`$[cat]` 是逗号 ID 字符串，不执行 `JSON.parse`。
- `moduleType` 必须为 `customContent`；分类控件兼容的 `type: "1"` 不发送给接口。
- 默认分类接口：`/api/website/customizedContentCat`。
- 默认列表接口：`/api/gatewayCms/getCustomizedContentList`。
- 已观察参数：`cat_id/page/page_size/keywords/sort_by/sort/language_type`。
- 分类为空时省略 `cat_id`，获取全部自定义内容。
- 父分类范围递归包含自身和全部后代；“全部”在限定范围内发送展开后的 IDs。
- `show_all_button` 只控制 UI，不改变查询范围。

### 响应和动态字段

- 已确认列表数组主要位于 `response.data.data`；分页字段如存在，读取 `response.data.total/page_size/current_page`。
- 常见字段：`id/cat_id/title/abstract/content/images/defined_link/attrs/sort/created_at/updated_at`，全部按可选值处理。
- 图片按 `images[].image.url` 等真实结构归一化；无图片时保持空，不虚构远程占位图。
- `attrs` 是动态字段集合，先归一成 Map，再按用户指定 key/name/id 渲染。
- `content` 可能是 HTML；默认不直接注入，只有用户明确要求且经过可信净化时才渲染。
- `defined_link` 安全有效时才生成链接；无链接保持不可点击。
- 不把 `sort` 当数组顺序唯一来源；接口排序和客户端稳定顺序需明确。

### 样式、JavaScript和可靠性

- 原生 CSS，不使用 Less；根类 `.customContentListYYYYMMDD`，所有选择器作用域隔离。
- 用 `document.currentScript` 定位当前实例，不使用固定 id 或全局重复绑定。
- 使用普通 `<script>` 的成熟 ES6、模板字面量；动态值先转义。
- 未确认环境时避免可选链、空值合并、`async/await`、动态 import、对象展开。
- 配置独立归一化；错误 JSON、未替换占位符、错误字段类型不得阻塞初始化。
- switch 显式识别开关，禁止 `Boolean("0")`。
- 至少实现 loading/success/empty/error+retry。
- 分类、搜索、排序变化重置第 1 页；用请求序号避免旧响应覆盖。
- 分类失败不阻塞列表；列表错误保留筛选和重试。

## 工作流

1. 检查真实模块、分类范围、列表响应样本和要展示的动态字段。
2. 校验 `moduleType: customContent`，归一化分类、分页、排序和语言。
3. 建立分类树、允许范围和父级后代展开。
4. 在响应适配器中归一化基础字段、图片、attrs 和安全链接。
5. 完成状态、筛选、分页/轮播、多实例和清理。
6. 同步输出完整 HTML 与可导入 JSON。
7. 验证 JSON、占位符、CSS 作用域、空配置、缺失动态字段和请求乱序。

## 验收

- [ ] customContent 接口没有与文章、案例或产品商品混用。
- [ ] 空分类获取全部内容，父分类递归范围正确。
- [ ] `response.data.data`、分页、images、attrs 和 defined_link 安全归一化。
- [ ] 缺失动态字段不报错，content 不会未经净化注入。
- [ ] 无 defined_link 时卡片不可点击，不虚构详情路径。
- [ ] 四种状态、多实例、成熟 ES6和原生 CSS满足要求。
- [ ] HTML 与完整可导入 JSON 同时交付。
