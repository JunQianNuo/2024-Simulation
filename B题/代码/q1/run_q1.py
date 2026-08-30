"""Q1-M6/A2：AQL-LTPD 双风险截尾序贯验收设计。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

from .exact_path_dp import (
    BoundaryPlan, evaluate, feasible_terminal_cutoffs, fixed_plan_as_boundary,
    llr_boundaries, preterminal,
)
from .fixed_binomial_plan import minimum_plan

HERE = Path(__file__).resolve().parent
CODE_DIR = HERE.parent
DEFAULT_OUT = CODE_DIR / "results" / "q1"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(cfg: dict) -> None:
    if cfg.get("model_id") != "Q1-M6" or cfg.get("algorithm_id") != "Q1-A2":
        raise ValueError("STALE_MODEL_RESULT: Q1 config must be Q1-M6/Q1-A2")
    if not 0 < cfg["p0"] < min(cfg["p1_values"]) < 1:
        raise ValueError("INVALID_DATA: require p0 < every p1")
    if cfg["main_p1"] not in cfg["p1_values"] or cfg["main_kappa"] not in cfg["kappa_values"]:
        raise ValueError("INVALID_DATA: main scenario missing from sensitivity grid")
    if min(cfg["kappa_values"]) < 1:
        raise ValueError("INVALID_DATA: kappa must be at least one")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"empty output: {path}")
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def plan_hash(plan: BoundaryPlan) -> str:
    payload = json.dumps(asdict(plan), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _candidate_n(n_fixed: int, kappa: float, fractions: list[float]) -> list[int]:
    cap = int(math.floor(kappa * n_fixed + 1e-12))
    values = {max(1, int(round(cap * fraction))) for fraction in fractions}
    values.update({n_fixed, cap})
    return sorted(n for n in values if n <= cap)


def _terminal_choice(rows: list[tuple[int, float, float]], alpha: float, beta: float):
    return min(rows, key=lambda row: (max(row[1] / alpha, row[2] / beta),
                                      abs(row[1] / alpha - row[2] / beta), row[0]))


def _objective(plan: BoundaryPlan, p_grid: np.ndarray) -> tuple[float, float, list[dict]]:
    rows = [evaluate(plan, float(p)) for p in p_grid]
    index = int(np.argmax([row["ASN"] for row in rows]))
    return float(rows[index]["ASN"]), float(p_grid[index]), rows


def search_plan(cfg: dict, p1: float, kappa: float, quick: bool = False) -> tuple[dict, list[dict]]:
    p0, alpha, beta = cfg["p0"], cfg["alpha"], cfg["beta"]
    baseline = minimum_plan(p0, p1, alpha, beta)
    n_fixed, c_fixed = int(baseline["n_fixed"]), int(baseline["c_fixed"])
    fixed = fixed_plan_as_boundary(p0, p1, n_fixed, c_fixed)
    fixed_eval = evaluate(fixed, p0), evaluate(fixed, p1)
    candidates = [{
        "plan": fixed, "producer_risk": fixed_eval[0]["P_reject"],
        "consumer_risk": fixed_eval[1]["P_accept"], "proxy_asn": float(n_fixed),
    }]

    alpha0, beta0 = cfg["alpha"], cfg["beta"]
    h_a0 = math.log(beta0 / (1 - alpha0))
    h_r0 = math.log((1 - beta0) / alpha0)
    search = cfg["search"]
    accept_offsets = search["accept_offsets"][::2] if quick else search["accept_offsets"]
    reject_offsets = search["reject_offsets"][::2] if quick else search["reject_offsets"]
    n_values = _candidate_n(n_fixed, kappa, search["n_fractions"])
    if quick:
        n_values = sorted(set([n_fixed, n_values[max(0, len(n_values) // 2)]]))
    p_dagger = -math.log((1 - p1) / (1 - p0)) / math.log(p1 * (1 - p0) / (p0 * (1 - p1)))
    seen = set()
    audit_rows = []
    for a_offset in accept_offsets:
        for r_offset in reject_offsets:
            h_accept, h_reject = h_a0 + a_offset, h_r0 + r_offset
            if h_accept >= h_reject:
                continue
            for n_max in n_values:
                accept, reject = llr_boundaries(n_max, p0, p1, h_accept, h_reject)
                signature = (n_max, accept, reject)
                if signature in seen:
                    continue
                seen.add(signature)
                shell = BoundaryPlan(p0, p1, n_max, 0, accept, reject,
                                     h_accept, h_reject, "calibrated-truncated-sprt")
                at_p0, at_p1 = preterminal(shell, p0), preterminal(shell, p1)
                cutoffs = feasible_terminal_cutoffs(at_p0, at_p1, n_max, alpha, beta)
                audit_rows.append({
                    "p1": p1, "kappa": kappa, "N_max": n_max,
                    "h_accept": h_accept, "h_reject": h_reject,
                    "feasible_terminal_count": len(cutoffs),
                })
                if not cutoffs:
                    continue
                cutoff, producer, consumer = _terminal_choice(cutoffs, alpha, beta)
                plan = BoundaryPlan(p0, p1, n_max, cutoff, accept, reject,
                                    h_accept, h_reject, "calibrated-truncated-sprt")
                candidates.append({
                    "plan": plan, "producer_risk": producer, "consumer_risk": consumer,
                    "proxy_asn": float(evaluate(plan, p_dagger)["ASN"]),
                })

    shortlist = sorted(candidates, key=lambda row: (row["proxy_asn"], row["plan"].n_max,
                                                      plan_hash(row["plan"])))[:search["shortlist"]]
    if candidates[0] not in shortlist:
        shortlist.append(candidates[0])
    points = 25 if quick else int(search["asn_grid_points"])
    p_grid = np.unique(np.r_[np.linspace(p0, p1, points), p_dagger])
    for row in shortlist:
        row["J_grid"], row["p_worst_grid"], _ = _objective(row["plan"], p_grid)
        endpoint_asn = [evaluate(row["plan"], p)["ASN"] for p in (p0, p1)]
        row["endpoint_max_asn"] = max(endpoint_asn)
        row["endpoint_mean_asn"] = sum(endpoint_asn) / 2
    chosen = min(shortlist, key=lambda row: (
        row["J_grid"], row["plan"].n_max, row["endpoint_max_asn"],
        row["endpoint_mean_asn"], plan_hash(row["plan"]),
    ))
    chosen.update({
        "n_fixed": n_fixed, "c_fixed": c_fixed,
        "fixed_producer_risk": baseline["producer_risk"],
        "fixed_consumer_risk": baseline["consumer_risk"],
        "asn_saving_vs_fixed": 1 - chosen["J_grid"] / n_fixed,
        "p_dagger": p_dagger,
        "status": "SUCCESS_LOCAL_CALIBRATION",
        "optimality_scope": "predeclared truncated-SPRT calibration grid; gray-zone ASN supremum evaluated on an adaptive grid",
        "candidate_count": len(candidates), "shortlist_count": len(shortlist),
    })
    return chosen, audit_rows


def _plan_row(result: dict) -> dict:
    plan = result["plan"]
    return {
        "p0": plan.p0, "p1": plan.p1, "kappa": result["kappa"],
        "status": result["status"], "family": plan.family,
        "plan_hash": plan_hash(plan), "n_fixed": result["n_fixed"],
        "c_fixed": result["c_fixed"], "N_max": plan.n_max,
        "c_N": plan.terminal_cutoff, "h_accept": plan.h_accept,
        "h_reject": plan.h_reject, "producer_risk": result["producer_risk"],
        "consumer_risk": result["consumer_risk"], "J_ASN_grid": result["J_grid"],
        "p_worst_grid": result["p_worst_grid"],
        "endpoint_max_ASN": result["endpoint_max_asn"],
        "endpoint_mean_ASN": result["endpoint_mean_asn"],
        "ASN_saving_vs_fixed": result["asn_saving_vs_fixed"],
        "candidate_count": result["candidate_count"],
    }


def _git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=HERE, text=True).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def solve(cfg: dict, outdir: Path, quick: bool = False) -> dict:
    validate_config(cfg)
    started = time.perf_counter()
    results, search_audit = [], []
    for p1 in cfg["p1_values"]:
        for kappa in cfg["kappa_values"]:
            result, audit = search_plan(cfg, p1, kappa, quick)
            result["kappa"] = kappa
            results.append(result)
            search_audit.extend(audit)

    plan_rows = [_plan_row(result) for result in results]
    boundary_rows, oc_rows = [], []
    oc_points = 31 if quick else int(cfg["search"]["oc_grid_points"])
    for result in results:
        plan = result["plan"]
        key = {"p1": plan.p1, "kappa": result["kappa"], "plan_hash": plan_hash(plan)}
        for t in range(1, plan.n_max + 1):
            boundary_rows.append({
                **key, "n": t,
                "k_accept_max": plan.terminal_cutoff if t == plan.n_max else
                                ("" if plan.accept_max[t] < 0 else plan.accept_max[t]),
                "k_reject_min": plan.terminal_cutoff + 1 if t == plan.n_max else
                                ("" if plan.reject_min[t] > t else plan.reject_min[t]),
                "terminal": t == plan.n_max,
            })
        p_grid = np.unique(np.r_[np.linspace(0, 1, oc_points), cfg["p0"], plan.p1,
                                 result["p_worst_grid"]])
        previous_accept = math.inf
        for p in p_grid:
            row = evaluate(plan, float(p))
            if row["mass_residual"] > cfg["tolerances"]["mass"]:
                raise RuntimeError("PROBABILITY_CONSERVATION_FAILED")
            if row["P_accept"] > previous_accept + cfg["tolerances"]["monotonicity"]:
                raise RuntimeError("OC_MONOTONICITY_FAILED")
            previous_accept = row["P_accept"]
            oc_rows.append({**key, **row})

    main = next(result for result in results if result["plan"].p1 == cfg["main_p1"]
                and result["kappa"] == cfg["main_kappa"])
    main_p0 = evaluate(main["plan"], cfg["p0"])
    main_p1 = evaluate(main["plan"], cfg["main_p1"])
    if main_p0["P_reject"] > cfg["alpha"] + cfg["tolerances"]["risk"] or \
            main_p1["P_accept"] > cfg["beta"] + cfg["tolerances"]["risk"]:
        raise RuntimeError("INFEASIBLE_RISK_PLAN")

    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "fixed_binomial_baselines.csv", [{
        "p0": cfg["p0"], "p1": result["plan"].p1,
        "n_fixed": result["n_fixed"], "c_fixed": result["c_fixed"],
        "producer_risk": result["fixed_producer_risk"],
        "consumer_risk": result["fixed_consumer_risk"],
    } for result in results[::len(cfg["kappa_values"])]])
    write_csv(outdir / "sequential_plans.csv", plan_rows)
    write_csv(outdir / "decision_boundaries.csv", boundary_rows)
    write_csv(outdir / "operating_characteristics.csv", oc_rows)
    write_csv(outdir / "calibration_search_audit.csv", search_audit)

    summary = {
        "problem": "2024-CUMCM-B-Q1", "model": "Q1-M6", "algorithm": "Q1-A2",
        "status": main["status"], "quick": quick,
        "main_scenario": _plan_row(main),
        "main_endpoint_checks": {"at_p0": main_p0, "at_p1": main_p1},
        "sensitivity_scenarios": plan_rows,
        "termination": "binary accept/reject by N_max; no undecided action",
        "checks": {
            "all_16_scenarios_present": len(plan_rows) == len(cfg["p1_values"]) * len(cfg["kappa_values"]),
            "all_producer_risks_feasible": all(row["producer_risk"] <= cfg["alpha"] + cfg["tolerances"]["risk"] for row in plan_rows),
            "all_consumer_risks_feasible": all(row["consumer_risk"] <= cfg["beta"] + cfg["tolerances"]["risk"] for row in plan_rows),
            "binary_terminal_rule": True,
            "maximum_probability_residual": max(row["mass_residual"] for row in oc_rows),
        },
        "optimality_claim": main["optimality_scope"],
        "limitations": [
            "p1 is an engineering scenario rather than problem-given data",
            "threshold search is a declared local calibration grid",
            "gray-zone ASN objective is grid evaluated, not interval-certified",
        ],
        "runtime_seconds": time.perf_counter() - started,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    writer = {
        "status": main["status"], "model": "Q1-M6", "algorithm": "Q1-A2",
        "claim_scope": main["optimality_scope"],
        "main_scenario": _plan_row(main),
        "evidence": {
            "fixed_baselines": "results/q1/fixed_binomial_baselines.csv",
            "plans": "results/q1/sequential_plans.csv",
            "boundaries": "results/q1/decision_boundaries.csv",
            "oc_asn": "results/q1/operating_characteristics.csv",
        },
        "warning": "p1=0.13 and kappa=1 are declared scenarios. The rule always ends in accept or reject; old undecided/Pareto conclusions are stale.",
    }
    (outdir / "code_to_writer.json").write_text(json.dumps(writer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_files = [HERE / name for name in (
        "run_q1.py", "fixed_binomial_plan.py", "exact_path_dp.py", "test_q1.py",
        "config.json", "requirements-q1.txt", "README.md",
    )]
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": f"cd B题/代码 && python -m q1.run_q1{' --quick' if quick else ''}",
        "python": sys.version, "platform": platform.platform(),
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__},
        "random_seed": None, "git_commit": _git_value("rev-parse", "HEAD"),
        "git_dirty": bool(_git_value("status", "--porcelain")),
        "config_sha256": hashlib.sha256((HERE / "config.json").read_bytes()).hexdigest(),
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source_files},
    }
    (outdir / "repro_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=HERE / "config.json")
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    summary = solve(read_json(args.config), args.outdir, args.quick)
    print(json.dumps(summary["main_scenario"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
