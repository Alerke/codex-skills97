---
name: ltd-article-list-builder
description: 创建、重构、审查或排查 LTD 建站平台的文章列表代码模块。适用于 moduleType 为 article、文章/视频/图册/图文/公告/活动/问答/知识/招聘/媒体报道等 mold_types、category 分类配置、分类树、父子分类聚合、关键词搜索、文章排序、分页或加载更多、文章卡片、发布时间、封面、摘要、作者、浏览量、扩展字段、文章详情链接、多语言、可导入配置 JSON、多实例和旧版 Safari/Chromium/WebView 兼容任务；不用于产品商品列表、文章详情编辑器或后台内容管理。
---

# LTD 文章列表 Skill

## 边界

- 只处理 LTD 前台文章列表及其分类、搜索、排序、分页、卡片和状态。
- 使用 `moduleType: "article"`，再由 `type` 决定 `mold_types`；不得把文章细分类型误当成独立 `moduleType`。
- 不混入商品价格、SKU、库存、加购、产品参数或交易逻辑。
- 新建任务默认同时交付完整模块 HTML 和可直接导入 LTD 的配置 JSON。
- 只生成前端 HTML、原生 CSS 和 JavaScript，不创建 Python、后端、数据库或构建工程。

## 必读参考

实现前按任务读取：

1. [`references/platform.md`](references/platform.md)：样式隔离、多实例、依赖和浏览器兼容。
2. [`references/category-and-types.md`](references/category-and-types.md)：`category` 配置、文章类型映射和父子分类范围。
3. [`references/article-type-profiles.md`](references/article-type-profiles.md)：十种文章细分类型的展示重点与禁止推断。
4. [`references/api-and-response.md`](references/api-and-response.md)：文章分类/列表接口、参数和响应归一化。
5. [`references/runtime.md`](references/runtime.md)：初始化、状态、并发、分页、安全渲染和销毁。
6. [`references/config.md`](references/config.md)：占位符、配置容错和可导入 JSON 基线。
7. [`references/i18n-and-links.md`](references/i18n-and-links.md)：多语言、详情链接和平台点击操作边界。

发生冲突时按 `SKILL.md` → 上述顺序处理。用户提供的已验证真实接口或响应优先于参考中的兼容性推断，并同步更新适配器。

## 输出合同

按以下顺序交付：

```html
<style data-article-list-initial>原生首屏 CSS</style>
<style data-article-list-styles>原生业务 CSS</style>
<!-- 当前模块 HTML -->
<script>JavaScript</script>
```

随后输出完整配置 JSON 数组：

- 每项包含 `key`、`label`、`value`、`default_value`、`input_type`。
- 配置 key 与占位符根 key 一一对应且唯一。
- 分类根 key 默认使用 `cat`，`input_type` 固定为 `category`。
- 多语言根 key 和 `input_type` 均固定为 `i18n`。
- `cat`、`i18n` 的导入值是 JSON 字符串；运行时 `$[i18n]` 是对象，不重复解析。
- 不用注释、伪代码、省略号或字段表代替真实 JSON。

## 硬规则

### 分类与文章类型

- 分类运行时读取 `$[cat]`、`$[cat.moduleType]`、`$[cat.type]`、`$[cat.pageSize]`、`$[cat.sortColumn]`、`$[cat.sortDirection]`。
- `$[cat]` 直接输出逗号分隔的分类 ID，不对其执行 `JSON.parse`。
- `moduleType` 必须为 `article`；`type` 默认 `"1"`，请求时映射到 `mold_types`。
- 支持的已知 type：`1` 文章、`2` 视频、`12` 图册、`19` 图文、`11` 公告通知、`10` 最新活动、`6` 常见问题、`5` 业务知识、`7` 官方招聘、`8` 媒体报道。
- 十种类型共用文章分类与列表接口，不为每种类型复制一套请求层；差异只落在标题文案、卡片字段和媒体展示策略。
- 切换 `cat.type` 后，模块标题、空状态和辅助文案必须切换为对应类型；不得继续显示固定“文章列表”。
- 类型专有字段只在真实响应确认后读取；不能因为类型名称推测并虚构 `video_url`、`gallery`、`salary`、`event_time` 等字段。
- 不因 UI 文案叫“招聘列表”或“视频列表”而改写 `moduleType`。
- 分类配置为空或未传时表示不限制分类，请求当前 type 下的全部数据；不得自动选中第一项。
- 后台指定分类范围时，父分类必须递归包含自身和所有后代；选择“全部”也只能查询该允许范围。
- 使用 `show_all_button` 控制“全部”选项显隐；隐藏仅影响界面，不改变空选择的全量语义。

### 接口与数据

- 默认分类接口：`/api/gatewayCms/articles/category`。
- 默认列表接口：`/api/gatewayCms/articles/list`。
- 分类和列表必须使用同一个 `mold_types`。
- 列表参数使用 `mold_types`、`cat_ids`、`page`、`page_size`、`keywords`、`sort_by`、`sort`、`language_type`。
- 只在配置分类非空时发送 `cat_ids`；排序字段来自合法化后的 `cat.sortColumn`，排序方向只允许 `asc/desc`。
- 优先使用页面已有请求封装 `r()`；缺失时才提供当前实例内的安全降级，不硬编码 localhost、代理域名或站点域名。
- 归一化列表响应后再渲染；已确认主结构为 `response.data.data`，分页来自 `response.data.total/page_size/current_page`。
- 按已确认列表项结构安全读取 `id/cat_id/type/title/thumbnail/source/source_url/author/abstract/seo_*/sort/is_recommended/created_at/updated_at/website_id/language_type/published_at/file/original_application/mold/share_copy/is_person/status/user_id/block_id/open_comment/ai_status/original_url/content/info/views`；每个字段仍按可选值处理。
- `id` 在已确认响应中是长数字字符串；从接收到生成详情 URL 的全过程保持字符串，禁止无意义的 `Number(id)`、一元 `+id` 或 `parseInt(id)`，以保持接口类型并兼容前导零或未来更大 ID。
- 已确认列表项没有 `defined_link` 或 `detail_url`；默认详情地址使用 `/article/{encodeURIComponent(String(id))}`。只有后续真实响应明确提供详情字段时才增加安全链接适配器。
- 不把接口文本直接拼进未转义的 `innerHTML`，不放行任意 `javascript:`、`data:` 或 `vbscript:`。

### 样式、实例与图标

- 初始状态与业务样式均使用原生 CSS，不使用 Less。
- 根类使用 `.articleListYYYYMMDD`，所有业务选择器必须从当前根类开始。
- 平台宿主规则从真实模块名称 `.gw-browse-module[name="文章列表"]` 或当前模块实际名称开始。
- 不裸写 `html`、`body`、`:root`、标签选择器、`.container`、`.wrapper` 等全局规则。
- 使用 `document.currentScript` 定位当前实例；DOM 查询、事件、请求序号和状态均限制在实例内。
- 不使用固定 id、`getElementById`、全局重复绑定或修改 `.merge.html`。
- 功能图标优先使用作用域内联 SVG 和 `currentColor`；需要大量图标时才复用页面已有 Font Awesome。

### JavaScript 与可靠性

- 使用普通 `<script>` 可运行的成熟 ES6：`const/let`、箭头函数、模板字面量、数组迭代、解构和默认参数。
- 多行结构优先模板字面量，但动态文本、属性和 URL 必须先转义或校验。
- 未确认环境时避免可选链、空值合并、`async/await`、动态 `import()`、对象展开等更高版本能力。
- 不依赖 `:has()`、`:scope`、`replaceChildren()`、`Array.prototype.flat()`、`Object.fromEntries()`。
- 所有配置独立归一化；未替换占位符、空值、错误 JSON、错误类型或越界值不得抛出未捕获异常。
- `switch` 显式识别 `"1"/1/true/"true"` 与 `"0"/0/false/"false"`，不得使用 `Boolean("0")`。
- 至少实现加载、成功、空数据和错误重试四种互斥状态。
- 搜索、分类和排序改变时重置为第 1 页；使用请求序号或取消旧请求防止乱序覆盖。
- 分类接口失败不阻塞文章列表；列表失败保留工具栏与重试入口。

### 多语言和内容

- 语言优先读取 URL `editor_language_type`，再读 `localStorage.lang`，最后回退 `zh-cn`。
- 标准语言 key 为 `zh-cn/zh/en/kr/ru/jp`，缺失文案逐键回退到 `zh-cn` 和内置中文。
- 请求语言与界面语言使用同一个归一化结果。
- 日期必须容忍空值和非法值，不直接对未知值调用 `split`。
- 封面按 `thumbnail.url` → `thumbnail.thumbnail` → `file.url` → `file.thumbnail` 回退；只按 URL 有效性判断，不因媒体对象的 `id/is_image` 为 `0` 隐藏图片。
- 列表项的分类只有 `cat_id` 时，通过已经请求的分类树映射分类名；不得虚构 `article_cat`。
- 扩展字段的已确认路径是 `info.extension_field`，且可能为 `null`；历史项目需要兼容 `article_info.extension_field` 时只能作为次级回退，并使用安全点路径函数。
- `content` 是完整 HTML 正文，默认不在列表卡片中渲染，也不作为摘要自动注入；用户明确要求正文预览时必须先使用平台可信净化器或经过验证的 HTML 净化流程。
- `source_url` 与 `original_url` 是来源元数据，不是本站文章详情链接；除非用户明确设计“查看来源”，不得替代 `/article/{id}`。
- `type` 与 `mold` 是返回项类型；请求数据源仍由配置 `cat.type → mold_types` 决定，不用单条异常数据反向切换接口。
- 默认文章卡片只显示配置允许的标题、摘要、日期、封面、分类、作者和浏览量；不虚构缺失内容。

## 工作流

1. 检查现有模块、真实模块名称、视觉参考、文章 type 和交付位置。
2. 读取分类配置，固定校验 `moduleType: article`，归一化 `type/pageSize/sortColumn/sortDirection`。
3. 确定根类、实例宿主、配置 key、列表展示字段和详情链接策略。
4. 先完成不会因脚本延迟而闪烁错位的初始 CSS 与状态壳。
5. 完成分类树递归范围、请求状态机、响应适配器、安全卡片渲染、筛选和分页。
6. 同步生成覆盖所有占位符的完整可导入配置 JSON。
7. 验证 JavaScript 语法、JSON、占位符一致性、CSS 作用域、多实例、空配置和请求乱序。
8. 能实测时检查 LTD 前台和编辑器；无法实测时明确列出未验证的接口字段。

## 最终验收

- [ ] 文章列表独立于产品商品 Skill，没有价格、SKU 或交易逻辑。
- [ ] `moduleType` 固定为 `article`，`type` 正确映射到分类和列表的同一个 `mold_types`。
- [ ] 分类为空时获取当前 type 的全部文章；限定范围和父分类递归聚合正确。
- [ ] “全部”按钮可配置显隐，隐藏不改变查询语义。
- [ ] `response.data.data`、`total/page_size/current_page` 已安全归一化。
- [ ] 长字符串 id 没有数值化，详情 URL 保留接口返回的完整 id。
- [ ] `cat_id`、日期、封面/file 回退、摘要、作者、浏览量、`info.extension_field` 缺失时不报错。
- [ ] `content` 没有未经净化直接注入列表，`source_url/original_url` 没有误当详情链接。
- [ ] 加载、成功、空数据、错误重试和分页状态正确。
- [ ] 搜索/分类/排序重置页码，旧请求不会覆盖新请求。
- [ ] 详情链接安全，动态文本和属性没有未转义注入。
- [ ] 分类使用 `input_type: "category"`，多语言使用 `key/input_type: "i18n"`。
- [ ] 模块 HTML 与完整可导入 JSON 同步交付。
- [ ] 原生 CSS、成熟 ES6、模板字面量、图标、多实例和旧浏览器约束均满足。
