# 动态字段

## images

- 把非数组归一为空数组。
- 每项按 `image.url`、`url`、`image.thumbnail`、`thumbnail` 依次读取安全 URL。
- 需要多图轮播时只在当前卡片实例初始化，并在重渲染前销毁。
- 默认只取第一张有效图；不要因第一项无效而忽略后续有效图片。

## attrs

attrs 可能是数组或对象。先归一成：

```js
{
  byId: {},
  byKey: {},
  byName: {}
}
```

- 数组项按真实 `id/key/name/label/value` 映射。
- 对象键值原样进入 `byKey`。
- 字段缺失返回空字符串或配置默认文案，不抛异常。
- 不把 attrs 值当 HTML，除非字段规范明确且经过净化。

## content

- 默认列表使用 `abstract`。
- `content` 可能含 HTML、富文本或普通文本。
- 用户明确要求富文本展示时，必须先确认内容格式并使用平台可信净化器。
- 不用正则表达式声称完成 HTML 安全净化。

## defined_link

- 空值表示不可点击。
- 只允许 http、https、站内相对路径和 hash；按任务需要允许 mailto/tel。
- 拒绝任意 javascript/data/vbscript。
