# 点击操作前台运行时接入

本规范只定义产品/商品列表和 LTD 点击运行时的边界。类型、点号字段与归一化规则见 [`click-action-type.md`](click-action-type.md)，卡片结构与视觉状态见 [`click-action-style.md`](click-action-style.md)。

## 1. 两类来源必须分开

### 静态后台点击配置

静态配置由 `input_type: "jump"` 提供。模板使用 `$[key.href]`、`$[key.target]` 等点号字段；平台在保存和页面渲染阶段补充 `data-gw-jump-*`、模块目标、表单模板和弹窗内容。不要把 `$[key]` 当 JSON 解析，也不要手工复制一套属性映射器。

```html
<a class="pl-card-link"
   href="$[card_click.href]"
   target="$[card_click.target]">
  查看详情
</a>
```

如果运行环境要求 `data-gw-*`，以平台最终生成结果为准。模块只消费和保留这些属性，不覆盖、不改写、不重复注入。

### 接口动态详情链接

每张产品/商品的详情地址来自接口时，在适配器中归一化为 `href` 和 `target`，通过 DOM API 创建真实 `<a>`。这类链接默认是普通导航，不生成 `input_type: "jump"`，也不推断为模块、表单或弹窗。

- 仅允许相对地址、`http:`、`https:`、`tel:`、`mailto:`。
- `_blank` 增加 `rel="noopener noreferrer"`。
- 空地址或危险协议渲染为普通内容，不添加点击样式。
- 不使用内联 `onclick`，不把接口文本拼入可执行 JavaScript。

## 2. 平台运行时所有权

- 若页面存在 `<script data-gw-open-form-jump-runtime>` 或 `window.__gwOpenFormJumpReady`，直接复用。
- `module`、`openForm`、`popup` 由平台在 document 捕获阶段拦截和处理；模块本地事件不得再次 `preventDefault`、设置 `location.href`、调用 `scrollTo` 或打开弹窗。
- 表单、二维码、指定页面和指定内容最终由平台调用 `Utils.Dialog.open`。
- 不复制平台的模块查找/重试算法、表单注入逻辑、iframe loading、Markdown 转换或二维码适配。
- 不重复注入全局 `.gw-dialog-*` 样式。

## 3. 平台生成属性

以下属性用于识别最终 DOM 和排查问题，不是要求模块针对静态配置手工拼装：

- 通用：`data-gw-jump-type`、`data-gw-jump-href`、`data-gw-jump-target`。
- 小程序：`data-gw-mini-program-path`。
- 模块：`data-gw-module-page-url`、`data-gw-module-target-type`、`data-gw-module-name`、`data-gw-module-id`、`data-gw-module-selector`、`data-gw-module-offset`。
- 表单：`data-gw-jump-form-template`、`data-gw-jump-form-title`、`data-gw-popup-form-auto-close` 与对应 `<template>`。
- 弹窗：`data-gw-popup-type`、`data-gw-popup-title`、`data-gw-popup-summary`、`data-gw-popup-description`、`data-gw-popup-width`、`data-gw-popup-height`、内容模板、页面 URL 或二维码字段。

当修改现有已编译模块时，应保留这些平台属性及关联 `<template>` 的一致性；模板 key 按模块实例唯一，不与同页其他列表冲突。

## 4. 小程序安全例外

`miniProgram` 的 `$[key.href]` 会输出受控的 `javascript:jumpMall('/path')`。历史 `web/url` 的严格 `jumpMall` 链接也会被编辑器归一为 `miniProgram`。

- 静态平台占位符可以直接作为 `href`，不要先经通用 URL 过滤器误删。
- 若需要审查最终 DOM，只接受明确类型为 `miniProgram` 且能提取合法内部路径的严格 `jumpMall` 格式。
- 接口动态链接不得使用这一例外；任何来自接口的 `javascript:` 都按危险链接拒绝。

## 5. 本地事件边界

- 动态卡片可在当前根节点使用事件委托，但只负责卡片选择、统计或模块自身 UI。
- 从 `event.target` 向上寻找触发器时，验证节点仍属于当前实例。
- 兼容没有 `Element.closest` 的旧 WebView 时，写局部祖先查找函数，不加载整套 polyfill。
- 整卡点击要排除内部 `a`、`button`、`input`、`select`、`textarea`、`label` 与 `[data-no-card-jump]`。
- 一次点击只允许产生一个导航、一个弹窗或一个模块滚动。

## 6. 验收

- 静态 `jump` 配置使用点号字段，没有 `JSON.parse($[key])`。
- 接口动态详情链接仍是安全真实 `<a>`，没有伪造复杂点击类型。
- `module`、`openForm`、`popup` 只执行一次。
- `miniProgram` 可正常调用平台桥接，同时没有放开任意脚本链接。
- 同页多个列表的事件、模板 key 和弹窗内容互不冲突。
- LTD 已有运行时和全局弹窗样式没有被重复注入或覆盖。
