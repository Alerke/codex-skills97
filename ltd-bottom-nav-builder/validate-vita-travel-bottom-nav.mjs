import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const folder = dirname(fileURLToPath(import.meta.url));
const html = await readFile(join(folder, 'vita-travel-bottom-nav.html'), 'utf8');
const config = JSON.parse(await readFile(join(folder, 'vita-travel-bottom-nav-config.json'), 'utf8'));
const preview = await readFile(join(folder, 'vita-travel-bottom-nav-preview.html'), 'utf8');
const keys = new Set(config.map((item) => item.key));
const placeholders = [...html.matchAll(/\$\[([^\].]+)(?:\.[^\]]+)?\]/g)].map((match) => match[1]);
const missing = [...new Set(placeholders.filter((key) => !keys.has(key)))];
const duplicateKeys = config.map((item) => item.key).filter((key, index, all) => all.indexOf(key) !== index);
const requiredSnippets = [
  '<style data-nav-initial>', '<style data-nav-styles>', 'bottomNav20260814', 'document.currentScript',
  "url: '/api/navCat'", 'position: 2', 'code === 0', "localStorage.getItem('websiteId')",
  'language_type: language', 'noopener noreferrer', 'javascript|data|vbscript', 'aria-expanded',
  'data-nav-list', "input_type\":\"navList", 'prefers-reduced-motion'
];
const failures = [];
if (missing.length) failures.push(`缺少配置 key: ${missing.join(', ')}`);
if (duplicateKeys.length) failures.push(`重复配置 key: ${duplicateKeys.join(', ')}`);
for (const item of config) {
  for (const field of ['key', 'label', 'value', 'default_value', 'input_type']) if (!(field in item)) failures.push(`${item.key || 'unknown'} 缺少 ${field}`);
  if (item.input_type === 'navList' || item.input_type === 'i18n') {
    try { JSON.parse(item.value); JSON.parse(item.default_value); } catch { failures.push(`${item.key} 内嵌 JSON 无法解析`); }
  }
}
for (const snippet of requiredSnippets) if (!html.includes(snippet) && !JSON.stringify(config).includes(snippet)) failures.push(`缺少要求片段: ${snippet}`);
if ((preview.match(/class="bottomNav20260814"/g) || []).length !== 2) failures.push('预览页未包含两个实例');
if (/\.merge\.html/i.test(html)) failures.push('不应引用 .merge.html');
if (/\bbody\s*\{[^}]*padding-bottom/i.test(html)) failures.push('不应写入全局 body padding-bottom');
if (failures.length) { console.error(failures.join('\n')); process.exitCode = 1; } else { console.log(`PASS: ${config.length} 个配置项，${new Set(placeholders).size} 个占位符，双实例预览已生成。`); }
