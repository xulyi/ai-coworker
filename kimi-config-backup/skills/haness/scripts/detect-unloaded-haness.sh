#!/usr/bin/env bash
# UserPromptSubmit hook: detect recent haness files that haven't been loaded
# Always exits 0 — informational only

HANESS_DIR=".claude/haness"

if [ ! -d "$HANESS_DIR" ]; then
    exit 0
fi

# Find latest haness file (excluding session-artifacts and hidden files)
LATEST=$(find "$HANESS_DIR" -maxdepth 1 -type f -name "*.md" ! -name "session-artifacts*" ! -name ".*" -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
    exit 0
fi

# Check if haness is newer than 24 hours (cross-platform stat)
if stat --version >/dev/null 2>&1; then
    MTIME=$(stat -c %Y "$LATEST")
else
    MTIME=$(stat -f %m "$LATEST")
fi

NOW=$(date +%s)
AGE_HOURS=$(( (NOW - MTIME) / 3600 ))

if [ "$AGE_HOURS" -ge 24 ]; then
    exit 0
fi

FILENAME=$(basename "$LATEST")

echo ""
echo "[haness] 检测到近 24 小时内生成的 haness 快照: $FILENAME"
echo "[haness] 如需恢复上下文，请说: 加载 haness $FILENAME"
echo ""

exit 0
