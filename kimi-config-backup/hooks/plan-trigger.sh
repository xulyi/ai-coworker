#!/bin/bash
# Plan Trigger — UserPromptSubmit hook (Kimi CLI 适配版)
# 检测多步任务关键词(中文+英文)，输出提示建议调用相关 skills

input=$(cat)
prompt=$(echo "$input" | jq -r '.prompt // empty')

# 太短的 prompt 跳过(简单问答/确认/继续)
if [ ${#prompt} -lt 6 ]; then
  exit 0
fi

# 多步任务关键词(中文+英文，简单调试/查询不触发)
KEYWORDS_CN='分析|建模|清洗|模拟|设计|重构|开发|架构|方案|规划|搭建|改造|生成数据|训练数据|创建系统|做.{0,4}流程|做.{0,4}计划|绩效|项目|实施|路线图'
KEYWORDS_EN='(^|[^a-zA-Z_])plan([^a-zA-Z_]|$)'

if echo "$prompt" | grep -qiE "$KEYWORDS_CN" || echo "$prompt" | grep -qiE "$KEYWORDS_EN"; then
  echo "📋 Plan Trigger 命中。检测到 plan 关键词。建议按以下顺序执行："
  echo "1. 调用 Skill code-plan-guard"
  echo "2. 调用 Skill planning-with-files"
  echo "3. 验证日志记录后再正式响应"
fi
exit 0
