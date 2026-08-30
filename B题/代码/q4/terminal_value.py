"""Q4-A1：Q2 确定性 Beta 求积与 Q3 共同随机数后验价值。"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np
from scipy.special import roots_jacobi
from scipy.stats import beta as beta_dist

from .batch_evaluators import Q2_POLICIES, Q3_POLICY_IDS, q2_profit_batch, q3_profit_batch
from .belief_state import BeliefState


@dataclass
class TerminalValue:
    status: str
    value: float
    best_index: int
    best_label: str | int
    policy_values: np.ndarray
    evpi: float
    integration_order: int
    integration_error: float
    best_optimal_probability: float
    best_mean_regret: float
    best_negative_probability: float
    best_quantiles: tuple[float, float, float]


def _beta_rule(a: float, b: float, order: int) -> tuple[np.ndarray, np.ndarray]:
    x, weights = roots_jacobi(order, b - 1, a - 1)
    return (x + 1) / 2, weights / weights.sum()


def _q2_at_order(case: dict, belief: BeliefState, order: int):
    rules = [_beta_rule(a, b, order) for a, b in zip(belief.alpha, belief.beta)]
    nodes = np.array(list(itertools.product(*(rule[0] for rule in rules))))
    weights = np.array([np.prod(parts) for parts in itertools.product(*(rule[1] for rule in rules))])
    values, feasible = q2_profit_batch(case, nodes)
    if not np.all(feasible == feasible[0]):
        raise RuntimeError("VALUE_INTEGRATION_NOT_CONVERGED: feasibility changed across interior nodes")
    policy_values = np.full(len(Q2_POLICIES), -np.inf)
    policy_values[feasible[0]] = weights @ values[:, feasible[0]]
    feasible_values = values[:, feasible[0]]
    sample_best = np.max(feasible_values, axis=1)
    ev_perfect = float(weights @ sample_best)
    return policy_values, ev_perfect, values, feasible[0], weights


def q2_terminal_value(case: dict, belief: BeliefState, orders: list[int],
                      tolerance: float) -> TerminalValue:
    previous = None
    previous_best = None
    last_error = np.inf
    for order in orders:
        values, ev_perfect, samples, feasible, weights = _q2_at_order(case, belief, order)
        best = int(np.argmax(values))
        if previous is not None:
            finite = np.isfinite(values) & np.isfinite(previous)
            last_error = float(np.max(np.abs(values[finite] - previous[finite])))
            top = np.argsort(values)[-2:]
            gap_error = abs((values[top[-1]] - values[top[-2]]) -
                            (previous[top[-1]] - previous[top[-2]]))
            if last_error <= tolerance and gap_error <= tolerance and best == previous_best:
                best_samples = samples[:, best]
                ties = np.isclose(samples[:, feasible], np.max(samples[:, feasible], axis=1)[:, None],
                                  rtol=1e-11, atol=1e-11)
                feasible_indices = np.flatnonzero(feasible)
                local_best = int(np.flatnonzero(feasible_indices == best)[0])
                return TerminalValue(
                    "VALUE_INTEGRATION_CONVERGED", float(values[best]), best,
                    "".join(map(str, Q2_POLICIES[best])), values,
                    max(0.0, ev_perfect - float(values[best])), order, last_error,
                    float(weights @ (ties[:, local_best] / ties.sum(axis=1))),
                    float(weights @ (np.max(samples[:, feasible], axis=1) - best_samples)),
                    float(weights @ (best_samples < 0)),
                    tuple(float(x) for x in _weighted_quantiles(best_samples, weights, [.05, .5, .95])),
                )
        previous, previous_best = values, best
    best_samples = samples[:, previous_best]
    ties = np.isclose(samples[:, feasible], np.max(samples[:, feasible], axis=1)[:, None], rtol=1e-11, atol=1e-11)
    feasible_indices = np.flatnonzero(feasible)
    local_best = int(np.flatnonzero(feasible_indices == previous_best)[0])
    return TerminalValue(
        "VALUE_INTEGRATION_NOT_CONVERGED", float(previous[previous_best]), previous_best,
        "".join(map(str, Q2_POLICIES[previous_best])), previous,
        max(0.0, ev_perfect - float(previous[previous_best])), orders[-1], last_error,
        float(weights @ (ties[:, local_best] / ties.sum(axis=1))),
        float(weights @ (np.max(samples[:, feasible], axis=1) - best_samples)),
        float(weights @ (best_samples < 0)),
        tuple(float(x) for x in _weighted_quantiles(best_samples, weights, [.05, .5, .95])),
    )


def q3_terminal_value(belief: BeliefState, uniforms: np.ndarray) -> TerminalValue:
    parameters = np.column_stack([
        beta_dist.ppf(uniforms[:, j], belief.alpha[j], belief.beta[j])
        for j in range(len(belief.names))
    ])
    values, feasible = q3_profit_batch(parameters)
    if not np.all(feasible == feasible[0]):
        raise RuntimeError("MC_NOT_CONVERGED: feasibility changed across posterior draws")
    policy_values = np.full(len(Q3_POLICY_IDS), -np.inf)
    policy_values[feasible[0]] = values[:, feasible[0]].mean(axis=0)
    best = int(np.argmax(policy_values))
    ev_perfect = float(np.max(values[:, feasible[0]], axis=1).mean())
    feasible_values = values[:, feasible[0]]
    ties = np.isclose(feasible_values, feasible_values.max(axis=1)[:, None], rtol=1e-11, atol=1e-11)
    feasible_indices = np.flatnonzero(feasible[0])
    local_best = int(np.flatnonzero(feasible_indices == best)[0])
    best_samples = values[:, best]
    return TerminalValue(
        "RQMC_POINT_ESTIMATE",
        float(policy_values[best]), best, int(Q3_POLICY_IDS[best]), policy_values,
        max(0.0, ev_perfect - float(policy_values[best])), len(uniforms), np.nan,
        float(np.mean(ties[:, local_best] / ties.sum(axis=1))),
        float(np.mean(feasible_values.max(axis=1) - best_samples)),
        float(np.mean(best_samples < 0)),
        tuple(float(x) for x in np.quantile(best_samples, [.05, .5, .95])),
    )


def _weighted_quantiles(values: np.ndarray, weights: np.ndarray, probabilities: list[float]) -> np.ndarray:
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cumulative = np.cumsum(weights) / weights.sum()
    return np.interp(probabilities, cumulative, values)
