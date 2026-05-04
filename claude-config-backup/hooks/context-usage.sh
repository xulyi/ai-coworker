#!/bin/bash
# 显示当前对话上下文 token 使用率，供 statusLine 调用
# 输入: stdin JSON（含 transcript_path）
# 输出: 一行 "🟢 142k/200k (71%)" 形式

INPUT=$(cat)
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty' 2>/dev/null)

# 动态读取 autoCompactWindow,作为状态栏分母
LIMIT=$(jq -r '.autoCompactWindow // 200000' ~/.claude/settings.json 2>/dev/null)
{ [ -z "$LIMIT" ] || [ "$LIMIT" = "null" ]; } && LIMIT=200000

# Claude Code 内部约在 autoCompactWindow * 85% 触发自动压缩
TRIGGER=$((LIMIT * 85 / 100))

if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  echo "📊 —"
  exit 0
fi

# 找最后一行包含 usage 的记录（最新一次 API 响应）
LAST=$(grep -F '"usage"' "$TRANSCRIPT" 2>/dev/null | tail -1)

if [ -z "$LAST" ]; then
  echo "📊 0k/$((LIMIT/1000))k"
  exit 0
fi

# 累加 input + cache_read + cache_creation = 当前对话总上下文
TOTAL=$(echo "$LAST" | jq -r '
  (.message.usage // .usage // {}) as $u
  | (($u.input_tokens // 0) + ($u.cache_read_input_tokens // 0) + ($u.cache_creation_input_tokens // 0))
' 2>/dev/null)

[ -z "$TOTAL" ] || [ "$TOTAL" = "null" ] && TOTAL=0

PERCENT=$((TOTAL * 100 / LIMIT))
TOKENS_K=$((TOTAL / 1000))
LIMIT_K=$((LIMIT / 1000))

if [ "$PERCENT" -ge 85 ]; then
  ICON="🔴"
elif [ "$PERCENT" -ge 65 ]; then
  ICON="🟡"
else
  ICON="🟢"
fi

# 提取本会话所有 Skill 工具调用的 skill 名,按调用顺序去重
SKILLS=$(grep -F '"name":"Skill"' "$TRANSCRIPT" 2>/dev/null \
  | jq -r '.message.content[]? | select(.type == "tool_use" and .name == "Skill") | .input.skill // empty' 2>/dev/null \
  | awk '!seen[$0]++')

SKILL_LINE=""
if [ -n "$SKILLS" ]; then
  COUNT=$(echo "$SKILLS" | wc -l | tr -d ' ')
  if [ "$COUNT" -le 6 ]; then
    SKILL_LIST=$(echo "$SKILLS" | paste -sd '→' -)
  else
    SHOWN=$(echo "$SKILLS" | head -6 | paste -sd '→' -)
    SKILL_LIST="${SHOWN}→+$((COUNT - 6))"
  fi
  SKILL_LINE=" | 🛠 ${SKILL_LIST}"
fi

echo "${ICON} ${TOKENS_K}k/${LIMIT_K}k (${PERCENT}%, 压缩@$((TRIGGER/1000))k)${SKILL_LINE}"
