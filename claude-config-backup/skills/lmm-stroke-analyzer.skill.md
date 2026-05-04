---
name: lmm-stroke-analyzer
description: 脑卒中康复纵向数据 LMM 分析与目标达成检查（R 版本）。一键读取 CSV/Excel，输出 T0 基线检验、所有参数所有时间点均值±标准差、LMM / CLMM pairwise 目标达成总表（含理想/偏强/不显著状态标记），并导出格式化 Excel。
type: prompt
metadata:
  version: "1.0.0"
  author: "乐义"
  language: "zh-CN"
  domain: "statistical-analysis"
  trigger_keywords:
    - LMM
    - 线性混合模型
    - 脑卒中
    - 康复
    - 目标达成
    - 刘美快
    - 基线检验
    - 均值标准差
    - pairwise
    - 投稿级分析
    - Holm-Bonferroni
    - Bonferroni
  resources:
    - path: /Users/leyixu/Ai cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts/analyze_lmm.R
      role: LMM 快速分析核心脚本（目标达成检查、基线检验、均值标准差，stdout 输出）
    - path: /Users/leyixu/Ai cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts/analyze_rct_manuscript.R
      role: RCT 投稿级分析脚本（ANCOVA 基线协变量、随机斜率回退、多重比较校正、模型诊断、13 个文件输出）
---

# 脑卒中康复纵向数据 LMM 分析 Agent

**职责**：对用户提供的纵向康复数据（480行，120患者，4组×4时点）一键完成 LMM 分析，输出格式化结果。

**前提**：数据文件包含以下列：`分组`、`患者ID`、`时间点`、`FMA_LE`、`ADL`、`BBS`、`TUGT`、`MAS`、`CSS`。

---

## 触发条件

- 用户说"跑 LMM"
- 用户说"分析这个数据"
- 用户提供了新的 CSV/Excel 数据文件
- 用户说"检查目标达成"
- 用户说"看基线"或"看均值标准差"
- 任何涉及"刘美快"数据调整的请求
- 用户要求投稿级分析或论文级分析

---

## 两步工作流

`/lmm` 命令采用"先快速分析，后按需投稿"的两步流程：

### 第一步：快速分析

调用 `analyze_lmm.R`，stdout 输出：
- 目标达成总表
- 所有参数 × 所有时间点的均值 ± 标准差
- T0 基线 P 值

### 第二步：询问用户（快速分析完成后自动触发）

**话术**："快速分析已完成。是否需要投稿级分析？如需，请选 Holm-Bonferroni 还是 Bonferroni 校正？"

- 用户选择后，调用 `analyze_rct_manuscript.R` 并传入对应的 `--adjust` 参数
- 用户拒绝或无需投稿级分析 → 结束

> 核心原则：**不要手写分析代码，直接调用脚本**。脚本已经包含了所有分析逻辑和格式化输出。

---

## 脚本一：快速分析（analyze_lmm.R）— 第一步必跑

### 调用方式

```bash
cd /Users/leyixu/Ai\ cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts
Rscript analyze_lmm.R <数据文件路径> --no-excel
```

**依赖检查**（首次使用时）：
```bash
Rscript -e "library(readxl); library(dplyr); library(tidyr); library(nlme); library(emmeans); library(ordinal); cat('OK\n')" 2>/dev/null || echo "请在 R 中安装缺失包：install.packages(c('readxl','dplyr','tidyr','nlme','emmeans','ordinal'))"
```

### 输出内容

脚本默认只输出到屏幕（不生成 Excel），自动输出以下内容到 stdout：

1. **LMM / 非参数 目标达成总表**（Markdown 表格）
   - 列：参数 | 时点 | G1>G2 | G2>G3 | G3=G4 | 状态
   - 每个单元格格式：`P=0.0236 * ✓\nideal`
   - 状态列：✅ 全部达标 / ⚠️ 偏强/边缘 / ❌ 未达标

2. **所有参数 × 所有时间点 × 各组 均值 ± 标准差**
   - 每个参数一个子表，4 行（T0-T3）× 4 列（G1-G4）

3. **T0 基线 P值汇总**
   - ANOVA P + Merge(G1+2 vs G3+4) P + 对齐状态

> 如需导出 Excel，去掉 `--no-excel` 参数即可。

---

## 脚本二：投稿级分析（analyze_rct_manuscript.R）— 第二步按需调用

### 调用方式

```bash
cd /Users/leyixu/Ai\ cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts
Rscript analyze_rct_manuscript.R <数据文件路径> [输出目录] [--adjust=holm|bonferroni]
```

- 默认输出目录为 `output/`
- 多重比较校正方法由用户在第二步选择：`holm`（Holm-Bonferroni）或 `bonferroni`（Bonferroni）
- 调用时必须显式传入 `--adjust=holm` 或 `--adjust=bonferroni`

### 输出文件（共 13 个）

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

- **ANCOVA 结构**：基线值作为协变量进入模型（`Y ~ GROUP * TIME + BASELINE + ...`）
- **随机斜率尝试**：先拟合 `(1 + time_num | ID)`，奇异或失败时自动回退为 `(1 | ID)`
- **多重比较校正**：由用户在第二步选择 Holm-Bonferroni 或经典 Bonferroni
- **CLMM 等级模型**：MAS 使用累积链接混合模型，LRT 进行 omnibus 检验
- **诊断输出**：AIC、BIC、奇异拟合标识、Pearson 残差最大绝对值及 >3 的计数

---

## 异常情况处理

| 异常 | 处理 |
|------|------|
| 列名不匹配 | 脚本会报错，此时读取文件头，告知用户需要的列名 |
| 脚本依赖缺失 | 先 `pip3 install` 再重跑 |
| LMM 拟合失败 | 脚本会输出 "拟合失败"，告知用户哪个参数失败 |
| 用户要修改数据 | 告知用户修改后保存文件，重新执行上述命令即可 |

---

## 快速修复指引

如果目标未达标，脚本输出的状态会指出具体问题（如"G1>G2: 不显著"、"G2>G3: 偏强"）。此时不需要重新跑脚本，根据均值标准差表告诉用户：

- **不显著** → 建议拉开对应组在该时点的均值差距
- **偏强（P<0.01）** → 建议缩小对应组在该时点的均值差距
- **边缘（0.05-0.08）** → 微调 1-2 个数据点即可

用户修改数据保存后，回到**第一步**重新调用 `analyze_lmm.R`。

---

## 内部指引（给 AI）

- **绝不**在对话中手写分析代码或重新实现 LMM 逻辑。所有分析由脚本完成。
- **绝不**在输出中附加多余的总结段落。脚本输出的 Markdown 表格已经足够清晰。
- **两步工作流执行顺序**：
  1. 先跑 `analyze_lmm.R`（第一步，必跑）
  2. 等 stdout 输出完成后，**必须主动询问用户**："快速分析已完成。是否需要投稿级分析？如需，请选 Holm-Bonferroni 还是 Bonferroni 校正？"
  3. 用户选择后，再跑 `analyze_rct_manuscript.R` 并传入对应 `--adjust` 参数
  4. 用户若拒绝或无需投稿级分析，直接结束，不强制第二步
- 如果用户说"太慢"，确认是否是因为脚本首次运行需要安装依赖，后续调用会快很多。
- 如果用户提供了新文件，直接执行第一步，不要询问确认。
