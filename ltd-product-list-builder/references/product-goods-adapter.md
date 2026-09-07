# 产品与商品数据适配层

产品 `product` 与商品 `goods` 共用列表内核，但使用不同接口并拥有不同业务字段。正确结构是“一套 UI/状态机 + 两个轻量数据适配器”，不是复制两份产品列表代码。

## 目录

- [共用能力](#1-共用能力)
- [体系映射](#2-体系映射)
- [适配器接口](#3-适配器接口)
- [共用卡片模型](#4-共用卡片模型)
- [共用字段](#5-共用字段)
- [产品差异](#6-产品差异)
- [商品差异](#7-商品差异)
- [分类差异](#8-分类差异)
- [参数差异](#9-参数差异)
- [详情链接](#10-详情链接)
- [能力开关](#11-能力开关)
- [验收矩阵](#12-验收矩阵)

## 1. 共用能力

以下能力完全共用：

- `cat_id` 六个分类占位符和限定分类树。
- 关键词、分类、排序、页码、每页数量和 URL 状态。
- loading、success、empty、error、重试和最新请求优先。
- 卡片容器、图片、标题、副标题、价格槽位和点击操作。
- 分页窗口、跳页、多语言、多实例和安全渲染。
- `website_id`、`language_type`、`page`、`page_size`、`keywords`、`cat_id`、`order` 等基础请求参数。

这些逻辑只能实现一次。

## 2. 体系映射

| 项目 | 产品 `product` | 商品 `goods` |
| --- | --- | --- |
| 平台 `moduleType` | `product` | `goods` |
| API 路径命名 | `product` / `productCat` | `shopGoods`（不是 moduleType） |
| 分类接口 | `/api/common/productCat?format=tree` | `/api/gatewayCms/shopGoods/category` |
| 列表接口 | `/api/gatewayCms/product/getProductList` | `/api/gatewayCms/shopGoods/getShopGoodsList` |
| 详情数据接口 | `/api/website/noAuthProductDetail/{id}` | `/api/gatewayCms/shopGoods/item/{id}` |
| 默认语义 | 展示型产品、方案、工业产品 | 可交易商品、库存、销量 |

`shopGoods` 只存在于商品 API 路径或后端命名中，不是分类控件 `moduleType`。配置 JSON 只能使用 `goods`。

每次模块交付都先读取 category `moduleType`：

- `product` 选择产品适配器。
- `goods` 选择商品适配器。
- 类型缺失或占位符未替换时才使用本次交付明确的 `DEFAULT_MODULE_TYPE`。
- 类型有效时不得被代码中原有的固定接口覆盖；旧代码写死了另一体系接口时，应改为从适配器取 URL。

配置为产品但旧代码调用商品接口，或配置为商品但旧代码调用产品接口，都是实现错配。正确处理不是保留固定接口，而是让有效类型选择对应适配器，使分类配置和请求接口自动保持一致。

## 3. 适配器接口

初始化时只归一化一次类型，再从适配器表取所有接口信息：

```js
const DEFAULT_MODULE_TYPE = 'product';
const adapters = {
  product: createProductAdapter({
    categoryUrl: '/api/common/productCat?format=tree',
    listUrl: '/api/gatewayCms/product/getProductList'
  }),
  goods: createGoodsAdapter({
    categoryUrl: '/api/gatewayCms/shopGoods/category',
    listUrl: '/api/gatewayCms/shopGoods/getShopGoodsList'
  })
};

const isPlaceholder = (value) => (
  typeof value === 'string' && /^\$\[[^\]]+\]$/.test(value.trim())
);

const readModuleType = (value, fallback) => {
  if (value === undefined || value === null || value === '' || isPlaceholder(value)) {
    return fallback;
  }
  return value === 'product' || value === 'goods' ? value : '';
};

const moduleType = readModuleType(categoryConfig.moduleType, DEFAULT_MODULE_TYPE);
const adapter = adapters[moduleType];
if (!adapter) {
  renderConfigError();
  return;
}

requestCategories(adapter.categoryUrl, adapter.buildCategoryParams(state, categoryConfig));
requestList(adapter.listUrl, adapter.buildListParams(state, categoryConfig, queryCatIds));
```

| category 类型 | 自动选择的适配器 | 分类接口 | 列表接口 |
| --- | --- | --- | --- |
| `product` | `product` | `/api/common/productCat?format=tree` | `/api/gatewayCms/product/getProductList` |
| `goods` | `goods` | `/api/gatewayCms/shopGoods/category` | `/api/gatewayCms/shopGoods/getShopGoodsList` |

自动判断必须满足：

1. 先读取类型，后创建请求；不能在类型解析前缓存固定列表 URL。
2. 分类和列表必须使用同一个 `adapter`，不得分别通过两套条件判断。
3. 改变配置 `moduleType` 后，不修改 JavaScript 就能切换两组接口。
4. `ids/type` 只传给由同一 category 类型选出的适配器，不自动跨体系映射。
5. 接口响应样例只用于完善对应适配器字段，不能因此把通用模块永久锁定到该接口。
6. 用户明确要求单一产品或单一商品模块时仍可只保留一个适配器，但同步输出的 category 类型必须一致；本产品/商品通用 Skill 默认生成两个适配器。
7. `shopGoods`、`article`、`case`、`customContent` 等非空值在当前 Skill 中均为非法 `moduleType`，不能映射、猜测或静默使用默认适配器。

两个适配器提供相同方法：

```js
{
  kind: 'product',
  categoryUrl: '',
  listUrl: '',
  detailApi: '',
  buildCategoryParams: function (state, config) {},
  buildListParams: function (state, config, queryCatIds) {},
  normalizeSort: function (column, direction) {},
  pickCategories: function (response) {},
  pickItems: function (response) {},
  pickTotal: function (response) {},
  normalizeCategory: function (raw) {},
  normalizeItem: function (raw, config) {},
  capabilities: {}
}
```

通用请求器只接收适配器给出的 URL 和参数；通用渲染器只接收归一化卡片模型。

## 4. 共用卡片模型

两个适配器都输出：

```js
{
  kind: 'product',
  id: '',
  title: '',
  subtitle: '',
  summary: '',
  imageUrl: '',
  imageAlt: '',
  priceText: '',
  marketPriceText: '',
  categoryText: '',
  views: null,
  sales: null,
  stock: null,
  href: '',
  target: '_self',
  badges: []
}
```

- 不存在的能力使用 `null` 或空值，渲染器按存在性隐藏。
- `kind` 只用于能力开关或语义 class，不在每个字段读取处重复分支。
- `raw` 仅在确有扩展需求时保留，不能由模板直接读取未清洗字段。

## 5. 共用字段

两种体系通常都可使用：

- `id`。
- `title`，副标题常为 `sub_title`。
- `thumbnail`，无有效图片时再回退附件或占位图。
- `price`、`market_price`、`price_format`。
- `counter.views`、`counter.sales`，缺失则隐藏。
- 分类 id、附件和可能存在的详情 URL。

已确认的列表响应字段映射见 [`list-response.md`](list-response.md)：数组位于 `response.data.data`；`thumbnail.url` 有效即可使用，即使 `thumbnail.id=0`；`defined_link` 为空时可回退安全的 `detail_url`。

价格统一调用 [`price-format.md`](price-format.md) 的格式化器。`priceText/marketPriceText` 已包含最终货币单位，渲染器不得再加符号；已确认响应中的 `price` 是元单位十进制字符串，不能除以 100，`0` 是有效价格。`price_ceiling` 仅是可选价格区间上限，不能映射为 `marketPriceText`。

## 6. 产品差异

产品适配器可按需处理：

- `abstract`、产品说明或展示摘要。
- `parameter_management_id`、`attr_value`、`attr_flag` 属性筛选。
- `is_recommended` 推荐产品。
- `is_content` 内容字段。
- `is_all_image` 多图。
- `area`、`para`、`is_file` 等产品展示数据。
- 产品创建/更新时间范围。

产品列表默认不显示库存、SKU 或交易按钮。即使响应偶尔出现同名字段，也不能自动变成商品交互。

## 7. 商品差异

商品适配器可按需处理：

- `stock` 库存。
- `status` 上下架状态。
- `mold` 商品形态。
- `is_sku` 与 SKU 数据。
- `is_video` 商品视频。
- `is_url` 商品链接。
- `is_consume_integral` 积分商品。
- `counter.sales`、`counter.reviews`、`counter.favorites`。
- `attrs`、`props` 等商品属性。

商品列表默认仍只负责展示。SKU 选择、加购、收藏和结算是可选交易能力，不能因为 `moduleType=goods` 自动加入。

## 8. 分类差异

- 产品分类接口明确使用 `format=tree`，通常直接得到树形数组。
- 商品分类接口可能直接返回 `children`，也可能需要以 `parent_id=0` 获取顶级后再按项目补子级；先检查真实响应。
- 两者都必须归一化为 `{ id, name, children }` 后交给共用分类树逻辑。
- 后台 `$[cat_id]` 的 allowedIds、子级提升、父级全部层级后代聚合和“全部允许范围”语义完全共用。父级配置先展开为 `allowedScopeIds`，再构造 `queryCatIds`。

## 9. 参数差异

先建立共用基础参数，再由适配器扩展：

```js
const baseParams = {
  cat_id: queryCatIds.join(','),
  keywords: state.keywords,
  page: state.page,
  page_size: state.pageSize,
  order: buildOrder(state.sortKey, config),
  language_type: config.languageType
};

const params = adapter.buildListParams(baseParams, state, config);
```

- 产品适配器不能发送 `stock/mold/is_sku`。
- 商品适配器不能默认发送 `area/para/is_file/is_recommended`。
- 只发送当前功能真正需要的非空参数。

## 10. 详情链接

详情数据接口不等于前台详情页面路由。两个适配器都按以下优先级生成 `href`：

1. 接口明确返回的 `defined_link`、`detail_url`、`url` 等有效字段。
2. 用户明确提供的路由规则。
3. 无法确认时输出不可点击卡片。

不得因为 `product` 猜测 `/product/{id}`，也不得因为 `goods` 猜测 `/goods/{id}`。

## 11. 能力开关

适配器声明能力，通用渲染器据此决定是否显示：

```js
// 示例，不代表必须全部实现
capabilities: {
  summary: true,
  price: true,
  stock: false,
  sales: true,
  sku: false,
  tradeAction: false
}
```

最终显示条件同时满足：适配器支持、用户配置开启、当前数据存在。任何一项不满足都隐藏。

## 12. 验收矩阵

- 同一份 HTML/状态/分页代码分别使用 product 和 goods 配置运行。
- 切换 `moduleType` 后只更换适配器，不改 UI 主流程。
- 两种体系的接口、专属参数和专属字段没有串用。
- 产品不出现库存/SKU/加购，商品不自动出现产品参数/附件展示。
- 两种分类响应都归一化为同一树模型。
- 两种列表响应都归一化为同一卡片模型。
- 已确认的 `data.data` 列表和 `total/page_size/current_page` 分页被正确提取，字符串页大小安全转为数字。
- `thumbnail.id=0` 但 URL 有效时仍显示图片；`price_ceiling=0.00` 不被显示为划线市场价。
- 未确认详情路由时两种卡片都不生成假链接。
