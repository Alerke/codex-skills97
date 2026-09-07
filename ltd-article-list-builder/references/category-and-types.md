# 文章分类与类型

## 分类配置

`input_type: "category"` 的导入值是 JSON 字符串，运行时通过点号语法读取：

| 语法 | 含义 |
| --- | --- |
| `$[cat]` | 选中分类 ID，逗号分隔 |
| `$[cat.moduleType]` | 固定为 `article` |
| `$[cat.type]` | 文章细分类型，映射到 `mold_types` |
| `$[cat.pageSize]` | 每页数量 |
| `$[cat.sortColumn]` | 排序字段 |
| `$[cat.sortDirection]` | `asc` 或 `desc` |

不要执行 `JSON.parse($[cat])`。`$[cat]` 已经是 ID 字符串。

## 已知 type

| type | 编辑器名称 | 请求参数 |
| --- | --- | --- |
| `1` | 文章 | `mold_types=1` |
| `2` | 视频 | `mold_types=2` |
| `12` | 图册 | `mold_types=12` |
| `19` | 图文 | `mold_types=19` |
| `11` | 公告通知 | `mold_types=11` |
| `10` | 最新活动 | `mold_types=10` |
| `6` | 常见问题 | `mold_types=6` |
| `5` | 业务知识 | `mold_types=5` |
| `7` | 官方招聘 | `mold_types=7` |
| `8` | 媒体报道 | `mold_types=8` |

各类型的默认标题、卡片展示重点与字段边界见 [`article-type-profiles.md`](article-type-profiles.md)。

未知非空 type 不应静默改成 `1`。在当前实例显示配置错误，避免请求错误内容类型。缺失或未替换时才使用交付配置中的明确默认 type。

## 分类树

分类接口：

`GET /api/gatewayCms/articles/category?mold_types={type}`

节点至少按以下兼容字段归一化：

- `id`
- `name`，缺失时回退 `title`
- `children`，非数组时回退 `[]`

创建 `Map<string, node>` 与父子关系：

1. 递归遍历完整分类树。
2. 把后台允许的分类 IDs 展开为自身和全部后代，得到 `allowedScopeIds`。
3. UI 只展示允许范围内的节点；只配置子节点时，可把该子节点提升为可见入口。
4. 选择父级时，再递归展开为本次请求的 `queryCatIds`。
5. “全部”在有限范围内发送 `allowedScopeIds`；配置为空时省略 `cat_ids`，表示当前 type 全量。

不得只合并直接 children，也不得因为隐藏“全部”按钮就自动选中第一个分类。
