import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.join(root, 'vita-travel-banner.html');
const configPath = path.join(root, 'vita-travel-banner-config.json');
const html = fs.readFileSync(htmlPath, 'utf8');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const expectedKeys = [
  'media_type', 'slides', 'video_slides', 'autoplay', 'autoplay_delay',
  'title_font_size', 'subtitle_font_size', 'title_font_weight', 'text_color',
  'subtitle_color', 'overlay_opacity', 'content_bottom', 'content_left',
  'mobile_ratio_mode', 'mobile_aspect_ratio', 'pc_ratio_mode',
  'pc_aspect_ratio', 'show_overlay',
  'slide_1_title', 'slide_1_subtitle', 'slide_1_button_text',
  'slide_1_button_url', 'slide_1_button_background', 'slide_1_button_text_color',
  'slide_1_title_color', 'slide_1_subtitle_color',
  'slide_1_button_border_start', 'slide_1_button_border_end',
  'slide_1_button_hover_background', 'slide_1_button_hover_text_color',
  'slide_1_button_hover_border_start', 'slide_1_button_hover_border_end',
  'slide_2_title', 'slide_2_subtitle', 'slide_2_button_text',
  'slide_2_button_url', 'slide_2_button_background', 'slide_2_button_text_color',
  'slide_2_title_color', 'slide_2_subtitle_color',
  'slide_2_button_border_start', 'slide_2_button_border_end',
  'slide_2_button_hover_background', 'slide_2_button_hover_text_color',
  'slide_2_button_hover_border_start', 'slide_2_button_hover_border_end',
  'slide_3_title', 'slide_3_subtitle', 'slide_3_button_text',
  'slide_3_button_url', 'slide_3_button_background', 'slide_3_button_text_color',
  'slide_3_title_color', 'slide_3_subtitle_color',
  'slide_3_button_border_start', 'slide_3_button_border_end',
  'slide_3_button_hover_background', 'slide_3_button_hover_text_color',
  'slide_3_button_hover_border_start', 'slide_3_button_hover_border_end',
  'inherit_first_content',
  'button_background_start', 'button_background_end', 'button_text_color',
  'button_border_start', 'button_border_end', 'button_border_width',
  'button_gradient_angle', 'button_hover_background_start',
  'button_hover_background_end', 'button_hover_text_color',
  'button_hover_border_start', 'button_hover_border_end',
  'button_hover_scale', 'button_hover_lift', 'button_flow_duration'
];

const keys = config.map((item) => item.key);
const placeholders = [...new Set([...html.matchAll(/\$\[([a-z_\d]+)\]/g)].map((match) => match[1]))].sort();
const sortedExpectedKeys = [...expectedKeys].sort();
const configByKey = Object.fromEntries(config.map((item) => [item.key, item]));
const parsedLists = ['slides', 'video_slides'].map((key) => ({
  key,
  value: Array.isArray(JSON.parse(configByKey[key].value)),
  defaultValue: Array.isArray(JSON.parse(configByKey[key].default_value))
}));

let rendered = html;
config.forEach((item) => {
  const token = `$[${item.key}]`;
  const value = item.key === 'slides' || item.key === 'video_slides'
    ? JSON.stringify(JSON.parse(item.value))
    : item.value;
  rendered = rendered.split(token).join(value);
});

const scripts = [...rendered.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
scripts.forEach((source, index) => new vm.Script(source, { filename: `banner-script-${index + 1}.js` }));

const report = {
  configCount: config.length,
  keysMatch: JSON.stringify([...keys].sort()) === JSON.stringify(sortedExpectedKeys),
  placeholdersMatch: JSON.stringify(placeholders) === JSON.stringify(sortedExpectedKeys),
  missingPlaceholders: sortedExpectedKeys.filter((key) => placeholders.indexOf(key) < 0),
  unknownPlaceholders: placeholders.filter((key) => sortedExpectedKeys.indexOf(key) < 0),
  everyConfigHasRequiredFields: config.every((item) =>
    ['key', 'label', 'value', 'default_value', 'input_type'].every((field) =>
      Object.prototype.hasOwnProperty.call(item, field)
    )
  ),
  parsedLists,
  scriptBlocks: scripts.length,
  scriptSyntax: 'valid',
  usesLessRuntime: /text\/less|less\.js/i.test(html),
  usesUnsafeProtocolLiteral: /javascript:|vbscript:|data:text\/html/i.test(html),
  usesInnerHTML: /\.innerHTML\s*=/.test(html),
  remainingPlaceholders: rendered.match(/\$\[[^\]]+\]/g) || [],
  supportsProtocolRelativeMedia: html.includes("const isProtocolRelativeUrl = (value) => /^\\/\\/[^/]/.test(value);"),
  supportsBareRelativeMedia: html.includes("!/^[a-z][a-z\\d+.-]*:/i.test(value)"),
  supportsNestedMediaObjects: html.includes('const readMediaCandidate = (value) => {') &&
    html.includes('readMediaCandidate(value.file)') &&
    html.includes('readMediaCandidate(value.image)'),
  supportsImageUrlFallback: html.includes('const collectUrls = (item, keys) => {') &&
    html.includes("'filepath_thumb', 'filePathThumb', 'thumbnail', 'thumb'") &&
    html.includes('imageUrlIndex < item.urls.length'),
  supportsLegacySwiperClass: html.includes('.swiper-container-initialized .swiper-wrapper') &&
    html.includes('.swiper-container-initialized .swiper-slide'),
  readsListsByLocalEvaluation: html.includes('const rawSlides = $[slides];') &&
    html.includes('const rawVideoSlides = $[video_slides];')
};

console.log(JSON.stringify(report, null, 2));

if (process.argv.includes('--preview')) {
  const escapeAttribute = (value) => value
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  const swiperAssets = '<link rel="stylesheet" href="https://static.ltdcdn.com/assets/lib/Swiper/5.4.5/css/swiper.min.css"><script src="https://static.ltdcdn.com/assets/lib/Swiper/5.4.5/js/swiper.min.js"></script>';
  const documentMarkup = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">${swiperAssets}<style>html,body{margin:0;background:#111} .gw-browse-module{width:100%}</style></head><body><div class="gw-browse-module">${rendered}</div><div class="gw-browse-module">${rendered}</div></body></html>`;
  const preview = `<!doctype html><html><head><meta charset="utf-8"><title>Vita Travel Banner iframe preview</title><style>body{background:#e8e8e5;font-family:Arial,sans-serif;margin:0;padding:24px}.preview-grid{display:grid;gap:24px;grid-template-columns:minmax(0,1fr) 390px}.preview-card{background:#fff;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.12);overflow:hidden}.preview-label{font-size:13px;font-weight:700;padding:12px 16px}.preview-card iframe{border:0;display:block;height:800px;width:100%}@media(max-width:900px){.preview-grid{grid-template-columns:1fr}.preview-card iframe{height:720px}}</style></head><body><div class="preview-grid"><div class="preview-card"><div class="preview-label">编辑器 iframe 模拟：桌面端</div><iframe title="桌面端 Banner 预览" srcdoc="${escapeAttribute(documentMarkup)}"></iframe></div><div class="preview-card"><div class="preview-label">编辑器 iframe 模拟：移动端</div><iframe title="移动端 Banner 预览" srcdoc="${escapeAttribute(documentMarkup)}"></iframe></div></div></body></html>`;
  fs.writeFileSync(path.join(root, 'vita-travel-banner-preview.html'), preview);
  fs.writeFileSync(path.join(root, 'vita-travel-banner-swiper5-preview.html'), documentMarkup);
}

const failed = !report.keysMatch ||
  !report.placeholdersMatch ||
  !report.everyConfigHasRequiredFields ||
  report.parsedLists.some((item) => !item.value || !item.defaultValue) ||
  report.scriptBlocks !== 1 ||
  report.usesLessRuntime ||
  report.usesUnsafeProtocolLiteral ||
  report.usesInnerHTML ||
  !report.supportsProtocolRelativeMedia ||
  !report.supportsBareRelativeMedia ||
  !report.supportsNestedMediaObjects ||
  !report.supportsImageUrlFallback ||
  !report.supportsLegacySwiperClass ||
  !report.readsListsByLocalEvaluation ||
  report.remainingPlaceholders.length > 0;

if (failed) process.exitCode = 1;
