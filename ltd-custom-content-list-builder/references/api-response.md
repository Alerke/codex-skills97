# 自定义内容接口与响应

## 接口

- 分类：`GET /api/website/customizedContentCat`
- 列表：`GET /api/gatewayCms/getCustomizedContentList`

已观察的列表参数：

`cat_id`、`page`、`page_size`、`keywords`、`sort_by`、`sort`、`language_type`。

不要发送 `mold_types`、商品 order 结构或案例详情参数。

## 响应

已确认列表常用结构：

```js
{
  code: 0,
  data: {
    data: []
  }
}
```

如响应同时提供 `total/page_size/current_page`，安全转为有限整数；没有分页元数据时，不虚构总页数，按实际列表长度或接口能力选择“无分页/加载更多”。

常见字段：

| 字段 | 规则 |
| --- | --- |
| `id` | 保持字符串标识语义 |
| `cat_id` | 用分类树 Map 映射名称 |
| `title` | 文本 |
| `abstract` | 摘要文本 |
| `content` | 可能是 HTML，默认不直接注入 |
| `images` | 图片集合，常见 URL 为 `item.image.url` |
| `defined_link` | 安全有效时才可点击 |
| `attrs` | 动态属性集合 |
| `sort` | 排序值 |
| `created_at/updated_at` | 可选时间 |

字段样本未确认前，不假设 `images[0]`、attrs 名称或 content 格式一定存在。
