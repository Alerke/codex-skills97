# 产品与商品列表数据

## 目录

- [共用内核与数据差异](#1-共用内核与数据差异)
- [请求参数](#2-请求参数)
- [响应适配](#3-响应适配)
- [字段归一化](#4-字段归一化)
- [安全渲染](#5-安全渲染)
- [状态机和并发](#6-状态机和并发)
- [分类](#7-分类)

## 1. 共用内核与数据差异

| 体系 | 分类接口 | 列表接口 | 默认用途 |
| --- | --- | --- | --- |
| `product` | `/api/common/productCat?format=tree` | `/api/gatewayCms/product/getProductList` | 展示型产品、解决方案、工业产品 |
| `goods` | `/api/gatewayCms/shopGoods/category` | `/api/gatewayCms/shopGoods/getShopGoodsList` | 可交易商品、库存和销量；`shopGoods` 仅是 API 路径命名 |

通用模块必须由 `$[cat_id.moduleType]` 自动选择适配器：`product` 使用产品分类/列表接口，`goods` 使用商品分类/列表接口。当前不接受其他类型；API 路径中的 `shopGoods` 不参与类型判断。分类和列表 URL 都从同一个已选适配器读取，不能保留与类型不一致的固定接口。完整实现见 [`product-goods-adapter.md`](product-goods-adapter.md)。

## 2. 请求参数

共同参数：

```js
{
  website_id: localStorage.getItem('websiteId'),
  cat_id: '',
  keywords: '',
  page: 1,
  page_size: 12,
  order: '',
  language_type: 'zh-cn'
}
```

- `keywords` 是复数。
- `page_size` 使用下划线。
- `order` 是 JSON 字符串，例如 `{"created_at":"desc"}` 或 `{"price":"asc"}`。
- `cat_id` 为空或未传表示不限制分类，省略该参数或按接口约定传空字符串；关键词、价格、属性等可选筛选为空时同样不附加对应参数。
- `product` 可按需增加 `parameter_management_id`、`attr_value`、`attr_flag`、`s_price`、`e_price`、`is_recommended`、`is_all_image`。
- `goods` 可按需增加 `ids`、`stock`、`status`、`mold`、`is_sku`、`is_video`。
- 不把未使用的高级参数全部默认传给接口。

使用平台的 `r(url, data, 'get')`。成功判断以真实接口为准，常见成功码为 `code === 0`。请求头语言应与页面当前语言一致。

## 3. 响应适配

当前已确认结构是 `response.data.data` 列表数组，以及同级的 `total/page_size/current_page`。完整字段契约见 [`list-response.md`](list-response.md)。不同环境也可能把数组放在 `data.list`、`data.rows` 或直接放在 `data`，因此集中写一个有序适配器：

```js
const pickList = (response) => {
  const data = response && response.data;
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.data)) return data.data;
  if (data && Array.isArray(data.list)) return data.list;
  if (data && Array.isArray(data.rows)) return data.rows;
  return [];
};
```

已确认分页值为 `data.total`、`data.page_size` 和 `data.current_page`，其中 `page_size` 可能为字符串，必须转为有限整数并限制范围。总数也可能在旧响应的 `data.count` 或分页对象中。不要用当前列表长度冒充总数；只有接口没有总数且明确采用“加载更多”时，才以返回数量判断是否还有下一页。

## 4. 字段归一化

把接口对象先转换为统一卡片模型，再渲染 DOM：

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

常见字段规则：

- 标题：`title`，副标题：`sub_title`。
- 主图：优先校验 `thumbnail.url`，不依赖 `thumbnail.id`；示例中 `id=0` 仍有有效缺省图。URL 不可用时再校验 `thumbnail.thumbnail`，最后回退模块占位状态。
- 价格：已确认结构的 `price` 是元单位十进制字符串，不除以 100；`price_ceiling` 是区间上限而非市场价，`0.00` 时隐藏。按 [`price-format.md`](price-format.md) 生成包含单位的最终 `priceText/marketPriceText`。数字文本已有货币标识时不得再拼 `price_icon`；HTML/CSS 不得二次添加单位；价格 `0` 不能按 falsy 隐藏。
- 统计：从 `counter.views`、`counter.sales` 读取，缺失时隐藏对应 UI，而不是显示 `undefined`。
- 链接：优先使用接口明确返回的安全 URL 或用户给定的详情页规则；不要凭空猜测详情路由。后台静态点击配置见 [`click-action-type.md`](click-action-type.md)，动态卡片链接见 [`click-action-runtime.md`](click-action-runtime.md)。

## 5. 安全渲染

- 标题、副标题、分类和统计用 `textContent`。
- 图片用 `setAttribute` 设置 `src`、`alt`、`loading="lazy"`、`decoding="async"`。
- 接口动态链接只允许相对地址、`http:`、`https:`、`tel:`、`mailto:`；拒绝 `javascript:`、`data:`、`vbscript:`。平台静态 `none` 和明确 `miniProgram` 的严格 `javascript:jumpMall(...)` 只按点击类型规范处理，不能成为接口 URL 的放行条件。
- `_blank` 链接补 `rel="noopener noreferrer"`。
- 不把接口文本直接拼入 `innerHTML`。若必须渲染富文本，须另行定义白名单净化策略；列表默认不渲染富文本。

## 6. 状态机和并发

统一维护：

```js
const state = {
  keywords: '',
  selectedCatId: '',
  sortKey: 'default',
  page: 1,
  pageSize: 12,
  total: 0,
  status: 'idle',
  requestId: 0
};
```

- 新搜索、新分类或新排序时把 `page` 设为 `1`。
- 每次请求递增 `requestId`，仅允许最后一次请求更新 DOM。
- 请求开始显示 loading；成功后根据数组长度进入 success 或 empty；失败进入 error。
- 搜索输入可在点击或回车时提交。若使用即时搜索，至少加入 250–400ms 防抖。
- 分页切换成功后按设计滚动到模块顶部；不要强制跳到页面顶部。

## 7. 分类

- 分类接口可能返回树形结构；默认只渲染设计所需层级。
- “全部”应清空 `selectedCatId`，不要使用虚构的分类 ID；请求时再回退到后台允许范围。
- 后台未配置任何分类范围时，“全部”表示当前 product/goods 适配器的全部数据；不得自动选中首个分类。
- 后台配置父分类时，先把允许范围展开为该父级自身和全部层级后代；“全部”和父级筛选都发送展开后的 ID 集合，不能只发送原始 `$[cat_id]` 或直接 children。
- `$[cat_id]` 已输出后台限定分类时，不应再请求并展示超出范围的分类。
- 分类切换按钮同步 `aria-pressed` 或选中状态。
- 详细的限定分类提升、父分类后代聚合与 URL 语义见 [`category-tree.md`](category-tree.md) 和 [`state-pagination.md`](state-pagination.md)。
