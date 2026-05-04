# Plan Feedback Loop — 反馈循环排查指南

> 本文档同时存在于两个 skill 目录,内容相同:
> - `~/.claude/skills/code-plan-guard/PLAN-FEEDBACK-LOOP.md`
> - `~/.claude/skills/planning-with-files/PLAN-FEEDBACK-LOOP.md`
>
> 任一目录都能完整查看。出现 plan 相关问题时,从这里开始排查。

---

## 1. 这个机制为什么存在

**问题背景**：AI 看到"plan"关键词时,**不会自觉调用** code-plan-guard / planning-with-files。导致:

- 复杂任务跳过 plan 直接动手
- `task_plan.md` 不被创建,`/clear` 后无法恢复
- 用户写在 CLAUDE.md 里的硬规则空转

**解决思路**：用 hook + 日志构建 **"信任但验证"** 闭环:

1. hook 强制注入指令(命令 AI 调 skill)
2. 每次 Skill 调用 → hook 写日志
3. AI 必须 tail 日志,把内容贴在回答**最顶部(对话第一页)**
4. 缺失就**返工**,直到日志显示两个 skill 都被调过

---

## 2. 整体流程图

```
[用户输入含 plan 关键词]
        ↓
[UserPromptSubmit hook]
~/.claude/hooks/plan-trigger.sh
检测关键词 → 注入 systemMessage 指令
        ↓
[AI 必须按指令调]
Skill code-plan-guard
Skill planning-with-files
        ↓
[PostToolUse(matcher:Skill) hook]
~/.claude/hooks/log-skill-call.sh
写一行 [时间戳] skill_name 到日志
        ↓
[AI 必须 Bash 验证]
tail -10 ~/.claude/logs/plan-skill-calls.log
        ↓
[AI 必须展示]
回答最顶部贴日志(对话第一页)
        ↓
[AI 必须验证]
60 秒内两个 skill 都有记录?
   ✅ 通过 → 进入正式响应
   ❌ 缺失 → 返工(重调缺失 skill,再 tail 再展示)
```

---

## 3. 涉及文件清单

| 文件 | 作用 | 修改入口 |
|------|------|---------|
| `~/.claude/hooks/plan-trigger.sh` | UserPromptSubmit hook,关键词检测 + 注入指令 | 改关键词列表 / 改注入文案 |
| `~/.claude/hooks/log-skill-call.sh` | PostToolUse(Skill) hook,写日志 | 改 skill 白名单 / 改字段提取 jq |
| `~/.claude/settings.json` | 注册以上两个 hook | 不要轻易改结构 |
| `~/.claude/logs/plan-skill-calls.log` | 调用日志(自动生成) | 偶尔人工清理 |

---

## 4. 触发条件

`plan-trigger.sh` 触发当且仅当:

1. prompt 长度 ≥ 6 字符(避免单字 "plan" 误触发)
2. prompt 包含以下任一关键词(大小写不敏感):
   - **中文**: `分析|建模|清洗|模拟|设计|重构|开发|架构|方案|规划|搭建|改造|生成数据|训练数据|创建系统|做X流程|做X计划|绩效|项目|实施|路线图`
   - **英文**: `plan` (覆盖 Plan/PLAN/plAn 等)

---

## 5. 验证标准

`tail -10 ~/.claude/logs/plan-skill-calls.log` 末尾 10 行内,**必须同时**包含:

- `code-plan-guard` 至少一条
- `planning-with-files` 至少一条
- 两条时间戳都在**最近 60 秒**内

任一缺失 → AI 必须返工。

---

## 6. 排查清单(出错时按症状查)

### 症状 A: 关键词命中了,但 AI 没调 skill

**自查命令**:
```bash
echo '{"prompt":"先plan,帮我做 X"}' | bash ~/.claude/hooks/plan-trigger.sh | jq .
```
期望: 输出包含 `systemMessage` 和 `additionalContext`。

**可能原因**:
1. `settings.json` 不合法 → `jq . ~/.claude/settings.json`
2. AI 上下文里没收到 hook 输出 → 重启会话
3. AI 看到了指令但偷懒不调 → 加强 CLAUDE.md 硬规则

### 症状 B: AI 调了 skill 但日志空

**自查命令**:
```bash
echo '{"tool_input":{"skill":"code-plan-guard"}}' | bash ~/.claude/hooks/log-skill-call.sh
cat ~/.claude/logs/plan-skill-calls.log
```
期望: 日志多一行 `[YYYY-MM-DD HH:MM:SS] code-plan-guard`。

**可能原因**:
1. `.tool_input.skill` 字段名变了(Claude Code 升级) → 改 `log-skill-call.sh` 里的 jq 表达式
2. `~/.claude/logs/` 不存在或无写权限 → `mkdir -p ~/.claude/logs`
3. `settings.json` 里 `matcher: "Skill"` 没注册 → 检查 PostToolUse 数组

### 症状 C: 日志有内容,但 AI 没在第一页展示

**根因**: AI 没遵守 hook 的 additionalContext 指令(服从度问题)。

**修复**:
- 检查 plan-trigger.sh 的指令措辞是否够强
- 在 `~/.claude/CLAUDE.md` 加硬规则: "看到日志验证标题,必须放回答顶部"
- 考虑改成 PreToolUse 拦截级别(强制中断到 AI 展示日志为止)

### 症状 D: 验证不通过,但 AI 没返工

**自查**:
- AI 的回答里有没有"60 秒内两个 skill 都有"这种检查文字?
- 没有 → AI 跳过了第 5 步检查 → 直接告诉 AI"日志缺 X skill,返工"

### 症状 E: hook 误触发(用户不想要 plan)

**根因**: 关键词列表覆盖太广。

**修复方案**:
- 用户在 prompt 里加 "skip-plan" 标识,plan-trigger.sh 加白名单跳过
- 或精简关键词列表

---

## 7. 手动验证命令

```bash
# 测试 hook 触发
echo '{"prompt":"先plan,帮我做 X"}' | bash ~/.claude/hooks/plan-trigger.sh | jq .

# 测试日志写入
echo '{"tool_input":{"skill":"code-plan-guard"}}' | bash ~/.claude/hooks/log-skill-call.sh
echo '{"tool_input":{"skill":"planning-with-files"}}' | bash ~/.claude/hooks/log-skill-call.sh
tail ~/.claude/logs/plan-skill-calls.log

# 测试 settings.json 合法
jq . ~/.claude/settings.json > /dev/null && echo "✅ settings.json OK"

# 测试无关 skill 不被记录(应该日志不增长)
echo '{"tool_input":{"skill":"random-skill"}}' | bash ~/.claude/hooks/log-skill-call.sh

# 清理日志(慎用,会丢失历史)
> ~/.claude/logs/plan-skill-calls.log
```

---

## 8. 不要做的事

- ❌ **不要相信** SKILL.md frontmatter 里的 hooks 会自动全局注册 — 实测表明真正生效的是 `~/.claude/settings.json` 注册的全局 hooks
- ❌ **不要把关键词列表拉太宽** — 容易在普通查询里误触发
- ❌ **不要赌 AI 自觉调 skill** — 必须靠 hook 注入指令 + 日志验证
- ❌ **不要在 log-skill-call.sh 记录所有 skill** — 只记录 plan 相关两个,避免日志噪音

---

## 9. 历史

| 日期 | 事件 |
|------|------|
| 2026-05-04 | 用户测试发现"先plan,帮我..."中英文混合 prompt **完全没命中** plan-trigger.sh(关键词列表只有中文) |
| 2026-05-04 | 同时验证: AI 看到 `plan` 关键词**不会自觉**调 code-plan-guard / planning-with-files,且 SKILL.md frontmatter hooks 大概率不生效 |
| 2026-05-04 | 加英文 `plan` 关键词,改 systemMessage 显式命令调两个 skill,加 PostToolUse(Skill) 写日志,加 60 秒窗口验证 + 返工流程 |
| 2026-05-04 | 实测 6 项不确定点全部通过(关键词命中 / matcher:"Skill" 真能匹配 / `.tool_input.skill` 字段名对 / 60 秒窗口生效 / AI 服从度足够 / 日志干净) |

---

## 10. 设计哲学

**为什么用日志而不是直接 inline 验证?**

日志是"第三方证据"。如果只让 AI 自己说"我调了",那就是 AI 自我证明。日志由 PostToolUse hook 写入,不依赖 AI,不可被 AI 伪造。

**为什么要求展示在第一页?**

把验证证据放在用户最先看到的位置,出问题时**用户也能立刻发现** — 而不是 AI 偷偷跳过然后给个看似正确的答案。

**为什么 60 秒窗口而不是直接看最后两行?**

避免历史日志干扰。比如用户在 30 分钟前调过一次,如果只看最后两行,可能"看起来通过"实际上本次根本没调。60 秒窗口强制本次会话内的真实调用。
