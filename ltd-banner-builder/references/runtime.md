# Banner 媒体运行时

## 1. 尺寸模式

非比例模式：

- 容器使用 `height: 100vh; height: 100svh;`。
- 默认最小高度 600px；1440/1024 断点可降至 500/460px。
- 移动端保持视口高度，不设置会截断内容的 max-height。

比例模式：

- `data-pc-ratio-mode="1"` 在 769px 以上使用 `pc_aspect_ratio`。
- `data-mobile-ratio-mode="1"` 在 768px 以下使用 `mobile_aspect_ratio`。
- 比例模式取消视口高度和最小高度。
- 标准品牌/电商横幅建议默认 `pc_ratio_mode=1`、`pc_aspect_ratio=21/9`，避免 Banner 高度超过普通电脑一屏；参考设计有明确比例时以设计为准。
- 移动端是否比例模式必须结合文案长度和图片裁切决定，不能机械沿用 PC 的 21/9。
- 不支持 `aspect-ratio` 时由当前实例 JavaScript 计算高度。

比例解析支持 `/ : ： ／ ∶` 以及正小数。宽高必须为有限正数并限制异常比例；非法值回退 `16 / 9`。不要混回 `desktop_height/tablet_height/mobile_height` 等旧高度变量。

## 2. CSS 变量

基线变量：

```text
--ltd-banner-title-size
--ltd-banner-subtitle-size
--ltd-banner-title-weight
--ltd-banner-text-color
--ltd-banner-subtitle-color
--ltd-banner-content-bottom
--ltd-banner-content-left
--ltd-banner-pc-aspect-ratio
--ltd-banner-mobile-aspect-ratio
--ltd-banner-overlay-opacity
```

增强档再设置：

```text
--ltd-banner-button-background
--ltd-banner-button-color
--ltd-banner-button-hover-background
--ltd-banner-button-hover-color
--ltd-banner-indicator-color
--ltd-banner-indicator-active-color
```

响应式字号和偏移可以用 `clamp()` 或经过归一化后的计算值；任何原始配置都必须先校验再写入 CSS 变量。悬浮样式同时应用于 `:hover` 和 `:focus-visible`，并保留清晰焦点轮廓。

## 3. 中文字体与排版

推荐字体栈：

```css
font-family: "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", STSong, serif;
font-family: "Source Han Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", sans-serif;
```

- 主标题优先思源宋体，副标题和按钮优先思源黑体；参考设计明显为无衬线时，标题也可用思源黑体。
- 未经授权不内嵌或远程引用商业品牌字体。思源字体栈只是优先选择；用户设备或站点未提供字体文件时会回退。
- 需要一致渲染时，使用站点自托管且许可明确的思源字体文件，并在交付中说明资源来源和是否已验证加载。
- 中文标题使用自然断行，避免英文式超大字距和全大写；默认 `line-height: 1.05–1.2`、轻微或零字距。
- 副标题默认 `line-height: 1.5–1.8`，限制合适行宽；移动端降低字号、控制两到三行，避免压住 CTA。
- CTA 中文文案尽量短，保持左右内边距而非固定宽度。

## 4. 模式选择

```js
const mediaType = readEnum(rawMediaType, ['image', 'video'], 'image');
const activeItems = mediaType === 'video'
  ? normalizeVideoSlides(rawVideoSlides)
  : normalizeImageSlides(rawSlides);
```

仅 `activeItems` 参与渲染、总数、指示器和 Swiper。不要把两份列表拼接。

## 5. Swiper

- 0 张：稳定空状态；编辑器中宜显示可辨识的配置提示，发布前端可隐藏内容区。
- 1 张：静态 slide，隐藏指示器，禁用 loop/autoplay。
- 2+ 张：尝试 `fade`、`crossFade: true`、`loop: true`、`speed: 1200`。
- 图片模式自动播放由 `autoplay/autoplay_delay` 控制，`disableOnInteraction: false`。
- 视频模式中全局 autoplay 控制 slide 推进；每项 autoplay/muted/controls 控制视频自身。
- 使用 DOM 元素创建 Swiper，不依赖固定 wrapper id。
- 初始化前销毁当前根节点保存的旧实例。
- slideChange 后暂停全部非活动视频，再按当前项配置安全播放活动视频。

有界等待示例：

```js
const waitForSwiper = (attempt) => {
  if (!root.isConnected) return;
  if (typeof window.Swiper === 'function') {
    enhanceWithSwiper();
    return;
  }
  if (attempt >= 20) {
    renderStaticFallback();
    return;
  }
  retryTimer = window.setTimeout(() => waitForSwiper(attempt + 1), 100);
};
```

## 6. 视频活动项

- 单视频：不创建 Swiper；允许自动播放时设置静音、playsinline 和 loop。
- 多视频：不设置单项永久 loop；视频 ended 且全局 autoplay 开启时进入下一项。
- 活动视频 autoplay=false 时不强制播放，轮播仍可按全局 delay 推进。
- 活动视频 autoplay=true 时尝试播放；被浏览器拒绝时保留 poster。
- 控件开启的视频不得被透明整卡链接覆盖。

## 7. 默认分段线指示器

- 默认不显示 `01 / 03` 等数字，按可见 slide 数量动态创建等宽分段线。
- 单图隐藏整个指示器；多图每段使用 `<button type="button">`，带可访问名称，例如“切换到第 2 张”。
- 非活动段颜色使用 `indicator_color`，活动填充颜色使用 `indicator_active_color`。
- 点击或键盘激活分段线时切换对应真实 slide，并重置当前实例的计时进度。
- Swiper 存在 `autoplayTimeLeft` 时直接更新活动段填充；旧版使用当前实例 requestAnimationFrame 按 `autoplay_delay` 回退。
- autoplay 关闭或减弱动效时，活动段保持 100% 静态填充，不运行伪进度动画。
- 重建、slide 变化、页面隐藏和实例销毁时取消旧 animation frame，不能让多个计时器叠加。
- 只有用户或参考设计明确要求数字时，才启用数字序号；总数必须由实际可见数据计算，不能在 HTML 固定为 `03`。

视频模式的分段填充表示 slide 停留时间，不表示视频缓冲或完整播放进度。

## 8. 暂停与清理

- 页面隐藏时暂停可用的 autoplay，恢复可见后按配置继续。
- 页面隐藏或 slide 离开活动状态时暂停视频。
- 键盘焦点进入 Banner 时暂停，离开后恢复；操作指示器后按配置恢复。
- `prefers-reduced-motion: reduce` 时关闭自动播放和标题位移动画。
- 清理 Swiper、所有 video 的 ended 监听、retry timer、animation frame、resize、visibility、focus 监听。
- 编辑器重复执行脚本时不得叠加实例或事件。
