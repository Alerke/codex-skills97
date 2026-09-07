# 新编辑器配置控件

已确认的 `input_type`：

| 类型 | 用途 | 运行时要点 |
| --- | --- | --- |
| `text` | 单行文本 | 字符串归一化 |
| `textarea` | 多行文本 | 默认按纯文本处理 |
| `number` | 数字 | 有限数字与范围限制 |
| `color` | 颜色 | 只接受合法颜色，写入根 CSS 变量 |
| `switch` | 开关 | 显式识别 1/0/true/false |
| `select` | 下拉选择 | 白名单枚举 |
| `media` | 图片或视频 | 根据实际媒体类型归一化 |
| `image` | 单图 | 兼容 URL、对象和控件对象 |
| `video` | 单视频 | 兼容 URL、对象、封面和媒体属性 |
| `jump` | 点击操作 | 使用 `$[key.href]`、`$[key.target]` 等点号输出 |
| `category` | 分类选择 | 使用 `$[key]` 与点号字段 |
| `i18n` | 多语言 | key 与 input_type 都使用 `i18n` |
| `mediaList` | 混合媒体列表 | JSON 数组，需归一化 |
| `imageList` | 图片列表 | JSON 数组，需归一化 |
| `videoList` | 视频列表 | JSON 数组，需归一化 |
| `navList` | 树形导航列表 | 递归过滤 hidden |
| `form` | 新版表单 | 默认直接输出 `$[key.preset]` |

## 通用读取

- 检测空值、`null/undefined` 和未替换 `$[...]`。
- 每个根配置单独读取和回退，不能用一个异常包住整个初始化。
- `value/default_value` 只在导入 JSON 中保存为字符串；运行时输出类型以控件说明为准。
- `jump/category/form` 的点号字段共同对应一个根 key，不生成带点的独立配置 key。
- 配置为空通常表示不开启附加条件或显示默认内容，不虚构选择结果。

## 多语言

语言优先读取 URL `editor_language_type`，再读 `localStorage.lang`，最后回退 `zh-cn`。标准 key 为 `zh-cn/zh/en/kr/ru/jp`，缺失文案逐键回退到 `zh-cn` 和内置中文。
