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

按顺序做，不用把清单贴进回复：

```text
- [ ] 1. 理清需求：先查有没有现成产品或库能复用，再用一条消息写出你的理解，停下来让用户改
- [ ] 2. 写设计计划：4–6 个具名颜色、字体、布局、一个记忆点，注明从参照借了什么
- [ ] 3. 做静态原型 design/prototype.html：桌面和手机画框，真实文案和数据，含空状态和出错状态
- [ ] 4. 截图，对照 ui.md 的「AI 痕迹」和「原型自评」改一轮
- [ ] 5. 把原型交给用户，停下来等确认
- [ ] 6. 按原型实现，连通一条真实主路径，再截图对照原型，按下面的格式汇报
```

第 1 步的目的是帮用户把想法理清，也让你自己弄清楚要做什么。不要抛一串开放问题，先写出你的理解让用户改，一屏以内：

```markdown
**要做的**：<一句话：做什么、给谁用、最常做的一件事；展示型还是工具型；网页、小程序还是 App>
**第一版**：做 <3–5 条>；先不做 <几条>
**现成方案**：<查到了什么，为什么还要自己做>
**参照**：<用户给了就写借哪一点；没给就按 ui.md 第 1 节提 3 个方向，每个一句话加一个代表网站>
**想确认**：<只问真正拿不准的 1–3 件事，每件附上你的默认答案，用户回“按你的”就能继续>
```

需求模糊到猜不出产品是什么时，先只问做什么、给谁用、最常做的一件事。用户确认或修改后，再开始第 2 步。

用户说过“直接做完”，第 1、5 步都不停：按自己的理解和自选的参照往下做，并在汇报里写明。

设计计划、参照和原型的细节、中文排版和国内环境见 [ui.md](references/ui.md)；复用、验证和上线合规见 [delivery.md](references/delivery.md)。列表、图标、数字、图表的写法可以打开 [组件配方](assets/patterns.html) 对照。

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

- 停在原型时只写三行：原型文件和截图、设计一句话、需要用户决定的事。
- 核心路径没跑通，就写没完成；构建通过、截图好看都不能替代它。
- 界面好不好看由用户判断，写“待你验收”。
- 部署、付款、发消息等外部操作只按用户已有授权做；这个 skill 不附带任何权限。
