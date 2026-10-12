# Agentic Craft UI

面向独立开发者的产品原型、全栈功能和已有应用改造工作流。帮助 Agent 把用户路径、契约、实现和验收串起来，减少架构漂移与无效上下文加载。

它由 Agent Skills 格式的指令、按需参考和一个 Python 标准库脚本组成。流程由宿主 Agent 执行；本仓库没有后台调度服务、文件权限执行器或自动部署系统。

## 适用场景

| 场景 | 入口 |
| --- | --- |
| 新产品、较大交互变化 | UI-First：先验证可点击原型，逐步落实契约和真实数据 |
| 纯后端、CLI、算法 | Logic-First：输入输出、错误和核心行为先行 |
| 已有应用改造 | Brownfield：复用既有栈，定向定位，渐进替换 |
| 小修复 | 精简路径，跳过完整原型、架构图和团队设置 |

默认候选视觉方向为 Apple Minimal，也可采用 Linear Dark、Clean Tech 或用户既有设计系统。不会因预设自动引入动画库、样式库或框架。

## 有什么改进

- 主 `SKILL.md` 保留分流和决策规则；UI、架构、协作、验收细则按需加载。
- 架构快照有范围、依据和更新规则，源码变化时重新核对；不要求永久相信旧地图。
- 采用项目现有包管理器与检查命令，不统一强制 Biome、Zod、TypeScript 或 npm。
- 多 Agent 按任务独立性与宿主能力选择，写入范围是协作约定，实际隔离取决于宿主工具。
- 验收区分静态检查、运行时契约、业务结果、真实 UI 和生产构建；保留失败与受阻项。

## 目录

```text
agentic-craft-ui/
├── SKILL.md
├── references/
│   ├── ui.md
│   ├── architecture-context.md
│   ├── collaboration.md
│   └── delivery.md
├── scripts/repo_map.py
├── tests/
└── docs/
```

## 安装与使用

完整保留 `SKILL.md`、`references/` 与 `scripts/` 的相对结构。只复制主文件会丢失按需参考和工具。Skill 使用 [Agent Skills 标准](https://agentskills.io/specification)；各宿主的发现路径、工具权限与子 Agent 能力仍有差异。

### Codex

本地可放在项目 `.agents/skills/agentic-craft-ui/` 或用户 `~/.agents/skills/agentic-craft-ui/`。路径与加载机制参见 [OpenAI 官方文档](https://learn.chatgpt.com/docs/build-skills)。

macOS / Linux 个人安装：

```bash
 git clone https://github.com/Jaxson-zip/agentic-craft-ui.git ~/.agents/skills/agentic-craft-ui
```

Windows PowerShell 个人安装：

```powershell
 git clone https://github.com/Jaxson-zip/agentic-craft-ui.git "$env:USERPROFILE\.agents\skills\agentic-craft-ui"
```

目标目录已存在时，先检查其来源和本地改动，再更新；不要覆盖用户已有文件。Codex CLI / IDE 中可显式使用 `$agentic-craft-ui`，桌面端从技能选择器选用；也可按 description 自动匹配。

### Claude Code

完整目录放在 `.claude/skills/agentic-craft-ui/` 或 `~/.claude/skills/agentic-craft-ui/`，使用 `/agentic-craft-ui`。参见 [Claude Code 官方文档](https://code.claude.com/docs/en/skills)。

### 其他 Agent

按该宿主当前的 Agent Skills 文档安装完整目录。没有 skill 发现机制时，显式要求 Agent 读取主文件并允许访问相邻参考和脚本；不承诺复制为单一 rules 文件就能获得全部能力。

例如：

```text
用 agentic-craft-ui 做一个个人订阅管理看板。先验证添加订阅、查看到期日和取消订阅的交互，再接真实数据。
```

## 轻量符号地图

需 Python 3.9+，无 pip 依赖。从应用根目录运行；以下以 skill 安装在 `.agents/skills/agentic-craft-ui` 为例：

```text
python .agents/skills/agentic-craft-ui/scripts/repo_map.py . --output docs/REPO_MAP.md --snapshot docs/repo-map.snapshot.json
python .agents/skills/agentic-craft-ui/scripts/repo_map.py . --check docs/repo-map.snapshot.json
```

支持 `.js/.jsx/.ts/.tsx/.mjs/.cjs/.mts/.cts/.vue` 文件的常见 ES export，记录符号名称、种类与行号；Vue 仅索引 script 块。无 export 文件仍会列入清单。可用 `--format json`，默认不限制已识别符号数；`--max-symbols N` 会显式记录省略量。

快照检查：`0` 表示索引范围内内容未变，`1` 表示过期，`2` 表示错误或不完整。内容指纹覆盖源码和选定清单/锁文件的内容与路径；函数体修改、增删文件或覆盖范围内的配置变更会触发失效。每次检测仍读取磁盘计算哈希，不是零 I/O 缓存。

**能力边界：** 使用文本启发式与普通注释/字符串屏蔽，不是 AST，不提供完整签名、依赖图、自动架构图或死代码检测。复杂模板、正则字面量、JSX 文本、解构、多变量声明、CommonJS 等可能误报或漏报。跳过预定义依赖/构建目录与符号链接，不遵循 `.gitignore`。SQL、其他语言、未列入的配置和外部系统不受指纹覆盖；“新鲜”不能证明整套架构最新。更多规则见 [架构与上下文](references/architecture-context.md)。

不承诺固定的 Token 节省比例、生成时限、零冲突或全自动商业交付。

## 开发验证

在此仓库根目录运行：

```text
python -m unittest discover -s tests -v
python scripts/repo_map.py --help
git diff --check
```

测试使用临时项目验证索引与快照行为。行为场景与结果见 [验证记录](docs/VALIDATION.md)；离线决策评估不等于实际产品端到端测试或跨模型基准。

## License

[MIT](LICENSE)
