"""Q1-A1 核心：Bernoulli 观测的 Beta–Binomial mixture 置信序列。

依据：B题阶段2模型设计报告 §4.4；阶段3算法设计报告 §4.2。
论文依据：Howard, Ramdas, McAuliffe, Sekhon (2021),
"Time-uniform, nonparametric, nonasymptotic confidence sequences".

===========================================================================
数学构造
===========================================================================
设 X_1, X_2, ... i.i.d. ~ Bernoulli(p)，K_t = sum_{i<=t} X_i。
取一个**不依赖数据**的先验 q ~ Beta(a, b)，定义混合似然比

    M_t(p) = ∫_0^1  [ q^{K_t} (1-q)^{t-K_t} ] / [ p^{K_t} (1-p)^{t-K_t} ]  dBeta(q; a, b)
           =  B(a+K_t, b+t-K_t) / B(a, b)  /  [ p^{K_t} (1-p)^{t-K_t} ].

对每个固定 p，{M_t(p)} 在 P_p 下是均值为 1 的非负鞅（它是似然比的混合）。
由 Ville 不等式：

    P_p( 存在某个 t 使 M_t(p) >= 1/alpha )  <=  alpha.

因此把 M_t(p) 反演得到的

    C_t(alpha) = { p in [0,1] : log M_t(p) < log(1/alpha) }

是一个 **anytime-valid** 的 (1-alpha) 置信序列：可以逐件看数据、随时停止，
覆盖保证依然成立。这正是 Q1 允许"边抽边停"所必需的性质——普通固定样本
置信区间在反复查看下会失效。

===========================================================================
本实现的两点工程决定（与阶段3报告的差异，已在交付说明中标注）
===========================================================================
决定 1：先验固定在 p0 处，不随被检验的 p 移动。
    取 a = t_opt * p0, b = t_opt * (1 - p0)。
    好处：log M_t(p) 中只有 -K log p - (t-K) log(1-p) 依赖 p，该项严格凸，
    故 C_t(alpha) **保证是一个区间**，端点可用 brentq 稳定求得，不会出现
    非连通的次水平集。若先验随 p 移动则凸性无保障，数值上要靠网格扫描兜底。
    调参口径与报告一致：v_opt = p0 (1-p0) t_opt 对应 a+b = t_opt。
    （高斯类比：mixture 边界在 intrinsic time v_t = t p0(1-p0) = 1/rho 处最紧，
      而 Beta(a,b) 先验诱导的 lambda 方差 rho ≈ 1/[(a+b) p0(1-p0)]。）

决定 2：判定规则不需要求根。
    log M_t(p) 关于 p 严格凸、极小点在 p_hat = K_t/t。因此
        p0 < L_t(alpha)  <=>  logM_t(p0) >= log(1/alpha)  且  p_hat > p0
        U_t(alpha) <= p0 <=>  logM_t(p0) >= log(1/alpha)  且  p_hat <= p0
    只需在 p0 这一点求值，全 (t,k) 三角表可用 gammaln 的外和一次性算出，
    O(N^2) 次加法，无迭代、无求根误差。
    端点求根版本 `cs_interval` 仍然实现，专门用于**交叉核验**与论文作图，
    对应报告 §4.2 要求的"两套独立实现，端点差 > 1e-8 则返回 CS_CROSSCHECK_FAILED"。
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.special import betaln, gammaln

__all__ = [
    "mixture_prior",
    "log_mixture_at",
    "log_mixture_triangle_at_p0",
    "cs_interval",
    "clopper_pearson_upper",
    "clopper_pearson_lower",
]

_EPS = 1e-15


# --------------------------------------------------------------------------
# 先验
# --------------------------------------------------------------------------
def mixture_prior(t_opt: int, p0: float) -> tuple[float, float]:
    """返回 mixture 先验 Beta(a, b)。

    a + b = t_opt 是先验伪计数，等价于 intrinsic time v_opt = p0(1-p0)*t_opt。
    先验均值取 p0，使边界在标称值附近最紧。
    """
    if t_opt <= 0:
        raise ValueError(f"t_opt 必须为正整数，收到 {t_opt}")
    a = t_opt * p0
    b = t_opt * (1.0 - p0)
    return a, b


# --------------------------------------------------------------------------
# 逐点求值（标量 / 数组）
# --------------------------------------------------------------------------
def log_mixture_at(t: int, k: int, p: float, a: float, b: float) -> float:
    """log M_t(p)，单点。log 域计算，避免大 t 下溢。"""
    if not 0 <= k <= t:
        raise ValueError(f"要求 0 <= k <= t，收到 t={t}, k={k}")
    p = min(max(p, _EPS), 1.0 - _EPS)
    log_marginal = betaln(a + k, b + t - k) - betaln(a, b)
    log_null = k * np.log(p) + (t - k) * np.log1p(-p)
    return float(log_marginal - log_null)


def log_mixture_triangle_at_p0(n_max: int, p0: float, a: float, b: float) -> np.ndarray:
    """一次性算出整个三角表 logM[t, k] = log M_t(p0)，0 <= k <= t <= n_max。

    利用 betaln(a+k, b+t-k) = gammaln(a+k) + gammaln(b+t-k) - gammaln(a+b+t)，
    把 O(N^2) 次 betaln 降为 O(N) 次 gammaln + O(N^2) 次加法。
    上三角（k > t）填 NaN，永不被读取。
    """
    idx = np.arange(n_max + 1)
    ga = gammaln(a + idx)          # gammaln(a + k)
    gb = gammaln(b + idx)          # gammaln(b + t - k)
    gab = gammaln(a + b + idx)     # gammaln(a + b + t)
    const = betaln(a, b)

    log_p0 = np.log(p0)
    log_q0 = np.log1p(-p0)

    # log_marginal[t, k] = ga[k] + gb[t-k] - gab[t] - const
    # log_null[t, k]     = k*log_p0 + (t-k)*log_q0
    tri = np.full((n_max + 1, n_max + 1), np.nan, dtype=np.float64)
    for t in range(n_max + 1):
        k = idx[: t + 1]
        log_marginal = ga[: t + 1] + gb[t::-1][: t + 1] - gab[t] - const
        log_null = k * log_p0 + (t - k) * log_q0
        tri[t, : t + 1] = log_marginal - log_null
    return tri


# --------------------------------------------------------------------------
# 端点反演（交叉核验用）
# --------------------------------------------------------------------------
def cs_interval(
    t: int,
    k: int,
    alpha: float,
    a: float,
    b: float,
    xtol: float = 1e-12,
) -> tuple[float, float]:
    """求 C_t(alpha) = {p : log M_t(p) < log(1/alpha)} 的端点 (L_t, U_t)。

    log M_t(p) 关于 p 严格凸、极小点 p_hat = k/t，故次水平集是区间，
    两侧各用一次 brentq。t = 0 时无信息，返回 [0, 1]。
    """
    if t == 0:
        return 0.0, 1.0
    thr = np.log(1.0 / alpha)

    def g(p: float) -> float:
        return log_mixture_at(t, k, p, a, b) - thr

    p_hat = k / t
    if g(min(max(p_hat, _EPS), 1 - _EPS)) >= 0.0:
        # 混合似然在最优点仍越界：区间为空。理论上不会发生（混合似然 <= 最大似然），
        # 交给调用方按数值异常处理。
        return float("nan"), float("nan")

    lo_anchor = max(p_hat, _EPS) if k > 0 else _EPS
    hi_anchor = min(p_hat, 1 - _EPS) if k < t else 1 - _EPS

    L = 0.0 if g(_EPS) < 0.0 else brentq(g, _EPS, lo_anchor, xtol=xtol, rtol=1e-15)
    U = 1.0 if g(1 - _EPS) < 0.0 else brentq(g, hi_anchor, 1 - _EPS, xtol=xtol, rtol=1e-15)
    return float(L), float(U)


# --------------------------------------------------------------------------
# 固定样本精确二项基准（阶段2报告 §4.2，仅作数量级核验）
# --------------------------------------------------------------------------
def clopper_pearson_upper(n: int, x: int, level: float = 0.90) -> float:
    """单侧精确上置信界 U_level(n, x) = F^{-1}_{Beta(x+1, n-x)}(level)。

    注意：这是**固定时点**的界。反复查看后提前停止会破坏其错误控制，
    所以它只用于核验数量级，不能当作序贯规则。
    """
    from scipy.stats import beta as beta_dist

    if x == n:
        return 1.0
    return float(beta_dist.ppf(level, x + 1, n - x))


def clopper_pearson_lower(n: int, x: int, level: float = 0.95) -> float:
    """单侧精确下置信界 L_level(n, x) = F^{-1}_{Beta(x, n-x+1)}(1 - level)。"""
    from scipy.stats import beta as beta_dist

    if x == 0:
        return 0.0
    return float(beta_dist.ppf(1.0 - level, x, n - x + 1))


# --------------------------------------------------------------------------
# 官方 confseq 库对照（阶段3报告 §3.1 要求，但不作为运行的硬依赖）
# --------------------------------------------------------------------------
def confseq_available() -> bool:
    try:
        import confseq  # noqa: F401
        return True
    except ImportError:
        return False


def crosscheck_against_confseq(
    samples: np.ndarray,
    alpha: float,
    t_opt: int,
    p0: float,
    tol: float = 1e-8,
) -> tuple[bool, str]:
    """把本模块的端点与官方 `confseq` 的 Bernoulli CS 逐点对照。

    报告 §3.1 要求"使用官方实现；另写独立公式进行交叉核验，不把第三方库当黑箱"。
    本仓库的主实现是独立公式（Howard 2021 的 Beta-Binomial mixture），
    此函数提供反向对照。未安装 confseq 时返回 (True, "skipped")，
    因为 stopping_rule.crosscheck_action_table 已经用两套自有实现完成了强制核验。

    注意：confseq 的 `betting_*` / `bernoulli_confidence_interval` 用的是
    不同的调参口径（v_opt / 下注策略），端点不会逐位相同。所以这里比对的是
    **判定一致性**（是否越过 p0），不是端点数值相等。
    """
    if not confseq_available():
        return True, "skipped: confseq 未安装，已由两套自有实现完成强制交叉核验"

    from confseq.betting import betting_ci  # type: ignore

    x = np.asarray(samples, dtype=float)
    v_opt = p0 * (1.0 - p0) * t_opt
    try:
        lo, hi = betting_ci(x, alpha=alpha, breaks=1000)
    except TypeError:
        lo, hi = betting_ci(x, alpha)

    t, k = len(x), int(x.sum())
    a, b = mixture_prior(t_opt, p0)
    own_lo, own_hi = cs_interval(t, k, alpha, a, b)

    same_reject = (own_lo > p0) == (lo > p0)
    same_accept = (own_hi <= p0) == (hi <= p0)
    if same_reject and same_accept:
        return True, f"判定一致 (v_opt={v_opt:.4f}); 自有=[{own_lo:.6f},{own_hi:.6f}] confseq=[{lo:.6f},{hi:.6f}]"
    return False, (
        f"CS_CROSSCHECK_FAILED: 自有=[{own_lo:.6f},{own_hi:.6f}] "
        f"confseq=[{lo:.6f},{hi:.6f}] tol={tol}"
    )
