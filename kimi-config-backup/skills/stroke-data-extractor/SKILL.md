---
name: stroke-data-extractor
description: |
  脑卒中论文数据提取技能。当用户提到"脑卒中论文数据"、"病案数据提取"、
  "提取病历数据"、"处理病案文件"、"脑卒中数据分析"或类似需求时立即启用。
  
  本技能用于从Markdown格式的病案记录中提取结构化数据，支持脑卒中相关
  诊断筛选、Brunnstrom分期、Ashworth评分、ADL评分等康复评估指标的提取。
  
  使用Python脚本进行初步提取，通过AI语义理解补全缺失内容。
---

# 脑卒中论文数据提取流程

## 概述

本技能实现从病案Markdown文件中提取结构化数据的完整流程，包括：
1. Python脚本自动提取（规则匹配）
2. AI语义理解补全（处理格式变体）
3. 生成CSV和JSON格式的最终报告

## 核心脚本位置

**主提取脚本**: `~/.claude/skills/stroke-data-extractor/scripts/extract_medical_records.py`

（兼容旧路径：`/Users/leyixu/extract_medical_records.py`）

此脚本包含完整的病案数据提取逻辑，包括：
- `MedicalRecord` 数据类定义
- `MedicalRecordParser` 解析器类
- 正则表达式模式匹配
- 批量处理功能

## 工作流程

### 第一步：运行Python提取脚本

使用主脚本处理病案文件目录：

```bash
python3 /Users/leyixu/extract_medical_records.py \
  --dir "/path/to/medical/records" \
  --csv "/output/path/extract_result.csv" \
  --json "/output/path/extract_result.json"
```

**支持的提取字段**:
- 基本信息：病案号、姓名、性别、年龄、入院次数
- 病程信息：病程天数（自动转换月/年为天）
- 专科检查：
  - Brunnstrom运动功能分期（上肢/手/下肢）
  - 改良Ashworth肌痉挛评分
  - ADL评分
  - 坐位/站位平衡
- 诊断信息：脑卒中相关诊断、所有诊断
- 评估记录：评估时间、项目、分数

**支持的格式变体**:
- Brunnstrom: `5期/5期/5期`、`II期/I期/V期`、`Ⅳ期/Ⅲ期`、`欠配合`、`NT期`
- Ashworth: `0级/1级`、`欠配合`、`降低`、`NT级`
- ADL: `ADL评定50分`、`ADL 50分`
- 平衡: `坐位平衡3级`、`坐站位平衡欠配合`

### 第二步：AI语义理解补全

由于病案格式存在大量变体，脚本提取后会有部分字段缺失。使用AI语义理解对原始文件进行深度分析，补全缺失内容。

**补全策略**:
1. 读取原始Markdown文件内容
2. 使用正则表达式捕获变体格式
3. 识别语义等价表达（如"欠配合"=无法评估）
4. 更新JSON/CSV数据

**关键补全代码模式**:

```python
import re
import json

# 读取提取结果
with open('extract_result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 对每条记录进行补全
for record in data:
    if not record.get('Brunnstrom_上肢'):
        # 读取原始文件
        with open(record['源文件'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 语义理解补全Brunnstrom
        # 支持："Brunnstrom:欠配合"、"分期:NT"等变体
        patterns = [
            r'Brunnstrom运动功能分期[:：]\s*(欠配合|NT|TN)',
            r'Brunnstrom[:：]\s*(右上肢|左上肢|上肢)\s*([ⅠⅡⅢⅣⅤⅥ\d]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                record['Brunnstrom_上肢'] = match.group(1)
                record['Brunnstrom_手'] = match.group(1)
                record['Brunnstrom_下肢'] = match.group(1)
                break
    
    # 补全Ashworth（处理"Ashworth肌张力评定"等变体）
    if not record.get('改良Ashworth_上肢'):
        ashworth_patterns = [
            r'[Aa]shworth肌(?:张力|痉挛)评定[：:]\s*上肢[:：]?\s*(欠配合|下降|降低|NT|[\d\+]+)',
            r'[Aa]shworth肌(?:张力|痉挛)评定[：:]\s*(欠配合)',
        ]
        for pattern in ashworth_patterns:
            match = re.search(pattern, content)
            if match:
                val = match.group(1)
                if val in ['欠配合', '下降', '降低', 'NT']:
                    record['改良Ashworth_上肢'] = val
                    record['改良Ashworth_下肢'] = val
                else:
                    record['改良Ashworth_上肢'] = val + '级'
                    # 查找下肢
                    leg_match = re.search(r'下肢[:：]?\s*(欠配合|下降|降低|NT|[\d\+]+)\s*级?', content)
                    if leg_match:
                        record['改良Ashworth_下肢'] = leg_match.group(1) + '级'
                break

# 保存补全后的结果
with open('extract_result_filled.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### 第三步：生成统计报告

生成包含完整度和统计信息的最终报告：

```python
import json

with open('extract_result_filled.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计信息
total = len(data)
fields = ['性别', '年龄', '病程天数', 'Brunnstrom_上肢', 
          '改良Ashworth_上肢', 'ADL评分', '坐位平衡', '站位平衡']

for field in fields:
    filled = sum(1 for r in data if r.get(field) and r.get(field) != 0 and r.get(field) != '')
    print(f"{field}: {filled}/{total} ({filled/total*100:.1f}%)")
```

## 输出文件格式

### CSV格式
- 编码：UTF-8 with BOM（支持Excel中文）
- 包含所有提取字段
- 评估记录以JSON字符串形式存储

### JSON格式
- 结构化数组
- 便于后续程序处理
- 保留原始行信息用于核对

## 注意事项

1. **数据质量**: 部分病案文件本身缺少某些评估项（如急诊记录无Brunnstrom），AI无法补全不存在的原始数据

2. **语义边界**: 以下情况标记为缺失而非猜测：
   - 原文写"欠配合"→标记"欠配合"（非空值）
   - 原文写"NT"→标记"NT"（非空值）
   - 原文完全未提及→保持空值

3. **验证建议**: 对关键研究数据，建议人工抽查10-20%的提取结果

## 依赖项

- Python 3.8+
- 标准库：`re`, `json`, `csv`, `os`, `pathlib`, `dataclasses`
- 无需第三方库

## 触发条件

当用户提及以下任何内容时立即启用：
- "脑卒中论文数据"
- "病案数据提取"
- "提取病历数据"
- "处理病案文件"
- "脑卒中数据分析"
- "病历信息提取"
- "康复评估数据提取"
- "Brunnstrom/Ashworth/ADL提取"
