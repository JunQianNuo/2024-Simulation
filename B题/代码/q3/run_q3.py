"""Q3：完整枚举 65536 个装配树固定策略。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "cumcm-q3-results"
import matplotlib.pyplot as plt
import mpmath
import numpy as np
import pandas as pd
import scipy

try:
    import resource
except ImportError:  # Windows
    resource = None

try:
    from .model import (
        BATCH_AUDIT, BATCH_CACHE, CONFIG, COSTS, EVENTS, HERE, KERNEL_AUDIT,
        KERNEL_CACHE, LEAVES, NODES, PRICE, RAW, REPLACEMENT, evaluate,
        evaluate_q3_policy, make_q3_evaluator, q3_nominal_parameters,
    )
except ImportError:
    from model import (
        BATCH_AUDIT, BATCH_CACHE, CONFIG, COSTS, EVENTS, HERE, KERNEL_AUDIT,
        KERNEL_CACHE, LEAVES, NODES, PRICE, RAW, REPLACEMENT, evaluate,
        evaluate_q3_policy, make_q3_evaluator, q3_nominal_parameters,
    )


OUTDIR = HERE.parent / "results" / "q3"


def validate_inputs():
    expected_children = {"s1": (1, 2, 3), "s2": (4, 5, 6), "s3": (7, 8), "root": ("s1", "s2", "s3")}
    if set(LEAVES) != set(range(1, 9)) or any(NODES[name][0] != children for name, children in expected_children.items()):
        raise ValueError("表 2 或图 1 的装配树不完整")
    if any(not 0 <= leaf[0] <= 1 or min(leaf[1:]) < 0 for leaf in LEAVES.values()):
        raise ValueError("零件参数越界")
    if any(not 0 <= node[1] <= 1 or min(node[2:]) < 0 for node in NODES.values()):
        raise ValueError("装配节点参数越界")


def enumerate_policies(context=None, recovery_mode="physical_retention"):
    return pd.DataFrame(evaluate(i, _context=context, recovery_mode=recovery_mode) for i in range(65536))


def feasible(frame):
    hp = frame.get("high_precision_reward_solve", False)
    if hasattr(hp, "fillna"):
        hp = hp.fillna(False).astype(bool)
    return frame[(frame.status == "SUCCESS_EXACT") | ((frame.status == "NEAR_NONABSORBING") & hp)].copy()


def select_best(frame):
    ok = feasible(frame)
    maximum = ok.expected_profit.max()
    scale = np.maximum(1.0, np.maximum(abs(maximum), ok.expected_profit.abs()))
    return ok[(maximum - ok.expected_profit).abs() <= CONFIG["tie_relative_tolerance"] * scale].sort_values("strategy_id")


def material_residuals(frame):
    result = {}
    parent = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3}
    for i in range(1, 9):
        result[f"part_{i}"] = (
            frame[f"expected_part_purchases_{i}"] + frame[f"expected_return_part_{i}"]
            - frame[f"expected_consume_part_{i}"] - frame[f"expected_part_scraps_{i}"]
        )
    for i in range(1, 4):
        result[f"semi_{i}"] = (
            frame[f"expected_semi_assemblies_{i}"] + frame[f"expected_return_semi_{i}"]
            - frame[f"expected_consume_semi_{i}"] - frame[f"expected_semi_disassemblies_{i}"]
            - frame[f"expected_semi_scraps_{i}"]
        )
    result["final"] = frame["expected_final_assemblies"] - frame["expected_final_disassemblies"] - frame["expected_final_scraps"] - 1
    return pd.DataFrame(result, index=frame.index)


def audit(frame):
    if len(frame) != 65536 or frame.strategy_id.nunique() != 65536 or set(frame.strategy_id) != set(range(65536)):
        raise RuntimeError("INCOMPLETE_POLICY_SET")
    ok = feasible(frame)
    tol = CONFIG["probability_tolerance"]
    if ok.empty or ok.max_local_equation_residual.max() > tol:
        raise RuntimeError("局部方程残差验收失败")
    costs = [f"cost_{name}" for name in COSTS]
    if (ok[costs].sum(axis=1) - ok.expected_total_cost).abs().max() > tol:
        raise RuntimeError("成本分账不守恒")
    purchase = sum(ok[f"expected_part_purchases_{i}"] * LEAVES[i][1] for i in range(1, 9))
    inspection = sum(ok[f"expected_part_inspections_{i}"] * LEAVES[i][2] for i in range(1, 9))
    checks = [
        (ok.cost_purchase, purchase), (ok.cost_part_inspection, inspection),
        (ok.cost_semi_inspection, ok.expected_semi_inspections * 4),
        (ok.cost_final_inspection, ok.expected_final_inspections * 6),
        (ok.cost_semi_assembly, ok.expected_semi_assemblies * 8),
        (ok.cost_final_assembly, ok.expected_final_assemblies * 8),
        (ok.cost_semi_disassembly, ok.expected_semi_disassemblies * 6),
        (ok.cost_final_disassembly, ok.expected_final_disassemblies * 10),
        (ok.cost_replacement_loss, ok.expected_replacements * 40),
    ]
    if max((a - b).abs().max() for a, b in checks) > tol:
        raise RuntimeError("事件次数与成本不一致")
    balances = material_residuals(ok)
    if balances.abs().to_numpy().max() > tol:
        raise RuntimeError("逐节点物料守恒失败")
    numeric = ok.select_dtypes(include=[np.number])
    if not np.isfinite(numeric.to_numpy()).all():
        raise RuntimeError("可行策略含 NaN/Inf")
    return ok, balances


def scan_best(context=None, recovery_mode="physical_retention"):
    items, counts = [], {}
    for strategy_id in range(65536):
        row = evaluate(strategy_id, _context=context, recovery_mode=recovery_mode)
        counts[row["status"]] = counts.get(row["status"], 0) + 1
        if row["status"] != "SUCCESS_EXACT" and not (
            row["status"] == "NEAR_NONABSORBING" and row.get("high_precision_reward_solve", False)
        ):
            continue
        items.append((row["expected_profit"], strategy_id))
    items.sort(key=lambda item: (-item[0], item[1]))
    if not items:
        return [], [], counts

    tolerance = CONFIG["tie_relative_tolerance"]

    def tied(a, b):
        return abs(a - b) <= tolerance * max(1.0, abs(a), abs(b))

    best_profit = items[0][0]
    best = [item for item in items if tied(item[0], best_profit)]
    remaining = [item for item in items if not tied(item[0], best_profit)]
    second = [] if not remaining else [item for item in remaining if tied(item[0], remaining[0][0])]
    return best, second, counts


def sensitivity_analysis(nominal_best):
    rows = []
    nominal_parameters = q3_nominal_parameters()
    for parameter in nominal_parameters:
        for value in (0.05, 0.20):
            varied = {**nominal_parameters, parameter: value}
            leaves = {i: (varied[f"part_{i}"], buy, test) for i, (_, buy, test) in LEAVES.items()}
            nodes = {
                name: (children, varied[f"semi_{int(name[1])}"] if name != "root" else varied["final"], assembly, inspection, disassembly)
                for name, (children, _, assembly, inspection, disassembly) in NODES.items()
            }
            best, second, _ = scan_best((leaves, nodes, REPLACEMENT, {}, {}))
            rows.append(_sensitivity_row(parameter, value, "official Table 1-2 observed defect-rate range", best, second, nominal_best))
            print(f"sensitivity {parameter}={value:.2f}", flush=True)

    cost_groups = ("part_inspection", "semi_inspection", "final_inspection", "replacement", "semi_disassembly", "final_disassembly")
    for parameter in cost_groups:
        for multiplier in (0.75, 1.25):
            leaves, nodes, replacement = deepcopy(LEAVES), deepcopy(NODES), REPLACEMENT
            if parameter == "part_inspection":
                leaves = {i: (p, buy, test * multiplier) for i, (p, buy, test) in leaves.items()}
            elif parameter == "replacement":
                replacement *= multiplier
            else:
                position = {"semi_inspection": 3, "final_inspection": 3, "semi_disassembly": 4, "final_disassembly": 4}[parameter]
                targets = ("s1", "s2", "s3") if parameter.startswith("semi") else ("root",)
                for name in targets:
                    values = list(nodes[name]); values[position] *= multiplier; nodes[name] = tuple(values)
            best, second, _ = scan_best((leaves, nodes, replacement, {}, {}))
            rows.append(_sensitivity_row(parameter, multiplier, "hypothetical +/-25% cost stress scenario", best, second, nominal_best))
            print(f"sensitivity {parameter} x{multiplier:.2f}", flush=True)
    return pd.DataFrame(rows)


def _sensitivity_row(parameter, value, basis, best, second, nominal_best):
    best_ids = ";".join(str(item[1]) for item in best)
    second_profit = second[0][0] if second else np.nan
    return {
        "parameter": parameter, "value_or_multiplier": value, "range_basis": basis,
        "best_strategy_ids": best_ids, "best_profit": best[0][0],
        "profit_gap_to_second": best[0][0] - second_profit,
        "nominal_strategy_changed": best_ids != nominal_best,
    }


def figures(top, sensitivity):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    labels = top.strategy_id.astype(str)
    bars = ax.bar(labels, top.expected_profit, color="#3976af")
    ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=8)
    ax.set(xlabel="Strategy ID", ylabel="Expected profit (yuan)", title="Q3 top feasible policies")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTDIR / "top_policy_profit.png", dpi=220)
    save_svg(fig, OUTDIR / "top_policy_profit.svg")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    data = sensitivity.reset_index(drop=True)
    changed = data.nominal_strategy_changed.astype(bool)
    ax.scatter(np.flatnonzero(~changed), data.loc[~changed, "profit_gap_to_second"],
               color="#3976af", s=24, label="Nominal strategy retained")
    ax.scatter(np.flatnonzero(changed), data.loc[changed, "profit_gap_to_second"],
               color="#d95f02", s=34, label="Strategy switched")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(xlabel="Sensitivity scenario", ylabel="Best-second profit gap (yuan)",
           title="Q3 decision-margin sensitivity")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUTDIR / "sensitivity_profit_gap.png", dpi=220)
    save_svg(fig, OUTDIR / "sensitivity_profit_gap.svg")
    plt.close(fig)


def save_svg(fig, path):
    fig.savefig(path, metadata={"Date": None})
    path.write_text(
        "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_sha256(path):
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def git_value(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=HERE, text=True).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def clean_record(record):
    return {key: value for key, value in record.items() if not pd.isna(value)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-sensitivity", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()
    validate_inputs()
    KERNEL_CACHE.clear(); BATCH_CACHE.clear(); KERNEL_AUDIT.clear(); BATCH_AUDIT.clear()
    all_rows = enumerate_policies()
    ok, balances = audit(all_rows)
    best = select_best(all_rows)
    top = ok.nlargest(10, "expected_profit").sort_values(["expected_profit", "strategy_id"], ascending=[False, True])
    gap = float(top.iloc[0].expected_profit - top.iloc[1].expected_profit)
    nominal_best = ";".join(map(str, best.strategy_id.astype(int)))
    kernel_registry = {
        "schema_version": CONFIG["kernel_schema_version"],
        "model_scope": "compositional kernel solver for the specified three-level assembly tree",
        "tree_and_parameter_sha256": sha256(HERE / "table2.json"),
        "bit_order": ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "y1", "y2", "y3", "yf", "z1", "z2", "z3", "zf"],
        "state_fields": ["phase", "quality", "information", "source"],
        "quality_values": ["missing", "bad", "good"],
        "information_values": ["missing", "unknown", "known_good"],
        "source_values": ["missing", "new", "recovered"],
        "batch_kernels": dict(BATCH_AUDIT), "subtree_kernels": dict(KERNEL_AUDIT),
    }

    if args.skip_sensitivity:
        sensitivity = pd.DataFrame()
    else:
        sensitivity = sensitivity_analysis(nominal_best)
    reset_best, reset_second, reset_counts = scan_best(recovery_mode="quality_reset_rebuild")
    structural = pd.DataFrame([
        {"recovery_mode": "physical_retention", "best_strategy_ids": nominal_best,
         "best_profit": best.expected_profit.max(), "status_counts": json.dumps(all_rows.status.value_counts().to_dict()),
         "note": "main model; recovered items retain physical quality"},
        {"recovery_mode": "quality_reset_rebuild", "best_strategy_ids": ";".join(str(x[1]) for x in reset_best),
         "best_profit": reset_best[0][0], "status_counts": json.dumps(reset_counts),
         "note": "structural stress only; dismantled children are statistically reset and rebuilt"},
    ])

    OUTDIR.mkdir(parents=True, exist_ok=True)
    all_rows.to_csv(OUTDIR / "all_policies.csv", index=False, encoding="utf-8-sig")
    best.to_csv(OUTDIR / "best_policies.csv", index=False, encoding="utf-8-sig")
    top.to_csv(OUTDIR / "top10_policies.csv", index=False, encoding="utf-8-sig")
    decision = []
    for _, row in best.iterrows():
        for i in range(1, 9):
            decision.append({"strategy_id": int(row.strategy_id), "node": f"part_{i}", "inspect": int(row[f"x{i}"]), "disassemble": "N/A"})
        for i in range(1, 4):
            decision.append({"strategy_id": int(row.strategy_id), "node": f"semi_{i}", "inspect": int(row[f"y{i}"]), "disassemble": int(row[f"z{i}"])})
        decision.append({"strategy_id": int(row.strategy_id), "node": "final", "inspect": int(row.yf), "disassemble": int(row.zf)})
    pd.DataFrame(decision).to_csv(OUTDIR / "decision_summary.csv", index=False, encoding="utf-8-sig")
    balance_summary = pd.DataFrame({
        "node": balances.columns,
        "max_abs_residual_all_feasible": [balances[column].abs().max() for column in balances],
        "best_policy_residual": [material_residuals(best)[column].abs().max() for column in balances],
    })
    balance_summary.to_csv(OUTDIR / "material_balance.csv", index=False, encoding="utf-8-sig")
    sensitivity.to_csv(OUTDIR / "sensitivity.csv", index=False, encoding="utf-8-sig")
    structural.to_csv(OUTDIR / "structural_comparison.csv", index=False, encoding="utf-8-sig")
    (OUTDIR / "kernel_registry.json").write_text(json.dumps(kernel_registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not sensitivity.empty:
        figures(top, sensitivity)

    runtime = time.perf_counter() - started
    source_files = [HERE.parent / "component_state.py"] + [HERE / name for name in (
        "model.py", "run_q3.py", "test_q3.py", "config.json", "table2.json",
        "requirements.txt", "README.md",
    )]
    metadata = {
        "schema_version": CONFIG["schema_version"], "kernel_schema_version": CONFIG["kernel_schema_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "cd B题/代码 && python -m q3.run_q3",
        "runtime_seconds": runtime,
        "peak_rss_kib": None if resource is None else resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": sys.version, "platform": platform.platform(),
        "versions": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
                     "matplotlib": matplotlib.__version__, "mpmath": mpmath.__version__},
        "input_sha256": sha256(HERE / "table2.json"), "config_sha256": sha256(HERE / "config.json"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty": bool(git_value("status", "--porcelain")),
        "source_snapshot": "exact and LF-normalized SHA-256 hashes are authoritative when git_dirty is true",
        "source_sha256": {str(path.relative_to(HERE.parent)): sha256(path) for path in source_files},
        "normalized_source_sha256": {str(path.relative_to(HERE.parent)): normalized_sha256(path) for path in source_files},
    }
    summary = {
        "model": "Q3-M3", "algorithm": "Q3-A1", "metadata": metadata,
        "model_scope": "specified three-level assembly tree; not a general tree generator",
        "policies_total": 65536, "status_counts": {str(k): int(v) for k, v in all_rows.status.value_counts().items()},
        "feasible_policies": len(ok), "best_profit": float(best.expected_profit.max()),
        "best_policies": [clean_record(x) for x in best.to_dict(orient="records")],
        "top3_feasible": [clean_record(x) for x in top.head(3).to_dict(orient="records")],
        "profit_gap_to_second": gap, "max_local_equation_residual": float(ok.max_local_equation_residual.max()),
        "minimum_absorption_margin": float(ok.absorption_margin.min()),
        "maximum_material_balance_residual": float(balances.abs().to_numpy().max()),
        "one_pass_success_no_inspection": float(np.prod([1 - x[0] for x in LEAVES.values()]) * np.prod([1 - x[1] for x in NODES.values()])),
        "sensitivity_range_note": "Defect-rate bounds use official Tables 1-2 observed range; cost multipliers are explicitly hypothetical stress scenarios.",
    }
    (OUTDIR / "run_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTDIR / "repro_manifest.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    switches = [] if sensitivity.empty else sensitivity.loc[
        sensitivity.nominal_strategy_changed, ["parameter", "value_or_multiplier", "best_strategy_ids"]
    ].to_dict(orient="records")
    writer = {
        "claims": [
            {"claim": "nominal optimum", "strategy_id": int(best.iloc[0].strategy_id),
             "strategy_bits": best.iloc[0].strategy_bits, "expected_profit_yuan": float(best.iloc[0].expected_profit),
             "expected_cost_yuan": float(best.iloc[0].expected_total_cost),
             "conditions": "Table 2 nominal parameters; physical quality retention",
             "table": "best_policies.csv", "figure": "top_policy_profit.svg",
             "validation": "test_q3.py full enumeration, closed-form batch crosscheck and material_balance.csv"},
            {"claim": "sensitivity switches", "switch_scenarios": switches,
             "table": "sensitivity.csv", "figure": "sensitivity_profit_gap.svg",
             "conditions": "Defect bounds use Tables 1-2 observed range; cost scenarios are hypothetical +/-25%."},
        ],
        "extension_validation": {
            "case": "part_1 defect=1e-12, all other upstream defects=0, final defect=0.1, strategy=32768",
            "expected_status": "NON_ABSORBING",
            "validation": "test_tiny_positive_defect_remains_structurally_nonabsorbing",
        },
        "caution": "The implementation targets the specified three-level assembly tree; it is not a general assembly-tree generator. quality_reset_rebuild is structural stress only.",
    }
    (OUTDIR / "code_to_writer.json").write_text(json.dumps(writer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    figure_index = {
        "top_policy_profit.svg": {"source": "top10_policies.csv", "supports": "nominal optimum and runner-up gap"},
        "sensitivity_profit_gap.svg": {"source": "sensitivity.csv", "supports": "decision stability and switch scenario"},
        "command": metadata["command"],
    }
    (OUTDIR / "figure_index.json").write_text(json.dumps(figure_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n65536 策略状态:", summary["status_counts"])
    print(best[["strategy_id", "strategy_bits", "expected_profit", "expected_total_cost",
                "expected_part_inspections", "absorption_margin"]].to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print(f"最大残差 {summary['max_local_equation_residual']:.3e}，物料守恒误差 {summary['maximum_material_balance_residual']:.3e}")
    print(f"运行 {runtime:.2f}s，结果目录 {OUTDIR}")


if __name__ == "__main__":
    main()
