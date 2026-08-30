# F002_Q1Q4_Data_Figure_Requirements_v1.0

**文档用途**：问题一（Q1）与问题四（Q4）数据图制作需求说明  
**适用范围**：2024 CUMCM B 题论文数据图制作  
**状态**：READY_FOR_TEAMMATE  
**当前结果基线**：`aa4037a28c4cf4ae151dbdb717bea80a3196cce2`

**说明**：
- 本文件仅整理需要队友通过代码结果制作的数据图；
- 不包含论文手自行制作的结构图/流程图；
- Q1 当前结果状态为 `SUCCESS_LOCAL_CALIBRATION`，不得表述为理论全局最优；
- Q4 当前证据仍为 `DEMO_ONLY_NOT_OFFICIAL_DATA`，相关图只能作为显式情景/算法结果展示，不能表述为企业实测正式结论；
- Q4 稳健结果当前为 `ROBUST_NUMERICAL`，不得写成 `ROBUST_CERTIFIED`。

---

# 一、问题一（Q1）数据图需求

## 总表

| 图编号 | 核心结论（一句话） | 图类型 | 数据来源 | 优先级 | 预期位置 |
|---|---|---|---|---|---|
| **Fig.Q1-1** | 主情景下序贯规则随累计样本数与累计次品数划分为接收、继续和拒收三区，并在 \(N_{\max}=968\) 处强制二元终止，不再存在旧模型的“未决”结果。 | 决策区域图 / 双边界阶梯图 | `results/q1/decision_boundaries.csv` + `results/q1/sequential_plans.csv` | **必须** | Q1 模型求解结果开头 |
| **Fig.Q1-2** | 新序贯方案同时满足 AQL 端生产方风险不超过 5% 和 LTPD 端使用方风险不超过 10%，且 ASN 最大值出现在 \(p_0,p_1\) 之间的灰区而非端点。 | 双面板曲线图：(a) OC；(b) ASN–\(p\) | `results/q1/operating_characteristics.csv` | **必须，核心图** | Q1 性能分析 |
| **Fig.Q1-3** | 质量分辨率 \(p_1-p_0\) 越小，所需样本量显著增加；适度放宽截尾倍率 \(\kappa\) 可以用更大的极端最大样本数换取更低的灰区最坏 ASN。 | 双面板热力图：(a) 灰区最坏 ASN；(b) 相对固定抽样节省率 | `results/q1/sequential_plans.csv` | **强烈建议** | Q1 敏感性分析 |
| **Fig.Q1-4** | 固定一次抽样与序贯抽样在相同双风险约束下具有不同样本负担，序贯方案的优势主要体现在期望抽检量而不是单纯降低最大样本量。 | 固定基线 vs 序贯方案对比图 / 哑铃图 | `results/q1/fixed_binomial_baselines.csv` + `results/q1/sequential_plans.csv` | 推荐，可与表格二选一 | Q1 结果讨论 |

## Fig.Q1-1 序贯接收—继续—拒收决策区域图

### 图名建议
**问题一主情景下序贯验收决策边界**

### 主情景
仅画：

\[
p_0=0.10,\qquad p_1=0.13,\qquad \kappa=1.
\]

对应：

\[
N_{\max}=968.
\]

### 坐标轴
横轴：

\[
n=\text{累计抽检数}
\]

纵轴：

\[
k=\text{累计次品数}
\]

### 必须展示
- 接收区域；
- 继续抽样区域；
- 拒收区域；
- 接收边界 \(a_n\)；
- 拒收边界 \(r_n\)；
- \(N_{\max}=968\) 截尾线。

### 数据字段
从 `decision_boundaries.csv` 读取：
- `n`
- `k_accept_max`
- `k_reject_min`
- `terminal`

从 `sequential_plans.csv` 读取：
- `p1`
- `kappa`
- `N_max`
- `c_N`
- `plan_hash`

### 关键修改
**禁止继续使用旧 Q1 图中的 `UNDECIDED_CAP`。**

新模型终止时只能：

\[
A=\text{接收},\qquad R=\text{拒收}.
\]

到达截尾点以后必须强制二元处置。

---

## Fig.Q1-2 OC 与 ASN 双面板图

### 图名建议
**问题一主情景的操作特性与平均抽样量**

推荐做成一张双面板：
- (a) 操作特性（OC）
- (b) 平均抽样量（ASN）

### (a) OC 曲线
横轴：

\[
p=\text{真实次品率}
\]

纵轴：

\[
P_{\mathrm{accept}}(p)
\]

可同时画：

\[
P_{\mathrm{reject}}(p)=1-P_{\mathrm{accept}}(p)
\]

但**不再画“未决概率”曲线**。

必须标出：

\[
p_0=0.10,\qquad p_1=0.13
\]

并建议在图中或图注标出：

\[
P_{0.10}(R)=0.0489132<0.05
\]

\[
P_{0.13}(A)=0.0995966<0.10.
\]

### (b) ASN 曲线
横轴同样为：

\[
p
\]

纵轴：

\[
ASN(p).
\]

建议将：

\[
[p_0,p_1]=[0.10,0.13]
\]

用浅色背景标记为“无差异区”，并重点标注：

\[
p_{\mathrm{worst}}\approx0.112375
\]

\[
J_{\mathrm{ASN}}\approx923.1035.
\]

### 图要表达的关键点
真正最难判定的位置并不在 \(p_0\) 或 \(p_1\)，而位于二者之间。

P50/P90/P99 可放附录或小表，不建议全部塞入主图。

---

## Fig.Q1-3 \(p_1-\kappa\) 双重敏感性图

### 图名建议
**问题一质量分辨率与截尾倍率的抽样效率敏感性**

建议做成两个并排 \(4\times4\) 热力图。

### 行
\[
p_1=0.12,\ 0.13,\ 0.15,\ 0.20
\]

### 列
\[
\kappa=1,\ 1.25,\ 1.5,\ 2
\]

### 左面板
每格展示：

\[
J_{\mathrm{ASN}}
=
\max_{p\in[p_0,p_1]}ASN(p)
\]

对应字段：`J_ASN_grid`

### 右面板
每格展示：

\[
\text{ASN saving vs fixed}
\]

对应字段：`ASN_saving_vs_fixed`

例如 \(p_1=0.13\)：

| \(\kappa\) | \(N_{\max}\) | 最坏 ASN | 相对固定抽样节省 |
|---:|---:|---:|---:|
| 1.00 | 968 | 923.10 | 4.64% |
| 1.25 | 1210 | 808.84 | 16.44% |
| 1.50 | 1452 | 767.82 | 20.68% |
| 2.00 | 1936 | 727.88 | 24.81% |

### 表述限制
- \(p_1=0.13\) 为基准情景，不是题面直接给定；
- \(\kappa\) 为工程设计参数；
- 不得写成“证明 \(\kappa=2\) 全局最优”；
- 当前结果状态为 `SUCCESS_LOCAL_CALIBRATION`。

---

## Fig.Q1-4 固定抽样与序贯抽样对比图

### 图名建议
**相同双风险约束下固定抽样与序贯抽样的样本负担比较**

### 推荐展示指标
每个 \(p_1\) 至少展示：
- 固定样本量 \(n_F\)
- 序贯方案灰区最坏 ASN
- 序贯方案最大样本量 \(N_{\max}\)

重点应放在：

\[
n_F\quad vs\quad ASN
\]

而不是只比较 \(n_F\) 与 \(N_{\max}\)。

若正文版面不足，可改为表格。

---

# 二、问题四（Q4）数据图需求

## 总表

| 图编号 | 核心结论（一句话） | 图类型 | 数据来源 | 优先级 | 预期位置 |
|---|---|---|---|---|---|
| **Fig.Q4-1** | 在当前显式演示抽样数据与检测成本下，Q2 六种情形中“立即停止抽样”的价值均高于继续检测任一质量参数，因此最优初始动作均为 STOP。 | 动作价值差热力图 | `results/q4/q2_voi_policy_summary.csv` | **必须** | Q4 序贯 VOI 结果 |
| **Fig.Q4-2** | Q3 中所有可追加检测参数的净 KG 均小于 0，而 STOP 的净值为 0，因此当前演示情景下继续获取信息不具经济价值。 | 横向条形图 / 森林图，Uniform 与 Jeffreys 双面板 | `results/q4/q3_kg_action_values.csv` | **必须** | Q4-Q3 抽样决策结果 |
| **Fig.Q4-3** | Bayesian 终止策略与数值稳健策略在部分情形下发生切换，体现“后验期望收益”与“最坏情形保护”之间的取舍。 | 分组柱状图 + 策略切换标记 | `results/q4/robust_audit.csv` | **强烈建议** | Q4 稳健审计 |
| **Fig.Q4-4** | 当前 STOP 结论依赖于假设的追加检测成本，应进一步考察检测成本变化何时使 STOP 切换为继续抽样。 | 成本敏感性曲线 / 相图 | 需要额外情景运行；当前结果文件不足 | **若 Q4 演示数值进入正文，则强烈建议补做** | Q4 敏感性分析 |
| Fig.Q4-A1 | 固定样本形成的 90%/95% 联合区间展示参数估计不确定程度，并为稳健审计提供矩形不确定集。 | 误差棒 / forest plot | `results/q4/simultaneous_intervals.csv` | 附录优先 | Q4 稳健审计前或附录 |

## Fig.Q4-1 Q2 初始动作价值差热力图

### 图名建议
**演示抽样情景下问题二各生产情形的追加抽样动作价值**

### 推荐结构
行：
- 情形1-Uniform
- 情形1-Jeffreys
- …
- 情形6-Uniform
- 情形6-Jeffreys

列：
- STOP
- 检测 p1
- 检测 p2
- 检测 pf

### 画什么数值
建议统一画：

\[
\Delta Q_a=Q_a(s)-G(s)
\]

其中：

\[
G(s)=Q_{\mathrm{STOP}}(s).
\]

因此：
- STOP 对应 0；
- \(\Delta Q_a>0\)：继续抽样优于立即停止；
- \(\Delta Q_a<0\)：继续抽样不划算。

### 数据字段
从 `q2_voi_policy_summary.csv` 读取：
- `case`
- `prior`
- `initial_action`
- `stop_value`
- `policy_value`
- `NVSI`
- `initial_action_values`
- `expected_additional_samples`
- `terminal_policy`

### 当前结果特征
当前所有 Q2 情形、两种先验均为：
- `initial_action = STOP`
- `expected_additional_samples = 0`
- `NVSI = 0`

### 图注限制
必须注明：

**“演示抽样情景下”**

不能写成“企业正式最优检测决策”。

---

## Fig.Q4-2 Q3 各参数净 KG 图

### 图名建议
**演示抽样情景下问题三各质量参数的边际净信息价值**

### 推荐形式
两个并排横向条形图：
- (a) Uniform prior
- (b) Jeffreys prior

### 纵轴
- 零件1–8
- 半成品1–3
- 最终成品

### 横轴
\[
\text{Net KG}
\]

必须加：
\[
\text{Net KG}=0
\]
参考线。

### 数据字段
从 `q3_kg_action_values.csv` 读取：
- `prior`
- `action`
- `action_value`
- `action_SE`
- `net_KG`
- `net_KG_CI_lower`
- `net_KG_CI_upper`
- `recommended`
- `status`
- `stop_production_policy`
- `stop_value`
- `EVPI`

### 误差棒
建议使用：

\[
[\text{net\_KG\_CI\_lower},\text{net\_KG\_CI\_upper}]
\]

作为横向误差棒。

### 当前结果特征
- 零件检测 Net KG 大约为 \(-1\) 或 \(-2\)
- 半成品约为 \(-35\sim-38\)
- 最终成品约为 \(-106\)

### 表述限制
Q3 使用 `myopic-KG`，因此只能写：

> 成本敏感一步 KG 给出的推荐动作

不能写：

> 全局最优序贯抽样策略

---

## Fig.Q4-3 Bayesian 终止策略与数值稳健审计比较

### 图名建议
**Bayesian 终止策略与数值稳健策略的最坏利润比较**

### Q2 推荐结构
按情形1–6做分组柱状图：
- Bayesian 终止策略最坏利润
- 数值稳健策略最坏利润

建议：
- 90% 联合集合一个面板
- 95% 联合集合一个面板

若：
\[
d_B\neq d_R
\]
则用 `★` 标记，并标策略位串。

### 重点示例：情形5
Bayesian 策略：
\[
0110
\]

90% 最坏利润：
\[
-2.6397
\]

数值稳健策略：
\[
1101
\]

90% 最坏利润：
\[
1.4537
\]

### Q3
Bayesian 终止策略：
\[
63487
\]

90% 最坏利润：
\[
26.9643
\]

数值稳健策略：
\[
65535
\]

90% 最坏利润：
\[
29.7129
\]

95%：
\[
23.6188\quad vs\quad26.9091
\]

### 数据字段
从 `robust_audit.csv` 读取：
- `domain`
- `coverage`
- `status`
- `bayesian_policy`
- `bayesian_policy_nominal_profit`
- `bayesian_policy_worst_profit`
- `robust_policy`
- `robust_policy_worst_profit`
- `case`
- `claim_scope`

### 重要措辞限制
当前状态为：

`ROBUST_NUMERICAL`

只能写：
- 数值稳健策略
- 数值稳健审计
- 矩形联合不确定集下的数值最坏利润

不能写：
- 严格认证稳健最优
- `ROBUST_CERTIFIED`
- 连续不确定集下已证明的全局稳健最优

---

## Fig.Q4-4 追加检测成本敏感性图

### 当前状态
仓库当前没有足够结果直接绘制，需要额外批量运行。

### 建议敏感性变量
对追加抽样成本设置倍率：

\[
c_j^{(s)}(\lambda)=\lambda c_j^{(s)}.
\]

应由团队预先声明一组 \(\lambda\) 值，不能看完结果以后反向挑选。

### 推荐图
横轴：
\[
\lambda
\]

纵轴可选：
- NVSI
- 期望追加样本数

同时标记初始动作：
- STOP
- SAMPLE p1
- SAMPLE p2
- …

### 最有价值的结果
观察是否存在：

\[
\boxed{\text{STOP}\rightarrow\text{SAMPLE}}
\]

的动作切换。

如果始终 STOP，也应如实报告。

---

## Fig.Q4-A1 联合参数区间图【附录优先】

### 图名建议
**演示固定样本下质量参数的联合置信区间**

### 推荐形式
横向 forest plot。

每个参数展示：
- 样本点估计；
- 90% 联合区间；
- 95% 联合区间。

### 数据
`simultaneous_intervals.csv`

字段：
- `parameter`
- `coverage`
- `lower`
- `upper`
- `method`
- `domain`
- `case`

### 作用
用于说明 Q4-M3 的矩形联合不确定集如何构造，不建议作为 Q4 最主要结果图。

当前固定样本方法为：

`clopper_pearson_fixed_n`

若以后改为 Q4-A3 自适应抽样得到正式证据，则必须换成适应可选停止的 simultaneous confidence sequence，不能继续照搬固定样本区间。

---

# 三、统一制图规范

1. 图题、坐标轴、图例统一使用中文；
2. 数学符号按论文统一记号；
3. 优先导出 SVG，同时保留高分辨率 PNG；
4. 保证黑白打印仍可辨认，不只依赖颜色；
5. 关键策略切换用 `★`、边框或线型再次标记；
6. Q1 不得继续出现：
   - Pareto
   - 未决率
   - `UNDECIDED_CAP`
   - “省样本/平衡/低未决”三方案；
7. Q1 图注应注明：
   - \(p_1\) 与 \(\kappa\) 属于预声明设计情景；
   - 当前最优性口径为 `SUCCESS_LOCAL_CALIBRATION`；
8. Q4 图题/图注必须注明“演示抽样情景”；
9. Q4 不得把 `DEMO_ONLY_NOT_OFFICIAL_DATA` 包装成企业实测；
10. Q4 稳健图只能使用 `ROBUST_NUMERICAL` 的措辞；
11. 所有数据直接从仓库结果文件读取，不手工复制后重新计算；
12. 若结果文件再次更新，应重新核对 commit / source hash 后再生成正式图。

---

# 四、建议制作顺序

## Q1
1. **Fig.Q1-2：OC + ASN 双面板**
2. **Fig.Q1-1：序贯决策区域**
3. **Fig.Q1-3：\(p_1-\kappa\) 敏感性**
4. Fig.Q1-4：固定 vs 序贯，可视版面决定

## Q4
1. **Fig.Q4-1：Q2 动作价值差热力图**
2. **Fig.Q4-2：Q3 净 KG 图**
3. **Fig.Q4-3：数值稳健审计比较**
4. **Fig.Q4-4：追加检测成本敏感性（需先补跑结果）**
5. Fig.Q4-A1：联合区间图，附录优先

---

# 五、当前结论

### Q1
正式数据图体系已经从旧版：

`决策区域 + OC + Pareto + 未决权衡`

重构为：

`决策边界 + OC/ASN + p1-kappa敏感性 + 固定/序贯基线比较`

旧 Pareto 和未决相关图不得继续使用。

### Q4
主图不应再围绕“Bayesian 最优利润是多少”展开，而应围绕：

`是否值得继续获取信息 → 下一件应该检测什么 → 何时停止 → 停止后采用什么生产策略 → 最坏情形下是否需要切换为更稳健策略`

展开。

当前演示结果下，Q2 精确 VOI-DP 与 Q3 myopic-KG 均推荐立即停止追加抽样，因此建议额外补做检测成本敏感性，以验证 STOP 结论对成本参数的依赖程度。
