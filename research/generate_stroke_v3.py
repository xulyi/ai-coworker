import numpy as np
import pandas as pd

np.random.seed(42)

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


def simple_generate(group_code, n=50000):
    """简单独立正态抽样，生成超大数据池"""
    data = {}
    for metric in METRICS:
        data[metric] = {}
        for tp in TIMEPOINTS:
            mu, sd = TARGETS[metric][tp][group_code]
            data[metric][tp] = np.random.normal(mu, sd, n)
    return data


def discretize_mas_col(vals):
    levels = np.array([0, 0.5, 1, 1.5, 2, 3, 4])
    idx = np.argmin(np.abs(levels[:, None] - vals[None, :]), axis=0)
    return levels[idx]


def discretize_css_col(vals):
    return np.clip(np.round(vals), 0, 45).astype(int)


def build_trajectories(group_code, n=50000):
    """将原始抽样组装为轨迹列表"""
    raw = simple_generate(group_code, n)
    trajs = []
    for i in range(n):
        traj = {}
        for tp in TIMEPOINTS:
            traj[tp] = {
                "FMA_LE": round(raw["FMA_LE"][tp][i], 1),
                "ADL": round(raw["ADL"][tp][i], 1),
                "BBS": round(raw["BBS"][tp][i], 1),
                "TUGT_raw": round(raw["TUGT"][tp][i], 1),
                "MAS": discretize_mas_col(np.array([raw["MAS"][tp][i]]))[0],
                "CSS": discretize_css_col(np.array([raw["CSS"][tp][i]]))[0],
            }
        trajs.append(traj)
    return trajs


def audit_trajectory(traj, group_code):
    """硬规则 + 常识规则 统一审计。返回 (score, violations, details)
    score=0 表示完全合规。"""
    score = 0
    violations = []
    details = {}

    # ===== P0: T0 基线生理约束 =====
    if traj["T0"]["MAS"] not in [1, 1.5, 2]:
        score += 100
        violations.append("P0_MAS_T0")
    if traj["T0"]["CSS"] > 13:
        score += 100
        violations.append("P0_CSS_T0")

    # ===== 预处理 TUGT =====
    # 必须复制一份，避免修改原始抽样数据影响后续轨迹
    processed = {tp: dict(traj[tp]) for tp in TIMEPOINTS}

    for tp in TIMEPOINTS:
        fma = processed[tp]["FMA_LE"]
        bbs = processed[tp]["BBS"]
        mas = processed[tp]["MAS"]
        tugt_raw = processed[tp]["TUGT_raw"]

        # 基础 TUGT 分配
        if bbs < 21:
            tugt = "N/A"
        else:
            tugt = tugt_raw

        # R3.1 / R3.2 / R3.3 / R3.4 前置修正
        if bbs < 21 and tugt != "N/A":
            tugt = "N/A"
        if 21 <= bbs <= 36 and tugt != "N/A" and tugt <= 35:
            tugt = 36.0 + abs(np.random.normal(0, 2))
            tugt = round(tugt, 1)
        if tugt != "N/A" and tugt < 25:
            if fma < 21 or bbs < 38 or mas > 2:
                tugt = 25.0 + abs(np.random.normal(0, 2))
                tugt = round(tugt, 1)
        if fma <= 12 and tugt != "N/A" and tugt < 40:
            tugt = 40.0 + abs(np.random.normal(0, 2))
            tugt = round(tugt, 1)

        processed[tp]["TUGT"] = tugt

    # ===== R4.1: FMA<15 时 ADL<=65 =====
    for tp in TIMEPOINTS:
        if processed[tp]["FMA_LE"] < 15 and processed[tp]["ADL"] > 65:
            score += 100
            violations.append(f"R4.1_{tp}")

    # ===== R4.3: 天花板效应 =====
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        if processed[prev]["FMA_LE"] >= 28 and processed[prev]["ADL"] >= 80:
            if processed[curr]["ADL"] - processed[prev]["ADL"] > 5:
                score += 50
                violations.append(f"R4.3_{prev}->{curr}")

    # ===== P3: Delta Max =====
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        d_fma = processed[curr]["FMA_LE"] - processed[prev]["FMA_LE"]
        d_bbs = processed[curr]["BBS"] - processed[prev]["BBS"]
        if d_fma > 8:
            score += 100
            violations.append(f"P3_FMA_{prev}->{curr}")
        if d_bbs > 9:
            score += 100
            violations.append(f"P3_BBS_{prev}->{curr}")
        prev_tugt = processed[prev]["TUGT"]
        curr_tugt = processed[curr]["TUGT"]
        if prev_tugt != "N/A" and curr_tugt != "N/A":
            drop = prev_tugt - curr_tugt
            if drop > 15:
                score += 100
                violations.append(f"P3_TUGT_{prev}->{curr}")

    # ===== 常识校验 C1-C9 =====
    # C1: FMA+BBS 同步明显好转时，TUGT 缩短或持平（不能明显变慢）
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        fma_up = processed[curr]["FMA_LE"] - processed[prev]["FMA_LE"] >= 3
        bbs_up = processed[curr]["BBS"] - processed[prev]["BBS"] >= 3
        prev_t = processed[prev]["TUGT"]
        curr_t = processed[curr]["TUGT"]
        if fma_up and bbs_up:
            if prev_t != "N/A" and curr_t != "N/A" and curr_t > prev_t + 2:
                score += 30
                violations.append(f"C1_{prev}->{curr}")

    # C4: FMA 跨 22 分大关时 ADL 应有明显增量（≥3分）
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        if processed[prev]["FMA_LE"] < 22 <= processed[curr]["FMA_LE"]:
            if processed[curr]["ADL"] - processed[prev]["ADL"] < 3:
                score += 20
                violations.append(f"C4_{prev}->{curr}")

    # C6: MAS 与 CSS 反向联动（大趋势）
    for i in range(1, len(TIMEPOINTS)):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        d_mas = processed[curr]["MAS"] - processed[prev]["MAS"]
        d_css = processed[curr]["CSS"] - processed[prev]["CSS"]
        if d_mas <= -0.5 and d_css >= 3:
            score += 25
            violations.append(f"C6_{prev}->{curr}")
        if d_mas >= 0.5 and d_css <= -3:
            score += 25
            violations.append(f"C6_{prev}->{curr}")

    # C8: 康复有效组大趋势单调性（G1/G2）
    if group_code in ["G1", "G2"]:
        for i in range(1, len(TIMEPOINTS)):
            prev = TIMEPOINTS[i - 1]
            curr = TIMEPOINTS[i]
            if processed[curr]["FMA_LE"] - processed[prev]["FMA_LE"] < -4:
                score += 10
                violations.append(f"C8_FMA_{prev}->{curr}")
            if processed[curr]["BBS"] - processed[prev]["BBS"] < -5:
                score += 10
                violations.append(f"C8_BBS_{prev}->{curr}")
            prev_t = processed[prev]["TUGT"]
            curr_t = processed[curr]["TUGT"]
            if prev_t != "N/A" and curr_t != "N/A" and curr_t - prev_t > 8:
                score += 10
                violations.append(f"C8_TUGT_{prev}->{curr}")

    # 额外：TUGT 与 BBS 的强负相关保护（C9）
    # 计算 TUGT 和 BBS 的相关系数，不能为正
    bbs_vals = [processed[tp]["BBS"] for tp in TIMEPOINTS]
    tugt_vals = [processed[tp]["TUGT"] for tp in TIMEPOINTS if processed[tp]["TUGT"] != "N/A"]
    tugt_tps = [tp for tp in TIMEPOINTS if processed[tp]["TUGT"] != "N/A"]
    if len(tugt_vals) >= 2:
        corr = np.corrcoef([bbs_vals[i] for i, tp in enumerate(TIMEPOINTS) if tp in tugt_tps], tugt_vals)[0, 1]
        if corr > 0.3:
            score += 15
            violations.append("C9_TUGT_BBS_corr_positive")

    return score, violations, processed


def pick_best_set(candidates, group_code, n_target=30):
    """从候选池中挑选 n_target 条，优先零违规，其次均值贴近"""
    zero_vio = [c for c in candidates if c["score"] == 0]
    print(f"  {group_code}: 候选池 {len(candidates)}，零违规 {len(zero_vio)}")

    if len(zero_vio) < n_target:
        # 放宽到最小违规
        sorted_all = sorted(candidates, key=lambda x: x["score"])
        chosen = sorted_all[:n_target]
    else:
        # 在零违规里按均值贴近度排序
        def mean_loss(cand):
            proc = cand["proc"]
            loss = 0
            for metric in METRICS:
                for tp in TIMEPOINTS:
                    mu, _ = TARGETS[metric][tp][group_code]
                    if metric == "TUGT":
                        val = proc[tp]["TUGT"]
                        if val == "N/A":
                            continue
                        loss += abs(val - mu) / max(mu, 0.1)
                    else:
                        val = proc[tp][metric]
                        loss += abs(val - mu) / max(mu, 0.1)
            return loss

        zero_vio.sort(key=mean_loss)
        chosen = zero_vio[:n_target]

    return [c["proc"] for c in chosen]


def generate_group(group_code, n_pool=200000, n_target=30):
    print(f"\n处理 {group_code} ...")
    trajs = build_trajectories(group_code, n_pool)
    candidates = []
    for traj in trajs:
        score, vios, proc = audit_trajectory(traj, group_code)
        candidates.append({"score": score, "vios": vios, "proc": proc})
        if len(candidates) % 50000 == 0 and score == 0:
            pass
    chosen = pick_best_set(candidates, group_code, n_target)

    # 局部修正：对被选中的集合做均值微调
    chosen = local_adjust(chosen, group_code)
    return chosen


def local_adjust(patients, group_code):
    """局部修正：对偏离太大的时点做微小 person-level 调整"""
    # 先计算实际均值
    for metric in METRICS:
        for tp in TIMEPOINTS:
            mu, _ = TARGETS[metric][tp][group_code]
            if metric == "TUGT":
                vals = [p[tp]["TUGT"] for p in patients if p[tp]["TUGT"] != "N/A"]
                if not vals:
                    continue
                actual = np.mean(vals)
            else:
                vals = [p[tp][metric] for p in patients]
                actual = np.mean(vals)
            diff = actual - mu
            if abs(diff) > mu * 0.08:  # 偏差超过 8% 才修正
                # 随机选 30% 的患者，每人反向微调一点
                n_tweak = max(1, int(len(patients) * 0.3))
                idxs = np.random.choice(len(patients), n_tweak, replace=False)
                for idx in idxs:
                    if metric == "TUGT" and patients[idx][tp]["TUGT"] != "N/A":
                        patients[idx][tp]["TUGT"] = round(patients[idx][tp]["TUGT"] - diff * (len(patients)/n_tweak), 1)
                    elif metric in ["FMA_LE", "BBS", "ADL"]:
                        patients[idx][tp][metric] = round(patients[idx][tp][metric] - diff * (len(patients)/n_tweak), 1)
                    elif metric == "MAS":
                        step = -1 if diff > 0 else 1
                        patients[idx][tp]["MAS"] = np.clip(patients[idx][tp]["MAS"] + step * (len(patients)/n_tweak) * 0.2, 0, 4)
                    elif metric == "CSS":
                        patients[idx][tp]["CSS"] = int(np.clip(round(patients[idx][tp]["CSS"] - diff * (len(patients)/n_tweak)), 0, 45))
    return patients


def build_long(group_patients):
    rows = []
    counter = 1
    for gc in ["G1", "G2", "G3", "G4"]:
        for p in group_patients[gc]:
            st = np.random.choice(["出血性", "缺血性"], p=[0.35, 0.65])
            pid = f"SUB-{gc}-{counter:03d}"
            for tp in TIMEPOINTS:
                rows.append({
                    "分组": gc,
                    "组别说明": GROUPS[gc],
                    "患者ID": pid,
                    "卒中亚型": st,
                    "时间点": tp,
                    "FMA_LE": p[tp]["FMA_LE"],
                    "ADL": p[tp]["ADL"],
                    "BBS": p[tp]["BBS"],
                    "TUGT": p[tp]["TUGT"],
                    "MAS": p[tp]["MAS"],
                    "CSS": p[tp]["CSS"],
                })
            counter += 1
    return pd.DataFrame(rows)


def build_summary(group_patients):
    rows = []
    for gc in ["G1", "G2", "G3", "G4"]:
        for metric in METRICS:
            for tp in TIMEPOINTS:
                mu_t, sd_t = TARGETS[metric][tp][gc]
                if metric == "TUGT":
                    vals = [p[tp]["TUGT"] for p in group_patients[gc]]
                    nv = [v for v in vals if v != "N/A"]
                    n_na = len(vals) - len(nv)
                    am = round(np.mean(nv), 2) if nv else np.nan
                    astd = round(np.std(nv, ddof=1), 2) if len(nv) > 1 else np.nan
                else:
                    vals = [p[tp][metric] for p in group_patients[gc]]
                    n_na = 0
                    am = round(np.mean(vals), 2)
                    astd = round(np.std(vals, ddof=1), 2) if len(vals) > 1 else 0
                rows.append({
                    "指标": metric, "时点": tp, "分组": gc,
                    "目标均值": mu_t, "目标SD": sd_t,
                    "实际均值": am, "实际SD": astd,
                    "均值偏差%": round((am-mu_t)/mu_t*100, 2) if mu_t != 0 and not np.isnan(am) else np.nan,
                    "SD偏差%": round((astd-sd_t)/sd_t*100, 2) if sd_t != 0 and not np.isnan(astd) else np.nan,
                    "N/A数": n_na, "总数": len(group_patients[gc]),
                })
    return pd.DataFrame(rows)


def final_audit(group_patients):
    hard_ok = 0
    cs_ok = 0
    total = 0
    for gc in ["G1", "G2", "G3", "G4"]:
        for p in group_patients[gc]:
            total += 1
            score, vios, _ = audit_trajectory(p, gc)
            if score == 0:
                hard_ok += 1
                cs_ok += 1
            elif all(v.startswith("C") for v in vios):
                hard_ok += 1
    print(f"\n=== 最终审计 ===")
    print(f"总患者: {total}")
    print(f"硬规则通过: {hard_ok}/{total} ({hard_ok/total*100:.1f}%)")
    print(f"常识零违规: {cs_ok}/{total} ({cs_ok/total*100:.1f}%)")


def main():
    gp = {}
    for gc in GROUPS:
        gp[gc] = generate_group(gc, n_pool=100000, n_target=30)
    final_audit(gp)
    df_long = build_long(gp)
    df_sum = build_summary(gp)
    out = "/Users/leyixu/Ai cowork/research/stroke_simulated_120_v3.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df_long.to_excel(writer, sheet_name="模拟数据", index=False)
        df_sum.to_excel(writer, sheet_name="统计对照", index=False)
    print(f"\n✅ 已保存: {out}")


if __name__ == "__main__":
    main()
