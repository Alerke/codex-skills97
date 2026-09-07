---
name: ltd-product-list-builder
description: 创建、重构、审查或排查 LTD 建站平台的产品列表与商品列表代码模块。适用于 moduleType 为 product 或 goods、cat_id、限定分类树、父子分类聚合、URL 状态、关键词搜索、排序、分页或加载更多、网格/列表布局、产品卡片、点击操作、data-gw-jump、弹窗触发、价格展示、空状态、接口降级、可导入配置 JSON、多实例和旧版 Safari/Chromium/WebView 兼容任务；不用于产品详情页、购物车或结算流程。
---

# LTD 产品与商品列表 Skill

## 边界

- 使用同一套列表内核处理产品与商品的工具栏、分类、卡片、搜索、排序、分页和状态。
- 模块必须先读取 `$[cat_id.moduleType]`，再选择 `product` 或 `goods` 适配器；分类接口、列表接口和字段解析必须全部来自已选适配器，不能先写死接口再反推类型。
- 当前 `moduleType` 只允许 `product`（产品）和 `goods`（商品）两个精确值；`shopGoods` 仅是商品 API 路径命名，不是配置类型，也不做别名兼容。
- 产品详情、SKU 选择、加购、支付、订单与会员业务不属于默认范围。
- 新建任务默认交付完整模块 HTML 和可直接导入 LTD 的配置 JSON；用户明确说“只要代码”或“不要 JSON”时才省略 JSON。
- 只生成前端 HTML、原生 CSS 和 JavaScript，不设计 Python、后端、数据库或构建工程。

## 必读顺序

开始实现前完整读取：

1. [`references/platform.md`](references/platform.md)：LTD 宿主、样式隔离、多实例、响应式和兼容性。
2. [`references/data.md`](references/data.md)：共用请求参数、响应结构、字段归一化和安全渲染。
3. [`references/list-response.md`](references/list-response.md)：已确认的 `data.data` 列表结构、分页字段、图片、价格和链接映射。
4. [`references/product-goods-adapter.md`](references/product-goods-adapter.md)：产品与商品共用内核、接口映射和差异字段。
5. [`references/price-format.md`](references/price-format.md)：价格字段归一化、单位符号去重和零价格。
6. [`references/category-type.md`](references/category-type.md)：分类类型点号语法、运行时读取和旧环境兼容。
7. [`references/i18n.md`](references/i18n.md)：多语言对象、类型标题、语言映射、运行时优先级和逐键回退。
8. [`references/click-action-type.md`](references/click-action-type.md)：点击类型、点号字段、小程序归一化和弹窗内容。
9. [`references/config-error-handling.md`](references/config-error-handling.md)：未替换变量、错误类型、旧数据和局部致命配置的安全降级。
10. [`references/implementation-core.md`](references/implementation-core.md)：初始化顺序、配置归一化、请求和渲染边界。
11. [`references/category-tree.md`](references/category-tree.md)：后台限定分类、子级提升、父级递归聚合和选中状态。
12. [`references/state-pagination.md`](references/state-pagination.md)：实例状态、URL 同步、并发控制和分页。
13. [`references/click-action-runtime.md`](references/click-action-runtime.md)：静态配置、动态详情链接、平台运行时和事件分工。
14. [`references/click-action-style.md`](references/click-action-style.md)：卡片点击结构、hover/focus/active/禁用状态和弹窗视觉参考。
15. [`references/config.md`](references/config.md)：分类变量、占位符与可导入 JSON。
16. [`references/module-spec.md`](references/module-spec.md)：默认模块、交互状态和验收。

发生冲突时按以下优先级处理：

`SKILL.md` → `platform.md` → `data.md` → `list-response.md` → `product-goods-adapter.md` → `price-format.md` → `category-type.md` → `i18n.md` → `click-action-type.md` → `config-error-handling.md` → `implementation-core.md` → `category-tree.md` → `state-pagination.md` → `click-action-runtime.md` → `click-action-style.md` → `config.md` → `module-spec.md`。

## 输出合同

模块代码使用：

```html
<style data-product-list-initial>原生首屏 CSS</style>
<style data-product-list-styles>原生业务 CSS</style>
<!-- HTML -->
<script>JavaScript</script>
```

随后同步交付完整配置 JSON 数组：

- 顶层必须是数组。
- 每项包含 `key`、`label`、`value`、`default_value`、`input_type`。
- JSON 中的 key 与 HTML 占位符根 key 必须一一对应且唯一；`$[cat_id.moduleType]` 等点号语法仍只对应一个 `cat_id` 配置项。
- 分类选择配置的 `input_type` 固定为 `category`；不得写成 `cat`、`select`、`product`、`goods` 或自定义类型。
- 多语言配置根 key 使用 `i18n`，其 `input_type` 也固定为 `i18n`；两者在平台配置中名称相同。
- 不使用注释、省略号、字段表或伪代码代替真实 JSON。
- 配置 JSON 中 `cat_id`、`i18n` 等复合项的 `value` 与 `default_value` 必须是可再次 `JSON.parse` 的字符串。
- `cat_id` 存储对象需保留编辑器产生的 `names` 和可选 `sortColumnVersion`；后者是分类控件版本元数据，不作为接口参数或独立配置 key。
- 生成的代码必须让 `cat_id.moduleType` 决定实际列表/分类接口。只有人为把已有配置从一个体系迁移成另一体系时，才需要同步清空原体系的 `ids/names/type`，不能把迁移规则误用于正常运行时。
- 模块运行时代码读取分类时使用点号语法；`$[cat_id]` 直接取得 ID 字符串，不默认对它执行 `JSON.parse`。
- 模板替换后的 `$[i18n]` 标准输出是 JavaScript 对象；配置导入字符串与运行时对象不得混淆或重复解析。
- 新建模块可从同目录 [`产品商品列表配置.json`](产品商品列表配置.json) 复制完整可导入基线，再按实际 HTML 使用项增删；不得只交付文字说明。

## 硬规则

### 样式和结构

- 初始状态和业务样式均使用标准 CSS，不使用 Less 或运行时样式编译器。
- 根类使用 `.productListYYYYMMDD`；子级使用带项目缩写或 `pl-` 前缀的语义类。
- 所有业务选择器从当前根类开始；平台规则从真实模块名称 `.gw-browse-module[name="产品列表"]`、`.gw-browse-module[name="商品列表"]` 或当前实例宿主类开始。
- 不裸写 `html`、`body`、`:root`、通用标签、`.container`、`.wrapper`、`.content` 等全局选择器。
- 默认 PC 优先，至少检查 `1024px`、`768px`、`576px` 三档。
- 功能图标默认优先使用内联 SVG，设置 `viewBox` 并用 `currentColor` 继承控件颜色；不使用 Emoji、特殊字符或不稳定的系统字形冒充图标。
- 大量统一图标可使用 Font Awesome：优先复用页面已有版本，只有确认未加载且任务允许外部依赖时才引入固定版本；不得重复加载或混用多个版本。
- 图标样式限制在模块根类内；纯装饰 SVG 使用 `aria-hidden="true"`，图标按钮必须由按钮提供可访问名称。

### 平台和实例

- 使用 `document.currentScript` 定位当前实例，所有普通 DOM 查询限制在当前根容器内。
- 状态、请求序号、事件和分页均保存在当前实例闭包或实例类中。
- 不使用固定 id、`getElementById` 或全局遍历重复绑定。
- 不修改自动生成的 `.merge.html`，不重复引入平台已有的 jQuery、Vue 或 Swiper。

### JavaScript 与兼容性

- 生成的 JavaScript 默认必须使用普通 `<script>` 可直接运行的成熟 ES6 语法；使用 `const`/`let` 管理变量，回调和纯函数优先使用箭头函数，多行模板必须优先使用模板字面量（template literals）。
- 可使用数组迭代、解构和默认参数使状态与数据流清晰。不得在没有明确兼容要求时自行退回以 `var`、大量普通回调和字符串 `+` 拼接为主的 ES5 写法。
- 多行静态结构、卡片批量模板和可读字符串必须优先使用模板字面量；所有接口文本、属性和 URL 必须先分别转义或校验，禁止把原始数据直接插入 `innerHTML`。
- 兼容性优先于追求新语法；未确认运行环境时避免可选链、空值合并、`async/await`、动态 `import()`、对象展开等 ES2017+ 能力。
- 不依赖 `:has()`、`:scope`、`replaceChildren()`、`structuredClone()`、`Array.prototype.flat()`、`Object.fromEntries()` 等旧 Safari/Chromium/WebView 风险能力。
- 对 `Element.closest`、`Object.assign` 等不稳定能力使用模块内局部兼容函数；不为了少量 API 加载整套 polyfill。
- 不用 user-agent 判断能力，优先特性检测。若目标浏览器不能解析 ES6，须整体转译或按用户要求输出 ES5 版本；运行时 polyfill 无法修复语法解析失败。

### 数据

- `product` 默认列表接口为 `/api/gatewayCms/product/getProductList`，分类接口为 `/api/common/productCat?format=tree`。
- `goods` 默认列表接口为 `/api/gatewayCms/shopGoods/getShopGoodsList`，分类接口为 `/api/gatewayCms/shopGoods/category`。
- 共用请求、状态、分类、分页、卡片壳和交互；接口 URL、专属参数、字段归一化和可选能力由数据适配器提供。
- 分支只允许出现在适配器边界；不得在渲染器各处反复判断 `moduleType`。
- 通用模块必须同时注册 `product/goods` 两个适配器，并用校验后的 `$[cat_id.moduleType]` 直接取 `adapters[moduleType]`。`product` 自动使用产品分类/列表接口，`goods` 自动使用商品分类/列表接口。
- 请求时必须读取 `adapter.categoryUrl` 和 `adapter.listUrl`；不得在通用请求器外另写固定的 `LIST_API_URL`，也不得用接口 URL 覆盖一个有效的 category 类型。
- 当现有代码的固定接口与有效 `moduleType` 不一致时，固定接口属于待修复实现：改为调用该类型适配器的接口，而不是忽略配置、清空分类或继续请求错误体系。
- 所有 LTD 请求携带 `website_id: localStorage.getItem("websiteId")`，并按当前页面语言传 `language_type` 或请求头。
- 使用平台请求封装 `r()`；仅在模块运行环境没有该封装时，才在当前模块内提供兼容实现。
- 关键词参数为 `keywords`，分页参数为 `page` 和 `page_size`，排序参数 `order` 是 JSON 字符串。
- 已确认列表响应以 `response.data.data` 为数组，`response.data.total/page_size/current_page` 为分页字段；`page_size` 可能是字符串，必须安全转为有限整数。历史结构只能在同一个响应适配器内有序回退。
- 图片只按 URL 有效性判断；`thumbnail.id` 为 `0` 时 `thumbnail.url` 仍可能是有效缺省图，不能因 id 为 0 隐藏。
- 已确认响应的 `price` 是元单位十进制字符串，不除以 100；`price_ceiling` 是可选区间上限，不是市场价，`0.00` 时隐藏且不得生成划线 `marketPriceText`。价格按 `price-format.md` 归一化为包含单位的最终 `priceText`，默认通过唯一文本节点一次写入。禁止静态符号 span、CSS `content` 或渲染器再次添加单位，价格为 0 仍显示。
- 标题、分类、文本、图片属性和接口动态链接使用 DOM API 安全写入；拒绝任意 `javascript:`、`data:`、`vbscript:`。仅平台 `none` 的空操作和明确 `miniProgram` 的严格 `javascript:jumpMall(...)` 属于受控例外，不能用于接口数据。
- 分类配置固定读取 `$[cat_id]`、`$[cat_id.moduleType]`、`$[cat_id.type]`、`$[cat_id.pageSize]`、`$[cat_id.sortColumn]`、`$[cat_id.sortDirection]`。
- `input_type: "category"` 表示分类控件类型；`moduleType: "product"/"goods"` 表示业务体系，两者不能互换。
- `$[cat_id]` 为空、未传或没有选中分类时表示不限制分类：省略请求的 `cat_id` 或按接口要求传空字符串，获取当前 product/goods 适配器下的全部数据，不自动选择第一个分类。
- 若已配置非空允许分类 ids，先递归展开为 `allowedScopeIds`；“全部”只获取该展开范围内的数据。空配置才表示当前数据源全量，不能把产品与商品两个体系混合请求。
- `sortColumn` 支持平台配置的自定义字段；通过计算属性创建对象后 `JSON.stringify`，不得拼接原始 JSON 文本。
- `type` 允许为空；`ids` 与 `names` 按编辑器顺序保存，运行时筛选只信任 ids；可选 `sortColumnVersion` 原样保留但不参与请求。
- 多语言标准 key 为 `zh-cn/zh/en/kr/ru/jp`；语言优先读取 `editor_language_type`，再读 `localStorage.lang`，最后回退 `zh-cn`，并对缺失文案逐键回退。
- 多语言配置必须同时使用 `key: "i18n"` 与 `input_type: "i18n"`；前者供 `$[i18n]` 引用，后者决定平台多语言编辑控件。
- 可见模块标题使用 `product_title/goods_title` 两个 i18n 键；适配器类型切换后立即重算当前标题，不能在 HTML 或 JavaScript 中固定为“产品列表”或“商品列表”。

### 状态和请求

- 至少提供加载、成功、空数据和错误四种互斥状态。
- 新搜索、新分类或新排序必须重置到第 1 页。
- 防止连续请求乱序覆盖新结果，可使用递增请求序号或可取消请求。
- 请求失败时保留工具栏与重试入口，不清空整个模块宿主。
- 分页页码与总页数必须来自真实响应或可靠计算，不硬编码。
- 分类选择状态与接口查询分类分开保存：URL 记录单个 `selectedCatId`，请求时再计算父分类及全部后代的 `queryCatIds`。
- 后台允许范围中的父分类必须递归展开为自身和所有层级后代；选择父级与选择“全部允许范围”都发送展开、去重后的 ID 集合，不能只发直接 children 或原始 allowedIds。
- 使用 `show_all_button` 的 `switch` 配置控制“全部”按钮显隐；关闭只影响 UI，不改变空 `selectedCatId` 的全量语义，不得自动选择第一个分类。
- URL 参数前缀必须按实例生成；不得让两个产品列表共用固定 `cpcat_` 前缀。
- 不用单个 `loading` 布尔值直接丢弃加载期间的新筛选；使用请求序号或取消旧请求，保证最后一次操作生效。
- 分类接口失败时仍请求产品列表；分类不是主列表成功显示的硬依赖。

### 配置容错

- 所有后台配置均视为不可信输入；每个根配置项独立检测未替换占位符、类型和取值范围，失败后返回稳定默认类型，不能抛出未捕获异常。
- `switch` 必须显式识别开值 `"1"/1/true/"true"` 和关值 `"0"/0/false/"false"`；不得让 `"0"` 回退为默认开启，也不得使用 `Boolean("0")`。
- 筛选型配置为空或未传时默认表示“不附加该筛选条件”，从当前数据源获取满足其他已生效条件的全部数据；不得虚构分类、关键词、价格或属性条件。
- `category` 字段异常时分别回退 ids、页数和排序；`i18n` 异常时回退内置中文；`jump` 异常时回退 `none`；开关、数字、颜色、尺寸和 URL 使用各自的安全默认值。
- 直接注入对象的读取动作使用局部 `try/catch` 隔离求值错误，但标准 `$[i18n]` 仍按对象使用，不盲目重复解析。
- `moduleType` 缺失、空值或未替换时使用本次交付明确的默认类型；任何非空的其他值（包括 `shopGoods`）均视为非法，不得静默回退，并只在当前实例显示配置错误。
- 不用覆盖整个初始化的空 `catch` 隐藏错误，不在生产前台打印完整配置或连续错误日志。

### 点击操作

- 静态后台点击配置使用 `input_type: "jump"`，模板始终优先把 `$[key.href]` 写入 `href`，按需使用 `$[key.target]`；所有点号字段共同对应一个配置根 key，不解析 `$[key]` 为 JSON。
- 平台在保存和渲染阶段归一化 `none/web/url/module/miniProgram/openForm/popup/mobile/email`，并为复杂类型注入 `data-gw-*` 与关联模板；模块不得重复实现属性映射器。
- 接口返回的动态详情地址仍通过 DOM API 创建安全真实 `<a>`，默认只作为普通链接，不推断为模块、表单或弹窗。
- 复用平台已有的 `data-gw-open-form-jump-runtime` 和 `Utils.Dialog.open`，不在列表中复制完整跳转/弹窗运行时或全局 `.gw-dialog-*` 样式。
- `miniProgram` 的严格 `javascript:jumpMall('路径')` 是平台受控桥接格式；历史 `web/url` 同格式会归一为小程序。不得因此放行任意脚本协议。
- 卡片存在有效操作时才显示 `cursor:pointer`、hover、focus-visible 和 active 状态；`none` 或无链接时保持普通内容样式。
- 整卡点击不能产生嵌套 `<a>`；卡片内有独立按钮或链接时，使用非链接卡片和事件排除规则。
- 平台运行时已处理的 `module`、`openForm`、`popup` 不得被模块本地事件再次执行。

## 默认能力

- 默认实现：一套产品/商品通用的分类配置、卡片网格、点击状态、加载态、空状态、错误重试和分页。
- 搜索、排序、布局切换、价格区间、属性筛选、推荐标识、销量/浏览量按用户要求或现有模块保留。
- 商品库存、SKU、销量、交易入口仅在 `goods` 且用户明确要求时启用；产品摘要、参数、附件、推荐仅在 `product` 且用户明确要求时启用。
- 默认不实现 SKU 弹窗、加购、收藏、对比、无限滚动、复杂筛选抽屉或强动效。
- 若用户提供现有模块，优先保留其视觉、字段和交互，只修复平台适配与可靠性问题。

## 工作流

1. 检查现有模块、真实模块名称、设计参考和交付位置。
2. 归一化 `cat_id.moduleType`，从适配器表选择数据源；确认通用请求器只使用已选适配器的分类 URL、列表 URL、参数和字段解析器。
3. 确定根类、宿主类和配置 key。
4. 先完成无需 JavaScript 也不会闪烁错位的初始 CSS 与 HTML 状态壳。
5. 完成带独立错误隔离的配置解析、请求状态机、字段归一化、卡片渲染、点击操作、筛选和分页。
6. 同步生成覆盖所有占位符的完整配置 JSON。
7. 验证脚本语法、JSON、占位符一致性、CSS 作用域、多实例和请求乱序。
8. 能实测时在 LTD 前台和编辑器中检查；无法实测时明确说明。

## 最终验收

- [ ] 产品与商品共用一套 UI/状态内核，只通过适配器区分数据。
- [ ] product 或 goods 适配器与接口一致，专属参数和字段未串用。
- [ ] 只把配置 `moduleType` 从 product 改为 goods、不修改 JS 时，分类和列表请求会自动从产品接口成对切换为商品接口；反向切换同样成立。
- [ ] 通用请求器只调用 `adapter.categoryUrl/listUrl`，没有独立写死商品或产品接口。
- [ ] HTML 与完整配置 JSON 同时交付。
- [ ] 页面不依赖 Less 编译即可正确显示。
- [ ] 加载、成功、空数据、错误与重试状态正常。
- [ ] 搜索/筛选/排序会重置页码，旧请求不会覆盖新结果。
- [ ] 后台限定分类、只选子分类、父子同时选择和父分类聚合查询均正确。
- [ ] 父分类筛选递归包含自身、子级、孙级及全部更深后代；“全部允许范围”对父级配置也使用展开后的 ID 集合。
- [ ] 分类六个点号占位符完整，`$[cat_id]` 未被错误地当作 JSON 对象解析。
- [ ] 分类根配置项使用 `input_type: "category"`，且没有生成点号子字段的独立配置项。
- [ ] 分类配置保留 ids/names 顺序和可选 `sortColumnVersion`，允许空 type，且未把编辑器元数据发送给列表接口。
- [ ] 分类配置为空/未传时请求当前适配器全部数据；存在允许 ids 时“全部”仍严格限制在允许范围，且不会自动选中首个分类。
- [ ] `show_all_button=1/0` 能显示/隐藏“全部”按钮；隐藏时查询范围、URL 和空选择语义不变。
- [ ] `$[i18n]` 按运行时对象读取，六种标准语言、别名映射、逐键回退和请求语言保持一致。
- [ ] 多语言配置同时使用 `key: "i18n"` 和 `input_type: "i18n"`。
- [ ] 任一配置缺失、未替换、类型错误或越界时均使用安全降级，不产生未捕获异常或阻塞同页其他模块。
- [ ] 有效配置类型不会被固定接口覆盖；类型缺失时才使用明确默认值，无有效类型或适配器时只显示局部配置错误。
- [ ] URL 只保存语义选中项，实例参数不冲突，浏览器历史策略前后一致。
- [ ] 图片、价格、链接和响应字段具备降级逻辑；销售价和市场价默认各只有一个最终文本节点，没有静态单位 span/伪元素与 `priceText` 叠加，价格 0 正常显示。
- [ ] 已确认响应能从 `data.data` 提取列表，从 `data.total/page_size/current_page` 提取分页；字符串 `"12"` 正确归一为 12。
- [ ] `thumbnail.id=0` 但 URL 有效时仍显示图片；`price='120.00'` 不除以 100，`price_ceiling='0.00'` 不生成市场价或灰色划线价格。
- [ ] product/goods 切换适配器时，可见标题、根节点无障碍名称和对应 i18n 文案同步切换。
- [ ] 静态点击配置使用同一根 key 的点号字段；`none/web/url/module/miniProgram/openForm/popup/mobile/email` 与四种弹窗语义正确。
- [ ] 平台受控 `jumpMall` 正常工作，接口任意脚本链接仍被拒绝，复杂操作没有双重触发。
- [ ] 卡片 hover/focus/active/无操作样式与实际可点击状态一致。
- [ ] 图标优先使用作用域内联 SVG；使用 Font Awesome 时没有重复加载、版本冲突或无障碍名称缺失。
- [ ] JavaScript 明确使用成熟 ES6：`const/let`、适用的箭头函数和模板字面量；未自行退回 ES5，也未混入未经确认的 ES2017+ 能力。
- [ ] PC、平板、手机和至少两个实例互不影响。
- [ ] 默认产物没有产品列表范围外的交易或后台功能。
