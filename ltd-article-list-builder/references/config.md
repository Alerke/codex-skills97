# 配置与容错

## 可导入基线

根配置默认包含：

- `cat`：文章分类与 type，`input_type: "category"`。
- `i18n`：六语言文案，`input_type: "i18n"`。
- 分类、搜索、封面、摘要、日期、分类名、作者、浏览量和分页开关。
- “全部”按钮开关。
- 栏数、图片比例和必要颜色。

完整基线见技能根目录 `文章列表配置.json`。

## 配置读取

每个配置项独立使用归一化函数：

- 未替换占位符：匹配 `$[` 后回退默认值。
- switch：显式识别开/关值，不使用 `Boolean(raw)`。
- number：`Number()` 后检查 `Number.isFinite`，再限制范围。
- color：仅接受安全 CSS 颜色格式；错误时回退默认色。
- ratio：只接受有限正数 `w/h` 或预设值。
- string：去除危险控制字符，保留合理长度。
- category：各子字段分别回退，单个错误不覆盖整个对象。
- i18n：运行时对象错误时回退内置中文。

不要用一个大 `try/catch` 包住整个初始化，也不要空 catch 后留下半初始化界面。

## 分类基线

```json
{
  "moduleType": "article",
  "type": "1",
  "ids": "",
  "names": [],
  "pageSize": 12,
  "sortColumn": "published_at",
  "sortDirection": "desc",
  "sortColumnVersion": 2
}
```

- `ids` 为空表示当前文章 type 的全部数据。
- `names` 是编辑器展示元数据，运行时筛选只信任 IDs。
- `sortColumnVersion` 原样保留，不发送给接口。
- 切换 type 时编辑器应清空原类型不兼容的 ids/names；运行时不得擅自迁移分类。

## 占位符核对

交付前收集 HTML 中所有 `$[root]` 和 `$[root.field]`：

1. 每个 root 在 JSON 中恰好存在一次。
2. JSON 中每个 key 在代码中实际使用，或明确作为编辑器配置保留。
3. 点号字段不生成独立 JSON 项。
4. `cat.value/default_value` 与 `i18n.value/default_value` 均可再次 `JSON.parse`。
