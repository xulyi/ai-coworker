# Three-Line Table Guide — 学术论文三线表完整规范与生成指南

> **本文件用途**：指导模型生成符合国内外学术期刊规范的三线表，覆盖基线特征、组间比较、重复测量、回归分析等全场景。
>
> **核心原则**：
> 1. 先判断变量类型和分布，再决定数据呈现方式
> 2. 效应量和 95% CI 必须纳入表格，不能只有 p 值
> 3. 表注是表格的组成部分，不能省略
> 4. 数值精度须全表统一，不得随意变换小数位数
> 5. 三线表中不允许出现竖线，辅助横线须有明确必要性
> 6. **统计符号必须斜体**：表格内和文字描述中，所有统计符号（t、p、F、Z、U、H、r 等）必须使用斜体

---

## 一、三线表结构规范

### 1.1 线条构成（铁律）

| 线条名称 | 位置 | 是否必须 | 线宽 | LaTeX 命令 |
|---|---|---|---|---|
| 顶线（Top Rule）| 表格最上方 | ✅ 必须 | **1.5 磅** | `\toprule` |
| 表头分隔线（Mid Rule）| 表头行下方 | ✅ 必须 | **0.5 磅** | `\midrule` |
| 底线（Bottom Rule）| 表格最下方 | ✅ 必须 | **1.5 磅** | `\bottomrule` |
| 辅助线（Cmidrule）| 分层表头、小计行 | ⚠️ 仅在必要时 | 0.5 磅 | `\cmidrule` |
| 竖线 | 任何位置 | ❌ 禁止 | — | — |
| 单元格边框 | 任何位置 | ❌ 禁止 | — | — |

> ⚠️ **Word 实现关键**：三线表必须是**三根黑线**——顶线 1.5 磅、中线 0.5 磅、底线 1.5 磅，其他边框全部移除。

### 1.2 表格标题规范

```
格式：表 [编号]  [内容描述]（[样本信息]）

✅ 正确示例：
  表 1  两组受试者基线特征比较（n = 60）
  表 2  干预前后各组主要结局指标比较
  表 3  步行速度的多元线性回归分析结果

❌ 错误示例：
  表1（标题太短，无实质内容）
  表 1  采用独立样本t检验和Mann-Whitney U检验对实验组和对照组进行比较的基线特征（标题过长）
  Figure 1（不能用Figure）
```

### 1.3 列标题规范

- 单位统一写在列标题括号内，**不得**重复写在每个单元格
- 分组列标题须注明各组 n（如：实验组（n=30））
- 统计量列须注明指标类型（如：*t* 值、*F* 值、*χ²*、*U* 值）— **统计符号必须斜体**
- 效应量列须注明指标（如：Cohen's d、*η²*、OR）
- p 值列标题写"*p*"或"*p* 值"，不写"显著性"或"Sig." — **p 必须斜体**

### 1.4 数值格式规范

| 数据类型 | 推荐精度 | 示例 |
|---|---|---|
| 均值（连续变量）| 保留小数位 = 原始测量精度 + 1 | 58.4（岁），23.14（kg/m²）|
| 标准差 | 与均值相同小数位 | ± 9.6 |
| 中位数 | 与原始数据相同精度 | 12 [9, 16] |
| 百分比 | 统一 1 位小数 | 60.0% |
| *t* / *F* / *Z* / *U* / *H* | 保留 2–3 位小数 | *t* = 2.34，*F* = 5.67 |
| 相关系数 *r* / *ρ* | 保留 3 位小数 | *r* = 0.456 |
| *p* 值 | 保留 3 位小数；< .001 时写 < .001 | *p* = .032，*p* < .001 |
| 效应量 *d* / *η²* / *r* | 保留 3 位小数 | *d* = 0.524 |
| OR / HR | 保留 2 位小数（大数值）或 3 位（< 1）| OR = 2.34，OR = 0.456 |
| 95% CI | 与对应统计量相同精度 | [1.23, 4.56] |

> ⚠️ **全表同一列必须使用相同小数位数**，若特殊行有不同精度，须在表注说明理由。

---

## 二、数据呈现方式决策树

```
变量类型判断
│
├── 连续变量
│   ├── 正态性检验（Shapiro-Wilk / KS）结果
│   │   ├── p > 0.05（近似正态）→ M ± SD
│   │   └── p < 0.05（偏态）→ M [Q1, Q3]
│   └── 特殊情况
│       ├── 等级量表（如 Likert 5分）→ 惯例视为连续，用 M ± SD，并在表注说明
│       └── 临床评分（如 NRS 0-10）→ 通常 M ± SD，偏态时 M [IQR]
│
├── 分类变量
│   ├── 二分类 → n (%)，说明分母
│   ├── 多分类（无序）→ 各类别分行 n (%)
│   └── 有序分类 → 各类别 n (%) 或中位数[IQR]（视研究惯例）
│
└── 特殊数据类型
    ├── 率（如发生率）→ n/N (%) 或 率/100人年
    ├── 时间（如生存时间）→ M [IQR] 或 中位数（95% CI）
    └── 计数（如复发次数）→ M [IQR] 或 负二项分布相关报告方式
```

---

## 三、八大常用三线表类型（完整模板）

### 3.1 基线特征比较表（Baseline Characteristics）

**适用场景**：RCT、队列研究的人口学和临床基线比较

```markdown
**表 1. 两组受试者基线特征比较（n = 60）**

| 变量 | 对照组（n=30） | 实验组（n=30） | 统计量 | *p* |
|:---|:---:|:---:|:---:|:---:|
| **连续变量（正态）** | | | | |
| 年龄（岁）| 58.4 ± 9.6 | 57.9 ± 8.8 | *t* = 0.21 | .832 |
| BMI（kg/m²）| 23.4 ± 3.2 | 24.1 ± 2.9 | *t* = 0.90 | .373 |
| 基线评分 | 42.3 ± 8.1 | 43.6 ± 7.8 | *t* = 0.64 | .525 |
| **连续变量（偏态）** | | | | |
| 病程（月）| 18 [12, 36] | 21 [14, 42] | *U* = 412 | .485 |
| **分类变量** | | | | |
| 性别（男）| 18 (60.0%) | 16 (53.3%) | *χ²* = 0.27 | .601 |
| 诊断类型 A | 12 (40.0%) | 14 (46.7%) | *χ²* = 0.27 | .601 |

注：连续变量符合正态分布时采用均值 ± 标准差（M ± SD）表示；分布偏态时采用中位数 [四分位数范围（IQR）] 表示；
分类变量采用 n（%）表示，百分比以各组总例数为分母。
组间差异：连续正态变量采用独立样本 *t* 检验，偏态变量采用 Mann-Whitney *U* 检验，分类变量采用 *χ²* 检验。
两组基线特征均衡，各项指标差异均无统计学意义（均 *p* > .05）。
```

### 3.2 主要结局比较表（含效应量，两组）

**适用场景**：RCT 主要结局、干预后两组对比

```markdown
**表 2. 两组受试者干预后主要结局指标比较**

| 指标 | 对照组（n=30）M±SD | 实验组（n=30）M±SD | 统计量 | *p* | Cohen's d [95% CI] |
|:---|:---:|:---:|:---:|:---:|:---:|
| 步行速度（m/s）| 0.82 ± 0.18 | 0.97 ± 0.21 | *t* = 2.96 | .004 | 0.76 [0.25, 1.27] |
| Berg 平衡量表（分）| 38.4 ± 7.6 | 44.2 ± 6.8 | *t* = 3.11 | .003 | 0.80 [0.29, 1.31] |
| FIM 运动（分）| 62.3 ± 11.4 | 70.8 ± 9.7 | *t* = 3.12 | .003 | 0.81 [0.29, 1.32] |
| 疼痛 NRS（分）† | 4 [3, 6] | 2 [1, 4] | *U* = 271 | .012 | *r* = 0.32 |

注：连续正态变量采用均值 ± 标准差（M ± SD）表示，组间比较采用独立样本 *t* 检验，效应量采用 Cohen's d（95% CI）；
†疼痛评分不满足正态性假设（Shapiro-Wilk *p* < .05），采用中位数 [IQR] 表示，组间比较采用 Mann-Whitney *U* 检验，效应量采用 *r* = |*Z*|/√N。
**p* < .01；所有检验均为双侧检验，α = .05。
```

### 3.3 前后比较表（配对设计 / 重复测量）

**适用场景**：单组前后对比、多时间点纵向追踪

```markdown
**表 3. 受试者干预前后主要指标变化（n = 30）**

| 指标 | 干预前（T0）| 干预后（T1）| 差值（T1-T0）| 统计量 | *p* | Cohen's d_z |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 步行速度（m/s）| 0.82 ± 0.18 | 0.97 ± 0.21 | 0.15 ± 0.12 | *t* = 6.84 | < .001 | 1.25 |
| Berg 评分（分）| 38.4 ± 7.6 | 44.2 ± 6.8 | 5.8 ± 4.3 | *t* = 7.39 | < .001 | 1.35 |
| FIM（分）| 62.3 ± 11.4 | 70.8 ± 9.7 | 8.5 ± 6.1 | *t* = 7.65 | < .001 | 1.39 |
| 疼痛 NRS（分）†| 4 [3, 6] | 2 [1, 4] | — | *Z* = -3.82 | < .001 | *r* = 0.70 |

注：连续变量采用均值 ± 标准差（M ± SD）表示；配对比较采用配对 *t* 检验，效应量采用 Cohen's d_z（= 差值均值 / 差值标准差）。
†不满足配对 *t* 检验前提，采用 Wilcoxon 符号秩检验，效应量采用 *r* = |*Z*|/√N。
所有检验为双侧检验，α = .05。
```

### 3.4 混合设计结果表（组别 × 时间）

**适用场景**：RCT 多时间点，含交互效应分析

```markdown
**表 4. 两组受试者步行速度（m/s）在不同时间点的比较（M ± SD）**

| 时间点 | 对照组（n=25）| 实验组（n=25）| 组间差异（Cohen's d [95% CI]）|
|:---|:---:|:---:|:---:|
| 基线（T0）| 0.82 ± 0.18 | 0.83 ± 0.19 | 0.05 [-0.51, 0.61] |
| 4 周（T1）| 0.88 ± 0.17 | 0.95 ± 0.20 | 0.38 [-0.18, 0.94] |
| 8 周（T2）| 0.91 ± 0.16 | 1.04 ± 0.18 | 0.76 [0.19, 1.33]* |

| 效应来源 | *F* | *p* | 偏 *η²* |
|:---|:---:|:---:|:---:|
| 时间主效应 | *F* = 18.42 | < .001 | .277 |
| 组别主效应 | *F* = 4.31 | .043 | .082 |
| 组别 × 时间交互 | *F* = 6.74 | .002 | .123 |

注：步行速度采用均值 ± 标准差（M ± SD）表示。分析采用 2（组别）× 3（时间）混合方差分析；
球形假设违反（Mauchly *W* = 0.87，*p* = .031），时间相关效应采用 Greenhouse-Geisser 校正（*ε* = 0.89）。
组间效应量采用 Cohen's d（95% CI）；方差分析效应量采用偏 *η²*（小 = .01，中 = .06，大 = .14）。
简单效应分析（Bonferroni 校正）显示，8 周时组间差异具有统计学意义（*p*_adj < .05）。
```

### 3.5 三组及以上比较表（含事后检验）

**适用场景**：三组或多组独立样本比较

```markdown
**表 5. 三组受试者康复结局指标比较（M ± SD）**

| 指标 | 对照组（n=20）| 低强度组（n=20）| 高强度组（n=20）| 统计量 | *p* | 效应量 | 事后比较 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 步速（m/s）| 0.82±0.18 | 0.93±0.20 | 1.05±0.22 | *F* = 9.43 | < .001 | *η²*=.249 | A<C*, A<B† |
| FIM（分）| 62±11 | 70±10 | 76±9 | *F* = 11.27 | < .001 | *η²*=.283 | A<B***, A<C*** |
| 疼痛 NRS† | 5[3,7] | 3[2,5] | 2[1,4] | *H* = 14.32 | < .001 | *η²_H*=.227 | A>B*, A>C** |

注：连续正态变量采用均值 ± 标准差（M ± SD），采用单因素方差分析（*F*），方差不齐时采用 Welch ANOVA。
†疼痛 NRS 不满足正态性假设，采用中位数 [IQR] 表示，组间比较采用 Kruskal-Wallis 检验（*H*）。
事后比较：方差分析后采用 Tukey HSD（方差齐）或 Games-Howell（方差不齐）；Kruskal-Wallis 后采用 Dunn 检验（Bonferroni 校正）。
A=对照组；B=低强度组；C=高强度组。†*p*_adj < .10；**p*_adj < .05；**p*_adj < .01；***p*_adj < .001。
效应量：*η²* 参照 Cohen（1988）标准：小 = .01，中 = .06，大 = .14。
```

### 3.6 相关分析矩阵表

**适用场景**：多变量相关性汇总

```markdown
**表 6. 主要变量间相关系数矩阵（n = 60）**

| 变量 | 1 | 2 | 3 | 4 | M ± SD |
|:---|:---:|:---:|:---:|:---:|:---:|
| 1. 步行速度（m/s）| — | | | | 0.92 ± 0.21 |
| 2. Berg 平衡量表（分）| .672*** | — | | | 41.3 ± 7.4 |
| 3. FIM 运动（分）| .584*** | .631*** | — | | 66.5 ± 10.8 |
| 4. 疼痛 NRS（分）| -.412** | -.356** | -.289* | — | 3.2 ± 2.1 |

注：采用 Pearson 相关（变量 1–3 正态分布）或 Spearman 秩相关（变量 4 偏态分布，以 *ρ* 表示）；
所有检验为双侧检验。
**p* < .05；**p* < .01；***p* < .001。
```

### 3.7 线性回归结果表

**适用场景**：多元线性回归、ANCOVA

```markdown
**表 7. 以步行速度为结局变量的多元线性回归分析（n = 60）**

| 变量 | *B* | SE | *β* | *t* | *p* | 95% CI |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 常数项 | 0.23 | 0.18 | — | 1.27 | .208 | [-0.14, 0.60] |
| 年龄（岁）| -0.008 | 0.003 | -.284 | -2.66 | .010 | [-0.014, -0.002] |
| BMI（kg/m²）| -0.012 | 0.007 | -.189 | -1.77 | .082 | [-0.026, 0.002] |
| Berg 评分（分）| 0.018 | 0.004 | .488 | 4.56 | < .001 | [0.010, 0.026] |
| 干预组别（实验=1）| 0.142 | 0.048 | .315 | 2.96 | .004 | [0.046, 0.238] |

注：*B* = 非标准化回归系数；SE = 标准误（正体）；*β* = 标准化回归系数；95% CI 为 *B* 的置信区间。
模型整体：*R²* = .524，调整后 *R²* = .493，*F* = 15.12，*p* < .001。
共线性诊断：所有预测变量 VIF < 3.0，未发现严重共线性问题（最大 VIF = 2.34）。
```

### 3.8 Logistic 回归结果表

**适用场景**：危险因素分析、二分类结局预测

```markdown
**表 8. 影响不良事件发生的二元 Logistic 回归分析（n = 120）**

| 变量 | *B* | SE | Wald *χ²* | *p* | OR | 95% CI |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 年龄（岁）| 0.042 | 0.019 | 4.87 | .027 | 1.04 | [1.005, 1.079] |
| 基线评分（分）| -0.078 | 0.024 | 10.61 | .001 | 0.92 | [0.880, 0.968] |
| 干预组别（实验=1）| -0.856 | 0.312 | 7.52 | .006 | 0.42 | [0.229, 0.782] |
| 病程（月）| 0.018 | 0.011 | 2.67 | .102 | 1.02 | [0.996, 1.040] |

注：*B* = Logistic 回归系数；SE = 标准误（正体）；Wald *χ²* = Wald 卡方统计量；OR = 优势比（Odds Ratio）= exp(*B*)；95% CI 为 OR 的置信区间（Wald 法）。
模型整体：*χ²* = 23.47，*p* < .001；Nagelkerke *R²* = .241；
Hosmer-Lemeshow 检验：*χ²* = 6.43，*p* = .599（*p* > .05 提示模型拟合良好）；AUC = 0.782（95% CI [0.698, 0.867]）。
参照组：组别中对照组 = 0。
```

---

## 四、Word 文档三线表实现（真正三根黑线）

### 4.1 Word 三线表核心要求

不同于 Markdown/LaTeX 的文本标记，Word 中的三线表需要通过**边框设置**实现：

| 线条位置 | 设置方式 | 线宽 | 颜色 |
|---|---|---|---|
| **顶线**（Top Rule）| 表格顶部边框 | **1.5 磅** | 黑色 |
| **中线**（Mid Rule）| 表头行下方边框 | **0.5 磅** | 黑色 |
| **底线**（Bottom Rule）| 表格底部边框 | **1.5 磅** | 黑色 |
| 其他边框 | 全部移除 | 无 | — |

> ⚠️ **禁止竖线**：Word 表格默认有竖线，必须全部移除
> ⚠️ **必须是三根黑线**：顶线 1.5 磅 + 中线 0.5 磅 + 底线 1.5 磅

### 4.2 Python 生成 Word 三线表完整代码

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_run_font(run, font_name='Times New Roman', font_size=10, bold=False, italic=False):
    """设置字体，支持中英文"""
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), 'SimSun')  # 中文字体
    rPr.insert(0, rFonts)

def set_cell_border(cell, **kwargs):
    """
    设置单元格边框
    参数：top, bottom, left, right = {"sz": 12, "val": "single", "color": "000000", "space": "0"}
    sz: 线宽（1/8磅），12=1.5磅，4=0.5磅
    val: "single"实线, "none"无边框
    color: 颜色代码，黑色="000000"
    """
    tc = cell._element
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')

    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge, {"sz": 0, "val": "none", "color": "000000", "space": "0"})
        tag = 'w:{}'.format(edge)
        element = OxmlElement(tag)
        element.set(qn('w:sz'), str(edge_data.get("sz", 0)))
        element.set(qn('w:val'), edge_data.get("val", "none"))
        element.set(qn('w:color'), edge_data.get("color", "000000"))
        element.set(qn('w:space'), str(edge_data.get("space", "0")))
        tcBorders.append(element)

    tcPr.append(tcBorders)

def add_italic_stat_to_cell(cell, text_parts):
    """
    向单元格添加带斜体统计符号的文本
    text_parts: [(text, italic), ...] 例如 [("t", True), (" = 2.34", False)]
    """
    paragraph = cell.paragraphs[0]
    paragraph.clear()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for text, italic in text_parts:
        run = paragraph.add_run(text)
        set_run_font(run, italic=italic)

def create_word_three_line_table(doc, title, headers, data, note=""):
    """
    创建 Word 三线表（真正的三根黑线）

    参数：
    - doc: Document 对象
    - title: 表格标题（如"表 1 两组基线特征比较"）
    - headers: 表头列表（统计符号需用 *符号* 标记，如 "*t* 值"）
    - data: 数据（二维列表）
    - note: 表注
    """
    # 添加标题
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run(title)
    set_run_font(title_run, font_size=10.5, bold=True)

    # 创建表格
    table = doc.add_table(rows=1 + len(data), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 填充表头
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        # 检查是否需要斜体（格式: *符号*）
        if header.startswith('*') and header.endswith('*') and header.count('*') == 2:
            # 纯斜体符号，如 "*p*"
            stat_symbol = header.strip('*')
            add_italic_stat_to_cell(cell, [(stat_symbol, True)])
        elif '*' in header:
            # 混合文本，如 "*t* 值"
            parts = []
            current = header
            while '*' in current:
                before, rest = current.split('*', 1)
                if before:
                    parts.append((before, False))
                stat, after = rest.split('*', 1)
                parts.append((stat, True))
                current = after
            if current:
                parts.append((current, False))
            add_italic_stat_to_cell(cell, parts)
        else:
            cell.text = header
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    set_run_font(run, bold=True)

    # 填充数据
    for row_idx, row_data in enumerate(data):
        for col_idx, cell_text in enumerate(row_data):
            cell = table.rows[row_idx + 1].cells[col_idx]

            # 检查是否包含统计符号需要斜体
            if '*t*' in cell_text or '*p*' in cell_text or '*F*' in cell_text or \
               '*χ²*' in cell_text or '*U*' in cell_text or '*Z*' in cell_text or \
               '*H*' in cell_text or '*r*' in cell_text:
                # 解析带斜体的文本
                import re
                parts = []
                current = cell_text
                # 匹配 *符号* 模式
                pattern = r'\*([^*]+)\*'
                last_end = 0
                for match in re.finditer(pattern, cell_text):
                    if match.start() > last_end:
                        parts.append((cell_text[last_end:match.start()], False))
                    parts.append((match.group(1), True))
                    last_end = match.end()
                if last_end < len(cell_text):
                    parts.append((cell_text[last_end:], False))
                add_italic_stat_to_cell(cell, parts)
            else:
                cell.text = str(cell_text)
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        set_run_font(run)

    # 设置三线表边框（真正的三根黑线）
    # sz 单位是 1/8 磅，12 = 1.5磅，4 = 0.5磅
    for row_idx, row in enumerate(table.rows):
        for col_idx, cell in enumerate(row.cells):
            if row_idx == 0:
                # 第一行（表头）：顶线1.5磅 + 底线0.5磅
                set_cell_border(cell,
                    top={"sz": 12, "val": "single", "color": "000000", "space": "0"},
                    bottom={"sz": 4, "val": "single", "color": "000000", "space": "0"},
                    left={"sz": 0, "val": "none"},
                    right={"sz": 0, "val": "none"}
                )
            elif row_idx == len(table.rows) - 1:
                # 最后一行：底线1.5磅
                set_cell_border(cell,
                    top={"sz": 0, "val": "none"},
                    bottom={"sz": 12, "val": "single", "color": "000000", "space": "0"},
                    left={"sz": 0, "val": "none"},
                    right={"sz": 0, "val": "none"}
                )
            else:
                # 中间行：无边框
                set_cell_border(cell,
                    top={"sz": 0, "val": "none"},
                    bottom={"sz": 0, "val": "none"},
                    left={"sz": 0, "val": "none"},
                    right={"sz": 0, "val": "none"}
                )

    # 设置列宽
    for col in table.columns:
        col.width = Inches(1.5)

    # 添加表注（表注中的统计符号也需要斜体）
    if note:
        doc.add_paragraph()
        note_para = doc.add_paragraph()
        note_para.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # 解析表注中的斜体标记
        import re
        pattern = r'\*([^*]+)\*'
        last_end = 0
        for match in re.finditer(pattern, note):
            if match.start() > last_end:
                run = note_para.add_run(note[last_end:match.start()])
                set_run_font(run, font_size=9)
            run = note_para.add_run(match.group(1))
            set_run_font(run, font_size=9, italic=True)
            last_end = match.end()
        if last_end < len(note):
            run = note_para.add_run(note[last_end:])
            set_run_font(run, font_size=9)

    return table

# 使用示例
"""
doc = Document()
headers = ['变量', '实验组(n=27)', '对照组(n=28)', '*t*', '*p*']
data = [
    ['年龄（岁）', '63.23 ± 11.76', '63.96 ± 13.63', '*t* = 0.21', '.832'],
    ['病程（天）', '9.00 ± 1.51', '8.91 ± 2.11', '*t* = 0.18', '.860'],
]
note = "数据以 M ± SD 表示。组间比较采用独立样本 *t* 检验。"
create_word_three_line_table(doc, '表 1 两组基线特征比较(n=55)', headers, data, note)
doc.save('/Users/leyixu/Desktop/三线表.docx')
"""
```

### 4.3 格式设置要点

#### 字体设置（中英文混排）
| 内容类型 | 英文字体 | 中文字体 | 字号 | 样式 |
|---|---|---|---|---|
| 表题 | Times New Roman | 宋体 | 10.5 pt | 加粗 |
| 表头 | Times New Roman | 宋体 | 10 pt | 加粗 |
| 数据 | Times New Roman | 宋体 | 10 pt | 常规 |
| 表注 | Times New Roman | 宋体 | 9 pt | 常规 |

#### 统计量符号斜体设置（关键！）
使用 `run.font.italic = True` 设置斜体：

```python
# 在单元格中设置斜体统计量符号
def add_italic_stat(cell, text_before, stat_symbol, text_after):
    """添加带斜体统计量的文本"""
    paragraph = cell.paragraphs[0]
    paragraph.clear()

    # 普通文本
    run1 = paragraph.add_run(text_before)
    set_run_font(run1)

    # 斜体统计量符号（如 t, p, F, χ²）
    run2 = paragraph.add_run(stat_symbol)
    set_run_font(run2, italic=True)

    # 普通文本
    run3 = paragraph.add_run(text_after)
    set_run_font(run3)

# 示例：生成 "t = 2.34"，其中 t 斜体
cell = table.rows[1].cells[3]
add_italic_stat(cell, "", "t", " = 2.34")
```

### 4.4 完整示例脚本（可直接运行）

上述代码已整合为完整脚本，位于：

> **`@/Users/leyixu/.claude/skills/thesis-data-analysis/scripts/word_three_line_table.py`**

**脚本特性：**
- ✅ 真正的三根黑线：顶线 1.5 磅、中线 0.5 磅、底线 1.5 磅
- ✅ 统计符号自动斜体：`*t*`、`*p*`、`*F*`、`*U*`、`*Z*`、`*H*`、`*r*` 等
- ✅ 希腊字母正体：`χ²`、`α`、`β`、`η` 等不斜体
- ✅ 表注中的统计符号同样支持斜体标记
- ✅ 三种示例表格：基线特征表、主要结局比较表、回归分析表

**快速使用：**

```bash
# 安装依赖
pip install python-docx

# 运行示例
python /Users/leyixu/.claude/skills/thesis-data-analysis/scripts/word_three_line_table.py
```

**自定义表格：**

```python
from docx import Document
from word_three_line_table import create_word_three_line_table

doc = Document()

headers = ['变量', '对照组（n=30）', '实验组（n=30）', '*t*', '*p*']
data = [
    ['年龄（岁）', '58.4 ± 9.6', '57.9 ± 8.8', '*t* = 0.21', '.832'],
    ['BMI（kg/m²）', '23.4 ± 3.2', '24.1 ± 2.9', '*t* = 0.90', '.373'],
]
note = "数据以 M ± SD 表示。组间比较采用独立样本 *t* 检验。"

create_word_three_line_table(
    doc, '表 1 两组基线特征比较（n = 60）',
    headers, data, note
)
doc.save('我的三线表.docx')
```

---

## 五、统计学符号与格式规范（核心修订）

### 5.1 符号斜体规则（GB 3358.1-2009 / APA 7th）

根据国家标准 GB 3358.1-2009《统计学词汇及符号》和 APA 7th：

| 符号类型 | 示例 | 格式 | 说明 |
|---|---|---|---|
| **必须斜体** | *t*, *F*, *p*, *s*, *n*, *r*, *Z*, *U*, *H*, *β* | **斜体** | 统计学变量符号 |
| **希腊字母** | χ²（整个符号）, *α*, *β*, *η²* | **正体** | 希腊文统计符号不斜体 |
| **正体** | SD, SE, CI, OR, RR, HR, M, df | 正体 | 缩写、常量 |
| **特殊** | P（大写）vs *p*（小写）| 国内期刊 *p* 斜体 | APA 要求小写 *p* 斜体 |

> ⚠️ **关键规范**：
> 1. **p 值**：小写 *p* 必须斜体（*p*），不是正体 p
> 2. **t 检验**：小写 *t* 必须斜体（*t*）
> 3. **F 检验**：大写 *F* 必须斜体（*F*）
> 4. **希腊字母**：χ²、α、β、η 等**不斜体**（保持正体）
> 5. **样本数**：小写 *n*（小组）、大写 *N*（总体）均斜体
> 6. **pH**：永远正体

### 5.2 统计量报告格式（修订版——去除自由度）

#### 修改后的格式（去除自由度括号）

| 检验类型 | 原格式 | **修改后格式** | 示例 |
|---|---|---|---|
| t 检验 | *t*(58) = 2.34 | ***t* = 2.34** | *t* = 2.34 |
| F 检验 | *F*(2, 57) = 9.43 | ***F* = 9.43** | *F* = 9.43 |
| χ² 检验 | χ²(1) = 0.15 | **χ² = 0.15** | χ² = 0.15 |
| Z 检验 | *Z* = 3.82 | ***Z* = 3.82** | *Z* = 3.82 |
| Mann-Whitney U | *U* = 271 | ***U* = 271** | *U* = 271 |
| 相关系数 | *r*(58) = 0.456 | ***r* = 0.456** | *r* = 0.456 |

> **自由度处理**：自由度在论文正文中说明，表格中省略以简化呈现
> **希腊字母不斜体**：χ² 中的 χ 是希腊字母，保持正体

#### p 值格式

| 情况 | 格式 | 示例 |
|---|---|---|
| p ≥ 0.001 | 保留 3 位小数，无前导零 | *p* = .032，*p* = .215 |
| p < 0.001 | 写 < .001，不写具体值 | *p* < .001 |
| 表格内 | 可简写为 .032 或 < .001 | .032，< .001 |

> ⚠️ **禁止**：p = 0.000，p = 0.032（前导零），P = .032（大写P），p=.032（无空格）
> ✅ **正确**：*p* < .001，*p* = .032（*p* 斜体，等号前后空格）

### 5.3 表格内 vs 文字描述中的统计符号（重要！）

#### 统一规则：**所有出现统计符号的地方都必须斜体**

| 位置 | 示例 | 是否正确 |
|---|---|---|
| 表格列标题 | *t* 值、*p* 值、*F* 值 | ✅ 正确（斜体）|
| 表格单元格 | *t* = 2.34、*p* = .032 | ✅ 正确（斜体）|
| 表注中的统计量 | "采用独立样本 *t* 检验" | ✅ 正确（*t* 斜体）|
| 表注中的 p 值 | "*p* < .05 视为显著" | ✅ 正确（*p* 斜体）|
| 表注中的效应量 | "偏 *η²* = .249" | ✅ 正确（*η²* 斜体，但希腊字母 η 本身不斜体）|

#### 表注中统计符号斜体示例

```markdown
✅ 正确的表注（统计符号均斜体）：
注：连续变量采用均值 ± 标准差（M ± SD）表示；组间比较采用独立样本 *t* 检验，
偏态变量采用 Mann-Whitney *U* 检验，分类变量采用 *χ²* 检验。
**p* < .01；所有检验均为双侧检验，α = .05。

❌ 错误的表注（统计符号未斜体）：
注：连续变量采用均值 ± 标准差（M ± SD）表示；组间比较采用独立样本 t 检验，
偏态变量采用 Mann-Whitney U 检验，分类变量采用 χ² 检验。
p < .01；所有检验均为双侧检验，α = .05。
```

### 5.4 完整示例（新格式——所有统计符号斜体）

```markdown
**表 1 两组受试者基线特征比较（n = 60）**

| 变量 | 对照组（n=30） | 实验组（n=30） | 统计量 | *p* |
|:---|:---:|:---:|:---:|:---:|
| 年龄（岁）| 58.4 ± 9.6 | 57.9 ± 8.8 | *t* = 0.21 | .832 |
| BMI（kg/m²）| 23.4 ± 3.2 | 24.1 ± 2.9 | *t* = 0.90 | .373 |
| 性别（男）| 18 (60.0%) | 16 (53.3%) | χ² = 0.27 | .601 |

注：连续变量以 M ± SD 表示；分类变量以 n (%) 表示。统计量符号采用斜体：*t* 为 *t* 检验，
χ² 为卡方检验（χ 为希腊字母，不斜体）。*p* < .05 视为差异有统计学意义。
```

---

## 六、LaTeX booktabs 完整代码模板库

### 6.1 基线特征表（LaTeX）

```latex
\usepackage{booktabs}
\usepackage{threeparttable}  % 支持表注

\begin{table}[htbp]
  \centering
  \caption{两组受试者基线特征比较（n = 60）}
  \label{tab:baseline}
  \begin{threeparttable}
    \begin{tabular}{lcccc}
      \toprule[1.5pt]  % 顶线 1.5磅
      变量 & 对照组（n=30） & 实验组（n=30） & 统计量 & \textit{p} \\[0.5em]
      \midrule[0.5pt]  % 中线 0.5磅
      \multicolumn{5}{l}{\textit{连续变量（正态）}} \\
      \quad 年龄（岁）& 58.4 ± 9.6 & 57.9 ± 8.8 & \textit{t} = 0.21 & .832 \\
      \quad BMI（kg/m²）& 23.4 ± 3.2 & 24.1 ± 2.9 & \textit{t} = 0.90 & .373 \\
      \multicolumn{5}{l}{\textit{分类变量}} \\
      \quad 男性，n (\%) & 18 (60.0) & 16 (53.3) & $\chi^2$ = 0.27 & .601 \\
      \bottomrule[1.5pt]  % 底线 1.5磅
    \end{tabular}
    \begin{tablenotes}
      \footnotesize
      \item 注：连续变量正态时采用均值 ± 标准差，偏态时采用中位数 [Q1, Q3]；
      分类变量采用 \textit{n}（\%），百分比以各组 \textit{n} 为分母。
      \item 组间比较：正态连续变量用独立样本 \textit{t} 检验；偏态用 Mann-Whitney \textit{U} 检验；
      分类变量用卡方检验。\textit{p} < .05 视为差异有统计学意义。
    \end{tablenotes}
  \end{threeparttable}
\end{table}
```

### 6.2 回归结果表（LaTeX）

```latex
\begin{table}[htbp]
  \centering
  \caption{多元线性回归分析结果（因变量：步行速度，n = 60）}
  \begin{threeparttable}
    \begin{tabular}{lccccc}
      \toprule[1.5pt]
      变量 & \textit{B} & SE & \textit{β} & \textit{t} & \textit{p} \\
      \midrule[0.5pt]
      年龄（岁）& -0.008 & 0.003 & -.284 & -2.66 & .010 \\
      Berg 评分 & 0.018 & 0.004 & .488 & 4.56$^{**}$ & < .001 \\
      干预组别 & 0.142 & 0.048 & .315 & 2.96$^{**}$ & .004 \\
      \midrule[0.5pt]
      \multicolumn{6}{l}{$R^2$ = .524，调整后 $R^2$ = .493，\textit{F} = 15.12，\textit{p} < .001} \\
      \bottomrule[1.5pt]
    \end{tabular}
    \begin{tablenotes}
      \footnotesize
      \item $^{**}$\textit{p} < .01。95\% CI 为非标准化系数 \textit{B} 的置信区间。
      \item SE = 标准误（正体）；\textit{β} = 标准化回归系数（斜体）。
    \end{tablenotes}
  \end{threeparttable}
\end{table}
```

---

## 七、Python 自动生成三线表代码

### 7.1 基线特征表生成器

```python
import pandas as pd
import numpy as np
from scipy import stats

def generate_baseline_table(df, group_col, cont_vars, cat_vars, alpha=0.05):
    """
    自动生成基线特征三线表（Markdown格式）
    所有统计符号自动标记斜体

    参数：
    - df: 数据框
    - group_col: 分组列名
    - cont_vars: 连续变量列表（字典：{变量名: 单位}）
    - cat_vars: 分类变量列表
    - alpha: 显著性水平
    """
    groups = sorted(df[group_col].unique())
    g_labels = {g: f"组{g}（n={df[df[group_col]==g].shape[0]}）" for g in groups}

    rows = []

    for var, unit in cont_vars.items():
        var_label = f"{var}（{unit}）" if unit else var
        row = {"变量": var_label}

        group_data = [df[df[group_col]==g][var].dropna() for g in groups]

        # 正态性检验
        sw_results = [stats.shapiro(gd) for gd in group_data]
        is_normal = all(sw.pvalue > alpha for sw in sw_results)

        if is_normal:
            # 参数方法
            for g, gd in zip(groups, group_data):
                row[g_labels[g]] = f"{gd.mean():.2f} ± {gd.std():.2f}"

            if len(groups) == 2:
                lev = stats.levene(*group_data)
                t_res = stats.ttest_ind(*group_data, equal_var=(lev.pvalue > alpha))
                # 格式: *t* = X.XX（斜体标记，无自由度）
                row["统计量"] = f"*t* = {t_res.statistic:.2f}"
                p = t_res.pvalue
            else:
                f_res = stats.f_oneway(*group_data)
                # 格式: *F* = X.XX（斜体标记，无自由度）
                row["统计量"] = f"*F* = {f_res.statistic:.2f}"
                p = f_res.pvalue
        else:
            # 非参数方法
            for g, gd in zip(groups, group_data):
                q1, q3 = gd.quantile([0.25, 0.75])
                row[g_labels[g]] = f"{gd.median():.1f} [{q1:.1f}, {q3:.1f}]"

            if len(groups) == 2:
                u_res = stats.mannwhitneyu(*group_data, alternative='two-sided')
                # 格式: *U* = XXX（斜体标记）
                row["统计量"] = f"*U* = {u_res.statistic:.1f}"
                p = u_res.pvalue
            else:
                h_res = stats.kruskal(*group_data)
                # 格式: *H* = X.XX（斜体标记，无自由度）
                row["统计量"] = f"*H* = {h_res.statistic:.2f}"
                p = h_res.pvalue

        # p 值格式: *p* < .001 或 .XXX（斜体标记，无前导零）
        row["*p*"] = "< .001" if p < 0.001 else f"= {p:.3f}".replace("0.", ".")
        rows.append(row)

    # 分类变量
    for var in cat_vars:
        ct = pd.crosstab(df[group_col], df[var])
        chi2, p, dof, expected = stats.chi2_contingency(ct)

        # 判断是否用Fisher
        use_fisher = (expected < 5).any() and ct.shape == (2,2)

        row = {"变量": var}
        for g in groups:
            n = df[df[group_col]==g].shape[0]
            pos = df[(df[group_col]==g) & (df[var]==1)].shape[0]
            row[g_labels[g]] = f"{pos} ({pos/n*100:.1f}%)"

        if use_fisher:
            _, p_fisher = stats.fisher_exact(ct)
            row["统计量"] = "Fisher 精确检验"
            p = p_fisher
        else:
            # 格式: χ² = X.XX（希腊字母不斜体，无自由度）
            row["统计量"] = f"χ² = {chi2:.2f}"

        # p 值格式: *p* < .001 或 .XXX（斜体标记，无前导零）
        row["*p*"] = "< .001" if p < 0.001 else f"= {p:.3f}".replace("0.", ".")
        rows.append(row)

    result_df = pd.DataFrame(rows)
    return result_df.to_markdown(index=False, tablefmt="pipe")

# 使用示例：
# print(generate_baseline_table(df, 'group',
#     cont_vars={"年龄": "岁", "BMI": "kg/m²"},
#     cat_vars=["sex", "diagnosis"]))
```

### 7.2 结果表效应量计算器

```python
def compute_effect_sizes(df, group_col, outcome_col):
    """计算两组比较的效应量及95% CI（Bootstrap法）"""
    import numpy as np
    from scipy import stats

    g1 = df[df[group_col]==df[group_col].unique()[0]][outcome_col].dropna().values
    g2 = df[df[group_col]==df[group_col].unique()[1]][outcome_col].dropna().values

    # Cohen's d
    n1, n2 = len(g1), len(g2)
    sd_pool = np.sqrt(((n1-1)*g1.std()**2 + (n2-1)*g2.std()**2) / (n1+n2-2))
    d = (g1.mean() - g2.mean()) / sd_pool

    # Bootstrap 95% CI for d
    n_boot = 5000
    boot_d = []
    for _ in range(n_boot):
        b1 = np.random.choice(g1, size=n1, replace=True)
        b2 = np.random.choice(g2, size=n2, replace=True)
        sd_b = np.sqrt(((n1-1)*b1.std()**2 + (n2-1)*b2.std()**2) / (n1+n2-2))
        boot_d.append((b1.mean() - b2.mean()) / sd_b if sd_b > 0 else 0)

    ci_low, ci_high = np.percentile(boot_d, [2.5, 97.5])

    print(f"Cohen's *d* = {d:.3f} [95% CI: {ci_low:.3f}, {ci_high:.3f}]")

    # 效应量解释
    if abs(d) < 0.2:
        interpretation = "可忽略效应"
    elif abs(d) < 0.5:
        interpretation = "小效应"
    elif abs(d) < 0.8:
        interpretation = "中等效应"
    else:
        interpretation = "大效应"

    print(f"效应量解释（Cohen 1988）：{interpretation}")
    return d, (ci_low, ci_high)
```

---

## 八、表格生成前决策清单

在生成任何三线表前，逐项确认：

**数据层面**
- [ ] 已确认每个变量的测量尺度（连续 / 分类 / 等级）
- [ ] 已检验连续变量的正态性，确定呈现方式（M±SD 或 M[IQR]）
- [ ] 已确认分类变量的百分比分母（各组 n 还是总 N）
- [ ] 已确认各组样本量（n）

**统计层面**
- [ ] 已明确每个对比使用的统计方法
- [ ] 已计算效应量（至少主要结局需包含）
- [ ] 已计算 95% CI（至少效应量需包含）
- [ ] p 值格式统一（< .001 或精确到 3 位小数）
- [ ] 统计量已去除自由度括号（如 *t* = 2.34，不是 *t*(58) = 2.34）
- [ ] 若有事后比较，已明确校正方法并在表注中说明

**格式层面（重点检查）**
- [ ] **表格内所有统计符号已斜体**（*t*、*p*、*F*、*U*、*Z*、*H*、*r* 等）
- [ ] **表注中的统计符号已斜体**（如"采用独立样本 *t* 检验"）
- [ ] **p 值列标题为 *p* 或 *p* 值**（斜体）
- [ ] **希腊字母不斜体**（χ²、α、β、η 等）
- [ ] 同一列小数位数统一
- [ ] 列标题含单位（括号内）
- [ ] 分组列标题含样本量（n=X）
- [ ] **无竖线，无单元格边框，只有三根水平黑线**
- [ ] 表注已写明：数据呈现方式 + 统计方法 + 效应量说明 + 显著性符号定义

---

## 九、常见错误与正确做法对照

| ❌ 错误做法 | ✅ 正确做法 |
|---|---|
| 所有连续变量一律 M±SD，不检验正态性 | 根据分布特征分别用 M±SD 或 M[IQR] |
| 只报告 p 值，无效应量 | 主要结局必须同时报告效应量 + 95% CI |
| 单位重复写在每个单元格 | 单位写在列标题括号内，单元格只填数值 |
| p = 0.000 | *p* < .001 |
| 表注缺失 | 表注必须说明呈现方式、统计方法、显著性定义 |
| 不同行小数位数不一致（如 2.3 和 4.23）| 同一列统一小数位数 |
| 显著性星号无说明 | 表注必须定义：*p < .05；**p < .01；***p < .001 |
| 效应量解释放在表格内单元格 | 效应量解释放在表注，表格只放数值 |
| 三组比较无事后检验说明 | 表注说明事后检验方法及校正策略 |
| OR 值写错（误用 B 代替 OR）| OR = exp(B)，必须用指数变换后的值 |
| **统计符号未斜体**（如 t = 2.34）| ***t* = 2.34**（t 斜体）|
| **p 值未斜体**（如 p = .032）| ***p* = .032**（p 斜体）|
| **表注中统计符号未斜体** | 表注中所有统计符号必须斜体 |
| Word 表格有竖线或边框 | 只保留三根水平黑线 |
| 统计量带自由度（如 *t*(58) = 2.34）| 去除自由度：*t* = 2.34 |

---

## 十、期刊投稿格式补充说明

### 国内中文期刊（如中华系列、中国康复等）
- 表格编号：阿拉伯数字，序号与正文引用一致
- 表题在表格上方，居中或左对齐
- 表注在表格下方，字号略小于正文
- 统计量通常写全名：*t* 值、*F* 值、χ²（不缩写）
- **p 值要求斜体小写 *p***（国内期刊多数采用）
- 三线表：顶线 1.5 磅、中线 0.5 磅、底线 1.5 磅

### 国际英文期刊（APA 7th / AMA / Vancouver）
- 表格标题使用 Title Case
- **统计量符号必须斜体**（*t*, *F*, *r*, *p*）
- p 值小写斜体，无前导零：*p* = .032（不写 *p* = 0.032）
- 95% CI 格式：[lower, upper]（方括号）
- 效应量和 CI 在脚注中解释解释标准
- 希腊字母（χ², α, β, η）不斜体

---

## 十一、关键要点总结

### 统计符号斜体速查表

| 符号 | 含义 | 是否斜体 | 正确示例 |
|---|---|---|---|
| *t* | t 检验统计量 | ✅ 斜体 | *t* = 2.34 |
| *p* | p 值 | ✅ 斜体 | *p* = .032，*p* < .001 |
| *F* | F 检验统计量 | ✅ 斜体 | *F* = 5.67 |
| *Z* | Z 检验统计量 | ✅ 斜体 | *Z* = 3.82 |
| *U* | Mann-Whitney U | ✅ 斜体 | *U* = 271 |
| *H* | Kruskal-Wallis H | ✅ 斜体 | *H* = 14.32 |
| *r* | 相关系数 | ✅ 斜体 | *r* = 0.456 |
| *n* / *N* | 样本数 | ✅ 斜体 | *n* = 30，*N* = 60 |
| χ² | 卡方统计量 | ⚠️ 希腊字母正体 | χ² = 0.15 |
| *α* / *β* | 显著性水平 | ⚠️ 希腊字母正体 | α = .05 |
| *η²* | 偏 eta 平方 | ⚠️ 希腊字母正体，整体斜体 | *η²* = .249 |
| SD | 标准差 | ❌ 正体 | SD = 9.6 |
| SE | 标准误 | ❌ 正体 | SE = 0.03 |
| CI | 置信区间 | ❌ 正体 | 95% CI [1.23, 4.56] |
| OR | 比值比 | ❌ 正体 | OR = 2.34 |
| M | 均值 | ❌ 正体 | M = 58.4 |

### 核心提醒

1. **表格内和表注中的统计符号必须统一斜体**
2. **Word 三线表必须是三根黑线**（顶线 1.5 磅、中线 0.5 磅、底线 1.5 磅）
3. **统计量去除自由度括号**（*t* = 2.34，不是 *t*(58) = 2.34）
4. **希腊字母（χ、α、β、η）不斜体**
5. **p 值小写斜体，无前导零**（*p* = .032）
