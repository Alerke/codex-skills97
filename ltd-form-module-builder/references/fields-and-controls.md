# 字段与控件

默认字段 DOM 由 `$[表单变量.preset]` 生成。只有代码模块样式或完全自定义 DOM 时，才需要按本文档自行渲染字段。

## 字段基础结构

每个可见字段都应放在字段 wrapper 中：

```html
<div class="gw-fit-form-field" data-field-id="phone" data-field-type="phone">
  <div class="gw-fit-form-field-shell">
    <div class="gw-fit-form-field-content">
      <label class="gw-fit-form-label" for="fitForm_phone">
        <span>手机号</span>
        <span class="gw-fit-form-required">*</span>
      </label>
      <div class="gw-fit-form-control-wrap">
        <input class="gw-fit-form-control" id="fitForm_phone" name="phone" type="tel">
      </div>
    </div>
  </div>
</div>
```

必须保留：

- `data-field-id`。
- `data-field-type`。
- `name`，字段取值和 payload 以控件 `name` 为准。
- `required`。
- `.gw-fit-form-control`。
- `.gw-fit-form-control-wrap`。

label 位置：

| class | 说明 |
| --- | --- |
| 无额外方向 class | label 在上方，默认布局。 |
| `is-label-left` | label 在左侧。 |
| `is-label-right` | label 在右侧。 |

## 字段类型

必须支持这些字段类型：

| type | 控件 | 必要 DOM/class |
| --- | --- | --- |
| `text` | 单行文本 | `input.gw-fit-form-control[type=text]` |
| `textarea` | 多行文本 | `textarea.gw-fit-form-control` |
| `password` | 密码 | `input.gw-fit-form-control[type=password]` |
| `number` | 数字输入 | `.gw-fit-form-counter` 或 `input[type=number]` |
| `counter` | 计数器 | `.gw-fit-form-counter`、`.gw-fit-form-stepper`、`.gw-fit-form-counter-input` |
| `email` | 邮箱 | `input.gw-fit-form-control[type=email]` |
| `phone` | 手机号 | `input.gw-fit-form-control[type=tel]` |
| `captcha` | 验证码 | `.gw-fit-form-captcha[data-gw-fit-captcha]`、`[data-gw-captcha-button]` |
| `description` | 描述文本 | `.gw-fit-form-description` |
| `select` | 下拉选择 | `.gw-fit-form-select-wrap`、`.gw-fit-form-select` |
| `cascader` | 级联选择 | `.gw-fit-form-cascader[data-gw-fit-cascader]` |
| `address` | 地址选择 | `.gw-fit-form-address[data-gw-fit-address]` |
| `radio` | 单选框组 | `.gw-fit-form-options`、`.gw-fit-form-option input[type=radio]` |
| `checkbox` | 多选框组 | `.gw-fit-form-options`、`.gw-fit-form-option input[type=checkbox]` |
| `switch` | 开关 | `.gw-fit-form-switch-row`、`.gw-fit-form-switch` |
| `slider` | 滑块 | `.gw-fit-form-slider`、`.gw-fit-form-slider-input` |
| `time` | 时间 | `.gw-fit-form-temporal input[type=time]` |
| `timeRange` | 时间范围 | `.gw-fit-form-range`、`name_start`、`name_end` |
| `date` | 日期 | `.gw-fit-form-temporal input[type=date]` |
| `dateRange` | 日期范围 | `.gw-fit-form-range`、`name_start`、`name_end` |
| `rate` | 评分 | `.gw-fit-form-rate`、`.gw-fit-form-rate-item` |
| `color` | 颜色选择 | `.gw-fit-form-color`、`.gw-fit-form-color-input` |
| `upload` | 上传 | `.gw-fit-form-upload`、`.gw-fit-form-upload-input` |
| `hidden` | 隐藏值 | `input[type=hidden]` |

未知类型降级为 `text`，不要中断整表渲染。

## 字段渲染

字段渲染规则：

- 字段外层写入字段 ID 和字段类型。
- 标签读取 `field.label`。
- placeholder 读取 `field.placeholder`。
- 选项读取 `field.options`。
- 必填状态读取 `field.required`。
- 默认值读取 `field.defaultValue`。
- `description` 渲染为说明块，不参与提交。
- `upload` 不能给原生 file input 写入非空 value。
- 日期、时间、颜色等原生控件也要提供统一样式。
- 代码模块样式不能只覆盖文本框和按钮，必须覆盖所有已声明字段类型。

不要写死“姓名、电话、邮箱”等具体字段。

## 错误态

控件 runtime 会把验证码等自定义错误写到字段 wrapper 或具体控件。错误文案统一通过 `Utils.Toast` 展示，DOM 中不插入错误文字节点。

```html
<div class="gw-fit-form-field is-error" data-gw-fit-form-error="请先填写正确的手机号">
  <input class="gw-fit-form-control is-error" aria-invalid="true" data-gw-fit-field-error="1">
</div>
```

样式必须覆盖：

- `.gw-fit-form-field.is-error .gw-fit-form-control`
- `.gw-fit-form-field.is-error select`
- `.gw-fit-form-field.is-error textarea`
- `.gw-fit-form-captcha.is-error .gw-fit-form-control`
- `.gw-fit-form-control.is-error`
- `[data-gw-fit-field-error="1"]`

## 验证码字段

验证码最低结构：

```html
<div
  class="gw-fit-form-captcha"
  data-gw-fit-captcha
  data-captcha-endpoint="/api/website/getSmsCode"
  data-captcha-sms-type="form"
  data-captcha-countdown="60"
>
  <input class="gw-fit-form-control" name="captchaCode" type="text" autocomplete="one-time-code">
  <button class="gw-fit-form-button is-secondary" type="button" data-gw-captcha-button>
    获取验证码
  </button>
</div>
```

要求：

- wrapper 带 `data-gw-fit-captcha`。
- 按钮带 `data-gw-captcha-button`。
- 按钮必须是 `type="button"`。
- 输入框必须有 `name`。
- endpoint、sms type、countdown 从字段 `captchaEndpoint`、`captchaSmsType`、`captchaCountdown` 输出到 data 属性。

默认 preset 已实现验证码发送，代码模块不要再复制旧验证码 JS。详细规则见 [validation-and-submit.md](validation-and-submit.md)。

## 地址字段

地址最低结构：

```html
<div class="gw-fit-form-address" data-gw-fit-address>
  <input class="gw-fit-form-address-value" type="hidden" name="address">
  <input type="hidden" name="address_province">
  <input type="hidden" name="address_province_id">
  <input type="hidden" name="address_city">
  <input type="hidden" name="address_city_id">
  <input type="hidden" name="address_district">
  <input type="hidden" name="address_district_id">
  <span class="gw-fit-form-select-wrap"><select data-level="0"></select></span>
  <span class="gw-fit-form-select-wrap"><select data-level="1"></select></span>
  <span class="gw-fit-form-select-wrap"><select data-level="2"></select></span>
  <input class="gw-fit-form-control gw-fit-form-address-detail" name="address_detail">
</div>
```

地址控件应优先调用：

```js
const regions = await formRuntime.getAddressRegions(parentId);
```

其中 `formRuntime` 通常来自 `window[变量名_表单ID]`，例如 `fitForm_10126`。

## 上传字段

文件上传：

```html
<label class="gw-fit-form-upload" data-upload-style="file">
  <input class="gw-fit-form-upload-input" type="file" name="file">
  <span class="gw-fit-form-upload-name">点击上传文件</span>
  <small class="gw-fit-form-upload-detail">选择文件后会显示文件名称和大小</small>
</label>
```

图片上传：

```html
<label class="gw-fit-form-upload is-image" data-upload-style="image">
  <input class="gw-fit-form-upload-input" type="file" accept="image/*" name="image">
  <img class="gw-fit-form-upload-preview" alt="" hidden>
</label>
```

runtime 会读取：

- `.gw-fit-form-upload-input`
- `.gw-fit-form-upload-name`
- `.gw-fit-form-upload-detail`
- `.gw-fit-form-upload-preview`

## 控件运行时

以下控件应优先复用已有控件运行时：

- 计数器。
- 滑块。
- 颜色选择器。
- 上传。
- 级联。
- 地址联动。
- 验证码。

不要把这些控件逻辑写进提交函数。控件工厂只负责渲染和控件交互，不负责提交接口。
