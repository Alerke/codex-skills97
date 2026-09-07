# 平台运行与实例

## 宿主

代码会被插入 `.gw-browse-module` 内。通过 `document.currentScript` 向上定位当前宿主和根节点，禁止用全局选择器绑定所有同名模块。

```javascript
const script = document.currentScript;
const host = script && script.closest
  ? script.closest(".gw-browse-module")
  : null;
const root = host ? host.querySelector(".acFeature20260728") : null;
if (!root) return;
```

根类与宿主类必须唯一且稳定。业务样式从根类开始；只有平台尺寸、溢出或编辑器适配规则可以从带真实名称的宿主选择器开始。

## 样式

固定输出两个标准 CSS 样式块：

```html
<style data-module-initial></style>
<style data-module-styles></style>
```

不输出 `text/less`，不加载 Less CDN。响应式优先使用 `1024px/768px/576px`，但以实际布局为准。

## 请求

- 静态模块不请求接口。
- 接口型模块使用页面已有 `r()`。
- 请求参数按真实接口文档生成；平台通用接口通常携带 `website_id: localStorage.getItem("websiteId")`。
- 新筛选或搜索递增 `requestId`，只有最后一次响应可更新 DOM。
- 请求失败保留模块结构和重试入口。

## 成熟 ES6

鼓励 `const/let`、箭头函数、模板字面量、解构、默认参数、`Map/Set`。为旧 Safari/Chromium/WebView 避免未确认的可选链、空值合并、`async/await`、对象展开和新数组 API。
