"""截尾二元序贯规则的精确 Bernoulli 路径递推。"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import binom


@dataclass(frozen=True)
class BoundaryPlan:
    p0: float
    p1: float
    n_max: int
    terminal_cutoff: int
    accept_max: tuple[int, ...]
    reject_min: tuple[int, ...]
    h_accept: float | None
    h_reject: float | None
    family: str

    def __post_init__(self) -> None:
        if len(self.accept_max) != self.n_max + 1 or len(self.reject_min) != self.n_max + 1:
            raise ValueError("INVALID_DATA: boundary length mismatch")
        if any(a >= r for a, r in zip(self.accept_max[:-1], self.reject_min[:-1])):
            raise ValueError("INVALID_DATA: overlapping boundaries")


def llr_boundaries(n_max: int, p0: float, p1: float,
                   h_accept: float, h_reject: float) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if not h_accept < h_reject:
        raise ValueError("INVALID_DATA: h_accept must be below h_reject")
    slope = math.log(p1 * (1 - p0) / (p0 * (1 - p1)))
    intercept = math.log((1 - p1) / (1 - p0))
    accept = [-1] * (n_max + 1)
    reject = [n_max + 1] * (n_max + 1)
    for t in range(1, n_max):
        a = math.floor((h_accept - t * intercept) / slope + 1e-12)
        r = math.ceil((h_reject - t * intercept) / slope - 1e-12)
        accept[t] = a if 0 <= a <= t else -1
        reject[t] = r if 0 <= r <= t else n_max + 1
        if accept[t] >= reject[t]:
            raise RuntimeError("INVALID_DATA: calibrated LLR boundaries overlap")
    return tuple(accept), tuple(reject)


def fixed_plan_as_boundary(p0: float, p1: float, n: int, cutoff: int) -> BoundaryPlan:
    accept = tuple([-1] * n + [cutoff])
    reject = tuple([n + 1] * n + [cutoff + 1])
    return BoundaryPlan(p0, p1, n, cutoff, accept, reject, None, None, "fixed-binomial-baseline")


def evaluate(plan: BoundaryPlan, p: float) -> dict[str, float | int]:
    if not 0 <= p <= 1:
        raise ValueError("INVALID_DATA: p must be in [0,1]")
    if plan.family == "fixed-binomial-baseline":
        accepted = float(binom.cdf(plan.terminal_cutoff, plan.n_max, p))
        rejected = float(binom.sf(plan.terminal_cutoff, plan.n_max, p))
        return {
            "p": p, "P_accept": accepted, "P_reject": rejected,
            "ASN": float(plan.n_max), "P50": plan.n_max, "P90": plan.n_max,
            "P99": plan.n_max, "terminal_mass": 1.0,
            "mass_residual": abs(accepted + rejected - 1.0),
        }
    alive = np.array([1.0])
    offset = 0
    accepted = rejected = asn = 0.0
    stop_pmf = np.zeros(plan.n_max + 1)
    for t in range(1, plan.n_max + 1):
        asn += float(alive.sum())
        nxt = np.zeros(alive.size + 1)
        nxt[:-1] += (1 - p) * alive
        nxt[1:] += p * alive
        k = np.arange(offset, offset + nxt.size)
        if t == plan.n_max:
            accept_mask = k <= plan.terminal_cutoff
            accepted += float(nxt[accept_mask].sum())
            rejected += float(nxt[~accept_mask].sum())
            stop_pmf[t] = float(nxt.sum())
        else:
            accept_mask = k <= plan.accept_max[t]
            reject_mask = k >= plan.reject_min[t]
            accepted += float(nxt[accept_mask].sum())
            rejected += float(nxt[reject_mask].sum())
            stop_pmf[t] = float(nxt[accept_mask | reject_mask].sum())
            keep = ~(accept_mask | reject_mask)
            if not np.any(keep):
                alive = np.zeros(0)
                break
            indices = np.flatnonzero(keep)
            offset += int(indices[0])
            alive = nxt[indices[0]:indices[-1] + 1]
    total = accepted + rejected
    cdf = np.cumsum(stop_pmf)
    return {
        "p": p, "P_accept": accepted, "P_reject": rejected,
        "ASN": asn,
        "P50": int(np.searchsorted(cdf, 0.50, side="left")),
        "P90": int(np.searchsorted(cdf, 0.90, side="left")),
        "P99": int(np.searchsorted(cdf, 0.99, side="left")),
        "terminal_mass": float(stop_pmf[-1]),
        "mass_residual": abs(total - 1.0),
    }


def preterminal(plan: BoundaryPlan, p: float) -> dict[str, object]:
    """返回终端分流前的存活质量，用于精确选择 c_N。"""
    alive = np.array([1.0])
    offset = 0
    accepted = rejected = asn = 0.0
    stop_pmf = np.zeros(plan.n_max + 1)
    for t in range(1, plan.n_max + 1):
        asn += float(alive.sum())
        nxt = np.zeros(alive.size + 1)
        nxt[:-1] += (1 - p) * alive
        nxt[1:] += p * alive
        k = np.arange(offset, offset + nxt.size)
        if t == plan.n_max:
            alive = {int(key): float(value) for key, value in zip(k, nxt) if value > 0}
            break
        accept_mask = k <= plan.accept_max[t]
        reject_mask = k >= plan.reject_min[t]
        accepted += float(nxt[accept_mask].sum())
        rejected += float(nxt[reject_mask].sum())
        stop_pmf[t] = float(nxt[accept_mask | reject_mask].sum())
        keep = ~(accept_mask | reject_mask)
        if not np.any(keep):
            alive = {}
            break
        indices = np.flatnonzero(keep)
        offset += int(indices[0])
        alive = nxt[indices[0]:indices[-1] + 1]
    return {"alive": alive, "accepted": accepted, "rejected": rejected,
            "asn": asn, "stop_pmf": stop_pmf}


def feasible_terminal_cutoffs(at_p0: dict[str, object], at_p1: dict[str, object],
                              n_max: int, alpha: float, beta: float) -> list[tuple[int, float, float]]:
    p0_alive = at_p0["alive"]
    p1_alive = at_p1["alive"]
    output = []
    for cutoff in range(-1, n_max + 1):
        producer = float(at_p0["rejected"]) + sum(v for k, v in p0_alive.items() if k > cutoff)
        consumer = float(at_p1["accepted"]) + sum(v for k, v in p1_alive.items() if k <= cutoff)
        if producer <= alpha + 1e-14 and consumer <= beta + 1e-14:
            output.append((cutoff, producer, consumer))
    return output
