# 案例接口与响应

## 接口

- `GET /api/gatewayCms/case/category`
- `GET /api/gatewayCms/case/list`
- `GET /api/gatewayCms/case/detail?id={id}` 只在需要详情数据时调用

列表常用参数：

| 参数 | 说明 |
| --- | --- |
| `cat_id` | 一个或多个案例分类 ID，逗号分隔 |
| `page` | 页码 |
| `page_size` | 每页数量 |
| `order` | JSON 字符串，例如 `{"updated_at":"desc"}` |

## 已确认主结构

```js
{
  code: 0,
  data: {
    data: {
      data: [],
      total: 0,
      page_size: 12,
      current_page: 1
    }
  }
}
```

响应适配器按顺序提取：

1. `response.data.data.data` 为数组。
2. 历史结构中 `response.data.data` 直接为数组。
3. 其他结构显示局部数据错误，不在渲染器中散落回退判断。

已观察的列表字段包括 `id/title/abstract/thumbnail/detail_link/cat_id/sort/is_recommended/created_at/updated_at`，但每个字段仍按可选值处理。

- `thumbnail.url` 有效时显示，不以媒体 id 单独判断。
- `detail_link` 必须经过协议校验。
- 没有安全响应链接且 id 存在时使用 `/case/${encodeURIComponent(String(id))}`。
- `detail_link`、`defined_link`、默认详情路径都不存在时渲染不可点击卡片。
- `total/page_size/current_page` 转成有限非负整数。
