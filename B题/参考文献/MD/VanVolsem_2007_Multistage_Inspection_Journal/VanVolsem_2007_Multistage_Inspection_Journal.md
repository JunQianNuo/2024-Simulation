---
raw_title: VanVolsem_2007_Multistage_Inspection_Journal
subject: VanVolsem_2007_Multistage_Inspection_Journal
source: VanVolsem_2007_Multistage_Inspection_Journal.pdf
status: mineru解析
parser: mineru
---

# An Evolutionary Algorithm and discrete event simulation for optimizing inspection strategies for multi-stage processes

Sofie Van Volsem <sup>a,b,\*</sup>, Wout Dullaert <sup>c</sup>, Hendrik Van Landeghem

<sup>a</sup> Department of Environment, Technology and Technology Management, University of Antwerp, Prinsstraat 13, B 2000 Antwerp, Belgium

<sup>b</sup> Department of Industrial Management, Ghent University, Technologiepark 903, B 9052 Zwijnaarde, Belgium <sup>c</sup> Institute of Transport and Maritime Management Antwerp, University of Antwerp, Keizerstraat 64, B 2000 Antwerp, Belgium

Received 6 April 2004; accepted 23 March 2005 Available online 15 December 2005

## Abstract

The problem of determining the optimal inspection strategy for a given multi-stage production process, i.e. the inspection strategy that results in the lowest total inspection cost, while still assuring a required output quality, is modelled as a joint optimization of inspection location, type and inspection limits. A fusion between a discrete event simulation to model the multi-stage process subject to inspection and to calculate the resulting inspection costs, and an Evolutionary Algorithm (EA) to optimize the inspection strategies, is suggested. - 2005 Elsevier B.V. All rights reserved.

Keywords: Metaheuristics; Evolutionary computations; Simulation; Inspection allocation; Quality economics

## 1. Introduction

The strategic importance of total quality management has become generally accepted. Improving the quality of products, processes and services is nowadays a key issue in many organizations to improve or at least maintain-profitability, market share and competitiveness.

In a production environment, reducing variance is the major key to achieve quality. It is pursued along diferent paths in design and operation of a production process. The implementation of an eficient inspection strategy is one of those paths. Eficient economic inspection strategies ensure the required output quality while minimizing the total inspection cost. Generally speaking, more and tighter inspection will induce a higher product quality—in terms of meeting product specifications—but will also result in higher costs of inspection, scrap and rework. An economic inspection plan will balance these efects.

For a single stage production process, the extent of inspection refers to the number of inspections executed (sample size and sampling frequency) and to the rigor of the inspections (acceptance limits). Thus, the problem facing the inspection planner consists of finding the combination of these inspection parameters that minimizes the total expected inspection cost TIC.

For multi-stage production processes, additional decision variables are added to the problem: the number and location of inspection stations in the production process. For an n-stage process, it is to be decided for each of the n stages whether or not inspection will be performed after that process stage, and if so, to what extent (i.e. which inspection parameters to be used).

Thus, in a multi-stage production system (MSPS) the inspection strategy addresses

1. the number and location of inspection stations;

2. the number of inspections executed (sample size—sampling frequency) for each inspection station;

3. the rigor of the inspections (acceptance limits) for each inspection station.

Determining optimal location of inspection stations in a (serial) MSPS, is typically about achieving minimum expected total cost of the inspection process, for a given expected proportion of defectives at each stage. The total inspection cost comprises the inspection cost of all inspected units and the cost incurred by the defective units detected at any given stage or eventually at the customer. Separate optimization of each type of decision variable has been studied extensively and is well-established in literature (see e.g. the seminal papers of Lindsay and Bishop (1964), White (1969), Britney (1972), Eppen and Hurst (1974) and Ballou and Pazer (1982) and the overview by Raz (1986)). Lindsay and Bishop (1964) and White (1969) show that for unconstrained systems and linear cost functions the optimal inspection policy at each of the inspection stations installed is 100% inspection. Hence, the only relevant decision variable is the locations of the inspection stations which then automatically implies full inspection at each such location.

If only the quality requirements of the final product are given, the expected fraction defective at each stage is not known. Instead, it has to be determined so that an inspection station located at a certain stage may sieve the defective units at that stage and thus ultimately reduce the process variance of the final product at minimum cost. As a result, all three types of inspection decision variables are relevant, resulting in a complex joint optimization problem. The problem of simultaneously optimizing the location of inspection stations and their inspection limits, has—to our knowledge—not been addressed before.

By embedding a discrete event simulation (DES) to model the serial n-stage MSPS in an Evolutionary Algorithm (EA) to perform the numerical optimization, this paper attempts at ofering a joint inspection optimization method. For a serial n-stage MSPS with a single quality characteristic, this methodology will allow the simultaneous determination of the inspection decision (no inspection (N), sampling inspection (S), and full inspection (F)), and the inspection limits, for each of the n process stages, so that the expected total inspection cost (TIC) is minimal.

The paper is organized as follows. After reviewing the literature in Section 2, the serial n-stage MSPS environment and the cost model are described in Section 3. In Section 4 the solution approach is proposed. A numerical example is presented in Section 5, Section 6 concludes and ofers suggestions for further research.

## 2. Literature review

Villalobos et al. (1993) present a model for (automated) inspection strategies for production of printed circuit boards. The idea is to impose a dynamic inspection strategy based on information on the manufacturing and inspection process, and a global objective (e.g. minimal cost or minimal scrap). After each manufacturing stage and for each unit produced, a decision is taken on whether or not to remove the unit from production, and whether or not it should be inspected. In the Villalobos et al. (1993) model, the extent of inspection of the overall production process is limited by time: each possible inspection operation takes a fixed amount of time, and the fixed amount of total available inspection time is to be allocated among all inspection stations. This way, the problem becomes one of optimal control of a dynamic Markov process under time constraints. The Markov chain structure and transition matrix are subsequently derived.

In Barad and Braha (1996) and Emmons and Rabinowitz (2002) it is assumed that an inspection is made at each production stage, so there is no problem of allocating (a limited number of) inspection facilities to production stations. The former address the problem of finding the optimal (limits for the) input quantity in each stage, while the latter focus on the assignment and scheduling of inspection tasks. The model of Barad and Braha (1996) (also set in the microelectronics industry) is essentially an optimal lot sizing problem in a MSPS with binomial yield and deterministic demand. After each production stage, a 100% reliable inspection is performed, so that all defective units are discarded. The solution to the problem consists of deciding on the number of products to process in the next stage, in order to try and meet the demand for non-defective finished units, at the lowest cost. There are three alternatives: processing all available non-defective units, processing less than available non-defective units by disposal (at a per unit cost) of some, and processing more than available non-defective units by reworking some of the defective units or by purchasing the necessary semi-finished units (also at a per unit cost). A dynamic programming approach is suggested to define the optimal policy, both for single and multiple production runs.

Emmons and Rabinowitz (2002) address an inspection system for detecting malfunctioning processors in a MSPS: a processor (a stage in the MSPS) can either be up (designating proper function) or down (designating malfunction). When a stage is down, each unit processed at that stage acquires a defect, when a stage is up, no unit does. A finished product is conforming if and only if it has not acquired a single defect. Inspection is there to detect stages as down, leading to immediate restoration of the detected down stage to up. Perfect inspection is assumed, the impact of imperfect inspection is accounted for in Rabinowitz and Yahalom (2001). The inspection system comprises several subsystems of single inspection facilities (IFs) responsible for inspecting a subset of production stages. In this setting three decisions are to be made: total inspection capacity (the number of IFs required), assignment of the stages to the IFs and inspection schedules in each subsystem. These three decisions are hierarchically structured, and thus solved through a hierarchical process. First, the inspection capacity is determined by solving a relaxed version of the base problem. The partition of the stages among the IFs is then determined by considering the inspection capacity from step 1 as the capacity of a multi-knapsack (bin packing) problem. Finally, the inspection schedule for each subsystem is derived.

The model by Bai and Yun (1996) allows inspection efort allocation in a serial multi-stage production system (MSPS) for a product consisting of identical components. In this model, only a limited number of (automatic) inspection machines are available, and the rate of production is constrained by the rate of inspection. The inspection level is defined as the proportion of components inspected. An inspection cost model is proposed and a method is constructed to determine optimal location of inspection machines and optimal inspection level. An exact search algorithm considering all possible allocations is proposed for problems in which the number of stages h and the number of inspection machines m is relatively small. For larger problems a heuristic algorithm using backward dynamic programming is suggested.

## 3. Model formulation

## 3.1. The serial multi-stage production system

Consider a serial MSPS in which products travel sequentially from stage 1 to stage n and inspection of products is performed by $k ( k \leqslant n )$ inspection stations (see Fig. 1). At each stage, a manufacturing operation is performed on the products, before moving on to an inspection station, or to the processing station of the next stage in case of no inspection.

After each of the processing stations, one of three inspection options can be chosen: no inspection (N), full inspection (F), or sampling inspection (S). The first option, no inspection (N), obviously does not necessitate any further inspection decision. If full inspection (F) is chosen, inspection limits subsequently have to be determined. Finally, the sampling inspection option (S), requires a decision on the inspection limits, and the (single) sampling scheme parameters: the sample size and acceptance number.

In any MSPS, three types of parameters can be distinguished: process parameters, inspection parameters and cost parameters. When using the model to optimize the overall inspection strategy, only the inspection parameters are considered endogenous (as they can be changed in the inspection strategy optimization process), while the cost and process parameters are exogenous because they cannot be changed for inspection strategy optimization purposes.

Prior to further model development, the following notations are adopted.

K batchsize

n number of process stages

$X _ { i }$ inspection option for stage i, i.e. $X _ { i } \in \{ F , N , S \}$

$p _ { i } ^ { \prime }$ fault occurrence in stage i

$\mathrm { L I L } _ { i }$ lower inspection limit in stage i (variable)

$\mathrm { U I L } _ { i }$ upper inspection limit in stage i (variable)

$\mathrm { L S } _ { n }$ lower specification limit after stage n (fixed)

$\mathrm { U } \mathrm { S } _ { n }$ upper specification limit after stage n (fixed)

$s _ { i }$ sample size for stage i $t _ { i }$ acceptance number for stage i $l _ { i }$ number of bad items in sample of stage i $d _ { i }$ number of bad items after stage i $c _ { \mathrm { T } , i }$ unit test cost in stage i $c _ { \mathrm { R } , i }$ unit rework cost in stage i $c _ { \mathrm { P } }$ unit penalty cost (after stage n) $\mathrm { T C } _ { i }$ test cost in stage i $\mathsf { R C } _ { i }$ rework cost in stage i $\mathrm { T T C }$ total test cost TRC total rework cost TPC total penalty cost TIC total inspection cost

![](images/3db61dd5b17dbb884836266c6981cd0949b1320ae2bbb04ebfc5743a542ff9eb.jpg)  
Fig. 1. A serial n-stage MSPS.

Consider a constant production and inspection rate, perfect inspection and perfect rework. In the MSPS, product is defective whenever the value of its quality characteristic in stage i lies outside its inspection limits, i.e. outside the interval $[ \mathrm { L I L } _ { i } , \mathrm { U I L } _ { i } ]$ . MSPS output (after the last stage n) is defective if the value of the quality characteristic is not contained in the specification interval $[ \mathrm { L S } _ { n } , \mathrm { U S } _ { n } ] .$

The fault occurrence $p _ { i } ^ { \prime }$ is the fraction of defective products in stage i. Because the inspection limits $( \mathrm { L I L } _ { i } , \mathrm { U I L } _ { i } )$ are independent variables of the inspection optimization problem under consideration, the fault occurrence $p _ { i } ^ { \prime }$ will be a dependent variable. For a single production stage, its value can be calculated using standard statistics, if the distribution of the quality characteristic value is known, and the LIL and UIL for the stage are chosen. Also for the first stage of a MSPS, $p _ { 1 } ^ { \prime }$ can be calculated in this way. For the following stages $i ( i = 2 , \ldots , n )$ however, the fault occurrence $p _ { i } ^ { \prime }$ not only depends on the choice of inspection limits $( \mathrm { L I L } _ { i } , \mathrm { U I L } _ { i } )$ , but also on the inspection strategy chosen in the previous stage(s).

Three types of cost are defined: test costs $\left( c _ { \mathrm { T } } \right)$ , rework costs $\left( c _ { \mathbf { R } } \right)$ and the penalty cost $\left( c _ { \mathbf { P } } \right)$ . Test cost is the cost of a single test or analysis. Rework or replacement costs are incurred if a defective product is discovered through testing, and reworked or replaced by a non-defective product. The penalty cost is incurred when a defective product is shipped to the customer.

Because it would be uneconomical to inspect a product if this were more expensive than reworking or replacing it, $c _ { \mathrm { T } , i } < c _ { \mathrm { R } , i } , \forall i .$ . Moreover, we assume that $c _ { \mathrm { R } , i } < c _ { \mathrm { R } , j } , \forall i < j .$ This assumption avoids having to introduce separate intermediate penalty costs: the penalty cost of detecting a defect only in stage $j ,$ instead of earlier in stage i, is implicitly derived as $c _ { \mathbf { R } , j } - c _ { \mathbf { R } , i } .$ Furthermore, it is assumed that if a batch is rejected after acceptance sampling inspection S, a full inspection F of the rejected batch is performed consecutively in the same stage.

## 3.2. Determination of the TIC

Determining the TIC is now straightforward:

$$
\mathrm{TIC} = \mathrm{TTC} + \mathrm{TRC} + \mathrm{TPC}\tag{1}
$$

with

$$
\mathrm{TTC} = \sum_ {i = 1} ^ {n} \mathrm{TC} _ {i}\tag{2}
$$

$$
\mathrm{TRC} = \sum_ {i = 1} ^ {n} \mathrm{RC} _ {i}\tag{3}
$$

$$
\mathrm{TPC} = c _ {\mathrm{P}} \cdot d _ {n}\tag{4}
$$

and with

$$
\mathrm{TC} _ {i} = \left\{ \begin{array}{l l} c _ {\mathrm{T}, i} \cdot K & \forall i (X _ {i} = F) \lor ((X _ {i} = S) \land (l _ {i} > t _ {i})) \\ c _ {\mathrm{T}, i} \cdot s _ {i} & \forall i (X _ {i} = S) \land (l _ {i} \leqslant t _ {i}) \\ 0 & \forall i X _ {i} = N \end{array} \right.\tag{5}
$$

$$
\mathrm{RC} _ {i} = \left\{ \begin{array}{l l} c _ {\mathrm{R}, i} \cdot p _ {i} ^ {\prime} \cdot K & \forall i (X _ {i} = F) \vee ((X _ {i} = S) \wedge (l _ {i} > t _ {i})) \\ 0 & \forall i (X _ {i} = N) \vee ((X _ {i} = S) \wedge (l _ {i} \leqslant t _ {i})) \end{array} \right.\tag{6}
$$

Determining the optimal inspection strategy, i.e. the whole of inspection decisions that minimize the TIC, requires the determination of inspection options $X _ { i }$ and the corresponding inspection limits $( \mathrm { L I L } _ { i } , \mathrm { U I L } _ { i } )$ and sampling parameters $( s _ { i } , t _ { i } )$ , for all stages $i = 1 , \ldots , n$ . Solving this optimization problem consists of finding the set of optimal values

$$
(X _ {1} ^ {*}, \dots , X _ {n} ^ {*}; \mathrm{LIL} _ {1} ^ {*}, \dots , \mathrm{LIL} _ {n} ^ {*}; \mathrm{UIL} _ {1} ^ {*}, \dots , \mathrm{UIL} _ {n} ^ {*}; s _ {1} ^ {*}, \dots , s _ {n} ^ {*}; t _ {1} ^ {*}, \dots , t _ {n} ^ {*})\tag{7}
$$

that minimize

$$
\operatorname{TIC} \left(X _ {1}, \dots , X _ {n}; \mathrm{LIL} _ {1}, \dots , \mathrm{LIL} _ {n}; \mathrm{UIL} _ {1}, \dots , \mathrm{UIL} _ {n}; s _ {1}, \dots , s _ {n}; t _ {1}, \dots , t _ {n}\right)\tag{8}
$$

The Evolutionary Algorithm suggested in Section 4.2 will decide on the inspection option $X _ { i }$ and the inspection limits $( \mathrm { L I L } _ { i } , \mathrm { U I L } _ { i } )$ , for each process stage i, but does not include the setting of sampling parameters $( s _ { i } , t _ { i } )$ , these are considered fixed $( s _ { i } = 5 0 , t _ { i } = 1 , \forall i )$ . The current algorithm returns the set

$$
(X _ {1} ^ {*}, \dots , X _ {n} ^ {*}; \mathrm{LIL} _ {1} ^ {*}, \dots , \mathrm{LIL} _ {n} ^ {*}; \mathrm{UIL} _ {1} ^ {*}, \dots , \mathrm{UIL} _ {n} ^ {*})\tag{9}
$$

that minimize

$$
\operatorname{TIC} \left(X _ {1}, \dots , X _ {n}; \mathrm{LIL} _ {1}, \dots , \mathrm{LIL} _ {n}; \mathrm{UIL} _ {1}, \dots , \mathrm{UIL} _ {n}\right)\tag{10}
$$

## 4. Solution approach

## 4.1. Discrete event simulation to calculate TIC

Simulation is used to study processes that are too complex to permit analytical model formulation and/ or evaluation. The complexity can be due to the size of the problem, the interactions between its subproblems, the inherent randomness of the problem, or a combination of these factors.

It is clear that TIC discussed in the previous Section refers to a single production batch. Of course, the inspection planner should not rely on just a single problem instance (i.e. one batch) to decide which strategy is the best. Diferent inspection strategy solutions should be evaluated over a number of problem instances to take into account the inherent stochastic properties of the production process. In this paper, each candidate solution is evaluated based on the average TIC from 50 simulated production batches.

## 4.2. An Evolutionary Algorithm to determine the optimal inspection strategy

## 4.2.1. Introduction

To explore the use of metaheuristics for determining the optimal inspection strategy, a simple Evolution ary Algorithm (EA) is presented. Evolutionary (or Genetic) Algorithms are adaptive heuristic search meth: ods based on population genetics. The basic concepts were developed by Holland (1975) and were forged into a problem solving methodology for complex optimization problems by De Jong (1975) and Goldberg (1989). The name evolutionary originates from the analogy of the heuristic with Darwin-s theory on natural selection. In selective breeding, ofspring are sought which have certain desirable characteristics, determined at the genetic level by combination of the parents- chromosomes. In a similar way, in seeking better solutions, EA-s combine pieces of existing solutions. Thereto, in an EA, a solution to a problem is first encoded as a chromosome, and new generations of ofspring are generated through an iteration process until some convergence criteria are met. The best chromosome generated is then decoded, providing the corresponding solution.

There are four main parts in the EA paradigm, namely the problem representation and initiation, the objective function evaluation (fitness calculation), the parent selection, and the actual evolutionary reproduction of candidate solutions

## 4.2.2. Problem representation and initiation

Every proposed solution is represented by a vector of the independent variables (inspection decision variables), coded as a chromosome constituted by as many genes as the number of independent variables. In a ‘‘standard’’ Genetic Algorithm, binary coding is applied. The term Evolutionary Algorithm is used if other than binary encoding is applied. The chromosomes used in the EA we propose, consist of both ‘‘integer’’ values (i.e. F, N or S) and real values $( \mathrm { i } . \mathrm { e } . \mathrm { L I L } _ { i }$ and $\mathrm { U I L } _ { i } )$

Every candidate solution to the inspection optimization problem considered thus is a set $( X _ { 1 } , \ldots , X _ { n } ;$ $\operatorname { L I L } _ { 1 } , \dotsc , \operatorname { L I L } _ { n } ; \operatorname { U I L } _ { 1 } , \dotsc , \operatorname { U I L } _ { n } )$ , which can be denoted as an array of n characters $X _ { i } ,$ each character associated with the two inspection limits $\mathrm { L I L } _ { i }$ and $\mathrm { U I L } _ { i }$ for the corresponding stage. For example the vector

$$
\left[ \begin{array}{c c c c} F _ {9. 1} ^ {1 0. 9} & N _ {1 8. 2} ^ {2 1. 8} & S _ {2 7. 7} ^ {3 2. 3} & F _ {3 7. 3} ^ {4 2. 7} \end{array} \right]
$$

denotes a four-stage MSPS with full inspection in the first and last stage, no inspection<sup>1</sup> in the second stage, and sampling inspection in the third stage. From the corresponding numbers, we read that inspection is performed between the limits 9.1 and 10.9 for the first stage, and so on for the other stages.

The basic idea is to start of with a population of M possible solutions to the problem. In the proposed EA, we use a population size M of 50. From this pool of initial solutions, some are selected (parents) to construct new solutions (children). The construction algorithm for the initial population consists in ran domizing the characters (N, S, F), and randomizing the limits by allowing (symmetrical) variation from the original limits (which are read in) by a certain user defined percentage (5% is applied in the calculated case example of Section 5). We assume symmetrical inspection limits, i.e. the expected value in each stage i is the arithmetic average of $( \mathrm { L I L } _ { i } , \mathrm { U I L } _ { i } )$

## 4.2.3. Objective function evaluation (fitness calculation)

For every candidate solution its fitness as a possible parent has to be evaluated, where fitness refers to measure of profit or goodness to be maximized while exploring the solution space. A naive choice is simply to use the value of the objective function for each candidate solution, but this is rarely a good idea, as it often leads to premature convergence to a poor local optimum (Reeves, 1993, p. 168). This problem can be mitigated using some scaling procedure. Diferent procedures are proposed and investigated in literature. We use a straightforward normalization procedure which ensures that the fitness values are all in [0, 1], and their sum is 1. This property allows us to set the probability of selecting a solution as a parent directly equal to its fitness value, so no additional conversion from fitness value to parent selection probability is required.

The fitness value f for each solution j in a population of M solutions is calculated as follows:

$$
f _ {j} = \frac {1 / \mathrm{TIC} _ {j}}{\sum_ {k = 1} ^ {M} (1 / \mathrm{TIC} _ {k})}\tag{11}
$$

This way, a smaller (better) TIC will result in a higher fitness value. This in fact corresponds to changing the minimization problem into a maximization problem.

## 4.2.4. Parent selection

Parent selection for producing ofspring is done as in Holland-s original Genetic Algorithm, i.e. for each reproduction two parents are chosen: one parent is selected on its fitness basis, the other is chosen randomly. The idea behind this scheme is that in doing this, the parent chosen for its fitness ensures genetic quality, while the random parent ensures genetic diversity.

Obviously, a proper balance between genetic quality and diversity is required within the population in order to ensure eficient search. This is dealt with through careful selection of the population related factors at the outset of the EA: population size, selection of the initial population, fitness calculation, crossover and mutation operators. A series of tests was performed to investigate the influence of these settings, the results are covered in Section 5.

## 4.2.5. Reproduction

The reproduction process makes use of the genes of the selected parents to produce ofspring that will make up the next generation. The reproduction operators exchange segments of the parents to build one or two children. The most common way to perform this exchange is as follows: a single crossover point X is chosen randomly; the children are then constructed as the pre-X section from one parent followed by the post-X section of the other. After construction of the children, mutation can be used to randoml modify genes of a single individual to further explore the solution space and to preserve genetic diversity. The occurrence of mutation is usually associated with a low probability. The one or two children are added to the new generation. After filling the entire new population with children (new solutions), this generation of solutions can replace the previous one entirely or partially, a population size of M being maintained throughout the course of the algorithm.

In our algorithm, the new generation consists of M - 1 children, the Mth solution in the next generation population is the best solution from the previous generation. Generating ofspring is performed in two consecutive steps: first crossover (with the crossover operators described below) is applied, then the inspection limits are adapted. After these two steps, reproduction is completed and the children thus obtained can populate the new generation. This way, the simultaneous determination of inspection option and inspection limits can be achieved. The inspection limits- adaptation is implemented analogous to the randomization of the limits used in the construction algorithm: we allow the children-s inspection limits to deviate from the parents- limits by a certain user defined percentage (5% is applied). The maximum number of generations is set to 800 and if no improvement is found after 100 generations, the EA is interrupted.

Our standard crossover operator randomly selects a crossover point, and constructs two new solutions by exchanging the tails (the whole of characters and limits) of both parents. An example for a six-stage MSPS and 2 as crossover point:

$$
\text { Parent   1: } \left[ \begin{array}{c c c c c c} F _ {9. 1} ^ {1 0. 9} & N _ {1 8. 2} ^ {2 1. 8} & S _ {2 7. 7} ^ {3 2. 3} & F _ {3 7. 3} ^ {4 2. 7} & S _ {4 6. 5} ^ {5 3. 5} & F _ {5 6. 0} ^ {6 4. 0} \end{array} \right]
$$

$$
\text { Parent   2: } \left[ N _ {9. 3} ^ {1 0. 7} \quad F _ {1 8. 0} ^ {2 2. 0} \quad F _ {2 7. 6} ^ {3 2. 4} \quad S _ {3 7. 5} ^ {4 2. 5} \quad N _ {4 6. 9} ^ {5 3. 1} \quad S _ {5 6. 5} ^ {6 4. 5} \right]
$$

$$
\text {   Child   1:   } \left[ \begin{array}{c c c c c c} F _ {9. 1} ^ {1 0. 9} & N _ {1 8. 2} ^ {2 1. 8} & F _ {2 7. 6} ^ {3 2. 4} & S _ {3 7. 5} ^ {4 2. 5} & N _ {4 6. 9} ^ {5 3. 1} & S _ {5 6. 5} ^ {6 4. 5} \end{array} \right]
$$

$$
\text {   Child   2:   } \left[ N _ {9. 3} ^ {1 0. 7} \quad F _ {1 8. 0} ^ {2 2. 0} \quad S _ {2 7. 7} ^ {3 2. 3} \quad F _ {3 7. 3} ^ {4 2. 7} \quad S _ {4 6. 5} ^ {5 3. 5} \quad F _ {5 6. 0} ^ {6 4. 0} \right]
$$

Instead of mutation, inversion is used (see Reeves, 1993, p. 173). It is applied through two reverse crossover operators, each associated with a low probability of 3%. Thus, in $6 \%$ of the cases, inversion is used instead of ‘‘normal’’ crossover (inversion type ‘‘reverse head’’ in 3% of the cases, inversion type ‘‘reverse tail’’ in 3% of the cases).

Reverse head crossover operator: This operator randomly chooses a crossover point (we will take 4 as example, and the same parents as above), and constructs two new solutions by exchanging the reversed heads (in reversing, only the characters, not the limits are reversed) of both parents.

$$
\begin{array}{l} \text {Child 1:} \left[ \begin{array}{c c c c c c} F _ {9. 1} ^ {1 0. 9} & S _ {1 8. 2} ^ {2 1. 8} & N _ {2 7. 7} ^ {3 2. 3} & F _ {3 7. 3} ^ {4 2. 7} & N _ {4 6. 9} ^ {5 3. 1} & S _ {5 6. 5} ^ {6 4. 5} \end{array} \right] \\ \text {Child 2:} \left[ \begin{array}{c c c c c c} S _ {9. 3} ^ {1 0. 7} & F _ {1 8. 0} ^ {2 2. 0} & F _ {2 7. 6} ^ {3 2. 4} & N _ {3 7. 5} ^ {4 2. 5} & S _ {4 6. 5} ^ {5 3. 5} & F _ {5 6. 0} ^ {6 4. 0} \end{array} \right] \end{array}
$$

Reverse tail crossover operator: This operator randomly chooses a crossover point (4 as example, same parents as above), and constructs two new solutions by exchanging the reversed tails (in reversing, only the characters, not the limits are reversed) of both parents.

$$
\begin{array}{l} \text {Child 1:} \left[ \begin{array}{c c c c c c} F _ {9. 1} ^ {1 0. 9} & N _ {1 8. 2} ^ {2 1. 8} & S _ {2 7. 7} ^ {3 2. 3} & F _ {3 7. 3} ^ {4 2. 7} & S _ {4 6. 9} ^ {5 3. 1} & N _ {5 6. 5} ^ {6 4. 5} \end{array} \right] \\ \text {Child 2:} \left[ \begin{array}{c c c c c c} N _ {9. 3} ^ {1 0. 7} & F _ {1 8. 0} ^ {2 2. 0} & F _ {2 7. 6} ^ {3 2. 4} & S _ {3 7. 5} ^ {4 2. 5} & F _ {4 6. 5} ^ {5 3. 5} & S _ {5 6. 0} ^ {6 4. 0} \end{array} \right] \end{array}
$$

## 5. Computational testing

Since—to the best of the authors- knowledge—no standard test cases exist in literature, a fictitious sixstage serial MSPS was constructed, representing a stack-up assembly operation, with the product dimension the quality characteristic under attention. Mathematically speaking, this comes down to performing an addition in each stage (the component added in each stage adds to the overall dimension). In Table 1 the process characteristics are shown. We used a combination of normal and uniform distributions to describe the dimensional characteristic of the components added in each stage. For normal distributions the parameters 1 and 2 designate the distribution-s mean and standard deviation, for uniform distributions the parameters designate the lower and upper boundary of the interval.

The parameters used in the cost model are shown in Table 2. The penalty cost $c _ { \mathrm { P } }$ is set at 3000. To conform to the specifications, the final products- dimension should be in the interval $[ \mathrm { L S } _ { 6 } , \mathrm { U S } _ { 6 } ] = [ 5 8 , 6 2 ] .$ . A batchsize $K = 1 0 0 0$ is assumed. As discussed in Section 3.1, these sets of parameters (process parameters and cost parameters) are exogenous to the inspection optimization problem. They do, however, influence the TIC and thus the outcome of the optimization process (for more details, see Van Volsem, 2002; Van Volsem and Van Landeghem, 2003).

Table 1 Process characteristics

<table><tr><td>Stage</td><td>Distribution</td><td>Parameter 1</td><td>Parameter 2</td><td>Expected value</td></tr><tr><td>1</td><td>Normal</td><td>10</td><td>0.3</td><td>10</td></tr><tr><td>2</td><td>Normal</td><td>10</td><td>0.5</td><td>20</td></tr><tr><td>3</td><td>Uniform</td><td>8.5</td><td>11.5</td><td>30</td></tr><tr><td>4</td><td>Normal</td><td>10</td><td>0.1</td><td>40</td></tr><tr><td>5</td><td>Normal</td><td>10</td><td>0.5</td><td>50</td></tr><tr><td>6</td><td>Uniform</td><td>9</td><td>11</td><td>60</td></tr></table>

Table 3 Solutions  
Table 2 Cost parameters

<table><tr><td>Stage</td><td>Test cost</td><td>Rework cost</td></tr><tr><td>1</td><td>1</td><td>50</td></tr><tr><td>2</td><td>1</td><td>100</td></tr><tr><td>3</td><td>2</td><td>200</td></tr><tr><td>4</td><td>1</td><td>400</td></tr><tr><td>5</td><td>1</td><td>800</td></tr><tr><td>6</td><td>2</td><td>1600</td></tr></table>

To test the EA for convergence, it was executed 25 times. This yielded minimal TIC-s ranging from 123,492 to 128,763, or a maximum 4% diference. The corresponding solution vectors are shown in Table 3, together with the number of generations and computing time necessary to find that solution (note that this number includes the generations of no improvement). The EA is coded in the C++ programming language, a PC with a 2.53 GHz processor and with 256 MB of RAM was used for the computational experiments.

<table><tr><td colspan="6">Solution vector</td><td>TIC</td><td>Generation</td><td>Time (hours:minutes)</td></tr><tr><td>1</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.907}^{31.093} & S_{38.745}^{41.255} & N & F_{58.015}^{61.985} \end{array} \right]$ </td><td>126,851</td><td>65</td><td>1:20</td></tr><tr><td>2</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.771}^{31.229} & S_{38.157}^{41.843} & S_{48.581}^{51.419} & F_{58.018}^{61.982} \end{array} \right]$ </td><td>126,882</td><td>91</td><td>2:42</td></tr><tr><td>3</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.771}^{31.229} & N & N & F_{58.002}^{61.998} \end{array} \right]$ </td><td>126,894</td><td>102</td><td>2:56</td></tr><tr><td>4</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.869}^{31.131} & N & S_{43.127}^{56.873} & F_{57.968}^{62.032} \end{array} \right]$ </td><td>128,687</td><td>110</td><td>3:01</td></tr><tr><td>5</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.875}^{31.125} & N & N & F_{58.016}^{61.984} \end{array} \right]$ </td><td>128,763</td><td>88</td><td>2:20</td></tr><tr><td>6</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.820}^{31.180} & N & S_{44.359}^{55.641} & F_{57.993}^{62.007} \end{array} \right]$ </td><td>124,325</td><td>75</td><td>1:59</td></tr><tr><td>7</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.798}^{31.202} & N & N & F_{57.975}^{62.025} \end{array} \right]$ </td><td>127,170</td><td>63</td><td>1:27</td></tr><tr><td>8</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.645}^{31.355} & S_{38.448}^{41.552} & N & F_{57.991}^{62.009} \end{array} \right]$ </td><td>128,611</td><td>82</td><td>2:16</td></tr><tr><td>9</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.840}^{31.160} & N & N & F_{57.990}^{62.010} \end{array} \right]$ </td><td>126,352</td><td>58</td><td>1:18</td></tr><tr><td>10</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.843}^{31.157} & N & S_{47.230}^{52.770} & F_{58.002}^{61.998} \end{array} \right]$ </td><td>123,549</td><td>83</td><td>2:11</td></tr><tr><td>11</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.920}^{31.080} & N & N & F_{58.012}^{61.988} \end{array} \right]$ </td><td>127,310</td><td>92</td><td>2:40</td></tr><tr><td>12</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.910}^{31.090} & N & N & F_{58.009}^{61.991} \end{array} \right]$ </td><td>126,522</td><td>83</td><td>2:36</td></tr><tr><td>13</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.810}^{31.190} & N & N & F_{58.004}^{61.996} \end{array} \right]$ </td><td>123,820</td><td>73</td><td>1:51</td></tr><tr><td>14</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.765}^{31.235} & S_{37.277}^{42.723} & S_{46.060}^{53.940} & F_{57.989}^{62.011} \end{array} \right]$ </td><td>125,839</td><td>68</td><td>1:36</td></tr><tr><td>15</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.830}^{31.170} & N & S_{48.287}^{51.713} & F_{58.015}^{61.985} \end{array} \right]$ </td><td>126,069</td><td>60</td><td>1:31</td></tr><tr><td>16</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.763}^{31.237} & S_{38.779}^{41.221} & N & F_{57.994}^{62.006} \end{array} \right]$ </td><td>123,883</td><td>64</td><td>1:31</td></tr><tr><td>17</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.870}^{31.130} & N & N & F_{58.000}^{62.000} \end{array} \right]$ </td><td>123,894</td><td>68</td><td>1:39</td></tr><tr><td>18</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.793}^{31.207} & S_{38.032}^{41.968} & N & F_{57.988}^{62.012} \end{array} \right]$ </td><td>124,670</td><td>86</td><td>2:00</td></tr><tr><td>19</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.904}^{31.096} & N & S_{40.620}^{59.380} & F_{58.051}^{61.949} \end{array} \right]$ </td><td>124,093</td><td>89</td><td>2:23</td></tr><tr><td>20</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.738}^{31.262} & N & S_{47.324}^{52.676} & F_{57.993}^{62.007} \end{array} \right]$ </td><td>124,410</td><td>68</td><td>1:38</td></tr><tr><td>21</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.792}^{31.208} & N & N & F_{57.999}^{62.001} \end{array} \right]$ </td><td>123,492</td><td>91</td><td>2:06</td></tr><tr><td>22</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{29.020}^{30.980} & N & S_{46.566}^{53.434} & F_{58.012}^{61.988} \end{array} \right]$ </td><td>127,899</td><td>62</td><td>1:27</td></tr><tr><td>23</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.740}^{31.260} & N & N & F_{58.021}^{61.979} \end{array} \right]$ </td><td>126,442</td><td>117</td><td>3:12</td></tr><tr><td>24</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.821}^{31.179} & S_{36.385}^{43.615} & S_{46.677}^{53.323} & F_{57.977}^{62.023} \end{array} \right]$ </td><td>127,066</td><td>92</td><td>2:33</td></tr><tr><td>25</td><td colspan="5"> $\left[ \begin{array}{lll} N & N & F_{28.918}^{31.082} & N & S_{46.460}^{53.540} & F_{58.009}^{61.991} \end{array} \right]$ </td><td>125,902</td><td>60</td><td>1:33</td></tr></table>

Fig. 2 shows the apparent conversion from the 68th generation onwards. From the results in Table 3 the EA-s convergence can be confirmed: it can be seen that all 25 solutions are of the same form NNFXXF, with $X \in \{ S , N \}$ (the indiference between S and N in stages 4 and 5 is discussed below). Moreover, the inspection limits $\mathrm { L I L } _ { 3 } , \mathrm { U I L } _ { 3 }$ and ${ \mathrm { L I L } } _ { 6 } { , } { \mathrm { U I L } } _ { 6 } ,$ corresponding with the stages where full inspection F is applied, are in the same range in each case.

In the first two stages, no inspection N is opted for. This means the cost avoidance of detecting defective products already in stages 1 or 2 does not outweigh the costs of performing full inspection in these stages. This can be explained considering the relatively low rework costs compared to the test costs in these stages.

In stages 3 and 6, full inspection F is selected. For stage 6 this entails avoidance of penalty costs. Indeed, the inspection limits $\mathrm { L I L } _ { 6 } , \mathrm { U I L } _ { 6 }$ selected by the EA, almost coincide with the specification limits $\mathrm { L S } _ { 6 } , \mathrm { U S } _ { 6 }$ (maximum diference $= \pm 0 . 0 5 1$ or less than 0.1%). The choice for full inspection in stage 3 implies that the cost avoidance through detecting defective products outweighs the incurred test costs. The choice of inspection limits $\mathrm { L I L } _ { 3 } , \mathrm { U I L } _ { 3 }$ will balance both cost aspects.

The fact that there is no clear discrimination between N and S inspection in stages 4 and 5, can be attributed to the full inspection F in stage 3. Seeing this provides stage 4 with an input of 0% defectives, and considering the low added variance of the production operation in stage 4, it can be argued that the fault occurrence in stage 5 will still be close to 0%. This means that in stages 4 and 5 there will be very few defec tives, reducing the need for (sampling) inspection. Performing sampling inspection S will thus not be advantageous compared to performing no inspection N. On the other hand, it will not be disadvantageous either, because given the relatively small sample size $( s _ { i } = 5 0 , \ \forall i )$ , the diferential cost of performing sampling inspection in stages 4 or 5 compared to performing no inspection will not be substantial. This explains the apparent indiference in selecting S or N in stages 4 and 5.

25 EA replications  
![](images/2ca13a6c450e85e6abde9ce60a3fad37942cf5698025f0a9b4deb7161aa38289.jpg)  
Fig. 2. TIC as a function of generation number, for 25 replications of the EA.

As mentioned in Section 4.2, careful selection of population related factors at the outset of the EA (such as population size, initial population, fitness calculation, crossover and mutation operators) is important to increase the probability of finding good solutions. The parameter settings were based on general recommendations found in textbooks on GA/EA-s (Reeves, 1993; Michaelewicz and Fogel, 2000), on insight in the problem specifics, as suggested in Silver (2004), and on several exploratory test runs.

The EA was tested—ceteris paribus—with population sizes 25, 50 and 100. This revealed, for this specific problem, no noticeable diferences. We therefore, selected a population size of 50 to keep computation times acceptable while safeguarding solution diversity, as suggested by Reeves (1993) and Michaelewicz and Fogel (2000). As explained in Section 4.2, we use inversion instead of mutation. The EA was tested with inversion parameters 6%, 12% and 20%. This again yielded no significant diferences, we opted for the smallest inversion percentage, i.e. 6% (3% reverse-head and 3% reverse-tail). Solution evaluation is based on the average TIC from a number simulated production batches (simulation runs). The metaheuristic was tested with 25, 50 and 100 simulation runs. Convergence of the EA could be demonstrated with 50 and 100 runs, whereas 25 runs did not sufice. We therefore, opted for 50 runs, to keep computation times acceptable. The number of simulation runs can also be derived dynamically, guaranteeing minimum confidence intervals for the simulation output of interest, see for example Law and Kelton (1982, p. 302).

## 6. Conclusions and suggestions for further research

Eficient production quality control is a major issue to manufacturers. Most production processes consist of a sequence of production stages. Each stage (but the last) produces input for the next production stage. As the production processes at each stage are generally stochastic in nature, deviations from product specifications occur, which, without intervention, will accumulate in the course of the production process. Quality inspection only at the last stage would therefore result in a large number of faulty products and high rework and scrap costs.

An optimal inspection strategy for a so-called serial multi-stage production system (MSPS) has to decide on (i) the number and location of inspection stations, (ii) the size of the production fraction subject to inspection (sample size) and (iii) the rigor of the inspections (acceptance limits) at each inspection station that minimize total expected inspection costs.

To our best of knowledge, this paper contains the first attempt at jointly optimizing the number and location of inspection stations, their inspection type and inspection limits (concurrent work includes the sampling parameters). Discrete event simulation is used to model the multi-stage production system subject to inspection and to calculate the resulting inspection costs, an Evolutionary Algorithm is suggested to optimize the inspection strategies. Computational testing illustrates potential of metaheuristics for optimizing quality inspection.

Since no standard test sets are available, further research is needed on designing problem instances for evaluating solution approaches for inspection strategies for multi-stage processes. Model extensions could accommodate features such as variable sampling parameters and a dynamic determination of the number of simulation runs.

## Acknowledgments

The authors wish to thank K. So¨rensen and two anonymous referees for the constructive comments that helped to improve the presentation of the paper. B. Raa-s help in optimizing the computer code is gratefully acknowledged.

## References

Bai, D.S., Yun, H.J., 1996. Optimal allocation of inspection efort in a serial multi-stage production system. Computers and Industrial Engineering 30 (3), 387–396.

Ballou, D.P., Pazer, H.L., 1982. The impact of inspector fallibility on the inspection policy in serial production systems. Management Science 28 (4), 387–399.

Barad, M., Braha, D., 1996. Control limits for multi-stage manufacturing processes with binomial yield (Single and Multiple Production Runs). Journal of the Operational Research Society 47, 98–112.

Britney, R.R., 1972. Optimal screening plans for nonserial production systems. Management Science 18 (9), 550–559.

De Jong, K.A., 1975. An Analysis of the Behaviour of a Class of Genetic Adaptive Systems. Ph.D. thesis, University of Michigan Press.

Emmons, H.E., Rabinowitz, G., 2002. Inspection allocation for multistage deteriorating production systems. IIE Transactions 34, 1031–1041.

Eppen, G.D., Hurst Jr., E.G., 1974. Optimal location of inspection stations in a multistage production process. Management Science 20 (8), 1194–1200.

Goldberg, D., 1989. Genetic Algorithms in Search, Optimization, and Machine Learning. Addison Wesley, NY.

Holland, J.H., 1975. Adaptation in Natural and Artificial Systems. University of Michigan Press.

Law, A.M., Kelton, W.D., 1982. Simulation Modeling and Analysis. McGraw-Hill, New York.

Lindsay, G.F., Bishop, A.B., 1964. Allocation of screening inspection efort—a dynamic programming approach. Management Scienc 10 (2), 342–352.

Michaelewicz, Z., Fogel, D.B., 2000. How to Solve it: Modern Heuristics. Springer-Verlag, Berlin.

Rabinowitz, G., Yahalom, O., 2001. Imperfect inspection of a multi-attribute deteriorating production system—a continuous time model. Quality and Reliability Engineering International 17, 407–418.

Raz, T., 1986. A survey of models for allocating inspection efort in multistage production systems. Journal of Quality Technology 18 (4), 239–247.

Reeves, C.R., 1993. Modern Heuristic Techniques for Combinatorial Problems. Blackwell Scientific Publications.

Silver, E., 2004. An overview of heuristic solution methods. Journal of the Operational Research Society 55, 936–956.

Van Volsem, S., 2002. Optimizing inspection strategies for multi-stage process chains: A case study. In: 16th Triennial IFORS Conference. International Federation of Operational Research Societies.

Van Volsem, S., Van Landeghem, R., 2003. Optimizing inspection strategies for multi-stage processes: An exploratory modelling framework and simulation. In: 5th international QUALITA Conference. Institut de Suˆrete´ Industrielle.

Villalobos, J.R., Foster, J.W., Disney, R.L., 1993. Flexible inspection systems for serial multi-stage production systems. IIE Transactions 25 (3), 16–26.

White, L.S., 1969. Shortest route models for the allocation of inspection efort on a production line. Management Science 15 (5), 249– 259.