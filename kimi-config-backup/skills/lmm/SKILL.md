---
name: lmm
description: 手动触发脑卒中康复纵向数据 LMM 快速分析（目标达成检查、基线检验、均值标准差）。
type: command
commands:
  - name: lmm
    description: 快速 LMM/CLMM 分析（目标达成检查、基线检验、均值标准差，stdout 输出）
    arguments:
      - name: file
        description: 数据文件路径 (.xlsx 或 .csv)，支持绝对路径或相对路径
        required: true
---

# LMM 分析 Skill

## /lmm — 快速分析（目标达成检查）

用户通过 `/lmm <数据文件路径>` 调用本命令时，执行以下操作：

1. 读取用户提供的数据文件路径
2. 执行快速分析脚本：
   ```bash
   Rscript /Users/leyixu/Ai\ cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts/analyze_lmm.R "<文件路径>" --no-excel
   ```
3. 将脚本的 stdout（目标达成总表、均值标准差、基线 P值）直接展示给用户
4. **快速分析完成后，询问用户**：是否需要投稿级分析？使用 Holm-Bonferroni 还是 Bonferroni 校正？

## 投稿级分析（可选后续步骤）

如果用户选择进行投稿级分析，执行投稿级分析脚本：

```bash
Rscript /Users/leyixu/Ai\ cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts/analyze_rct_manuscript.R "<文件路径>" [输出目录] [--adjust=holm|bonferroni]
```

- 默认输出目录为 `output/`
- 默认多重比较校正为 `holm`
- 支持切换为 `bonferroni`

### 输出文件（13 个）

| 文件名 | 内容 |
|--------|------|
| `baseline_table.csv` | 基线描述统计 |
| `descriptive_all.csv` | 所有时点所有组描述统计 |
| `missingness_table.csv` | 缺失数据汇总 |
| `primary_result_fma_t2_g1_vs_g2.csv` | 主要结局（FMA_LE T2 G1 vs G2） |
| `primary_model_anova.csv` | 主要结局模型 ANOVA |
| `primary_emmeans_all_times.csv` | 主要结局边际均值 |
| `primary_pairwise_postbaseline.csv` | 主要结局事后比较 |
| `secondary_omnibus.csv` | 次要结局 omnibus 检验 |
| `secondary_pairwise_postbaseline.csv` | 次要结局事后比较 |
| `model_diagnostics.csv` | 模型诊断（AIC/BIC/奇异拟合/残差） |
| `statistical_methods_for_manuscript.txt` | 自动生成的方法学文本 |
| `analysis_report.md` | 分析报告摘要 |
| `sessionInfo.txt` | R 会话信息 |

### 技术特性

- **ANCOVA 结构**：基线值作为协变量
- **随机斜率尝试**：先拟合 `(1 + time_num | ID)`，奇异或失败时自动回退为 `(1 | ID)`
- **多重比较校正**：Holm-Bonferroni 或经典 Bonferroni
- **CLMM 等级模型**：MAS 使用累积链接混合模型，LRT 进行 omnibus 检验

---

## 依赖安装

如果脚本返回错误或依赖缺失，提示用户在 R 中安装：
```r
install.packages(c('readxl','dplyr','tidyr','nlme','emmeans','ordinal'))
```