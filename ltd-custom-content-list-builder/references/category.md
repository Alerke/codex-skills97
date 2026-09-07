# 自定义内容分类

默认配置：

```json
{
  "moduleType": "customContent",
  "type": "1",
  "ids": "",
  "names": [],
  "pageSize": 12,
  "sortColumn": "sort",
  "sortDirection": "asc",
  "sortColumnVersion": 2
}
```

- `input_type` 固定为 `category`。
- 分类接口 `/api/website/customizedContentCat`。
- `type: "1"` 是分类控件兼容元数据，不发送给列表接口。
- 节点按 `id/name/title/children` 归一化。
- 后台允许父级时包含自身和所有后代。
- 选择父级或“全部允许范围”时，将展开后的 IDs 作为 `cat_id` 逗号字符串。
- ids 为空表示全部自定义内容，不自动选择第一分类。
