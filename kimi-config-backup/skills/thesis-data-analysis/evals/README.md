# Evals README — thesis-data-analysis Skill 完整评测框架

> 本目录用于系统性验证 `thesis-data-analysis` skill 是否在所有核心场景下，都能稳定执行正确的统计决策流程，并输出论文可用结果。
>
> **评测核心目标**：不是让输出"看起来很专业"，而是验证 skill 是否真正做到了：
> 1. 先问对问题（关键信息澄清）
> 2. 先判对路径（统计路径识别）
> 3. 先验前提（假设检验）
> 4. 能识别错误方法并给出替代方案
> 5. 信息不足时诚实停下，而不是强行推断
> 6. 输出符合 APA 7th / CONSORT 规范的论文可用结果

---

## 一、评测架构概览

```
评测体系
│
├── P0 必须通过 Case（核心能力，任何一条失败即为 Skill 退化）
│   ├── 两独立组连续变量比较（标准路径）
│   ├── 用户指定错误方法的纠偏
│   └── 信息不足时的停止推断
│
├── P1 强烈建议通过 Case（重要能力，失败表明 skill 不完整）
│   ├── 配对前后比较（配对识别）
│   ├── 混合设计（交互效应优先）
│   └── 分类变量比较（期望频数判断）
│
└── P2 条件允许时通过 Case（覆盖全面性）
    ├── 重复测量（球形假设处理）
    ├── 三组以上比较（事后检验选择）
    ├── 相关/回归分析
    ├── ICC 信度分析
    └── SPSS 截图解读
```

---

## 二、评测维度定义（6个核心维度）

### 维度 1：流程正确性（40分）

检查模型是否**按序**执行以下步骤：
- `asks_clarifying_questions`：在信息不足时先提问，而不是直接分析
- `outputs_statistical_path`：明确输出统计路径判定（路径名 + 候选方法）
- `validates_assumptions`：在执行检验前，先验证前提假设（正态性/方差齐性/球形假设）
- `selects_method_after_validation`：基于前提检验结果选择方法，而非预设

### 维度 2：统计方法正确性（30分）

检查方法选择的科学性：
- `correct_method_for_design`：是否根据研究设计（独立/配对/重复测量）选择正确方法
- `parametric_vs_nonparametric`：参数与非参数方法的切换是否有检验依据
- `correct_posthoc_test`：事后检验选择是否与方差齐性结果匹配（Tukey vs Games-Howell）
- `correct_effect_size_metric`：效应量指标是否与方法匹配（d_z vs d_s；η² vs ω²）
- `sphericity_handled`：重复测量设计中是否处理了球形假设

### 维度 3：输出完整性（20分）

检查输出是否包含所有论文必要元素：
- `provides_statistical_path`：输出统计路径判定
- `provides_assumption_report`：输出前提假设检验结果
- `provides_method_rationale`：说明方法选择理由
- `provides_effect_size_with_ci`：效应量 + 95% CI（不仅是 p 值）
- `provides_paper_style_summary`：输出论文式 Methods/Results 段落
- `provides_three_line_table`：提供三线表建议
- `provides_code`：提供 Python 和/或 SPSS 代码

### 维度 4：风险控制能力（10分）

检查模型是否能识别并处理高风险情境：
- `rejects_insufficient_info`：信息不足时停止推断，提出补充请求
- `corrects_wrong_method`：用户指定错误方法时先纠偏，给出理由和替代方案
- `warns_on_forced_execution`：即使执行用户坚持的方法，也保留风险提醒
- `no_fabrication`：不编造软件版本、效应量数值、研究设计
- `distinguishes_statistical_clinical`：区分统计显著性与临床意义

### 维度 5：数据科学诚实性（加分项，最高 +10分）

- `mentions_limitations`：主动说明分析局限性
- `offers_sensitivity_analysis`：提示需要敏感性分析的场景
- `correct_multiple_comparison`：多重比较场景中提醒校正的必要性
- `cross_validation_awareness`：说明 SPSS 与 Python 交叉验证的价值

### 维度 6：格式与规范性（加分项，最高 +5分）

- `apa7_format`：p 值格式（无前导零、< .001 而非 = 0.000）
- `effect_size_interpretation`：提供效应量的量化解释（小/中/大参照标准）
- `ci_reported`：95% CI 格式正确（方括号，与统计量精度一致）

---

## 三、通过标准定义

### 最低通过标准（硬性要求）

每个 Case 必须满足以下所有硬性检查项，**任一缺失即判为失败**：

```
MUST_PASS = [
    "asks_clarifying_questions",          # 有澄清行为（除非输入信息极其完整）
    "outputs_statistical_path",           # 有统计路径判定输出
    "validates_assumptions",              # 有前提假设验证（或明确说明无法验证的原因）
    "correct_method_for_design",          # 方法与研究设计匹配
    "provides_paper_style_summary",       # 有论文式输出
    "no_fabrication"                      # 无虚构信息
]
```

### 分级评分标准

| 分级 | 分数范围 | 判定 |
|---|---|---|
| 优秀（Pass+）| 90–105 分 | Skill 运行良好，可投入使用 |
| 通过（Pass）| 75–89 分 | 满足基本要求，建议优化 |
| 边缘（Marginal）| 60–74 分 | 核心能力存在缺陷，需修复后重测 |
| 失败（Fail）| < 60 分 | Skill 退化，禁止使用直到修复 |

---

## 四、Case 分类与测试优先级

### P0 Case（必须全部通过）

| Case ID | 场景描述 | 核心检查点 |
|---|---|---|
| P0-A | 两独立组连续变量（标准路径）| 澄清 → 前提检验 → 方法选择 → 效应量 |
| P0-B | 用户指定偏态数据做 t 检验 | 是否拒绝直接执行 + 替代方案 + 风险提醒 |
| P0-C | 信息不完整（只说"有数据想分析"）| 是否停下来提问而不是强行推断 |

### P1 Case（强烈建议通过）

| Case ID | 场景描述 | 核心检查点 |
|---|---|---|
| P1-D | 配对前后比较 | 识别配对 + 使用 d_z 而非 d_s |
| P1-E | 混合设计（组别×时间）| 交互效应优先报告 + 简单效应分析 |
| P1-F | 分类变量比较 | 期望频数检查 + Fisher vs 卡方判断 |
| P1-G | SPSS 截图无原始数据 | 明确说明无法重算 + 提供数据需求清单 |

### P2 Case（覆盖全面性）

| Case ID | 场景描述 | 核心检查点 |
|---|---|---|
| P2-H | 三组以上独立比较 | 事后检验选择（方差齐 vs 不齐）|
| P2-I | 重复测量多时间点 | Mauchly 球形检验 + GG/HF 校正 |
| P2-J | 相关分析（Pearson/Spearman）| 正态性判断 + 95% CI + 不能推断因果 |
| P2-K | ICC 信度分析 | 模型类型选择 + Koo&Mae 解释标准 |
| P2-L | 多元线性回归 | VIF + Cook's D + 残差诊断 |
| P2-M | Logistic 回归 | OR vs B + HL 检验 + AUC |
| P2-N | 三线表生成 | 效应量列 + 表注完整性 + 无竖线 |

---

## 五、失败判定示例（遇到即直接判 Fail）

以下行为**任一出现**，对应 Case 直接判为 Fail，且该行为需在 SKILL.md 中标注为待修复：

```
INSTANT_FAIL_CONDITIONS = [
    "用户提供数据后直接输出统计结果，跳过澄清和前提验证",
    "用户说'做t检验'，模型不判断前提直接执行",
    "把配对样本当独立样本处理（或反之）",
    "明显偏态数据（SW p<0.05）直接用均值±标准差和t检验，无任何说明",
    "重复测量设计不检验球形假设",
    "ANOVA总体显著后不做事后检验",
    "只报告p值，主要结局不报告效应量",
    "配对设计效应量使用d_s而非d_z",
    "编造用户未提供的软件版本/效应量数值/研究结论",
    "将p<0.05直接等同于临床有效",
    "无原始数据但声称已完成Python重算",
    "多重比较场景（≥3个检验）未提醒校正必要性"
]
```

---

## 六、evals.json 推荐结构规范

```json
{
  "skill_name": "thesis-data-analysis",
  "version": "2.0",
  "last_updated": "2026-03",
  "cases": [
    {
      "id": "P0-A-independent-groups",
      "priority": "P0",
      "category": "差异比较-两独立组",
      "prompt": "...",
      "context": {
        "study_design": "RCT",
        "n_groups": 2,
        "sample_type": "independent",
        "outcome_type": "continuous"
      },
      "expected_checks": {
        "must_pass": ["asks_clarifying_questions", "outputs_statistical_path", ...],
        "should_pass": ["provides_effect_size_with_ci", "provides_code"],
        "bonus": ["mentions_limitations", "offers_sensitivity_analysis"]
      },
      "instant_fail_if": ["runs_analysis_without_clarification", "no_assumption_check"],
      "scoring": {
        "process_correctness": 40,
        "method_correctness": 30,
        "output_completeness": 20,
        "risk_control": 10
      },
      "notes": "重点检查Levene检验后的t/Welch选择，以及Cohen's d的报告"
    }
  ]
}
```

---

## 七、评测执行流程

### 7.1 单次 Case 评测步骤

```
Step 1  →  向模型发送 prompt（不加任何提示）
Step 2  →  等待模型完整输出（不打断）
Step 3  →  对照 MUST_PASS 清单逐项检查（布尔值）
Step 4  →  计算各维度得分
Step 5  →  记录 Instant Fail 条件是否触发
Step 6  →  综合评分，写入结果
Step 7  →  如有失败，记录失败模式（供 SKILL.md 修复参考）
```

### 7.2 回归测试触发条件（何时必须重跑评测）

以下任一情况发生后，必须重跑所有 P0 和 P1 Case：

- 修改了 SKILL.md 中的任何流程规则
- 修改了统计方法判断逻辑
- 修改了效应量报告要求
- 升级了 Claude 模型版本
- 用户反馈出现新的系统性错误模式

---

## 八、评测结果记录模板

```
评测日期：____
Skill 版本：____
模型版本：____
评测人：____

| Case ID | 优先级 | MUST_PASS 全过？ | 即时失败触发？ | 总分 | 判定 | 失败原因（如有）|
|---|---|---|---|---|---|---|
| P0-A | P0 | ✅ / ❌ | 否 / 是（说明）| XX/100 | Pass/Fail | |
| P0-B | P0 | | | | | |
| ...  | | | | | | |

**本次评测总结**：
- P0 Case 全部通过：是 / 否
- P1 Case 通过率：X/Y
- P2 Case 通过率：X/Y
- 发现的新失败模式：
- 建议修改的 SKILL.md 条目：
```

---

## 九、维护建议

**短期（每次 SKILL.md 变更后）**
- 必须重跑全部 P0 Case（3个）
- 建议重跑全部 P1 Case（4个）

**中期（每月或每季度）**
- 补充 1–2 个新 Case（覆盖用户真实反馈中出现的新错误模式）
- 更新评分权重（根据实际使用中哪类错误影响最大）

**长期（Skill 大版本更新时）**
- 重新校准所有 Case 的期望输出
- 验证新增功能（如新统计方法支持）不破坏原有能力
- 更新 instant_fail 条件列表（随统计规范演进调整）
