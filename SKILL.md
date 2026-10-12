---
name: agentic-craft-ui
description: "Use when building an interactive product prototype, implementing a UI or full-stack feature, or changing an existing application where UI behavior, API contracts and delivery evidence must remain consistent. 适用于产品界面、全栈功能和已有应用改造。"
---

# Agentic Craft UI

把用户路径、视觉、运行时契约和交付证据连起来。按影响选择流程；用户意图、项目规则和现有授权优先。完善是把已授权的结果做实，不是增加流程、依赖或产品范围。

## 先定位任务

检查相关项目规则、当前改动、清单、锁文件及已有脚本，识别框架、样式、测试和运行方式。保留既有工具与其他人的改动，不自动安装 Biome、Zod、TypeScript、动画库或外部服务。

| 情况 | 推进方式 | 按需读取 |
| --- | --- | --- |
| 新交互产品、较大用户路径变化 | UI-First：可点击主路径，明确模拟边界，再接真实契约 | [UI 与交互](references/ui.md) |
| 已有应用功能、重构 | Brownfield：沿当前实现定位，复用组件，渐进改变 | [架构与上下文](references/architecture-context.md)；改 UI 时读 UI 参考 |
| 纯后端、CLI、算法 | Logic-First：输入输出、错误与核心规则先行 | [验收与交付](references/delivery.md) |
| 小修复、文案调整 | 直接定位与验证，跳过完整原型和架构流程 | 仅有相关风险时读取参考 |

只读相关参考。新产品选型、明确要求寻找模板或复用可能节省大量工作时，读 [生态调研](references/discovery.md)。小功能、已有栈与离线任务不以全网搜索作为开工前提。

## 关键决策与实现

1. **明确成功条件。** 提取核心用户路径、可观察结果、范围和约束。缺失信息会实质改变结果且无法合理推断时才问；独立工作继续推进。
2. **做出可审阅的视觉决定。** 继承现有设计系统与用户已选方向；没有指定时按用户、任务、密度、品牌与平台选一套合理方案，简述假设并做成可运行原型。需要用户选择时提供少量有区别的具体方案或预览，不把固定数量的风格审批设为每个任务的门禁。浅色、深色、暖色、侧栏与居中布局都按场景选择；双主题只在需求或已有系统要求时实现。可选 [视觉预设](references/visual-presets.md) 提供经过数值检查的起点。
3. **保持契约一致。** 确认字段、枚举、单位、错误、身份和状态变化。沿用已有类型和运行时校验；视觉调整也要核对表单选项与 API，不能私增业务枚举或让文案承诺尚未发生的操作。
4. **读到影响边界。** 用检索、语言服务或索引定位，再读实现、消费者、测试及配置。索引是入口，不是完整事实；不限制固定文件数量。源码改变后核对相关快照。
5. **修复以失败证据为起点。** 先复现，再做最小有效改动并回归。无法稳定复现时用日志或隔离实验说明不确定性，不用行数上限阻碍调查。
6. **落实反馈与失败恢复。** 覆盖适用的 loading、empty、error、success；保存成功由实际结果确认。保留失败输入，处理项目实际的冲突与重试语义；超时可能已提交时不能盲目重发写请求。
7. **用真实证据收尾。** 按 [验收与交付](references/delivery.md) 选择检查；UI 检查见 UI 参考。分别记录 passed、failed、blocked、not-run、not-applicable。HTTP 200、mock 或 build 通过不能替代业务验收。

## 架构与协作

涉及模块边界、API、模型或权限时，读 [架构与上下文](references/architecture-context.md)，更新受影响的文档；图表服务实际问题，无持久化任务不画 ER 图。

任务可独立并行、宿主允许且具备工具时，读 [多 Agent 协作](references/collaboration.md)。小改动、有顺序依赖或用户要求单人时串行；写入范围是协作约定，只有实际权限机制才称强制隔离。

## 资源与工具

- [scripts/repo_map.py](scripts/repo_map.py)：Python 标准库的 JS/TS/Vue 轻量符号索引，含行号、指纹和快照检查。先看 `--help`；从已知 skill 路径运行，目标为应用根目录。它不是 AST、调用图或死代码检测。其他语言或工具缺失时用 `rg`、语言服务及源码，不虚构执行结果。
- [assets/themes.css](assets/themes.css)：可选浅色/深色语义色与少量组件样式。按项目适配，不覆盖现有品牌；复制前读视觉预设的适用范围。
- [assets/theme-preview.html](assets/theme-preview.html)：无需安装依赖的配色预览，可本地打开；展示颜色及按钮状态，不代表完整产品设计或无障碍认证。

## 交付

说明实际结果、改动与验证结果、具体未验证项，附可审阅文件或原型。继续完成已授权范围；外部发布按现有授权与宿主规则执行，skill 不增加权限。
