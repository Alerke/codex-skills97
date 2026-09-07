# LTD articleAdd 接口约定

## 添加文章

- 方法：`POST`
- 编码：`application/x-www-form-urlencoded`
- 常见开放平台路径：`/api/open-api/articleAdd`
- 旧版兼容路径可能为：`/api/cmsgateway/articleAdd`

不得只凭路径名称判断鉴权方式。用户提供的当前接口文档和真实响应优先。

### 必填字段

| 字段 | 说明 |
| --- | --- |
| `cid` | 目标文章分类 ID |
| `title` | 文章标题 |
| `content` | 文本或 CMS 支持的富文本 HTML |
| `password` | AccessKey Secret，不是 AccessKey ID、登录密码或 Access Token |

### 可选字段

`author`、`source`、`original_url`、`seo_title`、`seo_keywords`、`seo_description`、`language_type`。

多个 SEO 关键词使用英文逗号分隔。没有用户提供或可靠来源时省略可选元数据，不编造作者、来源或 SEO 内容。

### 语言值

| 语种 | 值 |
| --- | --- |
| 中文 | `zh-cn` |
| 英文 | `en` |
| 繁体中文 | `zh` |
| 意大利文 | `it` |
| 日文 | `jp` |
| 韩文 | `kr` |
| 德文 | `de` |
| 西班牙文 | `es` |
| 葡萄牙文 | `pt` |
| 阿拉伯文 | `sa` |
| 法文 | `fr` |
| 俄文 | `ru` |
| 越南文 | `vm` |
| 印度文 | `in` |
| 泰文 | `th` |
| 伊朗文 | `ir` |
| 马来文 | `my` |
| 瑞典文 | `se` |
| 土耳其文 | `tr` |
| 缅甸文 | `mm` |
| 乌克兰文 | `ua` |

## 响应判定

理想成功响应包含：

```json
{
  "code": 0,
  "msg": "添加成功",
  "data": {
    "id": "文章 ID",
    "url": "文章地址"
  }
}
```

实际接口可能返回 `code: 0`、空 `msg` 和 `data: null`。此时不能判定文章已发布，必须走列表验收。

## 发布前查重与发布后验收

兼容 LTD 新版文章列表接口：

`GET /api/gatewayCms/articles/list`

常用参数：

- `mold_types=1`
- `cat_ids={cid}`
- `page=1`
- `page_size=100`
- `keywords={完整标题}`
- `sort_by=created_at`
- `sort=desc`
- `language_type={language_type}`

主结构通常是 `response.data.data`，分页字段为 `response.data.total/page_size/current_page`。文章 ID 按字符串处理，不转成 JavaScript 数字。

详情地址默认为 `/article/{id}`。兼容详情接口：

`GET /api/gatewayCms/articles/item/{id}`

验收条件：列表中存在分类和完整标题匹配的记录，记录 ID 与添加接口返回值一致（如果有），并且详情页可访问且包含标题。若列表接口结构不同，应根据目标站真实响应适配，不猜测字段。
