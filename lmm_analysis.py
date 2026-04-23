#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重复测量 LMM 分析脚本
目标：
1. T0 基线组间比较（P>0.05 为对齐）
2. LMM 模型：指标 ~ C(分组)*C(时间点) + (1|患者ID)
3. 提取 T2/T3 时点组间对比（G1>G2>G3≈G4）
"""

import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. 数据读取与预处理
# ============================================================
file_path = '/Users/leyixu/Desktop/4月20日数据 2.csv'
df = pd.read_csv(file_path)

# 清理列名（去除空格）
df.columns = df.columns.str.strip()

# 确保关键列类型正确
df['分组'] = df['分组'].astype(int)
df['患者ID'] = df['患者ID'].astype(str)
df['时间点'] = df['时间点'].astype(str).str.strip().str.upper()

# 将分组设为有序分类，1为参考组
df['分组'] = pd.Categorical(df['分组'], categories=[1, 2, 3, 4])
# 时间点有序分类，T0为参考组
df['时间点'] = pd.Categorical(df['时间点'], categories=['T0', 'T1', 'T2', 'T3'])

print("=" * 80)
print("数据概览")
print("=" * 80)
print(f"总记录数: {len(df)}")
print(f"患者数: {df['患者ID'].nunique()}")
print(f"分组分布:\n{df.groupby('分组')['患者ID'].nunique()}")
print(f"时间点分布:\n{df['时间点'].value_counts().sort_index()}")
print()

# ============================================================
# 2. T0 基线组间比较
# ============================================================
print("=" * 80)
print("【第一步】T0 基线组间比较")
print("=" * 80)
print("目标：各指标在 T0 时点组间差异 P > 0.05（基线对齐）")
print("-" * 80)

baseline_metrics = ['FMA_LE', 'ADL', 'BBS', 'TUGT']
t0_df = df[df['时间点'] == 'T0'].copy()

baseline_results = []
for metric in baseline_metrics:
    groups = []
    group_labels = []
    for g in [1, 2, 3, 4]:
        vals = t0_df[t0_df['分组'] == g][metric].dropna().values
        groups.append(vals)
        group_labels.append(f"G{g}")

    # 描述统计
    desc = []
    for i, g in enumerate([1, 2, 3, 4]):
        vals = groups[i]
        desc.append(f"G{g}: {np.mean(vals):.2f}±{np.std(vals, ddof=1):.2f}(n={len(vals)})")

    # One-way ANOVA（经典基线比较方法）
    f_stat, p_anova = stats.f_oneway(*groups)

    # Kruskal-Wallis（非参数备选，不依赖正态/方差齐）
    h_stat, p_kw = stats.kruskal(*groups)

    baseline_results.append({
        '指标': metric,
        'ANOVA_F': f_stat,
        'ANOVA_P': p_anova,
        'KW_H': h_stat,
        'KW_P': p_kw,
        '描述': ' | '.join(desc)
    })

    print(f"\n指标: {metric}")
    print(f"  描述: {' | '.join(desc)}")
    print(f"  ANOVA: F={f_stat:.3f}, P={p_anova:.4f} {'[对齐]' if p_anova > 0.05 else '[未对齐]'}")
    print(f"  Kruskal-Wallis: H={h_stat:.3f}, P={p_kw:.4f} {'[对齐]' if p_kw > 0.05 else '[未对齐]'}")

# ============================================================
# 3. LMM 建模与特定时点组间对比
# ============================================================
print("\n" + "=" * 80)
print("【第二步】线性混合模型 (LMM) 分析")
print("=" * 80)
print("模型公式: 指标 ~ C(分组, Treatment(1)) * C(时间点, Treatment('T0')) + (1 | 患者ID)")
print("随机效应: 患者ID 的随机截距")
print("-" * 80)

# 关注的指标和时点
metrics_of_interest = {
    'FMA_LE': ['T2', 'T3'],
    'ADL': ['T2'],
    'BBS': ['T2'],
    'TUGT': ['T2']
}


def get_contrast(result, coef_names, signs):
    """
    计算线性对比: sum(signs[i] * coef[coef_names[i]])
    返回: (估计值, 标准误, Z值, P值)
    """
    est = 0.0
    var = 0.0
    for i, name in enumerate(coef_names):
        est += signs[i] * result.params[name]
        for j, name2 in enumerate(coef_names):
            var += signs[i] * signs[j] * result.cov_params().loc[name, name2]
    se = np.sqrt(var)
    z = est / se if se > 0 else np.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if not np.isnan(z) else np.nan
    return est, se, z, p


def _find_param(params_index, *prefixes):
    """通过前缀模糊匹配找到唯一的参数名"""
    matches = []
    for p in params_index:
        if all(pref in p for pref in prefixes):
            matches.append(p)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # 取最短匹配（最精确）
        return min(matches, key=len)
    return None


def extract_timepoint_contrasts(result, timepoint):
    """
    从 LMM 全模型中提取特定时间点的组间对比。
    假设参考组为 G1，参考时间点为 T0。

    在时间点 T 时：
    - G1 vs G2 的差异 = C(分组)[T.2] + C(分组)[T.2]:C(时间点)[T.T]
    - G2 vs G3 的差异 = (G3-G1|T) - (G2-G1|T)
    """
    idx = result.params.index
    contrasts = {}

    # 动态查找参数名（兼容 statsmodels 不同版本的命名格式）
    p_g2 = _find_param(idx, 'C(分组', '[T.2]')
    p_g3 = _find_param(idx, 'C(分组', '[T.3]')
    p_g4 = _find_param(idx, 'C(分组', '[T.4]')
    p_g2_t = _find_param(idx, 'C(分组', '[T.2]', f'[T.{timepoint}]')
    p_g3_t = _find_param(idx, 'C(分组', '[T.3]', f'[T.{timepoint}]')
    p_g4_t = _find_param(idx, 'C(分组', '[T.4]', f'[T.{timepoint}]')

    if not all([p_g2, p_g3, p_g4, p_g2_t, p_g3_t, p_g4_t]):
        print(f"  [警告] 未能完全匹配 {timepoint} 的交互项系数，跳过对比提取")
        print(f"    找到: g2={p_g2}, g3={p_g3}, g4={p_g4}")
        print(f"    找到: g2_{timepoint}={p_g2_t}, g3_{timepoint}={p_g3_t}, g4_{timepoint}={p_g4_t}")
        return contrasts

    # --- G1 vs G2 ---
    names = [p_g2, p_g2_t]
    signs = [1, 1]
    contrasts['G1 vs G2'] = get_contrast(result, names, signs)

    # --- G1 vs G3 ---
    names = [p_g3, p_g3_t]
    signs = [1, 1]
    contrasts['G1 vs G3'] = get_contrast(result, names, signs)

    # --- G1 vs G4 ---
    names = [p_g4, p_g4_t]
    signs = [1, 1]
    contrasts['G1 vs G4'] = get_contrast(result, names, signs)

    # --- G2 vs G3 ---
    names = [p_g3, p_g3_t, p_g2, p_g2_t]
    signs = [1, 1, -1, -1]
    contrasts['G2 vs G3'] = get_contrast(result, names, signs)

    # --- G2 vs G4 ---
    names = [p_g4, p_g4_t, p_g2, p_g2_t]
    signs = [1, 1, -1, -1]
    contrasts['G2 vs G4'] = get_contrast(result, names, signs)

    # --- G3 vs G4 ---
    names = [p_g4, p_g4_t, p_g3, p_g3_t]
    signs = [1, 1, -1, -1]
    contrasts['G3 vs G4'] = get_contrast(result, names, signs)

    return contrasts


# 存储所有结果
all_results = []

for metric, timepoints in metrics_of_interest.items():
    print(f"\n{'='*60}")
    print(f"指标: {metric}")
    print(f"{'='*60}")

    # 准备数据：去除该指标的缺失值
    sub_df = df[['患者ID', '分组', '时间点', metric]].dropna().copy()
    n_subjects = sub_df['患者ID'].nunique()
    n_obs = len(sub_df)
    print(f"有效数据: {n_obs} 条记录 / {n_subjects} 名患者")

    if n_obs == 0:
        print("无有效数据，跳过")
        continue

    # 拟合 LMM 全模型
    formula = f"{metric} ~ C(分组, Treatment(1)) * C(时间点, Treatment('T0'))"
    try:
        model = smf.mixedlm(formula, data=sub_df, groups=sub_df['患者ID'])
        result = model.fit()

        print(f"\n模型收敛: {getattr(result, 'converged', True)}")
        print(f"AIC: {result.aic:.2f}, BIC: {result.bic:.2f}")

        # 输出关键固定效应（精简版）
        print(f"\n--- 固定效应摘要 ---")
        coef_df = pd.DataFrame({
            '估计值': result.params,
            '标准误': result.bse,
            'Z值': result.tvalues,
            'P值': result.pvalues
        })
        # 只显示与分组相关的效应
        group_related = [c for c in coef_df.index if '分组' in c or 'Intercept' in c]
        print(coef_df.loc[group_related].round(4))

        # 提取各关注时点的组间对比
        for tp in timepoints:
            print(f"\n--- {metric} @ {tp} 组间对比 ---")
            contrasts = extract_timepoint_contrasts(result, tp)

            for comp_name, (est, se, z, p) in contrasts.items():
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
                direction = ""
                if p < 0.05:
                    if est > 0:
                        direction = " (前者 > 后者)"
                    elif est < 0:
                        direction = " (前者 < 后者)"

                print(f"  {comp_name:12s}: Est={est:7.3f}, SE={se:6.3f}, Z={z:7.3f}, P={p:.4f} [{sig}]{direction}")

                all_results.append({
                    '指标': metric,
                    '时点': tp,
                    '对比': comp_name,
                    '估计值': est,
                    '标准误': se,
                    'Z值': z,
                    'P值': p,
                    '显著性': sig
                })

    except Exception as e:
        print(f"模型拟合失败: {e}")
        import traceback
        traceback.print_exc()

# ============================================================
# 4. 结果汇总表
# ============================================================
print("\n" + "=" * 80)
print("【第三步】结果汇总：是否符合目标？")
print("=" * 80)

if all_results:
    results_df = pd.DataFrame(all_results)

    # 目标模式检查
    target_checks = [
        ('G1 vs G2', '<', 0.05, 'G1 > G2 显著'),
        ('G2 vs G3', '<', 0.05, 'G2 > G3 显著'),
        ('G2 vs G4', '<', 0.05, 'G2 > G4 显著'),
        ('G3 vs G4', '>', 0.05, 'G3 = G4 不显著'),
    ]

    for metric in results_df['指标'].unique():
        for tp in results_df[results_df['指标']==metric]['时点'].unique():
            print(f"\n--- {metric} @ {tp} ---")
            sub = results_df[(results_df['指标']==metric) & (results_df['时点']==tp)]

            for comp, op, threshold, desc in target_checks:
                row = sub[sub['对比'] == comp]
                if not row.empty:
                    p = row['P值'].values[0]
                    est = row['估计值'].values[0]
                    met = (p < threshold) if op == '<' else (p > threshold)
                    status = "✅ 符合" if met else "❌ 不符"
                    print(f"  {comp:12s}: P={p:.4f} | {desc} | {status}")
                else:
                    print(f"  {comp:12s}: [无数据]")

print("\n" + "=" * 80)
print("分析完成")
print("=" * 80)
