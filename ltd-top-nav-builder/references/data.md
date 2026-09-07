# 顶部导航数据与安全渲染

顶部导航兼容 `/api/navCat` 和后台 `navList` 两种数据源。

## 数据源

默认接口：

```javascript
const fetchTopNav = () =>
  r({
    url: "/api/navCat",
    data: {
      website_id: localStorage.getItem("websiteId"),
      position: 1,
      language_type: localStorage.getItem("lang") || "zh-cn",
    },
  }).then((res) =>
    res && res.code === 0 && Array.isArray(res.data) ? res.data : null
  );
```

硬规则：

- 顶部导航固定传 `position: 1`。
- 使用 `code === 0` 判断成功。
- 携带 `website_id` 和当前 `language_type`。
- 不使用 `/api/website/navigation` 或 `code === 1`。
- 后台维护场景使用 `$[nav]`，对应 `input_type: "navList"`。
- 自定义语言跳转使用 `$[language_nav]`，同样对应 `input_type: "navList"`；必须递归过滤 `hidden/status`。

## 字段兼容

```javascript
const getNavField = (item, ...keys) => {
  for (const key of keys) {
    if (item && item[key] !== undefined && item[key] !== null) {
      return item[key];
    }
  }
  return "";
};

const getNavName = (item) =>
  getNavField(item, "title", "name", "label");

const getNavRemark = (item) =>
  getNavField(item, "remark", "description", "subtitle");

const isTruthyFlag = (value) =>
  value === true || value === 1 || value === "1" || value === "true";

const isNavHidden = (item) =>
  isTruthyFlag(item && item.hidden) ||
  (item && (item.status === 0 || item.status === "0"));

const getNavChildren = (item) =>
  (item && (item.children || item.subNav || item.subMenus)) || [];

const getVisibleNavItems = (items) =>
  (Array.isArray(items) ? items : []).filter((item) => !isNavHidden(item));

const getVisibleNavChildren = (item) =>
  getVisibleNavItems(getNavChildren(item));
```

每一级递归都过滤隐藏节点，不能只过滤顶层。

## 自定义语言导航

`use_custom_language_jump` 控制语言数据源：

- 开启：只读取 `language_nav`，不再请求 `/shop/frontend/languageList`。
- 关闭：忽略 `language_nav`，请求平台语言列表。
- 配置为空、解析失败或过滤后少于 2 项时隐藏语言入口，不阻塞主导航。
- `language_nav.id` 作为语言代码，`title` 作为显示名，`jump.href/target` 作为切换目标。
- 点击前写入 `localStorage.lang`；存储失败仍可执行安全跳转。
- 自定义列表与主导航共用链接净化、`_blank` 的 `rel` 处理和隐藏节点过滤。

## 跳转与图标

```javascript
const getNavLink = (item) => {
  if (item && item.jump) {
    if (typeof item.jump === "string") return item.jump;
    return item.jump.href || item.jump.url || "javascript:void(0);";
  }
  return getNavField(item, "link", "href", "url") || "javascript:void(0);";
};

const getNavTarget = (item) => {
  if (item && item.jump && typeof item.jump === "object") {
    return item.jump.target || "_self";
  }
  return (item && item.target) ||
    (/^https?:\/\//i.test(getNavLink(item)) ? "_blank" : "_self");
};

const getNavIcon = (item, selected = false) =>
  selected
    ? getNavField(item, "hoverIcon", "select_icon", "activeIcon")
    : getNavField(item, "icon", "default_icon");

const getIconUrl = (icon) => {
  if (!icon) return "";
  if (typeof icon === "string") return icon;
  if (icon.value) return getIconUrl(icon.value);
  return icon.url ||
    icon.src ||
    (icon.file && icon.file.url) ||
    (icon.image && icon.image.url) ||
    "";
};
```

## 链接安全

```javascript
const sanitizeNavHref = (href) => {
  const value = String(href || "").trim();
  if (!value) return "javascript:void(0);";
  if (
    /^(?:javascript|data|vbscript):/i.test(value) &&
    value !== "javascript:void(0);"
  ) {
    return "javascript:void(0);";
  }
  return value;
};

const applyNavAnchor = (anchor, item) => {
  anchor.href = sanitizeNavHref(getNavLink(item));
  anchor.target = getNavTarget(item);
  if (anchor.target === "_blank") {
    anchor.rel = "noopener noreferrer";
  }
  anchor.textContent = getNavName(item);
  const remark = getNavRemark(item);
  if (remark) anchor.title = remark;
};
```

- 名称使用 `textContent`。
- `remark` 使用 `title` 或独立文本节点。
- 图标使用 `img.src`。
- 不把配置内容拼进 `innerHTML`。
- 有真实链接的父级保留跳转；展开操作使用独立按钮。

## 当前页与递归

- 当前 URL 命中子级时，父级同步 active。
- 移动端默认展开 active 祖先。
- PC 默认支持三级；移动端可递归更多层级。
- 三级菜单根据视口空间决定向左或向右展开。

## 降级顺序

1. `navList` 有有效数据时直接使用。
2. 未配置时先显示 fallback，再请求 `/api/navCat`。
3. 接口成功后替换当前实例菜单。
4. 解析失败、接口失败或空数据时保留 fallback。
5. 不隐藏整个导航。

## 检查清单

- [ ] API 和 `navList` 两套字段都可渲染。
- [ ] 每一级都过滤 `hidden/status`。
- [ ] `remark`、默认图标和选中图标均已兼容。
- [ ] 危险协议被拦截，新窗口链接带 `rel`。
- [ ] 配置失败或接口失败不会隐藏整个导航。
