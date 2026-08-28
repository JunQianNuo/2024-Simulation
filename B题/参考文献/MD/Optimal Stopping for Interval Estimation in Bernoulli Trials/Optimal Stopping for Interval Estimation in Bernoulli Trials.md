---
raw_title: Optimal Stopping for Interval Estimation in Bernoulli Trials
subject: Optimal Stopping for Interval Estimation in Bernoulli Trials
source: Optimal Stopping for Interval Estimation in Bernoulli Trials.pdf
status: xparse-repaired-fulltext
parser: xparse-cli
pages: 22
note: original one-page catalog record preserved as Optimal Stopping for Interval Estimation in Bernoulli Trials_metadata.txt
---

<!-- 1 -->

# Optimal Stopping for Interval Estimation in

# Bernoulli Trials

Tony Yaacoub,George V. Moustakides, Senior Member, IEEE and Yajun Mei

## Abstract

We propose an optimal sequential methodology for obtaining confidence intervals for a binomial proportion $\theta$ . Assuming that an i.i.d. random sequence of Benoulli(θ) trials is observed sequentially,we are interested in designing a) a stopping time T that will decide when is the best time to stop sampling the process, and b) an optimum estimator $05$  that will provide the optimum center of the interval estimate of $\theta$ . We follow a semi-Bayesian approach, where we assume that there exists a prior distribution for $\theta$ ,and our goal is to minimize the average number of samples while we guarantee a minimal coverage probability level. The solution is obtained by applying standard optimal stopping theory and computing the optimum pair $\left(T,\hat {\theta }_{T}\right)$ numerically. Regarding the optimum stopping time component T,we demonstrate that it enjoys certainvery uncommon characteristics not encountered in solutions of other classical optimal stopping problems. Finally, we compare our method with the optimum fixed-sample-size procedure but also with existing alternative sequential schemes.

## Index Terms

Sequentia1 estimation, confidence intervals, binomial proportion, optimal stopping, sequential analy-sis.

## I. INTRODUCTION

Interval estimation of a binomial proportion $\theta$  is one of the most basic problems in statistics with many important real-world applications. Some classical applications include interval estimation of the

T. Yaacoub and Y. Mei are with the H. Milton Stewart School of Industrial and Systems Engineering, Georgia Institute of Technology, Atlanta, GA, USA. E-mail: (tyaacoub, ymei3)@gatech.edu. Website: http://www2.isye.gatech.edu/~ymei/.

G.V. Moustakides is with the Department of Computer Science, Rutgers University, Piscataway, NJ, USA and the Electrical and Computer Engineering Department, University of Patras, Rion, Greece. E-mail: george.mnoustakides@rutgers.edu, moustaki@upatras.gr. Website: https://www.cs.rutgers.edu/~gm463/.

Manuscript received ;revised

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- arXiv:1711.06912v1 [stat.ME] 18 Nov 2017 -->

<!-- 2 -->

prevalence of a rare disease [1]; interval estimation of the overall response rate in clinical trials [2]; and accuracy assessment in remote sensing [3]. In these applications, the sample size is fixed in advance, and a confidence interval for $\theta$  is obtained. There exists extensive bibliography regarding derivations of confidence intervals for $\theta$  when the sample size is fixed. Perhaps, the most widely known in this category is Wald's interval, which takes the form $\hat {\theta }_{\mathrm {T}}\pm z_{\frac {α}{2}}\sqrt {\frac {\hat {\theta }_{\mathrm {T}}\left(1-\hat {\theta }_{\mathrm {T}}\right)}{\mathrm {T}}}$ ,where T is the fixed sample size, $1-α$ expresses the desired coverage probability, $\hat {\theta }_{\mathrm {T}}$  is the sample mean of $\theta$  and $z_{\frac {α}{2}}$  satisfies $Q\left(z_{\frac {α}{2}}\right)=\frac {α}{2}$  with $Q(x)$ denoting the complementary cdf of a standard $N(0,1)$  Gaussian random variable. This confidence interval is derived based on the asymptotic normality of $\hat {\theta }_{\mathrm {T}}$ and, therefore, exhibits poor behavior when $T\theta (1-\theta )$ is small [4]-[7]. Several efforts to improve Wald's classical method are reported in [4], [8]-[12].There are also Baysian-based techniques [5], [13], [14] while in [4]-[7], [15] there exists interesting surveys that evaluate the relative performance of the above methods. Finally we must mention that [16] provides explicit formulas for the required sample size that can guarantee a prescribed coverage probability.

In many modern applications, sampling observations is costly and time consuming. Therefore, there is a desire to limit the sampling size without, however, compromising the quality of the interval estimate. For instance, in automatic fraud detection infinance, one needs to manually go through the "suspect" financial transactions that are automatically detected as fraudulent by some machine learning or other computer algorithm. Since the manual process is expensive in labor and cost, it is desirable to quickly estimate, with high confidence, what percentage of the suspect transactions are truly fraudulent. A different motivating application is in Statistical Model Checking, where with an approximate verification method, one overcomes the state space explosion problem for probabilistic systems by Monte Carlo simulations. Given an executable stochastic system, we verify a system's property with simulation and we desire to estimate the probability $\theta$  by which the system satisfies the property in question. The goal is to estimate $\theta$  within acceptable margins of error and confidence (see [17] and references therein). Because Monte Carlo simulations very often tend to require extensive time and computing power, it is advantageous to reduce their number assuring, at the same time, satisfactory quality levels for the corresponding estimate. The sequential version of the interval estimation aims exactly at reducing the sample size by selecting it to be random and, in particular, a stopping time controlled by the observations themselves. The literature focusing on the sequential setup of the problem is limnited compared to its fixed sample-size counterpart (see [18]-[20]).However,none of these articles is able to claim optimality of their corresponding schemes in any sense.

The objective of our current work is to offer optimum sequential methods for interval estimation of $\theta$ ,with the quality of the estimate expressed through the coverage probability. In addition to deriving the optimum scheme, we will also demonstrate some very uncommon but highly interesting properties 

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 3 -->

of the optimum solution. These properties are not encountered in optimum sequential schemes derived for other weIl known sequential problems (i.e. sequential hypothesis testing). We must also add that our methodology exhibits similarities with the work developed in [21]. However, the focus in [21] is on the actual estimate of $\theta$  with the adopted criterion being a variation of the classical mean square error. In our work, as we pointed out, we focus on confidence intervals and coverage probabilities; and, as it turns out, this difference makes our derivations and proofs far more complicated, requiring original analytical methodology. This becomes particularly apparent when we attempt to establish the validity of the unique properties, mentioned before, that characterize our optimum solution.

The remainder of this article is organized as follows. In Section II we discuss our proposed frame-work for interval estimation for $\theta$  and propose a well-defined optimization problem and discuss its general solution. In Section III we focus on the computational aspects of the optimum scheme and the unique properties that they characterize it. In Section IV we compare the proposed scheme against the fixed-sample-size and two existing sequential methods in the literature. Finally, Section V contains our conclusions.

## II. PROPOSED FRAMEWORK

We observe sequentially an i.i.d. process $X_{1},X_{2},\cdots \text {of}$ Bernoulli random variables with $X_{t}\in \{0,1\}$ and $\mathrm {P}\left(X_{t}=1\right)=\theta =1-\mathrm {P}\left(X_{t}=0\right)$ $\theta \in [0,$ $1]$ . The goal is to provide a confidence interval for $\theta$ .We are interested in confidence intervals of fixed width equal to $2h$  for some pre-specified $h\in \left(0,\frac {1}{2}\right)$ We would also like our scheme to be able to guarantee a coverage probability equalto $1-α,$ ,where $α\in (0,1)$ is given. Our scheme consists of a pair $\left(T,\hat {\theta }_{T}\right)$ , that is, a stopping time T and a mid-point estimator1 $\hat {\theta }_{T}$ ,where T is adapted to the observation history (filtration generated by the observations) and $\hat {\theta }_{T}$ is a function of the observations accumulated up to the time of stopping T. We would like to solve the following constrained optimization problem for the optimum pair

$\inf _{T,\hat {\theta }_{T}}\mathrm {E}[T|\theta ]$ ,subject to: $\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h|\theta \right)\leq α,$  (1)

where the desired interval estimate is $\left[\hat {\theta }_{T}-h,\hat {\theta }_{T}+h\right]$ (with the two ends cropped at 0 and 1,respectively, whenever they exceed the two limits) and where $P(·|\theta )$ and $E[·|\theta ]$ denote probability and expectation for given $\theta$ .

Although (1) seems as the ideal formulation, it unfortunately targets an infeasible goal. We note that we are asking for the pair $\left(T,\hat {\theta }_{T}\right)$ to minimize the average number of samples for every value of the

The estimate $\hat {\theta }_{T}$ does not have the meaning of a classical parameter estimator. It is the mid-point of the confidence interval $\left[\hat {\theta }_{T}-h,\hat {\theta }_{T}+h\right]$ and does not necessarily constitute an efficient estimate of $\theta$ .

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 4 -->

parameter $\theta$ . In other words, we want our scheme to enjoy a uniform optimality property over all $\theta$ ,a requirement which is impossible to satisfy. In order to be able to find a solution that has a well-defined form of optimality, we adopt a semi-Bayesian approach² and assume that a prior $\pi (\theta )$  for $\theta$  is available. This allows for the following modification of the previous constrained optimization

$\inf _{T,\hat {\theta }_{T}}\mathrm {E}[T]$ ,subject to: $\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h\right)\leq α$  (2)

where $P(·)$  and $E[·]$  denote probability and expectation including averaging over $\theta$  with the help of the prior.

**Remark** **1.** Ne must emphasize that the constraint in (2) does not guarantee that the desired coverage probability will also hold for each individual $\theta$ ,namely $\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h|\theta \right)\leq α,$ ,a property which is particularly desirable in practice. Perhaps, a more meaningful problem to consider in place of (2) would have been

$\inf _{T,\hat {\theta }_{T}}\mathrm {E}[T]$ ,subject to: $\sup _{\theta }\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h|\theta \right)\leq α,$  (3)

that assures a coverage probability ofat least $1-α$  for every $\theta$ . Unfortunately, it is unclear how to derive the optimal solution to this alternative formulation. Consequently, we focus on (2) as the optimum scheme we are going to develop, but in our numerical examples, we will evaluate it in terms of (3) as well.

Let $c>0$ denote a Lagrange multiplier that we use to combine the two terms in (2) into a single cost function $J\left(T,\hat {\theta }_{T}\right)=c\mathrm {E}[T]+\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h\right)$ , and consider the unconstrained optimization problem

$$\inf _{T,\hat {\theta }_{T}}J\left(T,\hat {\theta }_{T}\right)=\inf _{T,\hat {\theta }_{T}}\left\{c\mathrm {E}[T]+\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h\right)\right\}\tag{4}$$

We will first identify the solution to (4) and then demonstrate that a proper selection of c can also solve the constrained problem in (2).

### A. The Unconstrained Problem

We start by considering the classical Bayes estimation problem for fixed sample size t

$$\inf _{\hat {\theta }_{t}}\mathrm {P}\left(\left|\hat {\theta }_{t}-\theta \right|>h\right)\tag{5}$$

If we observe $\mathscr {F}_{t}=σ\left\{X_{1},\cdots ,X_{t}\right\}$ then,given that $\left\{X_{t}\right\}$ is i.i.d. Bernoulli(θ), the probability to obtain a specific combination of samples given $\theta$  is equal to $\theta ^{S_{t}}(1-\theta )^{t-S_{t}}$ ,where $S_{t}=\sum _{k=1}^{t}X_{k}$ is the number

²The term "semi-Bayesian" is used because our setup involves two different components where one is optimized while the other is constrained, unlike full-Bayesian approaches that combine all terms into a single performance measure.

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 5 -->

of "successes" up to time t. This implies that the posterior probability density of $\theta$  given the observations can be written as

$$\pi _{t}\left(\theta |\mathscr {F}_{t}\right)=\pi _{t}\left(\theta |S_{t}\right)=\frac {\theta ^{S_{t}}(1-\theta )^{t-S_{t}}\pi (\theta )}{\int _{0}^{1}\theta ^{S_{t}}(1-\theta )^{t-S_{t}}\pi (\theta )d\theta }\tag{6}$$

From Bayesian estimation theory [22, Page 142], we have that the optimization in (5) is achieved by the following Bayes estimator

$$\hat {\theta }_{t}\left(S_{t}\right)=\arg \inf _{\hat {\theta }_{t}}\mathrm {P}\left(\left|\hat {\theta }_{t}-\theta \right|>h|\mathscr {F}_{t}\right)=\arg \sup _{\hat {\theta }_{t}}\int _{\max \left\{\hat {\theta }_{t}-h,0\right\}}^{\min \left\{\hat {\theta }_{t}+h,1\right\}}\pi _{t}\left(\theta |S_{t}\right)d\theta ,\tag{7}$$

yielding the corresponding optimum conditional complementary coverage probability

$$\mathscr {C}_{t}\left(S_{t}\right)=\inf _{\hat {\theta }_{t}}\mathrm {P}\left(\left|\hat {\theta }_{t}-\theta \right|>h|\mathscr {F}_{t}\right)=1-\sup _{\hat {\theta }_{t}}\int _{\max \left\{\hat {\theta }_{t}-h,0\right\}}^{\min \left\{\hat {\theta }_{t}+h,1\right\}}\pi _{t}\left(\theta |S_{t}\right)d\theta\quad =1-\int _{\max \left\{\hat {vartheta}_{t}\left(S_{t}\right)-h,0\right\}}^{\min \left\{\hat {vartheta}_{t}\left(S_{t}\right)+h,1\right\}}\pi _{t}\left(\theta |S_{t}\right)d\theta .\tag{8}$$

From (7) and (8) we observe that both quantities $\hat {vartheta}_{t}\left(S_{t}\right),\mathscr {C}_{t}\left(S_{t}\right)$ are $\mathscr {F}_{t^{-}}$ measurable and,more precisely, functions of $S_{t}$ . For known prior $\pi (\theta )$ , we can, at least numerically, compute the Bayes estimate and the corresponding optimum conditional complementary coverage probability for each combination of integer pair $\left(t,S_{t}\right)$ 

**Remark** 2. By focusing on (7), we can make a small but interesting observation: Regarding the Bayes estimate $\hat {vartheta}_{t}\left(S_{t}\right)$ it is easy to verify that

$$h\leq \hat {vartheta}_{t}\left(S_{t}\right)\leq 1-h.\tag{9}$$

Indeed, this is clear, because if in (7) we select $\hat {\theta }_{t}<h$ or $\hat {\theta }_{t}>1-h$ ,this will yield an inferior cost compared to the selection $\hat {\theta }_{t}=h\text {or}$ $\hat {\theta }_{t}=1-h,$ ,respectively. The implication of this observation is that $\hat {vartheta}_{t}\left(S_{t}\right)$  will be biased and inconsistent when considered as an estimate of the true parameter $\theta$ , at least for values of $\theta$  outside the interval $[h,1-h]$ . As we mentioned, the correct meaning of this quantity is that it constitutes the mid-point of the confidence interval $\left[\hat {vartheta}_{t}\left(S_{t}\right)-h,\hat {vartheta}_{t}\left(S_{t}\right)+h\right]$ with the latter enjoying, for each fixed $t$ , the largest possible coverage probability.

Consider now the optimization in (4) which will be performed in twvo steps: First we fix the stopping time T and minimize $J\left(T,\hat {\theta }_{T}\right)$ with respect to $\hat {\theta }_{T}$ ; the resulting expression is then minimized, during the second step, over T in order to obtain the optimum pair. WNe have the following lemma that addresses the first problem.

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 6 -->

**Lemma** 1.Assume stopping time T is fixed and satisfies $T\leq N,$ ,where $N>0$ is some deterministic integer.Then,

$$J\left(T,\hat {\theta }_{T}\right)=c\mathrm {E}[T]+\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h\right)\geq \mathrm {E}\left[cT+\mathscr {C}_{T}\right]=\mathrm {J}(T)\tag{10}$$

with equality when we apply the corresponding Bayesian estimator $\hat {\theta }_{T}=\hat {vartheta}_{T}$ at the time of stopping.

Proof. The proof is straightforward and presented in the Appendix.

☐

A side-product of Lemma 1, as it can be verified from the corresponding proof in the Appendix, is the fact that the Bayesian estimator is not only optimum for fixed sample size, but it retains its optimality property when the sample size is controlled by any stopping time T adapted to the observations.

Using (10) from Lemma 1, we are now left with the optimization of the stopping time T. Assuming that N is an integer which is sufficiently large, we consider the following optimization over stopping times that are bounded by N

$$\inf _{0\leq T\leq N}\mathrm {\;J}(T)=\inf _{0\leq T\leq N}\mathrm {E}\left[cT+\mathscr {C}_{T}\right]\tag{11}$$

This is a classical finite horizon optimal stopping problem with cost per sample equal to c and cost for stopping at t equal to $\mathscr {C}_{t}$ . Of course, it is only natural to wonder wvhy we limited our analysis to finite horizons instead of considering the more classical infinite horizon version. As we will see in the sequel, for the most common prior we will be able to demonstrate that the infinite horizon assumption is completely unnecessary. Indeed, the optimum stopping time will turn out to be bounded by a deterministic quantity,suggesting that by limiting ourselves to a (sufficiently large) finite horizon, we do not suffer any performance losS.

In order to solve the optimization problem defined in (11), we follow the classical optimal stopping theory [23].For $t=0,1,\cdots ,N$ define the sequence of optimal average residual costs

$$\mathscr {V}_{t}=\inf _{t\leq T\leq N}\mathrm {E}\left[c(T-t)+\mathscr {C}_{T}|\mathscr {F}_{t}\right]\tag{12}$$

then we have

$\mathscr {V}_{t}=\min \left\{\mathscr {C}_{t},c+\mathrm {E}\left[\mathscr {V}_{t+1}|\mathscr {F}_{t}\right]\right\}$ $t=N,\cdots ,1,0,$  (13)

with the backward recursion initialized with $\mathscr {V}_{N+1}=1$ . Regarding this last selection, it produces $\mathscr {V}_{N}=$ $\mathscr {C}_{N}$ since the latter is a probability. In fact, this is exactly what the optimum residual cost at N must be, because if we have not stopped before N, then we necessarily stop at N and this produces cost $\mathscr {C}_{N}$ (simply the cost of stopping at N). The total optimum cost is expressed through $\mathscr {V}_{0}$ ,namely $\mathscr {V}_{0}=\inf _{0\leq T\leq N}\mathrm {\;J}(T)$ The next lemma specifies in more detail the recursion in (13).

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 7 -->

**Lemma** **2.** Consider the recursion in (13) then, the optimal residual cost $\mathscr {V}_{t},$ $t=N,\cdots ,$ $,0$ is a function $\mathscr {V}_{t}\left(S_{t}\right)$ $\text {of}S_{t}$ and therefore $\mathscr {F}_{t}$ -measurable. Furthermore, (13) can be written as

$\mathscr {V}_{t}\left(S_{t}\right)=\min \left\{\mathscr {C}_{t}\left(S_{t}\right),c+\tilde {\mathscr {V}}_{t}\left(S_{t}\right)\right\},$ $t=N,\cdots ,0,$  (14)

where $\tilde {\mathscr {V}}_{t}\left(S_{t}\right)$ expresses the optimum average residual cost to continue, satisfying

$$\tilde {\mathscr {V}}_{t}\left(S_{t}\right)=g_{t+1}\left(S_{t}\right)\mathscr {V}_{t+1}\left(S_{t}+1\right)+\left(1-g_{t+1}\left(S_{t}\right)\right)\mathscr {V}_{t+1}\left(S_{t}\right)\tag{15}$$

$$g_{t+1}\left(S_{t}\right)=\mathrm {P}\left(X_{t+1}=1|\mathscr {F}_{t}\right)=\frac {\int _{0}^{1}\theta ^{S_{t}+1}(1-\theta )^{t-S_{t}}\pi (\theta )d\theta }{\int _{0}^{1}\theta ^{S_{t}}(1-\theta )^{t-S_{t}}\pi (\theta )d\theta }\tag{16}$$

Finally, if the prior $\pi (\theta )$  is symmetric around $\frac {1}{2}$ then the functions $\mathscr {C}_{t}\left(S_{t}\right)$ $,\mathscr {V}_{t}\left(S_{t}\right),\tilde {\mathscr {V}}_{t}\left(S_{t}\right)$ are symmetric with respect to $S_{t}$ around the value $\frac {t}{2}$ 

Proof. The validity of this lemma is straightforward and can be easily established using induction. We therefore give no further details. ☐

Once the sequence of optimal residual costs has been obtained through the solution of (14), it is then immediate to define the optimum stopping time $T_{\mathrm {o}}$  that solves the minimization problem in (11).Again, optimal stopping theory [23] suggests that

$$T_{\mathrm {o}}=\inf \left\{0\leq t\leq N:\mathscr {V}_{t}\left(S_{t}\right)=\mathscr {C}_{t}\left(S_{t}\right)\right\}=\inf \left\{0\leq t\leq N:\mathscr {C}_{t}\left(S_{t}\right)\leq c+\tilde {\mathscr {V}}_{t}\left(S_{t}\right)\right\}\tag{17}$$

In other words, when the optimum residual cost $\mathscr {V}_{t}\left(S_{t}\right)$ matches, for the first time, the cost for stopping $\mathscr {C}_{t}\left(S_{t}\right)$ or, equivalently,the cost of stopping is smaller than the residual cost of continuing, this is when we stop. Since the functions involved depend on $S_{t}$ , this quantity can serve as our test statistic and we can express the stopping rule in (17) in terms of $S_{t}$ . Specifically, for each time t, we can find the sampling region $Ω_{t}=\left\{0\leq S_{t}\leq t:\mathscr {V}_{t}\left(S_{t}\right)<\mathscr {C}_{t}\left(S_{t}\right)\right\}=\left\{0\leq S_{t}\leq t:c+\tilde {\mathscr {V}}_{t}\left(S_{t}\right)<\mathscr {C}_{t}\left(S_{t}\right)\right\}$ with $Ω_{N}=\varnothing$ ,and we can equivalently define the stopping time as $T_{\mathrm {o}}=\inf \left\{0\leq t\leq N:S_{t}\notin Ω_{t}\right\}$ 

### B. The Constrained Problem

Let us now turn to the constrained problem in (2) which we can solve with the results we have so far. We will show that (2) can be recovered as an instance of the unconstrained version (4) corresponding to a special selection of the Lagrange multiplier c. Our result is summarized in the following theorem.

**Theorem** 1. For the solution of (2) we distinguish two cases:

i) $\text {If}α\geq \mathscr {C}_{0}=\mathrm {P}\left(\left|\hat {vartheta}_{0}-\theta \right|>h\right)$ ,with $\hat {vartheta}_{0}=\arg \inf _{\hat {\theta }_{0}}\mathrm {P}\left(\left|\hat {\theta }_{0}-\theta \right|>h\right)$ ,then the optimum is to stop without taking any samples,i.e. $T_{\mathrm {o}}=0$ and use as mid-point of the optimum confidence interval the value $\hat {vartheta}_{0}$ which is based only on the prior $\pi (\theta )$ 

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 8 -->

ii) $\text {IfP}\left(\left|\hat {vartheta}_{0}-\theta \right|>h\right)>α$ then for any horizon $N\geq N_{α}$ where $N_{α}$ satisfies $\mathrm {P}\left(\left|\hat {vartheta}_{N_{α}}-\theta \right|>h\right)<α,$  there exists Lagrange multiplier $c_{*}$ such that the solution of (4) is also the solution to (2) that can involve a possible randomization before taking any samples.

Proof. The proof of this theorem is presented in the Appendix.

☐

## III. PROPERTIES OF THE OPTIMUM SOLUTION

If we fix the value N of the horizon and the cost per sample c, we can then compute the mid-points $\left\{\left\{\hat {vartheta}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$  of the confidence intervals from (7). Assuming that $\pi (\theta )$  is continuous, candidates for $\hat {vartheta}_{t}\left(S_{t}\right)$ can be obtained from the solution of the following equation which we obtain by differentiating (7) with respect to $\hat {\theta }_{t}$ 

$$\left(\hat {\theta }_{t}+h\right)^{S_{t}}\left(1-\hat {\theta }_{t}-h\right)^{t-S_{t}}\pi \left(\hat {\theta }_{t}+h\right)-\left(\hat {\theta }_{t}-h\right)^{S_{t}}\left(1-\hat {\theta }_{t}+h\right)^{t-S_{t}}\pi \left(\hat {\theta }_{t}-h\right)=0.\tag{18}$$

The previous equation has clearly a solution in the interval $[h,1-h]$  when $0<S_{t}<t$ with the corresponding value providing a (local) extremum for the coverage probability. To these candidate mid-points we must include the two end points $h,1-h$ since the global maximum can occur at the two ends as well. Therefore, we need to examine which of these cases provides the best coverage probability and select the corresponding value as our optimum mid-point $\hat {vartheta}_{t}\left(S_{t}\right)$ .When $S_{t}=0,t$ it is possible (18) not to have any solution in $[h,1-h]$ .In this case, $\hat {vartheta}_{t}(0)$ and $\hat {vartheta}_{t}(t)$ are equal to one of the two end values $h$ or $1-h$ . Having identified the optimum mid-points $\left\{\left\{\hat {vartheta}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ ,we apply (8) to compute the corresponding optimum complementary conditional coverage probabilities $\left\{\left\{\mathscr {C}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ 

The next step consists in computing $\left\{\left\{g_{t+1}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ for $t=0,\cdots ,N$ and $S_{t}=0,\cdots ,t$ with numerical integration. Once we have available $\left\{\left\{\mathscr {C}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ and $\left\{\left\{g_{t+1}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ ,we can then use them in the backward recursion (14)to find the sequence $\left\{\left\{\tilde {\mathscr {V}}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ and the optimum residual cost sequence $\left\{\left\{\mathscr {V}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ . To identify the stopping rule, according to (17) we must compare the two sequences $\left\{\left\{\mathscr {C}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ $\left\{\left\{\mathscr {V}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ element-by-element. At coordinates $\left(t,S_{t}\right)$ where the sequences differ, we decide to continue sampling; whereas if they are equal, we decide to stop. This generates the sequence of sampling regions $\left\{Ω_{t}\right\}_{t=0}^{N}$ . Equivalently, we can compare $\left\{\left\{\mathscr {C}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ with $\left\{\left\{c+\tilde {\mathscr {V}}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ ,and wherever the first is no larger than the second, we stop, while we continue sampling in the opposite case.

We now present a conjecture that contains two significant claims for the optimum stopping time for the problem in (4) which we believe are valid for any prior $\pi (\theta )$ . We were able to provide a proof for the first claim (Lemma 3) for a rich class of priors, and prove both claims (Theorem 2) providing also 

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 9 -->

quantitative information when the prior is the Beta density. Regarding the latter case we should note that the Beta density is among the most popular priors for the problem we are considering in this work.

**Conjecture.** For any prior $\pi (\theta )$   and sufficiently large horizon N the optimum stopping time $T_{\mathrm {o}}$  of the unconstrained problem in (4) enjoys the following two properties:

i). There exists constant $t_{\mathrm {up}}$ depending only on c and not on N such that $T_{\mathrm {o}}\leq t_{\mathrm {up}}.$ 

ii). For sufficiently small c there exists constant $t_{\mathrm {lo}}\geq 1$ depending only on c and not on N such that $t_{\mathrm {lo}}\leq T_{\mathrm {o}}.$ 

Below we present a general proof of property i) of the Conjecture under the following additional assumption: Define the maximal conditional variance

$$σ_{t}^{2}=\max _{0\leq S_{t}\leq t}\mathrm {E}\left[\left(\theta -\mathrm {E}\left[\theta |S_{t}\right]\right)^{2}|S_{t}\right]=\max _{0\leq S_{t}\leq t}\int _{0}^{1}\left(\theta -\mathrm {E}\left[\theta |S_{t}\right]\right)^{2}\pi _{t}\left(\theta |S_{t}\right)d\theta ,\tag{19}$$

where $\pi _{t}\left(\theta |S_{t}\right)$ is the posterior pdf defined in (6) and assume that $σ_{t}\rightarrow 0$ as $t\rightarrow \infty$ . This forces the conditional variance to converge to 0 uniformly in $S_{t}$ . It also implies that the posterior distribution $\pi _{t}\left(\theta |S_{t}\right)$  converges, uniformly, to a degenerate measure at a single point (often the true $\theta$ ) as $t\rightarrow \infty$ This is clearly related to the consistency concept of posterior distributions in Bayesian statistics and is often considered a valid assumption (see [24]).

### Lemma 3. Let $σ_{t}$ be defined as in (19) with $\lim _{t\rightarrow \infty }σ_{t}=0$ .Then for sufficiently large horizon there exists constant $t_{\mathrm {up}}$ depending only on c such that $T_{\mathrm {o}}\leq t_{\mathrm {up}},$ i.e. property i) in the Conjecture is true.

Proof. The proof is a simple application of the Chebyshev inequality in combination with (19). Indeed we observe that

$$\mathscr{C}_{t}\left(S_{t}\right)=\inf _{\hat{\theta}_{t}}\mathrm{P}\left(\left|\theta-\hat{\theta}_{t}\right|>h\mid \mathscr{F}_{t}\right)\leq \mathrm{P}\left(\left|\theta-\mathrm{E}\left[\theta \mid \mathscr{F}_{t}\right]\right|>h\mid \mathscr{F}_{t}\right)\leq \frac{1}{h^{2}}\mathrm{E}\left[\left(\theta-\mathrm{E}\left[\theta \mid S_{t}\right]\right)^{2}\mid S_{t}\right]\leq \frac{\sigma_{t}^{2}}{h^{2}}\tag{20}$$

Since $σ_{t}\rightarrow 0$ as $t\rightarrow \infty$ ,there existsN such that $\mathscr {C}_{N}\leq \frac {σ_{N}^{2}}{h^{2}}\leq c$ and,therefore, from (14) we conclude that $\mathscr {C}_{N}\leq c+\tilde {\mathscr {V}}_{N}$ , which suggests that we will necessarily stopat N for any value of $S_{N}$ .Quantity $t_{\mathrm {up}}$ is the smallest N for which this is true. ☐

**Remark** 3. The assumption lim $t\rightarrow \infty σ_{t}=0$ does not hold for all prior distribution. A counterexample where it fails is when the prior is a two-point probability mass function, say $\mathrm {P}(\theta =0.4)=\mathrm {P}(\theta =0.6)=$ 0.5. However, even for this case the Conjecture might still be valid since the requirement $\mathscr {C}_{N}\left(S_{N}\right)\leq$ $\frac {σ_{N}^{2}}{h^{2}}<c$ used in our proof, is only sufficient for the validity of our claim.

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 10 -->

An interesting example where the assumption holds is when1 the prior is the Beta density $\pi (\theta )=$ $\text {Beta}(\theta ,p,q)$ ,where

$\text {Beta}(\theta ,p,q)=\frac {\theta ^{p-1}(1-\theta )^{q-1}}{\int _{0}^{1}\theta ^{p-1}(1-\theta )^{q-1}d\theta }$ $p,q>0$  (21)

To see this, we note that the posterior pdf is of the same type, namely $\pi \left(\theta |S_{}\right)=\text {Ba}\left(\theta p+S_{}-S_{}+q\right)$ and thus the maximal conditional variance in (19) becomes

$$σ_{t}^{2}=\max _{0\leq S_{t}\leq t}\frac {\left(p+S_{t}\right)\left(t-S_{t}+q\right)}{(t+p+q)^{2}(t+p+q+1)}\leq \frac {1}{4(t+p+q+1)},\tag{22}$$

where the equality is attainable when $S_{t}=\frac {t+q-p}{2}$ is an integer. Clearly, for fixed $p,q>0$ we have $σ_{t}\rightarrow 0$ $\text {as}t\rightarrow \infty$ ,and thus the assumption of Lemma 3 holds. Moreover, by the proof of Lemma 3, the optimum stopping time satisfies $T_{\mathrm {o}}\leq \max \left\{0,\frac {1}{4h^{2}c}-p-q-1\right\}$ for all $c>0$ . This bound is of the order of $c^{-1}$ . In Theorem 2, Section III-B, by applying a more advanced analysis, we will be able to improve it and provide an alternative estimate which is of the order of $|\log (c)|$ for the case of the symmetric prior $p=q.$ 

**Remark** 4. Property i) of the Conjecture suggests that the number of samples, under the optimum scheme, will never exceed the value $t_{\mathrm {up}}$ even if we allow the horizon to grow without limit. This interesting and uncommon characteristic was also observed in [21] but with cost function a variance of the classical mean square error. However, what is more intriguing in our conjecture is property ii), namely that we need first to accumulate a sufficient volume of information before we start asking ourselves whether we should stop sampling or not. This is an extremely uncommon feature and, to our knowledge, has never been reported before in Sequential Analysis as a property of optimum schemes. As we claim in our conjecture, we believe that both properties are valid for any prior $\pi (\theta )$ . Fortunately, as we mentioned before, this double claim is not without solid evidence. Indeed with Theorem 2, we demonstrate its validity when the prior is the symmetric Beta density.

### A. Performance Evaluation

What we presented so far allows for the determination of the stopping rule of the proposed scheme. We wouldI like now to compute its performance but also the performance of any stopping time which uses $S_{t}$ as its test statistic and is defined in terms of a sequence of sampling regions $\left\{Ω_{t}\right\}$ in terms of $\left\{S_{t}\right\}$ .In particular, we are interested in computing $\mathrm {E}[T|\theta ]$ $\mathrm {E}[T],\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|\leq h|\theta \right)$ and $\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|\leq h\right)$ Of course, we could obtain these quantities using Monte-Carlo simulations, but it is also possible to determine them numerically. The following lemma provides the necessary formulas.

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 11 -->

**Lemma** 4. Let the stopping time T be bounded by N having as test statistic the process $\left\{S_{t}\right\}$ .Assume for each t that $Ω_{}$ denotes the sampling region. Suppose also that for the combination(t, $\left.S_{t}\right)$  the scheme provides the mid-point estimate $\hat {\theta }_{t}\left(S_{t}\right)$ and the corresponding conditional complementary coverage probability $C_{t}\left(S_{t}\right)=\mathrm {P}\left(\left|\hat {\theta }_{t}\left(S_{t}\right)-\theta \right|>h|\mathscr {F}_{t}\right)$ $For$ $t=N-1,\cdots ,0,$ we then define the following backward recursions that must be applied for $S_{t}=0,1,\cdots ,t$ 

$$U_{t}\left(S_{t}\right)=1+\theta \mathbb {1}_{\left\{S_{t}+1\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t}+1\right)+(1-\theta )\mathbb {1}_{\left\{S_{t}\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t}\right)\tag{23}$$

$$\bar {U}_{t}\left(S_{t}\right)=1+g_{t+1}\left(S_{t}\right)\mathbb {1}_{\left\{S_{t}+1\in Ω_{t+1}\right\}}\bar {U}_{t+1}\left(S_{t}+1\right)+\left(1-g_{t+1}\left(S_{t}\right)\right)\mathbb {1}_{\left\{S_{t}\in Ω_{t+1}\right\}}\bar {U}_{t+1}\left(S_{t}\right)\tag{24}$$

$$W_{t}\left(S_{t}\right)=\mathbb {1}_{\left\{\left|\hat {\theta }_{t}-\theta \right|>h\right\}}\mathbb {1}_{\left\{S_{t}\notin Ω_{t}\right\}}+\left\{\theta W_{t+1}\left(S_{t}+1\right)+(1-\theta )W_{t+1}\left(S_{t}\right)\right\}\mathbb {1}_{\left\{S_{t}\in Ω_{t}\right\}}\tag{25}$$

$$\bar {W}_{t}\left(S_{t}\right)=C_{t}\left(S_{t}\right)\mathbb {1}_{\left\{S_{t}\notin Ω_{t}\right\}}+\left\{g_{t+1}\left(S_{t}\right)\bar {W}_{t+1}\left(S_{t}+1\right)+\left(1-g_{t+1}\left(S_{t}\right)\right)\bar {W}_{t+1}\left(S_{t}\right)\right\}\mathbb {1}_{\left\{S_{t}\in Ω_{t}\right\}}\tag{26}$$

where $g_{t+1}\left(S_{t}\right)$ is defined in (16) and the four recursions are initialized with $U_{N}\left(S_{N}\right)=\bar {U}_{N}\left(S_{N}\right)=$ 0, $W_{N}\left(S_{N}\right)=\mathbb {1}_{\left\{\left|\hat {\theta }_{N}-\theta \right|>h\right\}}$ $,\bar {W}_{N}\left(S_{N}\right)=C_{N}\left(S_{N}\right),$ $,Ω_{N}=\varnothing$ .Then, $\mathrm {E}[T|\theta ]=U_{0}\left(S_{0}\right)$ $,\mathrm {E}[T]=\bar {U}_{0}\left(S_{0}\right)$ $,\mathrm {P}\left(|\hat {\theta }_{T}-\right.$ $\left.\theta |>h|\theta \right)=W_{0}\left(S_{0}\right)$ and $\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h\right)=\bar {W}_{0}\left(S_{0}\right).$ 

Proof. The validity of these expressions is established in the Appendix.

☐

The applicability of Lemma 4 is clearly not limited to the proposed scheme but can be used to compute the performance of the fixed-sample-size and of other sequential alternatives that we intend to compare against the method we have developed.

### B. Beta Density as Prior

Let us now find the particular form of our scheme when we adopt as our prior the Beta density $\pi (\theta )=\text {Beta}(\theta ,a,a)$ ,where $Beta(\theta ,p,q)$ is defined in (21). We observe that the selection $a=1$ in the prior corresponds to the uniform density in $[0,1]$ . It is now straightforward to verify that the posterior pdf accepts a similar form,namely

$$\pi \left(\theta |S_{t}\right)=\text {Beta}\left(\theta ,a+S_{t},a+t-S_{t}\right)\tag{27}$$

while the conditional complementary coverage **probability** **at** time t becomes

$$\mathrm{P}\left(\left|\hat{\theta}_{t}-\theta\right|>h\mid \mathscr{F}_{t}\right)=1-I_{\min \left\{1,\hat{\theta}_{t}+h\right\}}\left(a+S_{t},a+t-S_{t}\right)+I_{\max \left(0,\hat{\theta}_{t}-h\right)}\left(a+S_{t},a+t-S_{t}\right)\tag{28}$$

where $I_{x}(p,q)$  is the incomplete Beta function (see [25, Page 944]) which is the cdf of $\text {Beta}(\theta ,p,q)$ 

The Bayes estimator, according to (18), can be found as the solution of the equation

$$\hat {\theta }_{t}=\arg \left\{\hat {\theta }_{t}:\left(\frac {\hat {\theta }_{t}-h}{\hat {\theta }_{t}+h}\right)^{a+S_{t}-1}=\left(\frac {1-h-\hat {\theta }_{t}}{1+h-\hat {\theta }_{t}}\right)^{a+t-S_{t}-1}\right\}$$

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 12 -->

corresponding to the root in the interval $[h,1-h]$ . Such root always exists except when $a=1$ and $S_{t}=0$ or t. For these cases, $\hat {vartheta}_{t}$ is equal to $h$  or $1-h,$ ,depending on which value provides a larger conditional coverage probability. The resulting optimum conditional complementary coverage probability becomes

$$\mathscr {C}_{t}\left(S_{t}\right)=1-I_{\min \left\{1,\hat {vartheta}_{t}+h\right\}}\left(a+S_{t},a+t-S_{t}\right)+I_{\max \left(0,\hat {vartheta}_{t}-h\right)}\left(a+S_{t},a+t-S_{t}\right)\tag{29}$$

Finally, as indicated in (15) and (16), we need to find the probability $g_{t+1}\left(S_{t}\right)$ ,for which we have the following simple formula

$$g_{t+1}\left(S_{t}\right)=\mathrm {P}\left(X_{t+1}=1|\mathscr {F}_{t}\right)=\frac {Γ\left(S_{t}+a+1\right)Γ(t+2a)}{Γ\left(S_{t}+a\right)Γ(t+2a+1)}=\frac {S_{t}+a}{t+2a}\tag{30}$$

We can now compute the sequences $\left\{\left\{\mathscr {V}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N},\left\{\left\{\tilde {\mathscr {V}}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ as explained in (14) and compare, element-by-element, $\left\{\left\{\mathscr {C}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ with $\left\{\left\{\mathscr {V}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ or $\left\{\left\{\mathscr {C}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$  with $\left\{\left\{c+\tilde {\mathscr {V}}_{t}\left(S_{t}\right)\right\}_{S_{t}=0}^{t}\right\}_{t=0}^{N}$ to identify the sampling and stopping regions.

For the particular prior adopted in (21), as we mentioned before, the resulting optimum stopping time $T_{\mathrm {o}}$ enjoys the unique properties claimed in the Conjecture. The next theorem provides the necessary evidence.

**Theorem** 2. The Conjecture is true when the prior is the Beta density $\pi (\theta )=\text {Beta}(\theta ,a,a)$ with the optimum stopping time $T_{\mathrm {o}}$ satisfying $C_{0}|\log (c)|\leq T_{\mathrm {o}}\leq C_{1}|\log (c)|$ for constants $C_{0}<C_{1}$ that depend only on a and $h$ .

Proof. The proof is very technical and detailed in the Appendix. Unfortunately,the analytical techniques developed for the specific prior are not directly extendable to the general case. ☐

Perhaps, it is worth mentioning the fact that from the proof of Theorem 2, we conclude that the two estimates for $t_{\mathrm {up}}$ and $t_{\mathrm {lo}}$ in (43),(45) grow linearly in $|\log (c)|$ having drastically different multiplicative coefficients $\left(C_{0}\right.$ of the order of $\frac {1}{2h^{2}}$ versus $C_{1}$ of the order of $\left.\frac {1}{|\log (0.5-h)|}\right)$ and different offsets.

As an illustration for these properties we consider $a=1,h=0.05,$ ,and $c=0.0001$ . Fig.1 depicts the sampling (green) and the stopping (red) region in terms of the test statistic $S_{t}$ .Both regions are clearly limited between the lines $S_{t}=t$ and $S_{t}=0$ . Even though we have marked a whole region in red,only the points that are next to the green region are actually accessible because $S_{t}$ can increase at most by one unit as we go from t to $t+1.$ .We can also see the two bounds $t_{\mathrm {up}}=561$ and $t_{\mathrm {lo}}=59$ for $T_{\mathrm {o}}$ For $t\leq t_{\mathrm {lo}}$ the light green region covers all points $0\leq S_{t}\leq t$ ,thus identifying the time instances we can never stop. Also, we note that once we pass $t_{\mathrm {up}}$ we are in the stopping region suggesting that we must necessarily stop at $t_{\mathrm {up}}$ .For each $t_{\mathrm {lo}}\leq t\leq t_{\mathrm {up}}$ the stopping region has an upper $r_{t}^{u}$ and a lower $r_{t}^{l}$ threshold and, as long as $S_{t}$ is between these two limits, we need to sample. Since the prior distribution

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 13 -->

<!-- 09 00E 09a S=t 5 002 OSt 100 00 。 0 $t_{v}$ 100 200 300 t 400 500 $x_{8}$ -->
![](https://web-api.textin.com/ocr_image/external/74f59ab0208ad3d0.jpg)

Fig. 1. Sampling (green) and stopping (red) regions for $a=1,h=0.05$ and $c=0.0001$ . Upper and lower bounds for optimum stopping time: $t_{\mathrm {lo}}=59$ and $t_{\mathrm {up}}=561$ .No possibility of stopping (light green).

is symmetric with respect to $1/2$ ,then, according to Theorem 1, the sampling region is symmetric around $t/2$ ,implying that $r_{t}^{u}+r_{t}^{l}=t$ 

In Fig.2, after using (24), we plot the average sample size and the two limits $t_{\mathrm {lo}},t_{\mathrm {up}}$ of $T_{\mathrm {o}}$ as functions of $C$  for $a=1$  and $h=0.05.$ .We can see that the lower limit $t_{\mathrm {lo}}$ is significantly smaller than the resulting average, suggesting that the optimum scheme very quicklyregards the accumulated information as capable of providing reliable interval estimates and therefore starts the process of questioning whether to stop or continue sampling.

<!-- 1000 900 $\begin{array}{l}\text {E}\left[T_{\circ }\right]\\ -t_{10}\\ -t_{\mathrm {up}}\end{array}$ 800 700 600 500 400 300 200 100 0 0.5 1 1.5 2 $2.5$ $x10^{-3}$ 3 C -->
![](https://web-api.textin.com/ocr_image/external/ec2ce13648981d37.jpg)

Fig. 2. Average sample size (red), lower $t_{10}$ o (blue) and upper $t_{\mathrm {up}}$  limit (green), as functions of $C$ c for optimum stopping time $T_{\mathrm {o}}$ when $a=1$ and $h=0.05.$ 

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 14 -->

## IV. COMPARISONS

Let us now compare our scheme with the optimal fixed-sample-size (FSS) and two sequential methods: The first was proposed by Frey in [20] and the second, the Conditional Method, was proposed in our earlier work in [26]. Frey's method uses a modified Wald-type sequential confidence interval based on the stopping time

$$T_{\mathrm {F}}=\inf \left\{t\geq 0:\frac {\tilde {\theta }_{t,k}\left(1-\tilde {\theta }_{t,k}\right)}{t}\leq \left(\frac {h}{z_{\frac {γ}{2}}}\right)^{2}\right\}\tag{31}$$

where $\tilde {\theta }_{t,k}=\frac {S_{t}+k}{t+2k}$  $k>0$ is a pre-specified constant and $γ=γ(k,h,α)$ is chosen so that the confidence interval $\left[\hat {\theta }_{T_{\mathrm {F}}}-h,\hat {\theta }_{T_{\mathrm {F}}}+h\right]$ ,with $\hat {\theta }_{t}=\frac {S_{t}}{t}$ ,has a confidence level of at least $1-α.$ .Table I provides the values of $k$  and $γ$  recommended in [20] for best results. From (31) and using the fact that $x(1-x)\leq \frac {1}{4}$ 

**TABLE I**

CHOICES OF $k$  AND $γ$  FOR 90%, 95%, AND 99% CONFIDENCE INTERVALS OF FIXED HALF-WIDTH $h$  IN [20].

<table border="1" ><tr>
<td></td>
<td>90%</td>
<td>95%</td>
<td>99%</td>
</tr></table>

<table border="1" ><tr>
<td></td>
<td colspan="2"></td>
<td colspan="2"></td>
<td colspan="2"></td>
</tr><tr>
<td>$h$</td>
<td>$k$</td>
<td>$γ$</td>
<td>$k$</td>
<td>$γ$</td>
<td>$k$</td>
<td>$γ$</td>
</tr><tr>
<td>0.10</td>
<td>4</td>
<td>0.0754</td>
<td>4</td>
<td>0.0356</td>
<td>6</td>
<td>0.0068</td>
</tr><tr>
<td>0.05</td>
<td>4</td>
<td>0.0859</td>
<td>6</td>
<td>0.0433</td>
<td>8</td>
<td>0.0083</td>
</tr><tr>
<td>0.01</td>
<td>8</td>
<td>0.0972</td>
<td>10</td>
<td>0.0487</td>
<td>14</td>
<td>0.0097</td>
</tr></table>

we conclude that the corresponding stopping time satisfies $T_{\mathrm {F}}\leq \left\lceil \frac {z_{\frac {γ}{2}}^{2}}{4h^{2}}\right\rceil =N$ . Regarding the finite-sample-size method, it uses the optimnum Bayes estimator $\hat {vartheta}_{t}$ , obtained in (7) and the number of samples $t$  is selected to meet the desired coverage probability. Finally, for the conditional method in [26],we should point out that it is a general sequential parameter estimation technique based on conditional costs which is not limited to binomial proportions. For the problem of interest, we have $T_{\mathrm {C}}=\inf \{t\geq$ $\left.0:\mathscr {C}_{t}\leq \beta \right\}$  and $\hat {\theta }_{T_{\mathrm {C}}}=\hat {vartheta}_{T_{\mathrm {C}}}$ ,where $\hat {vartheta}_{t}$ $\mathscr {C}_{t}$ are the Bayes estimator and the corresponding optimum conditional complementary coverage probability defined in (7),(8). Threshold $\beta$  is selected to guarantee that the resulting coverage probability is $1-α$ .For $\mathscr {C}_{t}$ we have from the proof of Theorem 1,eq.(32), that $\mathscr {C}_{t}\leq 2e^{-2h^{2}(t+2a+1)}$ ,consequently $T_{\mathrm {C}}\leq \left\lceil \max \left\{\frac {\left|\log \left(\frac {\beta }{2}\right)\right|}{2h^{2}}-2a-1,0\right\}\right\rceil =N.$  In other words, all four schemes satisfy the assumption of Lemma4 of bounded stopping time, therefore the corresponding performance can be compuited numerically by applying the recursions of the lemma without the need to perform Monte-Carlo simulations.

For the competing methods using (24),(26), we plot in Fig.3 the average number of samples $E[T]$ versus the coverage probability $\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|\leq h\right)$  when $a=1$ and $h=0.05.$ .Note that we have three

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 15 -->

<!-- Proposed 600 FSS Conditional Frey 500 Average Number of Samples 400 300 200 100 0.8 0.82 0.84 0.86 0.88 0.9 0.92 0.94 0.96 0.98 1 Coverage Probability -->
![](https://web-api.textin.com/ocr_image/external/f38cdc7a1c15367d.jpg)

Fig. 3. Average samnples size versus coverage probability for proposed (red),Frey (black +), fixed-sample-size (blue) and conditional (green),for $a=1$ and $h=0.05.$ 

points for Frey's scheme because of the tuning parameters $k$  and $γ$  which are provided in Table I only for three confidence levels. As we can see, the proposed method outperforms the fixed-sample-size and both alternative sequential techniques. It is only at very high coverage probability levels that the difference between the three sequential schemes becomes less pronounced.

As we pointed out in (3), Section II, there is practical interest in evaluating the performance for each individlual $\theta$ . Clearly in this case, the requirement is to be able to guarantee a minimal coverage probability for all $\theta$ . Again, we resort to Lemma4 and use (23),(25) to evaluate the performance of the competing methods for each $\theta$ . In Fig. 4a, we plot the coverage probability for each test versus $\theta$  and in Fig.4b, the corresponding average sample size required to obtain this performance. Parameters were selected so as all competing schemes provide the same worst-case coverage probability assuring a coverage of at least 0.95 for all $\theta$ . By observing the two figures, we can dIraw the following conclusions: The fixed-sample-size scheme can require up to almost eight times more samples compared to the proposed. Of course, one may argue that it produces higher coverage probability levels. Indeed this is true, but, unfortunately, this increased performance cannot be traded for a reduced sample size without compromising the worst-case level. Consequently, what we observe is in fact the best the fixed-sample-size method can offer. The conditional scheme, around $\theta =0.5,$ ,requires up to 30% more samples which, as in the case of fixed-sample-size, produce higher coverage probabilities. Again, it is impossible to sacrifice part of this increased performance to improve the corresponding sample size without degrading the worst-case coverage probability. Finally, we can see that the proposed and Frey's scheme require similar samples

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 16 -->

<!-- Proposed 1 FSS Conditional Frey 0.99 0.98 Coverage Probability 0.97 0.96 0.95 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 0 -->
![](https://web-api.textin.com/ocr_image/external/cfada680c3785a98.jpg)

(a)

<!-- 550 Proposed 500 FSS Conditional Frey 450 400 350 Average Number of Samples 300 250 200 150 100 50 0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 0 -->
![](https://web-api.textin.com/ocr_image/external/2faac1db11cd4a33.jpg)

(b)

Fig. 4. Coverage probability (a) and Average sample size (b) as a function of proportion $\theta$  for proposed (red),Frey(black), fixed-sample-size (blue) and conditional (green) when $a=1,$ $h=0.05$ and worst-case coverage probability 0.95.

over most $\theta$ . However, we observe that the proposed method has a coverage probability profile which is better than Frey's, since for most $\theta$  the corresponding probability is larger. Frey's scheme is slightly better only for $\theta$  close to 0 and 1. But even for these values of $\theta$  the proposed scheme requires almost 50% less samples.

## V. CONCLUSIONS

We proposed an optimal sequential scheme for obtaining confidence intervals for a binomial proportion under a well defined formulation. We proved that, for a particular prior (Beta density), our optimum stopping time enjoys certain uncommon properties not encountered in solutions of other classical optimal stopping problems. We also conjectured that these properties are present with any prior. Specifically, our claim is that our stopping time is always bounded from above and below, suggesting that we need to first accumulate a sufficient amount of information before we start applying our stopping rule, and that our stopping time will always terminate at a specific deterministic time even if we allow the time horizon to be infinite. Finally, our scheme was compared against the optimum fixed-sample-size procedure and against existing sequential alternatives. Numerical performance evaluations showed that the proposed method exhibits an overall improved performance profile compared to its rivals.

## VI. ACKNOWLEDGMENTS

This work was supported by the US National Science Foundation under Grant CIF 1513373 through Rutgers University and under Grant CMMI 1362876 through Georgia Institute of Technology.

<!-- DRAFT -->

<!-- November 21, 2017 -->

<!-- 17 -->

**APPENDIX**

Proof of Lemma 1: From (10) we can write

$$J\left(T,\hat {\theta }_{T}\right)=c\mathrm {E}[T]+\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h\right)=\sum _{t=0}^{N}\mathrm {E}\left[\left\{ct+\mathbb {1}_{\left\{|\hat {\theta }_{t}-\theta |>h\right\}}\right\}\mathbb {1}_{\{T=t\}}\right]$$

$$=\sum _{t=0}^{N}\mathrm {E}\left[\mathrm {E}\left[ct+\mathbb {1}_{\left\{|\hat {\theta }_{t}-\theta |>h\right\}}|\mathscr {F}_{t}\right]\mathbb {1}_{\{T=t\}}\right]=\sum _{t=0}^{N}\mathrm {E}\left[\left\{ct+\mathrm {P}\left(|\hat {\theta }_{t}-\theta |>h|\mathscr {F}_{t}\right)\right\}\mathbb {1}_{\{T=t\}}\right]\tag{32}$$

$$\geq \sum _{t=0}^{N}\mathrm {E}\left[\left\{ct+\inf _{\hat {\theta }_{t}}\mathrm {P}\left(\left|\hat {\theta }_{t}-\theta \right|>h|\mathscr {F}_{t}\right)\right\}\mathbb {1}_{\{T=t\}}\right]=\sum _{t=0}^{N}\mathrm {E}\left[\left\{ct+\mathscr {C}_{t}\right\}\mathbb {1}_{\{T=t\}}\right]\tag{33}$$

$$=\mathrm {E}\left[cT+\mathscr {C}_{T}\right].$$

The first equality in (32) is true because $\mathbb {1}_{\{T=t\}}$ is $\mathscr {F}_{t}$ measurable,also we have equality in (33) if we select $\hat {\theta }_{t}=\hat {vartheta}_{t}$ when $\{T=t\}$ . We observe that changing the order of summation and expectation presents absolutely no complication because the stopping time is bounded by the deterministic quantity N. ☐

Proof of Theorem 1: $\text {I}α\geq \mathrm {P}\left(\left|\hat {vartheta}_{0}-\theta \right|>h\right)$ then stopping at $T_{\mathrm {o}}=0$ corresponds to the smallest possible (average) number of samples while, at the same time,we satisfy the coverage probability constraint.

To prove ii) we first show that there exists $N_{α}$ such that $\mathrm {P}\left(\left|\hat {vartheta}_{N_{α}}-\theta \right|>h\right)<α$ .Note that

$$\mathrm {P}\left(\left|\hat {\theta }_{t}-\theta \right|>h\right)\leq \mathrm {P}\left(\left|\frac {S_{t}}{t}-\theta \right|>h\right)\leq \frac {1}{h^{2}}\mathrm {E}\left[\left(\frac {S_{t}}{t}-\theta \right)^{2}\right]\quad =\frac {1}{h^{2}}\mathrm {E}\left[\mathrm {E}\left[\left(\frac {S_{t}}{t}-\theta \right)^{2}|\theta \right]\right]=\frac {1}{h^{2}}\mathrm {E}\left[\frac {\theta (1-\theta )}{t}\right]\leq \frac {1}{4h^{2}t}\tag{34}$$

where we used the fact that $\frac {S_{t}}{t}$ is not the optimum Bayes estimator of the mid-point, then we applied the Chebyshev's inequality, then the fact that $\frac {S_{t}}{t}$ is an estimator of $\theta$  with estimation error variance equal to $\frac {\theta (1-\theta )}{t}$ and finally that $\theta (1-\theta )\leq \frac {1}{4}$ .From (34) we conclude that $\mathrm {P}\left(\left|\hat {vartheta}_{t}-\theta \right|>h\right)\rightarrow 0$ as $t\rightarrow \infty$ therefore,there exists $N_{α}$ such that $\mathrm {P}\left(\left|\hat {vartheta}_{N_{α}}-\theta \right|>h\right)<α.$ 

Fix $N\geq N_{α}$ and denote $\mathscr {V}_{t}\left(S_{t},c\right)=\inf _{t\leq T\leq N}$ $\mathrm {E}\left[c(T-t)+\mathscr {C}_{T}|\mathscr {F}_{t}\right]$ ,where we underline the dependence of $\mathscr {V}_{t}$ on c (in addition to $\left.S_{t}\right)$ .For $0\leq c_{1}\leq c_{2}$ and $T\geq t$ we can write

$$c_{1}(T-t)+\mathscr {C}_{T}\leq c_{2}(T-t)+\mathscr {C}_{T}$$

which, after taking expectation conditioned on $\mathscr {F}_{t}$  and then infimum over $t\leq T\leq N$ ,proves that $\mathscr {V}_{t}\left(S_{t},c\right)$ is increasing in c. The increase of $\mathscr {V}_{t}\left(S_{t},c\right)$ with respect to c also suggests that the optimum stopping time $T_{\mathrm {o}}(c)$ , defined in (17), is a decreasing function of $C$ .

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 18 -->

Consider now the sequence of optimum complementary coverage probabilities $\left\{\mathscr {C}_{t}\right\}$ ,we observe

$$\mathscr {C}_{t}=\inf _{\hat {\theta }}\mathrm {P}\left(|\hat {\theta }-\theta |>h|\mathscr {F}_{t}\right)=\inf _{\hat {\theta }}\mathrm {E}\left[\mathrm {P}\left(|\hat {\theta }-\theta |>h|\mathscr {F}_{t+1}\right)|\mathscr {F}_{t}\right]$$

$$\geq \mathrm {E}\left[\inf _{\hat {\theta }}\mathrm {P}\left(|\hat {\theta }-\theta |>h|\mathscr {F}_{t+1}\right)|\mathscr {F}_{t}\right]=\mathrm {E}\left[\mathscr {C}_{t+1}|\mathscr {F}_{t}\right]\tag{35}$$

We can then write

$$\mathrm {P}\left(\left|\hat {vartheta}_{T_{\mathrm {o}}(c)}-\theta \right|>h\right)=\mathrm {E}\left[\mathscr {C}_{T_{\mathrm {o}}(c)}\right]=\mathscr {C}_{0}-\mathrm {E}\left[\sum _{t=0}^{T_{\mathrm {o}}(c)-1}\left\{\mathscr {C}_{t}-\mathscr {C}_{t+1}\right\}\right]\quad =\mathscr {C}_{0}-\mathrm {E}\left[\sum _{t=0}^{N}\left\{\mathscr {C}_{t}-\mathscr {C}_{t+1}\right\}\mathbb {1}_{\left\{T_{\circ }(c)>t\right\}}\right]=\mathscr {C}_{0}-\mathrm {E}\left[\sum _{t=0}^{N}\left\{\mathscr {C}_{t}-\mathrm {E}\left[\mathscr {C}_{t+1}|\mathscr {F}_{t}\right]\right\}\mathbb {1}_{\left\{T_{\circ }(c)>t\right\}}\right]\tag{36}$$

where for the last equality we used the fact that $\mathbb {1}_{\left\{T_{\mathrm {o}}(c)>t\right\}}$ is $\mathscr {F}_{t}$ measurable. This combined with (35) and the decrease of $T_{\mathrm {o}}(c)$ with respect to c, implies that $\mathrm {P}\left(\left|\hat {vartheta}_{T_{\mathrm {o}}(c)}-\theta \right|>h\right)$ is increasing in c.

For $c=1$ we stop at 0 and, therefore, $\mathrm {P}\left(\left|\hat {vartheta}_{T_{o}(1)}-\theta \right|>h\right)=\mathrm {P}\left(\left|\hat {vartheta}_{0}-\theta \right|>h\right)>α$ .Set now $c=0$ which suggests that the cost of sampling is zero and therefore the optimum is to stop at N (we also deduce this by combining (17) and (35)). This yields $\mathrm {P}\left(\left|\hat {vartheta}_{T_{\mathrm {o}}(0)}-\theta \right|>h\right)=\mathrm {P}\left(\left|\hat {vartheta}_{N}-\theta \right|>h\right)=\mathrm {E}\left[\mathscr {C}_{N}\right]$ .Now from (35) by averaging we conclude that $\mathrm {E}\left[\mathscr {C}_{t}\right]$ is decreasing in t and for $N>N_{α}$ we have $\mathrm {E}\left[\mathscr {C}_{N}\right]\leq \mathrm {E}\left[\mathscr {C}_{N_{α}}\right]<α,$ implying $\mathrm {P}\left(\left|\hat {vartheta}_{T_{o}(0)}-\theta \right|>h\right)<α.$ .As mentioned, $\mathrm {P}\left(\left|\hat {vartheta}_{T_{\mathrm {o}}(c)}-\theta \right|>h\right)$ is increasing in c, if it is also continuous then there exists $0<c_{*}<1$ satisfying $\mathrm {P}\left(\left|\hat {vartheta}_{T_{\mathrm {o}}\left(c_{*}\right)}-\theta \right|>h\right)=α$ which means that $T_{\mathrm {o}}\left(c_{*}\right)$ solves the constrained problem. In case the function $\mathrm {P}\left(\left|\hat {vartheta}_{T_{\mathrm {o}}(c)}-\theta \right|>h\right)$  exhibits a jump at $c_{*}$  such that for $c_{*}-$  the probability is strictly smaller than $α$  while for $c_{*}+\mathrm {it}$ is strictly larger, then before taking any samples we need to perform a randomization to decide which of the two stopping times $T_{\mathrm {o}}\left(c_{*}-\right),T_{\mathrm {o}}\left(c_{*}+\right)$ to use. The randomization probability must be selected so that we satisfy the constraint with equality. ☐

Proof of Lemma 4: We prove (23) first. Set $Ω_{N}=\varnothing$ ,i.e. we stop necessarily at N. Then we note that

$$T=\sum _{t=0}^{N-1}\mathbb {1}_{\{T>t\}}=\left(1+\cdots \left(1+\mathbb {1}_{\left\{S_{N-1}\in Ω_{N-2}\right\}}\left(1+\mathbb {1}_{\left\{S_{N-1}\in Ω_{N-1}\right\}}\left(1+\mathbb {1}_{\left\{S_{N}\in Ω_{N}\right\}}\right)\right)\right)\cdots \right)$$

suggesting that

$$\mathrm{E}[T\mid \theta]=\mathrm{E}\left[\left(1+\cdots \mathrm{E}\left[\left(1+\mathbb{1}_{\left\{S_{N-1}\in \Omega_{N-1}\right\}}\mathrm{E}\left[\left(1+\mathbb{1}_{\left\{S_{N}\in \Omega_{N}\right\}}\right)\mid \mathscr{F}_{N-1},\theta\right)\mid \mathscr{F}_{N-2},\theta\right]\cdots\right)\mid \theta\right]\right.$$

If we set $U_{N}\left(S_{N}\right)=0$ then we can define the backward recursion

$$U_{t}\left(S_{t}\right)=\mathrm {E}\left[1+\mathbb {1}_{\left\{S_{t+1}\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t+1}\right)|\mathscr {F}_{t}\right]=1+\mathrm {E}\left[\mathbb {1}_{\left\{S_{t+1}\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t+1}\right)|\mathscr {F}_{t}\right]$$

$$=1+\mathrm {P}\left(X_{t+1}=1|S_{t},\theta \right)\mathbb {1}_{\left\{S_{t}+1\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t}+1\right)+\mathrm {P}\left(X_{t+1}=0|S_{t},\theta \right)\mathbb {1}_{\left\{S_{t}\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t}\right)$$

$$=1+\theta \mathbb {1}_{\left\{S_{t}+1\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t}+1\right)+(1-\theta )\mathbb {1}_{\left\{S_{t}\in Ω_{t+1}\right\}}U_{t+1}\left(S_{t}\right)$$

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 19 -->

which proves (23) and, also,that $U_{0}\left(S_{0}\right)=\mathrm {E}[T|\theta ]$ . For (24) we proceed similarly the only difference being that $\mathrm {P}\left(X_{t+1}=1|S_{t}\right)=g_{t+1}\left(S_{t}\right)$ with this probability being dlefined in (16).

For (25) and (26) we follow **similar** steps. We **have**

$$\mathbb {1}_{\left\{\left|\hat {\theta }_{T}-\theta \right|>h\right\}}=\sum _{t=0}^{N}\mathbb {1}_{\left\{\left|\hat {\theta }_{t}-\theta \right|>h\right\}}\mathbb {1}_{\{T=t\}}=\sum _{t=0}^{N}\mathbb {1}_{\left\{\left|\hat {\theta }_{t}-\theta \right|>h\right\}}\mathbb {1}_{\left\{S_{t}\notin Ω_{t}\right\}}\prod _{j=0}^{t-1}\mathbb {1}_{\left\{S_{j}\in Ω_{j}\right\}}\quad =\left(\mathbb {1}_{\left\{\left|\hat {\theta }_{0}-\theta \right|>h\right\}}\mathbb {1}_{\left\{S_{0}\notin Ω_{0}\right\}}\right)+\left(\mathbb {1}_{\left\{\left|\hat {\theta }_{1}-\theta \right|>h\right\}}\mathbb {1}_{\left\{S_{1}\notin Ω_{1}\right\}}\right)\mathbb {1}_{\left\{S_{0}\in Ω_{0}\right\}}+\cdots +\left(\mathbb {1}_{\left\{\left|\hat {\theta }_{N}-\theta \right|>h\right\}}\mathbb {1}_{\left\{S_{N}\notin Ω_{N}\right\}}\right)\prod _{j=1}^{N-1}\mathbb {1}_{\left\{S_{j}\in Ω_{j}\right\}}$$

Applying expectation given $\theta$  yields

$$\mathrm {P}\left(\left|\hat {\theta }_{T}-\theta \right|>h|\theta \right)=\mathrm {E}\left[\mathbb {1}_{\left\{\left|\hat {\theta }_{0}-\theta \right|\right\}}\mathbb {1}_{\left\{S_{0}\notin Ω_{0}\right\}}+\cdots \right.\quad +\mathrm {E}\left[\mathbb {1}_{\left\{\left|\hat {\theta }_{N-1}-\theta \right|>h\right\}}\mathbb {1}_{\left\{S_{N-1}\notin Ω_{N}\right\}}+\left(\mathrm {E}\left[\mathbb {1}_{\left\{\left|\hat {\theta }_{N}-\theta \right|>h\right\}}\mathbb {1}_{\left\{S_{N}\notin Ω_{N}\right\}}|\mathscr {F}_{N-1},\theta \right]\right)\mathbb {1}_{\left\{S_{N-1}\in Ω_{N-1}\right\}}|\mathscr {F}_{N-2},\theta ]\right)\cdots |\theta |$$

Defining $W_{N}\left(S_{N}\right)=\mathbb {1}_{\left\{\left|\hat {\theta }_{N}-\theta \right|>h\right\}}$ it is straightforward to see that the recursion in (25) computes the desired complementary coverage probability. Similarly for (26) only now instead of conditioning with respect to both $\mathscr {F}_{t}$ and $\theta$  we condition only with respect to $\mathscr {F}_{t}$ . This concludes the proof. ☐

Proof of Theorem 2: Let us first find upper and lower bounds of $\mathscr {C}_{}\left(S_{}\right)$ that are independent from $S_{t}$ From [27,Theorem 2.1] and for a random variable X with density $Beta(x,p,q)$ we have that

$$\mathrm {E}\left[e^{λ(X-μ)}\right]\leq e^{\frac {λ^{2}}{8(p+q+1)}},λ>0\tag{37}$$

where $μ=\frac {p}{p+q}$ is the average under the Beta density. Using the Markov inequality we can then write

$$\mathrm {P}(|X-μ|>h)=\mathrm {P}(X-μ>h)+\mathrm {P}(X-μ<-h)=\mathrm {P}(X-μ>h)+\mathrm {P}(1-X-(1-μ)>h)\quad \leq \frac {\mathrm {E}\left[e^{λ(X-μ)}\right]}{e^{λh}}+\frac {\mathrm {E}\left[e^{λ(1-X-(1-μ))}\right]}{e^{λh}}\leq 2e^{\frac {λ^{2}}{8(p+q+1)}-λh},\tag{38}$$

where we used the fact that if X is Beta distributed with parameters $p,q$  then $1-X$ is also Beta with parameters $q,p$ . Selecting in (38) $λ=4(p+q+1)h$ yields the tightest upper bound, namely

$$\mathrm {P}(|X-μ|>h)\leq 2e^{-2h^{2}(p+q+1)}\tag{39}$$

We can now use this result to upper bound $\mathscr {C}_{t}\left(S_{t}\right)$ .We observe that

$$\mathscr{C}_{t}\left(S_{t}\right)=\inf _{\hat{\theta}_{t}}\mathrm{P}\left(\left|\theta-\hat{\theta}_{t}\right|>h\mid \mathscr{F}_{t}\right)\leq \mathrm{P}\left(\left|\theta-\mathrm{E}\left[\theta \mid \mathscr{F}_{t}\right]\right|>h\mid \mathscr{F}_{t}\right)\leq 2e^{-2h^{2}(t+2a+1)}\tag{40}$$

For for the last inequality we used (39) and the fact that $\theta$  given $\mathscr {F}_{t}$ is Beta distributed with parameters $p=S_{t}+a$ and $q=t-S_{t}+a$ 

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 20 -->

Let us now find a lower bound for $\mathscr {C}_{t}\left(S_{t}\right)$ .From[25, Page 944, Formula 26.5.15] we conclude that $I_{x}(p,q)>I_{x}(p+1,q-1)$ for $q>1.$ Using this inequality repeatedly in (28) we conclude

$$\mathrm {P}\left(\left|\hat {\theta }_{t}-\theta \right|>h|\mathscr {F}_{t}\right)=1-I_{\min \left\{1,\hat {\theta }_{t}+h\right\}}\left(S_{t}+a,t-S_{t}+a\right)+I_{\max \left(0,\hat {\theta }_{t}-h\right)}\left(S_{t}+a,t-S_{t}+a\right)$$

$$=I_{\max \left\{0,1-h-\hat {\theta }_{t}\right\}}\left(t-S_{t}+a,S_{t}+a\right)+I_{\max \left(0,\hat {\theta }_{t}-h\right)}\left(S_{t}+a,t-S_{t}+a\right)$$

$$\geq I_{\max \left\{0,1-h-\hat {\theta }_{t}\right\}}\left(t+2n_{a}+δ_{a},δ_{a}\right)+I_{\max \left\{0,\hat {\theta }_{t}-h\right\}}\left(t+2n_{a}+δ_{a},δ_{a}\right)\tag{41}$$

where for the second equality we used the property $1-I_{x}(p,q)=I_{1-x}(q,p)$ and where $n_{a},δ_{a}$ are defined

as

$_{a}=\left\{\begin{array}{cl}[a]&\text {if}a\text {ot}\\ a-1&\text {if}a\text {ai}\end{array}\right.$ an integer - $δ_{a}=\left\{\begin{array}{cl}a-[a]&\text {if}a\\ 1&\text {if}a\end{array}\right.$ ot an integer nteger, integer

where $[a]$  denotes integer part of $a$ . Since $a>0$ we have $n_{a}\geq 0,1\geq δ_{a}>0$ and $a=n_{a}+δ_{a}$ .By taking the derivative of the last sum in (41) with respect to $\hat {\theta }_{t}$ we can show that it has the same sign as the following expression

$$φ\left(\hat {\theta }_{t}\right)=\frac {\left(\hat {\theta }_{t}-h\right)^{t+2n_{a}+δ_{a}-1}}{\left(1+h-\hat {\theta }_{t}\right)^{1-δ_{a}}}-\frac {\left(1-h-\hat {\theta }_{t}\right)^{t+2n_{a}+δ_{a}-1}}{\left(\hat {\theta }_{t}+h\right)^{1-δ_{a}}}$$

Now it is easy to verify that $φ\left(1-\hat {\theta }_{t}\right)=-φ\left(\hat {\theta }_{t}\right)$ therefore it is sufficient to analyze the sign of $φ\left(\hat {\theta }_{t}\right)$ for $h\leq \hat {\theta }_{t}\leq 0.5$  When $t\geq 1$ and because $1\geq δ_{a}$ we can see that the sign is negative for any value of $a$ ,suggesting that we have a minimum for $\hat {\theta }_{t}=0.5.$ .Therefore,if $Γ(x)$ denotes the Gamma function,then for $t\geq 1$ we can write

$$\mathscr {C}_{t}\geq 2I_{0.5-h}\left(t+2n_{a}+δ_{a},δ_{a}\right)\geq 2\frac {Γ\left(t+2n_{a}+2δ_{a}\right)\left(0.25-h^{2}\right)^{δ_{a}}}{Γ\left(t+2n_{a}+δ_{a}+1\right)Γ\left(δ_{a}\right)}(0.5-h)^{t+2n_{a}}$$

$$=2\frac {Γ\left(t+2n_{a}+2δ_{a}+1\right)\left(0.25-h^{2}\right)^{δ_{a}}}{\left(t+2n_{a}+2δ_{a}\right)Γ\left(t+2n_{a}+δ_{a}+1\right)Γ\left(δ_{a}\right)}(0.5-h)^{t+2n_{a}}$$

$$\geq 2\frac {\left(0.25-h^{2}\right)^{δ_{a}}}{\left(t+2n_{a}+2δ_{a}\right)Γ\left(δ_{a}\right)}(0.5-h)^{t+2n_{a}}\tag{42}$$

In the previous expression the second inequality comes from [25, Page 944, Formula 26.5.16]; for the next equality we usedI the property $Γ(x+1)=xΓ(x)$ ; while for the last inequality we used the increase of $Γ(x)$ for $x\geq 1$ $.5$ ,which is true in our case for $t\geq 1$ and any $a>0.$ 

Having established bounds for $\mathscr {C}_{t}$ we can now compute an upper bound N for $t_{\mathrm {up}}$ and a lower bound v for $t_{\mathrm {lo}}$ therefore proving their existence and demonstrating properties i) and ii). We first note that if $\mathscr {C}_{N}\leq c$ in (14) we will have $\mathscr {C}_{N}\leq c+\tilde {\mathscr {V}}_{N}$ meaning that $\mathscr {V}_{N}=\mathscr {C}_{N}$ and consequently N is a stopping instant for all values of $S_{t}$ .This implies that $T_{\mathrm {o}}\leq N$ .Quantity $t_{\mathrm {up}}$ is the smallest N for which this inequality is true for all $S_{t}$ .Requiring $2e^{-2h^{2}(N+2a+1)}\leq c$ $we$ obtain

$$N=\left\lceil \max \left\{0,\frac {|\log (c)|+\log (2)}{2h^{2}}-2a-1\right\}\right\rceil\tag{43}$$

<!-- DRAFT -->

<!-- November 21,2017 -->

<!-- 21 -->

To find a lower bound v for $t_{\mathrm {l}}$ we combine the lower bound of $\mathscr {C}_{t}$ with an upper bound for $\mathscr {V}_{t}$ .Finding the latter is straightforward. Indeed if we start from time instantNwhich,as we argued, is selected so that $\mathscr {C}_{N}\leq c,$ ,then using induction and the fact that

$$\mathscr {V}_{t}=\min \left\{\mathscr {C}_{t},c+\mathrm {E}\left[V_{t+1}|\mathscr {F}_{t}\right]\right\}\leq c+\mathrm {E}\left[\mathscr {V}_{t+1}|\mathscr {F}_{t}\right]$$

we can show that $\mathscr {V}_{t}\leq c+c(N-t)=c(N+1-t)$ . It is then clear that, as long as $c(N+1)\leq \mathscr {C}_{0},$ for any $t\geq 1$ for which we have

$$c(N+1-t)\left(t+2n_{a}+2δ_{a}\right)\leq 2\frac {\left(0.25-h^{2}\right)^{δ_{a}}}{Γ\left(δ_{a}\right)}(0.5-h)^{t+2n_{a}}\tag{44}$$

we do not stop at this time instant. In fact we can see that we have an interval of the form $t\in [0,\cdots ,ν]$ during which no stopping can occur. A rough estimate of v can be obtained by solving instead of (44) the simpler alternative maxt $c(N+1)\left(t+2n_{a}+2δ_{a}\right)=\frac {c}{4}\left(N+2n_{a}+2δ_{a}\right)^{2}\leq \frac {2\left(0.25-h^{2}\right)^{δ_{a}}}{Γ\left(δ_{a}\right)}(0.5-h)^{ν+2n_{a}}$ which yields

$$ν=\left\lfloor \max \left\{0,\frac {|\log (c)|-\log \left(\left(N+2n_{a}+δ_{a}\right)^{2}Γ\left(δ_{a}\right)\right)+\log \left(8\left(0.25-h^{2}\right)^{δ_{a}}\right)}{|\log (0.5-h)|}-2n_{a}\right\}\right\rfloor\tag{45}$$

provided c satisfies $c\leq \frac {\mathscr {C}_{0}}{N+1}$ .Regarding the latter, if we are in the non-trivial case where we do not stop at time 0 then $α<\mathscr {C}_{0}$ ,consequently it is sufficient to have $c\leq \frac {α}{N+1}$ . We thus conclude that for small enough c there is a lower limit $t_{\mathrm {lo}}\geq ν$ which is nontrivial. This concludes the proof. ☐

## REFERENCES

[1] A. Sullivan, D. Raben, J. Reekie, M. Rayment, A. Mocroft et al., "Feasibility and effectiveness of indicator condition-guided testing for HIV: results from HIDES I (HIV indicator diseases across Europe study)," PLoS ONE, vol. 8, no. 1,p. e52845,2013.

[2] J. Abramson, R. Takvorian, D. Fisher, Y. Feng, E. Jacobsen et al., "Oral clofarabine for relapsed/refractory non-Hodgkin lymphomas: results of a phase 1 study." Leukemia & Lymphoma, vol. 54, pp. 1915-1920,2013.

[3] J.T. Morisette and S. Khorram, “Exact binomial confidence interval for proportions," Photogrammetric Engineering & Remote Sensing, vol. 64, no. 4, pp. 281-283,1998.

[4] A. Agresti and B. A. Coull, “Approximate is better than “exact" for interval estimation of binomial proportions," The American Statistician, vol. 52, pp. 119-126,1998.

[5] L.D. Brown, T. Cai, and A. Dasgupta, "Interval estimation for a binomial proportion (with discussion)," Statistical Science, vol. 16, pp. 101-133,2001.

[6] R. G. Newcombe, “Two-sided confidence intervals for the single proportion: comparison of seven methods," Statistics in Medicine, vol. 17, pp. 857-872,1998.

[7] S. E. Vollset, "Confidence intervals for a binomial proportion," Statistics in Medicine, vol. 12, no. 9, pp. 809-824,1993.

[8] E.B. Wilson,"Probable inference, the law of succession, and statistical inference," Journal of the American Statistical Association, vol. 22, pp. 209-212,1927.

<!-- November 21,2017 -->

<!-- DRAFT -->

<!-- 22 -->

[9] C.J.Clopper and E. S. Pearson, "The use of confidence or fiducial limits illustrated in the case of the binomial," Biometrika, vol. 26, pp. 404-413,1934.

[10] T.E. Sterne, "Some remarks on confidence of fudicial limits," Biometrika, vol. 41, no. 1,pp.275-278,1954.

[11] E.L. Crow,"Confidence intervals for a proportion," Biometrika, vol. 43, pp. 423-435,1956.

[12] C.R. B3lyth and H. A. Still, "Binomial confidence intervals," Journal of the American Statistical Association, vol. 78, pp. 108-116,1983.

[13] L. D. Brown, T. Cai, and A. DasGupta, “Interval estimation for a binomial proportion and asymptotic expansions,"The Annals of Statistics, vol. 30, pp. 160-201,2002.

[14] J. Reiczigel, "Confidence intervals for the binomial parameter: some new considerations," Statistics in Medicine, vol. 22, no.4,pp.611-621,2003.

[15] A.M. Pires and C. Amado, “Interval estimators for a binomial proportion: comparison of twenty methods," REVSTAT-Statistical Journal, vol. 6, no. 2, pp. 165-197,2008.

[16]M. Thulin, "The cost of using exact confidence intervals for a binomial proportion," Electron. J. Statist., vol. 8, no.1,pp. 817-840,2014.

[17] C. Jegourel, J. Sun, and J. S. Dong, Sequential Schemes for Frequentist Estimation of Properties in Statistical Model Checking. Springer International Publishing, 2017, pp. 333-350.

[18] Y.S.Chow and H. Robbins, "On the asymptotic theory of fixed-width sequential confidence intervals for the mean," The Annals of Mathematical Statistics, vol. 36,no.2,pp.457-462,1965.

[19] M. Tanaka, “On a confidence interval of given length for the parameter of the binomial and the Poisson distributions," Annals of the Institute of Statistical Mathematics, vol. 13,pp.201-215,1961.

[20] J.Frey, "Fixed-width sequential confidence intervals for a proportion," The American Statistician, vol. 64, pp. 242-249, 2010.

[21] P. Cabilio, "Sequential estimation in Bernoulli trials," The Annals of Statistics, vol. 5, no. 2, pp. 342-356,1977.

[22] H. V. Poor, An Introduction to Signal Detection and Estimation, 2nd ed. New York: Springer, 1988.

[23] A.N. Shiryaev, Optimal Stopping Rules. Springer, 1978.

[24] T. Choi and R. V. Ramamoorthi, Remarks on consistency of posterior distributions, ser. Collections. Beachwood,Ohio, USA: Institute of Mathematical Statistics, 2008, vol. Volume 3, pp. 170-186.

[25] M. Abramowitz and I. A.Stegun, Handbook of Mathematical Functions, 9th ed. Dover Publication, 1972.

[26] G. V. Moustakides, T. Yaacoub, and Y. Mei, "Sequential estimation based on conditional cost," Proceedings of IEEE International Symposium on Information Theory, pp. 436-440, June 2017.

[27] O.Marchal and J. Arbel, "On the sub-Gaussianity of the Beta and Dirichlet distributions," Electron. Commun. Probab., vol.22,no.54,pp.1-14,2017.

<!-- DRAFT -->

<!-- November 21,2017 -->


