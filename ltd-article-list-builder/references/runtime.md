# 文章列表运行时

## 初始化顺序

1. 立即捕获 `document.currentScript`。
2. 定位当前模块宿主与 `.articleListYYYYMMDD` 根节点。
3. 独立解析每个配置；记录局部配置错误但不中断其他配置。
4. 归一化语言与文章 type。
5. 渲染稳定加载壳。
6. 分类和首屏列表可并行请求。
7. 分类失败时隐藏或降级分类控件，文章列表继续运行。
8. 每次筛选、搜索、排序、翻页都经同一个 `loadList()`。

## 实例状态

建议最小状态：

```js
{
  page: 1,
  pageSize: 12,
  total: 0,
  selectedCatId: "",
  allowedScopeIds: [],
  keywords: "",
  sortBy: "published_at",
  sortDirection: "desc",
  requestSeq: 0,
  destroyed: false
}
```

`selectedCatId` 是用户语义选择，`queryCatIds` 在请求前由分类树计算，二者不要混为一个字段。

## 并发与状态

- 请求前递增 `requestSeq` 并捕获本次序号。
- 响应到达后仅在序号仍为最新且实例未销毁时更新 DOM。
- 搜索、分类或排序变化先把 `page` 重置为 1。
- 状态只允许 loading、success、empty、error 中一个生效。
- 错误状态保留搜索和分类工具栏，提供当前实例内重试按钮。
- 不用一个 `loading` 布尔值直接丢弃用户最后一次操作。

## 渲染

- 静态卡片壳可用模板字面量。
- 接口文本优先用 `textContent`，URL 经协议校验后赋给 DOM 属性。
- 如果批量生成模板，先用独立 `escapeHtmlText`、`escapeHtmlAttr` 和 `safeUrl` 处理每个值。
- 文章 id 从响应进入适配器时立即使用 `String()` 归一，之后禁止数值化；即使当前示例仍在安全整数范围内，也要保持接口的字符串标识语义并兼容未来更大 ID。
- 分类名称从分类树的 `Map<string, node>` 按字符串化 `cat_id` 解析，响应没有分类名称时保持为空。
- 卡片摘要只使用 `abstract`；完整 `content` HTML 默认不进入列表 DOM。
- 主图按 `thumbnail` 再 `file` 回退，媒体对象 `id/is_image` 为 0 不能覆盖 URL 有效性判断。
- 整卡链接不得包裹另一个 `<a>` 或按钮；有独立操作时使用非链接卡片与事件排除。
- 使用 `DocumentFragment` 批量插入，避免逐项触发布局。

## 分页

- `totalPages = Math.max(1, Math.ceil(total / pageSize))`，空数据时隐藏分页。
- 当前页超出总页数时回到最后有效页并最多补发一次请求，避免循环。
- 页码、上一页、下一页使用真实 `<button>`，正确设置 disabled 与 `aria-current`。
- 加载更多模式追加统一模型；普通分页模式替换列表，不能混用。

## 销毁

- 移除当前实例绑定的事件、定时器、媒体查询监听和全局监听。
- 将 `destroyed` 设为 true，使迟到响应失效。
- 不清理其他模块或第三方全局对象。
