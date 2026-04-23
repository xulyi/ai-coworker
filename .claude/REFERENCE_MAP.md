# 文件引用关系映射

## 项目: AI Coworker - 科研写作

生成时间: 2026-04-09

---

## 一、文件结构总览

```
/Users/leyixu/Ai cowork/
├── CLAUDE.md                          # 项目主配置
├── .claude/
│   ├── REFERENCE_MAP.md              # 本文件（引用关系映射）
│   ├── skills/                       # Skill 定义（知识库）
│   │   ├── stats-advisor.skill.md
│   │   ├── data-validator.skill.md
│   │   ├── stats-executor.skill.md
│   │   ├── paper-formatter.skill.md
│   │   └── thesis-data-analysis/     # 外部 Skill（已存在）
│   │       ├── references/
│   │       │   ├── statistical-test-cheatsheet.md
│   │       │   ├── spss-syntax-templates.md
│   │       │   ├── three-line-table-guide.md
│   │       │   └── examples.md
│   │       ├── scripts/
│   │       │   ├── assumption_checks.py
│   │       │   ├── three_line_table.py
│   │       │   └── word_three_line_table.py
│   │       └── assets/
│   │           ├── result-paragraph-templates.md
│   │           └── statistical-methods-summary-template.md
│   └── agents/                       # Agent 定义（执行者）
│       ├── stats-advisor.agent.md
│       ├── data-validator.agent.md
│       ├── stats-executor.agent.md
│       └── paper-formatter.agent.md
```

---

## 二、引用关系链

### 2.1 Stats Advisor Agent

**文件**: `agents/stats-advisor.agent.md`

**引用的 Skills**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/Ai cowork/.claude/skills/stats-advisor.skill.md` | skills/stats-advisor.skill.md | 加载工作流程定义 |

**引用的外部资源**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/.claude/skills/thesis-data-analysis/references/statistical-test-cheatsheet.md` | ~/.claude/skills/thesis-data-analysis/references/statistical-test-cheatsheet.md | 统计检验选择速查 |

**状态**: ✅ 所有引用路径有效

---

### 2.2 Data Validator Agent

**文件**: `agents/data-validator.agent.md`

**引用的 Skills**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/Ai cowork/.claude/skills/data-validator.skill.md` | skills/data-validator.skill.md | 加载工作流程定义 |

**引用的外部资源**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/.claude/skills/thesis-data-analysis/scripts/assumption_checks.py` | ~/.claude/skills/thesis-data-analysis/scripts/assumption_checks.py | 前提假设检查脚本 |

**状态**: ✅ 所有引用路径有效

---

### 2.3 Stats Executor Agent

**文件**: `agents/stats-executor.agent.md`

**引用的 Skills**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/Ai cowork/.claude/skills/stats-executor.skill.md` | skills/stats-executor.skill.md | 加载工作流程定义 |

**引用的外部资源**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/.claude/skills/thesis-data-analysis/references/spss-syntax-templates.md` | ~/.claude/skills/thesis-data-analysis/references/spss-syntax-templates.md | SPSS 语法模板 |

**状态**: ✅ 所有引用路径有效

---

### 2.4 Paper Formatter Agent

**文件**: `agents/paper-formatter.agent.md`

**引用的 Skills**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/Ai cowork/.claude/skills/paper-formatter.skill.md` | skills/paper-formatter.skill.md | 加载工作流程定义 |

**引用的外部资源**:
| 引用路径 | 目标文件 | 用途 |
|---------|---------|------|
| `@/Users/leyixu/.claude/skills/thesis-data-analysis/references/three-line-table-guide.md` | ~/.claude/skills/thesis-data-analysis/references/three-line-table-guide.md | 三线表规范指南 |
| `@/Users/leyixu/.claude/skills/thesis-data-analysis/assets/statistical-methods-summary-template.md` | ~/.claude/skills/thesis-data-analysis/assets/statistical-methods-summary-template.md | 统计学方法摘要模板 |
| `@/Users/leyixu/.claude/skills/thesis-data-analysis/assets/result-paragraph-templates.md` | ~/.claude/skills/thesis-data-analysis/assets/result-paragraph-templates.md | 结果段写作模板 |

**状态**: ✅ 所有引用路径有效

---

## 三、外部依赖检查

### 3.1 thesis-data-analysis Skill（已存在）

| 资源类型 | 文件 | 状态 |
|---------|------|------|
| 参考文档 | references/statistical-test-cheatsheet.md | ✅ 存在 |
| 参考文档 | references/spss-syntax-templates.md | ✅ 存在 |
| 参考文档 | references/three-line-table-guide.md | ✅ 存在 |
| 参考文档 | references/examples.md | ✅ 存在 |
| 脚本 | scripts/assumption_checks.py | ✅ 存在 |
| 脚本 | scripts/three_line_table.py | ✅ 存在 |
| 脚本 | scripts/word_three_line_table.py | ✅ 存在 |
| 模板 | assets/result-paragraph-templates.md | ✅ 存在 |
| 模板 | assets/statistical-methods-summary-template.md | ✅ 存在 |

**状态**: ✅ 所有外部依赖有效

---

## 四、执行流程

### 4.1 Agent 调用链

```
用户输入
    ↓
CLAUDE.md (任务路由)
    ↓
匹配 Agent
    ↓
Agent 加载对应 Skill
    ↓
Agent 引用外部资源
    ↓
执行并输出
```

### 4.2 示例：完整数据分析流程

```
1. @stats-advisor
   └─ 加载: skills/stats-advisor.skill.md
   └─ 引用: thesis-data-analysis/references/statistical-test-cheatsheet.md
   └─ 输出: 推荐统计方法

2. @data-validator
   └─ 加载: skills/data-validator.skill.md
   └─ 引用: thesis-data-analysis/scripts/assumption_checks.py
   └─ 输出: 数据质量报告

3. @stats-executor
   └─ 加载: skills/stats-executor.skill.md
   └─ 引用: thesis-data-analysis/references/spss-syntax-templates.md
   └─ 输出: Python代码 + SPSS语法 + 图表

4. @paper-formatter
   └─ 加载: skills/paper-formatter.skill.md
   └─ 引用: thesis-data-analysis/references/three-line-table-guide.md
   └─ 引用: thesis-data-analysis/assets/*.md
   └─ 输出: 三线表 + 方法段 + 结果段
```

---

## 五、验证清单

- [x] 所有 Agents 文件存在
- [x] 所有 Skills 文件存在
- [x] 所有外部引用资源存在
- [x] 所有路径使用绝对路径（`@/Users/leyixu/...`）
- [x] Agents 正确引用对应 Skills
- [x] Skills 独立完整，不互相引用
- [x] 外部资源引用指向已存在的 thesis-data-analysis

---

## 六、注意事项

1. **路径格式**: 使用 `@/` 前缀表示绝对路径，Claude Code 会自动解析
2. **外部依赖**: thesis-data-analysis 是已有 Skill，位于 `~/.claude/skills/`
3. **Skill-Agent 分离**: 
   - Skills 只定义"怎么做"（知识）
   - Agents 负责"去做"（执行）
4. **引用时机**: Agents 在执行时按需加载 Skill 和资源，非一次性加载

