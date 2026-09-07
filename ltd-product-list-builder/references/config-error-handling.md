# 配置错误处理与安全降级

产品列表与商品列表必须把后台变量视为不可信输入。缺失、未替换、类型错误或旧数据格式都不能抛出未捕获异常并阻塞页面运行。

## 目录

- [基本原则](#1-基本原则)
- [通用读取器](#2-通用读取器)
- [直接注入对象](#3-直接注入对象)
- [各配置类型降级](#4-各配置类型降级)
- [错误等级](#5-错误等级)
- [初始化边界](#6-初始化边界)
- [验收](#7-验收)

## 1. 基本原则

- 每个根配置项独立读取和归一化；一个配置失败不能让其他配置失效。
- 先检测未替换占位符，再做类型转换或 JSON 解析。
- 所有读取器都接收安全默认值并返回稳定类型，不向外抛异常。
- 不用一个覆盖整个初始化流程的空 `catch` 隐藏问题；配置错误在读取边界处理，初始化最外层只负责最后一道实例隔离。
- 错误只影响当前模块实例，不修改宿主、不停止页面其他脚本、不输出完整配置或敏感数据。

## 2. 通用读取器

```js
const isPlaceholder = (value) => (
  typeof value === 'string' && /^\$\[[^\]]+\]$/.test(value.trim())
);

const readText = (value, fallback = '') => {
  if (value === undefined || value === null || isPlaceholder(value)) return fallback;
  return String(value);
};

const readNumber = (value, fallback, min, max) => {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(max, Math.max(min, parsed));
};

const readObject = (value, fallback) => {
  if (value && typeof value === 'object' && !Array.isArray(value)) return value;
  if (typeof value !== 'string' || isPlaceholder(value) || !value.trim()) return fallback;
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : fallback;
  } catch (error) {
    return fallback;
  }
};
```

- `readSwitch` 必须分别识别开启值 `"1"`、`1`、`true`、`"true"` 和关闭值 `"0"`、`0`、`false`、`"false"`；只有缺失、未替换或未知值才使用明确默认值。

```js
const readSwitch = (fallback, value) => {
  if (value === '1' || value === 1 || value === true || value === 'true') return true;
  if (value === '0' || value === 0 || value === false || value === 'false') return false;
  return fallback;
};
```
- `readEnum` 只接受允许值，未知值回退默认值。
- 数字先检查有限值，再限制范围；颜色、尺寸、URL 分别使用专用白名单，不共享通用字符串读取器。
- 若需支持不含 `Number.isFinite` 的旧 WebView，提供模块内 `isFiniteNumber` 等价函数，不加载整套 polyfill。

## 3. 直接注入对象

`$[i18n]` 等未加引号的对象占位符在变量未替换时可能于求值阶段报错，读取动作本身也要隔离：

```js
const readInjectedI18n = () => {
  try {
    return readObject($[i18n], DEFAULT_I18N);
  } catch (error) {
    return DEFAULT_I18N;
  }
};
```

标准运行时仍直接接收对象；这个 `try/catch` 只防止占位符未替换或宿主变量异常，不代表默认对 `$[i18n]` 执行 `JSON.parse`。

## 4. 各配置类型降级

| 配置 | 异常时处理 |
| --- | --- |
| `category` | ids 回退空数组，明确表示不限制分类并获取当前适配器全部数据；names 异常不影响 ids；空 type 不发送；pageSize、排序字段和方向回退安全默认值；可选 sortColumnVersion 仅保留为编辑器元数据 |
| `moduleType` | 只接受精确值 `product/goods`；缺失、空值或未替换时回退明确默认值；`shopGoods` 等非空非法值不映射、不静默回退，只停止当前实例 |
| `i18n` | 回退完整内置中文对象，并继续渲染 |
| `jump` | 回退 `none`，移除可点击样式；不得保留半有效 `href` 或执行未知动作 |
| `switch` | 回退该功能设计默认值，不能使用 `Boolean("0")` |
| `number` | 回退默认值并限制范围 |
| 颜色/尺寸 | 非法值回退默认 CSS 变量，不拼接整段 CSS |
| URL/target | 非法 URL 取消链接；target 回退 `_self` |

## 5. 错误等级

- 可恢复：单个可选字段缺失、数字越界、旧 JSON 解析失败、语言缺失和点击配置无效。旧代码固定接口与 category `moduleType` 错配时，不保留错误接口，而是重新从类型选择适配器。
- 致命但局部：有效配置和默认值都无法确定 moduleType、对应适配器不存在或核心根节点缺失。停止当前实例的请求/渲染流程，在当前实例显示可读配置错误；不得 `throw` 到全局。
- 请求错误不属于配置错误，进入列表 error 状态并保留重试入口。

筛选型配置的空值不是错误：空分类、关键词、价格或属性条件表示不附加对应请求参数，从当前适配器获取满足其他有效条件的全部数据。展示型配置的空值仍按该字段默认值处理。

开发调试时可收集不含原始值的警告代码，例如 `INVALID_PAGE_SIZE`。生产前台默认不输出连续 `console.error`，更不能打印完整配置、接口响应或令牌。

## 6. 初始化边界

1. 先定位当前根节点并建立最外层实例保护。
2. 独立读取 category、i18n、jump、开关、数字和样式配置。
3. 汇总为类型稳定的 `config` 对象，再创建状态、绑定事件和请求数据。
4. 可恢复错误不改变初始化顺序；局部致命错误调用 `renderConfigError()` 后安全返回。
5. `renderConfigError()` 只更新当前模块状态区，不能清空 `.gw-browse-module` 或页面容器。

## 7. 验收

- 分别破坏一个字符串、开关、数字、category、i18n 和 jump 配置，页面其他能力仍可运行。
- 未替换 `$[...]`、错误 JSON、数组冒充对象、`null`、越界数字和非法 URL 均有稳定回退。
- category 为空或缺失时没有自动选择分类，请求中不附加分类限制并返回当前数据源全部数据。
- category 的 names 数量不匹配、type 为空或 sortColumnVersion 缺失/非法时，筛选仍按有效 ids 与安全排序运行。
- 把 `moduleType` 在 product/goods 间切换时，分类接口和列表接口自动成对切换，不会继续调用旧的固定接口。
- 只有没有固定接口、没有有效配置/默认类型或适配器不存在时，才停止当前实例并显示错误；同页其他列表继续工作。
- 没有未捕获异常、全局空白、重复错误日志或敏感配置输出。
