# 渲染、媒体与点击操作

## 文本和富文本

- 普通文本始终使用 `textContent`。
- `textarea` 内容默认按纯文本换行显示。
- Markdown 或 HTML 只有在控件明确声明格式且经过平台可信转换/净化后才可注入。
- 不把接口内容、标题、属性值直接插入未转义模板字面量。

## 媒体

- 图片设置 `alt/loading="lazy"/decoding="async"`，加载失败显示局部占位。
- 视频默认不强制自动播放；自动播放时必须静音并使用 `playsinline`。
- URL 为空或非法时隐藏媒体节点，不影响文字内容。
- 图标优先内联 SVG；装饰图标使用 `aria-hidden="true"`，图标按钮提供可访问名称。

## 点击操作

静态点击配置使用 `input_type: "jump"`：

```html
<a href="$[action.href]" target="$[action.target]">查看详情</a>
```

- 支持平台的 `none/web/url/module/miniProgram/openForm/popup/mobile/email`。
- 不自行复制平台 `data-gw-*` 映射器或 `Utils.Dialog` 全局运行时。
- 接口返回的动态 URL 只允许相对地址、`http/https/tel/mailto`。
- `_blank` 补 `rel="noopener noreferrer"`。
- 无有效动作时移除手型、hover 位移和键盘跳转。

## 状态

接口型模块至少包含 loading、success、empty、error。搜索和筛选改变时重置页码；请求失败保留工具栏和重试入口。静态模块无需伪造 loading 状态。
