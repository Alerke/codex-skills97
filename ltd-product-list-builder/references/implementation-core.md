# 产品列表实现核心

本规范提炼自一份实际 LTD 产品分类列表模块，只保留可复用实现机制，不继承其 Less、设计系统、GSAP、视觉变量或具体样式。

## 目录

- [初始化顺序](#1-初始化顺序)
- [配置归一化](#2-配置归一化)
- [多语言与行为开关](#3-多语言与行为开关)
- [单一状态和派生值](#4-单一状态和派生值)
- [数据请求边界](#5-数据请求边界)
- [渲染边界](#6-渲染边界)
- [事件绑定](#7-事件绑定)
- [不继承的实现](#8-不继承的实现)

## 1. 初始化顺序

按以下顺序初始化一个实例：

1. 通过 `document.currentScript` 定位当前根节点并设置 `data-mounted`。
2. 缓存当前根节点内必要 DOM；缺少核心列表容器时立即退出。
3. 按 [`config-error-handling.md`](config-error-handling.md) 独立读取每个配置：先读取 `cat_id` 六个字段，再解析开关、数字、i18n 和行为配置；单项失败只使用该项默认值。
4. 归一化 `cat_id.moduleType`，从 product/goods 适配器表选出唯一适配器；分类和列表请求都从该适配器读取 URL。
5. 生成当前实例 id 与 URL 参数命名空间。
6. 从 URL 恢复语义状态，创建单一状态对象。
7. 只绑定一次根节点事件委托、分页事件和必要的窗口事件。
8. 请求分类；成功后构建允许范围内的分类树，失败时显示局部分类错误。
9. 无论分类请求成功与否，都请求产品列表。
10. 进入 loading → success/empty/error 状态并渲染分页。

不要把样式初始化、数据初始化和事件绑定交叉散落在脚本顶层。必须用 ES6 的 `const`/`let`、适用的箭头函数和清晰的小函数组织 `createProductList(root, config)`；普通 `function` 只保留给动态 `this`、构造函数语义或明确的旧环境兼容点。最外层实例保护只兜住意外错误，不能代替各配置读取器的局部降级。语法与 API 边界见 [`platform.md`](platform.md)。

## 2. 配置归一化

分类类型以六个点号占位符为标准；`$[cat_id]` 直接输出逗号 ID，不能默认当成 JSON。完整规则见 [`category-type.md`](category-type.md)。模板替换后的 `$[i18n]` 标准输出为对象，按 [`i18n.md`](i18n.md) 归一化；只有旧项目实际输出字符串时才集中解析一次。点击操作使用 `$[link.href]`、`$[link.type]` 等点号字段，不解析 `$[link]`，完整规则见 [`click-action-type.md`](click-action-type.md)。

再提供三个独立读取器：

- `readText(fallback, ...candidates)`：跳过空值和未替换占位符。
- `readNumber(fallback, min, max, ...candidates)`：转换为有限数字并限制范围。
- `readSwitch(fallback, value)`：显式识别 `"1"/1/true/"true"` 为开启，`"0"/0/false/"false"` 为关闭；其他值才回退，不能使用 `Boolean("0")`。

`show_all_button` 使用 `readSwitch(true, '$[show_all_button]')` 归一为布尔值，仅交给分类渲染器控制“全部”按钮显隐；不得参与 `selectedCatId/queryCatIds` 的计算。

读取器必须检测未替换 `$[...]`，捕获 JSON 解析和直接对象求值错误，并始终返回稳定类型。完整实现与各配置降级表见 [`config-error-handling.md`](config-error-handling.md)。

六个占位符最终归一化为：

```js
{
  moduleType: 'product',
  ids: '',
  type: '',
  pageSize: 12,
  sortColumn: 'sort',
  sortDirection: 'desc'
}
```

- `ids` 允许逗号字符串或数组，最终转为去重字符串数组。
- `names` 和 `sortColumnVersion` 只属于可导入配置/编辑器存储元数据，不加入运行时请求模型；names 不可信时不影响 ids。
- `pageSize` 限制在 `1–100`。
- `sortColumn` 支持平台配置的业务自定义字段；限制长度并拒绝控制字符，通过对象计算属性和 `JSON.stringify` 构造 `order`，不能拼接 JSON。
- `sortDirection` 只接受 `asc/desc`。
- 有效 `moduleType` 是通用模块选择适配器的权威：`product` 使用产品适配器，`goods` 使用商品适配器。当前不接受第三种值，不能用写死的接口 URL 覆盖有效类型。
- 分类请求和列表请求必须共享同一个 `adapter`；分别写 `if` 或提前写死其中一个 URL 都不合格。
- `moduleType` 缺失、空值或未替换时才使用明确默认值；非空非法值不回退默认类型，只显示当前实例配置错误。
- 配置类型缺失或占位符未替换时回退 `DEFAULT_MODULE_TYPE`；值非法且没有有效默认值，或对应适配器不存在时，才显示局部配置错误。

## 3. 多语言与行为开关

在创建状态前按 [`i18n.md`](i18n.md) 完成多语言归一化：URL 的 `editor_language_type` 优先于 `localStorage.lang`，别名映射到六种标准语言，再逐键回退 `zh-cn` 和内置文案。标准 `$[i18n]` 直接作为对象读取，不盲目 `JSON.parse`；请求的 `language_type` 与界面语言使用同一归一化值。先解析 moduleType 并创建 `t()`，再用 `product_title/goods_title` 初始化标题、无障碍名称、空状态和分页文案；类型变化时重新执行标题绑定。

配置控制显隐时切换根节点状态类或元素 `hidden` 属性，不把大量 `style.display` 分散在初始化流程。`open_in_current === "1"` 强制 `_self`；关闭时优先使用数据或明确配置的 target，仍未提供则回退 `_self`，不按 user-agent 猜测。

## 4. 单一状态和派生值

状态只存源数据，不重复保存可以计算的值：

```js
{
  selectedCatId: '',
  keywords: '',
  sortKey: 'default',
  layout: 'grid',
  page: 1,
  pageSize: 12,
  total: 0,
  items: [],
  status: 'idle',
  requestId: 0
}
```

以下值在请求或渲染时派生：

- `queryCatIds`：由 `selectedCatId`、分类树和后台允许 ids 计算。
- `order`：由经过白名单校验的排序配置生成 JSON 字符串。
- `totalPages`：`Math.ceil(total / pageSize)`。
- `activePath`：由当前分类及祖先链计算。

不要同时保存 `selectedCatId` 和已经展开的逗号分类字符串为同一个字段；这会污染 URL 和 UI 选中状态。

## 5. 数据请求边界

列表共用参数统一组装，再交给当前适配器扩展：

```js
{
  website_id: localStorage.getItem('websiteId'),
  cat_id: queryCatIds.join(','),
  keywords: state.keywords,
  page: state.page,
  page_size: state.pageSize,
  order: buildOrder(state.sortKey, config)
}
```

只发送非空可选参数。分类配置为空/未传且没有后台允许 ids 时，`queryCatIds` 为空并省略 `cat_id`，表示当前适配器的全部数据；存在允许 ids 时，先递归展开 `allowedScopeIds`，空分类选择使用展开结果，代表“全部允许范围”，不是全站全部数据。不得自动使用首个分类 id。

实际确认响应为：

```js
res.data = {
  data: [
    {
      id: 1404,
      title: 'asdfasdfad',
      thumbnail: {
        id: 0,
        url: 'https://static.ltdcdn.com/assets/images/no-image.jpg'
      },
      new_price: '',
      price: '120.00',
      price_ceiling: '0.00',
      defined_link: null,
      detail_url: 'http://fdfdf/goods/1404'
    }
  ],
  total: 3,
  page_size: '12',
  current_page: 1
};
```

因此 `res.data.data` 必须作为一等适配路径，同时保留其他项目常见的 `data.list`、`data.rows` 或直接数组适配。分页集中读取 `total/page_size/current_page`，字符串页大小须安全转为数字。字段、图片、价格和链接规则见 [`list-response.md`](list-response.md)。

## 6. 渲染边界

- 接口对象先归一化为卡片模型，再渲染。
- 价格统一按 [`price-format.md`](price-format.md) 在适配器内生成最终文案，销售价和市场价共用同一函数；默认 DOM 各使用一个文本节点并直接设置 `textContent = priceText`，渲染层和 CSS 不再添加任何货币符号。
- 分类名、产品标题、摘要、图片属性和链接不得直接拼接未经转义的数据。
- 优先使用 DOM API 和 `textContent`；若为性能批量生成 HTML，必须优先使用 ES6 模板字面量代替字符串 `+` 拼接，并先对文本、属性和 URL 分别转义/校验，再统一写入 `innerHTML`。
- 不猜测 `/goods/{id}`、`/product/{id}` 等详情路由。只使用 `defined_link`、`detail_url`、接口明确字段或用户给定规则。
- `target` 由配置明确决定；不根据 user-agent 自动把 PC 强制改为 `_blank`。
- 产品渲染失败不应破坏分类和工具栏；单个坏数据降级为局部占位。

## 7. 事件绑定

- 分类、分页、卡片操作均优先使用根节点事件委托，并且只绑定一次。
- 分类树重新渲染后不要再次给同一容器添加 click 监听。
- 窗口 `resize/popstate` 若需要，保存 handler 引用并提供销毁路径；不要在每次分类重绘时重复绑定。
- 不在生产代码保留接口完整响应、产品数据或依赖加载状态的 `console.log`。

## 8. 不继承的实现

以下内容来自参考模块但不是实现精髓，不能作为默认规则：

- Less 编译器和整套设计 token。
- GSAP 依赖、骨架动画和固定 500ms 人工等待。
- 全局 `document.querySelectorAll` 动画选择器。
- 行内 `style.display` 驱动全部状态。
- 固定详情路由、固定 URL 前缀和 user-agent 打开方式判断。
- `loading === true` 时直接 return 并丢弃用户的新操作。
