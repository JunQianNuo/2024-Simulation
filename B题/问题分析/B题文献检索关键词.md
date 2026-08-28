---
title: B题文献检索关键词
date: 2026-08-27 15:05
problem: 2024-CUMCM-B
stage: 1.5a-literature-keywords
status: query-ready
tags:
  - 数学建模
  - 文献检索
  - 质量控制
---

# B题文献检索关键词

> [!info] 使用边界
> 本文依据 solver 的 Stage 1.5a，从 [[国赛练习题/CUMCM2024Problems/B题/问题分析/B题问题深度分析.md|B题问题深度分析]] 提取**问题概念、同义词和检索式**。其中“序贯抽样”“更新报酬”“动态规划”等仅是扩大文献召回率的探索性方法词，**不代表已经选定模型**。

## 1. 检索总公式

建议使用四层扩展法：

1. **精确问题词**：题目中的统计或生产决策对象；
2. **同义词**：中英文术语及不同学科表述；
3. **场景限定词**：电子产品、装配系统、质量控制、制造系统；
4. **探索性方法词**：用于发现相关方法文献，但不在本阶段比较优劣。

通用组合为：

```text
[核心问题词] AND [决策/统计词] AND [制造场景词]
```

检索时不要把“2024 国赛 B 题”作为主关键词，否则容易只得到赛题解析而非可引用的学术文献。

## 2. 问题一：最少检测的抽样接收/拒收

### 2.1 关键词组

| 层次 | 中文关键词 | 英文关键词 |
|---|---|---|
| 核心对象 | 次品率、不合格品率、计数型质量特性、批质量 | defect rate, fraction nonconforming, proportion defective, lot quality |
| 抽样任务 | 验收抽样、计数抽样检验、批接收、抽样方案 | acceptance sampling, attribute sampling, lot acceptance sampling, sampling plan |
| 统计证据 | 单侧置信限、精确二项置信区间、二项分布、假设检验 | one-sided confidence bound, exact binomial confidence interval, binomial distribution, hypothesis testing |
| 样本量目标 | 最小样本量、平均样本数、检测成本 | minimum sample size, average sample number, inspection cost |
| 探索性方法词 | 序贯抽样、序贯概率比检验、两阶段抽样、零失效抽样 | sequential sampling, sequential probability ratio test, SPRT, double sampling, zero-failure sampling |
| 性能评价 | 接收概率、操作特性曲线、生产者风险、消费者风险、AQL、LTPD/RQL | probability of acceptance, operating characteristic curve, OC curve, producer's risk, consumer's risk, AQL, LTPD, RQL |

### 2.2 可直接复制的检索式

**中文数据库：**

```text
(验收抽样 OR 计数抽样检验) AND 次品率 AND (单侧置信限 OR 精确二项)
```

```text
序贯抽样 AND 次品率 AND (平均样本数 OR 操作特性曲线)
```

```text
零失效抽样 AND (可靠性 OR 次品率) AND 单侧置信上限
```

**英文数据库：**

```text
"acceptance sampling" AND "fraction nonconforming" AND "exact binomial" AND "one-sided confidence bound"
```

```text
("sequential acceptance sampling" OR SPRT) AND "defect rate" AND ("average sample number" OR "operating characteristic")
```

```text
"zero-failure acceptance sampling" AND "one-sided confidence limit"
```

## 3. 问题二：两零配件生产中的检测、拆解与调换决策

### 3.1 关键词组

| 层次 | 中文关键词 | 英文关键词 |
|---|---|---|
| 核心场景 | 两部件装配、装配制造、生产质量控制、缺陷零部件 | two-component assembly, assembly manufacturing, production quality control, defective components |
| 决策变量 | 零部件检测、成品检测、检测配置、检验策略 | component inspection, final-product inspection, inspection allocation, inspection policy |
| 不合格品处置 | 拆解、返工、回收、再制造、报废、残值 | disassembly, rework, component recovery, remanufacturing, scrapping, salvage value |
| 市场反馈 | 退货、无条件调换、质保、调换损失、信誉损失 | product return, replacement, warranty, replacement cost, goodwill loss |
| 经济指标 | 期望利润、期望总成本、长期平均收益、单位合格品成本 | expected profit, expected total cost, long-run average reward, cost per conforming product |
| 探索性方法词 | 概率决策、更新过程、更新报酬、马尔可夫报酬、闭环制造 | stochastic decision, renewal process, renewal reward, Markov reward, closed-loop manufacturing |

> [!warning] 同义词并非完全等价
> `rework` 通常指返工，`disassembly` 指拆解，`remanufacturing` 指再制造，`salvage` 偏向残值回收。应分别检索，不宜在论文中直接互换。

### 3.2 可直接复制的检索式

**中文数据库：**

```text
生产质量控制 AND (零部件检测 OR 成品检测) AND 决策优化
```

```text
(拆解回收 OR 返工 OR 再制造) AND 次品 AND 生产决策
```

```text
质量检验策略 AND (退货 OR 调换损失 OR 质保成本) AND 装配制造
```

```text
(更新报酬 OR 马尔可夫报酬) AND 检测 AND 返工 AND 制造
```

**英文数据库：**

```text
("quality inspection policy" OR "inspection allocation") AND assembly AND "defective components"
```

```text
manufacturing AND (rework OR disassembly OR "component recovery") AND "quality control decision"
```

```text
("warranty return" OR "product replacement" OR "replacement cost") AND "inspection policy" AND manufacturing
```

```text
("renewal reward" OR "Markov reward") AND inspection AND rework AND manufacturing
```

## 4. 问题三：多工序、多零配件装配系统

### 4.1 关键词组

| 层次 | 中文关键词 | 英文关键词 |
|---|---|---|
| 系统结构 | 多级装配系统、装配树、层级装配、多工序制造、串并联生产 | multistage assembly system, assembly tree, hierarchical assembly, multilevel manufacturing, serial-parallel production |
| 节点对象 | 零配件、半成品、中间产品、成品、装配节点 | component, subassembly, intermediate product, final product, assembly node |
| 质量机制 | 次品传播、质量传播、装配缺陷、条件次品率 | defect propagation, quality propagation, assembly defect, conditional defect rate |
| 决策任务 | 检测位置选择、检测配置、中间检验、检测计划 | inspection location, inspection allocation, intermediate inspection, inspection planning |
| 回流处置 | 拆解回流、返工环、物料回收、闭环生产 | disassembly feedback, rework loop, material recovery, closed-loop production |
| 探索性方法词 | 装配树动态规划、网络优化、随机动态规划、分解算法 | dynamic programming on assembly tree, network optimization, stochastic dynamic programming, decomposition algorithm |

### 4.2 可直接复制的检索式

**中文数据库：**

```text
多级装配系统 AND (检测策略 OR 检测配置) AND 质量控制
```

```text
装配树 AND (检验配置 OR 检测分配) AND 优化
```

```text
多工序制造 AND (次品传播 OR 质量传播) AND 返工
```

```text
半成品检测 AND 拆解回流 AND 生产决策
```

**英文数据库：**

```text
"multistage assembly system" AND ("inspection policy" OR "inspection allocation")
```

```text
"assembly tree" AND "quality control" AND optimization
```

```text
("multistage manufacturing" OR "serial-parallel production") AND "defect propagation" AND rework
```

```text
("intermediate product inspection" OR "subassembly inspection") AND "assembly system" AND "dynamic programming"
```

## 5. 问题四：次品率估计误差下的生产决策

### 5.1 关键词组

| 层次 | 中文关键词 | 英文关键词 |
|---|---|---|
| 不确定性来源 | 次品率估计、抽样误差、参数不确定性、小样本质量数据 | defect-rate estimation, sampling error, parameter uncertainty, small-sample quality data |
| 概率表达 | 二项抽样、Beta-二项分布、后验分布、后验预测分布、置信区间 | binomial sampling, Beta-binomial distribution, posterior distribution, posterior predictive distribution, confidence interval |
| 决策任务 | 不确定参数下生产决策、风险调整利润、策略稳定性 | production decision under uncertainty, risk-adjusted profit, policy stability |
| 探索性方法词 | 贝叶斯验收抽样、贝叶斯决策、鲁棒优化、分布鲁棒优化、随机规划 | Bayesian acceptance sampling, Bayesian decision, robust optimization, distributionally robust optimization, stochastic programming |
| 信息评价 | 信息价值、样本信息价值、再抽样价值 | value of information, expected value of sample information, value of additional sampling |

### 5.2 可直接复制的检索式

**中文数据库：**

```text
贝叶斯验收抽样 AND 次品率 AND (Beta二项 OR 后验预测)
```

```text
次品率估计不确定性 AND 生产质量决策
```

```text
鲁棒质量控制 AND 参数不确定性 AND 检测策略
```

```text
信息价值 AND 质量检验 AND 生产决策
```

**英文数据库：**

```text
"Bayesian acceptance sampling" AND "Beta-binomial" AND "defect rate"
```

```text
"parameter uncertainty" AND "inspection policy" AND manufacturing
```

```text
("robust quality control" OR "robust inspection policy") AND "uncertain defect rates"
```

```text
"posterior predictive" AND "defect rate" AND "production decision"
```

```text
"value of information" AND "quality inspection" AND manufacturing
```

## 6. 跨问题同义词表

| 题面词 | 建议扩展词 |
|---|---|
| 次品率 | 不合格品率；defect rate；fraction nonconforming；proportion defective；nonconforming rate |
| 抽样检测 | 验收抽样、计数抽样；acceptance sampling；attribute sampling；sampling inspection |
| 检测策略 | 检验策略、检测配置、检测分配；inspection policy；inspection allocation；inspection planning |
| 零配件 | 部件、元件；component；part；item |
| 半成品 | 中间产品、子装配体；intermediate product；subassembly |
| 拆解回流 | 拆解、部件回收、返工环；disassembly；component recovery；rework loop |
| 不合格成品调换 | 退货、质保更换；product return；warranty replacement；replacement cost |
| 多级装配 | 装配树、层级装配；multistage assembly；assembly tree；hierarchical assembly |
| 长期收益 | 长期平均利润、更新报酬；long-run average profit；renewal reward |

## 7. 首轮检索优先级

若只进行一轮快速检索，建议先运行以下 **8 条高覆盖检索式**；优先级表示对四个子问题的覆盖程度，不表示模型优劣。

| 优先级 | 检索式 | 对应问题 |
|---|---|---|
| P1 | `(验收抽样 OR 序贯抽样) AND 次品率 AND (单侧置信限 OR 平均样本数)` | Q1 |
| P1 | `生产质量控制 AND 检测策略 AND (拆解 OR 返工 OR 调换损失)` | Q2 |
| P1 | `多级装配系统 AND 检测策略 AND (半成品 OR 拆解回流)` | Q3 |
| P1 | `次品率估计不确定性 AND (贝叶斯 OR 鲁棒) AND 生产决策` | Q4 |
| P1 | `"acceptance sampling" AND "defect rate" AND ("one-sided confidence bound" OR "average sample number")` | Q1 |
| P1 | `"inspection policy" AND assembly AND (disassembly OR rework OR "warranty return")` | Q2 |
| P1 | `"multistage assembly system" AND "inspection policy" AND (subassembly OR rework)` | Q3 |
| P1 | `"parameter uncertainty" AND "defect rate" AND (Bayesian OR robust) AND "production decision"` | Q4 |

## 8. 文献筛选规则

### 纳入

- 标题或摘要同时命中至少一个**场景词**和一个**统计/决策词**；
- 能支持抽样规则、成本收益结构、装配质量传播或参数不确定性中的至少一项；
- 优先选择质量管理、运筹优化、可靠性工程、制造系统领域的同行评审文献；
- 应用文献可优先检索 2015—2026 年，经典抽样理论文献不设年份下限。

### 排除

- 仅讨论机器视觉、图像缺陷识别，而不涉及抽样或生产决策；
- 仅讨论机械拆卸路径，而不涉及质量、成本或回收决策；
- 仅为竞赛答案、博客或无法追溯出处的二手材料；
- 只有算法名称、没有与本题变量和指标建立对应关系的文献。

## 9. 建议的检索产出

首轮目标不是“搜得越多越好”，而是形成 **5—8 篇高相关文献**：

- Q1：抽样与单侧统计证据 2 篇；
- Q2：检测—返工/拆解—退换经济决策 2 篇；
- Q3：多级装配检测配置 1—2 篇；
- Q4：参数不确定性或贝叶斯质量决策 1—2 篇。

每篇文献建议记录：`研究场景—决策变量—目标函数—不确定性处理—可迁移结论—局限性`。完成检索后再进入候选模型对比，避免先定模型、再反向寻找文献。
## 10. 第二轮定向检索式（已执行）

第一轮覆盖审查后，将宽泛词收敛为以下缺口导向组合：

```text
"binomial confidence sequence" AND "optional stopping"
"time-uniform" AND Bernoulli AND "confidence sequence"
"optimal stopping" AND "interval estimation" AND "Bernoulli trials"
```

```text
"nonserial production systems" AND inspection AND allocation
"assembly tree" AND inspection AND disassembly AND recovery
"manufacturing systems" AND (recovery OR rework) AND (semi-Markov OR dynamic programming)
"disassembly tree" AND "quality-dependent recovery"
```

精确题名回查：

```text
"The Optional Allocation of Inspection Effort in a Class of Nonserial Production Systems"
"Determining optimal disassembly and recovery strategies"
"An optimization model for selective inspection in serial manufacturing systems"
```

执行结果与去重理由见 [[国赛练习题/CUMCM2024Problems/B题/参考文献/B题第二轮文献检索结果.md|B题第二轮文献检索结果]]。
