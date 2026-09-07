# 产品列表状态、URL 与分页

## 1. URL 命名空间

同页可能存在多个列表。为每个实例生成稳定命名空间，例如：

```text
pl_<instanceKey>_cat
pl_<instanceKey>_page
pl_<instanceKey>_q
pl_<instanceKey>_sort
```

`instanceKey` 优先来自明确配置或宿主模块 id，再回退到模块根节点唯一序号。不要给所有实例固定使用 `cpcat_cat/cpcat_page`。

URL 只保存用户可理解的源状态：单个 `selectedCatId`、页码、关键词、排序 key。不要保存父分类展开后的逗号 id 集合或完整 `order` JSON。

## 2. 历史策略

必须明确选择一种策略：

- 需要浏览器后退/前进恢复筛选：用户操作使用 `history.pushState`，初始化修正使用 `replaceState`，并监听 `popstate`。
- 不希望筛选产生历史记录：全部使用 `replaceState`，不声明后退/前进可以逐步恢复筛选。

不要一边只用 `replaceState`，一边把 `popstate` 当作筛选历史的主要机制。

处理 `popstate` 时：

1. 读取当前实例命名空间参数。
2. 校验分类和页码。
3. 一次性更新状态。
4. 重绘分类选中态。
5. 发起一次列表请求。

## 3. 状态更新入口

所有交互通过统一入口更新：

```js
const updateState = (patch, options) => {
  // 合并并校验 patch。
  // 非翻页操作默认 page = 1。
  // 按策略同步 URL。
  // 发起最新请求。
};
```

- 分类、搜索、排序变化重置到第 1 页。
- 布局切换不请求数据，只更新 UI 和可选 URL。
- 页码变化保留当前分类、关键词和排序。
- URL 恢复使用 `syncUrl: false`，避免 popstate 循环写回。

## 4. 并发控制

不要使用以下模式：

```js
if (state.loading) return;
```

它会在旧请求期间丢弃用户最新的分类或页码操作。使用递增序号：

```js
const requestId = ++state.requestId;
state.status = 'loading';
const response = await requestList(params);
if (requestId !== state.requestId) return;
```

如果请求层支持取消，可同时取消旧请求。无论采用哪种方式，只有最新请求能更新 items、total、status 和 DOM。

## 5. 状态显示

- 初次加载：显示骨架或简洁 loading。
- 筛选/翻页加载：可保留旧内容并在列表区域显示局部 busy，避免闪空。
- 成功且有数据：显示列表，隐藏 empty/error。
- 成功但无数据：显示 empty，分页隐藏。
- 失败：显示 error 与重试，保留筛选工具栏。

骨架最短展示时间不是业务必要条件。只有实测发现闪烁时才加很短的延迟，并且不能阻塞最新请求切换。

## 6. 分页窗口

`totalPages = Math.ceil(total / pageSize)`。`total === 0` 或 `totalPages <= 1` 时隐藏分页。

页码窗口：

- PC 默认显示当前页附近最多 5 个页码。
- 窄屏最多显示 3 个页码。
- 窗口外始终保留第 1 页和最后一页，中间用省略号。
- 上一页、下一页使用真实 `disabled` 属性。
- 当前页使用 `aria-current="page"`。

跳页输入：

- 使用 `type="number"`、`min="1"`、`max=totalPages`。
- 点击确认或按 Enter 走同一个函数。
- 对输入取整并限制在有效范围；无效输入显示提示，不静默清空。
- 跳到当前页不重复请求。

## 7. 翻页后的视口

翻页成功后滚动到当前模块结果区域，不滚到整页顶部。计算固定顶部导航偏移，旧浏览器不支持平滑滚动时回退到立即滚动。

滚动应发生在新数据成功渲染后，而不是请求发出时；否则失败时用户会被无意义移动。

## 8. 分页事件

- 分页容器只绑定一次委托事件。
- 重绘分页只替换内部按钮，不重复绑定容器事件。
- 从 `data-page` 读取后进行有限整数校验。
- disabled、当前页和超出范围按钮不触发请求。
