"""Q1-M6 的精确固定样本双风险基线。"""

from __future__ import annotations

from scipy.stats import binom


def risks(n: int, cutoff: int, p0: float, p1: float) -> tuple[float, float]:
    return float(binom.sf(cutoff, n, p0)), float(binom.cdf(cutoff, n, p1))


def minimum_plan(p0: float, p1: float, alpha: float, beta: float,
                 max_n: int = 100_000) -> dict[str, float | int]:
    if not 0 < p0 < p1 < 1 or not 0 < alpha < 1 or not 0 < beta < 1:
        raise ValueError("INVALID_DATA: require 0<p0<p1<1 and risks in (0,1)")
    for n in range(1, max_n + 1):
        cutoff = int(binom.ppf(alpha, n, p0))
        while cutoff <= n and binom.sf(cutoff, n, p0) > alpha:
            cutoff += 1
        while cutoff > 0 and binom.sf(cutoff - 1, n, p0) <= alpha:
            cutoff -= 1
        producer, consumer = risks(n, cutoff, p0, p1)
        if producer <= alpha and consumer <= beta:
            return {
                "n_fixed": n, "c_fixed": cutoff,
                "producer_risk": producer, "consumer_risk": consumer,
            }
    raise RuntimeError("INFEASIBLE_RISK_PLAN: fixed-plan search limit reached")
