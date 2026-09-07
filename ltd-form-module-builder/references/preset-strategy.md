# 表单预设策略

## 默认策略

生成 LTD 表单代码模块时，默认直接使用新版表单 preset：

```html
<div class="xxFormModule">
  $[fitForm.preset]
</div>
```

`$[fitForm.preset]` 已包含：

- scoped style。
- 表单 body。
- preset runtime script。
- 字段布局。
- 字段取值。
- 浏览器原生校验。
- 验证码发送、倒计时、字段错误态。
- 地址、上传、颜色、级联等控件增强。
- 提交请求和 payload。
- `Utils.Toast` 与 fallback。
- `变量名_表单ID` API。

不要把 `$[fitForm.preset]` 放进 `<script>`、`<style>`、`textarea`、JSON 字符串或 HTML 注释中。

**正确用法**：仅在 HTML 内容区域（如 `<div>` 内部）直接输出变量：

```html
<!-- 正确：在内容区域直接输出 -->
<div class="xxFormModule">
  $[fitForm.preset]
</div>
```

**错误用法**：

```html
<!-- 错误：在注释中引用变量 -->
<!-- 优先使用 $[fitForm.preset] 输出 -->

<!-- 错误：在 script 字符串中引用 -->
<script>
  // 不要这样写：$[fitForm.preset]
  const preset = "$[fitForm.preset]";  // 会导致解析错误
</script>

<!-- 错误：在 style 注释中引用 -->
<style>
  /* 使用 $[fitForm.preset] 输出表单 */
</style>
```

原因：LTD 变量解析器会替换文件中所有匹配 `$[变量名.属性]` 的文本，包括注释、字符串和脚本。在非内容区域使用会导致：
1. 注入的 HTML/JS/CSS 破坏原有语法结构
2. 运行时脚本被嵌套，导致重复执行
3. JSON 配置被截断或格式错误

如果需要在注释中说明，使用纯文本描述，如"使用表单 preset 变量输出"。

## 变量名规则

变量名是什么就是什么。

示例：

| 变量 key | 正确写法 | 错误写法 |
| --- | --- | --- |
| `fitForm` | `$[fitForm.preset]` | `$[fit_form.preset]` |
| `fit_form` | `$[fit_form.preset]` | `$[fitForm.preset]` |
| `contactForm` | `$[contactForm.preset]` | `$[contact_form.preset]` |

不要自动做驼峰、下划线或大小写转换。

## 变量输出

常见输出约定：

| 输出 | 用途 |
| --- | --- |
| `$[formKey.preset]` | 完整表单，包含 style + body + script。默认使用。 |
| `$[formKey.style]` | scoped CSS。需要拆分输出时使用。 |
| `$[formKey.body]` / `$[formKey.dom]` / `$[formKey.html]` | 仅表单结构。必须配合 `.script`。 |
| `$[formKey.script]` | preset runtime。安装校验、验证码、提交和 API。 |
| `$[formKey.config]` / `$[formKey.json]` | 完整 JSON 配置。仅代码模块样式或自定义渲染使用。 |
| `$[formKey.id]` | 当前表单 ID。 |
| `$[formKey.name]` | 当前表单变量名或表单名。 |
| `$[formKey.title]` | 表单标题。 |
| `$[formKey.description]` | 表单描述。 |
| `$[formKey.info]` | 表单基础信息 JSON。 |
| `$[formKey.fields]` | 字段数组 JSON。 |
| `$[formKey.layout]` | 布局配置 JSON。 |
| `$[formKey.appearanceMode]` | 外观模式。 |
| `$[formKey.appearancePreset]` | 系统 preset 名称。 |
| `$[formKey.appearanceCssVars]` | CSS 变量 JSON。 |
| `$[formKey.appearanceCss]` | CSS 文本。 |
| `$[formKey.appearanceStyle]` | style 属性文本。 |

不建议新模块依赖 `$[formKey]` 默认输出，因为默认输出会随外观模式变化。

## 拆分输出

只有需要调整 style、body、script 的插入位置时才拆分：

```html
$[fitForm.style]

<div class="xxFormModule">
  $[fitForm.body]
</div>

$[fitForm.script]
```

要求：

- `.script` 必须在 `.body` 之后。
- `.body` 必须保留 `data-ltd-form-module`、`data-form-id`、`data-submit-form-id`、scope class 和字段 data 属性。
- 不要只输出 `.body`。只有 body 会显示字段，但不会安装提交、验证码、校验和 API。

## 代码模块样式

只有下面情况读取 `$[formKey.config]`：

- 表单选择了“代码模块样式”。
- 用户明确要求代码模块完全控制 DOM 和原生 CSS。
- 需要沉淀多套自定义表单皮肤，并且不能放入系统 preset。

示例：

```html
<div class="xxFormModule" data-form-module-root>
  <textarea class="xx-form-config" hidden aria-hidden="true">$[fitForm.config]</textarea>
  <div class="xx-form-root"></div>
</div>
```

代码模块样式必须：

- 解析 `$[formKey.config]`。
- 渲染所有字段类型。
- 支持 24 栅格布局、`colSpan`、`offset`、`rowSpan`、`newRow`。
- 复用 preset 的 class/data 属性契约。
- 使用 `Utils.Toast`。
- 验证码遵守 `data-gw-fit-captcha` / `data-gw-captcha-button`。
- 提交 payload 与 preset 一致。
- 注册 `变量名_表单ID` 兼容 API。

如果只是修改颜色、间距、圆角、字体，优先使用 `$[formKey.style] + $[formKey.body] + $[formKey.script]` 后在模块原生 CSS 中覆盖 preset class，不要完整重写 DOM。

## 旧实现禁止项

不要生成：

- `<script type="application/json" class="ve-form-config">...`
- `ve-form-header`
- `ve-form-body`
- 旧 provider 输出。
- 重复 `presetRuntime`、`controlRuntime` 或提交 runtime。
- 自己再绑定一套验证码发送逻辑。
- 自己再绑定一套默认提交逻辑。

这些会导致 style/script 嵌套、runtime 重复注入、验证码点击无反馈或提交两次。

## 运行时调用

系统 preset 会注册：

```js
window.fitForm_10126
```

命名规则：

```text
表单变量名_提交表单ID
```

业务代码通过 runtime 调用：

```js
const runtime = window.fitForm_10126;

runtime.ready(function () {
  console.log(runtime.values());
});

runtime.submit();
```

完整说明见 [runtime-api.md](runtime-api.md)。
