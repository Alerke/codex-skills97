# 模块类型路由

| LTD 模块或需求 | 优先 Skill |
| --- | --- |
| 顶部 Header、主菜单、移动端汉堡、搜索、登录、语言、吸顶 | `ltd-top-nav-builder` |
| Footer 栏目、页脚链接、多列分组、移动端折叠 | `ltd-bottom-nav-builder` |
| 新版表单、preset、字段、校验、验证码、上传、提交 | `ltd-form-module-builder` |
| 图片或视频 Banner、全屏幻灯片、媒体轮播 | `ltd-banner-builder` |
| 产品与商城商品列表 | `ltd-product-list-builder` |
| 文章、视频、图册、图文、公告、活动、问答、知识、招聘、媒体报道列表 | `ltd-article-list-builder` |
| 案例列表 | `ltd-case-list-builder` |
| 自定义内容列表 | `ltd-custom-content-list-builder` |
| 文本、图片、按钮、图标、背景层、分割线、富文本 | 本 Skill |
| 单视频、地图、搜索框、滚动公告、跑马灯、悬浮组件 | 本 Skill |
| 数据查询、属性搜索、门店筛选 | 本 Skill + 真实接口资料；数据复杂后再拆领域 Skill |

## 不重复拆分

- 简单静态内容差异主要是配置和视觉，不为每种标签复制同一套平台规则。
- 具有独立数据接口、状态机或运行时的模块才拆为领域 Skill。
- 分类导航属于对应列表 Skill；站点导航属于顶部/底部导航 Skill。
- 移动端固定 Tab、侧边栏和面包屑若用户提供稳定示例后可独立拆分；当前不得猜测 API `position`。
