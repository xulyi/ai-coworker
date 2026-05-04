#!/bin/bash
# plan-stop-verify.sh — Stop hook，plan skill 调用兜底验证 (Kimi CLI 适配版)
#
# 说明: Kimi CLI 的 Stop 事件不提供 transcript_path，此版本降级为检查日志文件。
# 如果日志中近期无记录，输出警告但不 block（fail-open）。

LOG_FILE="${PLAN_SKILL_LOG:-$HOME/.kimi/logs/plan-skill-calls.log}"

input=$(cat)
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active // false')

# 如果 stop hook 未激活，静默放行
if [ "$stop_hook_active" != "true" ]; then
  exit 0
fi

# 找不到日志文件 → 降级放行
if [ ! -f "$LOG_FILE" ]; then
  echo "⚠️ plan-skill-calls.log 不存在，无法验证 skill 调用" >&2
  exit 0
fi

cutoff=$(date -v-60S +'%Y-%m-%d %H:%M:%S')
# 时间戳格式 [YYYY-MM-DD HH:MM:SS] 字典序 = 时间序，awk 比较即可
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
  echo "⚠️ plan 任务建议调用 Skill code-plan-guard 和 planning-with-files。日志显示最近 60 秒内缺少: ${missing_str}" >&2
  # 注意: Kimi CLI 中不 block，仅输出警告
fi

exit 0
