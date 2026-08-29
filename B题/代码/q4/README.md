# 2024 CUMCM B 题问题四

Q4 不另造生产模型，而是把抽样得到的次品率不确定性传入已验收的 Q2 吸收 Markov 收益模型和 Q3 装配树闭环模型。

```bash
cd B题/代码
uv pip install --python ../../.venv/bin/python -r q4/requirements.txt
../../.venv/bin/python -m q4.run_q4 --quick
../../.venv/bin/python -m unittest q4.test_q4 -v
```

去掉 `--quick` 后使用 `config.json` 中的正式 Monte Carlo 预算。向量化批量评价器在每个共同参数样本上覆盖 Q2 每情形 16 策略和 Q3 全部 65536 策略；快速模式的 Bayesian 结果一律标为 `MC_NOT_CONVERGED`，只用于验证数据流。

## 证据接口

题面没有提供真实 `(N,K)`，因此默认 `q4_demo_evidence.json` 明确标记为 `DEMO_ONLY_NOT_OFFICIAL_DATA`，不能写成企业实测结论。可用：

```bash
../../.venv/bin/python -m q4.run_q4 --evidence q4/your_evidence.json
```

每个记录必须有 `N,K,conditioning`。零件的 `conditioning` 是 `component`，装配次品率必须是 `all_inputs_good`。固定样本用 Bonferroni–Clopper–Pearson 联合区间；若某记录来自序贯停止，需额外给出 `"stopping_rule":"sequential_cs"` 和 `t_opt`，程序才会调用 Q1-A1 的 Beta–Binomial 置信序列端点。

## Q4-M2 / Q4-A1

Uniform `Beta(1,1)` 是主基准，Jeffreys `Beta(1/2,1/2)` 是先验敏感性。同一后验参数样本下比较全部策略，流式输出后验期望利润、策略最优概率、亏损概率、后验遗憾和 MC 标准误；分位数来自配置中固定大小的共同参数蓄水池，并在结果列中明确标注近似口径。可信区间与 MC 数值误差分开报告。

探索批只有同时满足配对利润差 Student-t 半宽、领先策略最优概率 MC SE、至少 8 批和连续 3 个稳定 checkpoint，再被独立固定确认批复核，才标 `SUCCESS_MC_TOL`。否则输出近优集，不强行声称唯一最优。

## Q4-M3 / Q4-A2

90% 联合矩形集是主稳健口径，95% 作敏感性。当前 Q2/Q3 固定策略闭式评价式只由非负成本、质量概率乘积和几何重试分母递归构成，因此成本关于每个缺陷率单调不减。程序同时执行 Sobol 盒内反例搜索，并保存递归区间导数证书；在该固定策略域和当前矩形集内，最坏点严格归约为全部缺陷率上端点，内层 gap 为 0。该 `ROBUST_CERTIFIED` 称谓不扩展到历史自适应策略、相关不确定集或其他生产模型。

输出在 `results/q4/`：全策略表、Bayesian 近优集、认证稳健方案、`summary.json`、`evidence_used.json` 和 `reproducibility.json`。利润口径始终是最终交付一件合格品，回收件保留真实质量，与 Q2/Q3 一致。
