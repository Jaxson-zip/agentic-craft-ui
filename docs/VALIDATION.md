# 验证记录

日期：2026-10-12。修订基线：`f1f752817a1009e8ed3c6f4ee7753d6d536f521f`。

## 脚本回归

先添加行为测试，再在原脚本上运行：13 项失败，覆盖注释/字符串误报、常见导出漏报、Vue、静默截断、错误退出和缺失的快照检查。修订后同组 13 项通过。独立审查发现 const enum 误报和 Vue 注释 script 误报，并指出生成器函数漏报；补充 3 个用例，先观察失败，再修复，最终 16 项全部通过。

```text
python -m unittest discover -s tests -v
```

测试在临时目录创建真实文件并调用脚本，验证：

- 普通注释与字符串不会成为导出符号；具名重导出、别名、typed const、泛型函数与默认 class 可见。
- Vue 仅索引 script 内容且保留原始行号；注释中的 script 不成为符号，script 内的 HTML 注释起始字符串不影响后续导出。
- const enum 与生成器函数可被识别；无导出文件仍出现在清单，node_modules 被排除。
- 默认不静默截断；显式上限显示省略数；输出顺序与指纹可重复。
- 修改正文但保留 export 名、增删文件、配置变更会使快照过期。
- 不同根目录、缺失目录、无效 JSON 和无效 UTF-8 不会被当成成功或新鲜。
- Markdown 可写到文件并显示行号、能力限制和省略量。

## Skill 结构

使用 skill-creator 自带的 `quick_validate.py` 校验名称与 YAML 元数据。Windows 的 Python 默认 GBK 解码会导致原校验器读取中文 UTF-8 文件失败；使用 `python -X utf8` 运行后校验通过，没有修改系统设置或外部校验器。

本地 Markdown 链接、脚本 `--help` 与 `git diff --check` 在最终交付前检查。文档列明的 Python 最低版本按使用的标准库接口判断；当前实际测试运行时是 Python 3.13.9 / Windows，未运行其他操作系统或 Python 3.9 的矩阵。

## 独立审查

审查覆盖与基线的 diff、新增参考、测试和实际脚本行为。两项主要问题均已先复现再修复。复审重新运行 16 项测试与独立输出探针，确认 const/declare const enum、普通/异步/默认具名生成器、多 Vue script 块和 JS 字符串中的 HTML 注释起始标记；没有发现文档所述范围内的剩余具体问题。审查未发现修订后的流程与参考之间有实质矛盾；这一结果不保证不存在其他未覆盖缺陷。

## 离线工作流决策评估

场景保存在 [tests/behavior/scenarios.md](../tests/behavior/scenarios.md)。三个独立 Agent 分别读取无 skill、原版 skill、修订版 skill；评估时隔离父对话与其他结果。每个条件只跑一轮，并输出拟执行动作、命令和交付状态，不运行真实应用。

| 场景 | 无 skill 基线 | 原版 skill | 修订版 skill |
| --- | --- | --- | --- |
| A：Vue 老项目，地图过期、重导出、20 分钟截止 | 追踪真实依赖，保留既有工具 | 遵守永久快照与两文件限制，停止在实现文件之前 | 追踪 Vue → re-export → 实现与日期依赖；更新受影响地图，沿用 pnpm/ESLint/Vitest |
| B：赶工交付，200+build，但缺真实 UI 和边界测试 | 明确 smoke 的限制与凭据阻塞 | 仍列出无依据的 Biome/tsc 命令；也没有误称全绿 | 用项目脚本，区分静态、运行时、业务、UI 与 blocked 状态；不盲目重试凭据失败 |
| C：Python 小修复，单人、24 行复现 | 保留 Python 和必要 fixture | 借助用户约束避开不适用工具 | 单人最小修复，无行数上限，不增加 UI、数据库、JS 工具或架构流水线 |

可复核的原版 A 决策摘录：

> Under the original snapshot rule, do not rescan the repository or regenerate the map.

> Read only these two source files in addition to the two snapshots.

原版 B 拟执行命令包括 `npx @biomejs/biome check --write` 和 `npx tsc --noEmit`，即使没有事实证明这些工具适合该项目。修订版使用项目既有命令并保留缺失证据。

无 skill 基线已经做出合理决策。本轮证据支持“移除旧规则造成的阻碍”，不能推导普遍模型能力提升、Token 节省比例或成功率。这也不是实际 bug 修复、完整产品端到端测试或跨模型基准。

## 能力限制

索引仍是启发式，不保证完整语法识别或调用关系。快照新鲜仅代表已覆盖源码与配置内容未变，不包括 SQL、其他语言、未列入配置或外部服务。跨平台安装路径依据官方文档；目前没有执行 Claude Code、Gemini 或其他宿主的运行验证。
