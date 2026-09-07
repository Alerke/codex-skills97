import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(root, 'vita-travel-banner.html'), 'utf8');
const config = JSON.parse(fs.readFileSync(path.join(root, 'vita-travel-banner-config.json'), 'utf8'));
const values = Object.fromEntries(config.map((item) => [item.key, item.value]));
const slides = [
  {
    url: 'https://invalid.example.invalid/banner.jpg',
    filepath_thumb: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=75',
    name: '回退测试按钮',
    title: '主图失败回退测试',
    subtitle: '主图加载失败时应继续加载缩略图',
    jump: { type: 'url', href: '/fallback', target: '_self' }
  },
  {
    image: { file: { url: '//images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1400&q=75' } },
    name: '嵌套对象测试',
    title: '嵌套图片对象',
    subtitle: '应能读取嵌套 URL',
    jump: { type: 'none', href: '', target: '_self' }
  }
];

values.slides = JSON.stringify(slides);
values.video_slides = '[]';
values.autoplay = '0';

let rendered = html;
Object.entries(values).forEach(([key, value]) => {
  const replacement = key === 'slides' || key === 'video_slides'
    ? JSON.stringify(JSON.parse(value))
    : value;
  rendered = rendered.split(`$[${key}]`).join(replacement);
});

const output = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0"><div class="gw-browse-module">${rendered}</div></body></html>`;
fs.writeFileSync(path.join(root, 'vita-travel-banner-fallback-preview.html'), output);
