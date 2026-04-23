import csv
import numpy as np

# 读取CSV文件
with open('/Users/leyixu/Desktop/rehab_summary_table——4-11.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# 表头
header = rows[0]
groups = ['G1', 'G2', 'G3', 'G4']
group_names = {
    'G1': '双侧真实',
    'G2': '患侧真实+健侧安慰剂',
    'G3': '双侧假刺激',
    'G4': '空白对照'
}

# 解析数据
GOAL = {m: {t: {} for t in ['T0', 'T1', 'T2', 'T3']} for m in ['FMA_LE', 'ADL', 'BBS', 'CSS']}
TUGT_GOAL = {g: {t: None for t in ['T0', 'T1', 'T2', 'T3']} for g in groups}
MAS_GOAL = {g: {t: {} for t in ['T0', 'T1', 'T2', 'T3']} for g in groups}

for row in rows[1:]:
    label = row[0].strip()
    parts = label.split('_')
    metric = parts[0]
    time = parts[1] if len(parts) > 1 else None
    vals = [v.strip().replace(' ', '') for v in row[1:5]]

    for i, g in enumerate(groups):
        mean_str, sd_str = vals[i].split('±')
        mean, sd = float(mean_str), float(sd_str)

        if metric in ['FMA_LE', 'ADL', 'BBS', 'CSS']:
            GOAL[metric][time][g] = (mean, sd)
        elif metric == 'TUGT':
            TUGT_GOAL[g][time] = (mean, sd)
        elif metric == 'MAS':
            MAS_GOAL[g][time] = (mean, sd)

# --- 打印 GOAL ---
print("GOAL = {")
for metric in ['FMA_LE', 'ADL', 'BBS', 'CSS']:
    print(f"    '{metric}': {{")
    for t in ['T0', 'T1', 'T2', 'T3']:
        d = GOAL[metric][t]
        line = ", ".join([f"'{g}': ({d[g][0]}, {d[g][1]})" for g in groups])
        print(f"        '{t}': {{{line}}},")
    print(f"    }},")
print("}")

# --- 打印 TUGT_GOAL ---
print("\nTUGT_GOAL = {")
for g in groups:
    items = []
    for t in ['T0', 'T1', 'T2', 'T3']:
        v = TUGT_GOAL[g][t]
        if v is None:
            items.append(f"'{t}': None")
        else:
            items.append(f"'{t}': ({v[0]}, {v[1]})")
    print(f"    '{g}': {{{', '.join(items)}}},")
print("}")

# --- 将 MAS 均值/SD 转换为离散分布 ---
# MAS 字符串值映射到数字
mas_values = {'0': 0.0, '1': 1.0, '1+': 1.5, '2': 2.0}


def fit_mas_dist(mean, sd, allowed=None):
    """
    根据目标均值和标准差，拟合 {0, 1, 1+, 2} 的离散分布。
    返回概率字典。如果无法精确匹配，返回最接近的合法分布。
    """
    if allowed is None:
        # T0 必须满足 R1.1: {1, 1+}
        # 其他时间点放宽到 {0, 1, 1+, 2}
        allowed = list(mas_values.keys())

    nums = np.array([mas_values[k] for k in allowed])
    best_dist = None
    best_score = float('inf')

    # 对4个取值，用网格搜索（步长0.01）效率太低；改用解析+随机搜索
    # 但有4个变量减1个约束（和为1），自由度为3。
    # 我们用蒙特卡洛随机采样大量概率向量，找最接近的
    np.random.seed(0)
    n_samples = 500000
    # Dirichlet 随机采样
    alphas = np.ones(len(allowed))
    # 根据均值给alphas加偏向
    for i, v in enumerate(nums):
        alphas[i] = max(0.01, 1.0 / (abs(v - mean) + 0.1))
    samples = np.random.dirichlet(alphas, n_samples)

    means = samples @ nums
    vars_ = samples @ (nums ** 2) - means ** 2
    sds = np.sqrt(vars_)

    scores = ((means - mean) / max(sd, 0.001)) ** 2 + ((sds - sd) / max(sd, 0.001)) ** 2
    idx = np.argmin(scores)
    best = samples[idx]
    # 四舍五入到两位小数并归一化
    best = np.round(best, 2)
    best = best / best.sum()
    return {k: float(best[i]) for i, k in enumerate(allowed)}


print("\nMAS_GOAL = {")
for g in groups:
    print(f"    '{g}': {{")
    for t in ['T0', 'T1', 'T2', 'T3']:
        mean, sd = MAS_GOAL[g][t]
        if t == 'T0':
            dist = fit_mas_dist(mean, sd, allowed=['1', '1+'])
        else:
            dist = fit_mas_dist(mean, sd)
        # 清理接近0的概率
        dist = {k: round(v, 3) for k, v in dist.items() if v > 0.001}
        # 重新归一化
        s = sum(dist.values())
        dist = {k: round(v / s, 3) for k, v in dist.items()}
        # 处理舍入误差，保证和为1
        remainder = 1.0 - sum(dist.values())
        if remainder != 0 and dist:
            last_key = list(dist.keys())[-1]
            dist[last_key] = round(dist[last_key] + remainder, 3)
        items = ", ".join([f"'{k}':{v}" for k, v in dist.items()])
        print(f"        '{t}': {{{items}}},")
    print(f"    }},")
print("}")
