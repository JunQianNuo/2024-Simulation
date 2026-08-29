# 2024 CUMCM B 题 Q1

代码实现已锁定的 Q1-M5 / Q1-A1：用官方 `confseq` Beta–Binomial 单侧 Bernoulli 置信序列生成逐时刻接收/拒收边界，用 SciPy 独立反演核验端点，再以有限状态 DP 精确评价 34 个 $(t_{opt},N_{max})$ 候选并求 ASN—未决率 Pareto 前沿。

建议在 Python 3.10 环境安装：

```bash
python -m pip install -r q1/requirements-q1.txt
python -m q1.run_q1
python -m unittest q1.test_q1 -v
```

完整运行会在 `results/q1/` 生成候选目标、OC 表、Pareto 表、三类推荐、主推荐边界、34 个候选的全部行动边界、CS 交叉核验、外部五阶段基线、图与复现元数据。拐点辅助指标是对归一化 Pareto 坐标计算的三点 Menger 几何曲率，不再使用二阶差分范数。`UNDECIDED_CAP` 表示到上限仍证据不足，不允许临时追加抽检后继续“看到满意为止”。

在项目根目录可使用 Linux 容器复现：

```bash
docker build -f B题/代码/q1/Dockerfile -t cumcm-q1 .
docker run --rm cumcm-q1
```

`repro_manifest.json` 保存 Git 工作区状态和 Q1 核心源文件 SHA-256；当工作区不干净时，以源文件哈希作为精确代码快照标识。

## 论文候选图

绘图入口只读取已生成的 CSV/JSON，不重新执行 Q1 模型：

```bash
cd B题/代码
python -m q1.plot_q1
```

新增图保存在 `results/q1/figures/`，改进后的 Pareto 图仍保存为 `results/q1/pareto_front.svg/.png`。图表数据源、结论边界、中文图注与渲染检查状态见 `results/q1/figure_index.json`。中文字体优先使用 `Noto Serif CJK SC`，不可加载时回退为 `FandolSong`；英文衬线回退为 `Liberation Serif`，数学符号使用 STIX。

结果的“精确 Pareto”仅指预先声明的 34 个有限候选内无 Monte Carlo 误差，不代表连续参数域或所有停止规则中的全局最优。批次有限且抽样比不可忽略时，应改用不放回抽样的置信序列。
