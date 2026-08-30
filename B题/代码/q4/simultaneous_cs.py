"""固定样本精确区间与可选停止有效的 Beta-mixture Bernoulli CS。"""

from __future__ import annotations

import math

from scipy.optimize import brentq
from scipy.special import betaln
from scipy.stats import beta


def clopper_pearson(n: int, k: int, alpha: float) -> tuple[float, float]:
    lower = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    upper = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lower, upper


def beta_mixture_cs(n: int, k: int, alpha: float,
                    mixture_a: float = 0.5, mixture_b: float = 0.5) -> tuple[float, float]:
    """反演 Beta-mixture e-process；对任意停止时刻保持覆盖。"""
    threshold = math.log(1 / alpha)
    constant = betaln(k + mixture_a, n - k + mixture_b) - betaln(mixture_a, mixture_b)

    def log_e(p: float) -> float:
        return constant - k * math.log(p) - (n - k) * math.log1p(-p)

    eps = 1e-12
    phat = k / n
    lower = 0.0 if k == 0 else float(brentq(lambda p: log_e(p) - threshold, eps, phat))
    upper = 1.0 if k == n else float(brentq(lambda p: log_e(p) - threshold, phat, 1 - eps))
    return lower, upper


def simultaneous_interval(record: dict, alpha_j: float, default_plan: str):
    n, k = record["N"], record["K"]
    rule = record.get("stopping_rule", default_plan)
    if rule == "fixed_n":
        return (*clopper_pearson(n, k, alpha_j), "clopper_pearson_fixed_n")
    return (*beta_mixture_cs(n, k, alpha_j), "beta_mixture_time_uniform_cs")
