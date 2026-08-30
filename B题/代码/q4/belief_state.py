"""Q4 Beta-Bernoulli belief state 与抽样证据校验。"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


ALLOWED_RECORD_FIELDS = {
    "N", "K", "conditioning", "stopping_rule", "t_opt",
    "sample_test_cost", "sample_preparation_cost", "sample_consumption_cost",
    "destructive", "sampled_object", "batch_id",
}


@dataclass(frozen=True)
class BeliefState:
    names: tuple[str, ...]
    alpha: tuple[float, ...]
    beta: tuple[float, ...]

    @property
    def means(self) -> np.ndarray:
        a, b = np.asarray(self.alpha), np.asarray(self.beta)
        return a / (a + b)

    def update(self, index: int, defective: bool) -> "BeliefState":
        a, b = list(self.alpha), list(self.beta)
        if defective:
            a[index] += 1
        else:
            b[index] += 1
        return BeliefState(self.names, tuple(a), tuple(b))


def validate_records(records: dict, conditioning: dict[str, str], label: str,
                     default_plan: str) -> None:
    if set(records) != set(conditioning):
        raise ValueError(f"INVALID_DATA: {label} parameter set mismatch")
    for name, expected in conditioning.items():
        item = records[name]
        if set(item) - ALLOWED_RECORD_FIELDS:
            raise ValueError(f"INVALID_DATA: {label}.{name} contains unknown fields")
        if not isinstance(item.get("N"), int) or not isinstance(item.get("K"), int):
            raise ValueError(f"INVALID_DATA: {label}.{name} requires integer N,K")
        if item["N"] <= 0 or not 0 <= item["K"] <= item["N"]:
            raise ValueError(f"INVALID_DATA: {label}.{name} requires N>0 and 0<=K<=N")
        if item.get("conditioning") != expected:
            raise ValueError(f"INVALID_CONDITIONING: {label}.{name} must be {expected}")
        rule = item.get("stopping_rule", default_plan)
        if rule not in {"fixed_n", "sequential_cs"}:
            raise ValueError(f"INVALID_DATA: {label}.{name} invalid stopping_rule")
        if rule == "sequential_cs" and (not isinstance(item.get("t_opt"), int) or item["t_opt"] <= 0):
            raise ValueError(f"INVALID_ADAPTIVE_SAMPLING_LOG: {label}.{name} missing t_opt")
        for key in ("sample_test_cost", "sample_preparation_cost", "sample_consumption_cost"):
            value = item.get(key, 0.0)
            if not isinstance(value, (int, float)) or not np.isfinite(value) or value < 0:
                raise ValueError(f"INVALID_DATA: {label}.{name}.{key} must be finite and nonnegative")
        if "sample_test_cost" not in item:
            raise ValueError(f"INVALID_DATA: {label}.{name} missing sample_test_cost")


def from_records(records: dict, names: tuple[str, ...], prior: tuple[float, float]) -> BeliefState:
    a0, b0 = prior
    if a0 <= 0 or b0 <= 0:
        raise ValueError("BELIEF_STATE_INVALID: prior parameters must be positive")
    alpha = tuple(a0 + records[name]["K"] for name in names)
    beta = tuple(b0 + records[name]["N"] - records[name]["K"] for name in names)
    return BeliefState(names, alpha, beta)


def marginal_cost(record: dict) -> float:
    return float(sum(record.get(key, 0.0) for key in (
        "sample_test_cost", "sample_preparation_cost", "sample_consumption_cost"
    )))


def past_sampling_cost(records: dict) -> float:
    return float(sum(item["N"] * marginal_cost(item) for item in records.values()))
