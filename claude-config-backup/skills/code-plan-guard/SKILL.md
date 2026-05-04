---
name: code-plan-guard
description: >
  在涉及复杂代码变更前，强制执行"制定计划 → 用户确认 → 分步执行"的守门流程。
  触发方式：1) Hook 自动检测（推荐）；2) 显式调用 /code-plan-guard；3) 说出"先 plan 一下"。
metadata:
  version: "1.0.0"
  author: "乐义"
  language: "zh-CN"
  domain: "coding-workflow"
  trigger_keywords:
    - 先 plan 一下
    - 制定计划
    - 规划一下
    - code plan guard
    - 重构这个
    - 重写这个模块
    - 设计架构
    - 实现功能
    - 添加新模块
    - 多文件修改
hooks:
  Stop:
    - hooks:
        - type: command
          command: "sh \"${CLAUDE_SKILL_DIR}/scripts/check-plan-sync.sh\" 2>/dev/null || sh \"$HOME/.claude/skills/code-plan-guard/scripts/check-plan-sync.sh\" 2>/dev/null"
---

# Code Plan Guard（代码规划守门员）

一句话概括：**复杂代码变更前，必须先过 Plan 这一关。**

---

## 一、触发条件

### 自动触发（通过 Hook）
当 `user-prompt-submit` Hook 检测到以下特征时自动激活：
- 涉及多文件修改
- 包含架构/设计/重构类关键词
- 用户明确要求"规划"或"plan"

### 手动触发
- 显式调用：`/code-plan-guard`
- 关键词："先 plan 一下"、"制定计划再执行"

### 不应触发的场景（简单任务）
- 修复单行 bug、改配置值、加日志
- 解释代码、代码审查意见
- 写独立的小函数/脚本

---

## 二、执行流程（三步法）

### Step 1：制定计划（Plan）

**⚠️ 此时禁止修改业务代码文件（Edit/Write/Bash 涉及项目源码写入）。唯一允许写入的文件是 `task_plan.md`。**

必须输出结构化的 Plan，并**直接写入 `task_plan.md`**。格式必须与 `planning-with-files` 的 `task_plan.md` 兼容，以便后续 hooks 自动接管进度追踪。

**写入位置：** 项目根目录或当前工作目录下的 `task_plan.md`。

```markdown
# Task Plan: [一句话描述本次变更]

## Goal
[对应原"目标"：一句话说明本次变更要解决什么问题]

## Current Phase
Phase 1

## Phases
<!-- 将原"执行步骤"映射为 phases，每个步骤一个 phase -->

### Phase 1: [步骤一名称]
- [ ] [具体任务描述（做什么）]
- **Status:** in_progress

### Phase 2: [步骤二名称]
- [ ] [具体任务描述（做什么）]
- **Status:** pending

### Phase 3: [步骤三名称]
- [ ] [具体任务描述（做什么）]
- **Status:** pending

## Key Questions
<!-- 将原"风险点"转化为需要回答的关键问题 -->
1. [风险1相关的问题]
2. [风险2相关的问题]

## Decisions Made
<!-- 将原"范围"中的文件修改决策记录在此 -->
| Decision | Rationale |
|----------|-----------|
| 修改 `path/to/file1` | [修改原因] |
| 修改 `path/to/file2` | [修改原因] |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |

## Notes
<!-- 原"风险点"、"回滚方案"、"验证方式"统一放在 Notes -->
- **风险 1**：[风险描述] → 缓解措施：[措施]
- **风险 2**：[风险描述] → 缓解措施：[措施]
- **回滚方案**：[git reset / 备份文件路径 / ...]
- **验证方式**：[测试命令 / 手动验证步骤 / 观察指标]
- 本 plan 由 code-plan-guard 生成，与 planning-with-files 格式兼容。
```

### Step 2：用户确认（Confirm）

Plan 输出后，**必须**使用 `AskUserQuestion` 询问用户：

> 以上是我制定的执行计划。
>
> - **（推荐）确认执行**：按此计划分步实施
> - **修改计划**：请告诉我需要调整的地方
> - **取消**：暂不执行，保持现状
> - **缩小范围**：只执行其中某几步

**等待用户明确回复后才可进入 Step 3。**

### Step 3：分步执行（Execute）

用户确认后，严格按照 `task_plan.md` 中的 phases 执行：
1. **开始一个 phase 前**：更新 `task_plan.md` 中对应 phase 的 `**Status:**` 为 `in_progress`
2. **每完成一步**：简要汇报进度，并更新 `task_plan.md` 中对应任务的 checkbox（`- [ ]` → `- [x]`）
3. **完成一个 phase 后**：更新 `task_plan.md` 中该 phase 的 `**Status:**` 为 `complete`，并更新 `## Current Phase` 到下一阶段
4. **如遇意外情况**（与 Plan 不符），暂停并询问用户
5. **全部完成后**：按 Notes 中的"验证方式"进行验证，验证通过后更新 `task_plan.md` 中所有 phase 为 `complete`

---

## 三、复杂度判定规则

以下情况视为**复杂代码任务**（必须走完整流程）：

| 类别 | 判定标准 | 示例 |
|------|----------|------|
| **架构变更** | 涉及模块拆分/合并、接口变更 | "重构路由层"、"拆分成微服务" |
| **多文件修改** | 预计修改 ≥3 个文件 | "改完 model 还要改 controller 和 view" |
| **功能实现** | 从零实现新功能/模块 | "实现用户登录"、"添加支付模块" |
| **数据迁移** | 涉及数据库结构变更 | "加字段"、"改表结构"、"数据迁移" |
| **重写/重构** | 对现有代码进行大规模改写 | "重写这个类"、"重构整个组件" |
| **依赖变更** | 新增/移除/升级关键依赖 | "升级 React 18"、"替换 ORM" |

以下情况视为**简单任务**（可跳过 Plan）：
- 修复单个文件的特定 bug
- 修改常量/配置
- 添加日志或注释
- 格式化代码
- 解释代码逻辑

---

## ⚠️ 四、Gotchas（高频踩坑速查）

### 场景 1：误判复杂度
- **陷阱**：用户说"小改一下"，但实际涉及多文件连锁修改
- **后果**：跳过 Plan，执行到一半发现遗漏，导致代码不一致
- **正确做法**：即使任务看起来简单，**如果涉及 ≥2 个文件**，主动询问用户是否需要制定计划

### 场景 2：Plan 过粗
- **陷阱**：Plan 只写"修改文件 A、修改文件 B"，没有说明改什么、为什么
- **后果**：用户无法判断计划是否合理，确认后执行发现理解偏差
- **正确做法**：每个步骤必须包含"做什么 + 为什么 + 预期结果"

### 场景 3：执行偏离 Plan 不报告
- **陷阱**：执行时发现 Plan 有问题，擅自修改执行方式但不告知用户
- **后果**：用户预期与实际结果不一致
- **正确做法**：任何偏离 Plan 的情况，必须暂停并重新确认

### 场景 4：Hook 未生效仍直接执行
- **陷阱**：用户配置了 Hook，但 Claude 因为某种原因没有触发 Guard
- **后果**：复杂任务直接执行，缺少规划
- **正确做法**：作为 Claude，在接到任何代码任务时，先自我检查复杂度。如果符合复杂任务标准，**主动进入 Plan 模式**，不依赖 Hook

### 场景 5：用户说"直接做，不要 plan"
- **陷阱**：用户 impatient，要求跳过 plan
- **后果**：高风险操作缺少确认，容易出错
- **正确做法**：尊重用户选择，但必须口头提醒风险点。如果是破坏性操作（删除、覆盖），仍然要求确认

---

## 五、输出要求

### Plan 阶段输出
- **必须写入 `task_plan.md`**（项目根目录），格式严格兼容 `planning-with-files` 的 `task_plan.md` 模板
- 必须包含：`Goal`、`Current Phase`、`Phases`（每个 phase 带 `**Status:**`）、`Key Questions`、`Decisions Made`、`Errors Encountered`、`Notes`
- 原 6 模块映射关系：
  - "目标" → `## Goal`
  - "范围" → `## Decisions Made` 表格
  - "执行步骤" → `## Phases`（每个步骤一个 phase）
  - "风险点" + "回滚方案" + "验证方式" → `## Notes`
- Phases 状态初始值：Phase 1 为 `in_progress`，其余为 `pending`
- 风险点不能写"无"，至少列出 1 个潜在风险

### 确认阶段输出
- 必须使用 `AskUserQuestion` 工具
- 选项清晰，包含"修改计划"的兜底

### 执行阶段输出
- 每步完成后 1 句话汇报
- **同时更新 `task_plan.md`**：勾选完成的任务、更新 phase status、推进 `Current Phase`
- 最终输出验证结果，验证通过后所有 phase status 设为 `complete`

---

## 六、兜底方案

| 情况 | 处理方式 |
|------|----------|
| 用户拒绝 Plan | 提醒风险，如用户坚持则记录原因后继续 |
| Plan 中信息不足 | 先调研（读代码/查文档），补充后再呈现 Plan |
| 执行中遇到未预见问题 | 暂停执行，更新 Plan 并重新确认 |
| Hook 配置错误未触发 | Claude 自我检查，发现复杂任务主动进入 Plan 模式 |
| 用户要求"先简单看看" | 视为调研阶段，输出调研结果作为 Plan 的一部分 |

---

## 七、Hook 配置指南（用户必读）

### 1. 创建检测脚本

文件：`~/.claude/hooks/check-complex-code.sh`

```bash
#!/bin/bash
# 检测是否为复杂代码任务
COMPLEX_PATTERNS="重构|架构|设计.实现|模块|系统|复杂|多文件|改写|优化.*代码|添加.*功能|新特性|重写|迁移|升级.*版本|拆分|合并.*模块|从零|新建.*项目"
SIMPLE_PATTERNS="解释|说明|为什么|查看|读一下|查.*bug|修.*一行|加.*日志|改.*配置|格式化"

if [ -z "$CLAUDE_PROMPT" ]; then
  exit 0
fi

# 如果明确是简单任务，跳过
if echo "$CLAUDE_PROMPT" | grep -qiE "$SIMPLE_PATTERNS"; then
  exit 0
fi

# 如果是复杂任务，输出激活标记
if echo "$CLAUDE_PROMPT" | grep -qiE "$COMPLEX_PATTERNS"; then
  echo "🔒 [CODE-PLAN-GUARD] 检测到复杂代码任务。请严格执行：制定计划 → 用户确认 → 分步执行。"
fi
```

赋予执行权限：
```bash
chmod +x ~/.claude/hooks/check-complex-code.sh
```

### 2. 配置 settings.json

编辑 `~/.claude/settings.json`，添加 Hook：

```json
{
  "hooks": {
    "user-prompt-submit": {
      "before": [
        "bash ~/.claude/hooks/check-complex-code.sh"
      ]
    }
  }
}
```

### 3. 验证

测试触发：
```bash
# 应该说"检测到复杂代码任务"
echo "帮我重构用户认证模块" | CLAUDE_PROMPT="帮我重构用户认证模块" bash ~/.claude/hooks/check-complex-code.sh

# 应该无输出
 echo "解释一下这段代码" | CLAUDE_PROMPT="解释一下这段代码" bash ~/.claude/hooks/check-complex-code.sh
```

---

## 八、与现有 Skill 的关系

| Skill | 关系 | 说明 |
|-------|------|------|
| `planning-with-files` | **深度兼容** | Plan 输出直接写入 `task_plan.md`，格式完全兼容。用户确认后，`planning-with-files` 的 hooks（UserPromptSubmit/PreToolUse/PostToolUse/Stop）自动接管进度追踪和 `/clear` 恢复 |
| `skill-creator` | 独立 | 本 Skill 不依赖 skill-creator |
| `subagent-driven-development` | 可协作 | 用户确认 Plan 后，可调用 subagent 执行具体步骤 |
| `simplify` | 下游 | 执行完成后，可调用 simplify 检查代码质量 |

---

## 执行指令

当被激活时（Hook 触发或显式调用）：

1. **自我检查**：判断当前任务是否符合"复杂代码任务"标准
2. **制定 Plan**：按 `task_plan.md` 格式写入计划（兼容 planning-with-files），禁止修改业务代码文件
3. **用户确认**：使用 `AskUserQuestion` 获取用户确认
4. **分步执行**：严格按 `task_plan.md` 执行，每步汇报并更新 phase status
5. **验证收尾**：按 Notes 中的验证方式执行，验证通过后更新所有 phase 为 `complete`

---

## 禁止行为

- ❌ 未输出 Plan 直接修改文件
- ❌ Plan 未经确认就执行
- ❌ 执行偏离 Plan 不告知用户
- ❌ 将复杂任务伪装成简单任务跳过 Plan
- ❌ Plan 内容过粗（缺少步骤说明或风险分析）
- ❌ 完成一个 phase 后未更新 `task_plan.md` 的 status 和 checkbox 就进入下一步
