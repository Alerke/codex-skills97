# 案例列表平台与运行时

- 用 `document.currentScript` 定位当前 `.gw-browse-module` 和 `.caseListYYYYMMDD`。
- 状态、事件解绑、请求序号、分类 Map 和销毁标记均保存在实例闭包中。
- CSS 只从根类或真实模块宿主开始，默认检查 1024px、768px、576px。
- 优先使用页面已有 `r()`；不要写 localhost、测试域名、代理头或固定 token。
- 默认用原生 DOM，不重复加载 Vue、jQuery、Swiper 或图标库。
- 接口文本优先用 `textContent`；批量模板必须先分别转义文本、属性和 URL。
- 至少维护 `page/pageSize/total/selectedCatId/allowedScopeIds/sortBy/sortDirection/requestSeq/destroyed`。
- 搜索、分类、排序变化时重置第 1 页；迟到响应只在序号最新时更新。
- 分类请求失败只降级分类 UI，仍请求主列表。
- 销毁时解绑当前实例事件、定时器、观察器和全局监听。
