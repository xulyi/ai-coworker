#!/bin/bash

# Code Plan Guard — 提醒级
# 在 Write/Edit 工具调用前注入系统指令，要求 Claude 先检查计划状态

cat <<'JSON'
{"systemMessage":"🔒 Plan Guard — 写代码前确认计划","hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"CODE PLAN GUARD — Before writing or editing any file:\n1. CHECK: Has a structured plan (目标/范围/步骤/风险/回滚/验证) been presented and explicitly confirmed by the user in this conversation?\n2. IF NO: Cancel the current tool call. Output a plan using the 6-module template (目标/范围/步骤/风险/回滚/验证). Use AskUserQuestion to get confirmation.\n3. IF YES: Proceed with surgical, minimal changes strictly following the confirmed plan. Report progress after each step."}}
JSON
