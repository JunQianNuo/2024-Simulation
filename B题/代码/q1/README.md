# 2024 CUMCM B题问题一

本程序采用预设的五阶段抽样节点 `40, 80, 160, 320, 800`。每个节点以单侧 Clopper--Pearson 置信界判断：下界超过 `p0=0.10` 时拒收，上界不超过 `p0` 时接收；在第 800 件仍不能判断则输出未决，并建议追加抽检。

接收错误预算各阶段之和为 `0.10`，拒收错误预算各阶段之和为 `0.05`；因此由 Bonferroni/union bound 控制整体错误概率。这是仅在五个预设节点检查的 group-sequential 方案，比逐件检查更少保守。批次足够大、抽样比例较低时，不放回抽样近似为 i.i.d. Bernoulli；默认检测准确无误。阈值附近仍可能未决，这是证据不足的正常输出，不是程序错误。

运行：

```bash
cd B题/代码
python -m q1.run_q1
```

若项目使用 uv：

```bash
uv run python -m q1.run_q1
```

运行会执行内置自检，并生成 `results/q1/operating_characteristics.csv`、`decision_boundary.csv` 和 `summary.json`。
