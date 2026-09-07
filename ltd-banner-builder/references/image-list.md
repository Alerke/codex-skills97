# Banner slides 数据

## 配置根项

```json
{
  "key": "slides",
  "label": "Banner 图片列表",
  "value": "[]",
  "default_value": "[]",
  "input_type": "imageList"
}
```

`$[slides]` 替换后通常是数组；旧数据为 JSON 字符串时仅兼容解析一次。显式 `[]` 是有效空配置，不能自动恢复示例图。

## 常见节点与字段优先级

```js
{
  url: 'https://example.com/banner.jpg',
  filepath_thumb: 'https://example.com/banner-thumb.jpg',
  name: '图片名称',
  title: '可见主标题',
  subtitle: '可见副标题',
  hidden: false,
  jump: {
    type: 'none',
    href: '',
    target: '_self'
  }
}
```

- 主标题：独立 slide 变量 → `title → name`。
- 副标题：独立 slide 变量 → `subtitle → desc → description`。
- alt：`name → title`；可见标题已表达同一内容且图片仅装饰时允许空 alt。
- 点击：`jump` 对象；旧扁平 `href/target` 只作兼容。

## 上传媒体 URL 归一化

LTD 不同编辑器版本、旧数据和上传返回值可能把图片地址保存成字符串或嵌套对象。不要只写 `item.url`。按主图优先、缩略图兜底提取：

1. 顶层 `url`、`image`、`filepath`、`src`。
2. 上述字段若是对象，继续读取其 `url/filepath/src/path`。
3. 兼容 `file.url/file.filepath/file.src`、`image.file.url` 等一层或两层常见媒体对象。
4. 最后才使用 `filepath_thumb` 及其对象形式。
5. 每个候选都必须经过安全相对或 HTTP(S) 图片 URL 校验；空对象不能被转成字符串 `[object Object]`。

可用递归深度受限的辅助函数，避免对未知对象无限遍历：

```js
const readMediaUrl = (value, depth) => {
  if (typeof value === 'string') return normalizeImageUrl(value);
  if (!value || typeof value !== 'object' || depth > 2) return '';
  const keys = ['url', 'filepath', 'src', 'path', 'image', 'file'];
  for (let index = 0; index < keys.length; index += 1) {
    const found = readMediaUrl(value[keys[index]], depth + 1);
    if (found) return found;
  }
  return '';
};

const imageUrl = readMediaUrl(item.url, 0)
  || readMediaUrl(item.image, 0)
  || readMediaUrl(item.filepath, 0)
  || readMediaUrl(item.src, 0)
  || readMediaUrl(item.filepath_thumb, 0);
```

上传图片后只显示遮罩色/黑色，通常说明 DOM 已建立但没有拿到有效主图 URL，或图片加载失败；必须检查实际 `$[slides]` 数据形状与 `<img src>`，不能直接归因于上传失败。

## 三张独立文案

标准三张增强档必须提供：

```text
slide_1_title       slide_1_subtitle
slide_2_title       slide_2_subtitle
slide_3_title       slide_3_subtitle
```

- 这些变量在变量设置面板中稳定可见，解决 imageList 界面只显示图片、不能稳定编辑扩展 `title/subtitle` 的问题。
- 变量值是权威覆盖值，包括空字符串；空标题隐藏标题元素，空副标题隐藏副标题元素。
- 每张都创建相同的标题、副标题和 CTA 容器，不能在 DOM 结构上只给第一张内容。
- 第四张及以后回退列表字段。若用户要求每张都独立配置且数量可变，优先使用列表扩展字段；若编辑器不支持，先确认最大张数再增加变量。
- 维护已有列表中的 `title/subtitle` 时不能删除；它们仍作为非增强档或超出覆盖范围的回退。

## 安全读取

```js
const readHidden = (value) => (
  value === true || value === 1 || value === '1' || value === 'true'
);

const parseSlides = (value, fallback) => {
  if (Array.isArray(value)) return value;
  if (typeof value !== 'string' || !value.trim()) return fallback;
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : fallback;
  } catch (error) {
    return fallback;
  }
};
```

- 不使用 `Boolean(item.hidden)`。
- 节点不是普通对象、图片无效或处于隐藏状态时跳过。
- 文本只接受字符串、数字等可安全转成文本的简单值；对象和数组回退空字符串。
- 解析失败与显式空数组要区分：前者可显示“配置不可解析”的编辑器诊断态，后者显示稳定空状态。

## DOM 渲染

优先用 DOM API：

```js
const slide = document.createElement('div');
const image = document.createElement('img');
const title = document.createElement('h2');

slide.className = 'swiper-slide';
image.className = 'ltd-banner-bg';
image.src = item.imageUrl;
image.alt = item.alt;
title.className = 'ltd-banner-title';
title.textContent = item.title;
```

不要把原始标题、副标题或图片地址直接放进模板字面量的 `innerHTML` 或 `style="background-image:..."`。`error` 事件只标记当前 slide 并显示局部降级背景，不能销毁整个 Banner。

## jump

默认安全支持 `none/web/url/mobile/email`；`_blank` 补安全 rel。`imageList` 的嵌套 jump 不会自动获得根级 `input_type: jump` 的属性注入。

`openForm/popup/module/miniProgram` 未经当前模块实测时降级为不可点击，不能放行任意 JavaScript URL。根级 CTA jump 必须使用 platform.md 的嵌套属性注入规则。
