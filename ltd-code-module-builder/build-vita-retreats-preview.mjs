import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const base = path.dirname(fileURLToPath(import.meta.url));
const source = fs.readFileSync(path.join(base, 'vita-retreats-recommendations.html'), 'utf8');
const config = JSON.parse(fs.readFileSync(path.join(base, 'vita-retreats-recommendations-config.json'), 'utf8'));
const values = Object.fromEntries(config.map((item) => [item.key, item]));
const replacements = {
  section_label: values.section_label.value,
  section_title: values.section_title.value,
  card_1_title: values.card_1_title.value,
  card_1_meta: values.card_1_meta.value,
  card_2_title: values.card_2_title.value,
  card_2_meta: values.card_2_meta.value,
  card_3_title: values.card_3_title.value,
  card_3_meta: values.card_3_meta.value,
  background_color: values.background_color.value,
  heading_color: values.heading_color.value,
  heading_size: values.heading_size.value,
  label_color: values.label_color.value,
  label_size: values.label_size.value,
  card_text_color: values.card_text_color.value,
  card_meta_color: values.card_meta_color.value,
  card_title_size: values.card_title_size.value,
  card_meta_size: values.card_meta_size.value
};

let rendered = source;
for (const [key, value] of Object.entries(replacements)) rendered = rendered.replaceAll('$[' + key + ']', value);
for (let index = 1; index <= 3; index += 1) {
  const jump = JSON.parse(values['card_' + index + '_action'].value);
  const image = JSON.parse(values['card_' + index + '_image'].value);
  rendered = rendered.replaceAll('$[card_' + index + '_action.href]', jump.href || '');
  rendered = rendered.replaceAll('$[card_' + index + '_action.target]', jump.target || '_self');
  rendered = rendered.replaceAll('$[card_' + index + '_image.alt]', image.alt || '');
  rendered = rendered.replaceAll('$[card_' + index + '_image.objectFit]', image.objectFit || 'cover');
  rendered = rendered.replaceAll('$[card_' + index + '_image.objectPosition]', image.objectPosition || 'center center');
  rendered = rendered.replaceAll('$[card_' + index + '_image]', image.url || '');
}

const document = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>推荐度假地预览</title><style>html,body{margin:0;background:#071e23}</style></head><body><div class="gw-browse-module" name="推荐度假地">' + rendered + '</div></body></html>';
fs.writeFileSync(path.join(base, 'vita-retreats-recommendations-preview.html'), document);
console.log('preview built');
