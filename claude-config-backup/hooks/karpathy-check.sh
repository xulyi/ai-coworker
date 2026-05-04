#!/bin/bash

# 如果在 coding 目录或其子目录，跳过（coding/CLAUDE.md 已包含 karpathy 原则）
CWD=$(pwd)
if [[ "$CWD" == *"/coding"* ]] || [[ "$CWD" == *"/coding/"* ]]; then
    echo '{"continue":true}'
    exit 0
fi

# 否则注入原则（仅在非 coding 目录写代码时生效）
cat <<'JSON'
{"systemMessage":"🛡️ Karpathy Check — 写代码前回顾原则","hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"KARPATHY CODING PRINCIPLES — Verify before writing:\n1. STATE assumptions explicitly. Ask when unclear. Never guess.\n2. MINIMUM code. No speculative features or premature abstractions.\n3. SURGICAL changes only. Don't touch unrelated code or style.\n4. VERIFY first. Define success criteria. Test before declaring done."}}
JSON
