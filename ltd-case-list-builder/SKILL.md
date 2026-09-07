---
name: ltd-case-list-builder
description: 创建、重构、审查或排查 LTD 建站平台的案例列表模块。适用于 moduleType 为 case、category 分类配置、案例分类树、父子分类聚合、关键词搜索、排序、分页或加载更多、案例卡片、封面、摘要、详情链接、推荐状态、多语言、可导入配置 JSON、多实例和旧版 Safari/Chromium/WebView 兼容任务；不用于文章、产品商品、自定义内容列表或案例详情后台。
---

# LTD 案例列表 Skill

## 边界

- 只处理 LTD 前台案例分类、案例列表、筛选、搜索、排序、分页、卡片和状态。
- 分类 `moduleType` 固定为 `case`；不得借用 article、product 或 goods 接口。
- 新建任务默认同步交付完整模块 HTML 和可直接导入的配置 JSON。
- 只生成前端 HTML、原生 CSS 和 JavaScript，不创建 Python、后端或构建工程。

## 必读参考

1. [`references/platform-runtime.md`](references/platform-runtime.md)：样式、多实例、ES6、状态和安全渲染。
2. [`references/category.md`](references/category.md)：`category` 配置和父子分类范围。
3. [`references/api-response.md`](references/api-response.md)：案例接口、参数、双层列表响应和字段。
4. [`references/config.md`](references/config.md)：配置、占位符和容错。
5. [`references/i18n-links.md`](references/i18n-links.md)：多语言和详情链接。

用户提供的真实响应优先于兼容性推断；确认新结构后只修改响应适配器，不让渲染器同时理解多种原始结构。

## 输出合同

```html
<style data-case-list-initial>原生首屏 CSS</style>
<style data-case-list-styles>原生业务 CSS</style>
<!-- 当前模块 HTML -->
<script>JavaScript</script>
```

随后输出完整 JSON 数组：

- 每项包含 `key/label/value/default_value/input_type`。
- 分类根 key 默认 `cat`，`input_type` 固定为 `category`。
- 多语言根 key 和 `input_type` 均为 `i18n`。
- `cat/i18n` 的导入值是可再次解析的 JSON 字符串。

## 硬规则

### 分类和接口

- 读取 `$[cat]`、`$[cat.moduleType]`、`$[cat.pageSize]`、`$[cat.sortColumn]`、`$[cat.sortDirection]`；`$[cat]` 是逗号分隔 ID，不执行 `JSON.parse`。
- `moduleType` 必须为 `case`；分类控件为非文章类型保留的 `type: "1"` 只是编辑器元数据，不发送给案例接口。
- 默认分类接口：`/api/gatewayCms/case/category`。
- 默认列表接口：`/api/gatewayCms/case/list`。
- 列表使用 `cat_id`、`page`、`page_size`、`order`；仅在真实接口确认时增加 `keywords` 等参数。
- `order` 使用合法化字段构造对象后 `JSON.stringify`，不得拼接原始 JSON。
- 配置分类为空或未传时省略 `cat_id`，获取全部案例，不自动选中首个分类。
- 父分类选择递归包含自身与全部后代；“全部”在限定范围内发送展开后的允许 IDs。
- `show_all_button` 只控制按钮显隐，不改变空选择语义。

### 响应和字段

- 已确认列表主要结构为 `response.data.data.data`，分页位于 `response.data.data.total/page_size/current_page`。
- 只在响应适配器内按顺序兼容 `response.data.data` 直接为数组的历史结构。
- 字段按可选值读取：`id/title/abstract/thumbnail/detail_link/defined_link/cat_id/sort/is_recommended/created_at/updated_at`。
- 图片只按安全 URL 判断；不得因 `thumbnail.id === 0` 直接隐藏。
- 详情优先使用经过协议校验的 `detail_link`，其次是明确安全的 `defined_link`，最后使用 `/case/{encodeURIComponent(String(id))}`。
- 接口文本使用 `textContent` 或先转义；拒绝任意 `javascript:`、`data:`、`vbscript:`。

### 样式和实例

- 初始和业务样式都使用原生 CSS，不使用 Less。
- 根类使用 `.caseListYYYYMMDD`，业务选择器全部从根类开始。
- 平台规则从真实模块名称 `.gw-browse-module[name="案例列表"]` 或当前实例宿主类开始。
- 不裸写 `html/body/:root`、通用标签、`.container/.wrapper/.content`。
- 用 `document.currentScript` 定位实例；查询、状态、事件和请求序号限制在实例内。
- 不使用固定 id、`getElementById` 或修改 `.merge.html`。
- 图标优先用作用域内联 SVG 和 `currentColor`。

### JavaScript 和可靠性

- 使用普通 `<script>` 可运行的成熟 ES6：`const/let`、箭头函数、模板字面量、数组迭代、解构和默认参数。
- 未确认环境时避免可选链、空值合并、`async/await`、动态 `import()`、对象展开。
- 不依赖 `:has()`、`:scope`、`replaceChildren()`、`Array.prototype.flat()`、`Object.fromEntries()`。
- 每项配置独立归一化；未替换占位符、错误 JSON、错误类型和越界值不得抛出未捕获异常。
- switch 显式识别开关值，禁止 `Boolean("0")`。
- 至少实现 loading、success、empty、error/retry 四种互斥状态。
- 搜索、分类、排序变化重置第 1 页；用请求序号或取消旧请求避免乱序覆盖。
- 分类接口失败不阻塞案例列表；列表失败保留工具栏和重试。

## 工作流

1. 检查真实模块名称、现有视觉、交付位置和案例响应。
2. 校验 `moduleType: case`，归一化分类、分页和排序。
3. 建立分类树 Map、允许范围和父级后代展开。
4. 完成首屏 CSS、状态壳、请求适配器和安全卡片渲染。
5. 完成筛选、分页、多语言、详情链接和多实例清理。
6. 同步生成覆盖全部占位符的完整配置 JSON。
7. 验证 JS、JSON、占位符、CSS 作用域、多实例、空配置和请求乱序。

## 验收

- [ ] `case` 与其他数据类型接口没有混用。
- [ ] 空分类获取全部案例，父分类递归包含全部后代。
- [ ] 双层 `data.data.data` 和分页已归一化。
- [ ] 图片、摘要、详情链接和缺失字段安全降级。
- [ ] 四种状态、筛选重置和请求乱序正确。
- [ ] 原生 CSS、成熟 ES6、模板字面量、多实例和旧浏览器约束满足。
- [ ] HTML 与可直接导入 JSON 同步交付。
