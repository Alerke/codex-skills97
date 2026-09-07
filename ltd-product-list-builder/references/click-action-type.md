# 点击操作类型与点号语法

本规范定义 LTD `input_type: "jump"` 的配置读取方式。产品列表与商品列表共用同一套规则；以下示例中的 `link` 是任意配置根 key，实际模块可命名为 `card_click`、`primary_link`、`form_link` 等。

## 1. 使用原则

- 静态点击配置始终优先把 `$[link.href]` 写入 `href`，按需把 `$[link.target]` 写入 `target`。
- `$[link]` 与 `$[link.href]` 都输出最终链接，但新代码使用点号形式以便同时读取类型和扩展字段。
- 所有点号字段只对应一个根配置项 `link`；配置 JSON 不得另建 `link.href`、`link.type` 等 key。
- 不把 `$[link]` 当作 JSON 对象解析，也不在模板中自行复刻编辑器的类型归一化。
- `input_type` 固定使用平台已有的 `jump`，不得发明 `clickAction` 等输入类型。

```html
<a href="$[primary_link.href]" target="$[primary_link.target]">点击跳转</a>
<a href="$[mini_program.href]">打开小程序页面</a>
<a href="$[form_link.href]">打开表单</a>
<a href="$[popup_link.href]">查看详情</a>
```

## 2. 标准字段

| 语法 | 输出 | 说明 |
| --- | --- | --- |
| `$[link]` | 完整链接 | 同 `$[link.href]`；打开表单时输出 `javascript:void(0)` |
| `$[link.href]` | 链接地址 | 推荐用于元素的 `href` |
| `$[link.target]` | `_self` / `_blank` | 打开方式；打开表单固定为 `_self` |
| `$[link.type]` | 点击类型 | `none`、`web`、`url`、`module`、`miniProgram`、`openForm`、`popup`、`mobile`、`email` |
| `$[link.formId]` | 表单 ID | 仅打开表单类型有值 |
| `$[link.popupType]` | 弹窗类型 | `form`、`qrcode`、`page`、`html`；`openForm` 归一为 `form` |
| `$[link.popupWidth]` | 弹窗宽度 | 例如 `720px`、`80vw` |
| `$[link.popupHeight]` | 弹窗高度 | 例如 `80vh`；未设置时由运行时按内容自适应 |
| `$[link.miniProgramPath]` | 小程序路径 | 例如 `/mall/search` |
| `$[link.path]` | 小程序路径别名 | 同 `$[link.miniProgramPath]` |

## 3. 点击类型

| type | 行为 |
| --- | --- |
| `none` | 不跳转，`href` 输出 `javascript:void(0);` |
| `web` | 站内页面；粘贴 `/path` 可由编辑器匹配站内页面 |
| `url` | 自定义链接；带域名的完整 URL 不自动匹配站内页面 |
| `module` | 跳转当前页或指定页面模块，目标可按模块名称、ID 或选择器配置 |
| `miniProgram` | 跳转小程序内部路径，`href` 输出 `javascript:jumpMall('路径')` |
| `openForm` | 打开表单，页面渲染时由平台注入 `data-gw-jump-type="openForm"` |
| `popup` | 弹出表单、二维码、指定页面或指定内容 |
| `mobile` | 拨打电话，平台自动补 `tel:` |
| `email` | 发送邮件，平台自动补 `mailto:` |

模块跳转由平台在页面中查找目标并平滑滚动。当前页面目标优先读取 `.gw-editor-module .gw-browse-module` 的 `data-module-name`、模块 ID 或选择器；模块代码不自行猜测目标，也不重复执行滚动。

## 4. 小程序跳转与历史兼容

- 新配置使用 `type: "miniProgram"` 并保存内部路径。
- 历史数据即使保存为 `type: "url"` 或 `type: "web"`，只要 `href` 是严格的 `javascript:jumpMall('路径')` 形式，编辑器会归一为 `miniProgram`，并由 `$[link.miniProgramPath]` / `$[link.path]` 输出纯路径。
- `javascript:jumpMall(...)` 是平台受控小程序桥接格式，不等于允许任意 `javascript:`。接口数据或普通 URL 配置中的任意脚本协议仍必须拒绝。

常见路径包括：

| 场景 | 路径示例 |
| --- | --- |
| 商城首页 / 搜索 | `/mall`、`/mall/search` |
| 分类 / 列表 | `/mall/classify`、`/mall/list` |
| 分类购物 | `/mall/classification?cat_id=category_id` |
| 商机 / 已购商机 | `/mall/businessOpportunity`、`/mall/myBuy` |
| 社区 / 发布内容 | `/mall/club`、`/mall/posting/question`、`/mall/posting/video`、`/mall/posting/invitation`、`/mall/posting/article` |
| 版块 / 问答 / 用户 | `/mall/forumTag/版块ID`、`/mall/forumDetail/问答ID`、`/mall/forumUser/会员ID` |
| 活动报名 | `/mall/bm?cat_id=category_id&pre_meta=...&sub_meta=...` |

`exclude_id`、`include_id`、`cat_id` 等参数可继续追加。参数名为 `cat_id`、`category_id`、`goods_category_id` 等分类字段时，编辑器可提供产品、商品、案例、自定义内容或文章细分分类选择器；最终只写入分类 ID，也允许手动填写。

## 5. 弹窗字段

| popupType | 内容 | 关键点号字段 |
| --- | --- | --- |
| `form` | 表单 | `$[link.formId]`、`$[link.autoCloseOnSuccess]`、`$[link.popupWidth]`、`$[link.popupHeight]` |
| `qrcode` | 二维码 | `$[link.qrcode]`、`$[link.qrcodeImage]`、`$[link.qrcodeStyle]`、`$[link.title]`、`$[link.summary]`、`$[link.description]` |
| `page` | 指定页面 | `$[link.pageUrl]`、`$[link.popupWidth]`、`$[link.popupHeight]` |
| `html` | 指定内容 | `$[link.html]`、`$[link.content]`、`$[link.contentFormat]`、`$[link.popupContents]` |

`contentFormat` 的语义：

- `text`：按纯文本和换行展示，不能作为 HTML 执行。
- `markdown`：保存替换时由平台渲染为 HTML 后放入弹窗模板。
- `html`：按原生 HTML 展示，不额外增加内容 padding。

表单、二维码、指定页面和指定内容都不是普通页面跳转。前台运行时拦截点击并调用 `Utils.Dialog.open`；指定页面使用 iframe 并显示加载状态。表单、页面和指定内容默认不显示弹窗头部，二维码使用内容区标题并按二维码尺寸适配。

## 6. 参数与安全

- 编辑器保存时把链接参数追加到最终 `href`，按 URL query 规则编码；编辑器展示时可解码为可读文本。
- 指定页面的参数跟随 `pageUrl` 进入 iframe 地址。
- `_blank` 的普通链接补 `rel="noopener noreferrer"`。
- 普通接口链接仅允许相对地址、`http:`、`https:`、`tel:`、`mailto:`。
- 只接受由明确 `miniProgram` 类型或历史严格 `jumpMall` 格式归一得到的小程序脚本链接；永远拒绝任意 `javascript:`、`data:`、`vbscript:`。

## 7. 静态配置与动态卡片

- 模块所有卡片共用一个后台点击动作时，在配置 JSON 中增加一个 `input_type: "jump"` 的根 key，并在静态模板中使用其点号字段。
- 每张卡片跳向接口返回的不同详情 URL 时，不为每条数据生成配置项；在适配器中归一化 `href`、`target`，再用 DOM API 创建安全 `<a>`。
- 动态接口 URL 默认只按普通链接处理。除非接口明确返回经过平台约定的结构并且任务要求接入，否则不得把接口文本推断成 `module`、`openForm` 或 `popup`。

## 8. 验收

- 点号字段与配置根 key 一一对应，没有额外的 `link.href` 配置项。
- `none`、普通网页、小程序、模块、表单及四种弹窗类型输出符合平台语义。
- 历史 `jumpMall` 能归一化，小程序路径字段不包含 JavaScript 包装。
- 任意接口 `javascript:` 仍被拒绝，没有因小程序兼容放宽通用 URL 安全。
- 链接参数、弹窗尺寸与内容格式没有在模块内二次编码或错误解析。
