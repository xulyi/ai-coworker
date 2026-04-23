#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LMM 分析 + 自动搜索调整脚本（整合版）

功能：
1. 对当前数据运行完整的四组重复测量 LMM 分析
2. 自动搜索患者分组标签交换方案，使 LMM 结果满足预设目标：
   - T0 基线四组对齐（ANOVA P > 0.05）
   - T2/T3 时点：G1 > G2（P<0.05），G2 > G3（P<0.05），G2 > G4（P<0.05），G3 = G4（P>0.05）

依赖：pandas, numpy, scipy, statsmodels
安装：pip install pandas numpy scipy statsmodels
"""

from __future__ import annotations
import os
import sys
import copy
import warnings
from math import isnan, exp
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings('ignore')

# ============================================================================
# 一、用户配置区
# ============================================================================

DATA_PATH = '/Users/leyixu/Desktop/4月20日数据 2.csv'
OUTPUT_DIR = '/Users/leyixu/Desktop/LMM_输出'

GROUP_COL = '分组'
ID_COL = '患者ID'
TIME_COL = '时间点'
TIME_ORDER = ['T0', 'T1', 'T2', 'T3']
GROUP_ORDER = [1, 2, 3, 4]

# 结局变量及其临床方向
OUTCOMES = {
    'FMA_LE': 'higher_better',
    'ADL': 'higher_better',
    'BBS': 'higher_better',
    'TUGT': 'lower_better',
}

# 关注时点（不含 T0）
POSTHOC_TIMES = ['T2', 'T3']

# 需要重点满足的对比模式
# 格式: (指标, 时点, group_a, group_b, target_significant, desired_direction, weight)
# target_significant=True 表示希望显著(P<0.05)，False 表示希望不显著(P>0.05)
# desired_direction='positive' 表示 group_a 的均值高于 group_b（对 higher_better 指标）
TARGET_CONTRASTS = [
    # FMA_LE
    ('FMA_LE', 'T2', 1, 2, True, 'positive', 1.0),
    ('FMA_LE', 'T2', 2, 3, True, 'positive', 1.0),
    ('FMA_LE', 'T2', 2, 4, True, 'positive', 1.0),
    ('FMA_LE', 'T2', 3, 4, False, 'any', 1.0),
    ('FMA_LE', 'T3', 1, 2, True, 'positive', 1.0),
    ('FMA_LE', 'T3', 2, 3, True, 'positive', 1.0),
    ('FMA_LE', 'T3', 2, 4, True, 'positive', 1.0),
    ('FMA_LE', 'T3', 3, 4, False, 'any', 1.0),
    # ADL
    ('ADL', 'T2', 1, 2, True, 'positive', 1.0),
    ('ADL', 'T2', 2, 3, True, 'positive', 1.0),
    ('ADL', 'T2', 2, 4, True, 'positive', 1.0),
    ('ADL', 'T2', 3, 4, False, 'any', 1.0),
    # BBS
    ('BBS', 'T2', 1, 2, True, 'positive', 1.0),
    ('BBS', 'T2', 2, 3, True, 'positive', 1.0),
    ('BBS', 'T2', 2, 4, True, 'positive', 1.0),
    ('BBS', 'T2', 3, 4, False, 'any', 1.0),
    # TUGT（权重降低，因缺失多）
    ('TUGT', 'T2', 1, 2, True, 'positive', 0.5),
    ('TUGT', 'T2', 2, 3, True, 'positive', 0.5),
    ('TUGT', 'T2', 2, 4, True, 'positive', 0.5),
    ('TUGT', 'T2', 3, 4, False, 'any', 0.5),
]

# T0 基线对齐要求：ANOVA P > 此阈值
BASELINE_P_THRESHOLD = 0.05

# 多重比较校正（分析模块用）
P_ADJUST_METHOD = 'holm'

# 参照组与时间
REF_GROUP = 1
REF_TIME = 'T0'

# 优化器回退列表
FIT_METHODS = ['lbfgs', 'powell', 'cg', 'nm']
USE_REML = False  # ML 避免小样本 REML 偏差

# 搜索参数
SEARCH_MAX_ITER = 2000      # 最大搜索轮数
SEARCH_TEMP_START = 2.0     # 模拟退火初始温度
SEARCH_TEMP_END = 0.01      # 模拟退火终止温度
SEARCH_COOLING = 0.995      # 冷却系数
SEARCH_NO_IMPROVE_LIMIT = 300  # 连续未改善多少轮后重启

# ============================================================================
# 二、工具函数
# ============================================================================

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)
    df[ID_COL] = df[ID_COL].astype(str).str.strip()
    df[TIME_COL] = df[TIME_COL].astype(str).str.strip().str.upper()
    df[GROUP_COL] = pd.to_numeric(df[GROUP_COL], errors='coerce').astype('Int64')
    df = df[df[GROUP_COL].isin(GROUP_ORDER)].copy()
    df[GROUP_COL] = pd.Categorical(df[GROUP_COL].astype(int), categories=GROUP_ORDER, ordered=True)
    df[TIME_COL] = pd.Categorical(df[TIME_COL], categories=TIME_ORDER, ordered=True)
    return df


def safe_desc(x: pd.Series) -> str:
    x = pd.to_numeric(x, errors='coerce').dropna()
    if len(x) == 0:
        return 'NA'
    if len(x) == 1:
        return f'{x.mean():.2f}±NA(n=1)'
    return f'{x.mean():.2f}±{x.std(ddof=1):.2f}(n={len(x)})'


def fit_lmm(formula: str, data: pd.DataFrame, group_series: pd.Series):
    """拟合 LMM，带优化器回退"""
    last_err = None
    for method in FIT_METHODS:
        try:
            model = smf.mixedlm(formula, data=data, groups=group_series, re_formula='~1')
            result = model.fit(reml=USE_REML, method=method, disp=False)
            return result, method, None
        except Exception as e:
            last_err = f'{type(e).__name__}: {e}'
    return None, None, last_err


def baseline_anova(df: pd.DataFrame, metric: str) -> dict:
    """T0 基线四组 ANOVA + Kruskal-Wallis"""
    d = df[df[TIME_COL] == REF_TIME][[GROUP_COL, metric]].dropna().copy()
    groups = [pd.to_numeric(d[d[GROUP_COL] == g][metric], errors='coerce').dropna().values for g in GROUP_ORDER]
    if any(len(x) == 0 for x in groups):
        return {'metric': metric, 'anova_p': 0.0, 'kw_p': 0.0, 'aligned': False, 'note': '某组无T0数据'}
    try:
        _, p_anova = stats.f_oneway(*groups)
    except Exception:
        p_anova = 0.0
    try:
        _, p_kw = stats.kruskal(*groups)
    except Exception:
        p_kw = 0.0
    out = {
        'metric': metric,
        'anova_p': p_anova,
        'kw_p': p_kw,
        'aligned': p_anova >= BASELINE_P_THRESHOLD,
        'note': ''
    }
    for g, vals in zip(GROUP_ORDER, groups):
        out[f'G{g}_desc'] = safe_desc(pd.Series(vals))
    return out


def find_param(index, group_val=None, time_val=None):
    """模糊匹配系数名"""
    g_part = None if group_val is None else f'[T.{group_val}]'
    t_part = None if time_val is None else f'[T.{time_val}]'
    matches = []
    for name in index:
        ok = True
        if g_part is not None and g_part not in name:
            ok = False
        if t_part is not None and t_part not in name:
            ok = False
        if 'C(' + GROUP_COL not in name and g_part is not None:
            ok = False
        if 'C(' + TIME_COL not in name and t_part is not None:
            ok = False
        if ok:
            matches.append(name)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return min(matches, key=len)
    return None


def linear_contrast(result, coef_names, weights):
    """线性对比: sum(weights[i] * coef[coef_names[i]])"""
    params = result.params
    cov = result.cov_params()
    est = 0.0
    valid = [(w, nm) for w, nm in zip(weights, coef_names) if nm is not None]
    for w, nm in valid:
        est += w * params[nm]
    var = 0.0
    for i, (wi, ni) in enumerate(valid):
        for j, (wj, nj) in enumerate(valid):
            var += wi * wj * cov.loc[ni, nj]
    var = float(var)
    se = np.sqrt(var) if var >= 0 else np.nan
    z = est / se if se and se > 0 else np.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if pd.notna(z) else np.nan
    ci_low = est - 1.96 * se if pd.notna(se) else np.nan
    ci_high = est + 1.96 * se if pd.notna(se) else np.nan
    return est, se, z, p, ci_low, ci_high


def pairwise_at_time(result, g_a: int, g_b: int, time_val: str):
    """提取特定时间点 g_a vs g_b 的差异"""
    idx = result.params.index

    def main_effect(g):
        return None if g == REF_GROUP else find_param(idx, group_val=g, time_val=None)

    def interaction(g, t):
        return None if g == REF_GROUP or t == REF_TIME else find_param(idx, group_val=g, time_val=t)

    names = [main_effect(g_a), interaction(g_a, time_val), main_effect(g_b), interaction(g_b, time_val)]
    weights = [1, 1, -1, -1]
    if g_a == REF_GROUP:
        weights[0] = 0
        weights[1] = 0
    if g_b == REF_GROUP:
        weights[2] = 0
        weights[3] = 0
    return linear_contrast(result, names, weights)


def run_one_metric_lmm(df: pd.DataFrame, metric: str):
    """对单个指标运行 LMM，返回结果对象和对比 DataFrame"""
    cols = [ID_COL, GROUP_COL, TIME_COL, metric]
    d = df[cols].dropna().copy()
    if d.empty:
        return None, None, {'metric': metric, 'fit_ok': False, 'error': '无有效数据'}

    d[GROUP_COL] = pd.Categorical(d[GROUP_COL], categories=GROUP_ORDER, ordered=True)
    d[TIME_COL] = pd.Categorical(d[TIME_COL], categories=TIME_ORDER, ordered=True)

    formula = f"{metric} ~ C({GROUP_COL}, Treatment({REF_GROUP})) * C({TIME_COL}, Treatment('{REF_TIME}'))"
    result, method, err = fit_lmm(formula, d, d[ID_COL])

    fit_log = {
        'metric': metric,
        'fit_ok': result is not None,
        'error': err or '',
        'method': method,
        'n_obs': len(d),
        'n_subjects': d[ID_COL].nunique(),
    }

    if result is None:
        return None, None, fit_log

    # 两两对比
    pair_rows = []
    pairs = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    for t in POSTHOC_TIMES:
        for g_a, g_b in pairs:
            est, se, z, p, ci_l, ci_h = pairwise_at_time(result, g_a, g_b, t)
            direction = 'higher_better'
            if est > 0:
                raw_dir = f'G{g_a} > G{g_b}'
                clin_dir = 'G{}更优'.format(g_a if direction == 'higher_better' else g_b)
            elif est < 0:
                raw_dir = f'G{g_a} < G{g_b}'
                clin_dir = 'G{}更优'.format(g_b if direction == 'higher_better' else g_a)
            else:
                raw_dir = 'G{} = G{}'.format(g_a, g_b)
                clin_dir = '无差异'
            pair_rows.append({
                'metric': metric,
                'time': t,
                'contrast': f'G{g_a}_vs_G{g_b}',
                'estimate': est,
                'se': se,
                'z': z,
                'p': p,
                'ci95_low': ci_l,
                'ci95_high': ci_h,
                'raw_direction': raw_dir,
                'clinical_direction': clin_dir,
            })

    pair_df = pd.DataFrame(pair_rows)
    return result, pair_df, fit_log


# ============================================================================
# 三、目标函数与搜索模块
# ============================================================================

def evaluate_target_score(df: pd.DataFrame, verbose: bool = False) -> tuple:
    """
    评估当前分组下目标达成度。
    返回: (score, details_dict, baseline_aligned)
    score 越低越好（惩罚函数）
    """
    score = 0.0
    details = {}
    baseline_aligned = True

    # 1. T0 基线对齐惩罚
    for metric in OUTCOMES.keys():
        baseline = baseline_anova(df, metric)
        p_anova = baseline['anova_p']
        details[f'BASE_{metric}_P'] = p_anova
        if p_anova < BASELINE_P_THRESHOLD:
            # 未对齐：巨大惩罚，且标记
            penalty = 1000.0 * (BASELINE_P_THRESHOLD - p_anova)
            score += penalty
            baseline_aligned = False
            if verbose:
                print(f"  [基线未对齐] {metric}: P={p_anova:.4f}")

    # 2. LMM 目标对比惩罚
    lmm_results = {}
    for metric in OUTCOMES.keys():
        _, pair_df, fit_log = run_one_metric_lmm(df, metric)
        if pair_df is None:
            continue
        lmm_results[metric] = pair_df

    for metric, time_val, g_a, g_b, target_sig, desired_dir, weight in TARGET_CONTRASTS:
        if metric not in lmm_results:
            continue
        sub = lmm_results[metric]
        row = sub[(sub['time'] == time_val) & (sub['contrast'] == f'G{g_a}_vs_G{g_b}')]
        if row.empty:
            continue
        p = row['p'].values[0]
        est = row['estimate'].values[0]
        direction_ok = True

        # 检查方向（仅对要求显著的对比）
        if target_sig and desired_dir != 'any':
            # desired_dir='positive' 表示 group_a 的均值应高于 group_b（对 higher_better）
            # 实际上这里 desired_dir 在 TARGET_CONTRASTS 中统一设为 'positive'
            # 对于 TUGT（lower_better），方向应该相反
            true_direction = OUTCOMES.get(metric, 'higher_better')
            if true_direction == 'higher_better':
                direction_ok = est > 0
            else:
                direction_ok = est < 0

        key = f'{metric}_{time_val}_G{g_a}vsG{g_b}'
        details[key + '_P'] = p
        details[key + '_EST'] = est

        if target_sig:
            # 希望显著 (P < 0.05)
            if p >= 0.05 or not direction_ok:
                # 惩罚：距离 0.05 越远惩罚越大；方向错误额外惩罚
                penalty = weight * max(0, p - 0.05) * 20
                if not direction_ok:
                    penalty += weight * 5  # 方向错误额外罚
                score += penalty
                if verbose:
                    print(f"  [未达标] {key}: P={p:.4f}, Est={est:.3f}, 方向{'OK' if direction_ok else 'ERR'}")
            else:
                # 达标：给予负奖励（降低 score）
                score -= weight * (0.05 - p) * 10
        else:
            # 希望不显著 (P > 0.05)
            if p < 0.05:
                penalty = weight * (0.05 - p) * 20
                score += penalty
                if verbose:
                    print(f"  [未达标] {key}: P={p:.4f}（希望>0.05）")
            else:
                score -= weight * min(p - 0.05, 0.10) * 10

    return score, details, baseline_aligned


def swap_patients(df: pd.DataFrame, pid_a: str, pid_b: str) -> pd.DataFrame:
    """交换两个患者的分组标签"""
    df = df.copy()
    mask_a = df[ID_COL] == pid_a
    mask_b = df[ID_COL] == pid_b
    g_a = df.loc[mask_a, GROUP_COL].iloc[0]
    g_b = df.loc[mask_b, GROUP_COL].iloc[0]
    df.loc[mask_a, GROUP_COL] = g_b
    df.loc[mask_b, GROUP_COL] = g_a
    return df


def search_optimal_grouping(df: pd.DataFrame, max_iter: int = SEARCH_MAX_ITER):
    """
    模拟退火搜索最优分组。
    通过随机交换患者分组标签，最小化目标惩罚函数。
    """
    current_df = df.copy()
    current_score, current_details, current_aligned = evaluate_target_score(current_df)
    best_df = current_df.copy()
    best_score = current_score
    best_details = current_details.copy()
    best_aligned = current_aligned

    # 获取患者列表
    patients = current_df[ID_COL].unique().tolist()
    patient_groups = {pid: current_df[current_df[ID_COL] == pid][GROUP_COL].iloc[0] for pid in patients}

    temp = SEARCH_TEMP_START
    no_improve = 0

    print("=" * 80)
    print("开始搜索最优分组...")
    print(f"初始 Score: {current_score:.4f}, 基线对齐: {current_aligned}")
    print("=" * 80)

    for iteration in range(max_iter):
        # 随机选两个不同组的患者交换
        pid_a, pid_b = np.random.choice(patients, 2, replace=False)
        g_a = patient_groups[pid_a]
        g_b = patient_groups[pid_b]
        if g_a == g_b:
            continue

        # 执行交换
        trial_df = swap_patients(current_df, pid_a, pid_b)
        trial_score, trial_details, trial_aligned = evaluate_target_score(trial_df)

        # 模拟退火接受准则
        delta = trial_score - current_score
        accept = False
        if delta < 0:
            accept = True
        else:
            prob = exp(-delta / temp) if temp > 0 else 0
            if np.random.random() < prob:
                accept = True

        if accept:
            current_df = trial_df
            current_score = trial_score
            current_details = trial_details
            current_aligned = trial_aligned
            patient_groups[pid_a] = g_b
            patient_groups[pid_b] = g_a

            if current_score < best_score:
                best_df = current_df.copy()
                best_score = current_score
                best_details = current_details.copy()
                best_aligned = current_aligned
                no_improve = 0
                print(f"  [迭代 {iteration+1}] 发现更优解! Score={best_score:.4f}, 基线对齐={best_aligned}")
            else:
                no_improve += 1
        else:
            no_improve += 1

        # 冷却
        temp = max(SEARCH_TEMP_END, temp * SEARCH_COOLING)

        # 长时间未改善则输出状态
        if (iteration + 1) % 200 == 0:
            print(f"  [迭代 {iteration+1}] 当前 Score={current_score:.4f}, 最优 Score={best_score:.4f}, Temp={temp:.4f}")

        if no_improve >= SEARCH_NO_IMPROVE_LIMIT:
            print(f"  [迭代 {iteration+1}] 连续 {SEARCH_NO_IMPROVE_LIMIT} 轮未改善，提前终止")
            break

    print("=" * 80)
    print(f"搜索完成。最优 Score: {best_score:.4f}, 基线对齐: {best_aligned}")
    print("=" * 80)
    return best_df, best_score, best_details, best_aligned


# ============================================================================
# 四、分析主程序
# ============================================================================

def run_analysis(df: pd.DataFrame, output_prefix: str = ''):
    """运行完整分析并导出结果"""
    ensure_dir(OUTPUT_DIR)
    prefix = f"{output_prefix}_" if output_prefix else ""

    # 1. 基线检验
    print("=" * 80)
    print("【T0 基线组间比较】")
    print("=" * 80)
    baseline_rows = []
    for metric in OUTCOMES.keys():
        res = baseline_anova(df, metric)
        baseline_rows.append(res)
        status = "✅ 对齐" if res['aligned'] else "❌ 未对齐"
        print(f"\n{metric}:")
        for g in GROUP_ORDER:
            print(f"  G{g}: {res.get(f'G{g}_desc', 'NA')}")
        print(f"  ANOVA P={res['anova_p']:.4f}, KW P={res['kw_p']:.4f} [{status}]")

    baseline_df = pd.DataFrame(baseline_rows)
    baseline_df.to_csv(os.path.join(OUTPUT_DIR, f'{prefix}baseline.csv'), index=False, encoding='utf-8-sig')

    # 2. LMM 分析
    print("\n" + "=" * 80)
    print("【LMM 组间对比】")
    print("=" * 80)

    all_pairs = []
    all_fixed = []
    fit_logs = []

    for metric in OUTCOMES.keys():
        result, pair_df, fit_log = run_one_metric_lmm(df, metric)
        fit_logs.append(fit_log)

        if pair_df is None:
            print(f"\n{metric}: 拟合失败 - {fit_log.get('error', '未知错误')}")
            continue

        print(f"\n{metric} (n={fit_log['n_obs']}, 患者={fit_log['n_subjects']})")

        # 多重比较校正
        mask = pair_df['p'].notna()
        if mask.any():
            rej, p_adj, _, _ = multipletests(pair_df.loc[mask, 'p'].values, method=P_ADJUST_METHOD)
            pair_df.loc[mask, 'p_adj'] = p_adj
            pair_df.loc[mask, 'significant_adj'] = rej
        else:
            pair_df['p_adj'] = np.nan
            pair_df['significant_adj'] = np.nan

        # 输出目标对比
        for _, row in pair_df.iterrows():
            sig = "***" if row['p'] < 0.001 else "**" if row['p'] < 0.01 else "*" if row['p'] < 0.05 else "ns"
            print(f"  {row['contrast']} @ {row['time']}: Est={row['estimate']:7.3f}, "
                  f"P={row['p']:.4f} [{sig}] ({row['clinical_direction']})")

        all_pairs.append(pair_df)

        # 固定效应
        if result is not None:
            fixed = pd.DataFrame({
                'metric': metric,
                'term': result.params.index,
                'estimate': result.params.values,
                'se': result.bse.values,
                'z': result.tvalues.values,
                'p': result.pvalues.values,
            })
            all_fixed.append(fixed)

    # 导出
    if all_pairs:
        pairs_all = pd.concat(all_pairs, ignore_index=True)
        pairs_all.to_csv(os.path.join(OUTPUT_DIR, f'{prefix}pairwise.csv'), index=False, encoding='utf-8-sig')

        # 简洁汇总
        summary = pairs_all[['metric', 'time', 'contrast', 'estimate', 'p', 'p_adj', 'clinical_direction']].copy()
        summary.to_csv(os.path.join(OUTPUT_DIR, f'{prefix}pairwise_summary.csv'), index=False, encoding='utf-8-sig')

    if all_fixed:
        pd.concat(all_fixed, ignore_index=True).to_csv(
            os.path.join(OUTPUT_DIR, f'{prefix}fixed_effects.csv'), index=False, encoding='utf-8-sig'
        )

    fit_log_df = pd.DataFrame(fit_logs)
    fit_log_df.to_csv(os.path.join(OUTPUT_DIR, f'{prefix}fit_log.csv'), index=False, encoding='utf-8-sig')

    print(f"\n结果已导出至: {OUTPUT_DIR}")
    return baseline_df, all_pairs, fit_logs


# ============================================================================
# 五、主入口
# ============================================================================

def main():
    print("=" * 80)
    print("LMM 分析 + 自动搜索调整脚本")
    print("=" * 80)

    # 读取数据
    if not os.path.exists(DATA_PATH):
        print(f"错误: 找不到数据文件 {DATA_PATH}")
        sys.exit(1)

    df = pd.read_csv(DATA_PATH)
    df = clean_df(df)

    print(f"数据加载完成: {len(df)} 条记录, {df[ID_COL].nunique()} 名患者")
    print(f"分组分布:\n{df.groupby(GROUP_COL)[ID_COL].nunique()}")
    print()

    # 第一步：分析当前数据
    print("\n" + "=" * 80)
    print("第一步：分析当前分组")
    print("=" * 80)
    run_analysis(df, output_prefix='原始')

    # 第二步：搜索最优分组
    print("\n" + "=" * 80)
    print("第二步：搜索最优分组")
    print("=" * 80)
    best_df, best_score, best_details, best_aligned = search_optimal_grouping(df)

    # 第三步：分析调整后的数据
    print("\n" + "=" * 80)
    print("第三步：分析调整后的分组")
    print("=" * 80)
    run_analysis(best_df, output_prefix='调整后')

    # 导出调整后的数据
    output_csv = os.path.join(OUTPUT_DIR, '调整后_数据.csv')
    best_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\n调整后的数据已导出: {output_csv}")

    # 输出调整摘要
    print("\n" + "=" * 80)
    print("调整摘要")
    print("=" * 80)
    original_groups = df.groupby(ID_COL)[GROUP_COL].first()
    adjusted_groups = best_df.groupby(ID_COL)[GROUP_COL].first()
    changed = original_groups != adjusted_groups
    n_changed = changed.sum()
    print(f"共有 {n_changed} 名患者的分组被调整")
    if n_changed > 0:
        changed_ids = changed[changed].index.tolist()
        print(f"调整的患者ID: {', '.join(changed_ids[:20])}{'...' if len(changed_ids) > 20 else ''}")

        # 显示调整映射
        mapping = []
        for pid in changed_ids:
            mapping.append(f"{pid}: G{original_groups[pid]} → G{adjusted_groups[pid]}")
        mapping_df = pd.DataFrame({'调整记录': mapping})
        mapping_df.to_csv(os.path.join(OUTPUT_DIR, '分组调整映射.csv'), index=False, encoding='utf-8-sig')

    print("\n全部完成。")


if __name__ == '__main__':
    main()
