# LTD Banner 平台规则

## 原生 CSS

- 参考模块中的 Less 只用于理解层级，不可原样交付。
- 将 `.ltdBannerYYYYMMDD { .swiper-container {} }` 展开为 `.ltdBannerYYYYMMDD .swiper-container {}`。
- 将嵌套 `@media` 移到顶层，并保留完整根类前缀。
- 输出 `data-banner-initial` 与 `data-banner-styles` 两段标准 CSS。
- 删除 Less CDN，不添加任何运行时编译器。

## 当前实例：强制双路径定位

LTD 编辑器 iframe 与发布前端的外层 DOM 可能不同。仅依赖 `closest('.gw-browse-module')` 或仅依赖前一兄弟节点，都可能导致 `root` 为空。脚本执行时必须立即捕获实例，并按前一兄弟节点优先、模块宿主回退：

```js
const script = document.currentScript;
const previous = script ? script.previousElementSibling : null;
const moduleHost = script && script.closest
  ? script.closest('.gw-browse-module')
  : null;
const root = previous && previous.classList && previous.classList.contains('ltdBanner20260821')
  ? previous
  : (moduleHost ? moduleHost.querySelector('.ltdBanner20260821') : null);

if (!root) return;
```

- 根类日期按当前模块改写，HTML 与 JavaScript 必须一致。
- 禁止回退到全局 `document.querySelector('.ltdBanner...')`，否则同页多实例会串用。
- setTimeout、Swiper 回调和事件回调只能闭包使用已经捕获的 `root`，不得再次读取 `document.currentScript`。
- 编辑器重复执行脚本时，先清理当前根节点保存的旧实例、定时器和监听。

## jump 变量注入边界

`input_type: "jump"` 是结构化对象，不是可直接拼进 JavaScript 的字符串。以下写法禁止：

```js
const link = $[button_link];
```

若 href 为 `#new-arrivals`，发布替换可能产生 `const link = #new-arrivals;`；在 `return` 表达式中则会出现 `return #new-arrivals;`。两者都会造成 JavaScript 语法错误，表现为 Banner 根层存在但内容、图片和空状态全部不渲染。

必须把嵌套字段注入 HTML 属性：

```html
<section class="ltdBanner20260821"
  data-button-link-type="$[button_link.type]"
  data-button-link-href="$[button_link.href]"
  data-button-link-target="$[button_link.target]">
</section>
```

再从当前实例读取：

```js
const rawButtonLink = {
  type: root.getAttribute('data-button-link-type') || 'none',
  href: root.getAttribute('data-button-link-href') || '',
  target: root.getAttribute('data-button-link-target') || '_self'
};
```

- 嵌套属性占位符在配置核对时归并到根 key `button_link`，不能误报缺少三个 JSON key。
- 文本/颜色属性仍应从 DOM 读取后校验，不能把用户输入直接拼入可执行代码。
- `$[slides]` 和 `$[video_slides]` 是平台列表数据，可在受控局部求值中读取；不要把这条特例错误套到 jump 对象上。

## 导入与保存顺序

建议顺序：

1. 先在代码编辑区粘贴并保存完整 HTML。
2. 再导入 JSON，检查变量类型、默认值和列表项。
3. 保存模块配置，再保存页面。
4. 分别打开保存预览和发布前端验证，发布后必要时强制刷新或清理页面缓存。

重新导入 JSON 可能覆盖当前变量值或已经上传的图片列表。修复已有页面前，先导出/备份现有配置；若只改 HTML，不要无必要重导 JSON。

## 依赖

- 复用 `window.Swiper`，不加载第二份 Swiper。
- 依赖尚未就绪时使用有界重试，例如 20 次 × 100ms。
- 重试前已经捕获 `root`；重试结束、实例被移除或超时后停止。
- Swiper 缺失、版本不兼容或初始化异常时，显示第一张可见 slide 并隐藏轮播增强。

## 兼容性

- 使用成熟 ES6，避免可选链、空值合并、对象展开、async/await、动态 import 和 `padStart`。
- `100vh` 写在 `100svh` 前作为 fallback。
- 使用 `CSS.supports('aspect-ratio', '16 / 9')` 前先检测 `window.CSS` 与 `CSS.supports`。
- 不支持 `aspect-ratio` 时按 `root.clientWidth / ratio` 设置当前容器高度，并用当前实例 resize handler 更新。
- 能力差异使用特性检测，不通过 user-agent 推断。
