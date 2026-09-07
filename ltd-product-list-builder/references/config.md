# 产品列表配置 JSON

## 目录

- [基本原则](#1-基本原则)
- [推荐基础 key](#2-推荐基础-key)
- [cat_id 结构](#3-cat_id-结构)
- [i18n 结构](#4-i18n-结构)
- [开关和数字](#5-开关和数字)
- [交付检查](#6-交付检查)

## 1. 基本原则

产品列表没有强制固定 key 数量。根据用户要求和现有模块确定配置，但必须满足：

- HTML 中每个占位符的根 key 在 JSON 中恰好出现一次；`$[cat_id]` 与 `$[cat_id.moduleType]` 等点号语法共同对应一个 `cat_id`。
- JSON 中不保留代码未使用的配置。
- 每项包含 `key`、`label`、`value`、`default_value`、`input_type`。
- 顶层 JSON 必须可直接导入，不能带 Markdown 注释、尾逗号或省略号。
- `value` 与 `default_value` 必须属于同一配置类型并分别可解析；编辑器可选元数据允许只存在于当前 `value`，例如 category 的 `sortColumnVersion`。
- 每个配置都要有运行时安全默认值；未替换、类型错误、非法值或旧数据解析失败不能阻塞模块初始化，具体规则见 [`config-error-handling.md`](config-error-handling.md)。

## 2. 推荐基础 key

| key | input_type | 用途 |
| --- | --- | --- |
| `cat_id` | `category` | 选择 product 或 goods 分类，并配置每页数量和排序 |
| `show_sidebar` | `switch` | 是否显示分类区域 |
| `show_all_button` | `switch` | 是否显示“全部”分类 |
| `show_description` | `switch` | 是否显示产品描述 |
| `enable_list_mode` | `switch` | 是否启用列表布局 |
| `show_title` | `switch` | 是否显示区域标题 |
| `show_count` | `switch` | 是否显示结果总数 |
| `open_in_current` | `switch` | 是否始终当前页打开 |
| `show_search` | `switch` | 是否显示关键词搜索 |
| `show_sort` | `switch` | 是否显示排序 |
| `show_price` | `switch` | 是否显示价格 |
| `show_pagination` | `switch` | 是否显示分页 |
| `columns_pc` | `number` | PC 列数 |
| `columns_tablet` | `number` | 平板列数 |
| `columns_mobile` | `number` | 手机列数 |
| `image_ratio` | `text` | 图片比例，例如 `4 / 3` |
| `theme_color` | `color` | 主题色 |
| `card_background` | `color` | 卡片背景色 |
| `text_color` | `color` | 主文字色 |
| `muted_color` | `color` | 辅助文字色 |
| `i18n` | `i18n` | 搜索、全部、空状态、错误、重试、分页文案 |

只保留当前模块实际使用的项。需要搜索、排序或价格时再加入对应 key；不要为了凑齐表格而生成无效配置。

`cat_id` 的 `input_type` 必须严格使用 `category`。这里的 `category` 表示平台分类选择控件；产品或商品体系由其值中的 `moduleType: "product"/"goods"` 决定，不能把 `product`、`goods` 写成 `input_type`。

“全部”选项需要可控时加入：

```json
{
  "key": "show_all_button",
  "label": "显示全部选项",
  "value": "1",
  "default_value": "1",
  "input_type": "switch"
}
```

代码使用 `$[show_all_button]` 并通过 `readSwitch` 解析。关闭只隐藏“全部”按钮，不改变空 `selectedCatId` 的全量查询语义，也不自动选择首个分类。

需要为所有产品/商品配置同一个静态点击操作时，可增加 `card_click`，其 `input_type` 使用平台已有的 `jump`，不要自行发明 `clickAction` 类型。代码使用 `$[card_click.href]`、`$[card_click.target]`、`$[card_click.type]` 等点号字段，它们共同对应一个 `card_click` 配置项；不得增加 `card_click.href` 等独立 key，也不得把 `$[card_click]` 当 JSON 解析。类型与字段见 [`click-action-type.md`](click-action-type.md)。

```html
<a href="$[card_click.href]" target="$[card_click.target]">查看详情</a>
```

若每张卡片跳到各自的接口详情 URL，则不增加该配置，直接从归一化数据生成安全真实链接。平台静态配置生成的 `data-gw-*` 由平台运行时处理；动态链接和事件边界见 [`click-action-runtime.md`](click-action-runtime.md)。

参考模块中 `theme_color`、`light_mode`、尺寸、列数、背景和字号属于样式配置，不属于本轮提炼的实现核心；只有模块真实使用时才保留。行为 key 优先采用上表已有命名，不同时生成语义重复的 `show_category` 与 `show_sidebar`。

## 3. cat_id 结构

`cat_id` 的 `value` 与 `default_value` 是字符串化 JSON。实际商品配置可包含多选 ids/names 和版本元数据：

```json
{"moduleType":"goods","type":"1","ids":"165567,212865,212869,212867,169069,190933,212861,212863","names":["客厅","客厅-1","客厅-1-1","客厅-2","餐厅","test","test-1","test-1-1"],"pageSize":12,"sortColumn":"sort","sortDirection":"asc","sortColumnVersion":2}
```

产品配置使用 `moduleType: "product"`，商品配置使用 `moduleType: "goods"`；运行时代码根据该值自动选择对应接口。只有明确执行“把现有配置迁移到另一体系”时，才改写 `moduleType` 并清空原体系的 `ids/names/type`；不同体系的分类 ID 不做自动映射。

`ids` 为空、`cat_id` 配置未传或用户未选择分类时表示不限制分类，获取当前 product/goods 模块的全部数据。运行时不得自动补第一个分类；若 ids 非空，则“全部”只代表这些允许分类内的全部数据。

`ids` 与 `names` 保留编辑器顺序；运行时请求仅使用清洗后的字符串 ids，分类显示名从分类接口读取。`type` 可以为空，空值不发送细分类型参数。`sortColumnVersion` 是可选编辑器元数据，维护时保留但不发送接口、不参与 order，也不要求 `default_value` 必须具有相同字段。

上面的字符串化对象只用于配置导入和后台存储。模块运行时按点号语法读取：

- `$[cat_id]` → ids。
- `$[cat_id.moduleType]` → 业务大类。
- `$[cat_id.type]` → 细分类型。
- `$[cat_id.pageSize]` → 每页条数。
- `$[cat_id.sortColumn]` → 排序字段。
- `$[cat_id.sortDirection]` → 排序方向。

不得把 `$[cat_id]` 默认交给 `JSON.parse`。只有明确兼容旧项目且值以 `{` 开始时，才把完整对象作为降级来源；新模块不要同时输出语义重复的 `category` key。完整规则见 [`category-type.md`](category-type.md)。`moduleType` 映射：

- `product` → 产品体系。
- `goods` → 商品体系。
- `shopGoods` 及其他非空值 → 非法类型；不得映射或静默使用默认值。
- 其他值 → 使用本次交付明确默认类型；没有有效默认类型时停止当前实例并显示错误。

## 4. i18n 结构

多语言配置使用 `key: "i18n"` 和 `input_type: "i18n"`。标准语言包含 `zh-cn`、`zh`、`en`、`kr`、`ru`、`jp`，每种语言内部 key 一致。配置导入时 `value/default_value` 保存为字符串化 JSON，模板替换后的 `$[i18n]` 则是可直接使用的 JavaScript 对象。推荐文案 key：

`product_title`、`goods_title`、`search_placeholder`、`search`、`clear`、`all`、`default_sort`、`newest`、`price_asc`、`price_desc`、`loading`、`empty`、`reset`、`error`、`retry`、`previous`、`next`。

默认不要用一个固定 `title` 同时表示两种类型。`product_title/goods_title` 必须同时存在于每种语言中，运行时根据 `cat_id.moduleType` 选择。

运行时优先读取 URL 的 `editor_language_type`，再读 `localStorage.lang`。缺失语言回退到 `zh-cn`，缺失单项再回退到模块内中文默认值；完整规则见 [`i18n.md`](i18n.md)。

## 5. 开关和数字

- `switch` 注入常见值为字符串 `"1"` 或 `"0"`，统一用显式比较解析，不能使用 `Boolean("0")`。
- `number` 必须转为有限数字并限制合理范围，例如列数 `1–6`、每页数量 `1–100`。
- CSS 配置通过根节点 CSS 变量写入，不拼接未校验的整段 CSS。
- `open_in_current: "1"` 强制 `_self`；关闭时优先使用产品数据或明确链接配置的 target，缺失时仍回退 `_self`，不根据设备类型自动改为 `_blank`。

## 6. 交付检查

交付前检查：

1. JSON 顶层能被 `JSON.parse`。
2. 配置 JSON 中 `cat_id` 与 `i18n` 的内嵌值能再次解析。
3. 模块代码包含 `cat_id` 六个标准点号占位符，且 `$[cat_id]` 只作为 ids 使用。
4. key 唯一且与 HTML 占位符根 key 集合一致；不得生成 `cat_id.moduleType` 等独立配置 key。
5. 改变 `moduleType` 后无需修改 JS，实际分类/列表接口会由适配器自动切换；人工迁移配置时已清空原体系的 `ids/names/type`。
6. 默认值能在没有后台配置时形成完整可用列表。
7. 每个 `jump` 根 key 的全部点号占位符都由同一项提供，且复杂点击类型已按平台运行时验证。
8. 分类根配置项的 `input_type` 严格等于 `category`。
9. 多语言根配置项使用 `key: "i18n"`，且 `input_type` 严格等于 `i18n`。
10. 逐项验证缺失值、未替换占位符、错误类型和非法值的运行时降级，不允许单项配置异常阻塞整个模块。
11. category 为空或未传时按“当前适配器全部数据”处理，没有生成默认分类筛选；非空允许 ids 仍得到严格保留。
12. category 的 ids/names 顺序、空 type 和可选 `sortColumnVersion` 得到保留；元数据没有进入列表请求或独立配置项。
13. 分别验证 product/goods：只改变配置类型，分类接口和列表接口自动成对切换。
14. 通用请求器只读取已选 `adapter.categoryUrl/listUrl`，没有另行写死某一体系接口。
15. 每种 i18n 语言都包含 `product_title/goods_title`，运行时按 moduleType 选择标题。
16. 使用 `$[show_all_button]` 时 JSON 中只有一个同名 `switch` 配置；`"0"` 隐藏按钮但不改变当前查询范围，`"1"` 显示并可清空分类选择。
