---
title: B题文献检索结果
date: 2026-08-27 15:14
problem: 2024-CUMCM-B
stage: 1.5a-literature-search
status: deep-read-complete
search_calls: 3
retained_papers: 8
tags:
  - 数学建模
  - 文献检索
  - 质量控制
---

# B题文献检索结果

> [!update] 第二轮定向检索已完成（2026-08-27 21:06）
> 已围绕可选停止、非串行生产网络、随机恢复和拆解树补充 8 篇候选文献（7 篇新增、1 篇追回）。详见 [[国赛练习题/CUMCM2024Problems/B题/参考文献/B题第二轮文献检索结果.md|B题第二轮文献检索结果]]。

> [!success] Stage 1.5b 已完成（2026-08-27 16:29）
> 后续上传的 8 组 PDF/MD 已统一重命名并审计：实际为 7 篇独立文献（5 篇全文、2 篇仅元数据）及 1 个重复工作论文版本；Kakade et al. (2004) 仍缺失。详见 [[国赛练习题/CUMCM2024Problems/B题/参考文献/文献语料清单.md|文献语料清单]] 与 [[国赛练习题/CUMCM2024Problems/B题/问题分析/文献结果报告.md|文献结果报告]]。

> [!info] 阶段边界
> 本次工作只完成“检索、去重、书目信息回查和摘要级关联判断”。文献尚未全部下载、转为 Markdown 并全文精读，因此下文的“方法”仅表示**论文使用了什么**，不构成对 B 题的模型推荐。

当前语料状态：[[国赛练习题/CUMCM2024Problems/B题/参考文献/文献语料清单.md|文献语料清单]]；原自动下载尝试保留在 [[国赛练习题/CUMCM2024Problems/B题/参考文献/论文下载状态.md|论文下载状态]] 作为历史记录。

关键词来源：[[国赛练习题/CUMCM2024Problems/B题/问题分析/B题文献检索关键词.md|B题文献检索关键词]]。

## 1. 检索策略与停止条件

solver Stage 1.5a 规定最多进行 5 次 WebSearch；本次在第 3 轮后已获得超过 5 篇高度相关论文，故停止继续扩展。

| 轮次 | 核心检索式 | 语言与信源 | 检索结果 |
|---|---|---|---|
| 1 | `acceptance sampling + exact binomial/one-sided confidence/sequential sampling`；`multistage assembly + inspection allocation + rework/disassembly`；`Bayesian acceptance sampling + uncertain defect rate` | 英文；出版社论文页、DOI 页面、大学机构库 | 命中经典统计论文、多阶段检测配置论文和贝叶斯验收抽样论文 |
| 2 | `验收抽样 + 单侧置信限/序贯抽样`；`多级装配系统 + 检测配置`；`质量检验 + 拆解/返工/退货`；`贝叶斯验收抽样 + 参数不确定性` | 中文；期刊官网、论文原文 PDF，同时补充英文出版社页面 | 命中中文验收抽样经济设计论文及退货、返工相关候选文献 |
| 3 | 对经典论文和多级检测论文按完整标题检索 DOI | 英文；期刊官网、Project Euclid、大学机构库 | 核实 Clopper–Pearson、Wald、Kakade、Van Volsem 等论文元数据 |

补充核验：使用 Crossref DOI 元数据逐项核对题名、作者、年份、期刊、卷期和页码；最终去重保留 8 篇。

## 2. 检索到的论文

| # | 论文 | 作者/年份 | 期刊与来源说明 | 摘要或正文显示使用的方法 | 与赛题的客观关联 |
|---:|---|---|---|---|---|
| 1 | [The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial](https://doi.org/10.1093/biomet/26.4.404) | C. J. Clopper, E. S. Pearson, 1934 | *Biometrika*；二项比例精确区间经典论文 | 基于二项分布构造精确置信限 | 对应 Q1 的二项次品率与单侧置信限理论 |
| 2 | [Sequential Tests of Statistical Hypotheses](https://doi.org/10.1214/aoms/1177731118) | A. Wald, 1945 | *The Annals of Mathematical Statistics*；序贯检验经典论文 | 序贯假设检验及随观测更新的停止规则 | 对应 Q1“检测次数尽可能少”的序贯统计文献入口 |
| 3 | [Inspection for Circuit Board Assembly](https://doi.org/10.1287/mnsc.43.9.1198) | Phillipe B. Chevalier, Lawrence M. Wein, 1997 | *Management Science*；电子装配工业应用 | 联合优化检测位置与测试规则，以测试、修理和流向客户的不合格品期望成本为指标 | 与 Q2/Q3 的电子装配、阶段检测、修理成本和漏检损失相近 |
| 4 | [An Optimization Model for Selective Inspection in Serial Manufacturing Systems](https://doi.org/10.1080/00207540410001704014) | Vivek Kakade, Jorge F. Valenzuela, Jeffrey S. Smith, 2004 | *International Journal of Production Research* | 在串行多阶段装配线上配置选择性检测力度 | 与 Q2/Q3 的检测配置、多工序生产和成本权衡相关 |
| 5 | [An Evolutionary Algorithm and Discrete Event Simulation for Optimizing Inspection Strategies for Multi-stage Processes](https://doi.org/10.1016/j.ejor.2005.03.054) | Sofie Van Volsem, Wout Dullaert, Hendrik Van Landeghem, 2007 | *European Journal of Operational Research* | 用离散事件仿真描述多阶段过程，用进化算法联合搜索检测位置、类型和检测限 | 与 Q3 的多工序检测节点配置及复杂策略搜索相关 |
| 6 | [A New Bayesian Acceptance Sampling Plan Considering Inspection Errors](https://doi.org/10.1016/j.scient.2012.09.009) | M. S. Fallah Nezhad, H. Hosseini Nasab, 2012 | *Scientia Iranica*；出版社标注开放获取 | 用贝叶斯推断描述批次次品数量，并把拒收成本、漏放次品成本和正确决策概率纳入方案评价 | 与 Q1 的验收抽样及 Q4 的次品率不确定性相关 |
| 7 | [基于不完美检验的验收抽样方案经济设计](https://iej.gdut.edu.cn/cn/article/pdf/preview/10.3969/j.issn.1007-7375.2023.04.006.pdf) | 张斌、杨风萍、周筱雯，2023 | 《工业工程》26(4): 44–51；期刊官网原文 PDF | 用次品率先验分布和误检概率计算后验风险，并建立含抽检、复检及误判损失的整数非线性经济模型 | 与 Q1 的风险约束及 Q4 的抽样误差传播直接相关 |
| 8 | [A Sampling-Based Inspection and Cost Optimization Model for Electronic Assembly Quality Control](https://doi.org/10.3390/jmmp10050170) | Luling Duan, Pan Zhang, 2026 | *Journal of Manufacturing and Materials Processing*；开放获取；近期论文 | 将单侧验收抽样与零部件检测、成品检测、调换损失和拆解决策的期望成本框架结合 | 研究场景与 B 题四问高度同构；因发表较新，仍需全文核验后才能评价其学术增量与方法可靠性 |

## 3. DOI 与全文入口

> [!note] 访问说明
> “开放入口”来自出版社或作者机构库；“DOI/机构权限”表示未在本轮确认到合法免费全文，不代表论文一定收费。

|   # | DOI                                    | 全文或下载入口                                                                                                                                                                                                 | 本轮确认状态    |
| --: | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
|   1 | `10.1093/biomet/26.4.404`              | [Oxford/DOI 页面](https://doi.org/10.1093/biomet/26.4.404)                                                                                                                                                | DOI/机构权限  |
|   2 | `10.1214/aoms/1177731118`              | [Project Euclid DOI 页面](https://doi.org/10.1214/aoms/1177731118) · [PDF](https://projecteuclid.org/download/pdf_1/euclid.aoms/1177731118)                                                               | 可访问原文     |
|   3 | `10.1287/mnsc.43.9.1198`               | [INFORMS 论文页](https://pubsonline.informs.org/doi/10.1287/mnsc.43.9.1198)                                                                                                                                | DOI/机构权限  |
|   4 | `10.1080/00207540410001704014`         | [Taylor & Francis 论文页](https://doi.org/10.1080/00207540410001704014)                                                                                                                                    | DOI/机构权限  |
|   5 | `10.1016/j.ejor.2005.03.054`           | [DOI 页面](https://doi.org/10.1016/j.ejor.2005.03.054) · [作者机构工作论文 PDF](https://medialibrary.uantwerpen.be/oldcontent/container1244/files/TEW%20-%20Onderzoek/Working%20Papers/RPS/2004/RPS-2004-010.pdf) | 有可访问版本    |
|   6 | `10.1016/j.scient.2012.09.009`         | [ScienceDirect 论文页](https://doi.org/10.1016/j.scient.2012.09.009)                                                                                                                                       | 出版社标注开放获取 |
|   7 | `10.3969/j.issn.1007-7375.2023.04.006` | [期刊官网 PDF](https://iej.gdut.edu.cn/cn/article/pdf/preview/10.3969/j.issn.1007-7375.2023.04.006.pdf)                                                                                                     | 可访问原文     |
|   8 | `10.3390/jmmp10050170`                 | [MDPI 论文页](https://www.mdpi.com/2504-4494/10/5/170)                                                                                                                                                     | 开放获取      |

## 4. 按子问题建立的文献证据索引

这里仅记录“检索到什么”，不据此确定最终模型。

| 子问题 | 已检索到的文献证据 |
|---|---|
| Q1 抽样接收/拒收 | #1 给出精确二项置信限；#2 研究序贯检验；#6、#7 研究带先验信息或检验误差的验收抽样；#8 联结单侧抽样与成本框架 |
| Q2 两零件生产决策 | #3 研究电子装配中的检测位置、测试策略和流出次品成本；#4 研究多阶段选择性检测；#8 涵盖零部件、成品、调换及拆解成本 |
| Q3 多级装配系统 | #3、#4、#5 均涉及多阶段检测配置；#5 进一步联合考虑检测位置、类型与检测限；#8 覆盖多级电子装配场景 |
| Q4 次品率由抽样得到 | #6 使用贝叶斯推断；#7 将次品率先验与误检概率传入风险和经济设计；#8 将抽样证据接入后续期望成本计算 |

## 5. 摘要层面观察（不是模型选择结论）

1. 检索结果形成三类文献簇：**精确/序贯抽样**、**多阶段检测配置**、**参数不确定性下的经济验收抽样**。
2. #3 的摘要明确把测试、修理和流向客户的不合格品成本放入同一目标；这与题面中的成品检测和调换损失具有结构上的相似性。
3. #5 把多阶段生产过程的离散事件仿真与检测策略搜索结合；其论文对象是串行多阶段过程，是否能直接迁移到 Q3 的装配树需全文审查。
4. #7 的原文明确考虑次品率为随机变量、检验误判、抽检/复检成本及误判损失；这为 Q4 提供了“不只代入点估计”的相关文献实例。
5. #8 与赛题场景近乎同构，但“高度相似”不等于“方法已经得到充分验证”；需要在全文精读时单独检查数据来源、假设、公式和对既有工作的增量。

## 6. 参考文献格式草案

1. CLOPPER C J, PEARSON E S. The use of confidence or fiducial limits illustrated in the case of the binomial[J]. *Biometrika*, 1934, 26(4): 404–413. DOI: 10.1093/biomet/26.4.404.
2. WALD A. Sequential tests of statistical hypotheses[J]. *The Annals of Mathematical Statistics*, 1945, 16(2): 117–186. DOI: 10.1214/aoms/1177731118.
3. CHEVALIER P B, WEIN L M. Inspection for circuit board assembly[J]. *Management Science*, 1997, 43(9): 1198–1213. DOI: 10.1287/mnsc.43.9.1198.
4. KAKADE V, VALENZUELA J F, SMITH J S. An optimization model for selective inspection in serial manufacturing systems[J]. *International Journal of Production Research*, 2004, 42(18): 3891–3909. DOI: 10.1080/00207540410001704014.
5. VAN VOLSEM S, DULLAERT W, VAN LANDEGHEM H. An evolutionary algorithm and discrete event simulation for optimizing inspection strategies for multi-stage processes[J]. *European Journal of Operational Research*, 2007, 179(3): 621–633. DOI: 10.1016/j.ejor.2005.03.054.
6. FALLAH NEZHAD M S, HOSSEINI NASAB H. A new Bayesian acceptance sampling plan considering inspection errors[J]. *Scientia Iranica*, 2012, 19(6): 1865–1869. DOI: 10.1016/j.scient.2012.09.009.
7. 张斌, 杨风萍, 周筱雯. 基于不完美检验的验收抽样方案经济设计[J]. 工业工程, 2023, 26(4): 44–51. DOI: 10.3969/j.issn.1007-7375.2023.04.006.
8. DUAN L, ZHANG P. A sampling-based inspection and cost optimization model for electronic assembly quality control[J]. *Journal of Manufacturing and Materials Processing*, 2026, 10(5): 170. DOI: 10.3390/jmmp10050170.

## 7. 下一阶段输入要求

若继续执行 solver Stage 1.5b，应将上述论文的合法全文下载并转为 Markdown，放入：

```text
国赛练习题/CUMCM2024Problems/B题/参考文献/MD/
```

全文到位后再逐篇提取：`研究背景—模型—适用条件—算法—结论—局限性`，并生成“文献结果报告”。

