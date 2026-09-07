---
name: ltd-form-module-builder
description: 用于创建、改造或排查 LTD 表单代码模块。适用于表单配置驱动渲染、系统预设样式、代码模块样式、兼容两种样式、字段控件、布局、校验、验证码、提交、上传、地址联动、颜色选择器、表单注入 API、i18n 和 Toast 等场景；生成时应优先复用目标平台已有的表单预设函数、运行时、控件工具、地址工具和提交工具，而不是重复手写。
---

# LTD 表单模块创建规范

## 使用原则

创建 LTD 表单模块时，默认复用新版编辑器的表单 preset 输出。只有表单选择“代码模块样式”或用户明确要求完全自定义 DOM 时，才生成配置驱动的自定义渲染代码。

表单模块不应硬编码具体表单、字段、选项或提交字段。真实展示内容应来自表单变量；校验、验证码、提交、Toast、地址和运行时 API 优先由 `$[表单变量.preset]` 或 `$[表单变量.script]` 提供。

新建任务默认同时交付模块 HTML 和可直接导入的配置 JSON。表单根配置的 `input_type` 固定为 `form`，可从同目录 [`表单模块配置.json`](表单模块配置.json) 复制基线并在编辑器中选择真实表单。

## 工作流

1. 先确认能否直接输出 `$[表单变量.preset]`。可以则不要生成字段 DOM、验证码逻辑或提交函数。
2. 变量名必须原样使用，不能把 `fit_form` 自动转成 `fitForm`。
3. 需要拆分位置时使用 `$[表单变量.style] + $[表单变量.body] + $[表单变量.script]`，且 `.script` 必须在 `.body` 之后。
4. 只有代码模块样式读取 `$[表单变量.config]`，并按职责复用 preset API、控件约定、地址、i18n、提交和 `Utils.Toast`。
5. 代码模块样式必须为所有支持字段类型提供对应控件样式、状态样式和移动端表现。
6. 代码模块样式如自建 DOM，也必须提供与系统 preset 兼容的表单 API。
7. 缺少能力时只补最小实现，不复制已有 runtime。
8. 验证多实例、移动端、提交、校验、验证码、地址联动、语言切换和错误反馈。

## 按需读取

- 创建模块结构、脚本封装和 LTD 三段式代码时，读取 [module-structure.md](references/module-structure.md)。
- 判断系统预设样式、代码模块样式和预设函数调用策略时，读取 [preset-strategy.md](references/preset-strategy.md)。
- 需要调用注入到前台的表单 API、地址函数或外部 i18n 时，读取 [runtime-api.md](references/runtime-api.md)。
- 读取表单配置、解析当前表单、处理布局时，读取 [config-and-layout.md](references/config-and-layout.md)。
- 渲染字段、安装控件运行时、处理上传/颜色/地址/级联时，读取 [fields-and-controls.md](references/fields-and-controls.md)。
- 编写代码模块样式并覆盖全部控件类型时，读取 [control-styles.md](references/control-styles.md)。
- 实现值采集、校验、验证码和提交时，读取 [validation-and-submit.md](references/validation-and-submit.md)。
- 需要验收检查时，读取 [testing.md](references/testing.md)。

## 总规则

- 优先复用已有能力，不重复手写已有 DOM、校验、提交、上传、颜色选择器、地址联动逻辑。
- 默认优先使用完整 `$[表单变量.preset]`。
- 不要把 `$[表单变量.preset]` 放进 `<script>`、`<style>`、`textarea`、JSON 字符串或 HTML 注释中。变量只能在 HTML 内容区域（如 `<div>` 内部）直接输出。在注释中说明时使用纯文本描述，如"使用表单 preset 变量输出"。
- 不要生成旧 `<script type="application/json" class="ve-form-config">`、旧 provider DOM 或重复 runtime。
- 代码模块样式只自定义视觉层和必要结构；取值、校验、验证码、提交、地址、i18n、控件增强仍优先复用已有 runtime。
- 代码模块样式必须覆盖所有支持字段类型的控件外观、交互状态和移动端表现。
- 自定义样式使用浏览器可直接执行的原生 CSS，不使用 Less、Sass 或运行时样式编译器。
- 自定义脚本使用成熟 ES6、箭头函数和模板字面量；未确认环境时避免可选链、空值合并和 `async/await`。
- 表单注入运行时名称使用“变量名 + 表单 ID”，例如变量 `fitForm`、表单 `10126` 对应 `fitForm_10126`；不要假定一定叫 `fitForm` 或 `form`。
- 字段控件集中管理，不要散落在事件绑定或提交函数里。
- 默认不要生成提交函数；需要完全自定义提交时再保持独立函数，并与 preset payload、事件和 Toast 约定一致。
- skill 和生成模块都不包含 mock 表单数据；真实表单、字段、选项和提交 ID 必须来自后续配置。
- 只生成 HTML、原生 CSS 和 JavaScript，不创建 Python、后端、数据库或构建工程。
