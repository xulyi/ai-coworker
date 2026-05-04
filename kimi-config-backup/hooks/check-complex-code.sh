#!/bin/bash
# Code Plan Guard - 复杂代码任务检测脚本 (Kimi CLI 适配版)
# 事件: UserPromptSubmit
# 输入: stdin JSON {prompt, session_id, cwd, hook_event_name}

input=$(cat)
prompt=$(echo "$input" | jq -r '.prompt // empty')

COMPLEX_PATTERNS="重构|架构|设计.实现|模块|系统|复杂|多文件|改写|优化.*代码|添加.*功能|新特性|重写|迁移|升级.*版本|拆分|合并.*模块|从零|新建.*项目|实现.*接口|改.*表结构|数据库.*变更|API.*变更"
SIMPLE_PATTERNS="解释|说明|为什么|查看|读一下|查.*bug|修.*一行|加.*日志|改.*配置|格式化|翻译|总结|对比"

# 如果 prompt 不存在，直接退出
if [ -z "$prompt" ]; then
  exit 0
fi

# 如果明确是简单任务，跳过
if echo "$prompt" | grep -qiE "$SIMPLE_PATTERNS"; then
  exit 0
fi

# 如果是复杂任务，输出激活标记
if echo "$prompt" | grep -qiE "$COMPLEX_PATTERNS"; then
  echo "🔒 [CODE-PLAN-GUARD] 检测到复杂代码任务。请严格执行：制定计划 → 用户确认 → 分步执行。"
  echo ""
  echo "复杂任务判定依据：用户输入匹配以下模式之一："
  echo "- 重构/架构/设计/模块/系统"
  echo "- 多文件/改写/重写/迁移"
  echo "- 添加功能/新特性/升级版本"
  echo "- 数据库变更/API变更"
fi
