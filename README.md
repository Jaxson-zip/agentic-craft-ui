# Agentic Craft UI

面向独立开发者的产品原型、全栈功能和已有应用改造工作流。帮助 Agent 把用户路径、契约、实现和验收串起来，减少架构漂移与无效上下文加载。

它由 Agent Skills 格式的指令、按需参考、可选视觉资源和 Python 标准库脚本组成。流程由宿主 Agent 执行；本仓库没有后台调度服务、文件权限执行器或自动部署系统。

## 适用场景

| 场景 | 入口 |
| --- | --- |
| 新产品、重要路线变化 | 先比较完整产品/服务、验证关键可行性，再实现确有缺口的部分 |
| 已定路线的较大交互变化 | UI-First：先验证可点击原型，逐步落实契约和真实数据 |
| 多租户 SaaS、跨领域系统 | 先确定身份、领域与数据边界，再贯通纵向业务路径；维护架构图及对应证据 |
| 纯后端、CLI、算法 | Logic-First：输入输出、错误和核心行为先行 |
| 已有应用改造 | Brownfield：复用既有栈，定向定位，渐进替换 |
| 小修复 | 精简路径，跳过完整原型、架构图和团队设置 |

根据用户、任务、内容密度与平台特征推导视觉方向（如高密度专业工作台、纯净业务系统、消费端内容界面，或严格沿用既有设计系统），不设单一强制默认风格。不会因风格推导自动引入动画库、样式库或外部框架。

## 有什么改进

- 主 `SKILL.md` 保留分流和决策规则；UI、架构、协作、验收细则按需加载。
- 复杂或持续任务用既有文档保留核心结果、已选方向、实际证据及下一步；开始扩建与交付前核对，避免长会话中用外围进展替代原目标。小修复不强制新建文件。
- 新产品与重要选型先澄清交付、已有答案及待定约束，先评估现有系统和成熟业务底座，再考虑 starter、单项模块与未覆盖的差异；采用几个库不代表已完成复用选型。测试也要说明假设与边界，不能成为默认自建的理由。
- 架构快照有范围、依据和更新规则，源码变化时重新核对；不要求永久相信旧地图。
- 采用项目现有包管理器与检查命令，不统一强制 Biome、Zod、TypeScript 或 npm。
- 多 Agent 按任务独立性与宿主能力选择，写入范围是协作约定，实际隔离取决于宿主工具。
- 验收区分静态检查、运行时契约、业务结果、真实 UI 和生产构建；保留失败与受阻项。
- 已授权反馈由宿主实际修改、验证并关联原任务；技术通过交给用户验收，自动录入不代替执行。见 [限定执行案例](docs/FEEDBACK_EXECUTION_CASE.md)。

## 目录

```text
agentic-craft-ui/
├── SKILL.md
├── references/
│   ├── ui.md
│   ├── intake.md
│   ├── discovery.md
│   ├── visual-presets.md
│   ├── art-direction-motion.md
│   ├── controls-and-color.md
│   ├── architecture-context.md
│   ├── saas-architecture.md
│   ├── collaboration.md
│   └── delivery.md
├── assets/
│   ├── themes.css
│   └── theme-preview.html
├── scripts/
│   ├── repo_map.py
│   └── sync_skill.py
├── tests/
└── docs/
```

## 安装与使用

运行 skill 时完整保留 `SKILL.md`、`references/`、`assets/` 与 `scripts/` 的相对结构。只复制主文件会丢失参考、视觉资源和工具；维护预设时还需 `tests/`，完整克隆或交付包均包含它。Skill 使用 [Agent Skills 标准](https://agentskills.io/specification)；各宿主的发现路径、工具权限与子 Agent 能力仍有差异。

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

### 同步与安装校验

已有独立源码目录时，从源码根目录运行下列命令。默认只读，输出 missing、changed、extra 与文件数；退出码 `0` 表示内容一致，`1` 表示有差异，`2` 表示输入错误或失败。

```powershell
python -X utf8 scripts/sync_skill.py "$env:USERPROFILE\.codex\skills\agentic-craft-ui"
python -X utf8 scripts/sync_skill.py "$env:USERPROFILE\.codex\skills\agentic-craft-ui" --apply --backup-dir "$env:USERPROFILE\.codex\backups\skills"
```

工具仅复制 `SKILL.md`、`README.md`、`LICENSE` 与存在的 `references/`、`assets/`、`scripts/`、`agents/`、`docs/`、`tests/`；不复制 Git、缓存、node_modules 或根目录的其他文件。既有安装存在变更时，先在指定外部目录备份并校验，再写入和逐文件核对 SHA-256。安装目录的 `.craft-install.json` 记录来源、文件哈希与整体内容指纹，比较时仍重新读取文件，不盲信旧清单。

有额外文件时默认拒绝覆盖；检查输出后，显式加 `--prune` 才会在备份成功后移除它们。拒绝源码/安装/备份路径重叠、Git 工作副本目标、链接/Windows junction，以及包中的嵌套 `SKILL.md`；历史冻结指令使用 `SKILL.snapshot.md`。备份应放在宿主技能发现目录之外，避免旧入口再次注册。工具使用逐文件替换，不承诺整棵目录原子切换或并发安装；失败时按 stderr 中的备份路径恢复。

它用于独立源码向安装目录同步；直接在 Git 克隆目录维护时使用正常 Git 工作流，不对该目录运行 `--apply`。普通应用开发无需运行安装工具。

### Claude Code

完整目录放在 `.claude/skills/agentic-craft-ui/` 或 `~/.claude/skills/agentic-craft-ui/`，使用 `/agentic-craft-ui`。参见 [Claude Code 官方文档](https://code.claude.com/docs/en/skills)。

### 其他 Agent

按该宿主当前的 Agent Skills 文档安装完整目录。没有 skill 发现机制时，显式要求 Agent 读取主文件并允许访问相邻参考和脚本；不承诺复制为单一 rules 文件就能获得全部能力。

例如：

```text
用 agentic-craft-ui 做一个个人订阅管理看板。先验证添加订阅、查看到期日和取消订阅的交互，再接真实数据。
```

## 视觉资源与复用决策

可选 [配色预设](references/visual-presets.md) 提供清透浅色与冷黑深色的语义变量，含按钮前景色、状态标签与焦点色；[本地预览](assets/theme-preview.html) 不依赖网络或安装包。通过数值检查的配对不能替代实际界面验收。已有品牌、暖色阅读产品、专业侧栏布局仍按用户与任务选择，不强制蓝白、920px、双主题或固定数量的审批。

新产品选型和确有复用价值的任务按 [生态调研](references/discovery.md) 判断许可证、适配与维护成本；小改动、已定路线和离线任务可以直接推进。没有检索能力时如实标注，不声称已经查遍开源生态。

按需求比较可直接采用的服务与完整产品，GitHub 只是来源之一；先检验最可能否决路线的核心能力，再扩建依赖它的定制界面。缺设备或凭据时保留未知、继续独立工作，不用保存/同步等局部通过替代核心结果。本轮失效与修订评估见 [复用关口复审](docs/REUSE_GATE_REVIEW.md)；指令检查不能保证 Agent 在真实任务中一定遵循。

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
python scripts/sync_skill.py --help
git diff --check
```

测试使用临时项目验证索引与快照行为，并检查实际发货 CSS 的文字、状态、按钮与焦点配色。行为场景与结果见 [验证记录](docs/VALIDATION.md)；离线决策评估不等于实际产品端到端测试或跨模型基准。

另在 Codex 中完成了 [订阅管理真实项目实验](docs/REAL_PROJECT_VALIDATION.md)：原型、HTTP + SQLite、30 天需求变更、生产路径与独立审查。记录包含截图、实际检查和未验证范围；没有证明跨平台运行或模型能力提升。

[SaaS 架构案例](docs/SAAS_ARCHITECTURE_CASE.md) 提供多租户协作平台的系统边界图、模块图、ER 图、事务/异步流程及本地切片的实际证据。该工程验证限定的跨模块行为，没有完成大型 SaaS 的生产认证、外部集成或容量验证。

该案例随后被用户否定产品/视觉质量，并指出重复自建的风险；不将它推荐为成品模板。对应流程修订、现成方案的资料核对与行为检查边界见 [开工与复用复审](docs/PREFLIGHT_REVIEW.md)。

后续 [成熟模块集成实验](docs/REUSE_INTEGRATION_CASE.md) 使用 Better Auth 的真实身份/组织、业务 SQLite 与新进程读取，10 项限定测试通过，并复现修正了在途权限撤销的竞态。它包含系统边界、数据关系与撤销时序图及可复现源码；没有完成 HTTP/UI 联调，不将该依赖强制为 skill 的默认技术栈。

之后 [Graphite API 案例](docs/GRAPHITE_API_CASE.md) 已把成熟身份/组织接入浏览器：登录、组织、任务保存/刷新、权限与冲突恢复实际运行，应用 19 项测试和相关浏览器检查通过。它是限定本地切片，尚不代表完整 SaaS、生产认证或 skill 的普遍提升。

本轮完善相对 Gemini 更新 `49b427f` 的内容、独立场景评估和具体限制见 [第二轮验证](docs/REFINEMENT_ROUND2.md)。历史记录保留各自基线，不自动代表当前版本通过。

2026-10-22 增加可复制执行的 [行为夹具](tests/behavior/execution/README.md)，覆盖日期边界、SQLite 归档及采集受阻；执行者实际修改或运行，由评审者复跑原始检查。主入口压缩重复规则，补充当前决定与信息优先级检查；安装工具加入备份、哈希和发现入口回归。本轮结果与限制见 [优化记录](docs/OPTIMIZATION-20261022.md)，不将有限任务通过解释为模型普遍提升。

## License

[MIT](LICENSE)
