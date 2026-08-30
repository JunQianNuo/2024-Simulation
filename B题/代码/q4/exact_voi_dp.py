"""Q4-A3/Q2：有限期记忆化价值信息动态规划。"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from .belief_state import BeliefState
from .terminal_value import TerminalValue, q2_terminal_value


@dataclass
class VoiResult:
    status: str
    value: float
    stop_value: float
    initial_action: str
    action_values: dict[str, float]
    state_count: int
    bellman_residual: float
    expected_samples: float
    sample_quantiles: dict[str, int]
    expected_allocation: dict[str, float]
    terminal_policy_probabilities: dict[str, float]
    nvsi: float
    evpi: float
    state_rows: list[dict]


class Q2VoiDP:
    def __init__(self, case: dict, initial: BeliefState, costs: tuple[float, ...],
                 horizon: int, orders: list[int], tolerance: float,
                 max_states: int, caps: tuple[int, ...] | None = None):
        self.case, self.initial, self.costs = case, initial, costs
        self.horizon, self.orders, self.tolerance = horizon, orders, tolerance
        self.max_states = max_states
        self.caps = caps or tuple([horizon] * len(initial.names))
        self.rows: dict[tuple, dict] = {}

    def belief(self, bad: tuple[int, ...], good: tuple[int, ...]) -> BeliefState:
        return BeliefState(self.initial.names,
                           tuple(a + x for a, x in zip(self.initial.alpha, bad)),
                           tuple(b + x for b, x in zip(self.initial.beta, good)))

    @lru_cache(maxsize=None)
    def terminal(self, bad: tuple[int, ...], good: tuple[int, ...]) -> TerminalValue:
        return q2_terminal_value(self.case, self.belief(bad, good), self.orders, self.tolerance)

    @lru_cache(maxsize=None)
    def value(self, bad: tuple[int, ...], good: tuple[int, ...], h: int) -> float:
        if self.value.cache_info().currsize > self.max_states:
            raise RuntimeError("VOI_DP_STATE_LIMIT")
        terminal = self.terminal(bad, good)
        stop = terminal.value
        actions = {"STOP": stop}
        if h > 0 and terminal.status == "VALUE_INTEGRATION_CONVERGED":
            belief = self.belief(bad, good)
            counts = tuple(x + y for x, y in zip(bad, good))
            for j, name in enumerate(belief.names):
                if counts[j] >= self.caps[j]:
                    continue
                bad_next = list(bad); bad_next[j] += 1
                good_next = list(good); good_next[j] += 1
                mu = belief.means[j]
                actions[name] = (-self.costs[j]
                                 + mu * self.value(tuple(bad_next), good, h - 1)
                                 + (1 - mu) * self.value(bad, tuple(good_next), h - 1))
        best_value = max(actions.values())
        tied = [name for name, value in actions.items() if best_value - value <= self.tolerance]
        action = "STOP" if "STOP" in tied else sorted(tied, key=lambda name: (self.costs[belief.names.index(name)], name))[0]
        self.rows[(bad, good, h)] = {
            "bad": bad, "good": good, "h_remaining": h,
            "stop_value": stop, "action": action, "value": best_value,
            "action_values": actions, "terminal_policy": terminal.best_label,
            "terminal_status": terminal.status,
            "bellman_residual": abs(best_value - max(actions.values())),
        }
        return best_value

    def forward_summary(self):
        zero = tuple([0] * len(self.initial.names))
        mass = {(zero, zero, self.horizon): 1.0}
        stop_by_count = defaultdict(float)
        allocation = np.zeros(len(self.initial.names))
        policies = defaultdict(float)
        while mass:
            next_mass = defaultdict(float)
            for (bad, good, h), probability in mass.items():
                self.value(bad, good, h)
                row = self.rows[(bad, good, h)]
                if row["action"] == "STOP":
                    used = self.horizon - h
                    stop_by_count[used] += probability
                    policies[str(row["terminal_policy"])] += probability
                    continue
                j = self.initial.names.index(row["action"])
                allocation[j] += probability
                mu = self.belief(bad, good).means[j]
                bad_next = list(bad); bad_next[j] += 1
                good_next = list(good); good_next[j] += 1
                next_mass[(tuple(bad_next), good, h - 1)] += probability * mu
                next_mass[(bad, tuple(good_next), h - 1)] += probability * (1 - mu)
            mass = dict(next_mass)
        counts = sorted(stop_by_count)
        cdf = np.cumsum([stop_by_count[count] for count in counts])
        quantiles = {f"P{q}": counts[int(np.searchsorted(cdf, q / 100))] for q in (50, 90, 99)}
        return sum(k * v for k, v in stop_by_count.items()), allocation, quantiles, policies

    def solve(self) -> VoiResult:
        zero = tuple([0] * len(self.initial.names))
        value = self.value(zero, zero, self.horizon)
        root = self.rows[(zero, zero, self.horizon)]
        expected, allocation, quantiles, policies = self.forward_summary()
        initial_terminal = self.terminal(zero, zero)
        residual = max(row["bellman_residual"] for row in self.rows.values())
        converged = all(row["terminal_status"] == "VALUE_INTEGRATION_CONVERGED"
                        for row in self.rows.values())
        return VoiResult(
            "SUCCESS_VOI_DP_TOL" if converged else "VALUE_INTEGRATION_NOT_CONVERGED",
            value, root["stop_value"], root["action"],
            root["action_values"], len(self.rows), residual, expected, quantiles,
            dict(zip(self.initial.names, map(float, allocation))), dict(policies),
            value - root["stop_value"], initial_terminal.evpi, list(self.rows.values()),
        )
