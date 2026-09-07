# 案例分类

默认导入值：

```json
{
  "moduleType": "case",
  "type": "1",
  "ids": "",
  "names": [],
  "pageSize": 12,
  "sortColumn": "updated_at",
  "sortDirection": "desc",
  "sortColumnVersion": 2
}
```

- `input_type` 固定为 `category`。
- `$[cat]` 输出 ID 字符串；点号字段共享一个 `cat` 根配置项。
- `type: "1"` 是非文章分类控件的兼容元数据，不等于文章 type，也不发送到案例接口。
- 分类接口 `/api/gatewayCms/case/category` 返回树；节点按 `id/name/title/children` 归一化。
- 后台限定父分类时，允许范围包含父级和全部深度后代。
- 选择父级时把展开后的 IDs 以逗号字符串传给 `cat_id`。
- ids 为空表示全部案例；存在允许范围时“全部”只查询该范围。
- `show_all_button=0` 不得自动选择第一分类。
