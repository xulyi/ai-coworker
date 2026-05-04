#!/usr/bin/env bash
# Stop hook: verify task_plan.md is being updated when file changes occur
# Always exits 0 — informational only

LOG_FILE=".claude/haness/session-artifacts.log"
PLAN_FILE="task_plan.md"

# No plan file = nothing to check
if [ ! -f "$PLAN_FILE" ]; then
    exit 0
fi

# No file changes this session = nothing to check
if [ ! -f "$LOG_FILE" ] || [ ! -s "$LOG_FILE" ]; then
    exit 0
fi

# Check if any checkbox is checked in task_plan.md
CHECKED=$(grep -c "\[x\]" "$PLAN_FILE" || true)
# Check if any phase is complete
COMPLETE=$(grep -cF "**Status:** complete" "$PLAN_FILE" || true)

# If there are file changes but no progress recorded in task_plan.md
if [ "$CHECKED" -eq 0 ] && [ "$COMPLETE" -eq 0 ]; then
    echo ""
    echo "[code-plan-guard] 检测到本次会话有文件变更，但 task_plan.md 中没有任何进展记录。"
    echo "[code-plan-guard] 请检查 plan 文件的 phase status 和 checkbox 是否需要手动更新。"
    echo ""
fi

exit 0
