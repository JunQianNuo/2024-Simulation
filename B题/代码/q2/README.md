# 2024 CUMCM B题问题二

本程序实现 Q2-M2 吸收 Markov 奖励闭环利润模型，并以 Q2-A1 穷举每种情形的 16 个固定策略 `(x1, x2, y, z)`。回收件保留真实质量并重新进入相同的检测—装配流程；若出现可达非终止闭类，策略会标记为不可行而不参与比较。

核算单位为“每最终交付一件合格品”：售价只计一次，调换损失不含替换产品本身的生产成本。

```bash
cd B题/代码
python -m q2.run_q2
```

若使用 uv：

```bash
uv run python -m q2.run_q2
```

运行自动检查概率矩阵、吸收性与线性方程残差，并生成 `results/q2/all_policies.csv`、`best_policies.csv` 和 `summary.json`。

success_probability = 1 表示“最终一定会交付合格品”的吸收概率，不是“一次装配合格率 100%”。