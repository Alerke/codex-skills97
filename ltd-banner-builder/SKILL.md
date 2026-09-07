---
name: ltd-banner-builder
description: 创建、重构、审查或排查 LTD 建站平台代码模块中的图片或视频 Banner、首屏横幅和媒体轮播。适用于新编辑器 imageList/videoList、图片 slides、video_slides、标题副标题与 CTA 叠层、三张独立文案、按钮及跳转、按钮悬浮颜色、分段轮播指示器、全屏或 PC/移动端比例、渐变遮罩、多实例、Swiper 降级、编辑器或发布前端空白、变量注入错误、旧版 Safari/Chromium/WebView 兼容和可直接导入配置 JSON；不用于商品详情相册或后台广告管理。
---

# LTD Banner Builder

## 边界与默认档位

- 图片模式使用 `slides + imageList`，视频模式使用 `video_slides + videoList`；由 `media_type` 明确选择。
- 同一外壳处理空数据、单项和多项；图片与视频分别归一化后进入共用 slide 模型。
- 标准三张营销/品牌 Banner 默认使用“32 项增强档”：18 项平台基线 + 14 项常用扩展。
- 用户明确要求精简、已有模块只需修复，或轮播数量不是三张时，可使用 18 项基线或按真实需求调整；不要为了凑 32 项制造无用变量。
- 三张以上且每张都要独立内容时，优先使用列表已有字段；若编辑器不能稳定编辑这些字段，必须先确认需要暴露的最大张数。
- 默认视觉能力是比例/全屏双模式、背景媒体、三张独立中文主副标题、统一 CTA、渐变遮罩和可点击分段指示器。
- 数字序号、箭头、圆点、缩略图、视差和粒子都不是默认项；只有用户或参考设计要求时才加入。
- 不默认把 imageList 与 videoList 合并成混排轮播；需要混排时必须取得统一媒体列表的真实结构和排序字段。
- 只生成 HTML、原生 CSS 和成熟 ES6 JavaScript；不设计 Python、后端或构建工程。
- 默认同步交付完整模块 HTML 与可直接导入的配置 JSON。
- 参考站只用于分析构图、层级、留白、色彩和交互，不复制品牌 Logo、受版权保护的图片或字体文件；优先使用用户素材、明确许可素材或按需生成的新素材。

## 必读路由

实现前完整读取相关文档：

1. 始终读取 [`references/platform.md`](references/platform.md)：原生 CSS、实例定位、跳转注入、导入顺序和兼容性。
2. 图片模式读取 [`references/image-list.md`](references/image-list.md)；视频模式读取 [`references/video-list.md`](references/video-list.md)；混合需求两者都读。
3. 轮播、响应式高度或字体排版读取 [`references/runtime.md`](references/runtime.md)。
4. 新建配置或修改变量时读取 [`references/config.md`](references/config.md)。
5. 出现编辑器空白、上传图片不显示、保存后丢失或前端空白时读取 [`references/troubleshooting.md`](references/troubleshooting.md)。

冲突时按 `SKILL.md → platform.md → image-list.md → video-list.md → runtime.md → config.md → troubleshooting.md` 处理。

## 输出合同

```html
<style data-banner-initial>原生首屏 CSS</style>
<style data-banner-styles>原生业务 CSS</style>
<!-- 当前模块 HTML -->
<script>当前实例 JavaScript</script>
```

- 不输出 `<style type="text/less">`，不加载 `less.js` 或其他运行时样式编译器。
- 新建标准三张 Banner 时同步输出完整 32 项配置 JSON；精简档输出完整 18 项基线 JSON。
- 每项包含 `key/label/value/default_value/input_type`。
- `slides` 与 `video_slides` 的 value/default_value 必须是可再次 `JSON.parse` 的数组字符串。
- HTML 根占位符与 JSON key 必须一一对应；jump 使用嵌套属性占位符，计数时归并为对应根 key。
- 交付时分别报告：本地语法/静态检查、编辑器 iframe、保存预览、发布前端。没有条件验证的项目必须明确写“未验证”和原因。

## 硬规则

### 样式、尺寸与中文字体

- 根类使用 `.ltdBannerYYYYMMDD`，子级使用 `.ltd-banner-*`。
- 把参考 Less 的嵌套选择器和媒体查询展开为标准 CSS；所有业务选择器从当前根类开始。
- 默认非比例模式使用 `100vh` 后接 `100svh` 并设置合理最小高度。
- PC 比例模式仅在 `min-width: 769px` 生效，移动比例模式仅在 `max-width: 768px` 生效。
- 标准横幅默认建议 `pc_ratio_mode=1`、`pc_aspect_ratio=21/9`，避免超过普通电脑一屏；若参考设计或用户有明确比例，以其为准。
- 比例模式优先使用 `aspect-ratio`；旧环境用当前实例宽度和已解析比例计算高度。不要重新引入旧版固定高度 key。
- 中文标题优先使用思源宋体栈，正文、按钮优先使用思源黑体栈并提供系统中文字体回退；未经授权不打包商业字体文件。
- 字体栈不等于字体资源已安装。需要像素一致时，必须让站点自托管已获许可的思源字体文件，并明确说明未托管时会回退。
- 标题、颜色、遮罩、内容偏移、比例、按钮及指示器颜色通过当前根节点 CSS 变量设置。
- 图片和视频使用绝对定位、`width/height: 100%`、`object-fit: cover`；减弱动效环境取消非必要动画。

### JavaScript 与当前实例

- 使用普通 script 可解析的成熟 ES6；未确认环境时避免可选链、空值合并、对象展开、`async/await`、动态 import 和 `padStart`。
- 脚本首次执行时立即捕获 `document.currentScript`，按“脚本前一兄弟根节点 → 最近 `.gw-browse-module` 内根节点”双路径定位当前实例；不得全局查找第一个 Banner。
- 必须执行 `if (!root) return;`；异步回调不得再次读取 `document.currentScript`。
- 不使用固定 id、全局状态或未隔离选择器；不重复引入平台已有的 jQuery、Vue、Swiper 或 Less。
- Swiper 等待必须有最大次数/时长；超时后展示第一张，禁止无限重试。
- 保存 Swiper、重试定时器、requestAnimationFrame 和事件引用；销毁或重建时完整清理。

### 变量注入与跳转

- `$[slides]`、`$[video_slides]` 是列表数据，可在局部求值中读取并兼容数组/JSON 字符串。
- `input_type: "jump"` 的对象绝不能以 `$[button_link]` 直接插进 JavaScript。发布时它可能被替换为裸 `#anchor`，生成 `return #anchor;` 并让整个模块语法错误。
- jump 必须通过 HTML 属性注入：`$[button_link.type]`、`$[button_link.href]`、`$[button_link.target]`，再从当前根节点 `dataset` 读取。
- 归一化 `type/href/target`；`none` 或空地址不可点击；`web/url` 只允许安全相对或 HTTP(S) URL；`mobile/email` 安全补 `tel:/mailto:`。
- `_blank` 补 `rel="noopener noreferrer"`，拒绝 `javascript:/data:/vbscript:`。
- imageList 内嵌 jump 不会自动获得根级 jump 的运行时注入；复杂 `openForm/popup/module/miniProgram` 未实测时降级为不可点击。

### 图片、视频与内容

- `media_type` 只接受 `image/video`；缺失或非法时回退 `image`。
- 图片只读取 `$[slides]`，视频只读取 `$[video_slides]`；另一份列表不渲染、不参与总数。
- 显式空数组保持为空；过滤 `hidden`，不能用 `Boolean("0")`。
- 图片 URL 兼容字符串及常见嵌套媒体对象；至少按 `url → image → filepath → src → filepath_thumb` 回退并逐级校验。
- 可复用增强模板为避免夹带第三方图片，`slides` 默认是空数组；实际交付可见 Banner 时必须换成用户素材、明确许可素材或生成素材，不能直接把参考站图片写进 JSON。
- 标准三张增强档使用 `slide_1_title/subtitle` 至 `slide_3_title/subtitle`；变量值包括空字符串都优先于列表文案，空值可用于隐藏。
- 超出变量覆盖范围时，文案回退 `title → name`、`subtitle → desc → description`。
- 每张 slide 都渲染相同内容版式和 CTA 容器，不得只有第一张有标题、副标题、按钮。
- 默认 32 项档使用统一 CTA 文案、跳转、常态色、悬浮色；若设计要求每张按钮颜色或流体渐变不同，使用 config.md 的可选“逐张 CTA 高级档”，并保留全局回退。
- 不直接把原始标题、副标题或 URL 插入 `innerHTML`；优先 DOM API 与 `textContent`。图片失败只降级当前 slide。
- 视频遵循 `playsinline`、静音自动播放、Promise 拒绝捕获、非活动项暂停和控件不可被透明链接遮挡等规则。

### 配置容错与轮播

- switch 显式识别；数值必须有限并限制范围；遮罩和偏移的 `0` 是合法值。
- 字重、颜色、比例、URL 都要校验；任一配置错误只回退当前项。
- 0 张显示稳定空状态或在前台隐藏内容区；1 张静态展示并隐藏指示器；2 张以上才启用 Swiper。
- 默认多图使用 `fade + crossFade` 和无数字的分段线指示器；每段可点击、有焦点态，活动段显示计时填充。
- 分段线基础色和活动色分别由 `indicator_color`、`indicator_active_color` 控制；只有参考设计明确使用数字时才输出数字进度。
- 图片自动切换由 `autoplay/autoplay_delay` 控制；视频自身播放策略不能绕过浏览器静音限制。
- 页面隐藏、键盘焦点进入或减弱动效时暂停/关闭非必要自动播放。

## 配置档位

### 18 项平台基线

`media_type`、`slides`、`video_slides`、`autoplay`、`autoplay_delay`、`title_font_size`、`subtitle_font_size`、`title_font_weight`、`text_color`、`subtitle_color`、`overlay_opacity`、`content_bottom`、`content_left`、`mobile_ratio_mode`、`mobile_aspect_ratio`、`pc_ratio_mode`、`pc_aspect_ratio`、`show_overlay`。

### 标准三张增强档：再加 14 项，共 32 项

- 独立文案 6 项：`slide_1_title/subtitle`、`slide_2_title/subtitle`、`slide_3_title/subtitle`。
- CTA 与指示器 8 项：`button_text`、`button_link`、`button_background_color`、`button_text_color`、`button_hover_background_color`、`button_hover_text_color`、`indicator_color`、`indicator_active_color`。

不要混入旧版 `banner_list/transition_speed/show_navigation/show_pagination/pause_on_hover/desktop_height/tablet_height/mobile_height`。

## 工作流

1. 检查现有模块、设计参考、目标语言、预期张数和目标位置；诊断任务先读取源代码与现象，不直接猜原因。
2. 选择 18 项基线、32 项增强或逐张 CTA 高级档，并使 HTML 占位符与 JSON 同步。
3. 只归一化当前 `media_type` 对应列表，生成每张一致的背景、文案和 CTA 结构。
4. 展开原生 CSS，实现全屏/PC 比例/移动比例及旧浏览器 fallback。
5. 按 0/1/2+ 选择空、静态或 Swiper 路径；实现有界依赖等待、分段指示器、媒体管理和清理。
6. 对 jump 使用属性注入，对文本使用 DOM API；完成静态语法和占位符检查。
7. 若可访问，依次验证编辑器 iframe、保存预览和发布前端；发布空白时检查发布后源码与控制台，不以本地预览代替。
8. 交付完整 HTML、可导入 JSON、验证结果和未验证项。重新导入 JSON 前提醒备份当前配置，避免覆盖已上传媒体。

## 最终验收

- [ ] `slides`/`video_slides` 类型与数组字符串可解析，当前媒体模式只启用对应列表。
- [ ] 配置档位正确：18 项基线、32 项标准增强，或已说明的自定义高级档；没有旧版 key。
- [ ] 三张标准 Banner 都有相同文案/CTA 版式，六个独立文案变量可修改且空值可隐藏。
- [ ] CTA 文案、跳转、常态色、悬浮色和指示器颜色均可配置；逐张高级样式按需启用。
- [ ] jump 没有以完整对象直接插进 JavaScript；发布替换后不存在 `return #...`、未解析 `$[...]` 或语法错误。
- [ ] 双路径实例定位有效，同页多实例的状态、计时器、指示器和 Swiper 互不影响。
- [ ] 图片上传后能从实际媒体对象提取 URL；失败仅影响当前 slide，并有可识别降级态。
- [ ] 中文标题/正文使用思源字体栈和系统回退；没有未经授权的字体文件或品牌图片素材。
- [ ] 初始与业务样式均为原生 CSS；全屏、PC 比例和移动比例边界正确，标准横幅不会无故超过一屏。
- [ ] 0/1/2+ 分别进入空、静态和轮播；默认指示器为无数字分段线，单图隐藏。
- [ ] 视频 poster、playsinline、布尔属性、播放失败、非活动暂停和控件交互处理正确。
- [ ] Swiper 缺失或失败时仍显示第一张，异步回调不读取失效的 `document.currentScript`。
- [ ] `overlay_opacity=0`、`content_bottom=0`、`content_left=0` 保持为 0。
- [ ] 已分别记录本地检查、编辑器 iframe、保存预览和发布前端结果；无法验证的项目明确说明原因。
