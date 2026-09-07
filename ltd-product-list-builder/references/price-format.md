# 产品与商品价格格式化

价格归一化必须在 product/goods 适配器内完成，通用渲染器只消费最终 `priceText` 和 `marketPriceText`。价格为 `0` 是有效值；仅 `null`、`undefined`、空字符串或非法数字表示无价格。

## 目录

- [单一符号原则](#1-单一符号原则)
- [ES6 参考实现](#2-es6-参考实现)
- [DOM 渲染合同](#3-dom-渲染合同)
- [原始数值回退](#4-原始数值回退)
- [验收样例](#5-验收样例)

## 1. 单一符号原则

- `price_format.price_icon`、`price_integer` 或原始价格文本可能已经包含 `¥/￥/$/€/£/₽/₩`、`RMB/CNY/USD/EUR/GBP/JPY/KRW/RUB` 或“元”。
- 最终价格只能保留一个货币标识。数字部分已有前置货币标识时，以已有标识为准，不再拼 `price_icon`。
- 数字部分已有“元”等后置单位时，保留原文本且不再添加前置图标。
- `price_icon` 自身为 `￥￥`、`RMBRMB` 等重复值时只取第一个有效标识。
- `priceText` 是包含单位的最终完整文案；HTML、CSS `::before` 和渲染器不得再次补货币符号。
- 市场价与销售价调用同一格式化函数，不能各自拼接单位。

## 2. ES6 参考实现

```js
const CURRENCY_TOKEN = '(?:CN¥|RMB|CNY|USD|EUR|GBP|JPY|KRW|RUB|[¥￥$€£₽₩])';
const leadingCurrencyPattern = new RegExp(
  `^\\s*(${CURRENCY_TOKEN})(?:\\s*${CURRENCY_TOKEN})*\\s*`,
  'i'
);
const anyCurrencyPattern = new RegExp(`${CURRENCY_TOKEN}|元`, 'i');
const singleCurrencyPattern = new RegExp(CURRENCY_TOKEN, 'i');

const normalizeCurrencySymbol = (value) => {
  const text = String(value === undefined || value === null ? '' : value).trim();
  const match = text.match(singleCurrencyPattern);
  return match ? match[0] : text;
};

const formatPriceParts = (priceFormat) => {
  const format = priceFormat && typeof priceFormat === 'object' ? priceFormat : {};
  const hasInteger = format.price_integer !== undefined && format.price_integer !== null;
  if (!hasInteger) return '';

  let integer = String(format.price_integer).trim();
  let symbol = normalizeCurrencySymbol(format.price_icon);
  const leading = integer.match(leadingCurrencyPattern);

  if (leading) {
    symbol = normalizeCurrencySymbol(leading[1]);
    integer = integer.replace(leadingCurrencyPattern, '');
  } else if (anyCurrencyPattern.test(integer)) {
    symbol = '';
  }

  let decimal = format.price_decimal;
  decimal = decimal === undefined || decimal === null ? '' : String(decimal).trim();
  decimal = decimal.replace(/^[.,]+/, '');

  const amount = decimal && !/\.\d+$/.test(integer)
    ? `${integer}.${decimal}`
    : integer;

  return `${symbol}${amount}`;
};
```

如接口返回已格式化的完整 `price_text`，先按相同货币标识规则折叠重复前缀，再作为最终 `priceText`；不得把它与 `price_icon` 再次拼接。

## 3. DOM 渲染合同

截图中 `¥ ¥123.00` 的直接原因通常是模板先输出静态符号，随后又写入已经带符号的 `priceText`。默认实现必须只保留一个最终文本节点：

```html
<span class="pl-price-text"></span>
<del class="pl-market-price-text"></del>
```

```js
priceTextElement.textContent = item.priceText;
marketPriceTextElement.textContent = item.marketPriceText;
```

以下组合一律禁止：

```html
<!-- 错误：priceText 为 "¥123.00" 时会得到两个 ¥ -->
<span class="pl-price-symbol">¥</span>
<span class="pl-price-text"></span>
```

```css
/* 错误：priceText 已含单位 */
.pl-price-text::before { content: "¥"; }
```

- 默认不要创建 `.pl-price-symbol`、`.currency`、`.price-icon` 等独立单位节点。
- 不在 HTML 模板、模板字面量、CSS `content` 或渲染函数中硬编码 `¥/￥/$`。
- 若设计明确要求货币符号与金额使用不同字号，适配器改为同时输出互斥的 `priceSymbol` 和不含单位的 `priceAmount`；渲染器只写这两个字段，不能再写 `priceText`。同一个价格只能选择“单节点 priceText”或“结构化 symbol + amount”一种模式。
- 市场价遵循相同互斥合同，不能出现销售价单节点、市场价静态符号等不一致结构。
- 交付前检查最终价格容器的 `textContent`，同一价格只能匹配一个前置货币标识。

## 4. 原始数值回退

- `price_format` 能产生有效结果时优先使用。
- 否则读取有限数值 `price`。适配器明确声明单位为“分”时除以 100；明确为“元”时不换算，不能根据数值大小猜单位。
- 当前已确认列表响应的 `price` 是元单位十进制字符串，例如 `'120.00'`；直接按 120 元格式化，不得除以 100。`'0.00'` 是有效零价格。
- 当前响应的 `price_ceiling` 是价格区间上限，不是市场价。`'0.00'` 表示没有有效上限；只有上限大于销售价且设计明确支持区间时才显示单符号区间，否则忽略。不得将其写入 `marketPriceText`。
- `marketPriceText` 只来自语义明确的 `market_price`、`original_price` 或已确认等价字段；当前响应没有这些字段时保持空字符串。
- `new_price` 为空时忽略；非空语义未经接口确认前，不猜测为销售价、市场价或促销价。
- 货币符号由适配器或接口的明确字段提供，只通过上述函数添加一次。
- 小数位遵循项目接口或设计要求；不要用字符串拼接制造 `100..00`、`¥¥100` 或 `100元元`。

## 5. 验收样例

| 输入 | 输出 |
| --- | --- |
| `icon=¥, integer=100, decimal=00` | `¥100.00` |
| `icon=¥, integer=¥100, decimal=00` | `¥100.00` |
| `icon=￥￥, integer=100` | `￥100` |
| `icon=¥, integer=100元` | `100元` |
| `icon=¥, integer=$100` | `$100` |
| `price=0` | 显示零价格，不隐藏 |
| 已确认响应 `price="120.00"` | 按元显示 `¥120.00`，不除以 100 |
| `price_ceiling="0.00"` | 隐藏上限，`marketPriceText` 为空 |
| 静态 `<span>¥</span>` + `priceText="¥123.00"` | 不合格，删除静态符号节点 |

交付前搜索生成模块的价格 DOM 和 CSS，确认没有静态货币字符、重复的单位 span 或 `::before { content: ... }` 与最终 `priceText` 叠加。仅格式化函数、测试数据和此类说明允许出现货币字符字面量。
