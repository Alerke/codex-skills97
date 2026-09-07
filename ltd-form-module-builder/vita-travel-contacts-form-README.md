# Vita Travel Contacts 表单模块

## 交付文件

- `vita-travel-contacts-form.html`：LTD 代码模块源码。
- `vita-travel-contacts-form-config.json`：可导入变量配置。

## 导入与绑定

1. 在 LTD 新版编辑器中导入 HTML 与配置 JSON。
2. 打开模块设置，在“表单”变量中选择 **ID 136511：联系我们**。
3. 在“提交按钮文字”中设置按钮文案，默认值为“提交”。
4. 确认该表单仍包含以下字段：
   - 姓名：`field_1647678186290`
   - 邮箱：`field_1786606430348`
   - 留言内容：`field_1786606455892`
5. 发布后分别测试桌面端、移动端、空值校验、合法邮箱和提交成功提示。

## 提交说明

模块直接输出 `fitForm` 的 preset，由 LTD runtime 负责取值、校验、Toast 和提交。绑定表单 136511 后，提交字段会按平台协议生成：

- `extensionField_136511[locationUrl]`
- `extensionField_136511[ltd_guest_token]`
- `extensionField_136511[website_id]`
- `extensionField_136511[gmac]`
- `form_id`
- `field_1647678186290`
- `field_1786606430348`
- `field_1786606455892`

其中 `locationUrl`、游客 token、网站 ID 和 gmac 由当前页面运行时实时生成，不应硬编码抓包值；姓名、邮箱和留言来自访客输入。

## 已核对的真实表单信息

- 表单 ID：`136511`
- 表单名：`联系我们`
- 说明：`欢迎咨询！`
- 网站 ID：`362426`
- 字段：姓名、邮箱、留言内容

表单变量保持为空是为了遵守 LTD 的表单选择流程，并避免把某个环境中的表单对象硬编码进通用模块。导入后请在变量面板手动选择 ID `136511` 的“联系我们”表单；模块源码无需修改。

“提交按钮文字”直接输出到模块自己的展示按钮，不再修改 preset 按钮的 DOM 文本。原 preset 按钮仅在视觉上隐藏；点击展示按钮时优先调用当前表单的 preset runtime，无法取得 runtime 时再触发原按钮，因此字段取值、校验、验证码、payload、禁用状态和 Toast 仍由 LTD 处理。
