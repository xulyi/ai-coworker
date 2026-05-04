---
haness_version: "1.0"
created_at: "2026-05-03T12:08:00+08:00"
topic: 优化 haness 产物自动追踪机制，解决 artifact discovery 不准确问题
artifacts:
  - path: ~/.claude/settings.json
    type: config
    description: 新增 SessionStart 和 PostToolUse hooks，用于自动清理和追踪会话文件变更
  - path: ~/.claude/skills/haness/SKILL.md
    type: doc
    description: 重构 artifact discovery 流程，从 3-tier 升级为 4-tier（自动 log + git 校验 + 用户确认）
  - path: ~/.claude/hooks/track-artifacts.sh
    type: code
    description: 自动追踪 git status 变更的 shell 脚本，由 PostToolUse hook 触发
---

## Conversation Goal

解决 haness skill 在记录会话产物时频繁遗漏或误报的问题。通过引入 `PostToolUse` hook 自动追踪 + git 校验 + 用户确认的三层机制，替代原来不可靠的 "AI 内心记账"（Tier 2），显著提升 haness 的 artifact discovery 准确度。

## Key Decisions

- **采用"自动化追踪为主，人工确认为辅"策略**：废弃原 Tier 2 的 AI mental bookkeeping，改为由 hook 自动维护变更日志。
- **新增两个 settings.json hooks**：
  - `SessionStart`：新会话开始时自动清理旧的 `session-artifacts.log`，避免跨会话污染。
  - `PostToolUse`（Write|Edit）：每次写/改文件后触发 `track-artifacts.sh`，自动记录 `git status --short`。
- **重构 haness SKILL.md**：将 artifact discovery 从 3-tier 升级为 4-tier：
  1. Auto-tracked session log（由 hook 维护，最可靠）
  2. Git direct diff（兜底）
  3. Git HEAD comparison（深兜底）
  4. 用户确认（强制最终步骤）
- **明确当前机制限制**：自动追踪仅对 git 仓库内文件有效；非 git 项目或仓库外文件（如 `~/.claude/settings.json`）需人工补充。
- **增加用户确认作为强制步骤**：即使自动化捕获了文件清单，也必须展示给用户确认，避免盲区。

## TODO / Next Steps

- [ ] 观察新机制在实际项目（如 coding/、research/）中的准确度，收集反馈
- [ ] 考虑为非 git 项目设计 fallback 方案（如基于时间戳的扫描 + 人工过滤）
- [ ] 评估是否需要把 `~/.claude/` 全局配置也纳入某种追踪范围（当前完全依赖人工）
- [ ] 测试 SessionStart hook 在 Claude Code 重启时是否正常触发

## Artifact Inventory

| File | Action | Description |
|------|--------|-------------|
| `~/.claude/settings.json` | Modified | 新增 `SessionStart` 和 `PostToolUse` hooks |
| `~/.claude/skills/haness/SKILL.md` | Modified | 重构 Phase 2 artifact discovery 为 4-tier fallback |
| `~/.claude/hooks/track-artifacts.sh` | Created | 自动追踪 `git status` 变更的 shell 脚本 |

## New Session Prompt

我们在优化 Claude Code 的 haness 对话快照机制，解决"记不准产物"的问题。本次已完成的工作包括：

1. 在 `~/.claude/settings.json` 中配置了两个 hook：
   - `SessionStart`：新会话开始时自动清理 `~/.claude/haness/session-artifacts.log`
   - `PostToolUse`（Write|Edit）：每次写/改文件后自动触发追踪脚本，记录 git status

2. 创建了 `~/.claude/hooks/track-artifacts.sh`，自动捕获 git 仓库内的文件变更并写入 log

3. 重构了 `~/.claude/skills/haness/SKILL.md`：
   - 废弃不可靠的 "AI 内心记账"
   - 新 Tier 1 为自动维护的 `session-artifacts.log`
   - 新增 Tier 4 "用户确认" 作为强制最终步骤

**当前已知限制**：
- 自动追踪只对 git 仓库内的文件有效
- `~/.claude/` 下的全局配置（如 `settings.json` 本身）不在 git 追踪范围内，haness 时仍需人工补充
- 同一文件多次修改会在 log 中重复出现（haness 时需去重）

请回顾上述改动，确认是否有遗漏或需要调整的地方。然后等待我的下一步指示。
