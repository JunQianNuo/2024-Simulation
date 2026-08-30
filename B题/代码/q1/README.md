# 2024 CUMCM B 题问题一

当前实现对应 `Q1-M6 / Q1-A2`：在 AQL `p0=0.10` 与 LTPD `p1>p0` 两个质量点下，构造生产方风险不超过 0.05、使用方风险不超过 0.10 的二元序贯验收规则。

主流程包括：精确二项固定样本基线、Wald LLR 边界初始化、预声明阈值/截尾网格校准、有限状态路径 DP 精确风险核验，以及 `p1 × kappa` 敏感性。所有路径最迟在 `N_max` 接收或拒收，不存在未决类别。

```bash
cd B题/代码
uv run --with-requirements q1/requirements-q1.txt python -m q1.run_q1
uv run --with-requirements q1/requirements-q1.txt python -m unittest q1.test_q1 -v
```

快速数据流检查可加 `--quick`。正式输出位于 `results/q1/`：

- `fixed_binomial_baselines.csv`：四个 LTPD 情景的固定样本 oracle；
- `sequential_plans.csv`：16 个 `p1 × kappa` 情景的推荐截尾规则与风险、ASN；
- `decision_boundaries.csv`：逐时刻接收/拒收边界；
- `operating_characteristics.csv`：OC、ASN、停止分位数和概率守恒；
- `calibration_search_audit.csv`：阈值和截尾候选的可行性审计。

当前搜索严格标记为 `SUCCESS_LOCAL_CALIBRATION`：风险与路径概率为精确 DP 值，但阈值族是报告前声明的校准网格，灰区 ASN 上确界是自适应网格评价，不能称连续边界族全局最优。`p1=0.13,kappa=1` 是报告指定的主情景，不是题面唯一给定参数。
