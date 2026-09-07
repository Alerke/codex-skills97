# 校验、验证码与提交

默认校验、验证码和提交由 `$[表单变量.preset]` 或 `$[表单变量.script]` 提供。生成模块时优先调用 runtime API，不要复制旧逻辑。

## 默认调用

```html
<div class="xxFormModule">
  $[fitForm.preset]
</div>
```

外部按钮：

```js
const runtime = window.fitForm_10126;
await runtime.ready();
await runtime.submit({
  button: event.currentTarget,
  extraPayload: { source: 'outside-button' },
  extensionField: { campaign: 'landing' }
});
```

生成代码时不要假定运行时一定叫 `fitForm_10126`。运行时名称由“变量名 + 提交表单 ID”决定，详见 [runtime-api.md](runtime-api.md)。

## 值采集

preset runtime 以真实控件 `name` 为字段 key 收集值。

规则：

- `description` 不提交。
- `checkbox` 同名多选会收集为数组。
- `address` 写入主隐藏值和省市区详细字段。
- `dateRange`、`timeRange` 使用 `name_start`、`name_end`。
- `switch` 输出选中控件值。
- `upload` 不要提交浏览器 `File` 对象或文件名作为最终附件值。

完全自定义 DOM 时，也必须让控件有稳定 `name`。

## 校验

preset submit 会：

- 调用浏览器 `checkValidity()`。
- 校验失败时调用 `reportValidity()`。
- 使用 `Utils.Toast.error` 显示失败提示。
- 验证码发送前单独校验手机号。

普通表单必填校验主要依赖浏览器原生校验。验证码等控件错误会写入字段错误态：

```html
<div class="gw-fit-form-field is-error" data-gw-fit-form-error="请先填写正确的手机号">
  <input class="gw-fit-form-control is-error" aria-invalid="true" data-gw-fit-field-error="1">
</div>
```

样式必须支持：

- `.gw-fit-form-field.is-error`
- `.gw-fit-form-captcha.is-error`
- `.gw-fit-form-control.is-error`
- `[aria-invalid="true"]`
- `[data-gw-fit-field-error="1"]`

禁止使用 `alert()`。

## 验证码

默认 preset 已实现验证码发送，不要重复绑定按钮。

验证码 DOM 契约：

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

默认配置：

| 配置 | 默认值 |
| --- | --- |
| endpoint | `/api/website/getSmsCode` |
| sms type | `form` |
| countdown | `60` |

手机号查找依据包括：

- `type="tel"`。
- `name` / `id`。
- `placeholder`。
- `aria-label`。
- label 文本。

匹配关键字：

- `phone`
- `mobile`
- `tel`
- `手机号`
- `手机`
- `电话`

排除关键字：

- `captcha`
- `verify`
- `code`
- `验证码`

手机号校验：

```text
^1[0-9]{10}$
```

失败时：

- focus 手机号字段。
- 手机号字段进入 `.is-error`。
- `Utils.Toast.error('请先填写正确的手机号')`。
- 触发 `gw-fit-form:captcha-error`。
- 重置验证码按钮。

发送成功时：

- 触发 `gw-fit-form:captcha-success`。
- `Utils.Toast.success('验证码已发送')`。
- 根据响应 `endtime/endTime` 与 `servertime/serverTime` 或默认秒数开始倒计时。

发送失败时：

- 写字段错误态。
- `Utils.Toast.error(错误信息)`。
- 触发 `gw-fit-form:captcha-error`。

自定义短信发送优先监听可取消事件：

```js
document.addEventListener('gw-fit-form:captcha-send', function (event) {
  const detail = event.detail || {};
  event.preventDefault();

  detail.setLoading();

  customSendSms(detail.phone)
    .then(function () {
      detail.startCountdown(60);
      Utils.Toast.success('验证码已发送');
    })
    .catch(function (error) {
      detail.reset();
      Utils.Toast.error(error.message || '验证码发送失败');
    });
});
```

## 提交

默认 preset 提交流程：

1. 执行字段校验。
2. 收集字段值。
3. 读取 `website_id`。
4. 检查 `form_id`。
5. 请求匿名表单 token。
6. 构造提交 payload。
7. 触发 `gw-fit-form:submit`。
8. 调用提交接口。
9. 成功时触发 `gw-fit-form:success` 并显示成功 Toast。
10. 失败时触发 `gw-fit-form:error` 并显示错误 Toast。
11. 恢复按钮状态。

提交前获取 token：

```text
/shop/user/getNoAuthWorkForm?form_id=表单ID
```

提交接口：

```text
POST https://wei.ltd.com/api/analyst/data/postBasicsFormMessage?website_id=website_id
```

payload 结构：

```js
{
  form_id: '10126',
  website_id: '10001',
  name: '张三',
  mobile: '13800138000',
  captchaCode: '123456',
  extensionField_10126: {
    locationUrl: location.href,
    ltd_guest_token: 'token',
    website_id: '10001',
    gmac: 'cookie-gmac'
  }
}
```

要求：

- `extensionField_表单ID` 必须是对象。
- 不要把 `extensionField_表单ID` JSON.stringify 成字符串。
- 字段值以控件 `name` 为 key。
- `extraPayload` / `payload` 可合并到根 payload。
- `extensionField` 可合并到 `extensionField_表单ID`。

如果目标环境已经提供 `submit()`、`payload()`、`finalPayload()` 或等价 API，应优先调用，不要重新写完整提交流程。

完全自定义提交时，提交函数可以独立，但必须保持 preset 的 payload、Toast、事件和按钮状态约定。

## 事件

提交前事件可取消：

```js
document.addEventListener('gw-fit-form:submit', function (event) {
  const detail = event.detail || {};

  if (!detail.values.mobile) {
    event.preventDefault();
    Utils.Toast.error('请填写手机号');
  }
});
```

成功和失败：

```js
document.addEventListener('gw-fit-form:success', function (event) {
  console.log(event.detail.response);
});

document.addEventListener('gw-fit-form:error', function (event) {
  Utils.Toast.error(event.detail.message || '提交失败');
});
```

## Toast

提示能力优先复用：

1. runtime options 中注入的 Toast。
2. `window.Utils.Toast`。
3. `window.toast`。
4. 内置 fallback。

Toast 应用于：

- 校验失败。
- 提交中。
- 提交成功。
- 提交失败。
- 验证码发送成功。
- 验证码发送失败。
- 上传失败。
- 配置解析失败。

不要使用 `alert()`。
