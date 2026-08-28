---
raw_title: FallahNezhad_2012_Bayesian_Acceptance_Sampling
subject: FallahNezhad_2012_Bayesian_Acceptance_Sampling
source: FallahNezhad_2012_Bayesian_Acceptance_Sampling.pdf
status: mineru解析
parser: mineru
---

# A new Bayesian acceptance sampling plan considering inspection errors

M.S. Fallah Nezhad<sup>∗</sup>, H. Hosseini Nasab

Department ofIndustrial Engineering, Yazd University, Yazd, Iran

Received 29 May 2011; revised 8 February 2012; accepted 15 May 2012

## KEYWORDS

Acceptance sampling plan; Bayesian inference; Prior distribution.

Abstract A sampling plan is a statement of criteria of acceptance applied to a batch, based on appropriate examination of a required number of sample units by specific methods. In this paper, a new acceptance sampling plan is introduced in which it is assumed that every defective item cannot be detected with complete certainty. To model the problem, the probability distribution function ofthe number ofdefective items in the batch is determined through Bayesian inference, and based on this probability density function, the probability of correct decisions in different actions is evaluated. An objective function is defined for each decision that minimizes the ratio of the system cost to the system correct decision probability, including the cost of rejecting the batch, and the cost of defectives items remaining in an accepted batch. Three numerical examples are provided to illustrate the applications of the proposed models.

© 2012 Sharif University of Technology. Production and hosting by Elsevier B.V. Open access under CC BY-NC-ND license.

## 1. Introduction

The sampling plan is a substantial aspect of the quality control problem, where inspection is an important task. In many cases, the inspector is unable to detect all defective items in a batch. Therefore, an estimation process for the number of undiscovered defective items is necessary for decision making about the quality of the batch.

Chun and Sumichrast [1] considered Bayesian inspection models, where there is some prior knowledge about the number of defects in a certain product. They proposed three conditions that should be put forth as desirable properties for a prior probability distribution ofthe number ofdefects in the product, reviewed various prior probability distributions and tested to see if they met those conditions.

Niaki and Fallahnezhad [2] used both stochastic dynamic programming and the Bayesian inferences concept to design an optimum-acceptance-sampling-plan policy in quality contro environments. They employed a combination of costs and risk functions in the objective function. They tried to minimize the ratio of the total discounted system cost to the discounted system correct choice probability.

Some researchers have considered a number ofdistributions arising from inspection sampling, when inspection may fai to identify a defective item, or may erroneously classify a non-defective item as ‘defective’ [3–5]. Kotz and Johnson [6] analyzed the effects of false and incomplete identification of nonconforming items on the properties of two-stage acceptance sampling procedures. They presented numerical tables, and some discussion of sensitivity to inspection errors. Bar-Lev et al. [7] considered multistage group testing with incomplete identification and unreliability features. The objective of their model is to find a cost-efficient group testing policy to select a pre-specified number of non-defective items from some populations in the presence of false-positive and false-negative test results, subject to reliability and other constraints. Bonett [8] defined a capture–recapture sampling plan for estimating the number of defects in one or more products. His sampling plan is useful in applications where every defect cannot be detected with complete certainty. Fallahnezhad and Hosseininasab [9] proposed a single stage acceptance sampling plan based on the control threshold policy. Fallahnezhad and Niaki [10] proposed a new acceptance sampling policy based on a number of successive conforming items. Fallahnezhad et al. [11] proposed a Markov chain approach in acceptance sampling plans based on the cumulative sum of the number of successive conforming items. Also, Fallahnezhad et al. [12] proposed a Bayesian acceptance sampling plan. Aslam et al. [13] presented a decision rule for a repetitive acceptance sampling plan. Fallahnezhad [14] analyzed the acceptance sampling design using a minimum angle method.

In this research, a new policy for an acceptance sampling problem is introduced. The objective of the model is to minimize the ratio of the system cost to the system correct decision probability, including the cost of rejecting the batch, and the cost of defective items remaining in an accepted batch. The probability distribution function of the number of defective items in the batch is considered to be determined based on the number of detected defective items, through Bayesian inference. Then, the value of the objective function for acceptance/rejection decisions is determined based on this probability density function. To the best of the author’s knowledge, no attention has been paid to the problem of Bayesian sampling designs in the case of imperfect inspection, where the ratio of cost to correct decision probability is defined as the objective function.

The paper is managed as follows: The assumptions and proposed model are presented in Section 2. The application of the proposed model for non-informative prior distribution, Poisson prior distribution and negative binomial prior distribution comes in Sections 3–5, respectively, and numerical examples for these prior distributions comes in Sections 3.1, 4.1 and 5.1, respectively. We discuss and conclude the results in Section 6.

## 2. The model

Suppose that a batch including n items is inspected, and the inspection process is imperfect, so that all defective items are not detected during the inspection process. To model the problem, two following assumptions are made:

1. However imperfect the inspection process is, the probability of detecting a defective item is given.

2. Because of the sampling cost, all items in the batch are not inspected, but the proportion of the batch that is inspected is given. Furthermore, the probability distribution function of the number of defective items in the batch is determined conditionally, based on the number of defective items that are detected in the inspection process. This probability distribution function is used to construct the objective function of the proposed model.

The following notation is necessary to explain and formulate the problem:

Z Total number of defective items in the batch;

π The proportion of the batch that is inspected during the inspection process;

Y Number of defective items in an inspected part of the batch;

p Inspection effectiveness (i.e., probability of detecting a defective item when inspected);

X Number of defective items in the inspected part that are detected during the inspection process;

R The cost of rejecting the batch;

c The cost of one defective item;

$\delta _ { 1 }$ The maximum acceptable level of batch quality;

$\delta _ { 2 }$ The minimum reject-able level of batch quality;

m Total number of products in a batch.

To determine the probability distribution function of the number of the defective items, Z, assume that after an inspection process, $X = x$ defective items have been detected. It is required to evaluate the posterior density function of the number of defective items in the batch, $P ( Z | X )$ . The posterior density of Z, given $X = x ,$ , is determined through the Bayesian rule as follows [1]:

$$
\begin{array}{l} P (Z | X) = \frac {P (X | Z) P (Z)}{\sum_ {z} P (X | Z) P (Z)} \\ = \frac {\sum_ {y} P (X | Y) P (Y | Z) P (Z)}{\sum_ {z} \sum_ {y} P (X | Y) P (Y | Z) P (Z)}. \end{array}\tag{1}
$$

In the above formula, it is required to calculate the probability density functions:

$$
P (X | Y), \qquad P (Y | Z), \qquad P (Z).
$$

1. Determining $P ( Y | Z )$

Since Y is the number of defective items in an inspected part of the batch and Z is the total number of defective items in the batch, the probability distribution, $P ( Y | Z ) ,$ , is a binomial distribution with parameters Z and π, where π is the proportion of the batch that is inspected.

2. Determining P(X|Y).

Since X is the number of detected defective items, the conditional probability of X, given Y, is also a binomial distribution, with parameters Y and p, where p is the probability of detecting a defective item.

Thus, by simplifying Eq. (1), the posterior probability distribution functions of Z can be written as follows (Appendix A):

$$
P (Z | X) \propto \frac {Z !}{(Z - X) !} (1 - \pi p) ^ {Z - X} P (Z).\tag{2}
$$

The prior density P(Z) reflects the prior beliefs that we have about parameter Z. If prior distribution P(Z) and posterior distribution P(Z|X) belong to the same family of probability density functions, then it is easy to apply the Bayesian inference in the inspection model. A family of density functions which have the above property is called a conjugate family of distributions [15].

We define an event, CD, as the event of correct decision. The conditional probability of event CD on all events of accepting and rejecting the batch can be defined as follows:

$$
\begin{array}{l} P (\mathrm{CD} | \text { Reject }) = \sum_ {z = \delta_ {2}} ^ {\infty} P (Z | X), \\ P (\mathrm{CD} | \text { Accept }) = \sum_ {z = x} ^ {\delta_ {1}} P (Z | X), \end{array}\tag{3}
$$

where $\delta _ { 1 }$ and $\delta _ { 2 }$ are determined as follows:

$$
\delta_ {1} = m \mathrm{AQL}, \qquad \delta_ {2} = m \mathrm{LTPD},
$$

where AQL is the Accepted Quality Level and LTPD is the Lot Tolerance Proportion Defective. P(CD|Reject) denotes the probability of correct decision when we have rejected the batch. When the proportion of defective items in the batch is LTPD, then this batch should be rejected. Therefore, we have assumed that when the number of defective items in the batch is more than $\delta _ { 2 } ~ = ~ m \mathrm { L T P D ~ o r } ,$ , equivalently, when the proportion of defective items is more than LTPD, then the batch is not acceptable and should be rejected. Thus, we have defined the probability of correct decision conditional on rejecting the batch as the probability of exceeding the number of defective items from $\delta _ { 2 } = m \mathrm { L T P D } .$ . P(CD|Accept) is determined by similar reasoning. The risk of wrong decision making is $1 - P ( \mathrm { C D } )$ and also the performance criteria are defined as the ratio of the cost to (1-risk) criterion. Thus, when the batch is accepted, the performance criteria of the system will be as follows:

$$
P C _ {1} = \frac {c E (Z)}{\sum_ {z = x} ^ {\delta_ {1}} P (Z | X)}.\tag{4}
$$

To reject the batch, the performance criteria of the system wil be as follows:

$$
P C _ {2} = \frac {R}{\sum_ {z = \delta_ {2}} ^ {\infty} P (Z | X)}.\tag{5}
$$

Hence, when $P C _ { 2 } ~ > ~ P C _ { 1 }$ , then, the batch should be accepted, else it should be rejected.

As mentioned, prior density P(Z) reflects prior beliefs that we have about the variable, Z. Since different people may have different prior information, a prior density $\bar { P } ( Z )$ should represent a wide variety of conditions of prior information. In the next sections, different kinds of prior density function, P(Z), for the Bayesian Acceptance Sampling plan are considered, and also the possibility of being a conjugate prior is examined. To perform mathematical computations easily, prior distribution is preferred to be a conjugate prior. Since a conjugate prior distribution leads to a posterior distribution, which is also a member of the same conjugate family, the successive applications of Bayes’ theorem can be easily achieved [1].

## 3. Non-informative prior

In the case of slight prior knowledge, it is better to use a non-informative prior distribution. One of the non-informative prior distributions of the number of defective items is defined as follows:

$$
P (Z) = \frac {1}{Z}.\tag{6}
$$

The posterior distribution of Z can be shown as:

$$
P (Z | X) = \binom{Z - 1}{Z - X} (\pi p) ^ {X} (1 - \pi p) ^ {Z - X},
$$

$$
Z = X, X + 1, \ldots .\tag{7}
$$

This distribution is a negative binomial density function. Thus:

$$
E (Z) = \frac {x}{\pi p}.\tag{8}
$$

Hence, by evaluating the values of $P C _ { 2 }$ and $P C _ { 1 } ,$ the optimal decision can be reached. Since posterior distribution, ${ \bar { P ( Z \vert X ) } }$ does not belong to the same family of prior density functions, it is concluded that prior distribution, $\begin{array} { r } { P ( \bar { Z } ) = \frac { 1 } { Z } } \end{array}$ , is not a conjugate distribution.

## 3.1. Numerical example

For a sampling plan, assume that $\pi \ : = \ : 0 . 1$ and $p = 0 . 9 5$ Other parameters of the decision making problem are:

$$
R = 500\$, \qquad c = 10\$, \qquad \delta_ {1} = 5, \qquad \delta_ {2} = 10.
$$

The values of $P C _ { 2 }$ and $P C _ { 1 }$ for different values of X are shown in Table 1. From Table 1, it is concluded that when the number of defective items in the inspected part of the batch (which are detected during the inspection process) are less than three, the batch should be accepted, otherwise it should be rejected (see the third row of Table 1).

Table 1: The optimal decision for different values of X in non-informative prior distribution.

<table><tr><td>X</td><td> $PC_1$ </td><td> $PC_2$ </td><td>Optimal decision</td></tr><tr><td>1</td><td>1494.882</td><td>11696.55</td><td>Accept the batch</td></tr><tr><td>2</td><td>9493.815</td><td>13928.13</td><td>Accept the batch</td></tr><tr><td>3</td><td>135661.6</td><td>37909.64</td><td>Reject the batch</td></tr><tr><td>4</td><td>5169422</td><td>180569.6</td><td>Reject the batch</td></tr></table>

Table 2: The optimal decision for different values of X in Poisson prior distribution.

<table><tr><td>X</td><td> $PC_1$ </td><td> $PC_2$ </td><td>Optimal decision</td></tr><tr><td>1</td><td>261.0088</td><td>4590.935</td><td>Accept the batch</td></tr><tr><td>2</td><td>512.05</td><td>2642.60</td><td>Accept the batch</td></tr><tr><td>3</td><td>1303.87</td><td>1648.62</td><td>Accept the batch</td></tr><tr><td>4</td><td>4870.82</td><td>1117.71</td><td>Reject the batch</td></tr><tr><td>5</td><td>35727.46</td><td>824.37</td><td>Reject the batch</td></tr></table>

## 4. Poisson distribution

If the prior density of Z is a Poisson distribution with a defective rate, λ:

$$
P (Z) = \frac {e ^ {- \lambda} \lambda^ {Z}}{Z !}, Z = 1, 2, \ldots .\tag{9}
$$

The posterior distribution of Z is determined as follows:

$$
P (Z) = \frac {e ^ {- (1 - \pi p) \lambda} ((1 - \pi p) \lambda) ^ {Z - X}}{(Z - X) !}, \quad Z = X, X + 1, \dots .\tag{10}
$$

Thus:

$$
E (Z) = (1 - \pi p) \lambda .\tag{11}
$$

By evaluating the values of $P C _ { 2 }$ and $P C _ { 1 }$ the optimal decision will be made. Eq. (10) shows that P(Z|X) follows Poisson distribution. Therefore, this distribution belongs to a family of conjugate prior distributions but prior Poisson distribution is not a non-informative prior distribution.

## 4.1. Numerical example

Assume that in an inspection system, $\pi = 0 .$ 1 and $p = 0 . 9 5 .$ Also, the parameters of the decision making problem are

$$
\begin{array}{l l} R = 5 0 0 , & c = 1 0 , \qquad \delta_ {1} = 5, \\ \delta_ {2} = 1 0, & \lambda = 7. \end{array}
$$

The values of $P C _ { 2 }$ and $P C _ { 1 }$ for different values ofX are shown in Table 2.

As shown in Table 2, when the number of defective items in the inspected part (which have been detected during the inspection process) is less than four, then the batch should be accepted, otherwise it should be rejected.

## 5. Negative binomial distribution

If the prior density of Z is a Poisson distribution with a defective rate, $\lambda ,$ then:

$$
P (Z) = \frac {e ^ {- \lambda} \lambda^ {Z}}{Z !} Z = 1, 2, \ldots ,\tag{12}
$$

Table 3: The optimal decision for different values ofX in negative binomial distribution.

<table><tr><td>X</td><td> $PC_1$ </td><td> $PC_2$ </td><td>Optimal decision</td></tr><tr><td>1</td><td>77.52</td><td>2436.34</td><td>Accept the batch</td></tr><tr><td>2</td><td>401.03</td><td>1167.56</td><td>Accept the batch</td></tr><tr><td>3</td><td>2414.46</td><td>751.04</td><td>Reject the batch</td></tr><tr><td>4</td><td>22332.43</td><td>591.30</td><td>Reject the batch</td></tr><tr><td>5</td><td>440783.08</td><td>529.16</td><td>Reject the batch</td></tr></table>

and defective rate λ is distributed as a gamma distribution:

$$
h (\lambda) = \frac {e ^ {- \lambda / b} \lambda^ {a - 1}}{\Gamma (a) b ^ {a}} Z = 1, 2, \dots .\tag{13}
$$

Then, the prior density of Z becomes:

$$
\begin{array}{l} P (Z) = \frac {\Gamma (Z + a)}{\Gamma (Z + 1) \Gamma (a)} \left(\frac {b}{1 + b}\right) ^ {z} \left(\frac {1}{1 + b}\right) ^ {a}, \\ Z = 1, 2, \ldots , \quad E (Z) = a b, \\ \operatorname{Var} (Z) = a b (b + 1). \end{array}\tag{14}
$$

That is known as a negative binomial distribution. The negative binomial prior can represent a wide variety of states of prior information, including the non-informative prior, by changing the values of parameters a and b. When b tends to infinity and a tends to zero, the prior variance ofZ in Eq. (14) tends to infinity, which adequately denotes the inspector’s vague knowledge about Z [1]. In such a case, the negative binomial prior in Eq. (14) reduces to the non-informative prior in Eq. (6). The posterior distribution of Z is calculated as follows (Appendix B):

$$
\begin{array}{l} P (Z | X) = \frac {\Gamma (Z + a)}{\Gamma (Z - x + 1) \Gamma (a + x)} \\ \qquad \times \left(\frac {b (1 - \pi p)}{1 + b}\right) ^ {z - x} \left(\frac {1 + b \pi p}{1 + b}\right) ^ {a + x}, \\ Z = X, X + 1, \ldots . \end{array}\tag{15}
$$

It can be shown that the posterior mean of Z is:

$$
E (Z | X) = \frac {x}{\pi p} \frac {(1 + b) \pi p}{1 + b \pi p} + a b \frac {1 - \pi p}{1 + b \pi p}.\tag{16}
$$

By evaluating the values of $P C _ { 2 }$ and $P C _ { 1 } ,$ , the optimal decision can be made. Also, Eq. (15) shows that P(Z|X) follows a negative binomial distribution. Therefore, this distribution belongs to a family of conjugate prior distributions.

## 5.1. Numerical example

Assume that in an inspection system, $\pi = 0 . 1 , p = 0 . 9 5$ Other parameters of the decision making problem are:

$$
\begin{array}{l} R = 5 0 0 , \qquad c = 1 0 , \qquad \delta_ {1} = 5, \qquad \delta_ {2} = 1 0, \\ a = 2, \qquad b = 3. \end{array}
$$

The values of $P C _ { 2 }$ and $P C _ { 1 }$ for different values ofX are shown in Table 3.

As shown in Table 3, when the number of detected defective items in the inspected part is less than three, then the batch should be accepted, otherwise it should be rejected. Also, it is concluded that all strategies are a type of control threshold strategy, so that if the number of detected defective items is more than a control threshold, the batch should be rejected, otherwise accepted. The outcome of this model ${ \mathrm { i } } s ,$ thus, a type of control threshold policy.

In general, it is concluded that non-informative prior distribution $\begin{array} { r } { P ( X ) \ = \ \frac { 1 } { Z } } \end{array}$ is not a conjugate prior distribution.

Also, Poisson prior distribution is not a non-informative prior distribution. Only the negative binomial distribution has the ability to be a non-informative prior distribution and belongs to the family of conjugate prior distribution. Thus, it is suggested to use this distribution for modelling such problems in practice.

## 6. Conclusion

Because of the methods used in some acceptance sampling plans and inspection errors, all defective items are not detected during the inspection process. In this paper, a new acceptance sampling plan is introduced. It is assumed that the inspection process is imperfect. A Bayesian method is developed for evaluating the probability density function of the number of defective items. Then, the value of the objective function for different decisions is determined. The presented model led to a control threshold policy for a batch acceptance problem. Also, different prior distributions are considered for the Bayesian model, and it is concluded that negative binomial prior is a suitable distribution for modelling the Bayesian acceptance sampling plan. Analyzing the proposed model, regarding the performance measures of acceptance sampling plans (like first and second type error, cost objective function and average number of inspected items), is suggested for future research.

## Appendix A

We assume the conditional probability of Y, given Z is a binomial distribution, and also the conditional probability ofX, given Y is a binomial distribution:

$$
\begin{array}{l} P (Y | Z) = \binom {z} {y} \pi^ {y} (1 - \pi) ^ {z - y}, \\ P (X | Y) = \binom {y} {x} p ^ {x} (1 - p) ^ {y - x}. \end{array}\tag{A.1}
$$

Therefore, from Eq. (A.1), the likelihood function of X is given by a binomial distribution with parameters z and πp [1]:

$$
P (X | Z) = \binom{z}{x} (\pi p) ^ {x} (1 - \pi p) ^ {z - x}.\tag{A.2}
$$

Thus:

$$
\begin{array}{l} P (Z | X) = \frac {\binom {z} {x} (\pi p) ^ {x} (1 - \pi p) ^ {z - x} P (Z)}{\sum_ {z} \binom {z} {x} (\pi p) ^ {x} (1 - \pi p) ^ {z - x} P (Z)} \\ = \frac {\frac {z !}{(z - x) !} (1 - \pi p) ^ {z - x} P (Z)}{\sum_ {z} \frac {z !}{(z - x) !} (1 - \pi p) ^ {z - x} P (Z)}. \end{array}\tag{A.3}
$$

Since $\begin{array} { r } { \sum _ { z } \frac { z ! } { ( z - x ) ! } ( 1 - \pi p ) ^ { z - x } P ( Z ) } \end{array}$ has a constant value, therefore:

$$
P (Z | X) \propto \frac {Z !}{(Z - X) !} (1 - \pi p) ^ {Z - X} P (Z).\tag{A.4}
$$

## Appendix B

We assume that P(Z) is a negative binomial distribution:

$$
\begin{array}{c} P (Z) = \frac {\Gamma (Z + a)}{\Gamma (Z + 1) \Gamma (a)} \left(\frac {b}{1 + b}\right) ^ {z} \left(\frac {1}{1 + b}\right) ^ {a}, \\ Z = 1, 2, \ldots . \end{array}\tag{B.1}
$$

Therefore, from Eq. (A.3), we have:

$$
\begin{array}{l} P (Z | X) = K \frac {Z !}{(Z - X) !} (1 - \pi p) ^ {Z - X} \\ \qquad \times \frac {\Gamma (Z + a)}{\Gamma (Z + 1) \Gamma (a)} \left(\frac {b}{1 + b}\right) ^ {z} \left(\frac {1}{1 + b}\right) ^ {a} \\ \qquad = K \frac {\Gamma (Z + a)}{\Gamma (Z - x + 1) \Gamma (a + x) (1 - \pi p) ^ {X}} \\ \qquad \times \left(\frac {b (1 - \pi p)}{1 + b}\right) ^ {z - x} \left(\frac {1}{1 + b}\right) ^ {a} \\ \qquad Z = X, X + 1, \ldots . \end{array}\tag{B.2}
$$

Now, since $\begin{array} { r } { \sum _ { Z = X } ^ { \infty } P ( Z | X ) = 1 } \end{array}$ , the following is concluded:

$$
\begin{array}{l} \left(K \left(\frac {1}{1 + b}\right) ^ {a} (1 - \pi p) ^ {x}\right) \\ \times \sum_ {Z = X} ^ {\infty} \frac {\Gamma (Z + a)}{\Gamma (Z - x + 1) \Gamma (a + x)} \left(\frac {b (1 - \pi p)}{1 + b}\right) ^ {z - x} = 1. \end{array}\tag{B.3}
$$

Now, by defining a negative binomial distribution with parameters $Z \ - \ \bar { X } \ \mathrm { a n d } \frac { \tilde { b ( 1 - \pi p ) } } { 1 + b }$ , and using the definition of binomial negative distribution, the following is concluded:

$$
\begin{array}{l} \sum_ {Z = X} ^ {\infty} \frac {\Gamma (Z + a)}{\Gamma (Z - X + 1) \Gamma (a + X)} \left(\frac {b (1 - \pi p)}{1 + b}\right) ^ {z - X} \\ = \frac {1}{\left(1 - \frac {b (1 - \pi p)}{1 + b}\right) ^ {Z - X}}. \end{array}\tag{B.4}
$$

Thus:

$$
\begin{array}{l} \sum_ {Z = X} ^ {\infty} P (Z | X) = 1 \to \left(\left(\frac {1}{1 + b}\right) ^ {a} (1 - \pi p) ^ {X} K\right) \\ \qquad = \left(1 - \frac {b (1 - \pi p)}{1 + b}\right) ^ {Z - X} \\ \qquad = \left(\frac {1 + b \pi p}{1 + b}\right) ^ {Z - X}. \end{array}\tag{B.5}
$$

Therefore:

$$
\begin{array}{l} P (Z | X) = \frac {\Gamma (Z + a)}{\Gamma (Z - x + 1) \Gamma (a + x)} \\ \qquad \times \left(\frac {b (1 - \pi p)}{1 + b}\right) ^ {z - x} \left(\frac {1 + b \pi p}{1 + b}\right) ^ {Z - X}, \\ Z = X, X + 1, \ldots . \end{array}\tag{B.6}
$$

## References

[1] Chun, Y.H. and Sumichrast, R.T. ‘‘Bayesian inspection model with the negative binomial prior in the presence of inspection errors’’, European Journal ofOperational Research, 182, pp. 1188–1202 (2007).

[2] Niaki, S.T.A. and Fallahnezhad, M.S. ‘‘Designing an optimum acceptance plan using Bayesian inference and stochastic dynamic programming’’ Scientia Iranica, 16(1), pp. 19–25 (2009).

[3] Johnson, N.L. and Kotz, S. ‘‘Faulty inspection distributions some general izations’’, Institute of Statistics Mimeo Series #1335, University of North Carolina at Chapel Hill, Proc. ofONR/ARO Reliability Workshop (1981).

[4] Johnson, N.L., Kotz, S. and Sorkin, H.L. ‘‘Faulty inspection distributions’’ Communications in Statistics, 9, pp. 917–922 (1980).

[5] Johnson, N.L. and Kotz, S. ‘‘Errors in inspection and grading: distributional aspects of screening and hierarchical screening’’, Communications in Statistics, 11(18), pp. 1997–2016 (1982).

[6] Kotz, S. and Johnson, N.L. ‘‘Effects of false and incomplete identification of defective items on the reliability of acceptance sampling’’, Operation Research, 32(3), pp. 575–590 (1984).

[7] Bar-Lev, S.K., Stadje, W. and Schouten, F.A. ‘‘Group testing procedures with incomplete identification and unreliable testing results’’, Applied Stochastic Models in Business and Industry, 22(3), pp. 281–296 (2006).

[8] Bonett, D.G. ‘‘Estimating the number of defects under imperfect inspection’’,Journal ofApplied Statistics, 15(1), pp. 63–67 (1988).

[9] Fallahnezhad, M.S. and Hosseininasab, H. ‘‘Designing a single stage acceptance sampling plan based on the control threshold policy’’ InternationalJournal ofIndustrial Engineering & Production Research, 22(3) pp. 143–150 (2011).

[10] Fallahnezhad, M.S. and Niaki, S.T.A. ‘‘A new acceptance sampling policy based on number of successive conforming items’’, Communications in Statistics—Theory and Methods (2012) (in press).

[11] Fallahnezhad, M.S., Niaki, S.T.A. and Abooie, M.H. ‘‘A new acceptance sampling plan based on cumulative sums of conforming run-lengths’’ Journal ofIndustrial and Systems Engineering, 4(4), pp. 256–264 (2011).

[12] Fallahnezhad, M.S., Niaki, S.T.A. and Vahdat, M.A. ‘‘A new acceptance sampling design using Bayesian modeling and backwards induction’’, International Journal of Engineering, Islamic Republic of Iran, 25(1) pp. 45–54 (2012).

[13] Aslam, M., Niaki, S.T.A., Rasool, M. and Fallahnezhad, M.S. ‘‘Decision rule of repetitive acceptance sampling plans assuring percentile life’’, Scientia Iranica, Transactions E-Industrial Engineering, 19(3), pp. 879–884 (2012).

[14] Fallahnezhad, M.S. ‘‘A new Markov chain based acceptance sampling policy via the minimum angle method’’, Iranian Journal of Operations Research (2012) (in press).

[15] DeGroot, M.H., Probability and Statistics, 2nd Edn., Addison-Wesley (1986)

Mohammad Saber Fallah Nezhad graduated from Sharif University of Technology, Tehran, Iran, and is currently an academic staff member of the Faculty of Industrial Engineering at Yazd University, Iran. His research area is focused on quality control. He is also interested in stochastic modelling dynamic programming and sequential analysis.

Hasan Hosseini Nasab graduated from Bath University, UK, and is currently an academic staff member of the Faculty of Industrial Engineering at Yazd University, Iran.

His research area is focused on manufacturing. He is also interested in preventive maintenance and production planning.