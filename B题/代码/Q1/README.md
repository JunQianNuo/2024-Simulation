# 2024 CUMCM B题问题一代码

本目录是 Python 包 `q1`，实现已锁定的 **Q1-M5**（置信约束下的多目标序贯抽样优化模型）和 **Q1-A1**（双单侧 Bernoulli 置信序列、精确路径 DP 与有限网格 Pareto 搜索）。模型公式及口径对应 `模型设计/B题阶段2模型设计报告.md` §4 与 `算法设计/B题阶段3算法设计报告.md` §4；本次整理只修复工程结构与可复现运行，不改变模型。

## 安装与运行

依赖为 Python 3、`numpy`、`scipy`、`pandas`、`pyyaml`；测试建议另装 `pytest`：

```bash
python -m pip install numpy scipy pandas pyyaml pytest
```

从仓库根目录运行：

```bash
cd B题/代码
python -m q1.run_q1 --quick
python -m q1.run_q1
python -m pytest q1/test_q1.py -v
python q1/run_tests_nopytest.py
```

若当前已在 `B题/代码`，直接执行代码块中 `cd` 之后的四条命令即可。`python -m q1.run_q1` 是主程序的规范入口，保留 `--quick`、`--outdir PATH` 和 `--no-crosscheck`。默认配置是包内的 `q1/q1_grid.yaml`，默认结果目录是 `B题/代码/results/q1/`，会自动创建。`pytest` 可用时共有 24 个测试实例；没有 pytest 时，回退脚本执行同一文件中的全部测试实例。

## 文件对应关系

| 文件 | 报告位置 | 内容 |
|---|---|---|
| `q1_grid.yaml` | 阶段3 §4.3 | 候选网格、13 个代表性 $p$、三套权重、容差；运行前冻结 |
| `schemas.py` | 阶段3 §2.1/2.2/13 | 输入输出契约、动作编码、状态码 |
| `bernoulli_cs.py` | 阶段2 §4.4，阶段3 §4.2 | Beta–Binomial mixture CS、端点反演、Clopper–Pearson 基准 |
| `stopping_rule.py` | 阶段2 (Q1-ALG)(Q1-T) | 动作表、$N_{\max}$ 截尾、交叉核验、边界表 |
| `exact_path_dp.py` | 阶段3 §4.4 | 精确路径概率递推，输出 ASN / P50 / P90 / 三种终止概率 |
| `pareto_search.py` | 阶段2 (Q1-OPT)，阶段3 §4.5 | 加权目标、非支配筛选、双准则拐点 |
| `run_q1.py` | 阶段3 §4 | 主程序 |
| `test_q1.py` | 阶段3 §4.7 | 五项检查，24 个测试实例 |
| `run_tests_nopytest.py` | 工程回退 | 无 pytest 时执行同一测试文件 |

## 输出文件

每次运行默认覆盖写入 `B题/代码/results/q1/`：

- `q1_operating_characteristics.csv`：候选 × 代表性 $p$ 的精确性能；
- `q1_candidate_objectives.csv`：各候选在三套权重下的 $(\mathrm{ASN}_w,U_w)$；
- `q1_decision_boundary.csv`：推荐方案的接收/拒收边界表；
- `q1_summary.json`：运行摘要、校验残差与最优性口径。

## 实现与建模限制

`confseq` 不是运行依赖。主实现按 Howard et al. (2021) 的 Beta–Binomial mixture 独立实现；`crosscheck_action_table` 使用 p0 点凸性判据与 `brentq` 端点反演两套自有实现核验。安装 `confseq` 后，`bernoulli_cs.py` 中预留的 `crosscheck_against_confseq()` 可补充第三方判定对照。

mixture 先验固定在 $p_0$，不随被检验的 $p$ 移动。只要先验不依赖数据，$\{M_t(p)\}$ 对固定 $p$ 仍是均值为 1 的非负鞅，Ville 覆盖保证不受影响。

阈值附近未决率很高不是代码 bug：在有限 $N_{\max}$ 下，满足双错误约束的 anytime-valid 规则可能无法累积足够证据。`UNDECIDED_CAP` 是模型显式输出，不能强制改为接收或拒收；应报告为证据不足、继续检验或另行协商的情形。可选的模型层处理是照实报告、引入有依据的无差异区，或重新分配错误预算后再定义截尾动作；不能在代码里把未决直接改成拒收（会破坏现有的 $(Q1-C1)$ 保证）。

该 Bernoulli 路径模型适用于可近似为独立同分布、或来自足够大批次且抽样比例很低的情形。对有限“一批零配件”的不放回抽样，观测条件分布会随已见次品数变化，严格来说不是 i.i.d. Bernoulli；若抽样比例不可忽略，应采用有限总体/超几何序贯推断并重新验证错误保证。

加权 Pareto 的“省样本型”仅表示在预先给定的代表性 $p$ 与权重下具有较低加权 ASN，不能直接称为绝对“样本量最少”。

## 最优性称谓

> 预先声明的有限候选网格内的精确 Pareto 前沿；不宣称对连续 $t_{\rm opt}$ 或所有可能停止规则全局最优。
