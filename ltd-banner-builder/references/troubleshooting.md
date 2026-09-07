# Banner 空白与媒体不显示排查

## 先区分现象，不猜原因

| 现象 | 可确认的证据 | 优先检查 |
| --- | --- | --- |
| 模块根节点都不存在 | Elements 中找不到 `.ltdBannerYYYYMMDD` | HTML 是否粘贴完整、是否保存到正确模块、模块是否被隐藏 |
| 只剩背景色/遮罩，图片、文案、空状态都没有 | 根节点存在，但脚本生成节点不存在 | JavaScript 是否语法错误；`root` 是否定位失败；脚本是否被平台拦截 |
| 出现稳定空状态 | 脚本已运行，归一化后为 0 项 | `$[slides]`/`$[video_slides]` 是否为空、解析失败、hidden 或媒体 URL 无效 |
| 上传缩略图可见，Banner 仍黑色/纯色 | 变量面板有媒体，`<img src>` 为空或请求失败 | 实际媒体对象结构、URL 提取优先级、网络状态/CORS/防盗链 |
| 编辑器可见，保存预览或发布为空 | iframe DOM 正常，前端源码/控制台异常 | 保存/发布状态、缓存、发布后变量替换、前端依赖差异 |
| 本地预览正常，LTD 全部为空 | 本地未经过平台变量替换 | 发布后源码中的占位符替换、jump 注入、LTD DOM 外壳差异 |

以上是诊断分支，不是仅凭截图即可下结论。必须用 DOM、源码、控制台或网络请求佐证。

## 已确认的致命模式：jump 直接注入 JavaScript

禁止：

```js
const buttonLink = $[button_link];
```

当跳转 href 为 `#new-arrivals` 时，发布替换可能生成：

```js
return #new-arrivals;
```

这不是字符串，而是非法 JavaScript，浏览器会在初始化前终止整个 script。结果就是根层/遮罩仍在，图片、标题、按钮和空状态全部不出现。

修复：使用根节点 `data-button-link-type/href/target` 和 `$[button_link.type/href/target]` 嵌套属性注入，再从 `dataset`/`getAttribute` 读取。发布后搜索源码，确保不存在 `return #`、`= #` 或裸的跳转地址。

## 图片上传后不显示

依次检查：

1. 变量面板的字段是否真的是 `slides` 且 `input_type: "imageList"`，不是普通文本或另一个未被 HTML 读取的 key。
2. 当前 `media_type` 是否为 `image`；视频模式不会读取 `slides`。
3. 页面保存后的 `$[slides]` 是否为数组/合法数组字符串，是否被后一次 JSON 导入覆盖。
4. 项目是否被 `hidden=true/1/"1"/"true"` 过滤。
5. 实际图片地址位于 `url/image/filepath/src/file/.../filepath_thumb` 中的哪一层。
6. 渲染后的 `<img src>` 是否非空且是安全相对或 HTTP(S) URL。
7. Network 中图片请求是否 200；若 403、404、混合内容或 CORS/防盗链失败，只降级当前 slide 并说明真实状态。
8. 遮罩透明度是否过高。遮罩会让图片变暗，但不会让 `<img src>` 消失；先区分加载失败与视觉过暗。

修复已有页面时，不要先重导 JSON。重导可能把刚上传的图片列表恢复为模板默认值；先备份当前配置，再只改必要文件。

## root 定位检查

编辑器 iframe 和发布前端都应使用双路径：

1. `document.currentScript.previousElementSibling` 是当前根节点时直接使用。
2. 否则从 `document.currentScript.closest('.gw-browse-module')` 查当前模块内根节点。
3. 两者都失败才返回；禁止全局选择第一个 Banner。

在控制台或临时诊断中核对 `script`、`previous`、`moduleHost`、`root`，但最终模块不要遗留全局调试变量或噪声日志。

## 四层验收顺序

### 1. 本地静态/语法

- JSON 可解析，key 唯一，列表 value/default_value 可再次解析。
- HTML 中所有根占位符都能在 JSON 中找到，jump 嵌套字段正确归并。
- JavaScript 在模拟变量替换后仍能解析。
- 搜索：未解析 `$[...]`、`return #`、`= #`、`innerHTML` 原始内容注入、Less、无限 Swiper 重试。

### 2. 编辑器 iframe

- 根节点存在，脚本生成 slide、标题、副标题、CTA 和指示器。
- 上传或替换图片后，当前 `<img src>` 与变量面板媒体一致。
- 三张都能切换且版式一致；修改每张主副标题变量后即时/保存后更新。
- 按钮常态、hover、focus 颜色和跳转控件可配置。

### 3. 保存预览

- 保存模块与保存页面后重新打开，不依赖编辑器未持久化的即时状态。
- 图片、文案、CTA 和轮播仍在；配置未被模板默认值覆盖。

### 4. 发布前端

- 发布后强制刷新；必要时确认 CDN/页面缓存更新时间。
- 检查最终源码/Elements，确保 jump 已变成属性字符串而不是裸 JavaScript。
- 检查控制台首个错误和 Network 的图片/视频/字体请求。
- 验证真实 CTA 跳转、`_blank` 安全属性、移动端比例和同页多实例。

如果某一层无法访问、没有登录态或用户未授权保存/发布，必须明确标为“未验证”，说明限制；不得用本地成功推断线上成功。

## 诊断与修改授权

- “排查/诊断”默认只做只读检查和原因说明，不自动保存、发布或覆盖变量。
- 用户明确要求修复时，可修改在范围内的 HTML/JSON；重新导入配置前仍要提示其可能覆盖当前媒体。
- 用户明确授权操作编辑器/发布后，才执行相应状态更改，并在完成后报告具体层级的结果。
