"""Q2：16 策略精确枚举、吸收 Markov 核算与验收输出。"""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mpmath
import numpy as np
import pandas as pd
import scipy

try:
    from .model import COMPONENTS, EVENTS, evaluate_policy
except ImportError:
    from model import COMPONENTS, EVENTS, evaluate_policy


HERE = Path(__file__).resolve().parent
OUTDIR = HERE.parent / "results" / "q2"
POLICIES = list(itertools.product((0, 1), repeat=4))
REQUIRED = {
    "case", "p1", "buy1", "test1", "p2", "buy2", "test2", "pf",
    "assembly", "test_product", "price", "replacement", "disassembly",
}


def load_inputs():
    cases = json.loads((HERE / "table1.json").read_text(encoding="utf-8"))
    config = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    if len(cases) != 6 or {row.get("case") for row in cases} != set(range(1, 7)):
        raise ValueError("表 1 必须恰含情形 1--6")
    for row in cases:
        if set(row) != REQUIRED or any(not 0 <= row[key] <= 1 for key in ("p1", "p2", "pf")):
            raise ValueError(f"情形 {row.get('case')} 字段或概率非法")
        if any(row[key] < 0 for key in REQUIRED - {"case", "p1", "p2", "pf"}):
            raise ValueError(f"情形 {row['case']} 成本不能为负")
    return cases, config


def feasible_rows(frame):
    return frame[frame["status"].isin(["SUCCESS_EXACT", "NEAR_NONABSORBING"])].copy()


def select_best(frame, config):
    frame = feasible_rows(frame)
    maxima = frame.groupby("case")["expected_profit"].transform("max")
    scale = np.maximum(1.0, np.maximum(maxima.abs(), frame["expected_profit"].abs()))
    return frame[(maxima - frame["expected_profit"]).abs() <= config["tie_relative_tolerance"] * scale]


def audit_accounting(frame, cases, config):
    tol = config["probability_tolerance"]
    lookup = {row["case"]: row for row in cases}
    checks = {
        "cost_purchase_1": ("expected_purchases_1", "buy1"),
        "cost_purchase_2": ("expected_purchases_2", "buy2"),
        "cost_inspection_1": ("expected_inspections_1", "test1"),
        "cost_inspection_2": ("expected_inspections_2", "test2"),
        "cost_product_inspection": ("expected_product_inspections", "test_product"),
        "cost_assembly": ("expected_assemblies", "assembly"),
        "cost_disassembly": ("expected_disassemblies", "disassembly"),
        "cost_replacement_loss": ("expected_replacements", "replacement"),
    }
    numeric = ["expected_total_cost", "expected_profit", "linear_residual", "spectral_radius"]
    if not np.isfinite(frame[numeric].to_numpy()).all():
        raise RuntimeError("可行策略含非有限数")
    cost_columns = [f"cost_{name}" for name in COMPONENTS]
    if (frame[cost_columns].sum(axis=1) - frame["expected_total_cost"]).abs().max() > tol:
        raise RuntimeError("成本分项与总成本不一致")
    for _, row in frame.iterrows():
        for cost_name, (event_name, parameter_name) in checks.items():
            target = row[event_name] * lookup[row["case"]][parameter_name]
            if abs(row[cost_name] - target) > tol:
                raise RuntimeError(f"情形 {int(row['case'])} {cost_name} 与事件计数不一致")


def enumerate_nominal(cases, config):
    rows, state_rows, edge_rows = [], [], []
    for case in cases:
        for policy in POLICIES:
            result = evaluate_policy(policy, case, config, include_graph=True)
            states, p, success, edges = result.pop("_graph")
            policy_id = "".join(map(str, policy))
            rows.append(result)
            for i, state in enumerate(states):
                state_rows.append({
                    "case": case["case"], "policy": policy_id, "state_id": i,
                    **state._asdict(), "transient_probability": float(p[i].sum()),
                    "success_probability": float(success[i]),
                })
            for source, target, probability in edges:
                edge_rows.append({
                    "case": case["case"], "policy": policy_id, "source_state": source,
                    "target_type": "transient", "target_state": target, "probability": probability,
                })
            for source, probability in enumerate(success):
                if probability > 0.0:
                    edge_rows.append({
                        "case": case["case"], "policy": policy_id, "source_state": source,
                        "target_type": "success", "target_state": "", "probability": probability,
                    })
    return pd.DataFrame(rows), pd.DataFrame(state_rows), pd.DataFrame(edge_rows)


def _best_for_case(case, config, recovery_mode="physical_retention"):
    frame = pd.DataFrame(evaluate_policy(p, case, config, recovery_mode) for p in POLICIES)
    frame = feasible_rows(frame)
    maximum = frame["expected_profit"].max()
    scale = np.maximum(1.0, np.maximum(abs(maximum), frame["expected_profit"].abs()))
    best = frame[(maximum - frame["expected_profit"]).abs() <= config["tie_relative_tolerance"] * scale]
    labels = ["".join(str(int(row[key])) for key in ("x1", "x2", "y", "z")) for _, row in best.iterrows()]
    return maximum, ";".join(labels)


def sensitivity_analysis(cases, config, nominal_best):
    rows = []
    # 取表 1 中实际出现的参数值，避免无依据的±10%。
    for parameter in ("test1", "test2", "replacement", "disassembly"):
        for value in sorted({case[parameter] for case in cases}):
            for original in cases:
                varied = {**original, parameter: value}
                profit, policies = _best_for_case(varied, config)
                rows.append({
                    "case": original["case"], "parameter": parameter, "value": value,
                    "range_basis": "Table 1 observed values", "best_policies": policies,
                    "best_profit": profit,
                    "policy_changed": policies != nominal_best[original["case"]][1],
                })
    structural = []
    for case in cases:
        for mode in ("physical_retention", "quality_reset"):
            profit, policies = _best_for_case(case, config, mode)
            structural.append({
                "case": case["case"], "recovery_mode": mode,
                "best_policies": policies, "best_profit": profit,
                "note": "main model" if mode == "physical_retention" else "structural sensitivity only",
            })
    return pd.DataFrame(rows), pd.DataFrame(structural)


def plot_best(best):
    grouped = best.groupby("case", as_index=False)["expected_profit"].max()
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    bars = ax.bar(grouped["case"].astype(str), grouped["expected_profit"], color="#3976af")
    ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=9)
    ax.set(xlabel="Case", ylabel="Expected profit (yuan)", title="Q2 optimal expected profit by case")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTDIR / "best_profit_by_case.png", dpi=220)
    fig.savefig(OUTDIR / "best_profit_by_case.svg")
    plt.close(fig)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_value(value):
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, np.bool_):
        return bool(value)
    raise TypeError(type(value).__name__)


def clean_record(record):
    return {key: value for key, value in record.items() if not pd.isna(value)}


def main():
    cases, config = load_inputs()
    all_policies, states, edges = enumerate_nominal(cases, config)
    if len(all_policies) != 96 or all_policies.duplicated(["case", "x1", "x2", "y", "z"]).any():
        raise RuntimeError("6×16 策略枚举不完整")
    feasible = feasible_rows(all_policies)
    audit_accounting(feasible, cases, config)
    best = select_best(all_policies, config).sort_values(["case", "x1", "x2", "y", "z"])
    nominal_lookup = {}
    for case in cases:
        subset = best[best["case"] == case["case"]]
        labels = ";".join("".join(str(int(row[key])) for key in ("x1", "x2", "y", "z")) for _, row in subset.iterrows())
        nominal_lookup[case["case"]] = (subset["expected_profit"].max(), labels)
    sensitivity, structural = sensitivity_analysis(cases, config, nominal_lookup)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    all_policies.to_csv(OUTDIR / "all_policies.csv", index=False, encoding="utf-8-sig")
    best.to_csv(OUTDIR / "best_policies.csv", index=False, encoding="utf-8-sig")
    states.to_csv(OUTDIR / "state_table.csv", index=False, encoding="utf-8-sig")
    edges.to_csv(OUTDIR / "transition_edges.csv", index=False, encoding="utf-8-sig")
    sensitivity.to_csv(OUTDIR / "sensitivity.csv", index=False, encoding="utf-8-sig")
    structural.to_csv(OUTDIR / "structural_comparison.csv", index=False, encoding="utf-8-sig")
    plot_best(best)

    metadata = {
        "schema_version": config["schema_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python B题/代码/q2/run_q2.py",
        "python": sys.version, "platform": platform.platform(),
        "versions": {
            "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__, "mpmath": mpmath.__version__,
        },
        "input_sha256": sha256(HERE / "table1.json"),
        "config_sha256": sha256(HERE / "config.json"),
        "code_sha256": {name: sha256(HERE / name) for name in ("model.py", "run_q2.py")},
    }
    summary = {
        "model": "Q2-M2", "algorithm": "Q2-A1", "metadata": metadata,
        "accounting_unit": "one finally delivered qualified product",
        "policy_order": ["component_1_test", "component_2_test", "product_test", "disassemble"],
        "policies_per_case": 16,
        "status_counts": {str(k): int(v) for k, v in all_policies.groupby("status").size().items()},
        "max_row_sum_error": float(all_policies["row_sum_error"].max()),
        "max_linear_residual": float(feasible["linear_residual"].max()),
        "minimum_success_absorption_margin": float(feasible["absorption_margin"].min()),
        "case_results": [
            {
                "case": case["case"],
                "one_assembly_success": (1 - case["p1"]) * (1 - case["p2"]) * (1 - case["pf"]),
                "best_strategies": [
                    clean_record(record)
                    for record in best[best["case"] == case["case"]].to_dict(orient="records")
                ],
            }
            for case in cases
        ],
        "artifacts": [
            "all_policies.csv", "best_policies.csv", "state_table.csv", "transition_edges.csv",
            "sensitivity.csv", "structural_comparison.csv", "best_profit_by_case.png",
            "best_profit_by_case.svg", "run_metadata.json",
            "code_to_writer.md",
        ],
    }
    (OUTDIR / "run_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=json_value) + "\n", encoding="utf-8")

    print("最优策略（x1,x2,y,z）：")
    print(best[["case", "x1", "x2", "y", "z", "expected_profit", "absorption_margin"]].to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("\n状态分类：", summary["status_counts"])
    print(f"最大行和误差 {summary['max_row_sum_error']:.3e}，最大求解残差 {summary['max_linear_residual']:.3e}")
    print(f"结果目录：{OUTDIR}")


if __name__ == "__main__":
    main()
