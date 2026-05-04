# Skill Creator

**版本**: 2.0.0
**功能**: 交互式创建 Claude Code Skill 的元工具

一个用于创建新 Skill 的引导式助手，通过结构化对话帮助用户把工作流程固化为符合官方规范的 Claude Code Skill。

---

## 核心改进（v2.0.0）

基于实际开发经验，本版本特别强化了以下关键点：

1. **Gotchas 避坑模块** — 强制要求识别高频错误场景
2. **路径引用规范** — 明确使用绝对路径，避免资源加载失败
3. **metadata.resources** — 标准方式声明外部资源
4. **版本管理** — 引导用户考虑版本迭代
5. **测试验证** — 要求创建 evals 和测试计划

---

## 工作流程

```
捕获意图 → 深度访谈 → 识别 Gotchas → 编写 SKILL.md → 创建目录 → 测试验证
```

### Step 1: 捕获意图
- 核心目标：这个 Skill 要解决什么问题？
- 触发条件：什么关键词应该激活？
- 主要输出：生成文件 / 提供建议 / 执行操作
- 复杂度评估：简单 / 中等 / 复杂

### Step 2: 深度访谈
- 触发条件的变体和排除场景
- 执行流程的详细步骤
- 外部资源需求（脚本、参考文档、模板）

### Step 3: 识别 Gotchas（关键！）
- 执行中容易犯的错误
- 常见误用场景
- 输出陷阱

### Step 4: 编写 SKILL.md
- 符合规范的 frontmatter
- 外部资源索引
- 执行步骤
- Gotchas 避坑指南
- 兜底方案

### Step 5: 创建目录结构
```
~/.claude/skills/<skill-name>/
├── SKILL.md              # 主文件（必需）
├── README.md             # 使用说明（推荐）
├── references/           # 参考资料（可选）
├── assets/               # 资源文件（可选）
├── scripts/              # 可执行脚本（可选）
└── evals/                # 测试验证（推荐）
```

### Step 6: 测试验证
- 基础触发测试
- 资源加载测试
- Gotchas 场景验证
- 创建 evals.json

---

## 关键规范

### 路径引用（重要！）

**❌ 错误写法：**
```yaml
# 相对路径无法识别
resources:
  - path: references/file.md
```

**✅ 正确写法：**
```yaml
# 绝对路径
resources:
  - path: /Users/<username>/.claude/skills/<skill-name>/references/file.md
```

**在正文中引用：**
```markdown
> 读取 `@/Users/<username>/.claude/skills/<skill-name>/references/file.md`
```

### Gotchas 模块结构

```markdown
## ⚠️ Gotchas（高频踩坑速查）

### 场景 1：XXX
- **陷阱**：描述常见误解
- **后果**：如果不避免会怎样
- **正确做法**：应该怎么处理

### 场景 2：YYY
- **陷阱**：什么情况下会失效
- **后果**：输出无效或错误
- **正确做法**：前置检查或兜底方案
```

### Frontmatter 完整示例

```yaml
---
name: thesis-data-analysis
description: >
  Analyze thesis data with evidence-based workflow...
metadata:
  version: "1.3.0"
  author: "乐义"
  language: "zh-CN"
  domain: "academic-data-analysis"
  trigger_keywords:
    - 论文数据分析
    - 统计方法选择
    - t检验
    - SPSS
  tools_hint:
    - pandas
    - scipy
  resources:
    - path: /Users/leyixu/.claude/skills/thesis-data-analysis/references/cheatsheet.md
      role: 统计检验选择速查
---
```

---

## 使用方式

用户说：
- "帮我创建一个 skill"
- "新建 skill"
- "我想做个 skill"
- "帮我写个 skill"

然后按步骤引导用户完成创建。

---

## 设计原则

1. **先调研、后设计、再实现** — 不急于写代码
2. **Gotchas 是高价值 Skill 的标配** — 把踩过的坑变成防范指南
3. **路径必须用绝对路径** — 避免资源加载失败
4. **保持可迭代** — 先简单可用，再逐步完善
5. **必须有测试计划** — evals/ 不是可选项

---

## 维护建议

当用户需要修改 skill 时：
1. 检查 version 是否需要更新
2. 验证新增的外部资源是否正确声明路径
3. 更新 Gotchas（如果有新发现的陷阱）
4. 更新 evals.json（添加新的测试用例）
