import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(root, 'vita-travel-banner.html'), 'utf8');
const config = JSON.parse(fs.readFileSync(path.join(root, 'vita-travel-banner-config.json'), 'utf8'));
const values = Object.fromEntries(config.map((item) => [item.key, item.value]));
const image = 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1600&q=80';

values.slides = JSON.stringify([
  { url: image, name: '第一张', title: '远行', subtitle: '第一张副标题', jump: { type: 'web', href: '/one', target: '_self' } },
  { url: image, name: '第二张图片文件名' },
  { url: image, name: '第三张图片文件名' }
]);
values.video_slides = '[]';
values.autoplay = '0';
values.pc_ratio_mode = '1';
values.slide_1_title = '远行';
values.slide_1_subtitle = '带着目的出发。静修、户外探索与精品旅居，在一处相遇。';
values.slide_1_button_text = '探索隐世旅程';
values.slide_1_button_url = '/retreats';
values.slide_2_button_border_start = '#24d6c8';
values.slide_2_button_border_end = '#3a7bd5';
values.slide_3_button_border_start = '#ff8a5b';
values.slide_3_button_border_end = '#ffd166';

let rendered = html;
Object.entries(values).forEach(([key, value]) => {
  const replacement = key === 'slides' || key === 'video_slides' ? JSON.stringify(JSON.parse(value)) : value;
  rendered = rendered.split(`$[${key}]`).join(replacement);
});

const scripts = [...rendered.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((match) => match[1]);
scripts.forEach((source, index) => new vm.Script(source, { filename: `three-slide-${index + 1}.js` }));

const output = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{margin:0;background:#111}</style></head><body><div class="gw-browse-module">${rendered}</div></body></html>`;
fs.writeFileSync(path.join(root, 'vita-travel-banner-three-slide-preview.html'), output);
console.log(JSON.stringify({ scriptSyntax: 'valid', slides: 3, output: 'vita-travel-banner-three-slide-preview.html' }, null, 2));
