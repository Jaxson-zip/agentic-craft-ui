---
name: agentic-craft-ui
description: "Use when building or changing a product UI or full-stack feature — web app, WeChat mini program or mobile app, especially for Chinese users — where the result must look polished, reuse existing solutions instead of rebuilding them, and be verified and reported honestly. 适用于面向中国用户的网页、小程序和 App：新产品、功能实现和已有项目改造。"
---

# Agentic Craft UI

做出**好看、好用、真能跑**的产品，并如实说明做到了哪一步。用户的要求和项目已有的规则永远优先。

## 先判断任务

| 任务 | 怎么做 | 读什么 |
| --- | --- | --- |
| 新产品 | 先查有没有现成产品或底座能直接用；选组件库，按项目定颜色和布局；连通一条能点的主路径 | [ui.md](references/ui.md)、[delivery.md](references/delivery.md) |
| 已有项目加功能 | 沿用现有栈、组件和风格，只改需要改的 | [delivery.md](references/delivery.md)；改界面再读 ui.md |
| 纯后端、CLI | 先定输入输出和错误，再实现 | [delivery.md](references/delivery.md) |
| 小修复、文案 | 直接改，直接验证 | 不用读 |

需求真不清楚时，只问会改变结果的一两个问题，并附上你建议的默认答案；其余按默认推进。

## 做好看

- 已有设计系统就照用。没有时用成熟组件库（shadcn/ui、Ant Design、Arco 等）打底，并**换掉它的默认主题**。
- 颜色、布局都按项目定：先看项目领域和核心动作，再从 [ui.md](references/ui.md) 的参考表里选；不要每个项目都套同一套。
- 中文界面字体随项目打包（`npm install misans` 等），不用 Google Fonts。
- 列表是扁平分组，不是一行一张卡片；每个实体都有图标；全站只有一个强调色。写之前看一眼 [组件配方](assets/patterns.html)。
- 交付前截一张桌面图、一张手机图，按 ui.md 末尾的自查看一遍。

## 做对

1. **先复用**：认证、支付、复杂控件、图表、编辑器先用现成的；自己写要说出现成方案哪里不合适。
2. **读到影响范围为止**：改之前读相关的实现、调用方和测试。
3. **跑通真实路径**：修复先复现再改；功能至少走通一条真实路径，失败时不丢用户输入。
4. **只改需要改的**：保留别人的改动，沿用项目工具，不顺手重构无关代码。

## 如实汇报

短而直接，用户先看到结论：

```markdown
**结果**：<做成了什么，能不能用；没做成就直说>
**改动**：<文件和一句话>
**没验证的**：<具体项和原因>
```

- 核心路径没跑通，就写没完成；构建通过、截图好看都不能替代它。
- 界面好不好看由用户判断，写“待你验收”。
- 部署、付款、发消息等外部操作只按用户已有授权做；这个 skill 不附带任何权限。
