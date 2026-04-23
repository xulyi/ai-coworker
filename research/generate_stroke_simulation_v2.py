"""
脑卒中康复模拟数据生成器 v2
核心改变：从"生成后审计"改为"生成中耦合+拒绝采样"
基于 stroke_amulate 硬规则 + stroke_simulation_common_sense 常识校验
"""
import numpy as np
import pandas as pd

np.random.seed(2025)

GROUPS = {
    "G1": "双侧真实",
    "G2": "患侧真实+健侧安慰剂",
    "G3": "双侧假刺激",
    "G4": "空白对照 (CT)",
}
TIMEPOINTS = ["T0", "T1", "T2", "T3"]
METRICS = ["FMA_LE", "ADL", "BBS", "TUGT", "MAS", "CSS"]

TARGETS = {
    "FMA_LE": {
        "T0": {"G1": (12.4, 3.5), "G2": (13.8, 3.7), "G3": (11.5, 3.1), "G4": (12.7, 3.4)},
        "T1": {"G1": (15.1, 3.8), "G2": (15.6, 4.0), "G3": (12.4, 3.4), "G4": (13.5, 3.5)},
        "T2": {"G1": (18.5, 4.2), "G2": (17.2, 4.1), "G3": (13.8, 3.6), "G4": (14.2, 3.7)},
        "T3": {"G1": (19.8, 4.5), "G2": (18.4, 4.3), "G3": (15.0, 4.0), "G4": (15.8, 4.1)},
    },
    "ADL": {
        "T0": {"G1": (48.5, 10.2), "G2": (51.2, 11.4), "G3": (47.8, 9.5), "G4": (52.1, 11.0)},
        "T1": {"G1": (54.2, 11.0), "G2": (55.4, 11.5), "G3": (49.5, 9.8), "G4": (54.0, 11.2)},
        "T2": {"G1": (61.5, 12.1), "G2": (58.5, 11.8), "G3": (51.2, 10.0), "G4": (55.8, 11.4)},
        "T3": {"G1": (63.5, 12.5), "G2": (60.5, 11.8), "G3": (53.4, 10.2), "G4": (57.6, 11.5)},
    },
    "BBS": {
        "T0": {"G1": (22.4, 6.1), "G2": (24.1, 6.5), "G3": (21.8, 5.8), "G4": (23.5, 6.2)},
        "T1": {"G1": (27.8, 6.5), "G2": (28.5, 6.8), "G3": (23.2, 6.0), "G4": (25.1, 6.4)},
        "T2": {"G1": (32.6, 7.1), "G2": (31.2, 7.0), "G3": (24.5, 6.2), "G4": (26.2, 6.6)},
        "T3": {"G1": (34.5, 7.5), "G2": (32.8, 7.2), "G3": (25.4, 6.4), "G4": (27.2, 6.8)},
    },
    "TUGT": {
        "T0": {"G1": (58.4, 14.5), "G2": (55.2, 13.8), "G3": (61.5, 15.2), "G4": (57.8, 14.2)},
        "T1": {"G1": (51.2, 12.8), "G2": (49.8, 12.2), "G3": (59.4, 14.8), "G4": (55.5, 13.5)},
        "T2": {"G1": (44.5, 10.5), "G2": (45.8, 11.0), "G3": (58.0, 14.5), "G4": (54.2, 13.8)},
        "T3": {"G1": (42.5, 10.2), "G2": (44.0, 10.6), "G3": (56.5, 14.0), "G4": (52.8, 13.5)},
    },
    "MAS": {
        "T0": {"G1": (1.18, 0.32), "G2": (1.24, 0.34), "G3": (1.16, 0.31), "G4": (1.21, 0.33)},
        "T1": {"G1": (1.12, 0.30), "G2": (1.17, 0.32), "G3": (1.32, 0.36), "G4": (1.30, 0.35)},
        "T2": {"G1": (0.85, 0.22), "G2": (1.05, 0.28), "G3": (1.72, 0.45), "G4": (1.65, 0.42)},
        "T3": {"G1": (0.92, 0.24), "G2": (1.22, 0.32), "G3": (1.85, 0.48), "G4": (1.78, 0.46)},
    },
    "CSS": {
        "T0": {"G1": (8.9, 1.4), "G2": (9.2, 1.6), "G3": (8.8, 1.5), "G4": (9.1, 1.6)},
        "T1": {"G1": (8.6, 1.3), "G2": (9.0, 1.5), "G3": (9.8, 1.7), "G4": (9.5, 1.6)},
        "T2": {"G1": (7.2, 1.2), "G2": (8.4, 1.4), "G3": (11.5, 1.8), "G4": (11.0, 1.7)},
        "T3": {"G1": (7.8, 1.4), "G2": (9.1, 1.5), "G3": (11.8, 1.9), "G4": (11.2, 1.8)},
    },
}


def draw_from_targets(group_code, metric, tp):
    """从目标分布中独立抽取一个值"""
    mu, sigma = TARGETS[metric][tp][group_code]
    val = np.random.normal(mu, sigma)
    return val


def generate_raw_trajectory(group_code):
    """生成一条原始轨迹，各时点独立抽取"""
    traj = {}
    for metric in METRICS:
        traj[metric] = {}
        for tp in TIMEPOINTS:
            traj[metric][tp] = draw_from_targets(group_code, metric, tp)
    return traj


def discretize_mas(mas_raw):
    """将 MAS 连续值映射到离散级别 0, 0.5, 1, 1.5, 2, 3, 4"""
    levels = np.array([0, 0.5, 1, 1.5, 2, 3, 4])
    idx = np.argmin(np.abs(levels - mas_raw))
    # 以一定概率向相邻级别微调
    if idx > 0 and idx < len(levels) - 1:
        p = (mas_raw - levels[idx]) / (levels[idx+1] - levels[idx])
        p = np.clip(p + 0.5, 0.2, 0.8)
        if np.random.random() < p:
            idx += 1
    return levels[idx]


def discretize_css(css_raw):
    """CSS 四舍五入到整数并截断"""
    return int(np.clip(round(css_raw), 0, 45))


def compute_mobility_score(fma, bbs):
    """基于 FMA-LE 和 BBS 推断 ADL 中 Mobility 项的分数 (0,5,10,15)"""
    # Barthel Mobility: 0=卧床, 5=轮椅独立, 10=辅助步行, 15=独立步行
    if fma < 8 or bbs < 15:
        return 0
    if fma < 15 or bbs < 21:
        return 5
    if fma < 22 or bbs < 29:
        return 10
    return 15


def compute_stairs_score(fma, bbs):
    """基于 FMA-LE 和 BBS 推断 ADL 中 Stairs 项的分数 (0,5,10)"""
    if fma < 15 or bbs < 21:
        return 0
    if fma < 22 or bbs < 36:
        return 5
    return 10


def build_adl_from_components(mobility, stairs, selfcare, bowel_bladder, transfer):
    """根据分项组装 ADL 总分（原始版 Barthel 0-100）"""
    # 原始 Barthel 分值分配：
    # Feeding 10, Bathing 5, Grooming 5, Dressing 10, Bowel 10, Bladder 10,
    # Toilet 10, Transfer 15, Mobility 15, Stairs 10
    # 我们把 selfcare 聚合为 Feeding+Bathing+Grooming+Dressing = 30
    # bowel_bladder 聚合为 Bowel+Bladder+Toilet = 30
    # transfer 为 Transfer 15
    # mobility 为 Mobility 15
    # stairs 为 Stairs 10
    adl = selfcare + bowel_bladder + transfer + mobility + stairs
    return int(np.clip(adl, 0, 100))


def assign_tugt(fma, bbs, tugt_raw):
    """根据 FMA-LE 和 BBS 决定 TUGT 是 N/A 还是数值"""
    if bbs < 21:
        return "N/A"
    # 基础耗时与 BBS 负相关
    expected_tugt = 70 - 0.8 * bbs + np.random.normal(0, 3)
    # 融合原始抽取值和生物力学期望值
    tugt = 0.4 * tugt_raw + 0.6 * expected_tugt
    # FMA 越低，TUGT 越慢
    tugt += max(0, 22 - fma) * 1.5
    # 加随机扰动
    tugt += np.random.normal(0, 2)
    # 保留1位小数
    tugt = round(tugt, 1)
    # 常识钳制：BBS 21-36 时 TUGT 不能太快
    if 21 <= bbs <= 36 and tugt <= 35:
        tugt = 36.0 + abs(np.random.normal(0, 3))
    # BBS >=38 但 FMA<21 时不应太快
    if bbs >= 38 and fma < 21 and tugt < 30:
        tugt = 30.0 + abs(np.random.normal(0, 2))
    # 常识钳制：TUGT<25 需要高质量步态三角（FMA>=21, BBS>=38, MAS<=2）在调用处检查
    return round(tugt, 1)


def generate_patient(group_code):
    """生成一条患者轨迹，内置耦合逻辑"""
    # 先生成所有原始值
    raw = generate_raw_trajectory(group_code)

    patient = {}
    for tp in TIMEPOINTS:
        patient[tp] = {}
        # FMA 和 BBS 保持连续（四舍五入到1位小数）
        fma = round(raw["FMA_LE"][tp], 1)
        bbs = round(raw["BBS"][tp], 1)

        # MAS 离散化
        mas = discretize_mas(raw["MAS"][tp])

        # CSS 离散化
        css = discretize_css(raw["CSS"][tp])

        # TUGT 由 FMA/BBS 决定
        tugt = assign_tugt(fma, bbs, raw["TUGT"][tp])

        # 如果 TUGT<25，必须满足步态三角（否则强制抬高）
        if isinstance(tugt, (int, float, np.floating)) and tugt < 25:
            if fma < 21 or bbs < 38 or mas > 2:
                tugt = 25.0 + abs(np.random.normal(0, 2))
                tugt = round(tugt, 1)

        # ADL 组装
        mobility = compute_mobility_score(fma, bbs)
        stairs = compute_stairs_score(fma, bbs)
        # selfcare 和 bowel_bladder 用潜变量+随机扰动，但与 FMA/BBS 弱相关
        u = np.random.normal(0, 1)
        selfcare_base = 20 + 0.3 * fma + 0.2 * bbs + 5 * u
        selfcare = int(np.clip(round(selfcare_base / 5) * 5, 0, 30))
        bb_base = 15 + 0.2 * fma + 0.15 * bbs + 4 * u
        bowel_bladder = int(np.clip(round(bb_base / 5) * 5, 0, 30))
        transfer_base = 5 + 0.3 * fma + 0.25 * bbs + 3 * u
        transfer = int(np.clip(round(transfer_base / 5) * 5, 0, 15))

        adl = build_adl_from_components(mobility, stairs, selfcare, bowel_bladder, transfer)

        patient[tp]["FMA_LE"] = fma
        patient[tp]["BBS"] = bbs
        patient[tp]["MAS"] = mas
        patient[tp]["CSS"] = css
        patient[tp]["TUGT"] = tugt
        patient[tp]["ADL"] = adl

    return patient


# ============== 硬约束审计（P0-P4） ==============

def audit_patient(patient, group_code):
    """对单个患者轨迹进行审计，返回 (pass: bool, violations: list)"""
    violations = []

    # P0
    mas_t0 = patient["T0"]["MAS"]
    css_t0 = patient["T0"]["CSS"]
    if mas_t0 not in [1, 1.5, 2]:
        violations.append(f"P0-MAS_T0={mas_t0}")
    if css_t0 > 13:
        violations.append(f"P0-CSS_T0={css_t0}")

    for tp in TIMEPOINTS:
        fma = patient[tp]["FMA_LE"]
        adl = patient[tp]["ADL"]
        bbs = patient[tp]["BBS"]
        tugt = patient[tp]["TUGT"]
        mas = patient[tp]["MAS"]

        # R3.1
        if bbs < 21 and tugt != "N/A":
            violations.append(f"R3.1-{tp}(BBS={bbs:.1f},TUGT={tugt})")
        # R3.2
        if 21 <= bbs <= 36:
            if isinstance(tugt, (int, float, np.floating)) and tugt <= 35:
                violations.append(f"R3.2-{tp}(BBS={bbs:.1f},TUGT={tugt})")
        # R3.3
        if isinstance(tugt, (int, float, np.floating)) and tugt < 25:
            if fma < 21 or bbs < 38 or mas > 2:
                violations.append(f"R3.3-{tp}(TUGT={tugt},FMA={fma:.1f},BBS={bbs:.1f},MAS={mas})")
        # R3.4
        if fma <= 12 and isinstance(tugt, (int, float, np.floating)) and tugt < 40:
            violations.append(f"R3.4-{tp}(FMA={fma:.1f},TUGT={tugt})")
        # R4.1
        if fma < 15 and adl > 65:
            violations.append(f"R4.1-{tp}(FMA={fma:.1f},ADL={adl})")

    # R4.3
    for i in range(1, len(TIMEPOINTS)):
        prev_tp = TIMEPOINTS[i-1]
        curr_tp = TIMEPOINTS[i]
        if patient[prev_tp]["FMA_LE"] >= 28 and patient[prev_tp]["ADL"] >= 80:
            delta_adl = patient[curr_tp]["ADL"] - patient[prev_tp]["ADL"]
            if delta_adl > 5:
                violations.append(f"R4.3-{prev_tp}->{curr_tp}(ΔADL={delta_adl})")

    # P3 Delta Max
    for i in range(1, len(TIMEPOINTS)):
        prev_tp = TIMEPOINTS[i-1]
        curr_tp = TIMEPOINTS[i]
        delta_fma = patient[curr_tp]["FMA_LE"] - patient[prev_tp]["FMA_LE"]
        delta_bbs = patient[curr_tp]["BBS"] - patient[prev_tp]["BBS"]
        if delta_fma > 8:
            violations.append(f"P3-FMA-{prev_tp}->{curr_tp}(Δ={delta_fma:.1f})")
        if delta_bbs > 9:
            violations.append(f"P3-BBS-{prev_tp}->{curr_tp}(Δ={delta_bbs:.1f})")
        prev_tugt = patient[prev_tp]["TUGT"]
        curr_tugt = patient[curr_tp]["TUGT"]
        if isinstance(prev_tugt, (int, float, np.floating)) and isinstance(curr_tugt, (int, float, np.floating)):
            drop = prev_tugt - curr_tugt
            if drop > 15:
                violations.append(f"P3-TUGT-{prev_tp}->{curr_tp}(drop={drop:.1f})")

    return len(violations) == 0, violations


# ============== 常识校验层 ==============

def common_sense_audit(patient, group_code):
    """返回 (score, violations_list)。score 越低越好。"""
    violations = []
    score = 0

    # C1: FMA/BBS 同步好转时，TUGT 必须缩短或保持 N/A
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i-1]
        curr = TIMEPOINTS[i]
        fma_up = patient[curr]["FMA_LE"] - patient[prev]["FMA_LE"] >= 3
        bbs_up = patient[curr]["BBS"] - patient[prev]["BBS"] >= 3
        prev_tugt = patient[prev]["TUGT"]
        curr_tugt = patient[curr]["TUGT"]
        if fma_up and bbs_up:
            if isinstance(prev_tugt, (int, float, np.floating)) and isinstance(curr_tugt, (int, float, np.floating)):
                if curr_tugt > prev_tugt + 2:  # 明显变好时反而变慢
                    violations.append(f"C1-{prev}->{curr}: FMA↑BBS↑ but TUGT↑ ({prev_tugt}->{curr_tugt})")
                    score += 5

    # C4: FMA 跨 22 分时 ADL 必须有级别跨越检查
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i-1]
        curr = TIMEPOINTS[i]
        if patient[prev]["FMA_LE"] < 22 <= patient[curr]["FMA_LE"]:
            # 检查该周期 ADL 增量是否明显
            delta_adl = patient[curr]["ADL"] - patient[prev]["ADL"]
            if delta_adl < 3:
                violations.append(f"C4-{prev}->{curr}: FMA crossed 22 but ΔADL only {delta_adl}")
                score += 3

    # C6: MAS 与 CSS 反向联动（大趋势）
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i-1]
        curr = TIMEPOINTS[i]
        delta_mas = patient[curr]["MAS"] - patient[prev]["MAS"]
        delta_css = patient[curr]["CSS"] - patient[prev]["CSS"]
        if delta_mas <= -0.5 and delta_css >= 3:
            violations.append(f"C6-{prev}->{curr}: MAS↓ but CSS↑ ({delta_mas:.1f}, {delta_css})")
            score += 4
        if delta_mas >= 0.5 and delta_css <= -3:
            violations.append(f"C6-{prev}->{curr}: MAS↑ but CSS↓ ({delta_mas:.1f}, {delta_css})")
            score += 4

    # C8: 纵向单调性大趋势（仅对 G1/G2 康复有效组）
    if group_code in ["G1", "G2"]:
        # FMA 大趋势不应出现断崖式下跌
        for i in range(1, len(TIMEPOINTS)):
            prev = TIMEPOINTS[i-1]
            curr = TIMEPOINTS[i]
            if patient[curr]["FMA_LE"] - patient[prev]["FMA_LE"] < -4:
                violations.append(f"C8-{prev}->{curr}: FMA drop {patient[prev]['FMA_LE']:.1f}->{patient[curr]['FMA_LE']:.1f}")
                score += 2
            if patient[curr]["BBS"] - patient[prev]["BBS"] < -5:
                violations.append(f"C8-{prev}->{curr}: BBS drop {patient[prev]['BBS']:.1f}->{patient[curr]['BBS']:.1f}")
                score += 2
            prev_tugt = patient[prev]["TUGT"]
            curr_tugt = patient[curr]["TUGT"]
            if isinstance(prev_tugt, (int, float, np.floating)) and isinstance(curr_tugt, (int, float, np.floating)):
                if curr_tugt - prev_tugt > 8:
                    violations.append(f"C8-{prev}->{curr}: TUGT worsened {prev_tugt}->{curr_tugt}")
                    score += 2

    return score, violations


def generate_group(group_code, n_target=30, max_attempts=50000):
    """用拒绝采样生成一组患者，兼顾硬规则和常识"""
    accepted = []
    attempts = 0
    best_fallback = None
    best_fallback_score = float("inf")

    while len(accepted) < n_target and attempts < max_attempts:
        patient = generate_patient(group_code)
        ok_hard, hard_vios = audit_patient(patient, group_code)
        cs_score, cs_vios = common_sense_audit(patient, group_code)

        if ok_hard and cs_score == 0:
            accepted.append(patient)
        else:
            # 记录最接近合规的候选（用于极端情况回退）
            total_penalty = len(hard_vios) * 100 + cs_score
            if total_penalty < best_fallback_score:
                best_fallback_score = total_penalty
                best_fallback = patient

        attempts += 1

    # 如果严格采样失败，使用 penalty 最低的回退候选并人工修复
    while len(accepted) < n_target:
        if best_fallback is not None:
            # 简单修复：强制钳制 TUGT 极端值
            patient = best_fallback
            for tp in TIMEPOINTS:
                bbs = patient[tp]["BBS"]
                if bbs < 21:
                    patient[tp]["TUGT"] = "N/A"
            accepted.append(patient)
        else:
            break

    print(f"  {group_code}: {len(accepted)}/{n_target} accepted in {attempts} attempts (best_fallback_score={best_fallback_score})")
    return accepted


def build_long_table(group_patients):
    """将分组患者数据转换为长表"""
    rows = []
    patient_counter = 1
    for group_code, patients in group_patients.items():
        group_name = GROUPS[group_code]
        for patient in patients:
            stroke_type = np.random.choice(["出血性", "缺血性"], p=[0.35, 0.65])
            patient_id = f"SUB-{group_code}-{patient_counter:03d}"
            for tp in TIMEPOINTS:
                rows.append({
                    "分组": group_code,
                    "组别说明": group_name,
                    "患者ID": patient_id,
                    "卒中亚型": stroke_type,
                    "时间点": tp,
                    "FMA_LE": patient[tp]["FMA_LE"],
                    "ADL": patient[tp]["ADL"],
                    "BBS": patient[tp]["BBS"],
                    "TUGT": patient[tp]["TUGT"],
                    "MAS": patient[tp]["MAS"],
                    "CSS": patient[tp]["CSS"],
                })
            patient_counter += 1
    return pd.DataFrame(rows)


def build_summary(group_patients):
    """生成统计对照表"""
    summary_rows = []
    for group_code in ["G1", "G2", "G3", "G4"]:
        patients = group_patients[group_code]
        for metric in METRICS:
            for tp in TIMEPOINTS:
                target_mean, target_sd = TARGETS[metric][tp][group_code]
                if metric == "TUGT":
                    vals = [p[tp]["TUGT"] for p in patients]
                    numeric_vals = [v for v in vals if v != "N/A"]
                    n_na = len(vals) - len(numeric_vals)
                    actual_mean = round(np.mean(numeric_vals), 2) if numeric_vals else np.nan
                    actual_sd = round(np.std(numeric_vals, ddof=1), 2) if len(numeric_vals) > 1 else np.nan
                else:
                    vals = [p[tp][metric] for p in patients]
                    n_na = 0
                    actual_mean = round(np.mean(vals), 2)
                    actual_sd = round(np.std(vals, ddof=1), 2) if len(vals) > 1 else 0

                summary_rows.append({
                    "指标": metric,
                    "时点": tp,
                    "分组": group_code,
                    "目标均值": target_mean,
                    "目标SD": target_sd,
                    "实际均值": actual_mean,
                    "实际SD": actual_sd,
                    "均值偏差%": round((actual_mean - target_mean) / target_mean * 100, 2) if target_mean != 0 and not np.isnan(actual_mean) else np.nan,
                    "SD偏差%": round((actual_sd - target_sd) / target_sd * 100, 2) if target_sd != 0 and not np.isnan(actual_sd) else np.nan,
                    "N/A数": n_na,
                    "总数": len(patients),
                })
    return pd.DataFrame(summary_rows)


def full_audit_report(group_patients):
    """输出硬规则和常识校验的完整报告"""
    total_patients = 0
    hard_pass = 0
    cs_zero = 0
    all_hard_vios = []
    all_cs_vios = []

    for gc, patients in group_patients.items():
        for p in patients:
            total_patients += 1
            ok, vios = audit_patient(p, gc)
            if ok:
                hard_pass += 1
            else:
                all_hard_vios.extend([(gc, p, v) for v in vios])
            cs_score, cs_vios_list = common_sense_audit(p, gc)
            if cs_score == 0:
                cs_zero += 1
            else:
                all_cs_vios.extend([(gc, cs_score, v) for v in cs_vios_list])

    report = {
        "total": total_patients,
        "hard_pass": hard_pass,
        "cs_zero": cs_zero,
        "hard_vio_count": len(all_hard_vios),
        "cs_vio_count": len(all_cs_vios),
    }

    # 打印前几条违规
    print(f"\n=== 审计报告 ===")
    print(f"总患者: {total_patients}")
    print(f"硬规则通过: {hard_pass}/{total_patients} ({hard_pass/total_patients*100:.1f}%)")
    print(f"常识零违规: {cs_zero}/{total_patients} ({cs_zero/total_patients*100:.1f}%)")
    if all_hard_vios:
        print(f"硬规则违规样例 (前5):")
        for v in all_hard_vios[:5]:
            print(f"  {v}")
    if all_cs_vios:
        print(f"常识违规样例 (前10):")
        for v in all_cs_vios[:10]:
            print(f"  {v}")
    return report


def main():
    group_patients = {}
    for gcode in GROUPS.keys():
        group_patients[gcode] = generate_group(gcode, n_target=30)

    full_audit_report(group_patients)

    df_long = build_long_table(group_patients)
    df_summary = build_summary(group_patients)

    output = "/Users/leyixu/Ai cowork/research/stroke_simulated_120_v2.xlsx"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_long.to_excel(writer, sheet_name="模拟数据", index=False)
        df_summary.to_excel(writer, sheet_name="统计对照", index=False)

    print(f"\n✅ 输出: {output}")
    print(f"   数据行数: {len(df_long)}")


if __name__ == "__main__":
    main()
