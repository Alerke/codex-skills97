# 顶部导航配置与导入 JSON

创建或交付顶部导航时，默认同时交付完整模块 HTML 和可直接导入 LTD 的 JSON 数组。只有用户明确说“只要代码”或“不要 JSON”时才省略 JSON。

无现有配置时，复制 [`sample-module/top-nav-sample.config.json`](sample-module/top-nav-sample.config.json) 作为基线，不从空数组临时拼装。

## 固定 26 项

| key | input_type | 说明 |
| --- | --- | --- |
| `nav` | `navList` | 多级导航菜单 |
| `use_custom_language_jump` | `switch` | 是否使用自定义语言跳转 |
| `language_nav` | `navList` | 自定义语言跳转列表 |
| `logo` | `image` | 默认 Logo |
| `stickyLogo` | `image` | 滚动态 Logo |
| `logo_link` | `jump` | Logo 跳转 |
| `phone` | `text` | 联系电话 |
| `email` | `text` | 联系邮箱 |
| `address` | `text` | 联系地址 |
| `sticky_mode` | `switch` | 是否吸顶 |
| `sticky_scroll_distance` | `number` | 滚动态切换距离 |
| `theme_color` | `color` | 主题色 |
| `nav_background_color` | `color` | 默认背景色 |
| `nav_blur` | `number` | 毛玻璃强度 |
| `nav_text_color` | `color` | 默认文字色 |
| `i18n` | `i18n` | 多语言界面文案 |
| `show_search` | `switch` | 是否显示搜索 |
| `search_link` | `jump` | 搜索跳转 |
| `show_login` | `switch` | 是否显示登录入口 |
| `sticky_nav_background_color` | `color` | 滚动后背景色 |
| `sticky_nav_text_color` | `color` | 滚动后文字色 |
| `logo_height_percent` | `number` | Logo 高度百分比 |
| `company_name` | `text` | 公司名称 |
| `company_name_color` | `color` | 默认公司名颜色 |
| `sticky_company_name_color` | `color` | 滚动后公司名颜色 |
| `mobile_menu_company_name_color` | `color` | 移动端菜单公司名颜色 |

不生成 `nav_list`、`search_action`、`contact_phone` 等同义旧 key。

## HTML 占位符

```javascript
const CONFIG = {
  nav: $[nav],
  useCustomLanguageJump: $[use_custom_language_jump],
  languageNav: $[language_nav],
  logo: $[logo],
  stickyLogo: $[stickyLogo],
  logoLink: $[logo_link],
  phone: $[phone],
  email: $[email],
  address: $[address],
  stickyEnabled: $[sticky_mode],
  stickyScrollDistance: $[sticky_scroll_distance],
  themeColor: $[theme_color],
  navBackgroundColor: $[nav_background_color],
  navBlur: $[nav_blur],
  navTextColor: $[nav_text_color],
  i18n: $[i18n],
  showSearch: $[show_search],
  searchLink: $[search_link],
  showLogin: $[show_login],
  stickyNavBackgroundColor: $[sticky_nav_background_color],
  stickyNavTextColor: $[sticky_nav_text_color],
  logoHeightPercent: $[logo_height_percent],
  companyName: $[company_name],
  companyNameColor: $[company_name_color],
  stickyCompanyNameColor: $[sticky_company_name_color],
  mobileMenuCompanyNameColor: $[mobile_menu_company_name_color],
};
```

占位符直接作为平台注入值使用，不放进字符串、注释或 JSON 文本。

## 解析

- `nav`、`language_nav` 是导航数组或导航数组 JSON 字符串。
- `use_custom_language_jump` 使用严格 switch 解析；开启时只使用 `language_nav`，关闭时才请求平台语言接口。
- `logo_link`、`search_link` 是 jump 对象或其 JSON 字符串。
- `i18n` 是对象或其 JSON 字符串。
- 图片可能是 URL、对象、带 `value` 的控件对象或 JSON 字符串。
- 解析失败使用 fallback，不阻止初始化。

```javascript
const parseSwitch = (value, fallback = true) => {
  if (value === "" || value == null) return fallback;
  return value === true || value === "1" || value === "true";
};

const parseNumber = (value, fallback = 0) => {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
};

const parseObject = (value, fallback) => {
  if (value === "" || value == null) return fallback;
  if (typeof value !== "string") return value || fallback;
  try {
    return JSON.parse(value) || fallback;
  } catch (error) {
    return fallback;
  }
};
```

## `nav` 与 `language_nav` 节点

```json
{
  "id": "home",
  "title": "首页",
  "jump": {
    "type": "web",
    "href": "/",
    "target": "_self"
  },
  "children": [],
  "remark": "",
  "icon": {
    "type": "image",
    "value": "",
    "name": ""
  },
  "hoverIcon": {
    "type": "image",
    "value": "",
    "name": ""
  },
  "hidden": false,
  "isBackend": false
}
```

## JSON 输出要求

- 顶层必须是数组。
- 必须包含完整 26 项，每个 key 只出现一次。
- 每项包含 `key`、`label`、`value`、`default_value`、`input_type`。
- 禁止注释、尾逗号、`...`、“其余同上”或 Markdown 占位文本。
- `nav`、`language_nav`、`logo_link`、`search_link`、`i18n` 的非空字符串必须能再次 `JSON.parse`。
- HTML 不得引用 JSON 中不存在的 key。
- 修改占位符时同步更新示例 HTML、示例 JSON、顶层 TXT 和顶层 JSON。
