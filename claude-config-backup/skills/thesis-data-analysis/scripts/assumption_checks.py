#!/usr/bin/env python3
"""
前提假设检查脚本 - 用于论文数据分析的自动化前提检验

包含：
- 正态性检验（Shapiro-Wilk / D'Agostino-Pearson / Q-Q图）
- 方差齐性检验（Bartlett / Levene）
- 样本量评估
- 异常值检测（Z-score / IQR）
- 重复测量球形检验（Mauchly's Test）

使用方法：
    from assumption_checks import *
    report = run_all_checks(groups=[group1, group2], group_names=["实验组", "对照组"])

依赖包：
    pip install numpy scipy matplotlib statsmodels pingouin
"""

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────
# 可选依赖：延迟检查，避免 import 时打印警告
# ─────────────────────────────────────────────
def _check_statsmodels():
    try:
        import statsmodels.api as sm
        return sm
    except ImportError:
        print("⚠️  statsmodels 未安装，Q-Q 图不可用。运行：pip install statsmodels")
        return None


def _check_pingouin():
    try:
        import pingouin as pg
        return pg
    except ImportError:
        print("⚠️  pingouin 未安装，球形检验不可用。运行：pip install pingouin")
        return None


# ─────────────────────────────────────────────
# 函数 1：正态性检验
# ─────────────────────────────────────────────
def normality_check(data, group_name=""):
    """
    正态性检验（自动选择方法 + Q-Q 图）

    参数:
        data       : array-like，待检验数据
        group_name : str，组名（用于输出标识）

    返回:
        is_normal   : bool，是否近似正态
        result_dict : dict，详细检验结果
    """
    data = np.asarray(data, dtype=float)
    n = len(data)

    print(f"\n{'='*40}")
    print(f"正态性检验：{group_name}（n={n}）")
    print(f"{'='*40}")

    result = {
        "n": n,
        "group_name": group_name,
        "skewness": None,
        "kurtosis": None,
        "shapiro_stat": None,
        "shapiro_p": None,
        "dagostino_stat": None,
        "dagostino_p": None,
        "main_p": None,
        "is_normal": None,
        "warning": None,
    }

    # 偏度 / 峰度参考
    sk = float(stats.skew(data))
    kurt = float(stats.kurtosis(data))
    result["skewness"] = sk
    result["kurtosis"] = kurt
    print(f"偏度={sk:.4f}，峰度={kurt:.4f}")

    # Shapiro-Wilk（始终执行，n<50 时作为主判断依据）
    sw_stat, sw_p = stats.shapiro(data)
    result["shapiro_stat"] = float(sw_stat)
    result["shapiro_p"] = float(sw_p)
    print(f"Shapiro-Wilk      : stat={sw_stat:.4f}, p={sw_p:.4f}")

    # D'Agostino-Pearson（n>=8 才可运行；n>=50 时作为主判断依据）
    if n >= 8:
        da_stat, da_p = stats.normaltest(data)
        result["dagostino_stat"] = float(da_stat)
        result["dagostino_p"] = float(da_p)
        print(f"D'Agostino-Pearson: stat={da_stat:.4f}, p={da_p:.4f}")
        main_p = float(sw_p) if n < 50 else float(da_p)
    else:
        print("D'Agostino-Pearson: n<8，跳过，仅参考 Shapiro-Wilk")
        main_p = float(sw_p)

    result["main_p"] = main_p

    # 大样本过敏感性警告
    if n > 100 and main_p <= 0.05:
        msg = ("大样本(n>100)警告：p≤0.05 可能因统计功效过高所致，"
               "请结合 Q-Q 图与偏度/峰度综合判断，不可机械依赖 p 值")
        result["warning"] = msg
        print(f"⚠️  {msg}")

    # Q-Q 图
    sm = _check_statsmodels()
    if sm is not None:
        fig, ax = plt.subplots(figsize=(6, 5))
        sm.qqplot(data, line="s", ax=ax)
        ax.set_title(f"{group_name} Q-Q 图（n={n}）")
        plt.tight_layout()
        plt.show()
    else:
        print("⚠️  Q-Q 图未生成（statsmodels 未安装）")

    is_normal = main_p > 0.05
    result["is_normal"] = is_normal
    print(f"结论：{'✅ 近似正态' if is_normal else '❌ 偏离正态 → 建议非参数方法'}")

    return is_normal, result


# ─────────────────────────────────────────────
# 函数 2：方差齐性检验
# ─────────────────────────────────────────────
def homogeneity_check(groups, groups_normal=None, group_names=None):
    """
    方差齐性检验（根据正态性自动选择 Bartlett / Levene）

    参数:
        groups        : list of array-like，各组数据
        groups_normal : list of bool or None，各组正态性结果
        group_names   : list of str or None，各组名称

    返回:
        is_homogeneous : bool，是否方差齐
        result_dict    : dict，详细检验结果
    """
    print(f"\n{'='*40}")
    print("方差齐性检验")
    print(f"{'='*40}")

    names = group_names or [f"Group{i+1}" for i in range(len(groups))]
    groups = [np.asarray(g, dtype=float) for g in groups]

    for name, g in zip(names, groups):
        print(f"  {name}: n={len(g)}, mean={np.mean(g):.4f}, std={np.std(g, ddof=1):.4f}")

    use_bartlett = (groups_normal is not None) and all(groups_normal)

    if use_bartlett:
        stat, p = stats.bartlett(*groups)
        method = "Bartlett（各组均正态，功效更高）"
    else:
        stat, p = stats.levene(*groups)
        method = "Levene（存在非正态或正态性未知，更稳健）"

    print(f"方法：{method}")
    print(f"stat={stat:.4f}, p={p:.4f}")

    is_homogeneous = p > 0.05
    print(f"结论：{'✅ 方差齐，可用标准参数检验' if is_homogeneous else '❌ 方差不齐 → 建议 Welch 校正或非参数方法'}")

    result = {
        "method": method,
        "stat": float(stat),
        "p": float(p),
        "is_homogeneous": is_homogeneous,
    }

    return is_homogeneous, result


# ─────────────────────────────────────────────
# 函数 3：样本量评估
# ─────────────────────────────────────────────
def sample_size_check(groups):
    """
    样本量评估，返回风险等级

    参数:
        groups : list of array-like，各组数据

    返回:
        risk_level  : str，'critical' / 'small' / 'adequate'
        result_dict : dict，详细样本量信息
    """
    print(f"\n{'='*40}")
    print("样本量评估")
    print(f"{'='*40}")

    sizes = [len(g) for g in groups]
    min_n = min(sizes)
    total_n = sum(sizes)

    print(f"各组样本量：{sizes}，最小组 n={min_n}，总 N={total_n}")

    if min_n < 5:
        print("🚨 样本量极小（每组 n<5）：结果仅供探索性参考，强烈建议非参数方法")
        risk_level = "critical"
    elif total_n < 20 or min_n < 30:
        print("⚠️  样本量偏小（总 N<20 或最小组 n<30）：参数检验结果需谨慎解释")
        risk_level = "small"
    else:
        print("✅ 样本量充足")
        risk_level = "adequate"

    result = {
        "group_sizes": sizes,
        "min_n": min_n,
        "total_n": total_n,
        "risk_level": risk_level,
    }

    return risk_level, result


# ─────────────────────────────────────────────
# 函数 4：异常值检测
# ─────────────────────────────────────────────
def outlier_check(data, threshold_pct=0.05, label=""):
    """
    异常值检测（Z-score + IQR，输出格式统一）

    参数:
        data          : array-like，待检测数据
        threshold_pct : float，触发阻断的异常值比例阈值（默认 5%）
        label         : str，组名标识（用于输出）

    返回:
        outlier_dict : dict，{'indices': [...], 'values': [...]}
        result_dict  : dict，详细检测结果
    """
    data = np.asarray(data, dtype=float)

    print(f"\n{'='*40}")
    print(f"异常值检测：{label}（n={len(data)}）")
    print(f"{'='*40}")

    # Z-score 方法（ddof=1，样本标准差，小样本更准确）
    z_scores = np.abs(stats.zscore(data, ddof=1))
    z_idx = np.where(z_scores > 3)[0]
    print(f"Z-score (>3, ddof=1) → 索引: {z_idx.tolist()}, 值: {data[z_idx].tolist()}")

    # IQR 方法（IQR=0 时跳过，避免误报）
    Q1, Q3 = np.percentile(data, [25, 75])
    IQR = Q3 - Q1

    if IQR == 0:
        print("⚠️  IQR=0（数据高度集中或含大量重复值），IQR 方法不适用，跳过")
        iqr_idx = np.array([], dtype=int)
    else:
        iqr_mask = (data < Q1 - 1.5 * IQR) | (data > Q3 + 1.5 * IQR)
        iqr_idx = np.where(iqr_mask)[0]

    print(f"IQR (×1.5)           → 索引: {iqr_idx.tolist()}, 值: {data[iqr_idx].tolist()}")

    all_outlier_idx = sorted(set(z_idx.tolist() + iqr_idx.tolist()))
    pct = len(all_outlier_idx) / len(data)
    print(f"异常值总计：{len(all_outlier_idx)} 个 / {len(data)} 个 ({pct*100:.1f}%)")

    if len(all_outlier_idx) > 0:
        if pct > threshold_pct:
            print(f"🚨 异常值比例 > {threshold_pct*100:.0f}%，强制返回阶段3处理，用户确认前禁止继续")
        else:
            print("⚠️  存在少量异常值，建议人工核查后确认是否继续")
    else:
        print("✅ 未检测到异常值")

    outlier_dict = {
        "indices": all_outlier_idx,
        "values": [float(v) for v in data[all_outlier_idx]],
    }

    result = {
        "label": label,
        "z_outliers": {
            "indices": z_idx.tolist(),
            "values": [float(v) for v in data[z_idx]],
        },
        "iqr_outliers": {
            "indices": iqr_idx.tolist(),
            "values": [float(v) for v in data[iqr_idx]],
        },
        "combined": outlier_dict,
        "count": len(all_outlier_idx),
        "percentage": float(pct),
        "block_required": pct > threshold_pct,
    }

    return outlier_dict, result


# ─────────────────────────────────────────────
# 函数 5：球形假设检验
# ─────────────────────────────────────────────
def sphericity_check(data_long, dv="value", within="time", subject="id"):
    """
    重复测量球形假设检验（3+ 时间点时执行）

    参数:
        data_long : DataFrame，长格式数据
        dv        : str，因变量列名
        within    : str，组内因子列名（时间点）
        subject   : str，被试 ID 列名

    返回:
        is_spherical : bool or None
        result       : DataFrame or None
    """
    pg = _check_pingouin()
    if pg is None:
        print("   或手动检查各时间点间差值的方差是否近似相等")
        return None, None

    print(f"\n{'='*40}")
    print("球形假设检验（Mauchly's Test）")
    print(f"{'='*40}")

    result = pg.sphericity(data_long, dv=dv, within=within, subject=subject)
    print(result)

    p = result["p-unc"].iloc[0]
    is_spherical = p > 0.05
    print(f"结论：{'✅ 满足球形假设，可直接使用重复测量 ANOVA' if is_spherical else '❌ 违反球形假设 → 应用 Greenhouse-Geisser 或 Huynh-Feldt 校正'}")

    return is_spherical, result


# ─────────────────────────────────────────────
# 主函数：完整检查流程
# ─────────────────────────────────────────────
def run_all_checks(groups, group_names=None, is_repeated=False, data_long=None):
    """
    执行完整前提假设检查流程（阶段 4）

    执行顺序：样本量 → 正态性 → 方差齐性 → 异常值 → 球形（重复测量时）

    参数:
        groups      : list of array-like，各组数据
        group_names : list of str or None，各组名称
        is_repeated : bool，是否为重复测量设计
        data_long   : DataFrame or None，长格式数据（重复测量时必须提供）

    返回:
        final_report : dict，完整检查结果汇总
    """
    groups = [np.asarray(g, dtype=float) for g in groups]
    names = group_names or [f"Group{i+1}" for i in range(len(groups))]

    # ── 步骤 1：样本量评估（优先，决定后续流程）──
    print("\n" + "="*50)
    print("【步骤 1】样本量评估")
    print("="*50)
    risk_level, sample_result = sample_size_check(groups)

    # ── 步骤 2：正态性检验（样本量极小时直接跳过）──
    print("\n" + "="*50)
    print("【步骤 2】正态性检验")
    print("="*50)

    groups_normal = []
    normality_results = []

    if risk_level == "critical":
        print("🚨 样本量极小（每组 n<5），跳过正态性检验，直接标记为非正态")
        groups_normal = [False] * len(groups)
        normality_results = [
            {"group_name": n, "is_normal": False, "warning": "样本量过小，跳过"}
            for n in names
        ]
    else:
        for name, grp in zip(names, groups):
            is_normal, res = normality_check(grp, name)
            groups_normal.append(is_normal)
            normality_results.append(res)

    # ── 步骤 3：方差齐性检验（两组及以上）──
    print("\n" + "="*50)
    print("【步骤 3】方差齐性检验")
    print("="*50)

    if len(groups) >= 2:
        is_homogeneous, homogeneity_result = homogeneity_check(
            groups, groups_normal, names
        )
    else:
        print("仅单组数据，跳过方差齐性检验")
        is_homogeneous = True
        homogeneity_result = None

    # ── 步骤 4：异常值复核（逐组检测，分别记录）──
    print("\n" + "="*50)
    print("【步骤 4】异常值复核")
    print("="*50)

    outlier_by_group = {}
    total_outliers = 0
    total_n = sum(len(g) for g in groups)
    block_required = False

    for name, grp in zip(names, groups):
        _, res = outlier_check(grp, label=name)
        outlier_by_group[name] = res
        total_outliers += res["count"]
        block_required = block_required or res["block_required"]

    overall_pct = total_outliers / total_n if total_n > 0 else 0.0
    outlier_summary = {
        "per_group": outlier_by_group,
        "total_count": total_outliers,
        "total_percentage": overall_pct,
        "block_required": block_required,
    }

    # ── 步骤 5：球形假设（重复测量且 3+ 时间点）──
    sphericity_result = None
    if is_repeated and data_long is not None:
        times = data_long["time"].nunique() if "time" in data_long.columns else 0
        if times >= 3:
            print("\n" + "="*50)
            print("【步骤 5】球形假设检验")
            print("="*50)
            _, sphericity_result = sphericity_check(data_long)
        else:
            print(f"\n⚠️  时间点数={times} < 3，无需球形检验")

    # ── 汇总报告 ──
    can_proceed = (
        all(groups_normal)
        and is_homogeneous
        and risk_level != "critical"
        and not block_required
    )

    final_report = {
        "sample_size": sample_result,
        "normality": {
            "all_normal": all(groups_normal),
            "per_group": normality_results,
        },
        "homogeneity": homogeneity_result,
        "outliers": outlier_summary,
        "sphericity": sphericity_result,
        "can_proceed": can_proceed,
    }

    print("\n" + "="*50)
    print("【检查完成】汇总")
    print("="*50)
    print(f"样本量风险等级  : {risk_level}")
    print(f"正态性          : {'✅ 全部满足' if all(groups_normal) else '❌ 部分不满足'}")
    print(f"方差齐性        : {'✅ 满足' if is_homogeneous else '❌ 不满足'}")
    print(f"异常值          : {total_outliers} 个 ({overall_pct*100:.1f}%) | 阻断={block_required}")
    print("-"*50)
    if can_proceed:
        print("✅ 前提假设检查通过，可继续参数检验")
    else:
        print("❌ 存在前提不满足项，请参考上述提示选择替代方法")

    return final_report


# ─────────────────────────────────────────────
# 示例用法
# ─────────────────────────────────────────────
if __name__ == "__main__":
    np.random.seed(42)
    group1 = np.random.normal(100, 15, 30)
    group2 = np.random.normal(105, 15, 30)

    report = run_all_checks(
        groups=[group1, group2],
        group_names=["实验组", "对照组"]
    )

    print("\n完整报告键：", list(report.keys()))
    print("可以继续参数检验：", report["can_proceed"])
