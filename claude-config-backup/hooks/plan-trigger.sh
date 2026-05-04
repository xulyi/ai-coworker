#!/bin/bash
# Plan Trigger — UserPromptSubmit hook
# 检测多步任务关键词(中文+英文),命令 AI 显式调用 code-plan-guard 和 planning-with-files
# 并要求 AI 在回答顶部展示 Skill 调用日志,缺失则返工(反馈循环)
# 详细规则参考 ~/.claude/CLAUDE.md 完整模式

input=$(cat)
prompt=$(echo "$input" | jq -r '.prompt // empty')

# 太短的 prompt 跳过(简单问答/确认/继续) — 中文环境下 bash 按字符计长度
if [ ${#prompt} -lt 6 ]; then
  exit 0
fi

# 多步任务关键词(中文+英文,简单调试/查询不触发)
# 中文 substring 匹配;英文 plan 用词边界,避免 explain/airplane/replant 误命中
KEYWORDS_CN='分析|建模|清洗|模拟|设计|重构|开发|架构|方案|规划|搭建|改造|生成数据|训练数据|创建系统|做.{0,4}流程|做.{0,4}计划|绩效|项目|实施|路线图'
KEYWORDS_EN='(^|[^a-zA-Z_])plan([^a-zA-Z_]|$)'

if echo "$prompt" | grep -qiE "$KEYWORDS_CN" || echo "$prompt" | grep -qiE "$KEYWORDS_EN"; then
  cat <<'JSON'
{"systemMessage":"📋 Plan Trigger 命中(含日志验证返工)","hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"检测到 plan 关键词。请严格按以下顺序执行,任何步骤不可省略:\n\n【调用阶段】\n1. 立即用 Skill 工具调用 code-plan-guard\n2. 接着用 Skill 工具调用 planning-with-files\n\n【验证阶段 — 必须做】\n3. 用 Bash 工具运行: tail -10 ~/.claude/logs/plan-skill-calls.log\n4. 在给用户的回答最顶部(对话第一页)插入以下结构:\n## ✅ Skill 调用验证日志\n```\n<上一步读到的日志内容>\n```\n\n【返工条件】\n5. 检查日志末尾 10 行内是否同时包含今日近 60 秒内的 code-plan-guard 和 planning-with-files 各至少一条记录\n6. 如果任何一个缺失 → 立即返工:重新用 Skill 工具调用缺失的 skill,再次 tail 日志,再次展示\n7. 直到两个 skill 都有今日最近的调用记录\n\n【正式响应】\n8. 验证通过后,日志展示永远放在回答最顶部,然后才能开始处理用户的实际请求\n9. 不要假设 hooks 会自动接管,所有 skill 调用必须显式 invoke 并通过日志验证"}}
JSON
fi
exit 0
