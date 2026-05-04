#!/bin/bash
# Karpathy Check — 写代码前回顾原则 (Kimi CLI 适配版)
# 事件: PreToolUse
# 说明: Kimi CLI 不支持通过 hook 注入 system message，此脚本输出提示到 stdout

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // empty')

# 只在写代码相关的工具调用时提示
case "$tool_name" in
  WriteFile|StrReplaceFile)
    echo "🛡️ Karpathy Check — 写代码前回顾原则:"
    echo "1. STATE assumptions explicitly. Ask when unclear. Never guess."
    echo "2. MINIMUM code. No speculative features or premature abstractions."
    echo "3. SURGICAL changes only. Don't touch unrelated code or style."
    echo "4. VERIFY first. Define success criteria. Test before declaring done."
    ;;
esac

exit 0
