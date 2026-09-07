import fs from 'node:fs';
import vm from 'node:vm';

const htmlPath = new URL('./marine-layer-banner.html', import.meta.url);
const configPath = new URL('./marine-layer-banner-config.json', import.meta.url);
const previewPath = new URL('./marine-layer-banner-preview.html', import.meta.url);
const html = fs.readFileSync(htmlPath, 'utf8');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const expectedKeys = [
  'media_type', 'slides',
  'slide_1_title', 'slide_1_subtitle', 'slide_2_title', 'slide_2_subtitle',
  'slide_3_title', 'slide_3_subtitle',
  'video_slides', 'autoplay', 'autoplay_delay',
  'title_font_size', 'subtitle_font_size', 'title_font_weight', 'text_color',
  'subtitle_color', 'overlay_opacity', 'content_bottom', 'content_left',
  'mobile_ratio_mode', 'mobile_aspect_ratio', 'pc_ratio_mode',
  'pc_aspect_ratio', 'show_overlay', 'button_text', 'button_link',
  'button_background_color', 'button_text_color',
  'button_hover_background_color', 'button_hover_text_color',
  'indicator_color', 'indicator_active_color'
];
const configKeys = config.map((item) => item.key);
const placeholderPattern = /\$\[([a-z0-9_]+)(?:\.([a-z0-9_]+))?\]/gi;
const placeholderKeys = Array.from(new Set(Array.from(html.matchAll(placeholderPattern), (match) => match[1])));
const requiredFields = ['key', 'label', 'value', 'default_value', 'input_type'];
const oldKeys = ['banner_list', 'transition_speed', 'show_navigation', 'show_pagination', 'pause_on_hover', 'desktop_height', 'tablet_height', 'mobile_height'];

const sameKeys = (left, right) => left.length === right.length && left.every((key, index) => key === right[index]);
const everyConfigHasRequiredFields = config.every((item) => requiredFields.every((field) => Object.prototype.hasOwnProperty.call(item, field)));
const parsedLists = ['slides', 'video_slides'].map((key) => {
  const item = config.find((entry) => entry.key === key);
  let value = false;
  let defaultValue = false;
  try { value = Array.isArray(JSON.parse(item.value)); } catch (error) { value = false; }
  try { defaultValue = Array.isArray(JSON.parse(item.default_value)); } catch (error) { defaultValue = false; }
  return { key, value, defaultValue };
});
const parsedJump = (() => {
  const item = config.find((entry) => entry.key === 'button_link');
  try {
    const value = JSON.parse(item.value);
    const defaultValue = JSON.parse(item.default_value);
    return Boolean(value && typeof value === 'object' && defaultValue && typeof defaultValue === 'object');
  } catch (error) {
    return false;
  }
})();

const values = new Map(config.map((item) => [item.key, String(item.value)]));
const structuredValues = new Map(config.map((item) => {
  try { return [item.key, JSON.parse(item.value)]; } catch (error) { return [item.key, item.value]; }
}));
const renderedModule = html.replace(placeholderPattern, (match, key, field) => {
  if (!values.has(key)) return match;
  if (!field) return values.get(key);
  const source = structuredValues.get(key);
  return source && typeof source === 'object' && source[field] != null ? String(source[field]) : '';
});
const scriptBlocks = Array.from(renderedModule.matchAll(/<script>([\s\S]*?)<\/script>/gi), (match) => match[1]);
let scriptSyntax = 'valid';
try { scriptBlocks.forEach((source) => new vm.Script(source)); } catch (error) { scriptSyntax = error.message; }

const preview = `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Marine Layer 风格 LTD Banner 预览</title>
  <style>html,body{margin:0;min-height:100%;background:#eef0ed;}body{font-family:Arial,sans-serif;}</style>
</head>
<body>
${renderedModule}
</body>
</html>`;
fs.writeFileSync(previewPath, preview, 'utf8');

const result = {
  configCount: config.length,
  keysMatch: sameKeys(configKeys, expectedKeys),
  placeholdersMatch: sameKeys(placeholderKeys.slice().sort(), expectedKeys.slice().sort()),
  everyConfigHasRequiredFields,
  parsedLists,
  parsedJump,
  oldKeysPresent: oldKeys.filter((key) => configKeys.includes(key) || html.includes(`$[${key}]`)),
  scriptBlocks: scriptBlocks.length,
  scriptSyntax,
  usesLessRuntime: /less\.js|text\/less/i.test(html),
  usesInnerHTML: /\.innerHTML\s*=/i.test(html),
  unresolvedPlaceholders: Array.from(new Set(Array.from(renderedModule.matchAll(placeholderPattern), (match) => match[1]))),
  rootIsolated: !/document\.querySelector\(['"]\.ltdBanner/i.test(html),
  preview: previewPath.pathname
};

console.log(JSON.stringify(result, null, 2));
if (!result.keysMatch || !result.placeholdersMatch || !everyConfigHasRequiredFields || parsedLists.some((item) => !item.value || !item.defaultValue) || !parsedJump || result.oldKeysPresent.length || scriptSyntax !== 'valid' || result.usesLessRuntime || result.usesInnerHTML || result.unresolvedPlaceholders.length || !result.rootIsolated) {
  process.exitCode = 1;
}
