# 文章接口与响应

## 默认接口

- 分类：`GET /api/gatewayCms/articles/category`
- 列表：`GET /api/gatewayCms/articles/list`
- 详情：`GET /api/gatewayCms/articles/item/{id}`，列表默认不预取详情

优先使用宿主页面的 `r(url, data, method)`。不要写入 localhost 代理、固定网站域名或测试请求头。

## 列表参数

| 参数 | 来源 | 规则 |
| --- | --- | --- |
| `mold_types` | `$[cat.type]` | 分类和列表保持一致 |
| `cat_ids` | 当前分类查询范围 | 空配置时省略 |
| `page` | 实例 state | 从 1 开始 |
| `page_size` | `$[cat.pageSize]` | 有限整数，建议限制 1–100 |
| `keywords` | 搜索 state | 空时省略 |
| `sort_by` | `$[cat.sortColumn]` | 合法字段名或 `table.field` |
| `sort` | `$[cat.sortDirection]` | 仅 `asc/desc` |
| `language_type` | 当前归一化语言 | 与界面语言一致 |

已确认文章排序预设包括：

`published_at`、`sort`、`views`、`created_at`、`updated_at`。

允许平台自定义字段，但必须符合：

`^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$`

## 主响应

已确认的列表容器：

```js
{
  code: 0,
  data: {
    data: [],
    total: 0,
    page_size: 12,
    current_page: 1
  }
}
```

把字符串分页值转成有限整数。仅在一个响应适配器中按顺序回退历史结构，渲染器只接收统一模型。

## 已确认的列表项

用户提供的真实列表项包含以下字段：

| 字段 | 已确认类型 | 列表用途 |
| --- | --- | --- |
| `id` | string | 列表 key 与详情路径 |
| `cat_id` | number/string | 当前文章分类 ID |
| `type` / `mold` | number/string | 返回项的文章类型 |
| `title` | string | 标题 |
| `thumbnail` | media object | 主封面 |
| `file` | media object | 媒体或封面回退 |
| `source` / `source_url` | string | 来源名称与来源链接 |
| `author` | string | 作者 |
| `abstract` | string | 摘要 |
| `seo_title/seo_keywords/seo_description` | string | SEO 元数据，默认不显示 |
| `sort` | number/string | 排序值 |
| `is_recommended` | number/boolean | 推荐标识 |
| `created_at/updated_at/published_at` | string | 时间字段 |
| `website_id/language_type` | number/string | 站点与语言元数据 |
| `original_application` | number/string | 来源应用元数据 |
| `share_copy` | nullable | 分享文案 |
| `is_person/status/user_id/block_id/open_comment/ai_status` | mixed | 状态元数据 |
| `original_url` | string | 原始来源地址 |
| `content` | string | 完整 HTML 正文 |
| `info.extension_field` | object/null | 扩展字段 |
| `views` | number/string | 浏览量 |

媒体对象已确认包含：

```js
{
  id: 0,
  is_image: 0,
  width: 0,
  height: 0,
  duration: 0,
  url: "https://...",
  thumbnail: "https://...",
  vod_video_id: ""
}
```

## 关键归一化

- `id` 示例为 `"5742874609370519"`，接口类型明确为字符串。该示例当前仍在 JavaScript 安全整数范围内，但仍须执行 `String(raw.id)` 并保持原字符串，以兼容前导零、未来更大 ID 和后端字符串标识语义；禁止无意义的 `Number`、`parseInt`、一元 `+`、数学运算或数值排序。
- React/Vue key、DOM `data-id`、Map key、URL 参数和详情路径都使用同一个完整字符串 id。
- `cat_id` 是文章行所属分类，不是配置允许范围。需要显示分类名称时，用 `String(cat_id)` 查询分类树 Map。
- `type` 与 `mold` 是返回项元数据；请求仍由 `cat.type` 生成 `mold_types`。可以校验或记录不一致，但不能让单条记录切换整个数据源。
- 文本把 `null/undefined` 归一为空字符串；日期为空或非法时隐藏，不直接调用 `split()`。
- 封面按 `thumbnail.url` → `thumbnail.thumbnail` → `file.url` → `file.thumbnail` 回退。媒体 `id === 0` 或 `is_image === 0` 时 URL 仍可能是有效缺省图，不能据此丢弃。
- `info.extension_field` 可能为 `null`。用安全点路径读取；只有兼容已确认旧项目时才回退 `article_info.extension_field`。
- `content` 是可能很长的 HTML 正文。列表默认只用 `abstract`，不得把 `content` 直接插入 `innerHTML`，也不得默认请求详情来补充正文。
- 用户明确要求正文片段时，优先使用服务端摘要；必须处理 HTML 时使用平台可信净化器或经过验证的净化流程，再限制文本长度。
- `source_url` 和 `original_url` 是来源链接，不是文章详情地址。仅在用户明确要求“查看来源”时单独渲染并执行协议校验。
- 当前真实项没有 `article_cat`、`article_info`、`defined_link` 或 `detail_url`，这些字段不得作为默认依赖。

## 详情链接

1. 有非空 id 时生成 `/article/${encodeURIComponent(String(id))}`。
2. id 缺失时渲染不可点击卡片，不生成 `/article/undefined`。
3. 后续若真实列表响应新增详情字段，再在响应适配器中校验并明确调整优先级；不要从 `source_url/original_url` 推断详情链接。
