"""Q4-A3/Q3：成本敏感 KG 与通用有限深度 rollout。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import qmc, t as student_t

from .belief_state import BeliefState
from .terminal_value import TerminalValue, q3_terminal_value


@dataclass
class KGResult:
    status: str
    stop_value: float
    action: str
    action_values: dict[str, float]
    net_kg: dict[str, float]
    action_se: dict[str, float]
    net_ci: dict[str, tuple[float, float]]
    terminal: TerminalValue
    draws_per_scramble: int
    scrambles: int
    seed: int
    confirm_seed: int


def sobol_uniforms(dimension: int, draws: int, seed: int) -> np.ndarray:
    power = int(np.ceil(np.log2(draws)))
    values = qmc.Sobol(dimension, scramble=True, seed=seed).random_base2(power)
    return np.clip(values[:draws], 1e-12, 1 - 1e-12)


def _scramble_action_values(belief: BeliefState, costs: tuple[float, ...],
                            draws: int, scrambles: int, seed: int):
    action_names = ("STOP", *belief.names)
    matrix = np.empty((scrambles, len(action_names)))
    uniforms_all = []
    for r in range(scrambles):
        uniforms = sobol_uniforms(len(belief.names), draws, seed + 104729 * r)
        uniforms_all.append(uniforms)
        terminal = q3_terminal_value(belief, uniforms)
        matrix[r, 0] = terminal.value
        for j in range(len(belief.names)):
            defective = q3_terminal_value(belief.update(j, True), uniforms)
            good = q3_terminal_value(belief.update(j, False), uniforms)
            mu = belief.means[j]
            matrix[r, j + 1] = -costs[j] + mu * defective.value + (1 - mu) * good.value
    terminal = q3_terminal_value(belief, np.vstack(uniforms_all))
    return action_names, matrix, terminal


def q3_knowledge_gradient(belief: BeliefState, costs: tuple[float, ...],
                          draws_per_scramble: int, scrambles: int,
                          seed: int, confirm_seed: int,
                          confidence: float, tolerance: float) -> KGResult:
    if scrambles < 2:
        raise ValueError("INVALID_DATA: at least two scrambles are required")
    names, exploration, _ = _scramble_action_values(
        belief, costs, draws_per_scramble, scrambles, seed)
    names2, confirmation, terminal = _scramble_action_values(
        belief, costs, draws_per_scramble, scrambles, confirm_seed)
    if names != names2:
        raise RuntimeError("MC_NOT_CONVERGED: action order changed")

    explore_mean = exploration.mean(axis=0)
    selected = int(np.argmax(explore_mean))
    mean = confirmation.mean(axis=0)
    se = confirmation.std(axis=0, ddof=1) / np.sqrt(scrambles)
    critical = float(student_t.ppf((1 + confidence) / 2, scrambles - 1))
    stop = confirmation[:, 0]
    net_samples = confirmation[:, 1:] - stop[:, None]
    net_mean = net_samples.mean(axis=0)
    net_se = net_samples.std(axis=0, ddof=1) / np.sqrt(scrambles)
    lower = net_mean - critical * net_se
    upper = net_mean + critical * net_se

    actions = dict(zip(names, map(float, mean)))
    action_se = dict(zip(names, map(float, se)))
    net = dict(zip(belief.names, map(float, net_mean)))
    net_ci = {name: (float(lower[j]), float(upper[j]))
              for j, name in enumerate(belief.names)}
    confirm_selected = int(np.argmax(mean))
    if np.max(upper) <= 0:
        action, status = "STOP", "STOP_NO_POSITIVE_NET_VOI"
    elif selected == confirm_selected and selected > 0 and lower[selected - 1] > 0:
        competitors = confirmation[:, selected, None] - np.delete(confirmation, selected, axis=1)
        lead_lower = competitors.mean(axis=0) - critical * competitors.std(axis=0, ddof=1) / np.sqrt(scrambles)
        if np.min(lead_lower) > -tolerance:
            action, status = names[selected], "SUCCESS_VOI_KG_MYOPIC"
        else:
            action, status = "AMBIGUOUS", "VOI_MC_NOT_CONVERGED"
    else:
        action, status = "AMBIGUOUS", "VOI_MC_NOT_CONVERGED"
    return KGResult(status, terminal.value, action, actions, net, action_se,
                    net_ci, terminal, draws_per_scramble, scrambles, seed, confirm_seed)


def rollout_with_oracle(initial_state, first_actions, horizon, paths, seed,
                        predictive_probability, update_state, terminal_value,
                        base_action, action_cost):
    """通用 CRN rollout；小问题单测和资源允许的 Q3 深度扩展共用。"""
    rng = np.random.default_rng(seed)
    base_uniforms = rng.random((paths, horizon))
    values = {}
    for first in first_actions:
        totals = np.zeros(paths)
        for path in range(paths):
            state, action = initial_state, first
            for depth in range(horizon):
                if action == "STOP":
                    break
                totals[path] -= action_cost(state, action)
                defective = base_uniforms[path, depth] < predictive_probability(state, action)
                state = update_state(state, action, defective)
                action = base_action(state) if depth + 1 < horizon else "STOP"
            totals[path] += terminal_value(state)
        values[first] = {
            "mean": float(totals.mean()),
            "se": float(totals.std(ddof=1) / np.sqrt(paths)) if paths > 1 else np.nan,
        }
    return values
