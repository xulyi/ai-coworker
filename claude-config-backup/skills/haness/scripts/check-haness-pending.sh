#!/usr/bin/env bash
# Stop hook: remind user to generate haness if session has unrecorded changes
# Always exits 0 — informational only

LOG_FILE=".claude/haness/session-artifacts.log"
HANESS_DIR=".claude/haness"

if [ ! -f "$LOG_FILE" ] || [ ! -s "$LOG_FILE" ]; then
    exit 0
fi

# Check if haness was generated in the last 60 minutes
RECENT_HANESS=$(find "$HANESS_DIR" -maxdepth 1 -type f -name "*.md" -mmin -60 2>/dev/null | grep -v "session-artifacts" | head -1)

if [ -z "$RECENT_HANESS" ]; then
    echo ""
    echo "[haness] 本次会话产生了文件变更，但尚未生成 haness 快照。"
    echo "[haness] 如需保存对话上下文，请输入: haness"
    echo ""
fi

exit 0
