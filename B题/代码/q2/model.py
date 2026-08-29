"""Q2 吸收 Markov 奖励模型。"""

from __future__ import annotations

from collections import deque
from typing import NamedTuple

import mpmath as mp
import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import splu


MISSING, BAD, GOOD = -1, 0, 1
INFO_MISSING, UNKNOWN, KNOWN_GOOD = "M", "U", "G"
SRC_MISSING, NEW, RECOVERED = "M", "N", "R"

COMPONENTS = [
    "purchase_1", "purchase_2", "inspection_1", "inspection_2", "assembly",
    "product_inspection", "disassembly", "replacement_loss",
]
EVENTS = [
    "expected_purchases_1", "expected_purchases_2", "expected_inspections_1",
    "expected_inspections_2", "expected_product_inspections", "expected_assemblies",
    "expected_disassemblies", "expected_replacements",
]


class State(NamedTuple):
    phase: str
    z1: int
    z2: int
    k1: str
    k2: str
    o1: str
    o2: str


START = State("prepare", MISSING, MISSING, INFO_MISSING, INFO_MISSING, SRC_MISSING, SRC_MISSING)


def _blank_rewards():
    return dict.fromkeys(COMPONENTS, 0.0), dict.fromkeys(EVENTS, 0.0)


def _positive(items):
    return [(state, probability) for state, probability in items if probability > 0.0]


def state_transitions(state, policy, case, recovery_mode="physical_retention"):
    """返回次态概率、成功吸收概率和本状态的成本/事件。"""
    x1, x2, y, z = policy
    costs, events = _blank_rewards()

    if state.phase == "prepare":
        outcomes1 = [(state.z1, state.k1, state.o1, 1.0)]
        outcomes2 = [(state.z2, state.k2, state.o2, 1.0)]
        if state.z1 == MISSING:
            costs["purchase_1"] = case["buy1"]
            events["expected_purchases_1"] = 1.0
            outcomes1 = [(GOOD, UNKNOWN, NEW, 1 - case["p1"]), (BAD, UNKNOWN, NEW, case["p1"])]
        if state.z2 == MISSING:
            costs["purchase_2"] = case["buy2"]
            events["expected_purchases_2"] = 1.0
            outcomes2 = [(GOOD, UNKNOWN, NEW, 1 - case["p2"]), (BAD, UNKNOWN, NEW, case["p2"])]
        transitions = [
            (State("inspect1", a, b, ka, kb, oa, ob), pa * pb)
            for a, ka, oa, pa in outcomes1 for b, kb, ob, pb in outcomes2
        ]
        return _positive(transitions), 0.0, costs, events

    if state.phase == "inspect1":
        if not x1 or state.k1 == KNOWN_GOOD:
            return [(state._replace(phase="inspect2"), 1.0)], 0.0, costs, events
        costs["inspection_1"] = case["test1"]
        events["expected_inspections_1"] = 1.0
        if state.z1 == BAD:
            nxt = State("prepare", MISSING, state.z2, INFO_MISSING, state.k2, SRC_MISSING, state.o2)
        else:
            nxt = state._replace(phase="inspect2", k1=KNOWN_GOOD)
        return [(nxt, 1.0)], 0.0, costs, events

    if state.phase == "inspect2":
        if not x2 or state.k2 == KNOWN_GOOD:
            return [(state._replace(phase="assemble"), 1.0)], 0.0, costs, events
        costs["inspection_2"] = case["test2"]
        events["expected_inspections_2"] = 1.0
        if state.z2 == BAD:
            nxt = State("prepare", state.z1, MISSING, state.k1, INFO_MISSING, state.o1, SRC_MISSING)
        else:
            nxt = state._replace(phase="assemble", k2=KNOWN_GOOD)
        return [(nxt, 1.0)], 0.0, costs, events

    if state.phase == "assemble":
        costs["assembly"] = case["assembly"]
        events["expected_assemblies"] = 1.0
        good_probability = (1 - case["pf"]) if state.z1 == state.z2 == GOOD else 0.0
        bad_state = state._replace(phase="known_bad")
        if y:
            costs["product_inspection"] = case["test_product"]
            events["expected_product_inspections"] = 1.0
        else:
            costs["replacement_loss"] = (1 - good_probability) * case["replacement"]
            events["expected_replacements"] = 1 - good_probability
        return _positive([(bad_state, 1 - good_probability)]), good_probability, costs, events

    if state.phase == "known_bad":
        if not z:
            return [(START, 1.0)], 0.0, costs, events
        costs["disassembly"] = case["disassembly"]
        events["expected_disassemblies"] = 1.0
        if recovery_mode == "physical_retention":
            nxt = State("inspect1", state.z1, state.z2, UNKNOWN, UNKNOWN, RECOVERED, RECOVERED)
            return [(nxt, 1.0)], 0.0, costs, events
        if recovery_mode == "quality_reset":
            transitions = [
                (State("inspect1", a, b, UNKNOWN, UNKNOWN, RECOVERED, RECOVERED), pa * pb)
                for a, pa in ((GOOD, 1 - case["p1"]), (BAD, case["p1"]))
                for b, pb in ((GOOD, 1 - case["p2"]), (BAD, case["p2"]))
            ]
            return _positive(transitions), 0.0, costs, events
        raise ValueError(f"未知拆解回用模式: {recovery_mode}")

    raise ValueError(f"未知状态: {state}")


def build_chain(policy, case, recovery_mode="physical_retention"):
    states, index, queue = [START], {START: 0}, deque([START])
    raw = {}
    while queue:
        state = queue.popleft()
        item = state_transitions(state, policy, case, recovery_mode)
        raw[state] = item
        for nxt, probability in item[0]:
            if probability > 0.0 and nxt not in index:
                index[nxt] = len(states)
                states.append(nxt)
                queue.append(nxt)

    n = len(states)
    p = np.zeros((n, n))
    success = np.zeros(n)
    rewards = np.zeros((n, len(COMPONENTS) + len(EVENTS)))
    edges = []
    for state, i in index.items():
        transitions, success_probability, costs, events = raw[state]
        success[i] = success_probability
        rewards[i] = [costs[name] for name in COMPONENTS] + [events[name] for name in EVENTS]
        for nxt, probability in transitions:
            j = index[nxt]
            p[i, j] += probability
            edges.append((i, j, probability))
    return states, p, success, rewards, edges


def closed_transient_classes(p, success):
    """用正概率边构图，不用数值容差改写图结构。"""
    n = len(p)
    graph = [[j for j in range(n) if p[i, j] > 0.0] for i in range(n)]
    reverse = [[i for i in range(n) if p[i, j] > 0.0] for j in range(n)]
    seen, order = set(), []

    def visit(i):
        seen.add(i)
        for j in graph[i]:
            if j not in seen:
                visit(j)
        order.append(i)

    for i in range(n):
        if i not in seen:
            visit(i)
    seen, groups = set(), []

    def collect(i, group):
        seen.add(i)
        group.append(i)
        for j in reverse[i]:
            if j not in seen:
                collect(j, group)

    for root in reversed(order):
        if root in seen:
            continue
        group = []
        collect(root, group)
        inside = set(group)
        if all(success[i] == 0.0 and all(j in inside for j in graph[i]) for i in group):
            groups.append(group)
    return groups


def _spectral_radius_mp(p, digits):
    mp.mp.dps = digits
    values = mp.eig(mp.matrix(p.tolist()), left=False, right=False)
    return float(max(abs(value) for value in values))


def _solve(a, rhs, config):
    lu = splu(csc_matrix(a))
    values = lu.solve(rhs)
    for _ in range(2):
        correction = lu.solve(rhs - a @ values)
        values += correction
        if np.linalg.norm(correction, ord=np.inf) <= 1e-14 * max(1.0, np.linalg.norm(values, ord=np.inf)):
            break
    denominator = np.linalg.norm(a, ord=np.inf) * np.linalg.norm(values, ord=np.inf) + np.linalg.norm(rhs, ord=np.inf)
    residual = float(np.linalg.norm(a @ values - rhs, ord=np.inf) / max(denominator, np.finfo(float).tiny))
    return values, residual


def evaluate_policy(policy, case, config, recovery_mode="physical_retention", include_graph=False):
    states, p, success, rewards, edges = build_chain(policy, case, recovery_mode)
    row_error = float(np.max(np.abs(p.sum(axis=1) + success - 1)))
    rho = float(max(abs(np.linalg.eigvals(p)))) if len(p) else 0.0
    margin = 1.0 - rho
    base = {
        "case": case["case"], "x1": policy[0], "x2": policy[1], "y": policy[2], "z": policy[3],
        "n_states": len(states), "n_edges": len(edges), "row_sum_error": row_error,
        "spectral_radius": rho, "absorption_margin": margin, "status": "SUCCESS_EXACT",
        "closed_class_count": 0,
    }
    tol = config["probability_tolerance"]
    if np.any(p < 0.0) or np.any(success < 0.0) or row_error > tol:
        base["status"] = "INVALID_PROBABILITY"
    else:
        closed = closed_transient_classes(p, success)
        if closed:
            base["status"] = "NON_ABSORBING"
            base["closed_class_count"] = len(closed)
        elif margin <= config["near_absorption_margin"]:
            base["status"] = "NEAR_NONABSORBING"
            base["spectral_radius_high_precision"] = _spectral_radius_mp(p, config["high_precision_digits"])

    if base["status"] not in {"SUCCESS_EXACT", "NEAR_NONABSORBING"}:
        if include_graph:
            base["_graph"] = (states, p, success, edges)
        return base

    a = np.eye(len(states)) - p
    rhs = np.column_stack([rewards, success])
    base["condition_number"] = float(np.linalg.cond(a))
    base["condition_warning"] = base["condition_number"] > config["condition_warning"]
    try:
        values, residual = _solve(a, rhs, config)
    except (RuntimeError, ValueError):
        base["status"] = "ILL_CONDITIONED"
        return base
    base["linear_residual"] = residual
    if residual > tol or abs(values[0, -1] - 1.0) > tol:
        base["status"] = "ILL_CONDITIONED"
        return base
    for name, value in zip(COMPONENTS, values[0, :len(COMPONENTS)]):
        base[f"cost_{name}"] = 0.0 if abs(value) < 1e-14 else float(value)
    for name, value in zip(EVENTS, values[0, len(COMPONENTS):-1]):
        base[name] = 0.0 if abs(value) < 1e-14 else float(value)
    base["expected_total_cost"] = float(values[0, :len(COMPONENTS)].sum())
    base["expected_profit"] = float(case["price"] - base["expected_total_cost"])
    base["success_probability"] = float(values[0, -1])
    base["factory_defect_rate"] = 0.0 if policy[2] else base["expected_replacements"] / (1 + base["expected_replacements"])
    base["exchange_rate"] = base["expected_replacements"]
    if include_graph:
        base["_graph"] = (states, p, success, edges)
    return base
