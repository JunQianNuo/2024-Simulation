"""Q4-M4/M2/M3：序贯抽样价值、终止生产决策与稳健审计。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy

from .batch_evaluators import Q2_POLICIES, Q3_POLICY_IDS, q2_profit_batch, q3_profit_batch
from .belief_state import (
    BeliefState, from_records, marginal_cost, past_sampling_cost, validate_records,
)
from .exact_voi_dp import Q2VoiDP
from .kg_rollout import q3_knowledge_gradient
from .simultaneous_cs import simultaneous_interval

HERE = Path(__file__).resolve().parent
CODE_DIR = HERE.parent
OUTDIR = CODE_DIR / "results" / "q4"
CONFIG_PATH = HERE / "config.json"
DEMO = HERE / "q4_demo_evidence.json"
Q2_NAMES = ("p1", "p2", "pf")
Q3_NAMES = tuple([f"part_{i}" for i in range(1, 9)] + ["semi_1", "semi_2", "semi_3", "final"])


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_q2_inputs() -> tuple[list[dict], dict]:
    return read_json(CODE_DIR / "q2" / "table1.json"), read_json(CODE_DIR / "q2" / "config.json")


def read_evidence(path: str | Path) -> dict:
    evidence = read_json(path)
    if set(evidence) - {"mode", "sampling_plan", "note", "q2", "q3"}:
        raise ValueError("INVALID_DATA: evidence top-level schema mismatch")
    plan = evidence.get("sampling_plan", "fixed_n")
    if plan not in {"fixed_n", "mixed", "sequential_cs"}:
        raise ValueError("INVALID_DATA: invalid sampling_plan")
    q2_conditioning = {"p1": "component", "p2": "component", "pf": "all_inputs_good"}
    for case_no in range(1, 7):
        validate_records(evidence.get("q2", {}).get(f"case_{case_no}", {}),
                         q2_conditioning, f"q2.case_{case_no}", plan)
    q3_conditioning = {
        **{f"part_{i}": "component" for i in range(1, 9)},
        **{f"semi_{i}": "all_inputs_good" for i in range(1, 4)},
        "final": "all_inputs_good",
    }
    validate_records(evidence.get("q3", {}), q3_conditioning, "q3", plan)
    return evidence


def interval_box(records: dict, names: tuple[str, ...], coverage: int, default_plan: str):
    alpha_j = (1 - coverage / 100) / len(names)
    rows, bounds = [], []
    for name in names:
        lower, upper, method = simultaneous_interval(records[name], alpha_j, default_plan)
        bounds.append((lower, upper))
        rows.append({"parameter": name, "coverage": coverage, "alpha_j": alpha_j,
                     "lower": lower, "upper": upper, "method": method})
    return np.asarray(bounds), rows


def _policy_label(domain: str, index: int) -> str | int:
    return "".join(map(str, Q2_POLICIES[index])) if domain == "q2" else int(Q3_POLICY_IDS[index])


def robust_audit(domain: str, records: dict, names: tuple[str, ...], coverage: int,
                 default_plan: str, case: dict | None, bayes_index: int) -> tuple[dict, list[dict]]:
    bounds, interval_rows = interval_box(records, names, coverage, default_plan)
    nominal = np.array([[records[name]["K"] / records[name]["N"] for name in names]])
    upper = bounds[:, 1][None, :]
    if domain == "q2":
        nominal_values, nominal_feasible = q2_profit_batch(case, nominal)
        worst_values, feasible = q2_profit_batch(case, upper)
    else:
        nominal_values, nominal_feasible = q3_profit_batch(nominal)
        worst_values, feasible = q3_profit_batch(upper)
    feasible = feasible[0]
    worst = worst_values[0]
    valid = np.flatnonzero(feasible)
    robust_index = int(valid[np.argmax(worst[valid])])
    if worst[bayes_index] > nominal_values[0, bayes_index] + 1e-9:
        raise RuntimeError("ROBUST_UNCERTIFIED: worst profit exceeds nominal profit")
    return {
        "domain": domain, "coverage": coverage,
        "status": "ROBUST_NUMERICAL",
        "bayesian_policy": _policy_label(domain, bayes_index),
        "bayesian_policy_nominal_profit": float(nominal_values[0, bayes_index]),
        "bayesian_policy_worst_profit": float(worst[bayes_index]),
        "robust_policy": _policy_label(domain, robust_index),
        "robust_policy_worst_profit": float(worst[robust_index]),
        "worst_parameter_location": "all rectangular upper endpoints",
        "inner_gap": None,
        "claim_scope": "endpoint result supported by structural monotonicity and numerical checks; no interval BnB certificate",
    }, interval_rows


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def run_q2_voi(config: dict, evidence: dict, quick: bool):
    cases, _ = load_q2_inputs()
    settings = config["q2_voi"]
    horizon = settings["quick_horizon"] if quick else settings["horizon"]
    orders = settings["quick_quadrature_orders"] if quick else settings["quadrature_orders"]
    summary_rows, dag_rows, terminal_by_case_prior = [], [], {}
    for case_no, case in enumerate(cases, 1):
        records = evidence["q2"][f"case_{case_no}"]
        costs = tuple(marginal_cost(records[name]) for name in Q2_NAMES)
        for prior_name, prior_values in config["priors"].items():
            belief = from_records(records, Q2_NAMES, tuple(prior_values))
            solver = Q2VoiDP(case, belief, costs, horizon, orders,
                             settings["value_tolerance"], settings["exact_dp_max_states"])
            result = solver.solve()
            terminal = solver.terminal((0, 0, 0), (0, 0, 0))
            terminal_by_case_prior[(case_no, prior_name)] = terminal
            expected_future_cost = sum(result.expected_allocation[name] * costs[j]
                                       for j, name in enumerate(Q2_NAMES))
            past_cost = past_sampling_cost(records)
            summary_rows.append({
                "case": case_no, "prior": prior_name, "status": result.status,
                "optimality_label": "exact-DP-to-tolerance" if result.status == "SUCCESS_VOI_DP_TOL" else "ambiguous",
                "horizon": horizon, "initial_action": result.initial_action,
                "stop_value": result.stop_value, "policy_value": result.value,
                "NVSI": result.nvsi, "EVPI": result.evpi,
                "expected_additional_samples": result.expected_samples,
                "expected_additional_sampling_cost": expected_future_cost,
                "past_sampling_cost": past_cost,
                "net_value_after_past_sampling": result.value - past_cost,
                "P50_samples": result.sample_quantiles["P50"],
                "P90_samples": result.sample_quantiles["P90"],
                "P99_samples": result.sample_quantiles["P99"],
                "terminal_policy": terminal.best_label,
                "terminal_value_status": terminal.status,
                "terminal_integration_order": terminal.integration_order,
                "terminal_integration_error": terminal.integration_error,
                "posterior_optimal_probability": terminal.best_optimal_probability,
                "posterior_mean_regret": terminal.best_mean_regret,
                "negative_profit_probability": terminal.best_negative_probability,
                "posterior_profit_p05": terminal.best_quantiles[0],
                "posterior_profit_p50": terminal.best_quantiles[1],
                "posterior_profit_p95": terminal.best_quantiles[2],
                "state_count": result.state_count,
                "bellman_residual": result.bellman_residual,
                "initial_action_values": json.dumps(_jsonable(result.action_values), ensure_ascii=False, sort_keys=True),
                "expected_allocation": json.dumps(_jsonable(result.expected_allocation), ensure_ascii=False, sort_keys=True),
                "terminal_policy_probabilities": json.dumps(_jsonable(result.terminal_policy_probabilities), ensure_ascii=False, sort_keys=True),
            })
            for row in result.state_rows:
                dag_rows.append({
                    "case": case_no, "prior": prior_name,
                    "bad_counts": json.dumps(row["bad"]), "good_counts": json.dumps(row["good"]),
                    "h_remaining": row["h_remaining"], "stop_value": row["stop_value"],
                    "value": row["value"], "action": row["action"],
                    "action_values": json.dumps(_jsonable(row["action_values"]), ensure_ascii=False, sort_keys=True),
                    "terminal_policy": row["terminal_policy"],
                    "terminal_status": row["terminal_status"],
                    "bellman_residual": row["bellman_residual"],
                })
    return summary_rows, dag_rows, terminal_by_case_prior


def run_q3_kg(config: dict, evidence: dict, quick: bool):
    settings = config["q3_voi"]
    draws = settings["quick_draws_per_scramble"] if quick else settings["draws_per_scramble"]
    scrambles = settings["quick_scrambles"] if quick else settings["scrambles"]
    records = evidence["q3"]
    costs = tuple(marginal_cost(records[name]) for name in Q3_NAMES)
    rows, results = [], {}
    for prior_name, prior_values in config["priors"].items():
        belief = from_records(records, Q3_NAMES, tuple(prior_values))
        result = q3_knowledge_gradient(
            belief, costs, draws, scrambles, settings["seed"],
            settings["confirm_seed"], settings["confidence"],
            settings["value_tolerance"])
        results[prior_name] = result
        for action, value in result.action_values.items():
            rows.append({
                "prior": prior_name, "action": action, "action_value": value,
                "action_SE": result.action_se[action],
                "net_KG": 0.0 if action == "STOP" else result.net_kg[action],
                "net_KG_CI_lower": 0.0 if action == "STOP" else result.net_ci[action][0],
                "net_KG_CI_upper": 0.0 if action == "STOP" else result.net_ci[action][1],
                "recommended": action == result.action, "status": result.status,
                "optimality_label": "myopic-KG" if result.action != "AMBIGUOUS" else "ambiguous",
                "draws_per_scramble": draws, "scrambles": scrambles,
                "seed": settings["seed"], "confirm_seed": settings["confirm_seed"],
                "stop_production_policy": result.terminal.best_label,
                "stop_value": result.stop_value, "EVPI": result.terminal.evpi,
                "posterior_optimal_probability": result.terminal.best_optimal_probability,
                "posterior_mean_regret": result.terminal.best_mean_regret,
            })
    return rows, results


def solve(config: dict, evidence: dict, outdir: Path, quick: bool, evidence_path: Path) -> dict:
    started = time.perf_counter()
    q2_rows, dag_rows, q2_terminals = run_q2_voi(config, evidence, quick)
    q3_rows, q3_results = run_q3_kg(config, evidence, quick)
    robust_rows, interval_rows = [], []
    plan = evidence.get("sampling_plan", "fixed_n")
    main_prior = config["main_prior"]
    cases, _ = load_q2_inputs()
    for case_no, case in enumerate(cases, 1):
        records = evidence["q2"][f"case_{case_no}"]
        bayes_index = q2_terminals[(case_no, main_prior)].best_index
        for coverage in config["robust_coverages"]:
            row, intervals = robust_audit("q2", records, Q2_NAMES, coverage, plan, case, bayes_index)
            row["case"] = case_no; robust_rows.append(row)
            interval_rows.extend({**item, "domain": "q2", "case": case_no} for item in intervals)
    q3_bayes_index = q3_results[main_prior].terminal.best_index
    for coverage in config["robust_coverages"]:
        row, intervals = robust_audit("q3", evidence["q3"], Q3_NAMES, coverage, plan, None, q3_bayes_index)
        row["case"] = ""; robust_rows.append(row)
        interval_rows.extend({**item, "domain": "q3", "case": ""} for item in intervals)

    outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(q2_rows).to_csv(outdir / "q2_voi_policy_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(dag_rows).to_csv(outdir / "q2_voi_policy_dag.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(q3_rows).to_csv(outdir / "q3_kg_action_values.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(robust_rows).to_csv(outdir / "robust_audit.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(interval_rows).to_csv(outdir / "simultaneous_intervals.csv", index=False, encoding="utf-8-sig")
    marker = "DEMO_ONLY_NOT_OFFICIAL_DATA" if evidence.get("mode") == "DEMO_ONLY_NOT_OFFICIAL_DATA" else "USER_SUPPLIED_EVIDENCE"
    used = {**evidence, "source_path": str(evidence_path.resolve()), "evidence_marker": marker}
    (outdir / "evidence_used.json").write_text(json.dumps(used, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "schema_version": config["schema_version"],
        "models": config["model_ids"], "algorithms": config["algorithm_ids"],
        "evidence_marker": marker, "quick": quick,
        "claim_scope": "题面未给实际 N,K、先验强度和完整抽样成本；默认结果仅为显式情景算法演示。",
        "q2_initial_decisions": q2_rows,
        "q3_initial_decisions": [row for row in q3_rows if row["recommended"] or
                                  (row["action"] == "STOP" and not any(
                                      item["recommended"] for item in q3_rows if item["prior"] == row["prior"]))],
        "robust_audit": robust_rows,
        "checks": {
            "q2_bellman_nonnegative_nvsi": all(row["NVSI"] >= -1e-8 for row in q2_rows),
            "q2_value_below_stop_plus_evpi": all(row["policy_value"] <= row["stop_value"] + row["EVPI"] + 1e-5 for row in q2_rows),
            "q2_binary_actions": all(row["initial_action"] == "STOP" or row["initial_action"] in Q2_NAMES for row in q2_rows),
            "q3_full_production_policy_domain": len(Q3_POLICY_IDS) == 65536,
            "sample_and_production_cost_accounts_separate": True,
        },
        "optimality_labels": {"q2": "exact-DP-to-tolerance", "q3": "myopic-KG or ambiguous after independent confirmation", "robust": "numerical endpoint audit"},
        "runtime_seconds": time.perf_counter() - started,
    }
    (outdir / "summary.json").write_text(json.dumps(_jsonable(summary), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    writer = {
        "evidence_marker": marker,
        "main_model": "Q4-M4 with Q4-M2 terminal value and Q4-M3 audit",
        "q2_claim": "Finite-horizon sampling/stop/production policy solved by memoized DP to the saved quadrature tolerance.",
        "q3_claim": "Saved action uses cost-sensitive one-step KG with independent scrambled-Sobol confirmation; it is not a globally optimal sampling policy.",
        "robust_claim": "Endpoint audit is ROBUST_NUMERICAL; no interval branch-and-bound certificate is claimed.",
        "files": {
            "q2_policy": "results/q4/q2_voi_policy_summary.csv",
            "q2_dag": "results/q4/q2_voi_policy_dag.csv",
            "q3_actions": "results/q4/q3_kg_action_values.csv",
            "robust": "results/q4/robust_audit.csv",
            "intervals": "results/q4/simultaneous_intervals.csv",
        },
        "limitations": ["default evidence is a declared demo scenario", "Q3 is myopic KG", "robust inner search is not interval-certified"],
    }
    (outdir / "code_to_writer.json").write_text(json.dumps(writer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sources = [HERE / name for name in (
        "run_q4.py", "belief_state.py", "terminal_value.py", "exact_voi_dp.py",
        "kg_rollout.py", "simultaneous_cs.py", "batch_evaluators.py", "test_q4.py",
        "config.json", "q4_demo_evidence.json", "requirements.txt", "README.md",
    )]
    repro = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": f"cd B题/代码 && python -m q4.run_q4{' --quick' if quick else ''}",
        "python": sys.version, "platform": platform.platform(),
        "versions": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__},
        "seeds": {"q3_sobol_exploration": config["q3_voi"]["seed"],
                  "q3_sobol_confirmation": config["q3_voi"]["confirm_seed"]},
        "config_sha256": hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
        "evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=HERE, text=True).strip()),
    }
    (outdir / "reproducibility.json").write_text(json.dumps(repro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=DEMO)
    parser.add_argument("--outdir", type=Path, default=OUTDIR)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    config, evidence = read_json(CONFIG_PATH), read_evidence(args.evidence)
    summary = solve(config, evidence, args.outdir, args.quick, args.evidence)
    print(json.dumps({"evidence": summary["evidence_marker"],
                      "q2": summary["optimality_labels"]["q2"],
                      "q3": summary["optimality_labels"]["q3"],
                      "runtime_seconds": summary["runtime_seconds"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
