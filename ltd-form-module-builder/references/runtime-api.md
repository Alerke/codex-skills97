# 表单运行时 API

## 适用范围

生成 LTD 表单模块时，优先调用新版表单 preset 注入的运行时 API。不要因为是代码模块样式，就重复手写取值、校验、验证码、提交、地址、i18n 或 Toast 逻辑。

默认使用：

```html
$[fitForm.preset]
```

拆分使用：

```html
$[fitForm.style]
$[fitForm.body]
$[fitForm.script]
```

如果页面只有 `$[fitForm.body]`，不会安装运行时 API。

## 运行时名称

表单运行时全局名使用：

```text
变量名_提交表单ID
```

提交表单 ID 为：

```js
form.submitFormId || form.id
```

例如变量名是 `fitForm`、提交表单 ID 是 `10126`，前台可调用：

```js
fitForm_10126.ready();
fitForm_10126.values();
fitForm_10126.submit();
```

变量名保持原样。如果变量名是 `contact_form`，表单 ID 是 `10126`：

```js
contact_form_10126.submit();
```

不要把 `contact_form` 自动转为 `contactForm`。

如果页面上已经存在同名 `window[变量名_表单ID]`，preset runtime 不应覆盖已有对象。可通过统一命名空间读取：

```js
window.__GwCodeRuntime && window.__GwCodeRuntime.fitForm_10126;
```

## 稳定 API

优先使用以下公开方法：

| API | 作用 |
| --- | --- |
| `ready(callback?)` | 等待目标表单初始化完成，返回 Promise。 |
| `config()` | 获取当前表单配置。 |
| `values()` | 获取全部字段值。 |
| `value(key)` | 获取单个字段值，key 可为字段 id 或 name。 |
| `payload(websiteId?, extraPayload?)` | 获取基础提交 payload。 |
| `finalPayload(options?)` | 获取最终提交 payload，补充 token 和 `extensionField_表单ID`。 |
| `validate()` | 执行浏览器原生表单校验，返回 `{ valid, message }`。 |
| `valid()` | 返回布尔校验结果。 |
| `submit(buttonOrOptions?, extraOptions?)` | 提交表单。 |
| `getAddressRegions(parentId)` | 获取地址地区列表。 |
| `reset()` | 重置表单。 |
| `language()` | 获取当前语言。 |
| `i18n()` | 获取当前多语言配置。 |
| `t(key, fallback?, lang?)` | 获取当前语言文案。 |
| `setI18n(i18n, options?)` | 覆盖多语言配置。 |
| `mergeI18n(i18n, options?)` | 增量合并多语言配置。 |
| `setLanguage(lang)` | 切换语言。 |

## 调用示例

外部按钮触发表单提交：

```js
document.querySelector('.submit-outside').addEventListener('click', async (event) => {
  event.preventDefault();
  const runtime = window.fitForm_10126;
  if (!runtime) return;

  await runtime.ready();
  await runtime.submit({
    button: event.currentTarget,
    extraPayload: { source: 'outside-button' },
    extensionField: { campaign: 'summer' }
  });
});
```

只获取 payload，不提交：

```js
const runtime = window.fitForm_10126;
await runtime.ready();

const payload = runtime.payload();
const finalPayload = await runtime.finalPayload({
  extraPayload: { source: 'preview' }
});
```

提交成功或失败后的业务处理请监听事件，不要假设 `submit()` 选项里存在回调：

```js
document.addEventListener('gw-fit-form:success', function (event) {
  console.log(event.detail.response);
});

document.addEventListener('gw-fit-form:error', function (event) {
  console.log(event.detail.message);
});
```

## 事件

| 事件 | 时机 | 可取消 |
| --- | --- | --- |
| `gw-fit-form:submit` | 提交前 | 是 |
| `gw-fit-form:success` | 提交成功 | 否 |
| `gw-fit-form:error` | 提交失败 | 否 |
| `gw-fit-form:captcha-send` | 验证码发送前 | 是 |
| `gw-fit-form:captcha-success` | 验证码发送成功 | 否 |
| `gw-fit-form:captcha-error` | 验证码发送失败 | 否 |

自定义业务逻辑优先监听事件，而不是改写 runtime。

## 地址地区函数

地址控件和自定义地址联动优先调用运行时地址函数：

```js
const runtime = window.fitForm_10126;

runtime.ready(async () => {
  const provinces = await runtime.getAddressRegions(0);
  const cities = await runtime.getAddressRegions(provinces[0].value);
});
```

返回数据统一按以下结构消费：

```js
[
  { value: '330000', label: '浙江省', has_children: 1 }
]
```

不要在每个模块里重复写地区接口、缓存和字段归一化逻辑。没有现成 API 时，才补最小地区请求函数，并确保携带 `website_id`。

## Toast

preset runtime 查找 Toast 的顺序：

1. runtime options 中注入的 Toast。
2. `window.Utils.Toast`。
3. `window.toast`。
4. 内置 fallback。

自定义代码模块样式如果自己写 JS，也必须遵守同样顺序，不能直接 `alert()`。

## 外部 i18n

运行时支持 LTD 标准六语言：

```text
zh-cn, zh, en, kr, ru, jp
```

外部代码可在表单 ready 前后设置语言包：

```js
fitForm_10126
  .setI18n({
    'zh-cn': {
      title: '联系我们',
      submitButtonText: '提交',
      fields: {
        phone: { label: '手机号', placeholder: '请输入手机号' }
      }
    },
    en: {
      title: 'Contact us',
      submitButtonText: 'Submit',
      fields: {
        phone: { label: 'Phone', placeholder: 'Enter phone number' }
      }
    }
  })
  .setLanguage('en');
```

## 代码模块样式兼容要求

如果使用 `$[fitForm.config]` 自己渲染 DOM，必须保持下列兼容性：

1. 表单根节点包含 `data-ltd-form-module`、`data-form-id`，有提交目标时包含 `data-submit-form-id`。
2. 字段节点包含 `data-field-id` 和 `data-field-type`。
3. 控件必须有稳定的 `name`，值收集以 `name` 为准。
4. 验证码 wrapper 使用 `data-gw-fit-captcha`，按钮使用 `data-gw-captcha-button`。
5. 错误态使用 `.is-error`、`aria-invalid="true"` 和 `[data-gw-fit-field-error="1"]`。
6. 提示必须使用 `Utils.Toast` 兼容链。
7. 对外 API 至少实现 `ready/config/values/value/validate/valid/submit/reset`。

除非完全自定义渲染并且没有使用 `$[fitForm.script]`，否则禁止生成：

```js
window.fitForm_10126 = { ... };
```
