import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const base = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.join(base, 'vita-retreats-recommendations.html');
const configPath = path.join(base, 'vita-retreats-recommendations-config.json');
const html = fs.readFileSync(htmlPath, 'utf8');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const errors = [];

if (!Array.isArray(config) || !config.length) errors.push('配置 JSON 必须是非空数组');

const requiredFields = ['key', 'label', 'value', 'default_value', 'input_type'];
const keys = new Set();
for (const item of config) {
  for (const field of requiredFields) {
    if (!Object.prototype.hasOwnProperty.call(item, field)) errors.push(item.key + ' 缺少字段 ' + field);
  }
  if (keys.has(item.key)) errors.push('配置 key 重复：' + item.key);
  keys.add(item.key);
  if (['image', 'video', 'jump', 'imageList', 'mediaList', 'videoList', 'i18n'].indexOf(item.input_type) >= 0) {
    try {
      const parsedValue = JSON.parse(item.value);
      if (item.input_type === 'image' && (!parsedValue || typeof parsedValue.url !== 'string')) errors.push(item.key + '.value 缺少图片 url');
    } catch (error) { errors.push(item.key + '.value 不是合法的 JSON 字符串'); }
    try {
      const parsedDefault = JSON.parse(item.default_value);
      if (item.input_type === 'image' && (!parsedDefault || typeof parsedDefault.url !== 'string')) errors.push(item.key + '.default_value 缺少图片 url');
    } catch (error) { errors.push(item.key + '.default_value 不是合法的 JSON 字符串'); }
  }
}

const placeholderMatches = html.match(/\$\[[A-Za-z0-9_.-]+\]/g) || [];
const placeholderRoots = new Set(placeholderMatches.map((item) => item.slice(2, -1).split('.')[0]));
for (const key of placeholderRoots) {
  if (!keys.has(key)) errors.push('HTML 占位符缺少配置：' + key);
}
for (const key of keys) {
  if (!placeholderRoots.has(key)) errors.push('配置未被 HTML 使用：' + key);
}

const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
  errors.push('未找到脚本');
} else {
  if (/\$\[[A-Za-z0-9_.-]+\]/.test(scriptMatch[1])) errors.push('JavaScript 中不应直接承载 LTD 标量或单图占位符');
  const jsForSyntax = scriptMatch[1].replace(/\$\[[A-Za-z0-9_.-]+\]/g, '""');
  try { new Function(jsForSyntax); } catch (error) { errors.push('JavaScript 语法错误：' + error.message); }
}

const styleText = (html.match(/<style[^>]*>[\s\S]*?<\/style>/g) || []).join('\n');
const forbiddenCss = /(^|[},]\s*)(html|body|:root|\.container|\.wrapper|\.content)(?=[\s,{.:#\[])/m;
if (forbiddenCss.test(styleText)) errors.push('发现可能污染全局的 CSS 选择器');
if (!html.includes('document.currentScript')) errors.push('脚本未使用 document.currentScript 定位实例');
for (let index = 1; index <= 3; index += 1) {
  if (!html.includes('src="$[card_' + index + '_image]"')) errors.push('卡片' + index + '未使用 LTD 单图原生 src 占位符');
}
if (/\b(?:getElementById|querySelectorAll\(['"]\.ltdRetreats20260813)/.test(scriptMatch ? scriptMatch[1] : '')) errors.push('发现全局实例绑定');
if (/\?\.|\?\?|async\s+function|\bawait\b/.test(scriptMatch ? scriptMatch[1] : '')) errors.push('发现未确认兼容性的较新 JavaScript 语法');

if (errors.length) {
  console.error('校验失败：\n- ' + errors.join('\n- '));
  process.exitCode = 1;
} else {
  console.log(JSON.stringify({
    status: 'passed',
    configItems: config.length,
    placeholderRoots: Array.from(placeholderRoots).sort(),
    checks: ['JSON', '复合配置 JSON 字符串', 'JavaScript 语法', '占位符双向对应', 'CSS 作用域', '多实例定位', '兼容语法']
  }, null, 2));
}
