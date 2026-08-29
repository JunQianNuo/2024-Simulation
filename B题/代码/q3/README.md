# 2024 CUMCM B 题问题三

程序实现 Q3-M3 题给三级装配树的组合核—吸收 Markov 奖励模型，完整枚举 Q3-A1 的 65536 个固定策略。位 0--7 是零件 `x1..x8`，位 8--10 是半成品 `y1..y3`，位 11 是 `yf`，位 12--14 是 `z1..z3`，位 15 是 `zf`。当前拓扑按题给 8 个零件和 3 个半成品实现，不声称为一般装配树自动生成器。

Q2/Q3 共用 `component_state.py` 中的质量—信息状态语义。零件批次核记录真实质量、`unknown/known-good` 信息和新购/拆回来源；补购另一个零件时，已检合格件不重复检测。拆回件保留物理质量，并按固定策略重新检测。

## 运行

```bash
cd B题/代码
uv pip install --python ../../.venv/bin/python -r q3/requirements.txt
../../.venv/bin/python -m q3.run_q3
../../.venv/bin/python -m unittest q3.test_q3 -v
```

快速调试可使用 `python -m q3.run_q3 --skip-sensitivity`，但该命令不生成完整交付。唯一完整复现命令是 `python -m q3.run_q3`。

## 数值与验证口径

- 正概率边的 SCC 是不可吸收的主判据，数值容差不改写图结构。
- 所有局部核传播谱半径、吸收裕度、条件数和残差。“必然良品”由检测决策和缺陷率是否严格为零判定，不使用浮点容差删除正概率坏件边。裕度不大于 `1e-10` 时用 80 位精度同时复核谱半径和奖励方程，未通过者不参与选优。
- 稀疏 LU 一次求解成本、事件和吸收概率右端。独立闭式批次公式交叉验证二/三零件显式链。
- 对每个零件、半成品和成品输出采购、消耗、返回、拆解和报废次数，并逐节点重算物料守恒。

## 输出

结果位于 `results/q3/`：

- `all_policies.csv`：65536 个策略的成本、事件、谱证书和物料流。
- `best_policies.csv`、`top10_policies.csv` 和 `decision_summary.csv`：最优策略、Top 10 与决策拆解。
- `material_balance.csv`：逐节点物料守恒残差。
- `kernel_registry.json`：状态字典、核 schema、局部谱半径、条件数和残差。
- `sensitivity.csv`：12 个缺陷率的官方表格观测范围 OAT，以及明确标注的±25% 假设成本压力情景。
- `structural_comparison.csv`：物理质量保持与“质量重置并重建”结构压力对照，后者不是主模型。
- `summary.json`、`repro_manifest.json` 和 `code_to_writer.json`：结果摘要、复现信息和论文交接。
- `top_policy_profit.*` 和 `sensitivity_profit_gap.*`：论文候选图，来源见 `figure_index.json`。

名义结果只适用于题设表 2 参数和“拆回件保留真实质量”假设。敏感性中的成本±25% 仅是无实测区间时的假设压力情景，不应表述为真实测量误差。
