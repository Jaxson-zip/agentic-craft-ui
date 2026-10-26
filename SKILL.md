---
name: agentic-craft-ui
description: "Builds and changes product UIs and full-stack features for Chinese users — web apps, WeChat mini programs and mobile apps — with a design grounded in the product's subject, existing solutions reused instead of rebuilt, and results verified and reported honestly. Use when creating a new app or page, adding a feature to an existing project, or polishing an interface that looks generic. 适用于面向中国用户的网页、小程序和 App：新产品、功能实现、已有项目改造和界面打磨。"
---

# Agentic Craft UI

做出**好看、好用、真能跑**的产品，并如实说明做到了哪一步。用户的要求和项目已有的设计系统永远优先。

## 先判断任务

- **小修复、文案**：直接改，直接验证，不用读参考。
- **已有项目加功能**：沿用现有栈、组件和风格，读 [delivery.md](references/delivery.md)；改界面再读 [ui.md](references/ui.md)。
- **新产品或新页面**：按下面的流程走，两篇参考都读。
- **纯后端、CLI**：先定输入输出和错误，再实现，读 [delivery.md](references/delivery.md)。

## 新产品流程

把这份清单复制到回复里，逐项勾掉：

```text
- [ ] 1. 理解主题：这是什么产品、给谁用、用户最常做的一件事是什么
- [ ] 2. 查复用：有没有现成产品或库能直接用；选组件库
- [ ] 3. 写设计计划：4–6 个具名颜色、字体、ASCII 线框、一个记忆点
- [ ] 4. 对照 ui.md 的「AI 痕迹」自审计划，雷同的部分改掉并说明
- [ ] 5. 实现，连通一条真实主路径
- [ ] 6. 截桌面和手机两张图，自评后再改一轮
- [ ] 7. 按下面的格式汇报
```

第 3、4 步的细节、中文排版和国内环境见 [ui.md](references/ui.md)；复用、验证和上线合规见 [delivery.md](references/delivery.md)。列表、图标、数字、图表的写法可以打开 [组件配方](assets/patterns.html) 对照。

## 始终遵守

- **先复用**：认证、支付、复杂表格、编辑器、图表先用现成的；自己写要说出现成方案哪里不合适。
- **只改需要改的**：保留别人的改动，沿用项目工具，不顺手重构无关代码。
- **跑通真实路径**：修复先复现再改；功能至少走通一条真实路径，失败时不丢用户输入。
- **大陆能用**：不依赖 Google Fonts、Firebase 这类大陆打不开的服务；中文字体随项目打包。

## 汇报格式

```markdown
**结果**：<做成了什么，能不能用；没做成就直说>
**改动**：<文件和一句话>
**设计**：<一句话：主题、配色、布局为什么这样选>（只在做了界面时写）
**没验证的**：<具体项和原因>
```

- 核心路径没跑通，就写没完成；构建通过、截图好看都不能替代它。
- 界面好不好看由用户判断，写“待你验收”。
- 部署、付款、发消息等外部操作只按用户已有授权做；这个 skill 不附带任何权限。
