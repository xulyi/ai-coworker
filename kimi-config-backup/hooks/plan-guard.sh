#!/bin/bash
# Code Plan Guard — 写代码前确认计划 (Kimi CLI 适配版)
# 事件: PreToolUse
# 说明: Kimi CLI 不支持通过 hook 注入 system message，此脚本输出提示到 stdout

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // empty')

# 只在写代码相关的工具调用时提示
case "$tool_name" in
  WriteFile|StrReplaceFile)
    echo "🔒 Plan Guard — 写代码前确认计划:"
    echo "1. CHECK: 是否已有结构化计划(目标/范围/步骤/风险/回滚/验证)并经过用户确认?"
    echo "2. IF NO: 先输出计划，使用 AskUserQuestion 获取确认"
    echo "3. IF YES: 严格按照确认的计划执行最小化修改"
    ;;
esac

exit 0
