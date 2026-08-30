# 2024 CUMCM B 题问题四

当前主线为 `Q4-M4 / Q4-A3`：在 Beta–Bernoulli belief state 上联合决定下一件检测哪个质量参数、何时停止抽样，以及停止后采用哪套 Q2/Q3 固定生产策略。`Q4-M2 / Q4-A1` 是停止价值层，`Q4-M3 / Q4-A2` 是独立稳健审计层。

```bash
cd B题/代码
uv run --with-requirements q4/requirements.txt python -m q4.run_q4 --quick
uv run --with-requirements q4/requirements.txt python -m unittest q4.test_q4 -v
```

Q2 每个表1情形使用确定性 Beta 求积和 finite-horizon memoized DP，输出策略 DAG、初始动作、NVSI/EVPI、期望抽样数和终止生产策略。Q3 覆盖全部 65536 个生产策略，使用共同 Sobol 样本计算成本敏感的一步 KG；它明确标记为 `myopic-KG`，不冒充全局最优抽样政策。`kg_rollout.py` 另提供共同随机数 rollout 内核，供扩大计算预算时做深度扩展和 Q2 oracle 校准。

`q4_demo_evidence.json` 中的 N、K、制样成本和检测成本都标记为演示情景。零件样本的条件是 `component`，半成品/成品装配次品率必须来自 `all_inputs_good` 制样。过去抽样成本只在最终净利润中扣除；未来抽样成本在 Bellman/KG 动作值中扣除；生产全检成本仍由 Q2/Q3 评价器计算，三者不会重复。

稳健审计根据 `stopping_rule` 自动选择 fixed-n Clopper–Pearson 区间或 time-uniform Beta-mixture Bernoulli CS。当前连续内层没有区间分支定界证书，因此结果严格标记为 `ROBUST_NUMERICAL`，不声称 `ROBUST_CERTIFIED`。

正式输出位于 `results/q4/`：`q2_voi_policy_summary.csv`、`q2_voi_policy_dag.csv`、`q3_kg_action_values.csv`、`simultaneous_intervals.csv`、`robust_audit.csv`、`summary.json` 与复现清单。题面没有真实样本和完整成本，任何“最优检测次数”都必须绑定保存的情景配置。
