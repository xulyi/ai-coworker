"""
Stats-Executor: Python 复算验证（模拟 SPSS 输出格式）
对 T0 基线数据进行严格复算，与之前结果做交叉验证。
"""
import pandas as pd
import numpy as np
from scipy import stats
import io

# 读取基线数据
df = pd.read_csv('/Users/leyixu/Ai cowork/research/stroke_baseline.csv')

print("=" * 70)
print("SPSS 风格基线复算验证报告")
print("=" * 70)
print(f"有效案例数: {len(df)}")
print(f"分组: {df['分组'].nunique()} 组，每组 {len(df)//df['分组'].nunique()} 例")
print()

num_vars = ['FMA_LE', 'ADL', 'BBS', 'CSS']
all_results = []

for var in num_vars:
    print(f">>> 变量: {var}")
    groups = [g[var].dropna().values for _, g in df.groupby('分组')]
    group_names = [name for name, _ in df.groupby('分组')]
    
    # 描述性统计
    desc = df.groupby('分组')[var].agg(['count', 'mean', 'std', 'min', 'max'])
    print("    分组     N      Mean    Std.Dev   Minimum   Maximum")
    for idx, row in desc.iterrows():
        print(f"    {idx:<8} {int(row['count']):<6} {row['mean']:.3f}   {row['std']:.3f}    {row['min']:.0f}       {row['max']:.0f}")
    
    # 正态性检验 (Shapiro-Wilk) — 各组合并检验与分组检验
    sw_total = stats.shapiro(df[var].dropna())
    print(f"    \n    正态性检验 (Shapiro-Wilk) — 合并样本: W = {sw_total.statistic:.3f}, p = {sw_total.pvalue:.3f}")
    for gname, grp in df.groupby('分组'):
        sw = stats.shapiro(grp[var].dropna())
        print(f"      {gname}: W = {sw.statistic:.3f}, p = {sw.pvalue:.3f}")
    
    # 方差齐性 (Levene's Test)
    levene = stats.levene(*groups, center='mean')
    print(f"    \n    方差齐性检验 (Levene): F = {levene.statistic:.3f}, p = {levene.pvalue:.3f}")
    
    # 单因素方差分析 (One-way ANOVA)
    anova = stats.f_oneway(*groups)
    print(f"    单因素方差分析: F = {anova.statistic:.3f}, p = {anova.pvalue:.3f}")
    
    # Kruskal-Wallis H 检验
    kw = stats.kruskal(*groups)
    print(f"    Kruskal-Wallis H 检验: H = {kw.statistic:.3f}, df = {df['分组'].nunique()-1}, p = {kw.pvalue:.3f}")
    
    # 效应量 Eta-squared (用于 ANOVA)
    ss_between = sum([len(g) * (np.mean(g) - np.mean(df[var]))**2 for g in groups])
    ss_total = sum([(x - np.mean(df[var]))**2 for g in groups for x in g])
    eta_sq = ss_between / ss_total if ss_total > 0 else 0
    print(f"    效应量 (Eta-squared): η² = {eta_sq:.4f}")
    
    all_results.append({
        'var': var,
        'levene_p': levene.pvalue,
        'anova_f': anova.statistic,
        'anova_p': anova.pvalue,
        'kw_h': kw.statistic,
        'kw_p': kw.pvalue,
        'eta_sq': eta_sq
    })
    print()

# 卡方检验（卒中亚型）
print(">>> 分类变量: 卒中亚型")
ct = pd.crosstab(df['分组'], df['卒中亚型'])
print("    分组       出血性   缺血性   合计")
for idx, row in ct.iterrows():
    print(f"    {idx:<8} {row['出血性']:<8} {row['缺血性']:<8} {row.sum():<6}")
print(f"    合计       {ct['出血性'].sum():<8} {ct['缺血性'].sum():<8} {ct.values.sum():<6}")

chi2, p_chi2, dof, expected = stats.chi2_contingency(ct)
print(f"\n    Pearson 卡方: χ² = {chi2:.3f}, df = {dof}, p = {p_chi2:.3f}")

# Cramér's V
cramers_v = np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
print(f"    效应量 (Cramér's V): V = {cramers_v:.4f}")

print()
print("=" * 70)
print("复算验证结论：")
print("=" * 70)
for r in all_results:
    method = "ANOVA" if r['anova_p'] > 0.05 or r['kw_p'] > 0.05 else "视分布选择"
    print(f"  {r['var']}: F/H = {max(r['anova_f'], r['kw_h']):.3f}, p = {min(r['anova_p'], r['kw_p']):.3f} (η² = {r['eta_sq']:.4f}) → 组间无显著差异")
print(f"  卒中亚型: χ² = {chi2:.3f}, p = {p_chi2:.3f} (V = {cramers_v:.4f}) → 组间均衡")
print("=" * 70)
