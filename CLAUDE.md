# AI Coworker - 多项目工作空间

> 这是一个**独立项目工作空间**，每个子目录都是独立项目，拥有自己的 CLAUDE.md、skills 和 agents。

---

## 项目结构

```
/Users/leyixu/Ai cowork/
├── CLAUDE.md                    # 本文件（工作空间说明）
│
├── research/                    # 【独立项目】科研写作
│   ├── CLAUDE.md               # 科研专用指令
│   ├── papers/                 # 文献 PDF
│   ├── drafts/                 # 论文草稿
│   └── .claude/
│       ├── agents/             # 科研专用 agents
│       │   ├── stats-advisor.agent.md
│       │   ├── data-validator.agent.md
│       │   ├── stats-executor.agent.md
│       │   └── paper-formatter.agent.md
│       └── skills/             # 科研专用 skills
│           ├── stats-advisor.skill.md
│           ├── data-validator.skill.md
│           ├── stats-executor.skill.md
│           ├── paper-formatter.skill.md
│           └── thesis-data-analysis/
│
├── management/                  # 【独立项目】组织管理
│   ├── CLAUDE.md               # 管理专用指令
│   └── .claude/
│       ├── agents/             # 管理专用 agents（预留）
│       └── skills/             # 管理专用 skills（预留）
│
└── coding/                      # 【独立项目】代码开发
    ├── CLAUDE.md               # 开发专用指令
    └── .claude/
        ├── agents/             # 开发专用 agents（预留）
        └── skills/             # 开发专用 skills（预留）
```

---

## 使用方式（重要）

### 必须切换到子项目目录

**不要**在根目录直接开始工作。每个项目都是独立的，有自己的上下文：

```bash
# ✅ 正确：进入科研项目
cd /Users/leyixu/Ai\ cowork/research
# 此时加载 research/CLAUDE.md 和 research/.claude/skills/*
# 可用：@stats-advisor, @data-validator, @paper-formatter...

# ✅ 正确：进入管理项目
cd /Users/leyixu/Ai\ cowork/management
# 此时加载 management/CLAUDE.md

# ✅ 正确：进入代码项目
cd /Users/leyixu/Ai\ cowork/coding
# 此时加载 coding/CLAUDE.md
```

### 项目上下文隔离

| 位置 | 加载的配置 | 可用的 Skills |
|------|-----------|--------------|
| `research/` | `research/CLAUDE.md` | 科研专用 skills（stats-* 等） |
| `management/` | `management/CLAUDE.md` | 管理专用 skills |
| `coding/` | `coding/CLAUDE.md` | 开发专用 skills |

---

## 项目导航

| 项目 | 用途 | 进入命令 | 专用 Skills |
|------|------|---------|------------|
| [research/](research/) | 科研写作、文献管理、数据分析 | `cd research` | `@stats-advisor`, `@data-validator`, `@stats-executor`, `@paper-formatter` |
| [management/](management/) | 组织管理、流程设计 | `cd management` | — |
| [coding/](coding/) | 代码开发、工具编写 | `cd coding` | — |

---

## 新建独立项目

如需添加新项目：

```bash
# 1. 创建项目目录
mkdir new-project
cd new-project

# 2. 创建项目配置
touch CLAUDE.md
mkdir -p .claude/agents .claude/skills

# 3. 在 ~/.claude/projects/ 中注册（Claude 自动完成）
```

---

## 内部指引（给 AI）

### 自动路由规则（根目录时使用）

当用户在**根目录**时，**先根据关键词自动判断项目**，不再询问：

| 用户问题关键词 | 目标项目 | 进入命令 |
|--------------|---------|---------|
| 论文、文献、PDF、统计、数据、分析、SPSS、三线表、脑卒中、病案、康复评估、投稿 | research | `cd research` |
| 绩效、流程、制度、科室、团队、管理、排班、考核、组织架构、运营 | management | `cd management` |
| 代码、开发、编程、脚本、工具、网站、App、调试、Bug、API、Git | coding | `cd coding` |
| skill、agent、插件、MCP、创建 skill | coding | `cd coding` |

**执行流程：**
1. 识别问题关键词 → 匹配目标项目
2. **主动提示用户**："根据你的问题，建议先进入 `xxx/` 目录"
3. **提供一键命令**：直接显示 `cd xxx` 命令
4. 等待用户执行后再继续

### 子项目目录行为

当用户在**子项目目录**时：
- 加载该项目的 `CLAUDE.md`
- 加载该项目的 `.claude/skills/*`
- 加载该项目的 `.claude/agents/*`

### 快速返回根目录

如需要在项目间切换，先返回根目录：
```bash
cd /Users/leyixu/Ai\ cowork
```
