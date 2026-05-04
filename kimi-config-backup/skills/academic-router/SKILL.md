---
name: academic-router
description: |
  学术技能统一路由入口。当用户提到任何与学术、论文、科研、数据分析、病案处理相关的需求时，
  自动分析意图并路由到正确的专业 skill。避免多个学术技能之间的触发冲突。

  触发场景：
  - 任何包含"论文"、"数据"、"统计"、"分析"、"病案"、"学术"、"研究"、"写作"、"文献"的关键词
  - 脑卒中/康复/临床相关的数据处理需求
  - 不确定该用哪个 skill 时

metadata:
  version: "1.0.0"
  author: "乐义"
  language: "zh-CN"
  type: "router"
---

# 学术技能路由中心

你的任务是**分析用户的学术/科研需求，并准确路由到对应的专业 skill**。

不要直接执行任务，而是：
1. 理解用户的真实意图
2. 判断需要哪个（些）skill
3. 明确告知用户将使用哪个 skill 及原因
4. 如需要，切换到对应的项目目录

---

## 路由决策树

```
用户请求
    │
    ├─► 包含"病案"、"提取"、"病历数据"、"病案文件"
    │   └─► 病案数据提取 Skill ───────────────────────┐
    │                                                   │► 进入对应项目目录
    ├─► 包含"统计分析"、"SPSS"、"三线表"、"统计方法"     │   执行对应 Skill
    │   └─► 论文数据分析 Skill ─────────────────────────┤
    │                                                   │
    ├─► 包含"深度研究"、"文献综述"、"研究问题"
    │   └─► Deep Research Skill (~/academic-research-skills)
    │
    ├─► 包含"写论文"、"论文写作"、"润色"、"投稿"
    │   └─► Academic Paper Skill (~/academic-research-skills)
    │
    ├─► 包含"评审"、"审稿"、"评审意见"
    │   └─► Academic Paper Reviewer (~/academic-research-skills)
    │
    └─► 模糊/多重意图
        └─► 询问用户澄清或列出可选方案
```

---

## Skill 对照表

| 意图 | 关键词 | 目标 Skill | 项目目录 | 执行方式 |
|------|--------|-----------|----------|----------|
| **病案数据提取** | 病案、提取病历、处理病案、病案文件 | stroke-data-extractor | 病案项目目录 | Skill 调用 |
| **统计数据分析** | 统计分析、SPSS、三线表、t检验、方差分析、RCT | thesis-data-analysis | 数据分析项目目录 | Skill 调用 |
| **深度研究** | 文献综述、研究问题、调研、深度研究 | deep-research | ~/academic-research-skills | 进入目录执行 |
| **论文写作** | 写论文、论文大纲、润色、投稿、摘要 | academic-paper | ~/academic-research-skills | 进入目录执行 |
| **论文评审** | 评审、审稿、评审意见、修改建议 | academic-paper-reviewer | ~/academic-research-skills | 进入目录执行 |
| **全流程** | 从研究到写作全流程 | academic-pipeline | ~/academic-research-skills | 进入目录执行 |

---

## 冲突消解规则

当多个关键词同时出现时，按以下优先级：

1. **"提取" + "病案"** → 病案数据提取（最高优先级，涉及数据获取）
2. **"统计" + "分析"** → 论文数据分析（数据处理）
3. **"研究" + "问题"** → Deep Research（研究设计）
4. **"研究" + "问题"** → Deep Research（研究设计）
5. **"写作" + "论文"** → Academic Paper（论文产出）

---

## 项目隔离规则

### 目录结构建议

```
~/research-projects/
├── stroke-cases/              # 病案数据提取项目
│   ├── raw/                   # 原始病案文件
│   ├── extracted/             # 提取结果
│   └── .claude/               # 项目配置
│
├── statistical-analysis/      # 统计数据分析项目
│   ├── data/                  # 实验数据
│   ├── output/                # 分析结果
│   └── .claude/
│
└── academic-papers/           # 论文写作项目
    ├── paper-1/
    ├── paper-2/
    └── .claude/
```

### 切换目录执行

如果需要进入特定项目目录：

```bash
# 病案提取项目
cd ~/research-projects/stroke-cases
# 自动加载 stroke-data-extractor

# 统计分析项目
cd ~/research-projects/statistical-analysis
# 自动加载 thesis-data-analysis

# 论文写作（使用 academic-research-skills）
cd ~/academic-research-skills
# 自动加载全套学术研究 skills
```

---

## 执行流程

### Step 1: 意图分析
用一句话总结用户的核心需求：
> 用户需要 [做什么] 来达成 [什么目的]

### Step 2: 技能匹配
根据决策树和对照表，确定最合适的 skill。

### Step 3: 冲突检查
检查是否有其他 skill 也可能被触发，说明为什么选择当前 skill。

### Step 4: 执行建议
告知用户：
1. 将使用的 skill
2. 建议的项目目录（如适用）
3. 下一步操作

---

## 示例

### 示例 1: 明确意图
用户："帮我提取这些病案里的 Brunnstrom 分期"

分析：
- 关键词：提取、病案、Brunnstrom
- 意图：从病案文件中提取结构化数据
- 路由：stroke-data-extractor
- 建议目录：病案项目目录

回应：
> 检测到病案数据提取需求。将使用 **stroke-data-extractor** skill 处理。
>
> 建议先进入病案项目目录：
> ```bash
> cd ~/research-projects/stroke-cases
> ```
>
> 然后提供病案文件路径，我将执行提取流程。

---

### 示例 2: 多重意图
用户："我有一批脑卒中患者的病案，需要提取数据并做统计分析"

分析：
- 关键词：病案、提取、脑卒中、统计分析
- 多重意图：数据提取 + 统计分析
- 路由：分两步，先提取后分析

回应：
> 检测到两个连续需求：
> 1. **病案数据提取**（stroke-data-extractor）
> 2. **统计分析**（thesis-data-analysis）
>
> 建议流程：
> ```bash
> # 第一步：提取数据
> cd ~/research-projects/stroke-cases
> # 使用 stroke-data-extractor 提取病案数据 → 生成 CSV
>
> # 第二步：统计分析
> cd ~/research-projects/statistical-analysis
> # 使用 thesis-data-analysis 分析提取的数据
> ```
>
> 先从哪一步开始？

---

### 示例 3: 模糊意图
用户："帮我处理这批数据"

分析：
- 关键词：处理、数据
- 意图模糊，需要澄清

回应：
> "处理数据"可能涉及多个环节，请明确你的需求：
>
> 1. **数据提取** - 从病案/PDF/文本中提取结构化数据
> 2. **数据分析** - 对已有数据进行统计分析、生成图表
> 3. **论文写作** - 基于数据撰写学术论文
>
> 你的数据是什么格式？最终想达成什么目标？

---

## 记忆更新

每次路由后，更新 memory 记录：
- 用户当前项目目录
- 正在使用的 skill 组合
- 项目特定的偏好设置
