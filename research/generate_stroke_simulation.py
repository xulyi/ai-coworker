"""
脑卒中康复模拟数据生成器
基于 stroke_amulate skill 要求：
- 候选池 -> 硬约束审计 -> 两阶段筛选 -> 输出 Excel
"""
import numpy as np
import pandas as pd
from copy import deepcopy

np.random.seed(42)

# ============== 1. 目标参数映射 ==============
GROUPS = {
    "G1": "双侧真实",
    "G2": "患侧真实+健侧安慰剂",
    "G3": "双侧假刺激",
    "G4": "空白对照 (CT)",
}
TIMEPOINTS = ["T0", "T1", "T2", "T3"]
METRICS = ["FMA_LE", "ADL", "BBS", "TUGT", "MAS", "CSS"]

TARGETS = {
    # FMA_LE
    "FMA_LE": {
        "T0": {"G1": (12.4, 3.5), "G2": (13.8, 3.7), "G3": (11.5, 3.1), "G4": (12.7, 3.4)},
        "T1": {"G1": (15.1, 3.8), "G2": (15.6, 4.0), "G3": (12.4, 3.4), "G4": (13.5, 3.5)},
        "T2": {"G1": (18.5, 4.2), "G2": (17.2, 4.1), "G3": (13.8, 3.6), "G4": (14.2, 3.7)},
        "T3": {"G1": (19.8, 4.5), "G2": (18.4, 4.3), "G3": (15.0, 4.0), "G4": (15.8, 4.1)},
    },
    # ADL (MBI)
    "ADL": {
        "T0": {"G1": (48.5, 10.2), "G2": (51.2, 11.4), "G3": (47.8, 9.5), "G4": (52.1, 11.0)},
        "T1": {"G1": (54.2, 11.0), "G2": (55.4, 11.5), "G3": (49.5, 9.8), "G4": (54.0, 11.2)},
        "T2": {"G1": (61.5, 12.1), "G2": (58.5, 11.8), "G3": (51.2, 10.0), "G4": (55.8, 11.4)},
        "T3": {"G1": (63.5, 12.5), "G2": (60.5, 11.8), "G3": (53.4, 10.2), "G4": (57.6, 11.5)},
    },
    # BBS
    "BBS": {
        "T0": {"G1": (22.4, 6.1), "G2": (24.1, 6.5), "G3": (21.8, 5.8), "G4": (23.5, 6.2)},
        "T1": {"G1": (27.8, 6.5), "G2": (28.5, 6.8), "G3": (23.2, 6.0), "G4": (25.1, 6.4)},
        "T2": {"G1": (32.6, 7.1), "G2": (31.2, 7.0), "G3": (24.5, 6.2), "G4": (26.2, 6.6)},
        "T3": {"G1": (34.5, 7.5), "G2": (32.8, 7.2), "G3": (25.4, 6.4), "G4": (27.2, 6.8)},
    },
    # TUGT
    "TUGT": {
        "T0": {"G1": (58.4, 14.5), "G2": (55.2, 13.8), "G3": (61.5, 15.2), "G4": (57.8, 14.2)},
        "T1": {"G1": (51.2, 12.8), "G2": (49.8, 12.2), "G3": (59.4, 14.8), "G4": (55.5, 13.5)},
        "T2": {"G1": (44.5, 10.5), "G2": (45.8, 11.0), "G3": (58.0, 14.5), "G4": (54.2, 13.8)},
        "T3": {"G1": (42.5, 10.2), "G2": (44.0, 10.6), "G3": (56.5, 14.0), "G4": (52.8, 13.5)},
    },
    # MAS
    "MAS": {
        "T0": {"G1": (1.18, 0.32), "G2": (1.24, 0.34), "G3": (1.16, 0.31), "G4": (1.21, 0.33)},
        "T1": {"G1": (1.12, 0.30), "G2": (1.17, 0.32), "G3": (1.32, 0.36), "G4": (1.30, 0.35)},
        "T2": {"G1": (0.85, 0.22), "G2": (1.05, 0.28), "G3": (1.72, 0.45), "G4": (1.65, 0.42)},
        "T3": {"G1": (0.92, 0.24), "G2": (1.22, 0.32), "G3": (1.85, 0.48), "G4": (1.78, 0.46)},
    },
    # CSS
    "CSS": {
        "T0": {"G1": (8.9, 1.4), "G2": (9.2, 1.6), "G3": (8.8, 1.5), "G4": (9.1, 1.6)},
        "T1": {"G1": (8.6, 1.3), "G2": (9.0, 1.5), "G3": (9.8, 1.7), "G4": (9.5, 1.6)},
        "T2": {"G1": (7.2, 1.2), "G2": (8.4, 1.4), "G3": (11.5, 1.8), "G4": (11.0, 1.7)},
        "T3": {"G1": (7.8, 1.4), "G2": (9.1, 1.5), "G3": (11.8, 1.9), "G4": (11.2, 1.8)},
    },
}

# ============== 2. 生成候选池 ==============

def generate_candidates(group_code, n_candidates=1500):
    """为一组生成 n_candidates 条患者轨迹"""
    # 个体潜变量
    u = np.random.normal(0, 1, n_candidates)  # 基础严重程度
    r = np.random.normal(0, 0.5, n_candidates)  # 恢复能力

    records = []

    for i in range(n_candidates):
        patient = {"patient_idx": i, "u": u[i], "r": r[i]}
        for t_idx, tp in enumerate(TIMEPOINTS):
            # 计算时间趋势因子（T0=0, T1=1, T2=2, T3=3）
            time_factor = t_idx

            # FMA_LE: 负向于 u，正向于 r
            mean_fma, sd_fma = TARGETS["FMA_LE"][tp][group_code]
            loading_fma = 0.55 * sd_fma
            recovery_fma = 0.3 * sd_fma
            noise_fma = np.random.normal(0, np.sqrt(max(0.01, sd_fma**2 - loading_fma**2 - recovery_fma**2)))
            fma = mean_fma - loading_fma * u[i] + recovery_fma * r[i] * time_factor + noise_fma

            # ADL
            mean_adl, sd_adl = TARGETS["ADL"][tp][group_code]
            loading_adl = 0.50 * sd_adl
            recovery_adl = 0.35 * sd_adl
            noise_adl = np.random.normal(0, np.sqrt(max(0.01, sd_adl**2 - loading_adl**2 - recovery_adl**2)))
            adl = mean_adl - loading_adl * u[i] + recovery_adl * r[i] * time_factor + noise_adl

            # BBS
            mean_bbs, sd_bbs = TARGETS["BBS"][tp][group_code]
            loading_bbs = 0.55 * sd_bbs
            recovery_bbs = 0.35 * sd_bbs
            noise_bbs = np.random.normal(0, np.sqrt(max(0.01, sd_bbs**2 - loading_bbs**2 - recovery_bbs**2)))
            bbs = mean_bbs - loading_bbs * u[i] + recovery_bbs * r[i] * time_factor + noise_bbs

            # TUGT (原始连续值)
            mean_tugt, sd_tugt = TARGETS["TUGT"][tp][group_code]
            loading_tugt = 0.50 * sd_tugt
            recovery_tugt = 0.30 * sd_tugt
            noise_tugt = np.random.normal(0, np.sqrt(max(0.01, sd_tugt**2 - loading_tugt**2 - recovery_tugt**2)))
            tugt_raw = mean_tugt + loading_tugt * u[i] - recovery_tugt * r[i] * time_factor + noise_tugt

            # MAS (原始连续值)
            mean_mas, sd_mas = TARGETS["MAS"][tp][group_code]
            loading_mas = 0.45 * sd_mas
            recovery_mas = 0.25 * sd_mas
            noise_mas = np.random.normal(0, np.sqrt(max(0.01, sd_mas**2 - loading_mas**2 - recovery_mas**2)))
            mas_raw = mean_mas + loading_mas * u[i] - recovery_mas * r[i] * time_factor + noise_mas

            # CSS (原始连续值)
            mean_css, sd_css = TARGETS["CSS"][tp][group_code]
            loading_css = 0.40 * sd_css
            recovery_css = 0.30 * sd_css
            noise_css = np.random.normal(0, np.sqrt(max(0.01, sd_css**2 - loading_css**2 - recovery_css**2)))
            css_raw = mean_css + loading_css * u[i] - recovery_css * r[i] * time_factor + noise_css

            patient[f"FMA_LE_{tp}"] = fma
            patient[f"ADL_{tp}"] = adl
            patient[f"BBS_{tp}"] = bbs
            patient[f"TUGT_raw_{tp}"] = tugt_raw
            patient[f"MAS_raw_{tp}"] = mas_raw
            patient[f"CSS_raw_{tp}"] = css_raw

        records.append(patient)

    df = pd.DataFrame(records)
    return df


def discretize_mas(df, group_code):
    """将 MAS 连续值映射到离散级别，并尽量保持均值/SD"""
    # MAS 离散级别
    mas_levels = np.array([0, 0.5, 1, 1.5, 2, 2.5, 3, 4])

    for tp in TIMEPOINTS:
        mean_mas, sd_mas = TARGETS["MAS"][tp][group_code]
        col_raw = f"MAS_raw_{tp}"
        col_out = f"MAS_{tp}"

        # 找到最近的两个离散级别 a < μ < b
        if mean_mas <= 0.25:
            a, b = 0, 0.5
        elif mean_mas >= 3.5:
            a, b = 3, 4
        else:
            # 找到包围 μ 的两个级别
            lower_idx = np.where(mas_levels < mean_mas)[0][-1]
            a = mas_levels[lower_idx]
            b = mas_levels[lower_idx + 1]

        # 基础概率
        if b == a:
            p_base = 0.5
        else:
            p_base = (mean_mas - a) / (b - a)
        p_base = np.clip(p_base, 0.05, 0.95)

        # 用 raw 值调整概率：raw 越高，取高值的概率越大
        raw_vals = df[col_raw].values
        # 将 raw 映射到 [-2, 2] 范围的 z-score
        z_raw = (raw_vals - mean_mas) / max(sd_mas, 0.01)
        p_individual = p_base + 0.15 * z_raw
        p_individual = np.clip(p_individual, 0.02, 0.98)

        # 抽取离散值
        rand = np.random.random(len(df))
        df[col_out] = np.where(rand < p_individual, b, a)

        # 做一次性均值微调：如果整体均值偏离 > 3%，用最接近的级别做 small swap
        actual_mean = df[col_out].mean()
        if actual_mean > mean_mas * 1.03 and b > a:
            # 需要降低均值：把一些 b 换成 a
            n_swap = int((actual_mean - mean_mas) / (b - a) * len(df))
            b_indices = df[df[col_out] == b].index
            if len(b_indices) > 0 and n_swap > 0:
                swap_idx = np.random.choice(b_indices, min(n_swap, len(b_indices)), replace=False)
                df.loc[swap_idx, col_out] = a
        elif actual_mean < mean_mas * 0.97 and b > a:
            # 需要升高均值
            n_swap = int((mean_mas - actual_mean) / (b - a) * len(df))
            a_indices = df[df[col_out] == a].index
            if len(a_indices) > 0 and n_swap > 0:
                swap_idx = np.random.choice(a_indices, min(n_swap, len(a_indices)), replace=False)
                df.loc[swap_idx, col_out] = b

    return df


def discretize_css(df, group_code):
    """CSS 四舍五入到整数"""
    for tp in TIMEPOINTS:
        col_raw = f"CSS_raw_{tp}"
        col_out = f"CSS_{tp}"
        df[col_out] = np.round(df[col_raw].values).astype(int)
        # 约束到合理范围 [0, 45]
        df[col_out] = df[col_out].clip(0, 45)
    return df


def assign_tugt(df):
    """根据 BBS 决定 TUGT 是 N/A 还是数值"""
    for tp in TIMEPOINTS:
        bbs_col = f"BBS_{tp}"
        tugt_raw_col = f"TUGT_raw_{tp}"
        tugt_col = f"TUGT_{tp}"

        bbs_vals = df[bbs_col].values
        tugt_vals = df[tugt_raw_col].values

        # BBS < 21 -> N/A
        # 否则保留数值（保留1位小数）
        tugt_assigned = np.where(bbs_vals < 21, "N/A", np.round(tugt_vals, 1))
        df[tugt_col] = tugt_assigned
    return df


# ============== 3. 硬约束审计 ==============

def audit_patient(row, group_code):
    """对单个患者轨迹进行审计，返回 (pass: bool, violations: list)"""
    violations = []

    # --- P0: T0 基线特异性生理约束 ---
    mas_t0 = row["MAS_T0"]
    css_t0 = row["CSS_T0"]
    if mas_t0 not in [1, 1.5, 2]:
        violations.append(f"P0-MAS_T0={mas_t0}")
    if css_t0 > 13:
        violations.append(f"P0-CSS_T0={css_t0}")

    # --- P1/P2/P3: 跨时点规则 ---
    for i, tp in enumerate(TIMEPOINTS):
        fma = row[f"FMA_LE_{tp}"]
        adl = row[f"ADL_{tp}"]
        bbs = row[f"BBS_{tp}"]
        tugt = row[f"TUGT_{tp}"]
        mas = row[f"MAS_{tp}"]

        # R3.1: BBS < 21 且 TUGT != N/A
        if bbs < 21 and tugt != "N/A":
            violations.append(f"R3.1-{tp}(BBS={bbs:.1f},TUGT={tugt})")

        # R3.2: 21 <= BBS <= 36 且 TUGT <= 35s
        if 21 <= bbs <= 36 and tugt != "N/A" and isinstance(tugt, (int, float, np.floating)) and tugt <= 35:
            violations.append(f"R3.2-{tp}(BBS={bbs:.1f},TUGT={tugt})")

        # R3.3: TUGT < 25 且 (FMA_LE < 21 或 BBS < 38 或 MAS > 2)
        if tugt != "N/A" and isinstance(tugt, (int, float, np.floating)) and tugt < 25:
            if fma < 21 or bbs < 38 or mas > 2:
                violations.append(f"R3.3-{tp}(TUGT={tugt},FMA={fma:.1f},BBS={bbs:.1f},MAS={mas})")

        # R3.4: FMA_LE <= 12 且 TUGT < 40
        if fma <= 12 and tugt != "N/A" and isinstance(tugt, (int, float, np.floating)) and tugt < 40:
            violations.append(f"R3.4-{tp}(FMA={fma:.1f},TUGT={tugt})")

        # R4.1: FMA_LE < 15 时，ADL 必须 <= 65
        if fma < 15 and adl > 65:
            violations.append(f"R4.1-{tp}(FMA={fma:.1f},ADL={adl:.1f})")

    # R4.3: FMA_LE >= 28 且 ADL >= 80 时，后续单周期 ΔADL <= 5
    for i in range(1, len(TIMEPOINTS)):
        prev_tp = TIMEPOINTS[i-1]
        curr_tp = TIMEPOINTS[i]
        if row[f"FMA_LE_{prev_tp}"] >= 28 and row[f"ADL_{prev_tp}"] >= 80:
            delta_adl = row[f"ADL_{curr_tp}"] - row[f"ADL_{prev_tp}"]
            if delta_adl > 5:
                violations.append(f"R4.3-{prev_tp}->{curr_tp}(ΔADL={delta_adl:.1f})")

    # --- P3: Delta Max ---
    for i in range(1, len(TIMEPOINTS)):
        prev_tp = TIMEPOINTS[i-1]
        curr_tp = TIMEPOINTS[i]

        delta_fma = row[f"FMA_LE_{curr_tp}"] - row[f"FMA_LE_{prev_tp}"]
        delta_bbs = row[f"BBS_{curr_tp}"] - row[f"BBS_{prev_tp}"]

        prev_tugt = row[f"TUGT_{prev_tp}"]
        curr_tugt = row[f"TUGT_{curr_tp}"]

        if delta_fma > 8:
            violations.append(f"P3-FMA-{prev_tp}->{curr_tp}(Δ={delta_fma:.1f})")
        if delta_bbs > 9:
            violations.append(f"P3-BBS-{prev_tp}->{curr_tp}(Δ={delta_bbs:.1f})")

        # TUGT 缩短幅度 > 15s（仅当两者都是数值时）
        if prev_tugt != "N/A" and curr_tugt != "N/A" and isinstance(prev_tugt, (int, float, np.floating)) and isinstance(curr_tugt, (int, float, np.floating)):
            tugt_drop = prev_tugt - curr_tugt
            if tugt_drop > 15:
                violations.append(f"P3-TUGT-{prev_tp}->{curr_tp}(drop={tugt_drop:.1f})")

    return len(violations) == 0, violations


def run_audit(df, group_code):
    """对 DataFrame 运行审计，返回通过的索引列表"""
    passed_indices = []
    for idx, row in df.iterrows():
        ok, _ = audit_patient(row, group_code)
        if ok:
            passed_indices.append(idx)
    return passed_indices


# ============== 4. 阶段 B 优化 ==============

def compute_stats(subset, group_code):
    """计算子集的实际统计量，返回 dict"""
    stats = {}
    for metric in METRICS:
        for tp in TIMEPOINTS:
            col = f"{metric}_{tp}"
            vals = subset[col]
            if metric == "TUGT":
                # 只统计数值型
                numeric_vals = pd.to_numeric(vals[vals != "N/A"], errors="coerce").dropna()
                if len(numeric_vals) > 0:
                    stats[(metric, tp, "mean")] = numeric_vals.mean()
                    stats[(metric, tp, "sd")] = numeric_vals.std(ddof=1) if len(numeric_vals) > 1 else 0
                else:
                    stats[(metric, tp, "mean")] = np.nan
                    stats[(metric, tp, "sd")] = np.nan
            else:
                numeric_vals = pd.to_numeric(vals, errors="coerce").dropna()
                stats[(metric, tp, "mean")] = numeric_vals.mean()
                stats[(metric, tp, "sd")] = numeric_vals.std(ddof=1) if len(numeric_vals) > 1 else 0
    return stats


def compute_loss(subset, group_code, w1=0.7, w2=0.15, w3=0.15):
    """计算损失函数"""
    stats = compute_stats(subset, group_code)
    mean_loss = 0
    sd_loss = 0
    n_metrics = 0

    for metric in METRICS:
        for tp in TIMEPOINTS:
            target_mean, target_sd = TARGETS[metric][tp][group_code]
            actual_mean = stats[(metric, tp, "mean")]
            actual_sd = stats[(metric, tp, "sd")]

            if np.isnan(actual_mean):
                continue

            n_metrics += 1
            mean_loss += abs(actual_mean - target_mean) / max(target_mean, 0.1)
            sd_loss += abs(actual_sd - target_sd) / max(target_sd, 0.1)

    if n_metrics > 0:
        mean_loss /= n_metrics
        sd_loss /= n_metrics

    # 叙事偏离分：检查 TUGT 中 N/A 的比例是否合理（BBS<21 的患者中）
    narrative_dev = 0
    for tp in TIMEPOINTS:
        bbs_col = f"BBS_{tp}"
        tugt_col = f"TUGT_{tp}"
        low_bbs = subset[subset[bbs_col] < 21]
        if len(low_bbs) > 0:
            na_count = (low_bbs[tugt_col] == "N/A").sum()
            na_rate = na_count / len(low_bbs)
            if na_rate < 0.95:
                narrative_dev += (0.95 - na_rate) * 0.5

    loss = w1 * mean_loss + w2 * sd_loss + w3 * narrative_dev
    return loss, mean_loss, sd_loss, narrative_dev


def greedy_optimize(candidates, group_code, n_target=30, n_trials=8000):
    """从候选池中用贪心+随机搜索找最优 n_target 子集"""
    if len(candidates) < n_target:
        return candidates

    best_subset = None
    best_loss = float("inf")
    best_info = None

    candidate_indices = candidates.index.tolist()

    for trial in range(n_trials):
        # 随机选 n_target 个
        chosen = np.random.choice(candidate_indices, n_target, replace=False)
        subset = candidates.loc[chosen]

        loss, mloss, sloss, ndev = compute_loss(subset, group_code)
        if loss < best_loss:
            best_loss = loss
            best_subset = subset.copy()
            best_info = (mloss, sloss, ndev)

    return best_subset, best_loss, best_info


# ============== 5. 主流程 ==============

def process_group(group_code, group_name, n_target=30):
    print(f"\n========== 处理 {group_code}: {group_name} ==========")

    # Step 3: 生成候选池
    n_candidates = 1500
    df = generate_candidates(group_code, n_candidates)

    # 离散化
    df = discretize_mas(df, group_code)
    df = discretize_css(df, group_code)

    # 先把连续指标四舍五入到合理精度
    for tp in TIMEPOINTS:
        df[f"FMA_LE_{tp}"] = np.round(df[f"FMA_LE_{tp}"].values, 1)
        df[f"ADL_{tp}"] = np.round(df[f"ADL_{tp}"].values, 1)
        df[f"BBS_{tp}"] = np.round(df[f"BBS_{tp}"].values, 1)

    df = assign_tugt(df)

    # Step 4: 硬约束审计
    passed_idx = run_audit(df, group_code)
    print(f"  候选池 {n_candidates} -> 通过审计 {len(passed_idx)} ({len(passed_idx)/n_candidates*100:.1f}%)")

    # 回退机制
    if len(passed_idx) < n_target * 2:
        print(f"  通过数不足 {n_target*2}，扩大候选池到 3000...")
        df = generate_candidates(group_code, 3000)
        df = discretize_mas(df, group_code)
        df = discretize_css(df, group_code)
        for tp in TIMEPOINTS:
            df[f"FMA_LE_{tp}"] = np.round(df[f"FMA_LE_{tp}"].values, 1)
            df[f"ADL_{tp}"] = np.round(df[f"ADL_{tp}"].values, 1)
            df[f"BBS_{tp}"] = np.round(df[f"BBS_{tp}"].values, 1)
        df = assign_tugt(df)
        passed_idx = run_audit(df, group_code)
        print(f"  候选池 3000 -> 通过审计 {len(passed_idx)} ({len(passed_idx)/3000*100:.1f}%)")

    candidates = df.loc[passed_idx]

    # Step 5: 阶段 B 优化
    print(f"  开始阶段 B 优化（目标 n={n_target}，搜索 15000 次子集）...")
    best_subset, best_loss, best_info = greedy_optimize(candidates, group_code, n_target, n_trials=15000)
    print(f"  优化完成 -> Loss={best_loss:.4f} (mean_err={best_info[0]:.4f}, sd_err={best_info[1]:.4f}, narr_dev={best_info[2]:.4f})")

    # Step 6: 最终审计
    print("  最终审计...")
    final_passed = 0
    for _, row in best_subset.iterrows():
        ok, vios = audit_patient(row, group_code)
        if ok:
            final_passed += 1
        else:
            print(f"    警告：最终子集中存在违规: {vios}")
    print(f"  最终子集硬规则通过率: {final_passed}/{len(best_subset)} ({final_passed/len(best_subset)*100:.1f}%)")

    return best_subset


def build_output(all_subsets):
    """将各组子集合并为长表格式"""
    rows = []
    patient_counter = 1

    for group_code, subset in all_subsets.items():
        group_name = GROUPS[group_code]
        for _, row in subset.iterrows():
            # 分配卒中亚型：约 35% 出血性，65% 缺血性
            stroke_type = np.random.choice(["出血性", "缺血性"], p=[0.35, 0.65])
            patient_id = f"SUB-{group_code}-{patient_counter:03d}"

            for tp in TIMEPOINTS:
                rows.append({
                    "分组": group_code,
                    "组别说明": group_name,
                    "患者ID": patient_id,
                    "卒中亚型": stroke_type,
                    "时间点": tp,
                    "FMA_LE": row[f"FMA_LE_{tp}"],
                    "ADL": row[f"ADL_{tp}"],
                    "BBS": row[f"BBS_{tp}"],
                    "TUGT": row[f"TUGT_{tp}"],
                    "MAS": row[f"MAS_{tp}"],
                    "CSS": row[f"CSS_{tp}"],
                })
            patient_counter += 1

    df_long = pd.DataFrame(rows)
    return df_long


def build_summary(all_subsets):
    """生成每组每时点实际 mean/SD 对照表"""
    summary_rows = []
    for group_code in ["G1", "G2", "G3", "G4"]:
        subset = all_subsets[group_code]
        for metric in METRICS:
            for tp in TIMEPOINTS:
                target_mean, target_sd = TARGETS[metric][tp][group_code]
                col = f"{metric}_{tp}"
                vals = subset[col]

                if metric == "TUGT":
                    numeric_vals = pd.to_numeric(vals[vals != "N/A"], errors="coerce").dropna()
                    n_na = (vals == "N/A").sum()
                    n_total = len(vals)
                    actual_mean = round(numeric_vals.mean(), 2) if len(numeric_vals) > 0 else np.nan
                    actual_sd = round(numeric_vals.std(ddof=1), 2) if len(numeric_vals) > 1 else np.nan
                else:
                    numeric_vals = pd.to_numeric(vals, errors="coerce").dropna()
                    n_na = 0
                    n_total = len(vals)
                    actual_mean = round(numeric_vals.mean(), 2)
                    actual_sd = round(numeric_vals.std(ddof=1), 2) if len(numeric_vals) > 1 else 0

                summary_rows.append({
                    "指标": metric,
                    "时点": tp,
                    "分组": group_code,
                    "目标均值": target_mean,
                    "目标SD": target_sd,
                    "实际均值": actual_mean,
                    "实际SD": actual_sd,
                    "均值偏差%": round((actual_mean - target_mean) / target_mean * 100, 2) if target_mean != 0 else np.nan,
                    "SD偏差%": round((actual_sd - target_sd) / target_sd * 100, 2) if target_sd != 0 else np.nan,
                    "N/A数": n_na,
                    "总数": n_total,
                })
    return pd.DataFrame(summary_rows)


def main():
    all_subsets = {}
    for gcode, gname in GROUPS.items():
        all_subsets[gcode] = process_group(gcode, gname, n_target=30)

    # 构建输出
    df_long = build_output(all_subsets)
    df_summary = build_summary(all_subsets)

    # 计算硬规则总体通过率
    total_patients = 0
    total_passed_audit = 0
    for gcode, subset in all_subsets.items():
        for _, row in subset.iterrows():
            total_patients += 1
            ok, _ = audit_patient(row, gcode)
            if ok:
                total_passed_audit += 1

    loss_info = pd.DataFrame([{
        "总患者数": total_patients,
        "硬规则通过数": total_passed_audit,
        "硬规则通过率%": round(total_passed_audit / total_patients * 100, 2),
    }])

    # 输出到 Excel
    output_path = "/Users/leyixu/Ai cowork/research/stroke_simulated_120.xlsx"
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_long.to_excel(writer, sheet_name="模拟数据", index=False)
        df_summary.to_excel(writer, sheet_name="统计对照", index=False)
        loss_info.to_excel(writer, sheet_name="审计摘要", index=False)

    print(f"\n✅ 已完成！输出文件: {output_path}")
    print(f"   主数据集: {len(df_long)} 行")
    print(f"   硬规则通过率: {total_passed_audit}/{total_patients}")


if __name__ == "__main__":
    main()
