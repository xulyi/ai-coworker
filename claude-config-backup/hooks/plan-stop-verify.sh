#!/bin/bash
# plan-stop-verify.sh — Stop hook,代码侧 plan skill 调用兜底验证
#
# 流程:
# 1. 从 transcript_path 读最后一条 type=user 且 content 是字符串的消息
# 2. 跑 plan 关键词检测(与 plan-trigger.sh 保持一致)
# 3. 命中关键词 → 查日志 60 秒窗口,检查 code-plan-guard 和 planning-with-files 是否都有调用
# 4. 缺哪个 → 输出 {"decision":"block","reason":"..."} 要求 AI 重调
# 5. 齐了或不命中 → exit 0 静默放行
#
# 详细原理见 ~/.claude/skills/code-plan-guard/PLAN-FEEDBACK-LOOP.md

LOG_FILE="${PLAN_SKILL_LOG:-$HOME/.claude/logs/plan-skill-calls.log}"

input=$(cat)
transcript_path=$(echo "$input" | jq -r '.transcript_path // empty' 2>/dev/null)

# 找不到 transcript → 降级放行(避免误 block)
if [ -z "$transcript_path" ] || [ ! -f "$transcript_path" ]; then
  exit 0
fi

# 取最后一条 type=user 且 content 是字符串的消息(排除 tool_result 这种 array content)
last_user_prompt=$(jq -r 'select(.type=="user" and (.message.content | type) == "string") | .message.content' "$transcript_path" 2>/dev/null | tail -1)

if [ -z "$last_user_prompt" ]; then
  exit 0
fi

# 关键词检测(必须与 ~/.claude/hooks/plan-trigger.sh 保持同步,改一处需同步另一处)
KEYWORDS_CN='分析|建模|清洗|模拟|设计|重构|开发|架构|方案|规划|搭建|改造|生成数据|训练数据|创建系统|做.{0,4}流程|做.{0,4}计划|绩效|项目|实施|路线图'
KEYWORDS_EN='(^|[^a-zA-Z])plan([^a-zA-Z]|$)'

if ! echo "$last_user_prompt" | grep -qiE "$KEYWORDS_CN" && ! echo "$last_user_prompt" | grep -qiE "$KEYWORDS_EN"; then
  # 非 plan 任务,放行
  exit 0
fi

# 命中关键词 → 验证日志
if [ ! -f "$LOG_FILE" ]; then
  jq -n '{decision:"block", reason:"plan 任务必须调用 Skill code-plan-guard 和 Skill planning-with-files,但日志文件不存在。请用 Skill 工具调用这两个 skill 后再结束响应。"}'
  exit 0
fi

cutoff=$(date -v-60S +'%Y-%m-%d %H:%M:%S')
# 时间戳格式 [YYYY-MM-DD HH:MM:SS] 字典序 = 时间序,awk 比较即可
recent=$(awk -v c="[$cutoff]" '$0 >= c' "$LOG_FILE")

has_guard=0
has_files=0
[ -n "$recent" ] && echo "$recent" | grep -q 'code-plan-guard' && has_guard=1
[ -n "$recent" ] && echo "$recent" | grep -q 'planning-with-files' && has_files=1

missing=()
[ "$has_guard" -eq 0 ] && missing+=("code-plan-guard")
[ "$has_files" -eq 0 ] && missing+=("planning-with-files")

if [ ${#missing[@]} -gt 0 ]; then
  missing_str=$(printf '%s, ' "${missing[@]}")
  missing_str="${missing_str%, }"
  reason="plan 任务必须调用 Skill code-plan-guard 和 Skill planning-with-files。日志显示最近 60 秒内缺少: ${missing_str}。请用 Skill 工具调用缺失的 skill 后再结束响应。"
  jq -n --arg r "$reason" '{decision:"block", reason:$r}'
  exit 0
fi

# 两个 skill 60 秒内都有,静默放行
exit 0
