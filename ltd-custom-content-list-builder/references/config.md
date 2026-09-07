# 自定义内容配置

完整基线见技能根目录 `自定义内容列表配置.json`。

- `cat`：`input_type: "category"`。
- `i18n`：key 和 input_type 都是 `i18n`。
- 配置开关控制分类、全部、搜索、图片、摘要、内容、动态字段和分页。
- `attr_keys` 是逗号分隔的动态字段 key/name/id；为空时不额外显示 attrs。

配置逐项容错：

- 未替换 `$[` 回退默认。
- switch 显式识别开关。
- number 检查有限值和范围。
- category 子字段分别回退。
- attr_keys 去空白、去重并限制数量。
- i18n 异常回退内置中文。

交付时确保每个占位符根 key 在 JSON 中唯一存在，cat/i18n 内嵌字符串均可再次解析。
