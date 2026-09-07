const fs = require('fs');

const htmlPath = process.argv[2];
const jsonPath = process.argv[3];
const html = fs.readFileSync(htmlPath, 'utf8');
const config = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
const start = html.indexOf('<script>');
const end = html.indexOf('</script>', start);
if (start < 0 || end < 0) throw new Error('script missing');
new Function(html.slice(start + 8, end));

const placeholders = Array.from(new Set(Array.from(html.matchAll(/\$\[([A-Za-z0-9_.]+)\]/g), (match) => match[1]))).sort();
const keys = Array.from(new Set(config.map((item) => String(item.key || ''))));
const missing = placeholders.filter((placeholder) => !keys.includes(placeholder) && !keys.some((key) => placeholder.indexOf(key + '.') === 0));

console.log(JSON.stringify({
  jsSyntax: 'ok',
  json: 'ok',
  configItems: config.length,
  placeholders: placeholders.length,
  missing,
  oldRootMatches: html.split('articleList20260812').length - 1,
  hasXhrFallback: html.indexOf('XMLHttpRequest') >= 0,
  hasWebsiteWait: html.indexOf('waitForWebsiteId') >= 0,
  hasStrictDetailField: html.indexOf('pc_detail_link') >= 0
}, null, 2));
