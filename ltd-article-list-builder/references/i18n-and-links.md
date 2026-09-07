# 多语言与链接

## 多语言

配置根项必须为：

```json
{
  "key": "i18n",
  "input_type": "i18n"
}
```

运行时 `$[i18n]` 是对象：

```js
const langMap = {
  "zh-cn": "zh-cn",
  "zh": "zh",
  "zh-tw": "zh",
  "zh-hk": "zh",
  "en": "en",
  "ko": "kr",
  "kr": "kr",
  "ru": "ru",
  "ja": "jp",
  "jp": "jp"
};
```

语言优先级：

1. URL `editor_language_type`
2. `localStorage.lang`
3. `zh-cn`

按键回退顺序：

当前语言 → `zh-cn` → 模块内置中文。

至少包含标题、搜索占位、全部、加载、空数据、加载失败、重试、上一页、下一页等键。标题不应因 type 改成视频、招聘等而虚构业务名称；如需自动切换，必须为每个 type 提供明确 i18n key。

## 文章详情链接

接口动态详情链接不是配置面板的静态点击操作：

- 有安全响应链接时使用响应链接。
- 否则用 `/article/{id}`。
- 只允许 `http:`、`https:`、站内相对路径、hash；按任务需要允许 `mailto:`/`tel:`。
- 拒绝任意 `javascript:`、`data:`、`vbscript:`。

## 平台点击操作

模块标题、查看更多等静态按钮需要后台操作时，使用一个 `input_type: "jump"` 根项：

- HTML 优先写 `$[more_link.href]`。
- 按需写 `$[more_link.target]`。
- 不把 `$[more_link]` 当 JSON 解析。
- 复用平台注入的 `data-gw-*` 和弹窗运行时，不复制完整 Dialog 实现。
- 仅平台明确归一化的 `miniProgram` 可使用严格 `javascript:jumpMall('路径')` 格式，不能借此放行其他脚本。
