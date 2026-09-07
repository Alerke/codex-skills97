import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const folder = dirname(fileURLToPath(import.meta.url));
const modulePath = join(folder, 'vita-travel-bottom-nav.html');
const configPath = join(folder, 'vita-travel-bottom-nav-config.json');
const outputPath = join(folder, 'vita-travel-bottom-nav-preview.html');
const moduleHtml = await readFile(modulePath, 'utf8');
const config = JSON.parse(await readFile(configPath, 'utf8'));
const values = Object.fromEntries(config.map((item) => [item.key, item.value]));

const parseStructured = (value) => {
  if (typeof value !== 'string') return value;
  try { return JSON.parse(value); } catch { return value; }
};
const resolveValue = (path) => {
  const parts = path.split('.');
  let value = parseStructured(values[parts.shift()]);
  for (const part of parts) value = value && typeof value === 'object' ? value[part] : '';
  if (value && typeof value === 'object') return value.url || value.value || JSON.stringify(value);
  return value == null ? '' : String(value);
};
const render = (source) => source.replace(/\$\[([^\]]+)\]/g, (_, path) => resolveValue(path));
const first = render(moduleHtml);
const secondConfig = JSON.parse(JSON.stringify(config));
const navItem = secondConfig.find((item) => item.key === 'nav_list');
navItem.value = JSON.stringify([
  { title: 'Retreats', jump: { href: '/retreats', target: '_self' }, children: [
    { title: 'Wellness', jump: { href: '/retreats/wellness', target: '_self' }, children: [] },
    { title: 'Yoga', jump: { href: '/retreats/yoga', target: '_self' }, children: [] }
  ] },
  { title: 'Journal', jump: { href: '/journal', target: '_self' }, children: [] }
]);
const secondValues = Object.fromEntries(secondConfig.map((item) => [item.key, item.value]));
const renderSecond = (source) => source.replace(/\$\[([^\]]+)\]/g, (_, path) => {
  const parts = path.split('.');
  let value = parseStructured(secondValues[parts.shift()]);
  for (const part of parts) value = value && typeof value === 'object' ? value[part] : '';
  if (value && typeof value === 'object') return value.url || value.value || JSON.stringify(value);
  return value == null ? '' : String(value);
});

const document = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Vita Travel Bottom Nav Preview</title>
<style>html,body{margin:0;background:#d9dfdd;font-family:Arial,sans-serif}.preview-spacer{align-items:flex-end;background:linear-gradient(145deg,#e5ece9,#b9c6c3);color:#24434a;display:flex;font-size:clamp(32px,6vw,92px);font-weight:700;height:52vh;padding:5vw}.preview-label{background:#fff;color:#24434a;font-size:14px;font-weight:700;letter-spacing:.08em;padding:12px 20px;text-transform:uppercase}</style>
<script>window.r=function(options){window.__lastNavRequest=options;var mode=new URLSearchParams(location.search).get('api');if(mode==='success')return Promise.resolve({code:0,data:[{title:'Explore',jump:{href:'',target:'_self'},children:[{title:'Safe link',jump:{href:'/safe',target:'_self'},children:[]},{title:'Hidden link',hidden:true,jump:{href:'/hidden',target:'_self'},children:[]},{title:'Danger link',jump:{href:'javascript:alert(1)',target:'_self'},children:[]},{title:'External link',jump:{href:'https://example.com/',target:'_blank'},children:[]}]},{title:'Hidden group',status:0,jump:{href:'/hidden-group',target:'_self'},children:[]}]});if(mode==='empty')return Promise.resolve({code:0,data:[]});return Promise.reject(new Error('Preview API fallback'));};</script></head><body>
<div class="preview-spacer">Vita Travel</div><div class="preview-label">Instance A · reference layout</div>${first}
<div class="preview-label">Instance B · nested navigation and instance isolation</div>${renderSecond(moduleHtml)}
</body></html>`;
await writeFile(outputPath, document, 'utf8');
console.log(outputPath);
