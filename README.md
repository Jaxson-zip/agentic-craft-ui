# Agentic Craft UI

一个 Agent Skill：让 AI 为**中国用户**做出好看、好用、真能跑的网页、微信小程序和 App，并如实说明做到了哪一步。

## 解决什么问题

| 问题 | skill 的做法 |
| --- | --- |
| 界面一眼 AI、不好看 | 用成熟组件库打底并换掉默认主题；颜色和布局按项目领域选，参考 flomo、滴答清单、LobeChat 等国内产品；附一页“照做 / 不要这样”的[组件配方](assets/patterns.html) |
| 重复造轮子 | 先查现成产品和库，自己写要说明理由 |
| AI 虚报完成 | 核心路径没跑通就说没完成；每个“通过”都要能复查 |
| 改老项目改乱 | 沿用现有栈和风格，只改需要改的 |
| 不懂国内环境 | 中文排版与字体、大陆能访问的依赖、备案和隐私合规提醒 |

## 目录

```text
agentic-craft-ui/
├── SKILL.md              # 入口：任务分流和核心规则（约 3KB）
├── references/
│   ├── ui.md             # 类型与参照清单、设计计划、静态原型、AI 痕迹自审、配色、中文排版、组件库、布局、组件、动效、文案
│   └── delivery.md       # 复用、改已有项目、验证、汇报、上线合规
├── assets/
│   └── patterns.html     # 组件配方，浏览器直接打开
├── evals/evals.json      # 三个评估场景（订阅看板、AI 写作助手、改已有账本），改 skill 后用它们对比
└── tests/                # 只检查体积上限、链接和评估格式，不随 skill 运行
```

Agent 运行时最多读三个 Markdown 文件，合计约 20KB。`tests/test_skill.py` 为每个文件设了体积上限，超出就会失败，防止规则越写越长。

## 安装

把整个目录放进宿主的技能目录即可，例如：

```bash
git clone https://github.com/Jaxson-zip/agentic-craft-ui.git ~/.claude/skills/agentic-craft-ui
```

- Claude Code：`~/.claude/skills/` 或项目里的 `.claude/skills/`，用 `/agentic-craft-ui` 调用。
- Codex：`~/.agents/skills/` 或项目里的 `.agents/skills/`。
- 其他宿主：按它的 Agent Skills 文档放置完整目录。

更新时在该目录里 `git pull`。

## 怎么写出来的

结构按 Anthropic 的 [Skill 编写最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：SKILL.md 只做导航和清单，细节放在一层深的参考文件里，长文件带目录。界面部分借鉴了官方 [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) skill 的做法：从产品主题出发写设计计划，再对照“AI 痕迹”清单自审；我们把它往前推了一步：先帮用户理清需求、定参照，再做静态原型给用户确认，最后才实现；在此之上补充了中文排版、国内环境和国内产品的布局参考。

## 开发

```bash
python -m unittest discover -s tests -v
```

历史版本（脚本、评估报告、示例页面等）都保留在 git 历史里。
