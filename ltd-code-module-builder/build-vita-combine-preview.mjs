import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const base = path.dirname(fileURLToPath(import.meta.url));
let html = fs.readFileSync(path.join(base,'vita-combine-retreat.html'),'utf8');
const config = JSON.parse(fs.readFileSync(path.join(base,'vita-combine-retreat-config.json'),'utf8'));
const map = new Map(config.map((item) => [item.key,item]));
for (const item of config) {
  if (item.input_type === 'image') {
    const image = JSON.parse(item.value);
    html = html.replaceAll('$[' + item.key + '.objectPosition]', image.objectPosition || 'center center');
    html = html.replaceAll('$[' + item.key + '.objectFit]', image.objectFit || 'cover');
    html = html.replaceAll('$[' + item.key + '.alt]', image.alt || '');
    html = html.replaceAll('$[' + item.key + ']', image.url || '');
  } else if (item.input_type === 'jump') {
    const jump = JSON.parse(item.value);
    html = html.replaceAll('$[' + item.key + '.href]', jump.href || '');
    html = html.replaceAll('$[' + item.key + '.target]', jump.target || '_self');
  } else html = html.replaceAll('$[' + item.key + ']', item.value);
}
const output = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Combine Retreat 预览</title><style>html,body{margin:0;background:#102124}</style></head><body><div class="gw-browse-module" name="Combine Retreat">' + html + '</div></body></html>';
fs.writeFileSync(path.join(base,'vita-combine-retreat-preview.html'),output);
console.log('preview built');
