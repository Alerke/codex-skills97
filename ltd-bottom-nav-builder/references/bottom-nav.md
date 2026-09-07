# 页脚/底部导航

本文件中的 `bottom-nav` 指站点页脚链接区，使用 `/api/navCat` 的 `position: 2`。它不是移动端底部固定 Tab；若用户明确要求“移动端底部 Tab 导航”，应作为独立组件处理。

## 默认能力

- 多列页脚链接分组。
- 支持二级或多级链接。
- 支持 API 数据和 `navList` 配置数据。
- 移动端可折叠分组。
- 当前语言和当前页高亮。
- API 失败时保留页脚结构和 fallback。

## HTML 骨架

```html
<section class="bottomNav20260424" aria-label="页脚导航">
  <div class="footer-inner">
    <nav class="footer-groups" aria-label="页脚链接"></nav>
  </div>
</section>
```

## 样式要点

- 输出 `<style data-nav-initial>` 与 `<style data-nav-styles>` 两个原生 CSS 样式块，保证页脚导航无需编译即可成立。
- 使用展开后的标准选择器，不使用 Less 嵌套、变量、mixin 或运行时编译器。
- 顶层容器使用 `bottomNav + 时间戳`。
- 子级类名使用 `footer-` 前缀。
- PC 端使用多列 grid。
- 移动端可改为单列折叠，分组标题作为按钮。
- 不给 `body` 写全局 `padding-bottom`；页脚导航在文档流中展示。

## 数据获取

```javascript
const fetchFooterNav = () =>
  r({
    url: "/api/navCat",
    data: {
      website_id: localStorage.getItem("websiteId"),
      position: 2,
      language_type: localStorage.getItem("lang") || "zh-cn",
    },
  }).then(({ code, data }) => (code === 0 && Array.isArray(data) ? data : null));
```

字段适配使用 [`../navigation.md`](../navigation.md) 中的统一 getter，并在每一级过滤 `hidden/status`。`remark` 可用于链接 `title`，图标兼容 `icon/default_icon` 与 `hoverIcon/select_icon`。

## 渲染建议

```javascript
const clearElement = (element) => {
  while (element && element.firstChild) element.removeChild(element.firstChild);
};

const renderFooterNav = (items = []) => {
  const root = container.querySelector(".footer-groups");
  if (!root) return;
  clearElement(root);

  getVisibleNavItems(items).forEach((group) => {
    const section = document.createElement("section");
    section.className = "footer-group";

    const title = document.createElement("button");
    title.className = "footer-title";
    title.type = "button";
    title.textContent = getNavName(group);
    title.title = getNavRemark(group) || "";
    title.setAttribute("aria-expanded", "false");

    const links = document.createElement("div");
    links.className = "footer-links";
    appendFooterLinks(getVisibleNavChildren(group), links);
    section.append(title, links);
    root.appendChild(section);
  });
};
```

链接递归渲染必须处理隐藏节点、target 和 rel，并用 DOM API 写入配置内容：

```javascript
const appendFooterLinks = (items, parent) => {
  getVisibleNavItems(items).forEach((item) => {
    const anchor = document.createElement("a");
    anchor.className = "footer-link";
    anchor.textContent = getNavName(item);
    anchor.title = getNavRemark(item) || "";
    applyLinkAttrs(anchor, item);

    const iconUrl = getIconUrl(getNavIcon(item));
    if (iconUrl) {
      const image = document.createElement("img");
      image.className = "footer-link-icon";
      image.src = iconUrl;
      image.alt = "";
      anchor.prepend(image);
    }
    parent.appendChild(anchor);

    const children = getVisibleNavChildren(item);
    if (children.length) {
      const nested = document.createElement("div");
      nested.className = "footer-links-sub";
      appendFooterLinks(children, nested);
      parent.appendChild(nested);
    }
  });
};
```

## 移动端折叠

- 分组标题用 `<button>`，同步 `aria-expanded`。
- 只折叠链接区，不移除链接 DOM。
- 默认可展开当前页所在分组。

## 检查清单

- [ ] 使用 `/api/navCat`，`position: 2`，成功码 `code === 0`。
- [ ] 不使用 `/api/website/bottom-navigation`。
- [ ] 不把页脚导航写成移动端固定底部 Tab。
- [ ] PC 多列、移动端单列或折叠。
- [ ] 每一级都过滤隐藏节点，并安全渲染 `remark` 与图标配置。
- [ ] API 失败不隐藏整个页脚导航。
- [ ] 初始布局和业务样式均为原生 CSS，不依赖样式编译。
