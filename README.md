# 🚀 Agentic Craft UI (`agentic-craft-ui`)

> **OPC (One-Person Company 一人公司) 终极全栈研发架构与防漂移引擎**  
> 将混乱的 Vibe-coding 升级为确定性的工业级流水线：**UI 原型先行 ➔ 三合一 Mermaid 架构 ➔ 代码骨架拓扑树 (省 90% Token) ➔ 多 Agent 领地隔离 ➔ 真实 HTTP 自主联调**。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Awesome](https://img.shields.io/badge/AI-Agentic%20Engine-purple.svg)](SKILL.md)
[![Platform](https://img.shields.io/badge/Platform-Antigravity%20%7C%20Cursor%20%7C%20Claude%20Code-orange.svg)](README.md)

---

## 💡 为什么需要这个 Skill？

传统的 Vibe-coding 在写中大型项目时常常陷入三大噩梦：
1. **视觉是答辩**：大紫大蓝渐变、圆滚滚的胶囊卡片、泛滥的系统 Emoji，充满廉价 AI 味。
2. **架构严重漂移**：聊到第 15 轮，AI 开始胡乱建目录，前后端接口字段对不上，一改就崩。
3. **长上下文失忆与 Token 爆炸**：修个小 Bug 就要全盘读取上万行代码，烧穿上下文，导致严重脑雾。

**`agentic-craft-ui` 就是为此而生的终极工程解法。**

---

## 🌟 核心特性 (Key Features)

### 1. 🎨 UI 交互原型先行 (UI-First Prototyping)
- **告别冰冷建表**：拒绝传统的“先写 SQL -> 搞后端 -> 最后画前端”的瀑布流。
- **5 分钟摸到界面**：先用极富真实感的 Mock 数据和 **Apple HIG 极简质感**（柔和毛玻璃、连续平滑圆角、Framer Motion 弹性物理阻尼）做出可点击原型。
- **逆向推导**：原型经由创始人满意后，再从界面逆向导出后端的 **Zod 契约** 与数据库结构。

### 2. 🗺️ 三合一 Mermaid 架构图谱
在架构定型时，强制输出三张不可篡改的标准图表：
- **C4-Lite 系统分层图**：严格界定客户端、契约层 (SSOT)、业务层与数据库的隔离边界。
- **端到端数据时序图**：画清正常流转、异常拦截与事务落库全链路。
- **实体关系图 (ER Diagram)**：清晰呈现数据库主外键与实体关系。

### 3. ⚡ AST 代码骨架拓扑树 (`repo_map.py`) —— 省 90% Token
- 灵感源自 Aider 的 Repo Map 思想。
- 重构与修 Bug 时，**严禁无脑全盘扫描**。通过内置的 `scripts/repo_map.py` 提取函数签名与类型导出，将万行代码压缩为 100 行骨架树。
- **定向微创手术**：精准锁定受影响的 1~2 个文件，单次上下文消耗从 80k Token 降至 3k Token，彻底根除漂移！

### 4. 👥 异构多 Agent 协同与“领地锁死” (Write Scope)
- 调度本地的 **Claude CLI**（专攻深度逻辑）、**Gemini**（专攻视觉与多模态）或 **Codex**。
- **领地隔离机制**：为每个模型划定唯一的 `Write Scope`（只能改这几个文件）与 `Read-Only` 依赖。
- 允许修改的文件交集严格为零，彻底消灭 AI 相互覆盖和代码冲突！

### 5. 🛠️ 幕后全自动联调与真实验活 (Joint Debugging)
- **机械压路机**：自动执行 `npx @biomejs/biome check --write`，毫秒级碾平代码风格差异。
- **静态安全**：自动执行 `npx tsc --noEmit`，确保前后端 100% 遵守同一份 Zod 契约。
- **真实验活**：在后台启动服务并模拟 `curl` 请求，确保拿到 `HTTP 200` 且 JSON 格式正确才算交付。

---

## 📦 跨平台通用安装指南 (Universal Installation)

本引擎采用纯标准 Markdown + 零依赖 Python 构建，**无任何专有黑盒绑定**，可无缝运行在市面所有主流 AI Agent 工具中：

| 工具平台 (Tool) | 放置路径与生效方式 | 驱动模型 |
| :--- | :--- | :--- |
| **Google Antigravity** | 克隆至 `~/.gemini/config/skills/craft-ui/` 或 `.agent/skills/` | Gemini 2.5/3 Pro/Flash |
| **Claude Code (Anthropic)** | 软链接至 `CLAUDE.md` 或 `.claude/skills/craft-ui/` | Claude 3.7 Sonnet |
| **Cursor** | 复制为项目根目录 `.cursorrules` 或 `.cursor/rules/craft.mdc` | Claude / GPT-4o / Codex |
| **Windsurf** | 复制为项目根目录 `.windsurfrules` | Cascade / Claude |
| **GitHub Copilot** | 复制为 `.github/copilot-instructions.md` | OpenAI o3 / Codex / GPT-4o |
| **Aider / CLI 工具** | 直接作为规范加载：`aider --read SKILL.md` | 任意本地/云端 LLM |

### 快速一键拉取：

```bash
# 1. 克隆本仓库到你的开发环境
git clone https://github.com/Jaxson-zip/agentic-craft-ui.git

# 2. 无论用什么工具，直接建立对应链接即可全局生效！
```

---

## 🎯 使用方法 (Usage)

在聊天窗口中，以创始人的口吻直接发号施令：

```text
"用 agentic-craft-ui 帮我规划一个「个人财务与订阅管理看板」的全栈系统。"
```

### 你的工作流程只有极其爽快的 3 步：

1. **第 1 步：看原型拍板**  
   AI 团队 5 分钟内为你输出 Apple 极简风的前端原型。你肉眼看效果，满意后输入：*“原型通过，开工”*。
2. **第 2 步：自动排期与自治开发**  
   AI 团队自动生成 `docs/ROADMAP.md` 排期表，把 Zod 契约锁死，前端部与后端部在各自独立分支/领地内闭关开发。
3. **第 3 步：幕后联调完工交差**  
   AI 在后台自动拔掉 Mock 接上真实 API，排查 500 报错并完成修复，向你交付开箱即用的完整商业功能！

---

## 📄 开源许可证 (License)

本项目采用 [MIT 许可证](LICENSE)。
