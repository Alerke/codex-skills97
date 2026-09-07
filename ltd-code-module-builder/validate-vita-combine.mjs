import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const base = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(base, 'vita-combine-retreat.html'), 'utf8');
const config = JSON.parse(fs.readFileSync(path.join(base, 'vita-combine-retreat-config.json'), 'utf8'));
const errors = [];
const keys = new Set();
const required = ['key','label','value','default_value','input_type'];
if (!Array.isArray(config) || !config.length) errors.push('配置必须是非空数组');
for (const item of config) {
  for (const field of required) if (!Object.prototype.hasOwnProperty.call(item, field)) errors.push(item.key + ' 缺少 ' + field);
  if (keys.has(item.key)) errors.push('重复 key：' + item.key); keys.add(item.key);
  if (['image','jump'].indexOf(item.input_type) >= 0) {
    for (const field of ['value','default_value']) {
      try { const parsed = JSON.parse(item[field]); if (item.input_type === 'image' && (!parsed || typeof parsed.url !== 'string')) errors.push(item.key + '.' + field + ' 缺少 url'); }
      catch (error) { errors.push(item.key + '.' + field + ' 不是合法 JSON 字符串'); }
    }
  }
}
const placeholders = html.match(/\$\[[A-Za-z0-9_.-]+\]/g) || [];
const roots = new Set(placeholders.map((item) => item.slice(2,-1).split('.')[0]));
for (const root of roots) if (!keys.has(root)) errors.push('占位符缺少配置：' + root);
for (const key of keys) if (!roots.has(key)) errors.push('配置未被 HTML 使用：' + key);
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) errors.push('缺少脚本');
else {
  if (/\$\[[A-Za-z0-9_.-]+\]/.test(scriptMatch[1])) errors.push('JavaScript 不应直接承载 LTD 标量或图片占位符');
  try { new Function(scriptMatch[1]); } catch (error) { errors.push('JavaScript 语法错误：' + error.message); }
  if (/\?\.|\?\?|async\s+function|\bawait\b/.test(scriptMatch[1])) errors.push('发现未确认兼容的新语法');
}
for (const key of ['background_image','step_1_image','step_2_image','step_3_image','step_4_image']) if (!html.includes('src="$[' + key + ']"')) errors.push(key + ' 未使用原生单图 src 占位符');
if (!html.includes('document.currentScript')) errors.push('未使用 document.currentScript');
const styles = (html.match(/<style[^>]*>[\s\S]*?<\/style>/g) || []).join('\n');
if (/(^|[},]\s*)(html|body|:root|\.container|\.wrapper|\.content)(?=[\s,{.:#\[])/m.test(styles)) errors.push('存在可能污染全局的 CSS');
if (errors.length) { console.error('校验失败：\n- ' + errors.join('\n- ')); process.exitCode = 1; }
else console.log(JSON.stringify({status:'passed',configItems:config.length,placeholderRoots:Array.from(roots).sort(),checks:['JSON','图片和跳转对象','JavaScript 语法','占位符双向对应','CSS 作用域','多实例定位','兼容语法']},null,2));
