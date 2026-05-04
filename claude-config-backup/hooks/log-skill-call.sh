#!/bin/bash
# log-skill-call.sh — PostToolUse(Skill) hook
# 把 plan 相关 skill 的调用记录到 ~/.claude/logs/plan-skill-calls.log
# 供 plan-trigger.sh 验证 AI 是否真的调用了 code-plan-guard / planning-with-files

LOG_FILE="$HOME/.claude/logs/plan-skill-calls.log"
mkdir -p "$(dirname "$LOG_FILE")"

input=$(cat)

# stdin 是 PostToolUse 的 JSON,字段含 tool_input.skill (来自 Skill 工具的参数)
skill_name=$(echo "$input" | jq -r '.tool_input.skill // empty' 2>/dev/null)
ts=$(date +'%Y-%m-%d %H:%M:%S')

# 只记录关键 plan skills,其它 skill 忽略避免日志污染
case "$skill_name" in
  code-plan-guard|planning-with-files)
    echo "[$ts] $skill_name" >> "$LOG_FILE"
    ;;
esac

exit 0
