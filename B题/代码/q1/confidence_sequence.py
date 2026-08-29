"""Official ConfSeq boundary calls and an independent SciPy inversion."""

from __future__ import annotations

import math

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq
from scipy.special import betaln, betainc, logsumexp

try:
    from confseq import boundaries as _official
except ImportError as exc:  # Official implementation is mandatory.
    raise RuntimeError(
        "CS_CROSSCHECK_FAILED: official confseq is required; install requirements-q1.txt"
    ) from exc


def _official_log(s: float, v: float, v_opt: float, g: float, h: float,
                  alpha_opt: float) -> float:
    return float(_official.beta_binomial_log_mixture(
        s, v, v_opt, g, h, alpha_opt, True
    ))


def _log_incomplete_beta(a: float, b: float, x: float) -> float:
    value = float(betainc(a, b, x))
    if value > 0.0 and math.isfinite(value):
        return float(betaln(a, b) + math.log(value))
    nodes, weights = leggauss(256)
    q = x * (nodes + 1.0) / 2.0
    terms = np.log(weights * x / 2.0) + (a - 1.0) * np.log(q) + (b - 1.0) * np.log1p(-q)
    return float(logsumexp(terms))


def _independent_log(s: float, v: float, v_opt: float, g: float, h: float,
                     alpha_opt: float) -> float:
    """SciPy translation of ConfSeq's one-sided BetaBinomialMixture."""
    z = math.log(1.0 / (2.0 * alpha_opt))
    rho = v_opt / (2.0 * z + math.log1p(2.0 * z))
    r = max(rho - g * h, 1e-3 * g * h)
    a0, b0 = r / (g * (g + h)), r / (h * (g + h))
    normalizer = _log_incomplete_beta(a0, b0, h / (g + h))
    a = (r + v - g * s) / (g * (g + h))
    b = (r + v + h * s) / (h * (g + h))
    return (
        v / (g * h) * math.log(g + h)
        - (v + h * s) / (h * (g + h)) * math.log(g)
        - (v - g * s) / (g * (g + h)) * math.log(h)
        + _log_incomplete_beta(a, b, h / (g + h))
        - normalizer
    )


def official_boundaries(n_max: int, p0: float, alpha_reject: float,
                        alpha_accept: float, t_opt: int) -> tuple[np.ndarray, np.ndarray]:
    """Return k<=accept and k>=reject thresholds for every time."""
    t = np.arange(n_max + 1, dtype=float)
    v = p0 * (1.0 - p0) * t[1:]
    v_opt = p0 * (1.0 - p0) * t_opt
    reject_radius = _official.beta_binomial_mixture_bound(
        v, alpha_reject, v_opt, p0, 1.0 - p0, alpha_reject, True
    )
    accept_radius = _official.beta_binomial_mixture_bound(
        v, alpha_accept, v_opt, 1.0 - p0, p0, alpha_accept, True
    )
    reject_min = np.full(n_max + 1, n_max + 1, dtype=int)
    accept_max = np.full(n_max + 1, -1, dtype=int)
    reject_min[1:] = np.ceil(p0 * t[1:] + reject_radius - 1e-12).astype(int)
    accept_max[1:] = np.floor(p0 * t[1:] - accept_radius + 1e-12).astype(int)
    idx = np.arange(1, n_max + 1)
    valid_r = reject_min[1:] <= idx
    log_r = np.full(n_max, -np.inf)
    log_r[valid_r] = _official.beta_binomial_log_mixture(
        reject_min[1:][valid_r] - p0 * idx[valid_r], v[valid_r], v_opt,
        p0, 1.0 - p0, alpha_reject, True
    )
    reject_min[1 + np.flatnonzero(log_r < math.log(1.0 / alpha_reject) - 1e-10)] += 1
    valid_a = accept_max[1:] >= 0
    log_a = np.full(n_max, -np.inf)
    log_a[valid_a] = _official.beta_binomial_log_mixture(
        p0 * idx[valid_a] - accept_max[1:][valid_a], v[valid_a], v_opt,
        1.0 - p0, p0, alpha_accept, True
    )
    accept_max[1 + np.flatnonzero(log_a < math.log(1.0 / alpha_accept) - 1e-10)] -= 1
    reject_min[(reject_min < 0) | (reject_min > t)] = n_max + 1
    accept_max[(accept_max < 0) | (accept_max > t)] = -1
    reject_min[0], accept_max[0] = n_max + 1, -1
    if np.any(accept_max >= reject_min):
        raise RuntimeError("INVALID_DATA: accept and reject regions overlap")
    return accept_max, reject_min


def _endpoint(t: int, k: int, alpha: float, t_opt: int, side: str,
              log_fn) -> float:
    phat = k / t
    threshold = math.log(1.0 / alpha)

    def objective(p: float) -> float:
        p = min(max(p, 1e-12), 1.0 - 1e-12)
        g, h = (p, 1.0 - p) if side == "lower" else (1.0 - p, p)
        s = (k - t * p) if side == "lower" else (t * p - k)
        v = p * (1.0 - p) * t
        return log_fn(s, v, p * (1.0 - p) * t_opt, g, h, alpha) - threshold

    eps = 1e-12
    if side == "lower":
        if k == 0 or objective(eps) < 0.0:
            return 0.0
        return float(brentq(objective, eps, max(phat, eps), xtol=1e-12, rtol=1e-14))
    if k == t or objective(1.0 - eps) < 0.0:
        return 1.0
    return float(brentq(objective, min(phat, 1.0 - eps), 1.0 - eps, xtol=1e-12, rtol=1e-14))


def crosscheck_endpoints(t_opt: int, states: list[tuple[int, int]],
                         alpha_reject: float, alpha_accept: float) -> list[dict[str, float]]:
    rows = []
    for t, k in states:
        official_l = _endpoint(t, k, alpha_reject, t_opt, "lower", _official_log)
        scipy_l = _endpoint(t, k, alpha_reject, t_opt, "lower", _independent_log)
        official_u = _endpoint(t, k, alpha_accept, t_opt, "upper", _official_log)
        scipy_u = _endpoint(t, k, alpha_accept, t_opt, "upper", _independent_log)
        rows.append({
            "t_opt": t_opt, "t": t, "k": k,
            "official_lower": official_l, "scipy_lower": scipy_l,
            "official_upper": official_u, "scipy_upper": scipy_u,
            "max_abs_error": max(abs(official_l - scipy_l), abs(official_u - scipy_u)),
        })
    return rows


def fixed_sample_baselines() -> dict[str, float]:
    from scipy.stats import beta

    return {
        "U_0.90(22,0)": float(beta.ppf(0.90, 1, 22)),
        "L_0.95(2,2)": float(beta.ppf(0.05, 2, 1)),
    }
