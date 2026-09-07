# 验收检查

## 输出检查清单

完成表单模块后检查：

- [ ] 已判断系统预设样式还是代码模块样式。
- [ ] 能直接使用 `$[表单变量.preset]` 的场景没有自定义 DOM、验证码或提交函数。
- [ ] `$[表单变量.preset]` 没有放进 `<script>`、`<style>`、`textarea` 或 JSON 字符串。
- [ ] 变量名保持原样，没有自动驼峰或下划线转换。
- [ ] 拆分输出时 `.script` 在 `.body` 之后。
- [ ] 代码模块样式按步骤复用配置、DOM、控件、runtime、验证码、提交能力。
- [ ] 代码模块样式已覆盖所有支持字段类型的控件外观。
- [ ] 代码模块样式已注册与系统 preset 兼容的 API。
- [ ] 运行时名称按“变量名 + 表单 ID”调用，没有假定一定叫 `fitForm` 或 `form`。
- [ ] 控件默认、hover、focus、disabled、error、loading 等状态有样式。
- [ ] 已优先复用目标环境已有表单函数。
- [ ] 没有重复手写已有 runtime。
- [ ] 没有硬编码具体字段、选项或真实表单 ID。
- [ ] 没有写入 mock 表单数据。
- [ ] 字段控件集中管理。
- [ ] 控件逻辑没有混入提交函数。
- [ ] 支持所有声明字段类型。
- [ ] 未知字段类型安全降级。
- [ ] 支持多实例。
- [ ] 支持移动端。
- [ ] 正确处理 `colSpan`、`offset`、`rowSpan`、`newRow`。
- [ ] 正确区分展示 ID 和提交 ID，runtime/提交使用 `submitFormId || id`。
- [ ] 上传提交附件 ID，不提交文件名或 File 对象。
- [ ] 验证码使用 `data-gw-fit-captcha` / `data-gw-captcha-button` 或直接复用 preset runtime。
- [ ] 验证码能找到手机号字段，手机号错误会触发字段 `.is-error` 和 `Utils.Toast.error`。
- [ ] 校验、提交、失败状态都有可见反馈，且提示优先使用 `Utils.Toast`。
- [ ] 提交 payload 中 `extensionField_表单ID` 是对象，不是 JSON 字符串。
- [ ] 地址联动优先调用 `getAddressRegions(parentId)` 或等价运行时 API。
- [ ] 外部按钮能通过 `ready()` 后调用 `submit()`。
- [ ] i18n 支持 `zh-cn`、`zh`、`en`、`kr`、`ru`、`jp`，并可通过外部 `setI18n()` / `mergeI18n()` / `setLanguage()` 修改。
