# 列表接口响应契约

本文记录已经确认的产品/商品列表响应结构。实现时先适配本契约，再按项目需要兼容其他历史结构。

## 目录

- [已确认结构](#1-已确认结构)
- [分页提取](#2-分页提取)
- [列表字段映射](#3-列表字段映射)
- [图片规则](#4-图片规则)
- [价格规则](#5-价格规则)
- [链接与类型边界](#6-链接与类型边界)
- [验收样例](#7-验收样例)

## 1. 已确认结构

接口业务响应的列表位于 `response.data.data`：

```js
{
  code: 0,
  msg: '',
  data: {
    data: [
      {
        id: 1404,
        title: 'asdfasdfad',
        thumbnail: {
          id: 0,
          duration: 0,
          url: 'https://static.ltdcdn.com/assets/images/no-image.jpg',
          thumbnail: 'https://static.ltdcdn.com/assets/images/no-image.jpg'
        },
        cat_id: 90,
        abstract: '',
        new_price: '',
        price: '120.00',
        price_ceiling: '0.00',
        created_at: '2017-08-02 10:52:20',
        updated_at: '2021-04-14 21:11:48',
        defined_link: null,
        detail_url: 'http://fdfdf/goods/1404',
        tags: []
      }
    ],
    total: 3,
    page_size: '12',
    current_page: 1
  }
}
```

注意：

- 外层 `data` 是分页对象，内层 `data` 才是列表数组。
- `page_size` 可能是字符串，不能假设所有分页字段都是 number。
- `code === 0` 是该响应的成功状态；仍应先验证 `data` 类型，不能因为成功码正确就直接解引用。
- 一条坏数据只能降级当前卡片，不能阻塞其他卡片和分页。

## 2. 分页提取

使用集中适配器提取数组和分页值：

```js
const readBoundedInteger = (value, fallback, min, max) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return fallback;
  return Math.min(max, Math.max(min, Math.floor(number)));
};

const pickConfirmedListPayload = (response) => {
  const payload = response && response.data && typeof response.data === 'object'
    ? response.data
    : {};

  return {
    items: Array.isArray(payload.data) ? payload.data : [],
    total: readBoundedInteger(payload.total, 0, 0, 1000000000),
    pageSize: readBoundedInteger(payload.page_size, 12, 1, 100),
    currentPage: readBoundedInteger(payload.current_page, 1, 1, 1000000000)
  };
};
```

对于示例响应，结果必须是：

```js
{
  items: [/* 3 项 */],
  total: 3,
  pageSize: 12,
  currentPage: 1
}
```

若项目还存在 `data.list`、`data.rows` 或直接数组等旧结构，只能在同一个响应适配器内增加有序回退，不能把结构判断散落在渲染器中。已确认的 `response.data.data` 应作为首要路径。

## 3. 列表字段映射

| 接口字段 | 统一模型 | 规则 |
| --- | --- | --- |
| `id` | `id` | 转为稳定字符串或项目统一 ID 类型 |
| `title` | `title` | 非字符串时回退空字符串 |
| `abstract` | `summary` | 空字符串表示没有摘要，隐藏摘要区域 |
| `cat_id` | 分类 ID | 用于匹配分类名称；不能当标题直接显示 |
| `thumbnail.url` | `imageUrl` | URL 有效即可使用，不依赖 `thumbnail.id` |
| `price` | `priceText` 的金额来源 | 当前响应为元单位十进制字符串，不除以 100 |
| `price_ceiling` | 可选价格区间上限 | 不是市场价或原价 |
| `new_price` | 未确认的可选价格字段 | 空值忽略；非空语义未确认前不得覆盖 `price` |
| `defined_link` | 首选动态链接 | `null` 或非法时继续回退 |
| `detail_url` | 动态链接回退 | 通过安全 URL 校验后使用 |
| `tags` | `badges` 的可选来源 | 仅数组有效，逐项归一化 |
| `created_at` / `updated_at` | 可选元数据 | 只在设计需要时展示 |

不要把接口原始对象直接交给模板。两个适配器都先输出统一卡片模型。

## 4. 图片规则

示例中 `thumbnail.id` 为 `0`，但 `thumbnail.url` 是有效的缺省图地址。因此：

1. 优先校验并使用 `thumbnail.url`，不要求 `thumbnail.id > 0`。
2. `thumbnail.url` 不可用时，再校验 `thumbnail.thumbnail`。
3. 两者都不可用时才使用模块自己的占位状态。
4. 不根据 `thumbnail.id === 0` 隐藏图片。
5. 不修改或重新拼接接口返回的图片处理参数；例如含 `??imageMogr2` 的地址应按原始有效 URL 使用或回退，不自行“修复”。

## 5. 价格规则

该已确认响应中的 `price` 是元单位的十进制金额字符串，例如：

- `'0.00'` → 有效零价格，默认格式化为 `¥0.00`。
- `'120.00'` → `¥120.00`，不能除以 100 变成 `¥1.20`。
- `''`、`null`、`undefined` 或非法文本 → 无价格。

`price_ceiling` 是区间上限，不是划线市场价：

- `'0.00'` 表示没有有效上限，隐藏区间上限。
- 大于 `price` 且设计明确支持价格区间时，可生成一个最终文本，例如 `¥120.00–200.00`。
- 不支持区间时忽略 `price_ceiling`。
- 绝不能把 `price_ceiling` 写入 `marketPriceText`，否则会错误显示灰色划线 `¥0.00`。

`marketPriceText` 只有在响应存在语义明确的 `market_price`、`original_price` 或项目已确认的等价字段时才生成；本响应没有此类字段，所以默认必须为空。

`new_price` 在当前样例中为空。空值不能覆盖 `price`；其非空业务语义得到真实接口说明前，不把它猜成销售价、市场价或促销价。

最终价格仍遵循 [`price-format.md`](price-format.md) 的单一符号与单一文本节点合同。

## 6. 链接与类型边界

- `defined_link` 为安全有效 URL 时优先使用。
- `defined_link` 为 `null`、空值或非法 URL 时，回退到经过校验的 `detail_url`。
- 两者均无效时，卡片保持不可点击。
- 不从 `detail_url` 中的 `/goods/` 或 `/product/` 反推 `moduleType`。
- `moduleType` 只由分类配置决定；`product` 与 `goods` 仍分别选择各自适配器和接口。

## 7. 验收样例

- 三条示例数据被提取为 3 个卡片，`total=3`、`pageSize=12`、`currentPage=1`。
- `thumbnail.id=0` 的两条数据仍显示 `thumbnail.url` 指向的缺省图。
- `price='0.00'` 正常显示零价格。
- `price='120.00'` 保持 120 元，不执行分转元。
- `price_ceiling='0.00'` 不生成价格区间，也不生成灰色划线市场价。
- `new_price=''` 不覆盖 `price`。
- `defined_link=null` 时使用通过安全校验的 `detail_url`。
- `tags=[]`、空摘要或缺失可选字段不会产生 `undefined`、报错或阻塞列表。
