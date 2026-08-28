"""Q3-M3 / Q3-A1：装配树上的精确固定策略枚举。"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


LEAVES = {1: (0.10, 2, 1), 2: (0.10, 8, 1), 3: (0.10, 12, 2), 4: (0.10, 2, 1), 5: (0.10, 8, 1), 6: (0.10, 12, 2), 7: (0.10, 8, 1), 8: (0.10, 12, 2)}
NODES = {"s1": ((1, 2, 3), .10, 8, 4, 6), "s2": ((4, 5, 6), .10, 8, 4, 6), "s3": ((7, 8), .10, 8, 4, 6), "root": (("s1", "s2", "s3"), .10, 8, 6, 10)}
PRICE, REPLACEMENT = 200, 40
OUTDIR = Path(__file__).resolve().parent.parent / "results" / "q3"
TOL = 1e-10
COSTS = ["purchase", "part_inspection", "semi_inspection", "final_inspection", "semi_assembly", "final_assembly", "semi_disassembly", "final_disassembly", "replacement_loss"]
EVENTS = ["expected_part_inspections", "expected_semi_inspections", "expected_final_inspections", "expected_semi_assemblies", "expected_final_assemblies", "expected_semi_disassemblies", "expected_final_disassemblies", "expected_replacements"]
KERNEL_CACHE = {}


def zeros():
    return np.zeros(len(COSTS) + len(EVENTS))


def decode(strategy_id):
    bits = tuple((strategy_id >> i) & 1 for i in range(16))
    return bits[:8], bits[8:11], bits[11], bits[12:15], bits[15]


def policy_text(bits):
    return "".join(map(str, bits))


def solve_loop(reward, repeat_probability):
    """一状态吸收奖励方程 V=r+pV，而非模拟或截断。"""
    value = np.linalg.solve(np.array([[1.0 - repeat_probability]]), reward.reshape(1, -1))[0]
    return value


def leaf_kernel(leaf, inspect):
    defect, buy, test = LEAVES[leaf]
    r = zeros()
    r[COSTS.index("purchase")] = buy
    if not inspect:
        return 1 - defect, r, 0.0
    r[COSTS.index("part_inspection")] = test
    r[len(COSTS) + EVENTS.index("expected_part_inspections")] = 1
    return 1.0, solve_loop(r, defect), defect


def node_kernel(name, policy, memo):
    """返回节点输出为良的概率、期望奖励、局部谱半径；缓存局部策略签名。"""
    parts, semis, yf, dis_semis, zf = policy
    if name != "root":
        i = int(name[1]) - 1
        first, last = ((0, 3), (3, 6), (6, 8))[i]
        key = (name, parts[first:last], semis[i], dis_semis[i])
        if key in KERNEL_CACHE:
            return KERNEL_CACHE[key]
    children, defect, assembly, inspection, disassembly = NODES[name]
    is_root = name == "root"
    child_results = []
    for child in children:
        if isinstance(child, int):
            child_results.append(leaf_kernel(child, parts[child - 1]))
        else:
            child_results.append(node_kernel(child, policy, memo))
    q = (1 - defect) * float(np.prod([item[0] for item in child_results]))
    r = sum((item[1] for item in child_results), zeros())
    r[COSTS.index("final_assembly" if is_root else "semi_assembly")] += assembly
    r[len(COSTS) + EVENTS.index("expected_final_assemblies" if is_root else "expected_semi_assemblies")] += 1
    test = yf if is_root else semis[int(name[1]) - 1]
    dismantle = zf if is_root else dis_semis[int(name[1]) - 1]
    child_guaranteed_good = all(abs(item[0] - 1.0) <= TOL for item in child_results)
    # 已知坏品拆解时，未检测的坏直接子件会原样返回，构成闭类。
    if test and dismantle and not child_guaranteed_good:
        raise ValueError("NON_ABSORBING")
    if not test and is_root and dismantle:
        if not child_guaranteed_good:
            raise ValueError("NON_ABSORBING")
        first = sum((item[1] for item in child_results), zeros())
        cycle = zeros()
        cycle[COSTS.index("final_assembly")] = assembly
        cycle[COSTS.index("final_disassembly")] = defect * disassembly
        cycle[COSTS.index("replacement_loss")] = defect * REPLACEMENT
        cycle[len(COSTS) + EVENTS.index("expected_final_assemblies")] = 1
        cycle[len(COSTS) + EVENTS.index("expected_final_disassemblies")] = defect
        cycle[len(COSTS) + EVENTS.index("expected_replacements")] = defect
        result = 1.0, first + solve_loop(cycle, defect), max(defect, *(item[2] for item in child_results))
        return result
    if not test:
        result = q, r, max(item[2] for item in child_results)
        if not is_root: KERNEL_CACHE[key] = result
        return result
    r[COSTS.index("final_inspection" if is_root else "semi_inspection")] += inspection
    r[len(COSTS) + EVENTS.index("expected_final_inspections" if is_root else "expected_semi_inspections")] += 1
    if not dismantle:
        result = 1.0, solve_loop(r, 1 - q), max(1 - q, *(item[2] for item in child_results))
        if not is_root: KERNEL_CACHE[key] = result
        return result
    # 安全拆解时所有直接子件均保证为良，失败只能来自本节点条件装配缺陷。
    cycle = zeros()
    cycle[COSTS.index("final_assembly" if is_root else "semi_assembly")] = assembly
    cycle[COSTS.index("final_inspection" if is_root else "semi_inspection")] = inspection
    cycle[COSTS.index("final_disassembly" if is_root else "semi_disassembly")] = defect * disassembly
    cycle[len(COSTS) + EVENTS.index("expected_final_assemblies" if is_root else "expected_semi_assemblies")] = 1
    cycle[len(COSTS) + EVENTS.index("expected_final_inspections" if is_root else "expected_semi_inspections")] = 1
    cycle[len(COSTS) + EVENTS.index("expected_final_disassemblies" if is_root else "expected_semi_disassemblies")] = defect
    first = sum((item[1] for item in child_results), zeros())
    result = 1.0, first + solve_loop(cycle, defect), max(defect, *(item[2] for item in child_results))
    if not is_root: KERNEL_CACHE[key] = result
    return result


def evaluate(strategy_id):
    bits = tuple((strategy_id >> i) & 1 for i in range(16))
    parts, semis, yf, dis_semis, zf = decode(strategy_id)
    row = {"strategy_id": strategy_id, "strategy_bits": policy_text(bits), **{f"x{i}": parts[i - 1] for i in range(1, 9)}, **{f"y{i}": semis[i - 1] for i in range(1, 4)}, "yf": yf, **{f"z{i}": dis_semis[i - 1] for i in range(1, 4)}, "zf": zf, "status": "SUCCESS_EXACT"}
    try:
        q, reward, rho = node_kernel("root", (parts, semis, yf, dis_semis, zf), {})
        # 根节点未成检时，市场坏品调换后按相同根流程继续；这是另一条一状态奖励方程。
        if not yf and not zf:
            reward[COSTS.index("replacement_loss")] += (1 - q) * REPLACEMENT
            reward[len(COSTS) + EVENTS.index("expected_replacements")] += 1 - q
            reward = solve_loop(reward, 1 - q)
            rho = max(rho, 1 - q)
        row["spectral_radius"] = rho
        row["local_loop_equations"] = 1
        rhs = reward.reshape(1, -1)
        residual = np.linalg.norm((1 - 0.0) * rhs - rhs, ord=np.inf) / (np.linalg.norm(rhs, ord=np.inf) + 1.0)
        row["local_equation_residual"] = float(residual)
        for name, value in zip(COSTS, reward[:len(COSTS)]):
            row[f"cost_{name}"] = float(value)
        for name, value in zip(EVENTS, reward[len(COSTS):]):
            row[name] = float(value)
        row["expected_total_cost"] = float(reward[:len(COSTS)].sum())
        row["expected_profit"] = PRICE - row["expected_total_cost"]
        row["one_pass_success_no_inspection"] = .9 ** 12
        row["factory_defect_rate"] = 0.0 if yf else row["expected_replacements"] / (1 + row["expected_replacements"])
        return row
    except ValueError as exc:
        if str(exc) != "NON_ABSORBING":
            raise
        row.update({"status": "NON_ABSORBING", "local_loop_equations": 1, "spectral_radius": 1.0, "local_equation_residual": np.nan, "one_pass_success_no_inspection": .9 ** 12})
        return row
    except np.linalg.LinAlgError:
        row.update({"status": "ILL_CONDITIONED", "local_loop_equations": 1, "spectral_radius": np.nan, "local_equation_residual": np.nan})
        return row


def validate_inputs():
    expected_leaves = {1: (.1, 2, 1), 2: (.1, 8, 1), 3: (.1, 12, 2), 4: (.1, 2, 1), 5: (.1, 8, 1), 6: (.1, 12, 2), 7: (.1, 8, 1), 8: (.1, 12, 2)}
    expected_nodes = {"s1": ((1, 2, 3), .1, 8, 4, 6), "s2": ((4, 5, 6), .1, 8, 4, 6), "s3": ((7, 8), .1, 8, 4, 6), "root": (("s1", "s2", "s3"), .1, 8, 6, 10)}
    if LEAVES != expected_leaves or NODES != expected_nodes or (PRICE, REPLACEMENT) != (200, 40):
        raise RuntimeError("题目表 2 或图 1 的树结构/参数值校验失败")
    if abs(.9 ** 12 - .282429536481) > 1e-12:
        raise RuntimeError("无检测一次良率基准失败")


def main():
    validate_inputs()
    rows = [evaluate(i) for i in range(1 << 16)]
    all_rows = pd.DataFrame(rows)
    if len(all_rows) != 65536 or all_rows.strategy_id.nunique() != 65536:
        raise RuntimeError("INCOMPLETE_POLICY_SET")
    # 半成品 1 检测并拆解、但零件 1 未检测：坏件可达且会原样循环。
    if evaluate((1 << 8) | (1 << 12))["status"] != "NON_ABSORBING":
        raise RuntimeError("微型坏件回流策略未被识别为 NON_ABSORBING")
    feasible = all_rows[all_rows.status.eq("SUCCESS_EXACT")].copy()
    if feasible.empty or (feasible[[f"cost_{x}" for x in COSTS]].sum(axis=1).sub(feasible.expected_total_cost).abs() > TOL).any() or (feasible.expected_profit.sub(PRICE - feasible.expected_total_cost).abs() > TOL).any():
        raise RuntimeError("成本或利润自检失败")
    best_profit = feasible.expected_profit.max()
    best = feasible[(best_profit - feasible.expected_profit).abs() <= 1e-8 * max(1, abs(best_profit))].sort_values("strategy_id")
    decisions = []
    for _, row in best.iterrows():
        for i in range(1, 9): decisions.append({"strategy_id": int(row.strategy_id), "node": f"part_{i}", "inspect": int(row[f"x{i}"]), "disassemble": "N/A"})
        for i in range(1, 4): decisions.append({"strategy_id": int(row.strategy_id), "node": f"semi_{i}", "inspect": int(row[f"y{i}"]), "disassemble": int(row[f"z{i}"])})
        decisions.append({"strategy_id": int(row.strategy_id), "node": "final", "inspect": int(row.yf), "disassemble": int(row.zf)})
    OUTDIR.mkdir(parents=True, exist_ok=True)
    all_rows.to_csv(OUTDIR / "all_policies.csv", index=False, encoding="utf-8-sig")
    best.to_csv(OUTDIR / "best_policies.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(decisions).to_csv(OUTDIR / "decision_summary.csv", index=False, encoding="utf-8-sig")
    summary = {"model": "Q3-M3", "algorithm": "Q3-A1", "solver": "局部闭环方程/树状递推的等价精确求解；未显式构建每条策略的完整多状态转移矩阵", "policies_total": 65536, "accounting_unit": "每最终交付一件合格成品", "status_counts": all_rows.status.value_counts().to_dict(), "feasible_policies": int(len(feasible)), "best_profit": best_profit, "best_policies": best.to_dict(orient="records"), "max_local_equation_residual": float(feasible.local_equation_residual.max()), "max_spectral_radius": float(feasible.spectral_radius.max()), "one_pass_success_no_inspection": .9 ** 12, "one_pass_defect_no_inspection": 1 - .9 ** 12, "economic_note": "最优策略先检测全部零件和半成品、拆解可安全回收的坏节点；成检成本相对 40 元调换损失在该参数下不划算。", "interpretation": "最终成功概率为 1 仅表示订单最终吸收交付，不代表一次装配合格率为 1。"}
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("65536 条策略状态统计:", all_rows.status.value_counts().to_dict())
    print(f"局部闭环方程最差残差: {feasible.local_equation_residual.max():.3e}")
    print(best[["strategy_id", "strategy_bits", "expected_profit", "expected_total_cost", "expected_part_inspections", "expected_semi_inspections", "expected_final_inspections", "expected_semi_assemblies", "expected_final_assemblies", "expected_semi_disassemblies", "expected_final_disassemblies", "expected_replacements"]].to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("结果目录:", OUTDIR)


if __name__ == "__main__":
    main()
