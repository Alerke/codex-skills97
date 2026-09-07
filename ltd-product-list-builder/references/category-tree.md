# 产品与商品分类树实现

本规范提炼 `$[cat_id]` 输出的后台限定分类范围、递归分类树和父分类聚合查询方式。分类类型字段读取见 [`category-type.md`](category-type.md)。

## 目录

- [四个不同概念](#1-四个不同概念)
- [分类树基础函数](#2-分类树基础函数)
- [后台限定分类的提升规则](#3-后台限定分类的提升规则)
- [“全部”的语义](#4-全部的语义)
- [父分类筛选](#5-父分类筛选)
- [选中和展开](#6-选中和展开)
- [请求失败降级](#7-请求失败降级)
- [安全渲染](#8-安全渲染)

## 1. 四个不同概念

必须区分：

- `allowedIds`：由 `$[cat_id]` 直接输出的后台允许分类 ID。
- `allowedScopeIds`：将每个 allowed 分类递归展开为“自身 + 所有层级后代”后的有效查询范围。
- `selectedCatId`：用户当前点击的单个语义分类；URL 只保存它。
- `queryCatIds`：实际发给接口的分类集合，可能包含父分类及全部后代。

不得用一个逗号字符串同时承担四种职责。

## 2. 分类树基础函数

集中提供纯函数：

- `findCategory(tree, id)`：递归查找分类。
- `findCategoryWithParents(tree, id)`：返回分类和完整祖先链。
- `collectDescendantIds(category)`：深度优先递归返回当前分类及所有层级后代 id，不只读取直接 `children`；使用 `Set` 去重并防止异常循环引用。
- `hasActiveDescendant(category, selectedCatId)`：决定祖先分组是否展开。
- `cloneAllowedSubtree(category, allowedSet)`：复制允许范围内的子树，不修改接口原对象。

所有 id 在比较前统一转成字符串。

```js
const collectDescendantIds = (category) => {
  const result = [];
  const seen = new Set();
  const visitedNodes = new Set();

  const walk = (node) => {
    if (!node) return;
    if (visitedNodes.has(node)) return;
    visitedNodes.add(node);
    const id = node.id === undefined || node.id === null ? '' : String(node.id);
    if (id && !seen.has(id)) {
      seen.add(id);
      result.push(id);
    }
    const children = Array.isArray(node.children) ? node.children : [];
    children.forEach((child) => walk(child));
  };

  walk(category);
  return result;
};

const expandAllowedScopeIds = (allowedIds, nodeById) => {
  const result = [];
  const seen = new Set();
  allowedIds.forEach((rawId) => {
    const node = nodeById.get(String(rawId));
    collectDescendantIds(node).forEach((id) => {
      if (!seen.has(id)) {
        seen.add(id);
        result.push(id);
      }
    });
  });
  return result;
};
```

## 3. 后台限定分类的提升规则

当 `allowedIds` 为空时，使用接口完整树。

`cat_id` 配置为空、未传或没有选择任何分类时，`allowedIds` 为空，表示分类不设限；列表应获取当前适配器的全部数据，分类 UI 保持“全部”状态。

当后台只选中子分类时：

- 将该子分类提升为展示树的顶层项，便于直接筛选。
- 保留它在允许范围内的后代。

当后台同时选中父分类和其子分类时：

- 只把父分类放在顶层。
- 子分类保留在父分类的 `children` 中。
- 不再把同一子分类重复提升到顶层。

当多个配置 id 重复或祖先重叠时，按后台配置顺序输出首次有效项，并通过 `seenIds` 去重。

实现时先为完整树建立 `id → { node, parents }` 索引，避免每个 allowed id 反复递归搜索父级。

`allowedScopeIds` 必须按 allowedIds 的配置顺序展开：找到每个节点后调用 `collectDescendantIds`，合并并去重。若后台只配置一个父分类，该父分类的所有子级、孙级及更深层级都属于允许范围；不能因为这些后代没有单独出现在 `$[cat_id]` 中而被过滤掉。

## 4. “全部”的语义

“全部”代表全部允许范围：

- `selectedCatId = ''`。
- 若 `allowedIds` 非空，`queryCatIds = allowedScopeIds`，因此后台配置父分类时“全部”也包含其全部后代。
- 若 `allowedIds` 为空，省略请求中的 `cat_id`。

不要为了查询方便把 `allowedIds.join(',')` 写回 `selectedCatId`，否则“全部”的选中态和 URL 会失真。

`show_all_button` 仅控制“全部”按钮是否出现在分类 UI：

```js
const showAllButton = readSwitch(true, '$[show_all_button]');

if (showAllButton) {
  const allButton = document.createElement('button');
  allButton.type = 'button';
  allButton.className = 'pl-category-all';
  allButton.setAttribute('data-category-action', 'all');
  allButton.setAttribute('aria-pressed', selectedCatId ? 'false' : 'true');
  allButton.textContent = t('all');
  categoryContainer.appendChild(allButton);
}
```

- 配置 key 固定为 `show_all_button`，`input_type` 使用 `switch`；常见值 `"1"` 显示、`"0"` 隐藏，必须通过 `readSwitch` 显式解析。
- 关闭时不生成按钮，或在已有静态节点上设置 `hidden`；不能只通过不可访问的透明度隐藏。
- 该开关不改变查询语义。按钮隐藏且 `selectedCatId === ''` 时，仍按上述规则查询全部数据或全部 `allowedScopeIds`。
- 关闭时不得自动选择第一个分类，也不得为制造 active 状态而改变 URL 或发起额外筛选请求。
- 开启时点击“全部”清空 `selectedCatId`、把页码重置为 1，并按全部允许范围请求；按钮文字使用 `t('all')`。
- `show_sidebar` 控制整个分类区，`show_all_button` 只控制其中的“全部”选项，两者不能互相替代。

## 5. 父分类筛选

用户选择父分类时：

1. `selectedCatId` 只保存该父级 id。
2. 从展示树或完整树找到该分类。
3. `queryCatIds = collectDescendantIds(category)`。
4. 若存在 `allowedIds`，与展开后的 `allowedScopeIds` 取交集，而不是与原始 allowedIds 取交集。
5. 将页码重置为 1 后发起最新请求。

用户选择叶子分类时，`queryCatIds` 只包含该叶子 id。

发送前按深度优先顺序去重并 `join(',')`。父级本身必须包含在结果中，例如 `1 → 2 → 3` 应发送 `1,2,3`；存在多个分支时必须包含每个分支的全部后代。

## 6. 选中和展开

- URL 恢复的 `selectedCatId` 必须存在于允许展示树内；否则清空并回到“全部”，不得自动选择首个分类。
- 当前分类添加 active 状态，所有祖先分组展开。
- 点击展开按钮只切换树的展开状态，不触发筛选。
- 点击分类名称才更新 `selectedCatId`、页码和产品请求。
- 展开状态属于 UI 状态，可与筛选状态分开保存；重新渲染时至少保证 active path 展开。

## 7. 请求失败降级

- 分类接口失败时显示局部分类错误或隐藏分类区，但继续加载列表。
- 若后台已有 `allowedIds`，分类接口失败、无法获知后代结构时可暂时用原始 ids 限制列表请求，并标记分类降级；这是唯一不能展开后代的例外，不能猜测不存在的子级 ID。
- 不因为分类为空而把主产品区误判为接口错误。

## 8. 安全渲染

- 分类名称优先用 `textContent`；批量模板使用模板字面量时，不能直接插入未经转义的分类名称。
- `data-id` 只写经过字符串化和属性安全处理的 id。
- 分类树按钮使用真实 `<button>`，同步 `aria-expanded`。
- 当前筛选按钮同步 `aria-pressed` 或 `aria-current`。
