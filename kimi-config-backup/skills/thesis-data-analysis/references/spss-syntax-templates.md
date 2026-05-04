# SPSS Syntax Templates — 完整统计分析语法与 Python 交叉验证模板库

> **本文件用途**：提供论文常用统计方法的 SPSS 完整语法模板、输出解读要点，以及配套的 Python 等效代码，用于双平台交叉验证。
>
> **使用规则**：
> 1. 使用前必须将所有占位符变量名替换为真实变量名
> 2. 运行语法前先确认变量名、分组编码与数据结构
> 3. 任何方法运行前必须已完成前提假设验证
> 4. SPSS 与 Python 结果若存在差异，必须排查原因，不得直接采用其中一个

---

## 变量名约定（全文通用）

| 占位符 | 含义 | 替换示例 |
|---|---|---|
| `group` | 分组变量（数值编码）| group: 1=实验组, 2=对照组 |
| `outcome` / `score` | 主要因变量（连续）| pain_score, FIM_total |
| `before` / `after` | 前后测量变量 | T0_balance, T1_balance |
| `time1` `time2` `time3` | 重复测量时间点变量 | FIM_T0, FIM_T1, FIM_T2 |
| `id` | 受试者唯一标识 | patient_id |
| `x1` `x2` `x3` | 预测变量 / 协变量 | age, BMI, baseline_score |
| `event` | 二分类结局变量 | adverse_event (0=无, 1=有) |
| `var1` `var2` | 相关分析变量 | muscle_strength, gait_speed |

---

## 一、前提假设验证语法（所有分析前必须运行）

### 1.1 正态性检验（Shapiro-Wilk / KS）

```spss
* 分组正态性检验（每组分别出 Shapiro-Wilk）
EXAMINE VARIABLES=outcome
  /PLOT BOXPLOT HISTOGRAM NPPLOT
  /COMPARE GROUPS
  /STATISTICS DESCRIPTIVES
  /CINTERVAL 95
  /MISSING LISTWISE
  /NOTOTAL
  BY group.
```

> **结果解读**：
> - Shapiro-Wilk 列（n < 50 时优先参考）：Sig. > 0.05 → 近似正态
> - 同时查看 Normal Q-Q Plot：点接近对角线 → 近似正态
> - 箱线图：是否存在极端离群值（圆圈/星号标记）

**Python 等效代码**：
```python
from scipy import stats
import matplotlib.pyplot as plt

# Shapiro-Wilk 检验
for name, grp in df.groupby('group')['outcome']:
    stat, p = stats.shapiro(grp)
    print(f"组 {name}: W={stat:.4f}, p={p:.4f}")

# Q-Q 图
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for i, (name, grp) in enumerate(df.groupby('group')['outcome']):
    stats.probplot(grp, plot=axes[i])
    axes[i].set_title(f'Q-Q Plot: Group {name}')
plt.tight_layout()
plt.savefig('qq_normality.png', dpi=150)
```

---

### 1.2 方差齐性检验（Levene）

```spss
* 在独立样本t检验或ONEWAY输出中自动包含
* 也可单独运行：
EXAMINE VARIABLES=outcome BY group
  /STATISTICS DESCRIPTIVES
  /PLOT NONE
  /MISSING LISTWISE.
```

> **结果解读**：
> - "Test of Homogeneity of Variances" 表：Levene's F 的 Sig. > 0.05 → 方差齐
> - 若 p < 0.05 → 使用 Welch 校正版本

---

## 二、独立样本 t 检验（含 Welch t 检验）

### 2.1 SPSS 完整语法

```spss
* 独立样本 t 检验（SPSS 自动同时输出等方差与Welch两行结果）
T-TEST GROUPS=group(1 2)
  /MISSING=ANALYSIS
  /VARIABLES=outcome
  /CRITERIA=CI(.95).
```

### 2.2 输出解读（关键步骤，不可跳过）

```
Step 1: 先看 "Levene's Test for Equality of Variances"
  → Sig. > 0.05：读 "Equal variances assumed" 那行（标准独立t）
  → Sig. < 0.05：读 "Equal variances not assumed" 那行（Welch t）

Step 2: 在选定的行中读取：
  → t 值（含符号）
  → df（Welch时为小数，正常）
  → Sig.(2-tailed) → 报告时写 p = .XXX（< .001 时写 < .001）
  → Mean Difference = 组1均值 - 组2均值
  → 95% CI [Lower, Upper]

Step 3: SPSS 不直接输出 Cohen's d，需手动计算或用Python补充：
  Cohen's d = Mean Difference / SD_pooled
```

> ⚠️ **常见错误**：忘记先看Levene检验就直接读第一行，导致方差不齐时采用了错误结果。

### 2.3 Python 交叉验证代码

```python
import pingouin as pg
import scipy.stats as stats
import numpy as np

group1 = df[df['group'] == 1]['outcome'].dropna()
group2 = df[df['group'] == 2]['outcome'].dropna()

# pingouin（自动处理等方差/Welch，输出Cohen's d和power）
result = pg.ttest(group1, group2, paired=False, correction='auto')
print(result.to_string())
# 输出：t, dof, alternative, p-val, CI95%, cohen-d, BF10, power

# scipy 验证
t, p = stats.ttest_ind(group1, group2, equal_var=False)  # Welch
print(f"scipy Welch t: t={t:.4f}, p={p:.4f}")

# 效应量手动计算
n1, n2 = len(group1), len(group2)
sd_pooled = np.sqrt(((n1-1)*group1.std()**2 + (n2-1)*group2.std()**2) / (n1+n2-2))
cohens_d = (group1.mean() - group2.mean()) / sd_pooled
print(f"Cohen's d = {cohens_d:.4f}")
```

---

## 三、Mann-Whitney U 检验（独立样本非参数）

### 3.1 SPSS 完整语法

```spss
* Mann-Whitney U 检验
NPAR TESTS
  /M-W=outcome BY group(1 2)
  /STATISTICS DESCRIPTIVES
  /MISSING ANALYSIS.
```

> **结果解读**：
> - Mann-Whitney U 值
> - Asymp. Sig. (2-tailed)：样本量较大时用此渐近p值
> - Exact Sig.：样本量小时用精确p值（若SPSS有输出）
> - SPSS **不输出效应量 r**，需用Python补充：r = |Z| / √N

### 3.2 Python 交叉验证代码

```python
from scipy import stats
import numpy as np

group1 = df[df['group'] == 1]['outcome'].dropna()
group2 = df[df['group'] == 2]['outcome'].dropna()

U, p = stats.mannwhitneyu(group1, group2, alternative='two-sided')

# 效应量 r
N = len(group1) + len(group2)
z = stats.norm.ppf(p / 2)  # 从p值反推Z
r = abs(z) / np.sqrt(N)

print(f"Mann-Whitney U = {U:.1f}, p = {p:.4f}, r = {r:.4f}")
print(f"Median Group1: {group1.median():.2f} [IQR: {group1.quantile(0.25):.2f}-{group1.quantile(0.75):.2f}]")
print(f"Median Group2: {group2.median():.2f} [IQR: {group2.quantile(0.25):.2f}-{group2.quantile(0.75):.2f}]")
```

---

## 四、配对样本 t 检验

### 4.1 SPSS 完整语法

```spss
* 配对样本 t 检验
T-TEST PAIRS=before WITH after (PAIRED)
  /CRITERIA=CI(.95)
  /MISSING=ANALYSIS.
```

> **结果解读**：
> - "Paired Differences" 表：
>   → Mean：差值均值（after - before）
>   → Std. Deviation：差值标准差（用于计算 d_z）
>   → 95% CI [Lower, Upper]：差值的置信区间
>   → t 值 + df + Sig.(2-tailed)
> - Cohen's d_z = Mean / Std. Deviation（SPSS不直接输出，需手算）

### 4.2 Python 交叉验证代码

```python
import pingouin as pg
import scipy.stats as stats

pre = df['before'].dropna()
post = df['after'].dropna()

# pingouin（输出d_z）
result = pg.ttest(post, pre, paired=True)
print(result.to_string())

# scipy 验证
t, p = stats.ttest_rel(post, pre)
diff = post - pre
d_z = diff.mean() / diff.std(ddof=1)
print(f"scipy: t={t:.4f}, p={p:.4f}")
print(f"Cohen's d_z = {d_z:.4f}")
```

---

## 五、Wilcoxon 符号秩检验（配对非参数）

### 5.1 SPSS 完整语法

```spss
* Wilcoxon 符号秩检验
NPAR TESTS
  /WILCOXON=before WITH after (PAIRED)
  /STATISTICS DESCRIPTIVES
  /MISSING ANALYSIS.
```

> **结果解读**：
> - "Test Statistics" 表：Z 值 + Asymp. Sig. (2-tailed)
> - 效应量 r = |Z| / √N（SPSS不输出，需手算）
> - N = 参与检验的非零差值对数

### 5.2 Python 交叉验证代码

```python
from scipy import stats
import numpy as np

pre = df['before'].dropna()
post = df['after'].dropna()

stat, p = stats.wilcoxon(post, pre, alternative='two-sided')

# 效应量
diff = post - pre
n_nonzero = (diff != 0).sum()
# 使用正态近似计算Z（大样本）
z_approx = stats.norm.ppf(p / 2)
r = abs(z_approx) / np.sqrt(n_nonzero)

print(f"Wilcoxon W = {stat:.1f}, p = {p:.4f}, r = {r:.4f}")
```

---

## 六、单因素方差分析（One-Way ANOVA）

### 6.1 SPSS 完整语法（含多种事后检验）

```spss
* One-Way ANOVA（含方差齐性检验 + 多种事后检验）
ONEWAY outcome BY group
  /STATISTICS DESCRIPTIVES HOMOGENEITY WELCH BROWNFORSYTHE
  /MISSING ANALYSIS
  /POSTHOC=TUKEY GH BONFERRONI ALPHA(.05).
  /* TUKEY：方差齐时用；GH(Games-Howell)：方差不齐时用 */
```

> **结果解读**：
> - "Test of Homogeneity of Variances"：Levene p > 0.05 → 方差齐 → 参考ANOVA行和Tukey
> - 若方差不齐：参考 "Robust Tests of Equality of Means"（Welch F）和 Games-Howell
> - ANOVA 表：F([df_between], [df_within]) = [F值]，p = .XXX
> - η² = SS_Between / SS_Total（SPSS不直接输出，需手算或用Python）
> - 事后比较："Multiple Comparisons" 表：每对比较的 Mean Diff + 95% CI + Sig.

### 6.2 Python 交叉验证代码

```python
import pingouin as pg
from scipy import stats
import scikit_posthocs as sp

groups = [df[df['group'] == g]['outcome'].dropna().values for g in df['group'].unique()]

# pingouin（输出η²和ω²）
aov = pg.anova(data=df, dv='outcome', between='group', detailed=True)
print(aov.to_string())

# 事后检验（Tukey）
tukey = pg.pairwise_tukey(data=df, dv='outcome', between='group')
print(tukey.to_string())

# Games-Howell（方差不齐时）
gh = pg.pairwise_gameshowell(data=df, dv='outcome', between='group')
print(gh.to_string())
```

---

## 七、Kruskal-Wallis 检验（多组非参数）

### 7.1 SPSS 完整语法

```spss
* Kruskal-Wallis 检验
NPAR TESTS
  /K-W=outcome BY group(1 3)
  /STATISTICS DESCRIPTIVES
  /MISSING ANALYSIS.
```

> **结果解读**：
> - Chi-Square（H统计量）+ df + Asymp. Sig.
> - SPSS不输出效应量η²_H，需手算：η²_H = (H - k + 1) / (n - k)
> - 总体差异显著后，必须进行事后两两比较（Dunn + Bonferroni）

### 7.2 Python 代码（含Dunn事后检验）

```python
from scipy import stats
import scikit_posthocs as sp
import numpy as np

groups = [df[df['group'] == g]['outcome'].dropna().values for g in sorted(df['group'].unique())]
H, p = stats.kruskal(*groups)

k = len(groups)
n = sum(len(g) for g in groups)
eta2_H = (H - k + 1) / (n - k)

print(f"Kruskal-Wallis H({k-1}) = {H:.4f}, p = {p:.4f}, η²_H = {eta2_H:.4f}")

# Dunn事后检验（Bonferroni校正）
dunn = sp.posthoc_dunn(df, val_col='outcome', group_col='group', p_adjust='bonferroni')
print("\nDunn post-hoc (Bonferroni-corrected p-values):")
print(dunn.round(4))
```

---

## 八、重复测量方差分析（含球形假设处理）

### 8.1 SPSS 完整语法（3个时间点）

```spss
* 重复测量方差分析（单组，3时间点）
GLM time1 time2 time3
  /WSFACTOR=time 3 Polynomial
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(time) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=time.
```

> **结果解读（必须按序读）**：
> 1. "Mauchly's Test of Sphericity"：
>    → Sig. > 0.05：球形假设满足 → 读 "Sphericity Assumed" 行
>    → Sig. < 0.05：球形假设违反
>      - ε < 0.75 → 读 "Greenhouse-Geisser" 行，报告ε值
>      - ε ≥ 0.75 → 读 "Huynh-Feldt" 行，报告ε值
> 2. "Tests of Within-Subjects Effects"：F + df + p + Partial Eta²
> 3. "Pairwise Comparisons"（Bonferroni校正）：每对时间点比较

### 8.2 Python 交叉验证代码

```python
import pingouin as pg

# 数据需为长格式
df_long = df.melt(id_vars=['id'], value_vars=['time1', 'time2', 'time3'],
                  var_name='time', value_name='outcome')

# 重复测量ANOVA（含球形假设检验）
rm_aov = pg.rm_anova(data=df_long, dv='outcome', within='time',
                     subject='id', detailed=True, correction=True)
print(rm_aov.to_string())

# 事后Bonferroni配对比较
posthoc = pg.pairwise_tests(data=df_long, dv='outcome', within='time',
                             subject='id', parametric=True, padjust='bonferroni')
print(posthoc[['A', 'B', 'T', 'dof', 'p-unc', 'p-corr', 'cohen-d']].to_string())
```

---

## 九、混合方差分析（组别 × 时间，两因素混合设计）

### 9.1 SPSS 完整语法

```spss
* 混合方差分析（组别为被试间因子，时间为被试内因子）
GLM time1 time2 time3 BY group
  /WSFACTOR=time 3 Polynomial
  /BETWEEN=group
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(group*time) COMPARE(time) ADJ(BONFERRONI)
  /EMMEANS=TABLES(group) COMPARE ADJ(BONFERRONI)
  /EMMEANS=TABLES(time) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE ETASQ HOMOGENEITY
  /CRITERIA=ALPHA(.05)
  /WSDESIGN=time
  /DESIGN=group.
```

> **结果解读（优先顺序）**：
> 1. **交互效应（group * time）**：偏η² + F + p → 这是核心！
> 2. 若交互显著 → 分别读各组的时间效应（简单效应），以及各时间点的组间差异
> 3. 若交互不显著 → 读时间主效应和组别主效应
> 4. "Mauchly's Test"：同重复测量ANOVA处理方式
> 5. "Levene's Test of Equality of Error Variances"：各时间点的方差齐性

### 9.2 Python 交叉验证代码

```python
import pingouin as pg

df_long = df.melt(id_vars=['id', 'group'], value_vars=['time1', 'time2', 'time3'],
                  var_name='time', value_name='outcome')

# 混合ANOVA
mixed = pg.mixed_anova(data=df_long, dv='outcome', within='time',
                       between='group', subject='id', correction=True)
print(mixed.to_string())

# 简单效应：各组内时间效应
for g in df_long['group'].unique():
    sub = df_long[df_long['group'] == g]
    aov = pg.rm_anova(data=sub, dv='outcome', within='time', subject='id')
    print(f"\nGroup {g} - Time effect: F={aov['F'].values[0]:.4f}, p={aov['p-unc'].values[0]:.4f}, η²={aov['np2'].values[0]:.4f}")
```

---

## 十、卡方检验与 Fisher 精确检验

### 10.1 SPSS 完整语法

```spss
* 卡方检验（含期望频数、Fisher精确检验、效应量）
CROSSTABS
  /TABLES=group BY event
  /FORMAT=AVALUE TABLES
  /STATISTICS=CHISQ PHI RISK
  /CELLS=COUNT ROW COLUMN EXPECTED
  /COUNT ROUND CELL.
  /* CHISQ：卡方；PHI：φ/Cramér's V；RISK：OR和RR */
```

> **结果解读**：
> 1. 先看 "Cell counts" 表：检查期望频数（Expected Count）是否均 ≥ 5
> 2. 如有格子期望频数 < 5：用 "Fisher's Exact Test" 行（精确p值）
> 3. 否则用 "Pearson Chi-Square" 行：χ² + df + Asymp. Sig.
> 4. "Symmetric Measures"：Phi / Cramér's V（效应量）
> 5. "Risk Estimate"：OR + 95% CI（2×2表时可用）
> ⚠️ **SPSS 输出 .000 时，报告为 p < .001**

### 10.2 Python 交叉验证代码

```python
from scipy import stats
import numpy as np

ct = pd.crosstab(df['group'], df['event'])

# 卡方检验
chi2, p, dof, expected = stats.chi2_contingency(ct)
print(f"Expected frequencies:\n{expected.round(2)}")
print(f"\nChi2({dof}) = {chi2:.4f}, p = {p:.4f}")

# Cramér's V
n = ct.values.sum()
cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
print(f"Cramér's V = {cramers_v:.4f}")

# Fisher精确检验（2×2时）
if ct.shape == (2, 2):
    OR, p_fisher = stats.fisher_exact(ct)
    print(f"Fisher Exact: OR = {OR:.4f}, p = {p_fisher:.4f}")
```

---

## 十一、McNemar 检验（配对分类变量）

### 11.1 SPSS 完整语法

```spss
* McNemar 检验（配对前后二分类对比）
CROSSTABS
  /TABLES=before_event BY after_event
  /STATISTICS=MCNEMAR
  /CELLS=COUNT.
```

### 11.2 Python 代码

```python
from statsmodels.stats.contingency_tables import mcnemar
import numpy as np

# 构建配对列联表
ct_paired = pd.crosstab(df['before_event'], df['after_event'])
result = mcnemar(ct_paired, exact=True)
print(f"McNemar: statistic={result.statistic:.4f}, p={result.pvalue:.4f}")
```

---

## 十二、相关分析（Pearson / Spearman）

### 12.1 SPSS 完整语法

```spss
* Pearson 相关
CORRELATIONS
  /VARIABLES=var1 var2 var3
  /PRINT=TWOTAIL SIG
  /STATISTICS DESCRIPTIVES
  /MISSING=PAIRWISE.

* Spearman 相关
NONPAR CORR
  /VARIABLES=var1 var2
  /PRINT=SPEARMAN TWOTAIL SIG
  /MISSING=PAIRWISE.
```

> **结果解读**：
> - r 值 + Sig.(2-tailed) + N（样本量）
> - ⚠️ SPSS 不输出 95% CI，需用 Python 补充（Fisher's z 变换法）
> - 注意区分：相关矩阵中每个格子的N可能不同（成对排除缺失值）

### 12.2 Python 交叉验证代码（含95% CI）

```python
import pingouin as pg

# Pearson 相关（含95% CI）
r_result = pg.corr(df['var1'], df['var2'], method='pearson')
print(r_result[['n', 'r', 'CI95%', 'p-val']].to_string())

# Spearman 相关
rho_result = pg.corr(df['var1'], df['var2'], method='spearman')
print(rho_result[['n', 'r', 'CI95%', 'p-val']].to_string())
```

---

## 十三、ICC（组内相关系数）

### 13.1 SPSS 完整语法

```spss
* ICC 分析（双因素混合效应绝对一致性）
* 适用于评估者间信度 / 重测信度
RELIABILITY
  /VARIABLES=rater1 rater2 rater3
  /FORMAT=NOLABELS
  /SCALE('ALL VARIABLES') ALL
  /MODEL=ALPHA
  /ICC=MODEL(MIXED) TYPE(ABSOLUTE) CONFIDENCE(95) TESTVAL(.0).
```

> **结果解读**：
> - "Intraclass Correlation Coefficient" 表：
>   → Single Measures ICC（单个评估者的信度）
>   → Average Measures ICC（多个评估者平均后的信度）
>   → 95% CI [Lower, Upper]
>   → F检验 + p值
> - 根据 Koo & Mae（2016）：> 0.90 极好；0.75-0.90 良好；0.50-0.75 中等；< 0.50 差

### 13.2 Python 代码

```python
import pingouin as pg

# 数据需为长格式：id, rater, score
icc = pg.intraclass_corr(data=df_long, targets='id', raters='rater',
                          ratings='score', nan_policy='omit')
print(icc[icc['Type'] == 'ICC2']['ICC'].values[0])  # 双因素混合绝对一致性
print(icc.to_string())
```

---

## 十四、线性回归

### 14.1 SPSS 完整语法（含诊断）

```spss
* 多元线性回归（含共线性诊断和残差分析）
REGRESSION
  /DESCRIPTIVES MEAN STDDEV CORR SIG N
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA COLLIN TOL CHANGE CI(95)
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN
  /DEPENDENT outcome
  /METHOD=ENTER x1 x2 x3
  /SCATTERPLOT=(*ZRESID, *ZPRED)
  /RESIDUALS HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /CASEWISE PLOT(ZRESID) OUTLIERS(3)
  /SAVE COOK DFFIT LEVER.
```

> **结果解读**：
> - "Model Summary"：R, R², 调整R², Std. Error
> - "ANOVA" 表：整体模型F检验
> - "Coefficients" 表：B + SE + β + t + Sig. + 95% CI [Lower, Upper]
> - "Collinearity Statistics"：Tolerance < 0.1（VIF > 10）→ 严重共线性问题
> - 残差散点图：无明显喇叭形 → 方差齐性满足

### 14.2 Python 交叉验证代码

```python
import statsmodels.api as sm
import statsmodels.stats.outliers_influence as oi
import pandas as pd

X = df[['x1', 'x2', 'x3']]
y = df['outcome']
X_const = sm.add_constant(X)

model = sm.OLS(y, X_const).fit()
print(model.summary())

# VIF检查
vif_data = pd.DataFrame({
    'Variable': X.columns,
    'VIF': [oi.variance_inflation_factor(X_const.values, i+1) for i in range(len(X.columns))]
})
print("\nVIF:")
print(vif_data)

# Cook's D
influence = model.get_influence()
cooks_d, _ = influence.cooks_distance
print(f"Max Cook's D: {cooks_d.max():.4f} (threshold: {4/len(y):.4f})")
```

---

## 十五、二元 Logistic 回归

### 15.1 SPSS 完整语法

```spss
* 二元 Logistic 回归（含Hosmer-Lemeshow拟合优度检验）
LOGISTIC REGRESSION VARIABLES event
  /METHOD=ENTER x1 x2 x3
  /CONTRAST (x_categorical)=Indicator(1)  /* 分类变量设置参照组 */
  /PRINT=GOODFIT ITER(1) CI(95)
  /CRITERIA=PIN(.05) POUT(.10) ITERATE(20) CUT(.5)
  /CLASSPLOT
  /CASEWISE OUTLIER(2).
```

> **结果解读**：
> - "Omnibus Tests"：模型整体χ² + p
> - "Model Summary"：-2 Log likelihood + Cox & Snell R² + Nagelkerke R²
> - "Hosmer and Lemeshow Test"：Sig. > 0.05 → 模型拟合较好（不显著为好）
> - "Variables in the Equation"：B + SE + Wald + Sig. + **Exp(B)即OR** + 95% CI
> ⚠️ 报告时用 Exp(B) 作为 OR 值，不是 B 值

### 15.2 Python 交叉验证代码（含AUC）

```python
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import numpy as np

X = df[['x1', 'x2', 'x3']]
y = df['event']
X_const = sm.add_constant(X)

logit_model = sm.Logit(y, X_const).fit()
print(logit_model.summary())

# OR 和 95% CI
params = logit_model.params
conf = logit_model.conf_int()
conf['OR'] = np.exp(params)
conf.columns = ['2.5%', '97.5%', 'OR']
conf['2.5%'] = np.exp(conf['2.5%'])
conf['97.5%'] = np.exp(conf['97.5%'])
print("\nOR [95% CI]:")
print(conf[['OR', '2.5%', '97.5%']].round(4))

# ROC / AUC
y_pred_prob = logit_model.predict(X_const)
auc = roc_auc_score(y, y_pred_prob)
print(f"\nAUC = {auc:.4f}")
```

---

## 十六、描述性统计

### 16.1 SPSS 完整语法

```spss
* 连续变量描述性统计
DESCRIPTIVES VARIABLES=var1 var2 var3
  /STATISTICS=MEAN STDDEV MIN MAX SEMEAN KURTOSIS SKEWNESS.

* 偏态变量中位数/四分位数
EXAMINE VARIABLES=var1 var2
  /PLOT NONE
  /STATISTICS DESCRIPTIVES
  /PERCENTILES(25,50,75)
  /MISSING LISTWISE.

* 分类变量频数
FREQUENCIES VARIABLES=group sex event
  /STATISTICS=MODE
  /ORDER=ANALYSIS.

* 按组分层描述
SORT CASES BY group.
SPLIT FILE SEPARATE BY group.
DESCRIPTIVES VARIABLES=outcome
  /STATISTICS=MEAN STDDEV MIN MAX.
SPLIT FILE OFF.
```

### 16.2 Python 等效代码

```python
import pandas as pd
import numpy as np

# 连续变量（按组）
desc = df.groupby('group')['outcome'].agg([
    ('n', 'count'),
    ('mean', 'mean'),
    ('sd', 'std'),
    ('median', 'median'),
    ('Q1', lambda x: x.quantile(0.25)),
    ('Q3', lambda x: x.quantile(0.75)),
    ('min', 'min'),
    ('max', 'max'),
    ('skewness', lambda x: x.skew()),
    ('kurtosis', lambda x: x.kurtosis())
]).round(3)
print(desc)

# 分类变量（按组）
cat_summary = df.groupby(['group', 'event']).size().reset_index(name='n')
cat_summary['pct'] = cat_summary.groupby('group')['n'].transform(lambda x: x / x.sum() * 100).round(1)
print(cat_summary)
```

---

## 十七、SPSS 与 Python 差异排查清单

每次交叉验证发现差异时，按以下清单逐项排查：

| 排查项目 | 说明 | 常见差异原因 |
|---|---|---|
| 样本量 N | 两平台的有效样本量是否一致 | SPSS 可能用 listwise / pairwise 不同排除策略 |
| 缺失值处理 | 缺失值排除方式是否相同 | SPSS 默认 listwise；Python 需手动 dropna |
| 单尾/双尾 | 是否均为双侧检验 | Python 中需指定 alternative='two-sided' |
| 方差齐性设定 | t 检验是否使用了同样的等方差设定 | SPSS 输出两行，需选正确行 |
| 分类变量编码 | 参照组是否一致 | SPSS 默认最小值为参照；Python 需显式指定 |
| 球形校正 | 重复测量中校正方法是否一致 | 确认均用 GG 或均用 HF |
| 精度 | 四舍五入方式 | 差异 < 0.001 通常可接受 |
| 检验方向 | 事后检验配对顺序（A-B vs B-A）| 符号不同但绝对值相同属正常 |

---

## 十八、结果解读标准流程（每次分析必须遵守）

```
Step 1  →  确认检验方法是否与研究设计匹配
Step 2  →  确认前提假设是否满足（Levene / Shapiro-Wilk / Mauchly）
Step 3  →  确认读取了正确的输出行（如t检验须先看Levene再决定读哪行）
Step 4  →  提取关键统计量：检验统计量 + df + p值
Step 5  →  提取或计算效应量 + 95% CI
Step 6  →  对照 Python 结果（差异 < 0.001 为合理）
Step 7  →  以"论文可用"语言写出结果段落
Step 8  →  在结果段中体现方法选择理由（若使用了非参数替代，需说明原因）
```

---

## 十九、禁止事项

| 禁止行为 | 原因 |
|---|---|
| 不看Levene检验就直接读t检验第一行 | 可能读取错误（方差不齐时应用Welch行）|
| SPSS显示.000直接写p=0.000 | 应写p < .001 |
| 只报告p值不报告效应量 | 违反APA第七版及SAMPL指南 |
| 没有原始数据时宣称已完成Python重算 | 学术诚信问题 |
| 用户变量名不清就直接填入语法运行 | 必须先确认变量含义和编码 |
| ANOVA显著后不做事后检验 | 无法确定哪对组间存在差异 |
| 非参数检验不报告效应量 | Mann-Whitney/Wilcoxon必须报告r |
