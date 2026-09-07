# 配置读取与布局

## 什么时候读取配置

默认不要读取配置自行渲染，直接输出：

```html
$[fitForm.preset]
```

只有代码模块样式或完全自定义 DOM 时，才读取：

```html
<textarea class="xx-form-config" hidden aria-hidden="true">$[fitForm.config]</textarea>
```

不要把完整 JSON 放进：

```html
<script type="application/json" class="ve-form-config"></script>
```

也不要把 `$[fitForm.preset]` 放进 textarea。

## 配置读取

生成模块时不要写入 mock 表单数据。真实表单、字段、选项和布局都来自 `$[变量.config]`。

示例：

```html
<div class="xxFormModule" data-form-module-root>
  <textarea class="xx-form-config" hidden aria-hidden="true">$[fitForm.config]</textarea>
  <div class="xx-form-root"></div>
</div>
```

读取配置时必须兼容：

- 空配置。
- JSON 字符串。
- 二次 JSON 字符串。
- 已解析对象。
- 未选择表单。

示例：

```js
const readFormConfig = (container) => {
  const node = container.querySelector('.xx-form-config');
  const raw = node ? String(node.textContent || '').trim() : '';
  if (!raw || raw === '$[' + 'fitForm.config]') return {};

  try {
    let parsed = JSON.parse(raw);
    if (typeof parsed === 'string') parsed = JSON.parse(parsed);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch (error) {
    console.warn('[ltd form] config parse failed:', error);
    return {};
  }
};
```

## 当前表单解析

当前源码选择顺序：

1. `config.forms + config.selectedFormId`
2. `config.form`
3. `config.forms[0]`
4. 无表单时返回空状态，不允许提交

示例：

```js
const selectFormFromConfig = (config) => {
  if (!config || typeof config !== 'object') return null;
  const selectedFormId = config.selectedFormId != null ? String(config.selectedFormId) : '';

  if (Array.isArray(config.forms) && config.forms.length && selectedFormId) {
    const selected = config.forms.find((form) => String(form && form.id) === selectedFormId);
    if (selected) return selected;
  }

  if (config.form) return config.form;
  if (Array.isArray(config.forms) && config.forms.length) return config.forms[0];
  return null;
};
```

## 表单数据结构

表单配置通常包含：

```json
{
  "type": "visual_form",
  "version": 2,
  "selectedFormId": "form-id",
  "forms": [],
  "form": {
    "id": "form-id",
    "submitFormId": "submit-form-id",
    "name": "表单名称",
    "description": "",
    "info": {},
    "fields": [],
    "layout": {
      "columns": 24,
      "gap": 16,
      "fieldLayouts": {}
    },
    "relationships": []
  }
}
```

如果存在两个 ID，必须区分：

```js
const runtimeFormId = form.submitFormId || form.id;
```

规则：

- `form.id` 用于展示、选择、编辑器状态和列表识别。
- `submitFormId || form.id` 用于 runtime 名称、提交接口、扩展字段和 payload。
- 不要把展示 ID 错当成提交接口 ID。

## 根节点属性

preset body 根节点是表单：

```html
<form
  class="gw-fit-form-dom gw-fit-form-dom-10126 is-preset-style"
  data-ltd-form-module
  data-form-id="10126"
  data-submit-form-id="9983"
>
  ...
</form>
```

自定义 DOM 至少保留：

- `data-ltd-form-module`
- `data-form-id`
- 有提交目标时使用 `data-submit-form-id`
- 唯一 scope class

当前 preset 不输出 `data-form-key`，不要把它写成必须属性。

## 布局规则

布局使用配置驱动：

- 过滤 `visible === false` 字段。
- 排序优先读取布局项 `order`，再回退字段 `order`。
- 总列数默认 24。
- 间距默认 16。
- 支持 `colSpan`、`offset`、`rowSpan`、`newRow`。
- 必须处理 `offset`。
- 移动端可降级为单列。

布局字段说明：

| 字段 | 含义 |
| --- | --- |
| `order` | 排序 |
| `colSpan` | 占据列数 |
| `offset` | 左侧空列数 |
| `rowSpan` | 占据行数 |
| `newRow` | 是否另起一行 |
| `hideLabel` | 是否隐藏 label |
| `labelPosition` | `top`、`left`、`right` |
| `labelWidth` | 左右 label 宽度 |

`offset` 表示字段前方空列数。  
例如 24 栅格中 `colSpan: 12`、`offset: 3`，字段应从第 4 列开始：

```css
grid-column: 4 / span 12;
```

不要只写：

```css
grid-column: span 12;
```

## label 布局

当前 preset 的顶部 label 不额外输出方向 class：

```html
<div class="gw-fit-form-field-content">
  ...
</div>
```

左侧和右侧分别输出：

```html
<div class="gw-fit-form-field-content is-label-left"></div>
<div class="gw-fit-form-field-content is-label-right"></div>
```

移动端应自动堆叠，避免 label 和控件重叠。
