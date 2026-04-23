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
  resources:
    - path: /Users/leyixu/Ai cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts/analyze_lmm.R
      role: LMM 分析与格式化输出核心脚本（R 版本，连续变量用 LMM，等级变量 MAS 用 CLMM）
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

---

## 工作流程（极简版）

> 核心原则：**不要手写分析代码，直接调用脚本**。脚本已经包含了所有分析逻辑和格式化输出。

### 第一步：确认数据文件

- 如果用户提供了文件路径，直接使用。
- 如果用户没有提供，检查当前工作目录下是否有 `.csv` 或 `.xlsx` 文件，询问用户确认。

### 第二步：直接调用脚本

```bash
cd /Users/leyixu/Ai\ cowork/coding/.claude/skills/lmm-stroke-analyzer/scripts
Rscript analyze_lmm.R <数据文件路径> --no-excel
```

**依赖检查**（首次使用时）：
```bash
Rscript -e "library(readxl); library(dplyr); library(tidyr); library(lme4); library(lmerTest); library(emmeans); library(geepack); library(openxlsx); cat('OK\n')" 2>/dev/null || echo "请在 R 中安装缺失包：install.packages(c('readxl','dplyr','tidyr','lme4','lmerTest','emmeans','geepack','openxlsx'))"
```

### 第三步：直接展示脚本输出

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

### 第四步：异常情况处理

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

用户修改数据保存后，回到**第二步**重新调用脚本。

---

## 内部指引（给 AI）

- **绝不**在对话中手写分析代码或重新实现 LMM 逻辑。所有分析由 `analyze_lmm.R` 脚本完成。
- **绝不**在输出中附加多余的总结段落。脚本输出的 Markdown 表格已经足够清晰。
- 如果用户说"太慢"，确认是否是因为脚本首次运行需要安装依赖，后续调用会快很多。
- 如果用户提供了新文件，直接执行 `Rscript analyze_lmm.R <新文件>`，不要询问确认。
