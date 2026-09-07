# 页脚/底部导航数据规范

本文件定义 LTD 页脚链接区的数据源、字段适配、安全渲染和失败降级。它不包含顶部导航或移动端固定 Tab 规则。

## 数据源

默认使用 `/api/navCat`，固定传 `position: 2`：

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

- 成功码固定为 `code === 0`。
- 不使用 `/api/website/bottom-navigation` 等旧接口。
- 用户明确要求后台维护或模块配置时，使用 `navList` 注入值 `$[nav_list]`。

## `navList` 配置

```json
{
  "key": "nav_list",
  "label": "页脚导航",
  "input_type": "navList",
  "value": "[{\"id\":\"about\",\"title\":\"关于我们\",\"remark\":\"了解企业\",\"hidden\":false,\"jump\":{\"href\":\"/about\",\"target\":\"_self\"},\"icon\":{},\"hoverIcon\":{},\"children\":[]}]"
}
```

```javascript
const parseNavList = (value, fallback = []) => {
  if (!value || value === "$[nav_list]") return fallback;
  if (Array.isArray(value)) return value;
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : fallback;
  } catch (e) {
    return fallback;
  }
};
```

## 字段适配

同时兼容 `/api/navCat` 与 `navList`：

```javascript
const getNavField = (item, ...keys) => {
  for (const key of keys) {
    if (item && item[key] !== undefined && item[key] !== null) return item[key];
  }
  return "";
};

const getNavName = (item) => getNavField(item, "title", "name", "label");
const getNavRemark = (item) => getNavField(item, "remark", "description", "subtitle");

const isTruthyFlag = (value) =>
  value === true || value === 1 || value === "1" || value === "true";

const isNavHidden = (item) =>
  isTruthyFlag(item && item.hidden) ||
  (item && (item.status === 0 || item.status === "0"));

const getNavChildren = (item) =>
  (item && (item.children || item.subNav || item.subMenus)) || [];
const getVisibleNavItems = (items) =>
  (Array.isArray(items) ? items : []).filter((item) => !isNavHidden(item));
const getVisibleNavChildren = (item) => getVisibleNavItems(getNavChildren(item));

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
```

图标兼容字符串和图片控件对象：

```javascript
const getIconUrl = (icon) => {
  if (!icon) return "";
  if (typeof icon === "string") return icon;
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
  if (/^(?:javascript|data|vbscript):/i.test(value) && value !== "javascript:void(0);") {
    return "javascript:void(0);";
  }
  return value;
};

const applyLinkAttrs = (anchor, item) => {
  anchor.href = sanitizeNavHref(getNavLink(item));
  anchor.target = getNavTarget(item);
  if (anchor.target === "_blank") anchor.rel = "noopener noreferrer";
};
```

- 每一级递归都过滤隐藏节点，不能只过滤分组顶层。
- 名称和 `remark` 使用 `textContent` 与 `title`，不拼接不可信 HTML。
- 图标使用 `img.src`；无法提取 URL 时不显示。
- 父级有真实链接时保留跳转；空链接才使用分组兜底。

## 失败降级

```javascript
const loadFooterNav = (fallback) =>
  fetchFooterNav()
    .then((data) => (data && data.length ? data : fallback))
    .catch(() => fallback);
```

- API 失败或空数据时使用 fallback。
- 配置解析失败时使用 fallback。
- 保留 Footer 品牌、版权、联系方式和导航容器，不隐藏整个页脚。

## 检查清单

- [ ] `/api/navCat` 固定传 `position: 2`，并以 `code === 0` 判断成功。
- [ ] 请求携带 `website_id` 和当前 `language_type`。
- [ ] API 与 `navList` 字段均可渲染。
- [ ] 每一级都过滤 `hidden/status`。
- [ ] 安全处理 `remark`、图标、链接协议、`target` 和 `rel`。
- [ ] 失败时保留 Footer 结构和 fallback。
