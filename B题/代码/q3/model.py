"""Q3 装配树局部状态核与固定策略评价。"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import mpmath as mp
import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import splu

try:
    from component_state import (
        INFO_MISSING, KNOWN_GOOD, MISSING, SRC_MISSING, UNKNOWN,
        closed_transient_classes, inspect_component, positive_transitions,
        purchase_options,
    )
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from component_state import (
        INFO_MISSING, KNOWN_GOOD, MISSING, SRC_MISSING, UNKNOWN,
        closed_transient_classes, inspect_component, positive_transitions,
        purchase_options,
    )


HERE = Path(__file__).resolve().parent
RAW = json.loads((HERE / "table2.json").read_text(encoding="utf-8"))
CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
LEAVES = {int(i): (x["defect"], x["purchase"], x["inspection"]) for i, x in RAW["leaves"].items()}
NODES = {
    name: (tuple(x["children"]), x["defect"], x["assembly"], x["inspection"], x["disassembly"])
    for name, x in RAW["nodes"].items()
}
PRICE, REPLACEMENT = RAW["price"], RAW["replacement"]

COSTS = [
    "purchase", "part_inspection", "semi_inspection", "final_inspection",
    "semi_assembly", "final_assembly", "semi_disassembly", "final_disassembly",
    "replacement_loss",
]
EVENTS = [
    "expected_part_purchases", "expected_part_inspections", "expected_semi_inspections",
    "expected_final_inspections", "expected_semi_assemblies", "expected_final_assemblies",
    "expected_semi_disassemblies", "expected_final_disassemblies", "expected_replacements",
] + [f"expected_part_purchases_{i}" for i in range(1, 9)] \
  + [f"expected_part_inspections_{i}" for i in range(1, 9)] \
  + [f"expected_part_scraps_{i}" for i in range(1, 9)] \
  + [f"expected_semi_assemblies_{i}" for i in range(1, 4)] \
  + [f"expected_semi_disassemblies_{i}" for i in range(1, 4)] \
  + [f"expected_semi_scraps_{i}" for i in range(1, 4)] \
  + ["expected_final_scraps"] \
  + [f"expected_consume_part_{i}" for i in range(1, 9)] \
  + [f"expected_return_part_{i}" for i in range(1, 9)] \
  + [f"expected_consume_semi_{i}" for i in range(1, 4)] \
  + [f"expected_return_semi_{i}" for i in range(1, 4)]


class BatchState(NamedTuple):
    phase: int
    quality: tuple[int, ...]
    info: tuple[str, ...]
    source: tuple[str, ...]


@dataclass
class Kernel:
    good: float
    reward: np.ndarray
    spectral_radius: float = 0.0
    condition_number: float = 1.0
    residual: float = 0.0
    equations: int = 0
    status: str = "SUCCESS_EXACT"
    high_precision_radius: float | None = None


class KernelFailure(Exception):
    def __init__(self, status, **diagnostics):
        super().__init__(status)
        self.status = status
        self.diagnostics = diagnostics


KERNEL_CACHE, BATCH_CACHE, KERNEL_AUDIT, BATCH_AUDIT = {}, {}, {}, {}


def zero():
    return np.zeros(len(COSTS) + len(EVENTS))


def ci(name):
    return COSTS.index(name)


def ei(name):
    return len(COSTS) + EVENTS.index(name)


def decode(strategy_id):
    bits = tuple((strategy_id >> j) & 1 for j in range(16))
    return bits, bits[:8], bits[8:11], bits[11], bits[12:15], bits[15]


def _radius_mp(p):
    mp.mp.dps = CONFIG["high_precision_digits"]
    values = mp.eig(mp.matrix(p.tolist()), left=False, right=False)
    return float(max(abs(value) for value in values))


def _solve_matrix(p, rhs, terminal):
    if closed_transient_classes(p, terminal):
        raise KernelFailure("NON_ABSORBING", spectral_radius=1.0, absorption_margin=0.0)
    rho = float(max(abs(np.linalg.eigvals(p)))) if len(p) else 0.0
    margin = 1 - rho
    status, hp = "SUCCESS_EXACT", None
    if margin <= CONFIG["near_absorption_margin"]:
        status, hp = "NEAR_NONABSORBING", _radius_mp(p)
    a = np.eye(len(p)) - p
    condition = float(np.linalg.cond(a))
    try:
        lu = splu(csc_matrix(a))
        values = lu.solve(rhs)
        for _ in range(2):
            values += lu.solve(rhs - a @ values)
    except (RuntimeError, ValueError) as exc:
        raise KernelFailure("ILL_CONDITIONED", spectral_radius=rho, absorption_margin=margin) from exc
    denominator = np.linalg.norm(a, np.inf) * np.linalg.norm(values, np.inf) + np.linalg.norm(rhs, np.inf)
    residual = float(np.linalg.norm(a @ values - rhs, np.inf) / max(denominator, np.finfo(float).tiny))
    if residual > CONFIG["probability_tolerance"]:
        raise KernelFailure("ILL_CONDITIONED", spectral_radius=rho, absorption_margin=margin, residual=residual)
    return values, Kernel(0.0, zero(), rho, condition, residual, 1, status, hp)


def solve_loop(reward, repeat):
    if repeat >= 1.0:
        raise KernelFailure("NON_ABSORBING", spectral_radius=1.0, absorption_margin=0.0)
    margin = 1 - repeat
    status = "NEAR_NONABSORBING" if margin <= CONFIG["near_absorption_margin"] else "SUCCESS_EXACT"
    value = reward / margin
    residual = float(np.linalg.norm(margin * value - reward, np.inf) / (np.linalg.norm(reward, np.inf) + 1))
    if residual > CONFIG["probability_tolerance"]:
        raise KernelFailure("ILL_CONDITIONED", spectral_radius=repeat, absorption_margin=margin, residual=residual)
    return value, Kernel(0.0, zero(), repeat, 1 / margin, residual, 1, status, repeat if status != "SUCCESS_EXACT" else None)


def _combine(kernels):
    result = Kernel(0.0, zero())
    for item in kernels:
        if item.status == "NEAR_NONABSORBING":
            result.status = item.status
        result.spectral_radius = max(result.spectral_radius, item.spectral_radius)
        result.condition_number = max(result.condition_number, item.condition_number)
        result.residual = max(result.residual, item.residual)
        result.equations += item.equations
        if item.high_precision_radius is not None:
            result.high_precision_radius = max(result.high_precision_radius or 0.0, item.high_precision_radius)
    return result


def input_batch(ids, inspections, leaves=LEAVES, cache=None):
    """补购仅重检未知件，保留件的 known-good 信息。"""
    cache = BATCH_CACHE if cache is None else cache
    key = (tuple(ids), tuple(inspections))
    if key in cache:
        return cache[key]
    n = len(ids)
    start = BatchState(0, (MISSING,) * n, (INFO_MISSING,) * n, (SRC_MISSING,) * n)
    states, index, queue, raw = [start], {start: 0}, deque([start]), {}
    while queue:
        state = queue.popleft()
        reward, transitions, terminal, good = zero(), [], 0.0, 0.0
        if state.phase == 0:
            options = []
            for j in range(n):
                if state.quality[j] == MISSING:
                    leaf_id = ids[j]
                    reward[ci("purchase")] += leaves[leaf_id][1]
                    reward[ei("expected_part_purchases")] += 1
                    reward[ei(f"expected_part_purchases_{leaf_id}")] += 1
                options.append(purchase_options(state.quality[j], state.info[j], state.source[j], leaves[ids[j]][0]))
            combos = [([], 1.0)]
            for option in options:
                combos = [(prefix + [item], probability * p) for prefix, probability in combos for item, p in option]
            for combo, probability in combos:
                q, k, o = zip(*combo)
                transitions.append((BatchState(1, tuple(q), tuple(k), tuple(o)), probability))
        else:
            j, leaf_id = state.phase - 1, ids[state.phase - 1]
            charged, rejected, info = inspect_component(state.quality[j], state.info[j], inspections[j])
            if charged:
                reward[ci("part_inspection")] += leaves[leaf_id][2]
                reward[ei("expected_part_inspections")] += 1
                reward[ei(f"expected_part_inspections_{leaf_id}")] += 1
            if rejected:
                reward[ei(f"expected_part_scraps_{leaf_id}")] += 1
                q, k, o = list(state.quality), list(state.info), list(state.source)
                q[j], k[j], o[j] = MISSING, INFO_MISSING, SRC_MISSING
                transitions = [(BatchState(0, tuple(q), tuple(k), tuple(o)), 1.0)]
            elif state.phase == n:
                terminal, good = 1.0, float(all(q == 1 for q in state.quality))
            else:
                k = list(state.info)
                k[j] = info
                transitions = [(BatchState(state.phase + 1, state.quality, tuple(k), state.source), 1.0)]
        transitions = positive_transitions(transitions)
        raw[state] = transitions, terminal, good, reward
        for nxt, probability in transitions:
            if probability > 0.0 and nxt not in index:
                index[nxt] = len(states)
                states.append(nxt)
                queue.append(nxt)

    size = len(states)
    p, terminal, quality, rewards = np.zeros((size, size)), np.zeros(size), np.zeros(size), np.zeros((size, len(zero())))
    for state, i in index.items():
        transitions, terminal[i], quality[i], rewards[i] = raw[state]
        for nxt, probability in transitions:
            p[i, index[nxt]] += probability
    if np.max(np.abs(p.sum(axis=1) + terminal - 1)) > CONFIG["probability_tolerance"]:
        raise KernelFailure("INVALID_PROBABILITY")
    values, diagnostics = _solve_matrix(p, np.column_stack([rewards, quality, terminal]), terminal)
    if abs(values[0, -1] - 1) > CONFIG["probability_tolerance"]:
        raise KernelFailure("ILL_CONDITIONED", residual=abs(values[0, -1] - 1))
    result = Kernel(float(values[0, -2]), values[0, :-2], diagnostics.spectral_radius,
                    diagnostics.condition_number, diagnostics.residual, diagnostics.equations,
                    diagnostics.status, diagnostics.high_precision_radius)
    cache[key] = result
    BATCH_AUDIT[str(key)] = {
        "ids": list(ids), "inspections": list(inspections), "n_states": size,
        "spectral_radius": result.spectral_radius, "condition_number": result.condition_number,
        "residual": result.residual, "status": result.status,
    }
    return result


def _record_assembly(reward, name, children, cost):
    if name == "root":
        reward[ci("final_assembly")] += cost
        reward[ei("expected_final_assemblies")] += 1
        for i in range(1, 4):
            reward[ei(f"expected_consume_semi_{i}")] += 1
    else:
        i = int(name[1])
        reward[ci("semi_assembly")] += cost
        reward[ei("expected_semi_assemblies")] += 1
        reward[ei(f"expected_semi_assemblies_{i}")] += 1
        for child in children:
            reward[ei(f"expected_consume_part_{child}")] += 1


def _record_disassembly(reward, name, children, cost):
    if name == "root":
        reward[ci("final_disassembly")] += cost
        reward[ei("expected_final_disassemblies")] += 1
        for i in range(1, 4):
            reward[ei(f"expected_return_semi_{i}")] += 1
    else:
        i = int(name[1])
        reward[ci("semi_disassembly")] += cost
        reward[ei("expected_semi_disassemblies")] += 1
        reward[ei(f"expected_semi_disassemblies_{i}")] += 1
        for child in children:
            reward[ei(f"expected_return_part_{child}")] += 1


def retest_children(children, policy, leaves=LEAVES, nodes=NODES):
    _, parts, semis, _, _, _ = policy
    reward = zero()
    for child in children:
        if isinstance(child, int) and parts[child - 1]:
            reward[ci("part_inspection")] += leaves[child][2]
            reward[ei("expected_part_inspections")] += 1
            reward[ei(f"expected_part_inspections_{child}")] += 1
        elif isinstance(child, str) and semis[int(child[1]) - 1]:
            reward[ci("semi_inspection")] += nodes[child][3]
            reward[ei("expected_semi_inspections")] += 1
    return reward


def node(name, policy, leaves=LEAVES, nodes=NODES, replacement=REPLACEMENT,
         kernel_cache=None, batch_cache=None, recovery_mode="physical_retention"):
    kernel_cache = KERNEL_CACHE if kernel_cache is None else kernel_cache
    batch_cache = BATCH_CACHE if batch_cache is None else batch_cache
    bits, parts, semis, yf, dis_semis, zf = policy
    if name != "root":
        i = int(name[1]) - 1
        start, stop = ((0, 3), (3, 6), (6, 8))[i]
        key = (CONFIG["kernel_schema_version"], recovery_mode, name, parts[start:stop], semis[i], dis_semis[i])
        if key in kernel_cache:
            return kernel_cache[key]
    children, defect, assembly, inspection, disassembly = nodes[name]
    root = name == "root"
    if all(isinstance(child, int) for child in children):
        child_kernels = [input_batch(children, [parts[c - 1] for c in children], leaves, batch_cache)]
    else:
        child_kernels = [
            node(child, policy, leaves, nodes, replacement, kernel_cache, batch_cache, recovery_mode)
            for child in children
        ]
    diagnostics = _combine(child_kernels)
    q = (1 - defect) * float(np.prod([item.good for item in child_kernels]))
    first = sum((item.reward for item in child_kernels), zero())
    _record_assembly(first, name, children, assembly)
    tested = yf if root else semis[int(name[1]) - 1]
    dismantle = zf if root else dis_semis[int(name[1]) - 1]
    all_good = all(abs(item.good - 1) <= CONFIG["probability_tolerance"] for item in child_kernels)

    if not tested and not (root and dismantle):
        result = Kernel(q, first, diagnostics.spectral_radius, diagnostics.condition_number,
                        diagnostics.residual, diagnostics.equations, diagnostics.status,
                        diagnostics.high_precision_radius)
    elif tested and not dismantle:
        first[ci("final_inspection" if root else "semi_inspection")] += inspection
        first[ei("expected_final_inspections" if root else "expected_semi_inspections")] += 1
        if root:
            first[ei("expected_final_scraps")] += 1 - q
        else:
            first[ei(f"expected_semi_scraps_{int(name[1])}")] += 1 - q
        value, loop = solve_loop(first, 1 - q)
        diagnostics = _combine([diagnostics, loop])
        result = Kernel(1.0, value, diagnostics.spectral_radius, diagnostics.condition_number,
                        diagnostics.residual, diagnostics.equations, diagnostics.status,
                        diagnostics.high_precision_radius)
    elif recovery_mode == "physical_retention":
        if not all_good:
            raise KernelFailure("NON_ABSORBING", spectral_radius=1.0, absorption_margin=0.0)
        cycle = zero()
        _record_assembly(cycle, name, children, assembly)
        if tested:
            cycle[ci("final_inspection" if root else "semi_inspection")] += inspection
            cycle[ei("expected_final_inspections" if root else "expected_semi_inspections")] += 1
        if root and not tested:
            cycle[ci("replacement_loss")] += defect * replacement
            cycle[ei("expected_replacements")] += defect
        dismantled = zero()
        _record_disassembly(dismantled, name, children, disassembly)
        cycle += defect * (dismantled + retest_children(children, policy, leaves, nodes))
        value, loop = solve_loop(cycle, defect)
        diagnostics = _combine([diagnostics, loop])
        result = Kernel(1.0, sum((item.reward for item in child_kernels), zero()) + value,
                        diagnostics.spectral_radius, diagnostics.condition_number, diagnostics.residual,
                        diagnostics.equations, diagnostics.status, diagnostics.high_precision_radius)
    elif recovery_mode == "quality_reset_rebuild":
        attempt = first.copy()
        if tested:
            attempt[ci("final_inspection" if root else "semi_inspection")] += inspection
            attempt[ei("expected_final_inspections" if root else "expected_semi_inspections")] += 1
        disassembled = zero()
        _record_disassembly(disassembled, name, children, disassembly)
        attempt += (1 - q) * disassembled
        if root and not tested:
            attempt[ci("replacement_loss")] += (1 - q) * replacement
            attempt[ei("expected_replacements")] += 1 - q
        value, loop = solve_loop(attempt, 1 - q)
        diagnostics = _combine([diagnostics, loop])
        result = Kernel(1.0, value, diagnostics.spectral_radius, diagnostics.condition_number,
                        diagnostics.residual, diagnostics.equations, diagnostics.status,
                        diagnostics.high_precision_radius)
    else:
        raise ValueError(f"未知回收模式: {recovery_mode}")
    if name != "root":
        kernel_cache[key] = result
        KERNEL_AUDIT[str(key)] = {
            "node": name, "good_probability": result.good, "spectral_radius": result.spectral_radius,
            "condition_number": result.condition_number, "residual": result.residual,
            "status": result.status,
        }
    return result


def q3_nominal_parameters():
    return {**{f"part_{i}": LEAVES[i][0] for i in range(1, 9)},
            **{f"semi_{i}": NODES[f"s{i}"][1] for i in range(1, 4)}, "final": NODES["root"][1]}


def _config_from_parameters(parameters):
    expected = {f"part_{i}" for i in range(1, 9)} | {"semi_1", "semi_2", "semi_3", "final"}
    if set(parameters) != expected or any(not 0 <= float(value) <= 1 for value in parameters.values()):
        raise ValueError("Q3 参数必须恰为 12 个 [0,1] 缺陷率")
    leaves = {i: (float(parameters[f"part_{i}"]), buy, test) for i, (_, buy, test) in LEAVES.items()}
    nodes = {
        name: (children, float(parameters[f"semi_{int(name[1])}"]) if name != "root" else float(parameters["final"]), assembly, inspection, disassembly)
        for name, (children, _, assembly, inspection, disassembly) in NODES.items()
    }
    return leaves, nodes


def _base_row(strategy_id):
    bits, parts, semis, yf, dis_semis, zf = decode(strategy_id)
    return {
        "strategy_id": strategy_id, "strategy_bits": "".join(map(str, bits)),
        **{f"x{i}": parts[i - 1] for i in range(1, 9)},
        **{f"y{i}": semis[i - 1] for i in range(1, 4)}, "yf": yf,
        **{f"z{i}": dis_semis[i - 1] for i in range(1, 4)}, "zf": zf,
    }


def evaluate(strategy_id, parameters=None, _context=None, recovery_mode="physical_retention"):
    row = {**_base_row(strategy_id), "status": "SUCCESS_EXACT"}
    bits, parts, semis, yf, dis_semis, zf = decode(strategy_id)
    if _context is not None:
        leaves, nodes, replacement, kernel_cache, batch_cache = _context
    else:
        leaves, nodes = (LEAVES, NODES) if parameters is None else _config_from_parameters(parameters)
        replacement = REPLACEMENT
        kernel_cache, batch_cache = (KERNEL_CACHE, BATCH_CACHE) if parameters is None else ({}, {})
    one_pass = float(np.prod([1 - leaves[i][0] for i in leaves]) * np.prod([1 - nodes[name][1] for name in nodes]))
    try:
        result = node("root", (bits, parts, semis, yf, dis_semis, zf), leaves, nodes,
                      replacement, kernel_cache, batch_cache, recovery_mode)
        if not yf and not zf:
            result.reward[ci("replacement_loss")] += (1 - result.good) * replacement
            result.reward[ei("expected_replacements")] += 1 - result.good
            result.reward[ei("expected_final_scraps")] += 1 - result.good
            value, loop = solve_loop(result.reward, 1 - result.good)
            diagnostics = _combine([result, loop])
            result = Kernel(1.0, value, diagnostics.spectral_radius, diagnostics.condition_number,
                            diagnostics.residual, diagnostics.equations, diagnostics.status,
                            diagnostics.high_precision_radius)
        row.update({
            "status": result.status, "local_loop_equations": result.equations,
            "spectral_radius": result.spectral_radius, "absorption_margin": 1 - result.spectral_radius,
            "max_condition_number": result.condition_number,
            "condition_warning": result.condition_number > CONFIG["condition_warning"],
            "max_local_equation_residual": result.residual,
        })
        if result.high_precision_radius is not None:
            row["spectral_radius_high_precision"] = result.high_precision_radius
        for name, value in zip(COSTS, result.reward[:len(COSTS)]):
            row[f"cost_{name}"] = 0.0 if abs(value) < 1e-14 else float(value)
        for name, value in zip(EVENTS, result.reward[len(COSTS):]):
            row[name] = 0.0 if abs(value) < 1e-14 else float(value)
        row["expected_total_cost"] = float(result.reward[:len(COSTS)].sum())
        row["expected_profit"] = PRICE - row["expected_total_cost"]
        row["factory_defect_rate"] = 0.0 if yf else row["expected_replacements"] / (1 + row["expected_replacements"])
    except KernelFailure as exc:
        row.update({"status": exc.status, **exc.diagnostics})
    row["one_pass_success_no_inspection"] = one_pass
    return row


def evaluate_q3_policy(parameters, strategy_id):
    return evaluate(strategy_id, parameters)


def make_q3_evaluator(parameters):
    leaves, nodes = _config_from_parameters(parameters)
    context = (leaves, nodes, REPLACEMENT, {}, {})
    return lambda strategy_id: evaluate(strategy_id, _context=context)
