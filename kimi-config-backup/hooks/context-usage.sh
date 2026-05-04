#!/bin/bash
# 显示当前对话上下文 token 使用率 (Kimi CLI 适配版)
# 说明: Kimi CLI 不提供 transcript_path 和 settings.json 中的 autoCompactWindow。
# 此版本基于可用信息做简化估算，主要用于状态展示。

input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id // empty')

# Kimi CLI 不暴露 transcript 路径和 token 使用细节，做简化提示
echo "📊 Kimi CLI 上下文统计 (session: ${session_id:0:8}...)"
echo "提示: 使用 /compact 手动压缩上下文，或开启自动压缩以保持流畅。"
