# Banner 视频列表

## 配置根项

```json
{
  "key": "video_slides",
  "label": "Banner 视频列表",
  "value": "[]",
  "default_value": "[]",
  "input_type": "videoList"
}
```

`$[video_slides]` 替换后通常是数组，旧 JSON 字符串只兼容解析一次。

## 已确认节点

```js
{
  url: 'https://example.com/banner.mp4',
  poster: 'https://example.com/banner-poster.jpg',
  name: '视频标题',
  description: '视频说明',
  autoplay: true,
  controls: false,
  muted: true,
  hidden: false,
  jump: {
    type: 'none',
    href: '',
    target: '_self'
  }
}
```

编辑器支持视频上传、封面、名称、描述、自动播放、显示控件、静音、隐藏、拖拽排序和点击操作。

## 归一化

- `url` 必须是安全相对或 HTTP(S) 视频地址。
- `poster` 必须通过图片 URL 校验；非法时省略。
- 标准三张增强档先读取 `slide_1_title/subtitle` 至 `slide_3_title/subtitle`；变量值包括空字符串都作为权威覆盖值。
- 没有独立变量覆盖时，使用 `title → name` 和 `subtitle → description → desc`；维护数据已有 `title/subtitle` 时必须保留。
- `autoplay/controls/muted/hidden` 使用显式布尔读取器，不能用 `Boolean("false")`。
- 自动播放为 true 时强制 `muted=true`，与编辑器行为保持一致。
- hidden 项和无有效视频 URL 的项不进入列表。
- jump 使用与图片 slide 相同的安全归一化。

## 文案与 CTA 版式

- 视频模式和图片模式复用同一内容层结构；三张视频都必须有相同的标题、副标题和 CTA 容器。
- 控件开启时，CTA 只占自身可见区域，不能用整张透明链接盖住原生控件。
- 标题、副标题、按钮文字和颜色使用同一套 32 项增强变量；需要逐张 CTA 颜色或渐变时使用 config.md 的可选高级档。

## DOM

```js
const video = document.createElement('video');
video.className = 'ltd-banner-video';
video.src = item.url;
video.playsInline = true;
video.muted = item.autoplay ? true : item.muted;
video.controls = item.controls;
video.autoplay = false;
video.preload = item.autoplay ? 'auto' : 'metadata';
if (item.poster) video.poster = item.poster;
```

先把 `autoplay` 设为 false，由活动 slide 管理器决定何时调用 `play()`，避免所有视频在 DOM 建立时同时播放。

## 播放规则

- 仅活动 slide 的视频允许播放。
- `play()` 返回 Promise 时捕获拒绝；失败后保持 poster，不能阻塞 Banner。
- 离开活动 slide 时执行 `pause()`；按设计决定是否安全重置 `currentTime=0`。
- 单视频且允许自动播放时可以 loop。
- 多视频不得逐项永久 loop；视频结束且全局 autoplay 开启时可切换下一项。
- 多视频的全局 `autoplay_delay` 是最大停留时间；视频提前结束可提前切换。
- `prefers-reduced-motion: reduce`、页面隐藏或 `navigator.connection.saveData=true` 时不主动播放。
- controls=true 时不能用透明整卡链接遮挡原生视频控件；点击操作限制在独立内容层。

## 混排边界

`imageList` 与 `videoList` 是两个独立编辑器组件，没有共同的跨列表排序。默认只支持 `media_type=image` 或 `media_type=video`。

只有用户提供统一混合媒体结构，或平台新增带 `type/order` 的混合组件时，才实现图片与视频交错排序；不得简单连接两个数组并声称顺序可编辑。
