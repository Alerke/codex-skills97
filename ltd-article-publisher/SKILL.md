---
name: ltd-article-publisher
description: 将本地 DOCX、HTML、Markdown 或纯文本文章交给官网富文本排版技能处理并完成网站兼容校验，再通过 LTD 或兼容 articleAdd 接口安全推送到网站，包含鉴权、查重、图片边界和发布后验收。用于用户要求向网站后台新增或批量推送文章；不用于没有兼容内容接口的网站，也不代替浏览器后台手工录入。
---

# LTD 文章自动推送

把文章先排成适合官网阅读的富文本，再可靠地新增到目标网站，并用前台数据证明结果。接口返回 `code: 0` 只代表请求被接受；没有查到真实文章记录时，不得声称发布成功。

## 开始前

收集并核对：

- 完整发布接口或网站域名；
- 分类 ID `cid`；
- AccessKey Secret；AccessKey ID 不能作为 `password`；
- 文章源文件、标题、语言和可选元数据；
- 图片处理方案；
- 当前请求是否明确授权真实发布。

密钥只从运行时环境变量 `LTD_ARTICLE_ACCESS_SECRET` 读取。不得写进 Skill、脚本、项目文件、日志或最终回复。

如果用户只要求阅读、准备、测试或检查，不发送 POST。真实发布前，简要说明目标网站、分类、标题、图片策略和是否使用 HTTP；缺少明确授权时先询问。

## 接口选择

用户提供且已验证的完整接口优先。对于 LTD 开放平台：

- AccessKey Secret 通常发送到 `/api/open-api/articleAdd` 的 `password` 字段；
- `/api/cmsgateway/articleAdd` 可能是旧版密码入口，不得因为示例中出现该路径就静默替换；
- 两个入口出现矛盾时，先用不含密钥和正文的只读或空请求确认路由，再请用户或接口方确认；不得用真实文章反复试错。

需要字段、语言值和响应判定时，读取 [references/api-contract.md](references/api-contract.md)。

## 发布前正文准备（强制）

发布接口只能接收排版后的干净 HTML 片段。不得把原始 Markdown、纯文本、Word 直转的裸 HTML、完整预览页或带脚本的页面直接推送。

1. 读取 [references/pre-publish-content.md](references/pre-publish-content.md)，归一化源文件并核对标题、章节、列表、引用、链接、表格和图片位置。不得为了排版增删或改写实质内容。
2. 使用 `$website-article-editorial-layout` 生成官网富文本。用户指定配色时照用；未指定时运行该技能的 `scripts/select_palette.py --title "文章标题"`。批量发布使用 `--avoid` 排除上一篇配色，避免连续文章视觉重复。已有经过用户确认且校验通过的 HTML 不强制重排。
3. 只保留干净的 `<section>...</section>` 正文片段，不上传完整预览页，不添加公众号互动、平台工具栏、作者栏或其他详情页外壳。作者署名、来源和原文链接只在原文已有或用户提供时保留。
4. 图片必须先完成上传并替换为可公开访问的 `https://` URL 或站内路径。用户明确选择纯文字发布时，删除图片和图片说明，不保留“图片URL”“待补素材”等占位。
5. 先运行 `$website-article-editorial-layout/scripts/validate_fragment.py`，再运行 `scripts/validate_publish_html.py`；第二项必须返回 `valid: true`。最后抽查开头、中段和结尾，确认没有漏段、错序、重复标题或自创内容，并记录采用的配色名称与 ID。

`scripts/publish_article.py` 会再次执行网站兼容校验；未排版、含危险标签或仍有素材占位的正文会在联网前被拒绝。

## 准备正文

- `.docx`：提取段落、标题、列表、表格、链接和图片位置；只需纯文字且需要旧流程兜底时，可运行 `scripts/docx_to_html.py --image-policy omit`，但其输出仍须交给官网排版技能处理，不得直接发布。
- `.html`：先剥离原站样式和页面外壳，恢复语义结构，再按选定主题重新排版。
- `.md` / `.txt`：先确认或自动推断章节结构，再转换为排版 HTML；不得把 Markdown 标记原样当作富文本。
- 首段是标题时，把它用于 `title`，正文中通常不重复；如果这会改变用户提供的结构，先说明。
- 本地 `C:\`、`G:\`、`file://` 等路径不能作为网页图片地址。没有媒体上传接口或公网 URL 时，只能让用户选择纯文字、提供上传接口或明确同意已验证的其他方案。
- 不默认使用 Base64 图片；接口支持、请求体限制和用户授权都明确时才可考虑。

DOCX 转换后检查脚本输出的标题、段落、标题层级、表格、链接和省略图片数量，并抽查生成 HTML。不要仅凭文件生成成功就发布。

## 安全发布流程

1. 校验 `cid`、标题、排版后的正文、语言和接口地址；运行网站兼容校验并确认正文不含本地资源路径或素材占位。
2. 用目标站文章列表接口按分类和完整标题查重。发现同名记录时停止，报告 ID 与 URL；只有用户明确允许重复发布才继续。
3. HTTP 会明文传输 Secret。优先 HTTPS；只能使用 HTTP 时，说明风险并取得明确同意。
4. 运行 `scripts/publish_article.py`。真实提交必须带 `--confirm-publish`；HTTP 还必须带 `--allow-http`。
5. POST 只发送一次。传输超时、连接中断或响应含义不明时不得自动重试，先查列表确认是否已经生成记录。
6. 发布后按完整标题和分类查询列表，并打开 `/article/{id}` 或接口返回的 URL。ID、标题、分类和详情页都匹配才称为“已验证发布”。

推荐命令形态：

```powershell
$env:LTD_ARTICLE_ACCESS_SECRET = '<仅在当前进程设置>'
python scripts/publish_article.py `
  --endpoint 'https://example.com/api/open-api/articleAdd' `
  --site-base 'https://example.com' `
  --cid '123456' `
  --title '文章标题' `
  --content-file 'article.html' `
  --language-type 'zh-cn' `
  --confirm-publish
```

排版完成后，先运行以下本地门禁：

```powershell
python "<website-article-editorial-layout>/scripts/validate_fragment.py" 'article.formatted.html'
python scripts/validate_publish_html.py --html 'article.formatted.html'
```

先检查而不发布时使用 `--dry-run`。即使使用 `--dry-run` 或 `--skip-preflight`，排版门禁仍会执行。列表接口不可用时，可在用户明确接受无法查重的风险后使用 `--skip-preflight`；无法验收时可用 `--skip-verify`，但最终必须标记为“接口已接受，未验证发布”。

## 停止条件

- 接口返回非零 `code`：停止并报告原始错误，不更换密钥字段或接口后自动重试。
- `code: 0` 但 `data` 为空：继续只读验收；查不到文章就报告“未发布或未确认”，不能报成功。
- 列表已出现文章但详情页暂不可访问：报告记录 ID 和当前状态，不再次 POST。
- 排版校验不通过、密钥无效、分类不属于目标站、接口权限未启用或图片方案未确定：停止并报告具体问题。

## 结果交付

成功时给出标题、采用的官网配色名称与 ID、分类、文章 ID、可点击 URL、正文/图片策略和验收信号。失败时区分：排版门禁失败、鉴权失败、接口拒绝、传输状态未知、接口假成功但未写入、列表可见但详情不可访问。不得回显 Secret。
