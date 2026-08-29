# 2024 CUMCM B 题问题二

程序实现 Q2-M2 吸收 Markov 奖励模型，枚举表 1 每个情形的 16 个固定策略 `(x1, x2, y, z)`：两个 `x` 表示零件检测，`y` 表示成品检测，`z` 表示拆解已知不合格品。

状态为 `(phase,z1,z2,k1,k2,o1,o2)`，同时记录零件的真实质量、已知信息和新购/拆回来源。已检合格且保留的零件不重复检测；拆回件保留真实质量，并按固定策略重新检测。

核算单位为“每最终交付一件合格品”：售价只计一次，调换损失不含替换品本身的生产成本。

## 运行

```bash
cd B题/代码
python -m pip install -r q2/requirements.txt
python -m q2.run_q2
python -m unittest q2.test_q2 -v
```

主程序使用正概率边的 SCC 判定闭合暂态类，再计算谱半径与吸收裕度。裕度不大于 `1e-10` 时标记 `NEAR_NONABSORBING`，用 80 位精度同时复核谱半径和全部奖励方程；高精度求解未通过的策略不得参与选优。数值阈值不参与图结构分类。

## 输出

结果位于 `B题/代码/results/q2/`：

- `all_policies.csv`：96 个策略的状态、谱信息、成本分项和事件次数。
- `best_policies.csv`：各情形最优策略，并列解全部保留。
- `state_table.csv` 和 `transition_edges.csv`：可追溯的状态/边表，状态表同时包含本步成本和事件奖励。
- `sensitivity.csv`：检测、调换和拆解费用的单因素分析，范围依据为表 1 已观测值。
- `structural_comparison.csv`：物理质量保持与传统质量重置近似的结构对照。
- `summary.json` 和 `run_metadata.json`：汇总、版本、配置与 SHA-256 哈希。
- `best_profit_by_case.png/.svg`：各情形最优期望利润图。

`SUCCESS_EXACT` 表示闭环最终吸收；`NON_ABSORBING` 表示存在无成功泄漏的可达闭合类。`factory_defect_rate` 是进入市场的成品中次品的期望比例；`exchange_rate` 是每订单期望调换次数，不是“至少调换一次”的概率。

## 论文候选图

绘图入口只读取现有 Q2 CSV/JSON，不重新枚举策略或求解 Markov 奖励方程：

```bash
cd B题/代码
python -m q2.plot_q2
```

新增图保存在 `results/q2/figures/`，改进后的最优利润图仍保存为
`results/q2/best_profit_by_case.svg/.png`。数据源、结论边界、中文图注和渲染检查状态见
`results/q2/figure_index.json`。默认使用 `Noto Serif CJK SC`，英文数字回退为
`Liberation Serif`，数学符号使用 STIX。

图中的“最优”只指表 1 名义参数下预先声明的 16 个固定二元策略；非吸收策略不参与利润比较，
不代表历史自适应策略空间中的全局最优。质量重置模式仅用于结构敏感性对照，主结论仍以拆解后
保持零件真实质量的模型为准。
