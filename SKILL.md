---
name: agentic-craft-ui
description: "Use when building or changing a product UI or full-stack feature — web app, WeChat mini program or mobile app, especially for Chinese users — where the result must look polished, reuse existing solutions instead of rebuilding them, and be verified and reported honestly. 适用于面向中国用户的网页、小程序和 App：新产品、功能实现和已有项目改造。"
---

# Agentic Craft UI

目标：做出**好看、好用、真能跑**的产品，并如实说明做到了哪一步。用户意图和项目已有规则优先。

## 1. 先判断任务

先看项目规则、当前改动、清单与锁文件，弄清现有框架、组件和命令。只读当前需要的参考。

| 任务 | 怎么做 | 读哪些参考 |
| --- | --- | --- |
| 新产品 | 先查有没有现成产品或底座能直接用，再定栈、布局和视觉，最后连通一条可点的主路径 | [生态调研](references/discovery.md) → [平台与组件库](references/platforms.md) → [页面布局库](references/layouts.md) → [视觉规范](references/visual-style.md) → [UI 与交互](references/ui.md) |
| 已有项目加功能 | 沿用现有栈、组件和风格，只改需要改的 | [架构与上下文](references/architecture-context.md)；改界面再读 UI 与交互 |
| 纯后端、CLI | 先定输入输出和错误，再实现 | [验收与交付](references/delivery.md) |
| 小修复、文案 | 直接改，直接验证，不走上面的流程 | 不需要 |

面向中国用户时加读 [中国用户](references/china.md)。用户提到多租户、团队协作系统时加读 [SaaS 架构](references/saas-architecture.md)；需要并行委派时读 [多 Agent 协作](references/collaboration.md)。

方向、风格或关键能力真的不确定时，按 [开工澄清](references/intake.md) 只问会改变结果的问题，并附上建议的默认答案。

## 2. 做好看

- 已有设计系统就沿用。没有时，以 [视觉规范](references/visual-style.md) 为默认审美：浅色、近黑主按钮、中文字体随项目打包，强调色**按项目选**：先按领域定色相，再和页面上大面积的颜色避让（用 [accent.py](scripts/accent.py) `--avoid` 检查并生成配套色），报告里写出备选和放弃理由，再加**一个和核心动作相关、亲手试过的招牌交互**。先打开 [示例页面](assets/demo.html) 用一遍。
- 布局**按项目选**：按核心动作从 [页面布局库](references/layouts.md) 里挑一种国内参考项目的骨架（滴答、flomo、思源、LobeChat、Folo、Innei、Dify、落地页），并检查防空洞规则。
- 写列表、图标、数字、图表前，先看 [组件配方](assets/patterns.html)，照“照做”一栏写；“不要这样”一栏是 AI 最常做出的后台表格样子。
- 用成熟组件库打底（见 [平台与组件库](references/platforms.md)），再用视觉规范的 tokens 覆盖它的默认主题。不要手写一套简陋控件，也不要原样使用组件库的默认蓝。
- 想要更鲜明的品牌或叙事动效时，读 [艺术方向与动效](references/art-direction-motion.md)。
- 交付前在桌面和手机宽度各截一张图，按 [防模板化自查](references/art-direction-motion.md#防模板化自查) 看一遍，命中的改掉。

## 3. 做对

1. **先复用。** 认证、支付、复杂控件、图表、编辑器这类通用能力，先用现成产品、服务或库；自己写必须说出现成方案哪里不合适。
2. **读到影响范围为止。** 改动前读相关的实现、调用方、测试和配置；字段、单位、错误和状态要和真实接口一致。
3. **跑通真实路径。** 修复先复现再改；功能至少走通一条真实路径，检查失败后能否恢复，失败时不丢用户输入。
4. **只改需要改的。** 保留别人的改动，沿用项目工具，不顺手重构或格式化无关代码。

## 4. 如实汇报

按 [交付报告](references/templates.md#交付报告) 写，短而直接：结果、改动、没验证的。

- 每项检查标 `passed / failed / blocked / not-run`，并指向命令、文件或截图。
- 核心路径没跑通，整体就是没完成；构建通过、截图好看都不能替代它。
- 视觉是否满意由用户判断，技术检查通过后写“待你验收”。
- 外部操作（部署、发消息、付款、迁移数据）遵循用户已有授权；这个 skill 不附带任何权限。

## 工具

- [repo_map.py](scripts/repo_map.py)：JS/TS/Vue 项目的轻量符号索引和快照检查，用法见 `--help`。
- [themes.css](assets/themes.css)：视觉规范对应的 CSS 变量，可直接复制或映射到组件库主题。
- [accent.py](scripts/accent.py)：输入一个品牌色，生成强调色的四个配套值（浅色和深色）并检查对比度。
- [sync_skill.py](scripts/sync_skill.py)：只在安装或维护本 skill 时使用，见 [README](README.md#同步与安装校验)。
