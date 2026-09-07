# LTD 模块结构

## 三段式结构

LTD 代码模块使用原生 CSS 与脚本结构：

```html
<style data-form-initial>
/* 首屏原生 CSS */
</style>
<style data-form-styles>
/* 业务原生 CSS */
</style>

<!-- HTML 骨架 -->

<script>
/* 业务逻辑 */
</script>
```

## 默认表单结构

普通新版表单模块不需要自建 `FormModule`、控件工厂或提交函数，直接输出 preset：

```html
<div class="xxFormModule">
  $[fitForm.preset]
</div>
```

需要拆分位置时：

```html
$[fitForm.style]
<div class="xxFormModule">$[fitForm.body]</div>
$[fitForm.script]
```

只有代码模块样式或完全自定义 DOM 时，才使用后续复杂结构。

## 命名空间

- 顶层容器类名必须唯一。
- 子级类名使用同一业务前缀。
- 禁止使用 `.container`、`.content`、`.wrapper`、`.left`、`.right` 等通用类名。
- 所有 DOM 查询必须限制在当前模块容器内。
- 不要使用 `getElementById`，避免多实例冲突。

## 多实例封装

完全自定义代码模块样式时，复杂表单模块应拆分为：

- 模块实例：保存当前容器、配置、表单、字段、布局、根节点和局部状态。
- 控件工厂：集中渲染字段控件。
- 独立提交函数：仅在不能使用 preset `submit()` 时，编排校验、payload、接口请求和按钮恢复。
- 运行时 API：向当前容器和统一注册表暴露 `ready`、`values`、`submit` 等稳定方法，保持系统 preset 和代码模块样式可被同一套外部代码调用。

推荐骨架：

```js
(() => {
  class FormModule {
    constructor(container) {
      this.container = container;
      this.root = container.querySelector('.xx-form-root');
      this.submitLocked = false;
    }

    mount() {
      if (!this.root) return;
      this.registerApi();
      this.bindEvents();
    }

    bindEvents() {
      this.container.addEventListener('click', (event) => {
        const button = event.target.closest('[data-submit-form]');
        if (!button) return;
        event.preventDefault();
        submitFormModule(this, button);
      });
    }

    createApi() {
      const api = {
        ready: () => Promise.resolve(this),
        config: () => this.config,
        values: () => this.getValues(),
        validate: () => this.validate(),
        valid: () => this.validate().valid === true,
        submit: (options) => submitFormModule(this, options && options.button),
        reset: () => this.formEl && this.formEl.reset()
      };
      Object.defineProperties(api, {
        id: { value: this.form && this.form.id, enumerable: false },
        type: { value: 'form', enumerable: false },
        container: { value: this.container, enumerable: false }
      });
      return api;
    }

    registerApi() {
      const api = this.createApi();
      this.container.__visualModuleApi = api;
      const runtime = window.VisualModuleRuntime = window.VisualModuleRuntime || {};
      runtime.__gwCodeModules = runtime.__gwCodeModules || {};
      runtime.__gwCodeModules.form = runtime.__gwCodeModules.form || [];
      runtime.__gwCodeModules.form.push(api);
      runtime.list = runtime.list || ((type) => runtime.__gwCodeModules[type] || []);
    }
  }

  const submitFormModule = async (formModule, button) => {
    // 只有完全自定义提交时才需要这类函数；默认应调用 preset runtime.submit()。
    if (formModule.submitLocked) return;
    formModule.submitLocked = true;
    button.disabled = true;

    try {
      // 校验、构造 payload、提交。
    } finally {
      formModule.submitLocked = false;
      button.disabled = false;
    }
  };

  document.querySelectorAll('.xxFormModule').forEach((container) => {
    new FormModule(container).mount();
  });
})();
```

## 代码风格

- 使用普通 `<script>` 可运行的成熟 ES6。
- 使用 `const` / `let`。
- 使用箭头函数、模板字符串和对象解构。
- 未确认环境时避免可选链、空值合并、`async/await`、动态 `import()` 和对象展开。
- 对复杂业务规则添加中文注释。
- 不要手写 ES5 拼接式运行时。
- 不要把函数源码存进 JSON 配置。
- 运行时注入函数应维护为源码函数，再通过平台能力序列化。
