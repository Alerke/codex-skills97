import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const modulePath = path.join(currentDir, "marine-layer-mega-top-nav.html");
const configPath = path.join(currentDir, "marine-layer-mega-top-nav.config.json");
const previewPath = path.join(currentDir, "marine-layer-mega-top-nav-preview.html");

const expectedKeys = [
  "nav",
  "use_custom_language_jump",
  "language_nav",
  "logo",
  "stickyLogo",
  "logo_link",
  "phone",
  "email",
  "address",
  "sticky_mode",
  "sticky_scroll_distance",
  "theme_color",
  "nav_background_color",
  "nav_blur",
  "nav_text_color",
  "i18n",
  "show_search",
  "search_link",
  "show_login",
  "sticky_nav_background_color",
  "sticky_nav_text_color",
  "logo_height_percent",
  "company_name",
  "company_name_color",
  "sticky_company_name_color",
  "mobile_menu_company_name_color"
];

const nestedJsonKeys = new Set(["nav", "language_nav", "logo_link", "search_link", "i18n"]);
const moduleHtml = fs.readFileSync(modulePath, "utf8");
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
const errors = [];

if (!Array.isArray(config)) errors.push("配置顶层必须是数组");
if (config.length !== expectedKeys.length) errors.push(`配置项数量应为 ${expectedKeys.length}，当前为 ${config.length}`);

const actualKeys = config.map((item) => item.key);
const duplicateKeys = actualKeys.filter((key, index) => actualKeys.indexOf(key) !== index);
if (duplicateKeys.length) errors.push(`存在重复 key：${[...new Set(duplicateKeys)].join(", ")}`);

for (const key of expectedKeys) {
  if (!actualKeys.includes(key)) errors.push(`缺少配置 key：${key}`);
}

for (const item of config) {
  for (const field of ["key", "label", "value", "default_value", "input_type"]) {
    if (!Object.prototype.hasOwnProperty.call(item, field)) errors.push(`${item.key || "未知配置"} 缺少字段 ${field}`);
  }
  if (nestedJsonKeys.has(item.key)) {
    for (const field of ["value", "default_value"]) {
      if (item[field] !== "") {
        try { JSON.parse(item[field]); } catch (error) { errors.push(`${item.key}.${field} 不是合法的内嵌 JSON`); }
      }
    }
  }
}

const placeholderKeys = [...moduleHtml.matchAll(/\$\[([A-Za-z0-9_]+)\]/g)].map((match) => match[1]);
const uniquePlaceholderKeys = [...new Set(placeholderKeys)];
for (const key of uniquePlaceholderKeys) {
  if (!expectedKeys.includes(key)) errors.push(`HTML 引用了未定义配置：${key}`);
}
for (const key of expectedKeys) {
  if (!uniquePlaceholderKeys.includes(key)) errors.push(`HTML 未引用配置：${key}`);
}

const forbiddenPatterns = [
  [/:has\s*\(/, ":has()"],
  [/:scope\b/, ":scope"],
  [/replaceChildren\s*\(/, "replaceChildren()"],
  [/\/api\/website\/navigation/, "旧导航接口"],
  [/\?\./, "可选链"],
  [/\.merge\.html/, ".merge.html 引用"]
];

for (const [pattern, label] of forbiddenPatterns) {
  if (pattern.test(moduleHtml)) errors.push(`模块包含禁止项：${label}`);
}

for (const requiredText of [
  '<style data-nav-initial>',
  '<style data-nav-styles>',
  'document.currentScript',
  'url: "/api/navCat"',
  'position: 1',
  'response.code === 0',
  'top-nav-host-20260821',
  'top-nav-host-floating',
  'nav-mega-card',
  'nav-mega-group',
  'nav-mb-card-grid',
  'nav-mb-subviews',
  'nav-mb-promo-card',
  'mobileViewController'
]) {
  if (!moduleHtml.includes(requiredText)) errors.push(`模块缺少关键实现：${requiredText}`);
}

const configMap = new Map(config.map((item) => [item.key, item.value]));
try {
  const messages = JSON.parse(configMap.get("i18n") || "{}");
  for (const language of ["zh-cn", "en"]) {
    for (const key of ["searchPlaceholder", "loginText", "featuredTitle", "moreLinksTitle", "phoneLabel", "emailLabel", "addressLabel"]) {
      if (!messages[language] || !messages[language][key]) errors.push(`i18n.${language} 缺少可编辑文案：${key}`);
    }
  }
} catch (error) {
  errors.push("无法校验 i18n 可编辑文案");
}

if (/<img[^>]+src=["']https?:/i.test(moduleHtml)) errors.push("模块结构中存在绕过配置的硬编码图片");

let renderedModule = moduleHtml.replace(/\$\[([A-Za-z0-9_]+)\]/g, (match, key) => {
  if (!configMap.has(key)) return match;
  return JSON.stringify(configMap.get(key));
});

const scripts = [...renderedModule.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
for (const script of scripts) {
  try { new Function(script); } catch (error) { errors.push(`脚本语法错误：${error.message}`); }
}

const previewHtml = `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>透明悬浮图片文字 Mega 导航预览</title>
  <style>
    *{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:"Segoe UI","PingFang SC",sans-serif}.gw-browse-module{width:100%}.gw-browse-module .code-html-content{width:100%}.preview-banner{min-height:720px;padding:180px 8vw 80px;color:#fff;background:linear-gradient(90deg,rgba(12,21,35,.58),rgba(12,21,35,.18)),url("https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=2000&q=86") center/cover no-repeat}.preview-banner h1{max-width:680px;margin:0 0 20px;font-size:clamp(42px,7vw,88px);line-height:.98;letter-spacing:-.04em}.preview-banner p{max-width:520px;font-size:18px;line-height:1.7}.preview-content{min-height:900px;padding:100px 8vw;color:#172033;background:#f4f1eb}.preview-content h2{font-size:42px}.preview-note{position:fixed;right:14px;bottom:14px;z-index:20000;padding:8px 11px;color:#fff;background:rgba(23,32,51,.86);border-radius:4px;font-size:12px}
  </style>
</head>
<body>
  <div class="gw-browse-module" name="顶部导航"><div class="gw-browse-module-content"><div class="gw-browse-component"><div class="code-html-content">${renderedModule}</div></div></div></div>
  <section class="preview-banner"><h1>Soft essentials,<br>made to live in.</h1><p>导航透明悬浮在 Banner 上方；向下滚动后切换为白色吸顶状态。</p></section>
  <section class="preview-content"><h2>继续向下滚动</h2><p>用于检查滚动态颜色、Logo 与吸顶行为。</p></section>
  <div class="preview-note">桌面端悬停“产品系列 / 品牌故事”；移动端请缩窄窗口。</div>
</body>
</html>`;

if (errors.length) {
  console.error(errors.map((error) => `- ${error}`).join("\n"));
  process.exitCode = 1;
} else {
  fs.writeFileSync(previewPath, previewHtml, "utf8");
  console.log(`验证通过：26 项配置、嵌套 JSON、占位符、禁止项、脚本语法均正常。`);
  console.log(`已生成预览：${previewPath}`);
}
