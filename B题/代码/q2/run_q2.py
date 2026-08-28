"""Q2-M2：吸收 Markov 奖励闭环利润优化的精确枚举。"""

from __future__ import annotations

import itertools
import json
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd


CASES = [
    {"case": 1, "p1": .10, "buy1": 4, "test1": 2, "p2": .10, "buy2": 18, "test2": 3, "pf": .10, "assembly": 6, "test_product": 3, "price": 56, "replacement": 6, "disassembly": 5},
    {"case": 2, "p1": .20, "buy1": 4, "test1": 2, "p2": .20, "buy2": 18, "test2": 3, "pf": .20, "assembly": 6, "test_product": 3, "price": 56, "replacement": 6, "disassembly": 5},
    {"case": 3, "p1": .10, "buy1": 4, "test1": 2, "p2": .10, "buy2": 18, "test2": 3, "pf": .10, "assembly": 6, "test_product": 3, "price": 56, "replacement": 30, "disassembly": 5},
    {"case": 4, "p1": .20, "buy1": 4, "test1": 1, "p2": .20, "buy2": 18, "test2": 1, "pf": .20, "assembly": 6, "test_product": 2, "price": 56, "replacement": 30, "disassembly": 5},
    {"case": 5, "p1": .10, "buy1": 4, "test1": 8, "p2": .20, "buy2": 18, "test2": 1, "pf": .10, "assembly": 6, "test_product": 2, "price": 56, "replacement": 10, "disassembly": 5},
    {"case": 6, "p1": .05, "buy1": 4, "test1": 2, "p2": .05, "buy2": 18, "test2": 3, "pf": .05, "assembly": 6, "test_product": 3, "price": 56, "replacement": 10, "disassembly": 40},
]

OUTDIR = Path(__file__).resolve().parent.parent / "results" / "q2"
COMPONENTS = ["purchase_1", "purchase_2", "inspection_1", "inspection_2", "assembly", "product_inspection", "disassembly", "replacement_loss"]
TOL = 1e-10


def state_transitions(state, policy, case):
    """返回下一状态概率、成功吸收概率和本状态发生的成本分项。"""
    phase, q1, q2, source1, source2 = state
    x1, x2, y, z = policy
    costs = dict.fromkeys(COMPONENTS, 0.0)

    if phase == "prepare":
        costs["purchase_1"] = case["buy1"] if q1 == -1 else 0.0
        costs["purchase_2"] = case["buy2"] if q2 == -1 else 0.0
        outcomes1 = [(q1, source1, 1.0)] if q1 != -1 else [(1, "N", 1 - case["p1"]), (0, "N", case["p1"])]
        outcomes2 = [(q2, source2, 1.0)] if q2 != -1 else [(1, "N", 1 - case["p2"]), (0, "N", case["p2"])]
        transitions = [(('inspect1', a, b, oa, ob), pa * pb) for a, oa, pa in outcomes1 for b, ob, pb in outcomes2]
        return transitions, 0.0, costs

    if phase == "inspect1":
        if not x1:
            return [(('inspect2', q1, q2, source1, source2), 1.0)], 0.0, costs
        costs["inspection_1"] = case["test1"]
        return ([(('prepare', -1, q2, "M", source2), 1.0)] if q1 == 0 else [(('inspect2', q1, q2, source1, source2), 1.0)]), 0.0, costs

    if phase == "inspect2":
        if not x2:
            return [(('assemble', q1, q2, source1, source2), 1.0)], 0.0, costs
        costs["inspection_2"] = case["test2"]
        return ([(('prepare', q1, -1, source1, "M"), 1.0)] if q2 == 0 else [(('assemble', q1, q2, source1, source2), 1.0)]), 0.0, costs

    if phase == "assemble":
        costs["assembly"] = case["assembly"]
        return [], 0.0, costs

    if phase == "known_bad":
        # 该状态表示成品真实不合格且企业已经知道；可来自成检或市场退回。
        if z:
            costs["disassembly"] = case["disassembly"]
            return [(('inspect1', q1, q2, "R", "R"), 1.0)], 0.0, costs
        return [(('prepare', -1, -1, "M", "M"), 1.0)], 0.0, costs

    raise RuntimeError(f"未知状态 {state}")


def build_chain(policy, case):
    """BFS 仅展开初始订单可达状态；产品好坏通过单独的市场/已知坏状态表达。"""
    start = ("prepare", -1, -1, "M", "M")
    states, index, queue = [start], {start: 0}, deque([start])
    raw = {}
    while queue:
        state = queue.popleft()
        transitions, success, costs = state_transitions(state, policy, case)
        if state[0] == "assemble":
            # 装配成功进入市场/成检；失败成为已知坏品（成检）或市场退回品。
            q1, q2, o1, o2 = state[1:]
            good = (1 - case["pf"]) if q1 == q2 == 1 else 0.0
            if policy[2]:
                costs["product_inspection"] = case["test_product"]
                transitions, success = [(('known_bad', q1, q2, o1, o2), 1 - good)], good
            else:
                # 未检成品先进入市场；坏品产生一次调换损失，再作为已知坏退回。
                costs["replacement_loss"] = (1 - good) * case["replacement"]
                transitions, success = [(('known_bad', q1, q2, o1, o2), 1 - good)], good
        raw[state] = (transitions, success, costs)
        for nxt, probability in transitions:
            if probability > 0 and nxt not in index:
                index[nxt] = len(states)
                states.append(nxt)
                queue.append(nxt)

    p = np.zeros((len(states), len(states)))
    success = np.zeros(len(states))
    rewards = np.zeros((len(states), len(COMPONENTS)))
    for state, i in index.items():
        transitions, success_probability, costs = raw[state]
        success[i] = success_probability
        rewards[i] = [costs[name] for name in COMPONENTS]
        for nxt, probability in transitions:
            p[i, index[nxt]] += probability
    return states, p, success, rewards


def has_closed_transient_class(p, success):
    """Kosaraju 图检查：存在无成功泄漏的可达闭 SCC 即不可吸收。"""
    n = len(p)
    graph = [[j for j in range(n) if p[i, j] > TOL] for i in range(n)]
    reverse = [[i for i in range(n) if p[i, j] > TOL] for j in range(n)]
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
    seen = set()
    def collect(i, group):
        seen.add(i); group.append(i)
        for j in reverse[i]:
            if j not in seen:
                collect(j, group)
    for root in reversed(order):
        if root in seen:
            continue
        group = []
        collect(root, group)
        inside = set(group)
        if all(success[i] <= TOL and all(j in inside for j in graph[i]) for i in group):
            return True
    return False


def evaluate_policy(policy, case):
    states, p, success, rewards = build_chain(policy, case)
    row_sums = p.sum(axis=1) + success
    base = {"case": case["case"], "x1": policy[0], "x2": policy[1], "y": policy[2], "z": policy[3], "n_states": len(states), "row_sum_error": float(np.max(np.abs(row_sums - 1))), "status": "SUCCESS_EXACT"}
    if np.any(p < -TOL) or np.any(success < -TOL) or base["row_sum_error"] > TOL:
        base["status"] = "INVALID_PROBABILITY"
        return base
    if has_closed_transient_class(p, success):
        base["status"] = "NON_ABSORBING"
        return base
    a = np.eye(len(states)) - p
    condition = float(np.linalg.cond(a))
    base["condition_number"] = condition
    if not np.isfinite(condition) or condition > 1e12:
        base["status"] = "ILL_CONDITIONED"
        return base
    try:
        values = np.linalg.solve(a, np.column_stack([rewards, success]))
    except np.linalg.LinAlgError:
        base["status"] = "ILL_CONDITIONED"
        return base
    residual = float(np.linalg.norm(a @ values - np.column_stack([rewards, success]), ord=np.inf) / (np.linalg.norm(a, ord=np.inf) * np.linalg.norm(values, ord=np.inf) + np.linalg.norm(np.column_stack([rewards, success]), ord=np.inf)))
    base["linear_residual"] = residual
    if residual > TOL or abs(values[0, -1] - 1.0) > TOL:
        base["status"] = "ILL_CONDITIONED"
        return base
    for name, value in zip(COMPONENTS, values[0, :-1]):
        base[f"cost_{name}"] = float(value)
    base["expected_total_cost"] = float(values[0, :-1].sum())
    base["expected_profit"] = float(case["price"] - base["expected_total_cost"])
    base["success_probability"] = float(values[0, -1])
    return base


def validate_inputs():
    required = {"case", "p1", "buy1", "test1", "p2", "buy2", "test2", "pf", "assembly", "test_product", "price", "replacement", "disassembly"}
    if len(CASES) != 6 or {case["case"] for case in CASES} != set(range(1, 7)):
        raise RuntimeError("表 1 情形编号必须恰为 1--6")
    for case in CASES:
        if set(case) != required or any(not 0 <= case[key] <= 1 for key in ("p1", "p2", "pf")):
            raise RuntimeError(f"情形 {case.get('case')}: 参数字段或次品率非法")
        if any(case[key] < 0 for key in required - {"case", "p1", "p2", "pf"}):
            raise RuntimeError(f"情形 {case['case']}: 成本或售价不能为负")


def main():
    validate_inputs()
    parameters = pd.DataFrame(CASES)
    parameters["one_assembly_success"] = (1 - parameters["p1"]) * (1 - parameters["p2"]) * (1 - parameters["pf"])
    print("表 1 参数（元/件；p 为次品率）：")
    print(parameters.to_string(index=False))
    rows = [evaluate_policy(policy, case) for case in CASES for policy in itertools.product((0, 1), repeat=4)]
    all_policies = pd.DataFrame(rows)
    if len(all_policies) != 96 or all_policies.duplicated(["case", "x1", "x2", "y", "z"]).any():
        raise RuntimeError("16 策略全枚举完整性检查失败")
    feasible = all_policies[all_policies["status"] == "SUCCESS_EXACT"].copy()
    if feasible.empty:
        raise RuntimeError("没有可行策略，不写出最终结果")
    cost_columns = [f"cost_{name}" for name in COMPONENTS]
    if (feasible[cost_columns].sum(axis=1).sub(feasible["expected_total_cost"]).abs() > TOL).any():
        raise RuntimeError("成本分项与总期望成本不一致")
    if not np.isfinite(feasible[["expected_total_cost", "expected_profit", "linear_residual"]].to_numpy()).all():
        raise RuntimeError("可行策略出现非有限数")
    best_value = feasible.groupby("case")["expected_profit"].transform("max")
    tie_tolerance = 1e-8 * np.maximum(1.0, np.maximum(best_value.abs(), feasible["expected_profit"].abs()))
    best = feasible[(best_value - feasible["expected_profit"]).abs() <= tie_tolerance].sort_values(["case", "x1", "x2", "y", "z"])
    OUTDIR.mkdir(parents=True, exist_ok=True)
    all_policies.to_csv(OUTDIR / "all_policies.csv", index=False, encoding="utf-8-sig")
    best.to_csv(OUTDIR / "best_policies.csv", index=False, encoding="utf-8-sig")
    summary = {"model": "Q2-M2", "algorithm": "Q2-A1", "accounting_unit": "每最终交付一件合格品", "policies_per_case": 16, "status_counts": all_policies.groupby("status").size().to_dict(), "best_policies": best.to_dict(orient="records")}
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n每种情形的最优策略（并列者均保留；核算单位：每最终交付一件合格品）：")
    print(best[["case", "x1", "x2", "y", "z", "expected_profit", "expected_total_cost", "cost_purchase_1", "cost_purchase_2", "cost_assembly", "cost_product_inspection", "cost_disassembly", "cost_replacement_loss", "linear_residual"]].to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    print("\n状态检查：", all_policies.groupby("status").size().to_dict())
    print(f"最大概率行和误差: {all_policies['row_sum_error'].max():.3e}")
    print(f"可行策略最大线性残差: {feasible['linear_residual'].max():.3e}")
    print(f"结果已写入: {OUTDIR}")


if __name__ == "__main__":
    main()
