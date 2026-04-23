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


def simple_generate(group_code, n=100000):
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


def preprocess_traj(traj, group_code):
    """应用硬规则前置修正"""
    proc = {tp: dict(traj[tp]) for tp in TIMEPOINTS}
    # P0
    if proc["T0"]["MAS"] not in [1, 1.5, 2]:
        proc["T0"]["MAS"] = float(np.random.choice([1, 1.5, 2]))
    if proc["T0"]["CSS"] > 13:
        proc["T0"]["CSS"] = 13

    for tp in TIMEPOINTS:
        fma = proc[tp]["FMA_LE"]
        bbs = proc[tp]["BBS"]
        mas = proc[tp]["MAS"]
        tugt_raw = proc[tp]["TUGT_raw"]

        if bbs < 21:
            tugt = "N/A"
        else:
            tugt = tugt_raw

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

        proc[tp]["TUGT"] = tugt

    return proc


def hard_audit(proc, group_code):
    """只审计硬规则 P0-P4"""
    vios = []
    if proc["T0"]["MAS"] not in [1, 1.5, 2]:
        vios.append("P0_MAS_T0")
    if proc["T0"]["CSS"] > 13:
        vios.append("P0_CSS_T0")

    for i in range(1, 4):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        if proc[curr]["FMA_LE"] - proc[prev]["FMA_LE"] > 8:
            vios.append(f"P3_FMA_{prev}->{curr}")
        if proc[curr]["BBS"] - proc[prev]["BBS"] > 9:
            vios.append(f"P3_BBS_{prev}->{curr}")
        pt = proc[prev]["TUGT"]
        ct = proc[curr]["TUGT"]
        if pt != "N/A" and ct != "N/A" and (pt - ct) > 15:
            vios.append(f"P3_TUGT_{prev}->{curr}")

    for tp in TIMEPOINTS:
        if proc[tp]["FMA_LE"] < 15 and proc[tp]["ADL"] > 65:
            vios.append(f"R4.1_{tp}")
        bbs = proc[tp]["BBS"]
        tugt = proc[tp]["TUGT"]
        if bbs < 21 and tugt != "N/A":
            vios.append(f"R3.1_{tp}")
        if 21 <= bbs <= 36 and tugt != "N/A" and tugt <= 35:
            vios.append(f"R3.2_{tp}")
        if tugt != "N/A" and tugt < 25:
            if proc[tp]["FMA_LE"] < 21 or bbs < 38 or proc[tp]["MAS"] > 2:
                vios.append(f"R3.3_{tp}")
        if proc[tp]["FMA_LE"] <= 12 and tugt != "N/A" and tugt < 40:
            vios.append(f"R3.4_{tp}")

    for i in range(1, 4):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        if proc[prev]["FMA_LE"] >= 28 and proc[prev]["ADL"] >= 80:
            if proc[curr]["ADL"] - proc[prev]["ADL"] > 5:
                vios.append(f"R4.3_{prev}->{curr}")

    return len(vios) == 0, vios


def subset_loss(subset, group_code):
    """均值+SD联合偏离，权重可配"""
    mean_err = 0
    sd_err = 0
    n = 0
    for metric in METRICS:
        for tp in TIMEPOINTS:
            mu, sigma = TARGETS[metric][tp][group_code]
            if metric == "TUGT":
                vals = [p[tp]["TUGT"] for p in subset if p[tp]["TUGT"] != "N/A"]
                if not vals:
                    continue
            else:
                vals = [p[tp][metric] for p in subset]
            n += 1
            mean_err += abs(np.mean(vals) - mu) / max(mu, 0.1)
            actual_sd = np.std(vals, ddof=1)
            sd_err += abs(actual_sd - sigma) / max(sigma, 0.1)
    return (mean_err * 0.7 + sd_err * 0.3) / n


def local_fix(proc, group_code):
    """只修最致命的常识问题：TUGT 反向"""
    for i in range(1, 4):
        prev = TIMEPOINTS[i - 1]
        curr = TIMEPOINTS[i]
        fma_up = proc[curr]["FMA_LE"] - proc[prev]["FMA_LE"] >= 3
        bbs_up = proc[curr]["BBS"] - proc[prev]["BBS"] >= 3
        pt = proc[prev]["TUGT"]
        ct = proc[curr]["TUGT"]
        if fma_up and bbs_up and pt != "N/A" and ct != "N/A" and ct > pt + 1:
            proc[curr]["TUGT"] = round(pt - abs(np.random.normal(1, 1)), 1)
            if proc[curr]["TUGT"] < 0:
                proc[curr]["TUGT"] = 0.1
    return proc


def generate_group(group_code, n_pool=100000, n_target=30, n_search=15000):
    print(f"处理 {group_code} ...")
    raw = simple_generate(group_code, n_pool)
    hard_ok_pool = []
    for i in range(n_pool):
        traj = {}
        for tp in TIMEPOINTS:
            traj[tp] = {
                "FMA_LE": round(raw["FMA_LE"][tp][i], 1),
                "ADL": round(raw["ADL"][tp][i], 1),
                "BBS": round(raw["BBS"][tp][i], 1),
                "TUGT_raw": round(raw["TUGT"][tp][i], 1),
                "MAS": float(discretize_mas_col(np.array([raw["MAS"][tp][i]]))[0]),
                "CSS": int(discretize_css_col(np.array([raw["CSS"][tp][i]]))[0]),
            }
        proc = preprocess_traj(traj, group_code)
        ok, _ = hard_audit(proc, group_code)
        if ok:
            hard_ok_pool.append(proc)

    print(f"  硬规则通过池: {len(hard_ok_pool)} / {n_pool}")
    if len(hard_ok_pool) < n_target:
        raise ValueError(f"{group_code} 硬规则池不足 {n_target}")

    best_loss = float("inf")
    best_subset = None
    indices = np.arange(len(hard_ok_pool))
    for _ in range(n_search):
        chosen_idx = np.random.choice(indices, n_target, replace=False)
        subset = [hard_ok_pool[j] for j in chosen_idx]
        loss = subset_loss(subset, group_code)
        if loss < best_loss:
            best_loss = loss
            best_subset = subset

    # 局部修正
    fixed = []
    for p in best_subset:
        new_p = {tp: dict(p[tp]) for tp in TIMEPOINTS}
        new_p = local_fix(new_p, group_code)
        fixed.append(new_p)

    # 最终硬规则补位
    final = []
    reserve = n_target
    for p in fixed:
        ok, _ = hard_audit(p, group_code)
        if ok:
            final.append(p)
        else:
            while reserve < len(hard_ok_pool):
                rep = hard_ok_pool[reserve]
                reserve += 1
                rep_fixed = local_fix({tp: dict(rep[tp]) for tp in TIMEPOINTS}, group_code)
                ok2, _ = hard_audit(rep_fixed, group_code)
                if ok2:
                    final.append(rep_fixed)
                    break
    print(f"  最终入选: {len(final)}, best_loss={best_loss:.4f}")
    return final


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
                    "TUGT": str(p[tp]["TUGT"]),
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
                    "指标": metric,
                    "时点": tp,
                    "分组": gc,
                    "目标均值": mu_t,
                    "目标SD": sd_t,
                    "实际均值": am,
                    "实际SD": astd,
                    "均值偏差%": round((am - mu_t) / mu_t * 100, 2) if mu_t != 0 and not np.isnan(am) else np.nan,
                    "SD偏差%": round((astd - sd_t) / sd_t * 100, 2) if sd_t != 0 and not np.isnan(astd) else np.nan,
                    "N/A数": n_na,
                    "总数": len(group_patients[gc]),
                })
    return pd.DataFrame(rows)


def main():
    gp = {}
    for gc in GROUPS:
        gp[gc] = generate_group(gc, n_pool=100000, n_target=30, n_search=20000)

    # 硬规则终检
    total = 0
    hard_pass = 0
    for gc in ["G1", "G2", "G3", "G4"]:
        for p in gp[gc]:
            total += 1
            ok, vios = hard_audit(p, gc)
            if ok:
                hard_pass += 1
            else:
                print(f"  硬规失败: {gc} {vios}")
    print(f"\n硬规则通过: {hard_pass}/{total} ({hard_pass / total * 100:.1f}%)")

    # 常识抽检
    c1_fails = 0
    c1_examples = []
    for gc in ["G1", "G2", "G3", "G4"]:
        for p in gp[gc]:
            for i in range(1, 4):
                prev = TIMEPOINTS[i - 1]
                curr = TIMEPOINTS[i]
                fma_up = p[curr]["FMA_LE"] - p[prev]["FMA_LE"] >= 3
                bbs_up = p[curr]["BBS"] - p[prev]["BBS"] >= 3
                pt = p[prev]["TUGT"]
                ct = p[curr]["TUGT"]
                if fma_up and bbs_up and pt != "N/A" and ct != "N/A" and ct > pt + 2:
                    c1_fails += 1
                    if len(c1_examples) < 3:
                        c1_examples.append((gc, prev, curr, pt, ct))
    print(f"C1 抽检违规: {c1_fails} 例次")
    for ex in c1_examples:
        print(f"  {ex}")

    df_long = build_long(gp)
    df_sum = build_summary(gp)
    out = "/Users/leyixu/Ai cowork/research/stroke_simulated_120_v5.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df_long.to_excel(writer, sheet_name="模拟数据", index=False)
        df_sum.to_excel(writer, sheet_name="统计对照", index=False)
    print(f"\n已保存: {out}")


if __name__ == "__main__":
    main()
