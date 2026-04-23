---
name: skill-creator
description: 创建新的 Claude Code Skill。当用户说"帮我创建一个 skill"、"新建 skill"、"我想做个 skill"或需要把某个工作流程固化为可复用的 skill 时使用。提供交互式引导，帮助用户从零创建符合官方规范的 SKILL.md 文件和目录结构。特别关注：正确声明外部资源路径、添加 Gotchas 避坑指南、设置版本管理和测试验证。
metadata:
  version: "2.0.0"
  author: "乐义"
  language: "zh-CN"
  domain: "skill-development"
  trigger_keywords:
    - 创建 skill
    - 新建 skill
    - 我要做个 skill
    - 帮我写个 skill
    - skill 开发
    - 制作 skill
    - 元技能
    - 技能创建
---

# Skill Creator（元技能创建助手）

一个用于创建新 Skill 的交互式助手。通过结构化对话，帮助用户把工作流程固化为符合规范的 Claude Code Skill。

> **核心理念**：Skill 不是简单的 prompt 堆砌，而是**可复用、可维护、可验证**的行为规范。

---

## 第一步：捕获意图

先理解用户想解决什么问题。依次询问：

### 1. 核心目标
这个 Skill 要解决什么问题？请用一句话描述。

### 2. 触发条件
用户说什么关键词时应该激活这个 Skill？（列出 3-5 个）

### 3. 主要输出
- [ ] 生成代码/文件
- [ ] 提供分析建议
- [ ] 执行特定操作
- [ ] 其他：_____

### 4. 复杂度评估
- [ ] 简单（单一步骤，直接输出）
- [ ] 中等（多步骤，需要判断分支）
- [ ] 复杂（需要外部资源、多阶段协作）

---

## 第二步：深度访谈

根据初步回答，深入挖掘关键细节。

### 关于触发条件（关键！避免 under/over-trigger）

- 用户可能用哪些**不同说法**表达相同意图？（变体词）
- 有哪些**容易混淆**的场景应该**排除**？
- 这个 Skill 和现有 skill 会不会冲突？

### 关于执行流程

请描述典型执行步骤：
1. ____
2. ____
3. ____

- 有没有**必须先做**的判断/检查？
- 有没有**高风险操作**需要确认？
- 成功完成的**明确标准**是什么？

### 关于外部资源

是否需要配套文件？
- [ ] 脚本文件（Python/Bash 等）
- [ ] 参考文档/速查表
- [ ] 模板文件
- [ ] 示例数据

**重要**：如果有外部资源，必须在 `metadata.resources` 中声明，并使用**绝对路径**引用。

---

## 第三步：识别 Gotchas（避坑指南）

这是高价值 Skill 的关键模块。请思考：

### 执行中容易犯的错误
- 用户常有什么**误解**？（如：把"帮我做 t 检验"理解为可以直接做）
- 什么情况下会产生**错误输出**？
- 什么**边界条件**容易被忽略？

### 常见误用场景
- 用户在什么情况下会**错误使用**这个 skill？
- 需要哪些**前置信息**才能正确执行？
- 如果信息不足，应该**如何兜底**？

### 输出陷阱
- 输出格式有什么**硬性要求**？
- 什么情况下输出会**无效**或**误导**？
- 如何验证输出质量？

> 💡 **提示**：Gotchas 不是泛泛而谈，而是**具体、可检查、可避免**的错误清单。

---

## 第四步：编写 SKILL.md

根据访谈结果，生成规范文件。

### Frontmatter（头部元数据）

```yaml
---
name: <skill-name>              # kebab-case，如：thesis-data-analysis
description: >                  # 必须包含：触发条件 + 功能描述
  具体描述这个 skill 做什么，
  以及什么时候触发（关键词）。
metadata:
  version: "1.0.0"             # 语义化版本，如：1.0.0, 1.2.3
  author: "作者名"
  language: "zh-CN"            # 主要语言
  domain: "领域标签"            # 如：data-analysis, document-processing
  trigger_keywords:            # 触发关键词列表（10-20个）
    - 关键词1
    - 关键词2
    - 关键词3
  tools_hint:                  # 可能用到的工具（可选）
    - python
    - pandas
    - matplotlib
  resources:                   # 外部资源声明（如有）
    - path: /Users/<username>/.claude/skills/<skill-name>/references/file.md
      role: 资源用途说明
    - path: /Users/<username>/.claude/skills/<skill-name>/scripts/script.py
      role: 脚本用途说明
---
```

### 正文结构

```markdown
# Skill 标题

一句话概括这个 skill 的核心价值。

---

## 一、外部资源索引（如有）

> 本 Skill 包含外部资源文件，按需读取。

| 文件路径 | 触发时机 | 用途 |
|---|---|---|
| `@/Users/<username>/.claude/skills/<skill-name>/references/xxx.md` | 阶段 X | 用途说明 |
| `@/Users/<username>/.claude/skills/<skill-name>/scripts/xxx.py` | 阶段 Y | 用途说明 |

---

## 二、触发条件

- 关键词 1
- 关键词 2
- ...

---

## 三、执行步骤

1. 步骤一
   > 如需外部资源：读取 `@/Users/<username>/.claude/skills/<skill-name>/references/xxx.md`
2. 步骤二
3. 步骤三

---

## ⚠️ 四、Gotchas（高频踩坑速查）

### 场景 1：常见错误
- **陷阱**：描述常见误解
- **后果**：如果不避免会怎样
- **正确做法**：应该怎么处理

### 场景 2：边界条件
- **陷阱**：什么情况下会失效
- **后果**：输出无效或错误
- **正确做法**：前置检查或兜底方案

### 场景 3：误用防范
- **陷阱**：用户可能的错误用法
- **后果**：产生错误结果
- **正确做法**：如何识别并纠正

---

## 五、输出要求

- 格式规范
- 必须包含的内容
- 验证标准

---

## 六、兜底方案

当无法执行时：
- 情况 1：_____ → 处理方式
- 情况 2：_____ → 处理方式
```

---

## 第五步：创建目录结构

标准目录结构：

```
~/.claude/skills/<skill-name>/
├── SKILL.md                      # 主文件（必需）
├── README.md                     # 使用说明（推荐）
├── references/                   # 参考资料（可选）
│   ├── cheatsheet.md            # 速查表
│   └── examples.md              # 示例
├── assets/                       # 资源文件（可选）
│   └── templates.md             # 模板
├── scripts/                      # 可执行脚本（可选）
│   └── helper.py
└── evals/                        # 测试验证（推荐）
    ├── evals.json
    └── README.md
```

### 路径引用规范（关键！）

**❌ 错误写法：**
- `references/file.md` — 相对路径，无法识别
- `@references/file.md` — 路径不完整

**✅ 正确写法：**
```markdown
@/Users/<username>/.claude/skills/<skill-name>/references/file.md
```

**在 metadata.resources 中声明：**
```yaml
resources:
  - path: /Users/<username>/.claude/skills/<skill-name>/references/cheatsheet.md
    role: 速查表，用于阶段 X
```

**在正文中引用：**
```markdown
> 读取 `@/Users/<username>/.claude/skills/<skill-name>/references/cheatsheet.md`
```

---

## 第六步：测试与验证

创建完成后，必须进行验证：

### 1. 基础测试
```bash
# 显式调用测试
/skill-name

# 触发测试（使用关键词）
"帮我做 xxx"  # 应该自动触发
```

### 2. 资源加载测试
- 验证外部文件是否能被正确读取
- 验证路径引用是否正确
- 验证资源内容是否被使用

### 3. Gotchas 验证
- 故意触发陷阱场景，看是否能正确识别
- 测试边界条件处理
- 验证兜底方案是否生效

### 4. 创建 evals/ 目录

```json
// evals/evals.json
{
  "evals": [
    {
      "name": "basic-trigger",
      "description": "测试基础触发",
      "prompt": "用户说：'帮我做 xxx'",
      "expected": "应该触发 skill 并执行步骤 X"
    },
    {
      "name": "gotcha-handling",
      "description": "测试 Gotcha 识别",
      "prompt": "用户说：'yyy'（陷阱场景）",
      "expected": "应该识别陷阱并给出正确引导"
    }
  ]
}
```

---

## 执行指令

当用户请求创建 skill 时：

1. **按步骤访谈**：一次问 1-2 个问题，循序渐进
2. **确认理解**："我理解你想要一个能...的 skill，对吗？"
3. **强调 Gotchas**：必须让用户思考"哪些地方容易出错"
4. **创建文件**：
   - SKILL.md（主文件）
   - README.md（使用说明）
   - 外部资源（如有）
   - evals/（测试用例）
5. **验证路径**：检查所有 `@path` 是否为绝对路径
6. **展示结果**：说明文件位置和如何使用

---

## 禁止行为

- ❌ 不问清楚就直接写代码
- ❌ 忽略 Gotchas 模块的重要性
- ❌ 使用相对路径引用外部资源
- ❌ 创建过于复杂的 skill（保持可迭代）
- ❌ 不创建 evals/ 或测试计划

---

## 风格要求

- 使用中文与用户交流
- 解释专业术语（frontmatter、kebab-case、Gotchas）
- 提供具体示例帮助理解
- 强调"先调研、后设计、再实现"的原则
