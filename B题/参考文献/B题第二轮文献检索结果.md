---
title: B题第二轮文献检索结果
date: 2026-08-27 21:06
problem: 2024-CUMCM-B
stage: 1.5a-literature-search-round2
status: fulltext-deep-read-complete
search_calls_round2: 2
cumulative_websearch_calls: 5
retained_candidates: 8
new_distinct_candidates: 7
recovered_candidates: 1
fulltexts_verified: 8
metadata_records_repaired: 2
---

# B题第二轮文献检索结果

关联：[[国赛练习题/CUMCM2024Problems/B题/问题分析/B题文献覆盖度评估.md|覆盖度评估]] · [[国赛练习题/CUMCM2024Problems/B题/参考文献/B题文献检索结果.md|第一轮检索结果]] · [[国赛练习题/CUMCM2024Problems/B题/参考文献/文献语料清单.md|当前全文语料清单]]

> [!success] 第二轮检索结论
> 围绕第一轮暴露出的三个硬缺口——**Q1 可选停止有效性、Q2 返工/回收循环、Q3 非串行装配树与拆解回流**——共保留 8 篇高相关候选文献：7 篇为新增文献，1 篇为第一轮已命中但未取得全文的 Kakade et al. (2004)。其中 Q1 的理论缺口与 Q3 的非串行/拆解树缺口得到显著补强；Q2 的客户退换—补产闭环仍没有完全同构文献。

> [!success] 全文精读状态更新
> 8 篇候选现均已核验为完整正文并完成第二轮精读；Howard 与 Yaacoub 原一页馆藏记录已替换为开放全文。候选阶段的待下载/摘要级状态已被全文结论取代。详见 [[国赛练习题/CUMCM2024Problems/B题/问题分析/第二轮文献精读报告.md|第二轮文献精读报告]] 和 [[国赛练习题/CUMCM2024Problems/B题/问题分析/B题文献覆盖度评估.md|更新后覆盖度评估]]。

## 1. 第二轮检索目标

| 第一轮缺口 | 第二轮检索方向 | 判定标准 |
|---|---|---|
| Q1 固定时点置信区间不能直接支撑“边抽边停” | Bernoulli confidence sequence、time-uniform inference、optimal stopping | 区间在任意停止时刻仍有效，或直接优化 Bernoulli 区间估计的停止时间 |
| Q2 只算首次装配，缺少返工/回收循环 | manufacturing error recovery、semi-Markov、rework/recovery strategy | 显式描述故障后恢复、部分回收、长期收益或吞吐率 |
| Q3 串行检测不能代表多子件汇合 | nonserial production inspection、assembly/disassembly tree、stochastic DP | 显式使用非串行生产网络、产品树或拆解树，并给出可执行算法 |
| 第一轮缺失全文 | Kakade et al. (2004) 精确题名回查 | 核实正式出版页、DOI、卷期页码和方法摘要 |

## 2. 检索过程与停止条件

solver Stage 1.5a 将 WebSearch 总次数限制为 5 次。第一轮已使用 3 次，本轮使用剩余 2 次后停止扩展。

| 累计轮次 | 本轮用途 | 核心检索式 | 结果 |
|---:|---|---|---|
| 4 | 缺口导向扩检 | `nonserial inspection allocation assembly`；`manufacturing inspection disassembly rework recovery optimization`；`Bernoulli confidence sequence optional stopping`；Kakade 精确题名 | 命中非串行检测、随机恢复、产品拆解树、Bernoulli 序贯区间及 Kakade 正式出版页 |
| 5 | 精确题名与元数据回查 | Yum & McDowell；Teunter；Yaacoub；Howard 等精确题名 | 核实 DOI、正式出版信息、开放全文入口与方法摘要 |

书目信息另用 Crossref DOI 元数据逐项复核；未继续进行宽泛扩展，以避免偏离题意和重复命中。

## 3. 保留的 8 篇候选文献

### 3.1 汇总表

|    # | 文献                                                                                                                  | 核心方法（摘要级）                                                              | 主要补强问题            | 与题目仍不一致之处                       | 全文入口状态           |
| ---: | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------- | ------------------------------- | ---------------- |
| R2-1 | Howard et al. (2021), *Time-uniform, nonparametric, nonasymptotic confidence sequences*                             | 构造对所有时间同时有效的非参数、非渐近置信序列，将集中不等式、LIL 与序贯检验统一起来                           | Q1；兼顾 Q4          | 不直接给出本题“95% 拒收/90% 接收”的经济停止规则   | 本地全文已核验（26 页；修复）    |
| R2-2 | Yaacoub, Moustakides & Mei (2019), *Optimal Stopping for Interval Estimation in Bernoulli Trials*                   | 对序贯 Bernoulli 样本联合设计停止时间与区间中心，在覆盖约束下研究平均样本量；采用半贝叶斯表述                   | Q1                | 研究的是区间估计，不是本题的双阈值验收；先验设定需另行解释   | 本地全文已核验（22 页；修复） |
| R2-3 | Britney (1972), *Optimal Screening Plans for Nonserial Production Systems*                                          | 对一般 $n$ 阶段非串行生产网络，以检验、修复和漏出缺陷的总期望成本为准则；用吸收 Markov 链刻画缺陷物流，并用分支定界搜索检测方案 | Q3；部分 Q2          | 没有客户退换和拆解后重复装配；年代较早，需核对符号与假设    | 本地全文已核验     |
| R2-4 | Yum & McDowell (1981), *The Optional Allocation of Inspection Effort in a Class of Nonserial Production Systems*    | 直接研究一类非串行生产系统中的检验力度配置                                                  | Q3                | 全文证实为无回路网络；拒绝品恢复良品，不处理客户退换或拆解复装      | 本地全文已核验     |
| R2-5 | Kakade, Valenzuela & Smith (2004), *An Optimization Model for Selective Inspection in Serial Manufacturing Systems* | 在串行多阶段装配线上配置各阶段选择性检验力度，权衡产出率与检验准确性，并用模拟退火求解                            | Q2/Q3 的检测配置       | 仍是串行结构，且无拆解回流；是第一轮已命中但缺全文的“追回项” | 本地全文已核验（21 页）  |
| R2-6 | Kao (1995), *Optimal Recovery Strategies for Manufacturing Systems*                                                 | 用半 Markov 模型描述自动化单服务台装配中的随机故障恢复，比较完全/部分恢复并优化吞吐或利润                      | Q2 的循环与长期核算       | “故障恢复”不等于客户退货；零件质量后验和拆解树未覆盖     | 本地全文已核验     |
| R2-7 | Meacham, Uzsoy & Venkatadri (1999), *Optimal Disassembly Configurations for Single and Multiple Products*           | 在层级产品树上求收益最大化的拆解配置；单产品情形给出线性时间算法，并扩展到固定成本、容量和需求约束                      | Q3 的产品树、拆解深度与回收价值 | 面向拆解规划而非生产检验；没有质量抽样与重新装配循环      | 本地全文已核验     |
| R2-8 | Teunter (2006), *Determining Optimal Disassembly and Recovery Strategies*                                           | 在给定拆解树、过程相关质量分布和质量相关回收收益下建立随机动态规划，允许不同拆解过程与部分拆解                        | Q3；部分 Q2/Q4       | 主要面向回收处置，未直接含生产补料、成品替换与复装       | 本地全文已核验（5 页）    |

> [!note] 关于 R2-4 的题名
> 出版社与 Crossref 均登记为 **The Optional Allocation...**，本报告保留正式元数据中的 “Optional”，不擅自改成 “Optimal”。

### 3.2 规范书目信息与入口

1. Howard S R, Ramdas A, McAuliffe J, et al. Time-uniform, nonparametric, nonasymptotic confidence sequences[J]. *The Annals of Statistics*, 2021, 49(2): 1055–1080. DOI: [10.1214/20-AOS1991](https://doi.org/10.1214/20-AOS1991). [arXiv](https://arxiv.org/abs/1810.08240).
2. Yaacoub T, Moustakides G V, Mei Y. Optimal stopping for interval estimation in Bernoulli trials[J]. *IEEE Transactions on Information Theory*, 2019, 65(5): 3022–3033. DOI: [10.1109/TIT.2018.2885405](https://doi.org/10.1109/TIT.2018.2885405). [arXiv](https://arxiv.org/abs/1711.06912).
3. Britney R R. Optimal screening plans for nonserial production systems[J]. *Management Science*, 1972, 18(9): 550–559. DOI: [10.1287/MNSC.18.9.550](https://doi.org/10.1287/MNSC.18.9.550).
4. Yum B J, McDowell E D. The Optional Allocation of Inspection Effort in a Class of Nonserial Production Systems[J]. *AIIE Transactions*, 1981, 13(4): 285–293. DOI: [10.1080/05695558108974564](https://doi.org/10.1080/05695558108974564).
5. Kakade V, Valenzuela J F, Smith J S. An optimization model for selective inspection in serial manufacturing systems[J]. *International Journal of Production Research*, 2004, 42(18): 3891–3909. DOI: [10.1080/00207540410001704014](https://doi.org/10.1080/00207540410001704014).
6. Kao J F. Optimal recovery strategies for manufacturing systems[J]. *European Journal of Operational Research*, 1995, 80(2): 252–263. DOI: [10.1016/0377-2217(94)00169-D](https://doi.org/10.1016/0377-2217(94)00169-D).
7. Meacham A, Uzsoy R, Venkatadri U. Optimal disassembly configurations for single and multiple products[J]. *Journal of Manufacturing Systems*, 1999, 18(5): 311–322. DOI: [10.1016/S0278-6125(00)87634-7](https://doi.org/10.1016/S0278-6125(00)87634-7).
8. Teunter R H. Determining optimal disassembly and recovery strategies[J]. *Omega*, 2006, 34(6): 533–537. DOI: [10.1016/j.omega.2005.01.014](https://doi.org/10.1016/j.omega.2005.01.014). [机构库 PDF](https://repub.eur.nl/pub/1195/ei200409.pdf).

## 4. 对各问题的覆盖增量

### Q1：从“固定时点区间”补到“允许边抽边停”

- R2-1 的置信序列在所有采样时刻同时控制覆盖概率，正面处理反复查看数据后停止造成的覆盖失真。
- R2-2 直接以 Bernoulli 序列为对象，同时设计停止时间和区间估计，可为“检测次数尽可能少”提供更贴近题意的理论文献。
- 两篇仍没有替本题决定 $p_0,p_1$、拒收/接收风险如何分配，也不能仅凭摘要给出最终抽样规则。

### Q2：从“一次装配成本”补到“恢复过程的长期评价”

- R2-6 引入半 Markov 恢复过程和长期吞吐/利润，使“出错—恢复—继续生产”的循环不再被当作一次性成本。
- R2-3 同时计入检验、修复和漏出缺陷成本，可补充零件/工序筛查后的概率流描述。
- R2-5 可补检测力度与产出率的连续权衡。
- 仍缺一篇完全同构地同时包含**用户退回、免费调换、补产、拆解回收件再装配**的文献，因此 Q2 仍需自行建立闭环守恒关系。

### Q3：从“串行生产线”补到“非串行网络 + 拆解树”

- R2-3、R2-4 明确研究非串行生产系统，可弥补第一轮文献全部偏串行的结构缺陷。
- R2-7 用产品层级树决定拆哪些节点以及回收价值，为父子节点关系和拆解深度提供文献入口。
- R2-8 在拆解树上进一步加入质量随机性、回收选择和动态规划，是当前候选中与“半成品/成品拆解回流”最接近的一篇。
- 这些文献分别覆盖检测网络或拆解树，仍未在同一模型中完成“装配—检测—拆解—回到子节点—再次装配”的全循环。

### Q4：理论不确定性得到补强，但系统集成仍是瓶颈

- R2-1 可避免在不固定样本量时误用普通置信区间；R2-2 可量化覆盖概率与平均样本量的权衡。
- R2-8 的过程相关质量分布提示：回收件质量不能继续当作无条件原始次品率。
- 仍未找到把多节点后验分布直接传入完整装配树回流模型的端到端论文，因此 Q4 的主要瓶颈仍是先把 Q2/Q3 建对。

## 5. 覆盖度预期（待全文核验）

| 子问题 | 第一轮已核验覆盖 | 第二轮候选全文若通过审查 | 预期增量 | 主要新增证据 |
|---|---:|---:|---:|---|
| Q1 | 60% | 80% | +20 | time-uniform confidence sequence；Bernoulli optimal stopping |
| Q2 | 45% | 65% | +20 | semi-Markov recovery；nonserial defective-flow accounting |
| Q3 | 40% | 75% | +35 | nonserial inspection；product/disassembly tree；stochastic DP |
| Q4 | 70% | 75% | +5 | 任意时刻有效推断；过程相关质量分布 |
| **等权总体** | **54%** | **约 74%** | **约 +20** | — |

> [!important] 解释
> 表中的 80%/65%/75%/75% 是“候选文献被成功取得且全文内容与摘要一致”时的工程预期，不应提前写入论文作为已验证覆盖结论。

## 6. 未纳入主清单的候选及原因

| 候选 | 处理 | 原因 |
|---|---|---|
| *Performance of Test Supermartingale Confidence Intervals for the Success Probability of Bernoulli Trials* (arXiv:1709.04078) | 备选 | 对可选停止很相关，但与 R2-1 的现代置信序列框架重叠；可在精读 Q1 时补充 |
| *Optimizing integrated manufacturing and products inspection policy for deteriorating manufacturing system with imperfect inspection* (2015) | 暂不保留 | 重点是设备劣化、维护与不完美检验，不是本题装配树回流 |
| *An optimal production and inspection strategy with preventive maintenance error and rework* (2013) | 暂不保留 | 维护/库存占主导，Q2 的拆解与退换关联较弱 |
| 2025 年与本赛题场景高度同构的多阶段抽样/拆解论文 | 不作为主证据 | 可能由赛题衍生，存在循环引用与方法质量风险；仅可作为复现对照 |
| 2026 年废旧产品并行拆解序列规划论文 | 暂不保留 | 更偏 EOL 拆解排序，不直接解决生产检测与再装配 |

## 7. 下载与精读优先级

### P0：先下载

1. **R2-1 Howard et al. (2021)**：Q1 可选停止有效性的核心现代来源，已有开放全文。
2. **R2-2 Yaacoub et al. (2019)**：Q1 最小样本量目标的直接 Bernoulli 序贯来源，已有开放全文。
3. **R2-8 Teunter (2006)**：Q3 随机拆解树与回收策略的核心来源，已有机构库 PDF。
4. **R2-3 Britney (1972)**：Q3 非串行生产网络与缺陷流的直接来源。
5. **R2-6 Kao (1995)**：Q2 长期恢复循环的核心来源。

### P1：随后下载

6. R2-7 Meacham et al. (1999)：产品树算法与拆解价值。
7. R2-4 Yum & McDowell (1981)：非串行检验力度配置，需全文确认细节。
8. R2-5 Kakade et al. (2004)：第一轮遗漏全文的追回项，用于串行检测配置对照。

批量 DOI 已写入 [[国赛练习题/CUMCM2024Problems/B题/参考文献/B题第二轮论文DOI清单.txt|B题第二轮论文DOI清单]]。

## 8. 下一阶段验收标准

每篇下载并转为 Markdown 后，至少核验：

1. 目标函数按“每投入件、每周期、每合格交付件”中的哪一种口径定义；
2. 缺陷品被检测后是报废、返工、修复还是拆解，是否允许再次进入系统；
3. 回收件质量是无条件、条件分布还是可观测状态；
4. 非串行网络是否支持多子件汇合以及严格物料守恒；
5. 算法是否给出状态、转移、边界条件、复杂度和可复现实验；
6. Q1 方法是否保证可选停止下的覆盖，而不是仅在预先固定的 $n$ 上成立。

通过上述核验后，再更新 [[国赛练习题/CUMCM2024Problems/B题/参考文献/文献语料清单.md|文献语料清单]] 和 [[国赛练习题/CUMCM2024Problems/B题/问题分析/B题文献覆盖度评估.md|覆盖度评估]]。
