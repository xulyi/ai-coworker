---
haness_version: "1.0"
created_at: "2026-04-23T10:55:00+08:00"
topic: 创建 code-plan-guard Skill 及 PreToolUse Hook，在 Write/Edit 前强制执行 Plan-Confirm-Execute 流程
artifacts:
  - path: /Users/leyixu/.claude/skills/code-plan-guard/SKILL.md
    type: doc
    description: Code Plan Guard skill 主文件，定义 Plan-Confirm-Execute 流程、Plan 六模块模板、Gotchas 及 Hook 配置指南
  - path: /Users/leyixu/.claude/hooks/plan-guard.sh
    type: code
    description: PreToolUse Hook 脚本，在 Write/Edit 前注入 systemMessage，要求 Claude 检查计划状态
  - path: /Users/leyixu/.claude/hooks/check-complex-code.sh
    type: code
    description: user-prompt-submit Hook 脚本（备用方案），基于关键词检测复杂任务
  - path: /Users/leyixu/.claude/settings.json
    type: config
    description: Claude Code 全局配置，已追加 PreToolUse Hook 注册 plan-guard.sh（once: false）
---

## Conversation Goal

用户希望在使用复杂代码前，有一套"Plan → 询问 → 执行"的流程。目标是将其固化为可复用的 Skill + Hook 机制，自动在代码执行前触发。

## Key Decisions

- **触发方式**：采用 `PreToolUse` Hook（Write/Edit 前），而非 `user-prompt-submit` 关键词检测。用户明确表示不希望基于 prompt 触发。
- **约束级别**：提醒级（注入 systemMessage），依赖 Claude 自我约束，不强制阻塞工具调用。
- **触发频率**：`once: false`，每次调用 Write/Edit 前都触发（而非每会话仅一次）。
- **与现有 Hook 的关系**：与已有的 `karpathy-check.sh` 并行运行，互不干扰。

## TODO / Next Steps

- [ ] 在新会话中测试 PreToolUse Hook 是否生效（输入一个需要写代码的任务，观察 Claude 是否在 Write/Edit 前先输出 Plan）
- [ ] 根据实际使用体验，调整 `plan-guard.sh` 中注入的 systemMessage 措辞
- [ ] 如需排除特定目录（类似 karpathy-check 排除 coding/），在 `plan-guard.sh` 中添加目录判断逻辑
- [ ] 考虑是否删除备用的 `check-complex-code.sh` 及其相关配置

## Artifact Inventory

| File | Action | Description |
|------|--------|-------------|
| `~/.claude/skills/code-plan-guard/SKILL.md` | Created | Skill 主文件，包含触发条件、Plan 六模块模板、Gotchas、兜底方案 |
| `~/.claude/hooks/plan-guard.sh` | Created | PreToolUse Hook 脚本，注入 Plan Guard systemMessage |
| `~/.claude/hooks/check-complex-code.sh` | Created | 备用脚本，基于 prompt 关键词检测（未采用） |
| `~/.claude/settings.json` | Modified | 在 `PreToolUse` 的 `hooks` 数组中追加了 `plan-guard.sh` 配置 |

## New Session Prompt

我们刚才完成了 `code-plan-guard` Skill 的创建和 Hook 配置。当前状态：

- Skill 文件位于 `~/.claude/skills/code-plan-guard/SKILL.md`
- PreToolUse Hook 脚本位于 `~/.claude/hooks/plan-guard.sh`，已在 `~/.claude/settings.json` 中注册，每次 Write/Edit 前触发
- Hook 为提醒级，注入 systemMessage 要求 Claude 在修改文件前检查是否有已确认的 Plan（目标/范围/步骤/风险/回滚/验证）

请帮我验证 Hook 是否正常工作：给一个需要修改代码的任务（例如"给这个文件加一个新函数"），观察 Claude 是否在执行 Write/Edit 前先输出 Plan 并询问确认。如果行为不符合预期，请检查 `settings.json` 中的 Hook 配置和 `plan-guard.sh` 的 systemMessage 内容。

Then wait for my instructions.
