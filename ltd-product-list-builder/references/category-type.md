# LTD 分类类型与点号语法

分类配置的 key 可以按模块命名。本 Skill 统一使用 `cat_id`；下表中的 `$[cat]` 对应模块里的 `$[cat_id]`。任何分类选择配置都必须使用平台类型 `input_type: "category"`。

`category` 是配置控件类型，不是配置 key，也不是业务类型。当前产品/商品列表只处理两个 `moduleType`：`product` 表示产品，`goods` 表示商品；不得把它们写进 `input_type`。

## 目录

- [标准输出](#1-标准输出)
- [推荐读取方式](#2-推荐读取方式)
- [排序参数](#3-排序参数)
- [HTML 数据桥接](#4-html-数据桥接)
- [旧环境兼容](#5-旧环境兼容)
- [配置 JSON 与运行时](#6-配置-json-与运行时的区别)

## 1. 标准输出

| 语法 | 运行时输出 | 用途 |
| --- | --- | --- |
| `$[cat_id]` | `1837,2066` | 选中的分类 ID，逗号分隔 |
| `$[cat_id.moduleType]` | `product` | 当前只允许 `product / goods` |
| `$[cat_id.type]` | `1` | 当前业务的细分类型 |
| `$[cat_id.pageSize]` | `10` | 每页条数 |
| `$[cat_id.sortColumn]` | `published_at` | 排序字段，允许业务自定义字段 |
| `$[cat_id.sortDirection]` | `desc` | `desc / asc` |

关键规则：`$[cat_id]` 的标准输出是 ID 字符串，不是完整 JSON 对象。只有配置导入 JSON 中的 `value/default_value` 才保存字符串化对象。

`$[cat_id]` 为空字符串、未传或未替换后被安全读取器判定为缺失时，语义都是“不限制分类”。列表请求省略 `cat_id` 或按当前接口要求传空字符串，从已经确定的 product/goods 适配器获取全部数据；不能自动选择第一个分类。这里的“全部”只针对当前业务体系，不同时请求产品与商品。

## 2. 推荐读取方式

```js
const rawCategory = {
  ids: '$[cat_id]',
  moduleType: '$[cat_id.moduleType]',
  type: '$[cat_id.type]',
  pageSize: '$[cat_id.pageSize]',
  sortColumn: '$[cat_id.sortColumn]',
  sortDirection: '$[cat_id.sortDirection]'
};
```

对每个字段分别做未替换占位符检测和类型转换：

- `ids`：按逗号拆分、trim、去空、去重，保留字符串 id。
- `moduleType`：只接受精确值 `product` 或 `goods`。`shopGoods` 不是类型，不做归一化。通用模块必须由本字段直接选择适配器、分类接口和列表接口，不能被预先写死的 URL 覆盖。
- `type`：允许 `"1"` 或空字符串；作为业务细分类型保留，只有接口明确需要且非空时才发送。
- `pageSize`：转换为整数并限制在 `1–100`。
- `sortColumn`：允许平台产生的自定义字段，不维护固定字段白名单；限制长度、拒绝控制字符。
- `sortDirection`：只接受 `asc/desc`，否则使用安全默认值。

## 3. 排序参数

自定义排序字段不能通过字符串拼接生成 JSON：

```js
const buildDefaultOrder = (column, direction) => {
  if (!column) return '';
  const order = {};
  order[column] = direction === 'asc' ? 'asc' : 'desc';
  return JSON.stringify(order);
};
```

这样既支持 `published_at`、`updated_at`、`sort` 及业务自定义字段，也避免破坏 JSON 结构。

## 4. HTML 数据桥接

不需要在 JavaScript 字符串中读取时，可以通过数据属性桥接：

```html
<div class="pl-category-data"
     data-ids="$[cat_id]"
     data-module-type="$[cat_id.moduleType]"
     data-type="$[cat_id.type]"
     data-page-size="$[cat_id.pageSize]"
     data-sort-column="$[cat_id.sortColumn]"
     data-sort-direction="$[cat_id.sortDirection]"
     hidden></div>
```

随后从当前模块根节点读取 `dataset`。桥接元素必须位于当前实例内，不能使用固定 id。

## 5. 旧环境兼容

只有确认旧项目会把 `$[cat_id]` 输出为完整 JSON 时才提供兼容：

1. 先读取六个标准点号字段。
2. 当 `$[cat_id]` 以 `{` 开始时，尝试解析旧对象。
3. 点号字段有效时优先点号字段，旧对象只补缺失项。
4. 若 `$[cat_id]` 是普通逗号 ID，绝不执行 `JSON.parse`。
5. 解析失败回退空 ids；`moduleType` 缺失时使用本次交付明确默认值，不能随机猜测或同时请求两套接口。

新模块不得把“完整 JSON 解析”作为主流程，也不要同时生成 `cat_id` 和语义重复的 `category` 配置 key。

## 6. 配置 JSON 与运行时的区别

真实商品分类配置可以使用：

```json
{
  "key": "cat_id",
  "label": "分类选择",
  "value": "{\"moduleType\":\"goods\",\"type\":\"1\",\"ids\":\"165567,212865,212869,212867,169069,190933,212861,212863\",\"names\":[\"客厅\",\"客厅-1\",\"客厅-1-1\",\"客厅-2\",\"餐厅\",\"test\",\"test-1\",\"test-1-1\"],\"pageSize\":12,\"sortColumn\":\"sort\",\"sortDirection\":\"asc\",\"sortColumnVersion\":2}",
  "default_value": "{\"moduleType\":\"goods\",\"type\":\"\",\"ids\":\"\",\"names\":[],\"pageSize\":12,\"sortColumn\":\"sort\",\"sortDirection\":\"asc\"}",
  "input_type": "category"
}
```

这是后台存储结构，不代表 `$[cat_id]` 在模块运行时输出整段对象。

- `ids` 是逗号分隔字符串，顺序按编辑器选择结果保留；每个 id 始终按字符串处理。
- `names` 是编辑器展示元数据，与 ids 通常按索引对应，可包含 `客厅-1-1` 这类层级显示名。运行时分类名称仍以分类接口为准，不用 names 代替 id 或重建分类树。
- `names` 缺失、数量与 ids 不一致或存在重复时不能阻塞运行；保留有效项，筛选仍只使用清洗后的 ids。
- `sortColumnVersion` 是分类控件的可选版本元数据。维护现有配置时原样保留；新编辑器生成 `2` 时不要删除、改写或作为 `$[cat_id.sortColumnVersion]` 的必需运行时字段。
- `sortColumnVersion` 不写入列表请求，不参与 `order`，也不生成独立配置项。它可能只存在于 `value`，而 `default_value` 没有该字段，这是有效结构。
- `type` 允许当前值为 `"1"`、默认值为空；空值表示不附加具体细分类型参数。

运行时以有效 `moduleType` 选择接口：配置是 `product` 就调用产品接口并使用其中的产品分类 ids，配置是 `goods` 就调用商品接口。只有人工把一份已有配置从 product 迁移为 goods 或反向迁移时，才必须清空原体系的 `ids/names/type`；正常运行时不能因为旧代码写死了另一接口而丢弃当前有效分类。

交付前检查分类根配置项只有一个，且其 `input_type` 严格等于 `category`；`cat_id.moduleType`、`cat_id.pageSize` 等点号子字段不能作为独立配置项输出。
