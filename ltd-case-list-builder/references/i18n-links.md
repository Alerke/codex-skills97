# 案例多语言与链接

- 多语言配置固定使用 `key: "i18n"` 和 `input_type: "i18n"`。
- 语言优先读 URL `editor_language_type`，再读 `localStorage.lang`，最后 `zh-cn`。
- 标准 key 为 `zh-cn/zh/en/kr/ru/jp`；每个文案逐键回退到 `zh-cn` 和内置中文。
- 请求语言与 UI 语言保持一致。

详情链接优先级：

1. 安全的 `detail_link`。
2. 安全的 `defined_link`。
3. `/case/${encodeURIComponent(String(id))}`。
4. 无 id 时不可点击。

仅允许 http、https、站内相对路径和 hash；任务明确需要时允许 mailto/tel。拒绝任意脚本协议。`_blank` 补 `rel="noopener noreferrer"`。
