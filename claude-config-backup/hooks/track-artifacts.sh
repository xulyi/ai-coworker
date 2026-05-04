#!/bin/bash
# track-artifacts.sh — 自动追踪会话中的文件变更
# 由 PostToolUse hook (Write|Edit) 触发

# 找到项目根目录（向上查找 .git）
DIR="$PWD"
ROOT=""
while [ "$DIR" != "/" ]; do
  if [ -d "$DIR/.git" ]; then
    ROOT="$DIR"
    break
  fi
  # 如果没有 .git，找 CLAUDE.md 作为项目根标记
  if [ -f "$DIR/CLAUDE.md" ]; then
    ROOT="$DIR"
    # 继续向上找，优先 .git
  fi
  DIR=$(dirname "$DIR")
done

# 如果没有找到项目根，使用当前目录
if [ -z "$ROOT" ]; then
  ROOT="$PWD"
fi

# 创建 haness 目录
mkdir -p "$ROOT/.claude/haness"

LOG_FILE="$ROOT/.claude/haness/session-artifacts.log"
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S)

# 如果有 git，记录 git status
if [ -d "$ROOT/.git" ]; then
  cd "$ROOT"
  # 只记录有变更的文件（新增、修改、删除）
  CHANGES=$(git status --short)
  if [ -n "$CHANGES" ]; then
    echo "[$TIMESTAMP] git-changes" >> "$LOG_FILE"
    # 过滤掉 haness 自身产生的文件，避免循环记录
    FILTERED=$(echo "$CHANGES" | grep -v "\.claude/haness/session-artifacts\.log" | grep -v "\.claude/haness/.*\.md$" | grep -v "\.claude/haness/artifacts/")
    if [ -n "$FILTERED" ]; then
      echo "$FILTERED" >> "$LOG_FILE"
      echo "" >> "$LOG_FILE"
    fi
  fi
fi
