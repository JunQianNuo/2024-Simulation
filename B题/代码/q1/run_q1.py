"""Solve Q1-M5 with official Bernoulli CS, exact path DP and Pareto search."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import beta, binom

from .confidence_sequence import crosscheck_endpoints, fixed_sample_baselines, official_boundaries

HERE = Path(__file__).resolve().parent
CODE_DIR = HERE.parent
DEFAULT_OUT = CODE_DIR / "results" / "q1"


def load_config(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    p = cfg["problem"]
    if not all(0 < p[key] < 1 for key in ("p0", "alpha_reject", "alpha_accept")):
        raise ValueError("INVALID_DATA: probabilities must be in (0,1)")
    if len(cfg["p_grid"]) != 13 or sorted(cfg["p_grid"]) != cfg["p_grid"]:
        raise ValueError("INVALID_DATA: the declared 13-point p grid is required")
    return cfg


def candidates(cfg: dict) -> list[tuple[int, int]]:
    result = [(t, n) for t in cfg["t_opt"] for n in cfg["n_max"] if n >= t]
    if len(result) != 34:
        raise ValueError(f"INVALID_DATA: expected 34 candidates, got {len(result)}")
    return result


def evaluate_cutoffs(p: float, accept_max: np.ndarray, reject_min: np.ndarray,
                     cutoffs: list[int]) -> dict[int, dict[str, float | int]]:
    top = max(cutoffs)
    q = np.zeros(top + 1)
    q[0] = 1.0
    accepted = rejected = asn = 0.0
    stop_pmf = np.zeros(top + 1)
    output = {}

    for t in range(1, top + 1):
        asn += float(q[:t].sum())
        nxt = np.zeros(t + 1)
        nxt[:t] += (1.0 - p) * q[:t]
        nxt[1:] += p * q[:t]
        k = np.arange(t + 1)
        acc, rej = k <= accept_max[t], k >= reject_min[t]
        a_mass, r_mass = float(nxt[acc].sum()), float(nxt[rej].sum())
        accepted += a_mass
        rejected += r_mass
        stop_pmf[t] = a_mass + r_mass
        nxt[acc | rej] = 0.0
        q[:t + 1] = nxt

        if t in cutoffs:
            undecided = float(nxt.sum())
            total = accepted + rejected + undecided
            pmf = stop_pmf[:t + 1].copy()
            pmf[t] += undecided
            cdf = np.cumsum(pmf)
            output[t] = {
                "p": p, "ASN": asn,
                "P50": int(np.searchsorted(cdf, 0.5 * total)),
                "P90": int(np.searchsorted(cdf, 0.9 * total)),
                "P_accept": accepted, "P_reject": rejected,
                "P_undecided": undecided, "mass_residual": abs(total - 1.0),
            }
    return output


def normalize_weights(raw: list[float] | None, size: int) -> np.ndarray:
    w = np.ones(size) if raw is None else np.asarray(raw, dtype=float)
    if w.size != size or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("INVALID_DATA: invalid weight scheme")
    return w / w.sum()


def pareto(rows: list[dict], scheme: str) -> list[dict]:
    a_key, u_key = f"ASN_w[{scheme}]", f"U_w[{scheme}]"
    front = []
    for row in rows:
        dominated = any(
            (other[a_key] <= row[a_key] and other[u_key] <= row[u_key])
            and (other[a_key] < row[a_key] or other[u_key] < row[u_key])
            for other in rows if other is not row
        )
        if not dominated:
            front.append(row)
    return sorted(front, key=lambda x: x[a_key])


def recommendations(front: list[dict], scheme: str = "equal") -> dict[str, object]:
    a = np.array([r[f"ASN_w[{scheme}]"] for r in front])
    u = np.array([r[f"U_w[{scheme}]"] for r in front])
    an = (a - a.min()) / (np.ptp(a) or 1.0)
    un = (u - u.min()) / (np.ptp(u) or 1.0)
    ideal_idx = int(np.argmin(np.hypot(an, un)))
    curve_idx = ideal_idx
    if len(front) >= 3:
        curve_idx = int(np.argmax(np.linalg.norm(np.diff(np.c_[an, un], n=2, axis=0), axis=1))) + 1
    return {
        "sample_saving": front[0], "balanced": front[ideal_idx],
        "low_undecided": front[-1], "knee_agreement": ideal_idx == curve_idx,
        "ideal_index": ideal_idx, "curvature_index": curve_idx,
    }


def group_sequential_baseline(p_grid: list[float]) -> list[dict]:
    stages = [40, 80, 160, 320, 800]
    alpha_r = [0.01] * 5
    alpha_a = [0.04, 0.025, 0.015, 0.012, 0.008]
    plan = []
    for n, ar, aa in zip(stages, alpha_r, alpha_a):
        acc = [k for k in range(n + 1) if (1.0 if k == n else beta.ppf(1 - aa, k + 1, n - k)) <= 0.1]
        rej = [k for k in range(n + 1) if (0.0 if k == 0 else beta.ppf(ar, k, n - k + 1)) > 0.1]
        plan.append((n, max(acc, default=-1), min(rej, default=n + 1)))

    rows = []
    for p in p_grid:
        alive, prev, asn = np.array([1.0]), 0, 0.0
        accepted = rejected = 0.0
        for n, acc, rej in plan:
            asn += (n - prev) * float(alive.sum())
            alive = np.convolve(alive, binom.pmf(np.arange(n - prev + 1), n - prev, p))
            k = np.arange(n + 1)
            accepted += float(alive[k <= acc].sum())
            rejected += float(alive[k >= rej].sum())
            alive[(k <= acc) | (k >= rej)] = 0.0
            prev = n
        rows.append({"p": p, "ASN": asn, "P_undecided": float(alive.sum())})
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"empty output: {path}")
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=HERE, text=True).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plot_front(rows: list[dict], front: list[dict], rec: dict, outdir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.scatter([r["ASN_w[equal]"] for r in rows], [r["U_w[equal]"] for r in rows],
               s=28, color="#9aa0a6", label="34 candidates")
    ax.plot([r["ASN_w[equal]"] for r in front], [r["U_w[equal]"] for r in front],
            "o-", color="#1f77b4", label="Pareto front")
    colors = {"sample_saving": "#2ca02c", "balanced": "#d62728", "low_undecided": "#9467bd"}
    for name, color in colors.items():
        row = rec[name]
        ax.scatter(row["ASN_w[equal]"], row["U_w[equal]"], s=85, color=color, label=name)
    ax.set(xlabel="Weighted average sample number (ASN)", ylabel="Weighted undecided probability",
           title="Q1 finite-grid Pareto front")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "pareto_front.svg")
    fig.savefig(outdir / "pareto_front.png", dpi=220)
    plt.close(fig)


def solve(cfg: dict, outdir: Path, quick: bool = False) -> dict:
    problem = cfg["problem"]
    grid = candidates(cfg)
    if quick:
        grid = [(50, 200), (200, 400)]
    by_t: dict[int, list[int]] = {}
    for t_opt, n_max in grid:
        by_t.setdefault(t_opt, []).append(n_max)

    oc_rows, objective_rows, cross_rows = [], [], []
    cache = {}
    for t_opt, cutoffs in by_t.items():
        accept, reject = official_boundaries(
            max(cutoffs), problem["p0"], problem["alpha_reject"], problem["alpha_accept"], t_opt
        )
        cache[t_opt] = (accept, reject)
        probe_t = sorted(set(min(max(cutoffs), x) for x in (25, 50, 100, 200, 400, 800, 1600, 3200)))
        states = [(t, min(t, max(0, int(round(problem["p0"] * t)) + d)))
                  for t in probe_t for d in (-2, 0, 2)]
        cross_rows.extend(crosscheck_endpoints(
            t_opt, states, problem["alpha_reject"], problem["alpha_accept"]
        ))
        evaluated = {n: [] for n in cutoffs}
        for true_p in cfg["p_grid"]:
            points = evaluate_cutoffs(true_p, accept, reject, cutoffs)
            for n in cutoffs:
                row = {"t_opt": t_opt, "N_max": n, **points[n], "status": "SUCCESS_EXACT"}
                oc_rows.append(row)
                evaluated[n].append(row)
        for n in cutoffs:
            hit = np.flatnonzero(accept[:n + 1] >= 0)
            row = {"t_opt": t_opt, "N_max": n,
                   "first_accept_all_good": int(hit[0]) if hit.size else None,
                   "status": "SUCCESS_EXACT"}
            for name, raw in cfg["weights"].items():
                w = normalize_weights(raw, len(cfg["p_grid"]))
                row[f"ASN_w[{name}]"] = float(np.dot(w, [x["ASN"] for x in evaluated[n]]))
                row[f"U_w[{name}]"] = float(np.dot(w, [x["P_undecided"] for x in evaluated[n]]))
            objective_rows.append(row)

    worst_mass = max(r["mass_residual"] for r in oc_rows)
    worst_cs = max(r["max_abs_error"] for r in cross_rows)
    at_threshold = [r for r in oc_rows if r["p"] == problem["p0"]]
    worst_false_reject = max(r["P_reject"] for r in at_threshold)
    worst_false_accept_limit = max(r["P_accept"] for r in at_threshold)
    if worst_mass > cfg["tolerances"]["mass"]:
        raise RuntimeError(f"PROB_CONSERVATION_FAILED: {worst_mass:.3e}")
    if worst_cs > cfg["tolerances"]["cs_endpoint"]:
        raise RuntimeError(f"CS_CROSSCHECK_FAILED: {worst_cs:.3e}")
    if worst_false_reject > problem["alpha_reject"] + 1e-10:
        raise RuntimeError("ERROR_CONSTRAINT_FAILED: false rejection")
    if worst_false_accept_limit > problem["alpha_accept"] + 1e-10:
        raise RuntimeError("ERROR_CONSTRAINT_FAILED: false acceptance")

    fronts = {name: pareto(objective_rows, name) for name in cfg["weights"]}
    rec = recommendations(fronts["equal"])
    chosen = rec["balanced"]
    accept, reject = cache[chosen["t_opt"]]
    boundary_rows = [
        {"n": t, "k_accept_max": None if accept[t] < 0 else int(accept[t]),
         "k_reject_min": None if reject[t] > t else int(reject[t])}
        for t in range(1, chosen["N_max"] + 1)
    ]

    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "operating_characteristics.csv", oc_rows)
    write_csv(outdir / "candidate_objectives.csv", objective_rows)
    write_csv(outdir / "pareto_front.csv", fronts["equal"])
    write_csv(outdir / "decision_boundary.csv", boundary_rows)
    write_csv(outdir / "cs_crosscheck.csv", cross_rows)
    recommendation_rows = [
        {"type": name, **rec[name]} for name in ("sample_saving", "balanced", "low_undecided")
    ]
    write_csv(outdir / "recommendations.csv", recommendation_rows)
    sensitivity_rows = []
    for scheme, front in fronts.items():
        scheme_rec = recommendations(front, scheme)
        for kind in ("sample_saving", "balanced", "low_undecided"):
            row = scheme_rec[kind]
            sensitivity_rows.append({
                "weight_scheme": scheme, "recommendation_type": kind,
                "t_opt": row["t_opt"], "N_max": row["N_max"],
                "ASN_w": row[f"ASN_w[{scheme}]"], "U_w": row[f"U_w[{scheme}]"],
            })
    write_csv(outdir / "sensitivity_recommendations.csv", sensitivity_rows)

    base = group_sequential_baseline(cfg["p_grid"])
    w = normalize_weights(None, len(base))
    baseline_row = [{
        "method": "Q1-BL-GSCP-5",
        "ASN_w[equal]": float(np.dot(w, [x["ASN"] for x in base])),
        "U_w[equal]": float(np.dot(w, [x["P_undecided"] for x in base])),
        "role": "external_baseline_not_in_pareto_grid",
    }]
    write_csv(outdir / "baseline_comparison.csv", baseline_row)
    plot_front(objective_rows, fronts["equal"], rec, outdir)

    baseline = fixed_sample_baselines()
    if abs(baseline["U_0.90(22,0)"] - 0.0994) > 5e-4 or abs(baseline["L_0.95(2,2)"] - 0.2236) > 5e-4:
        raise RuntimeError("fixed-sample baseline check failed")
    summary = {
        "problem": "2024-CUMCM-B-Q1", "model": "Q1-M5", "algorithm": "Q1-A1",
        "status": "SUCCESS_EXACT", "candidate_count": len(grid),
        "representative_p": cfg["p_grid"], "baseline": baseline,
        "worst_mass_residual": worst_mass, "worst_cs_endpoint_error": worst_cs,
        "error_constraint_check": {
            "max_reject_at_p0": worst_false_reject,
            "max_accept_at_p0_right_limit": worst_false_accept_limit,
        },
        "pareto_sizes": {k: len(v) for k, v in fronts.items()},
        "recommendations": {
            name: {"t_opt": rec[name]["t_opt"], "N_max": rec[name]["N_max"],
                   "ASN_w_equal": rec[name]["ASN_w[equal]"], "U_w_equal": rec[name]["U_w[equal]"]}
            for name in ("sample_saving", "balanced", "low_undecided")
        },
        "knee_selection": {"criteria_agree": rec["knee_agreement"],
                           "ideal_index": rec["ideal_index"], "curvature_index": rec["curvature_index"]},
        "optimality_claim": "exact Pareto front within the declared 34-candidate finite grid only",
        "undecided_action": "UNDECIDED_CAP; no unbudgeted continued inspection",
    }
    (outdir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    writer_handoff = {
        "status": "SUCCESS_EXACT",
        "claim": summary["optimality_claim"],
        "balanced_reference": summary["recommendations"]["balanced"],
        "alternative_recommendations": {
            "sample_saving": summary["recommendations"]["sample_saving"],
            "low_undecided": summary["recommendations"]["low_undecided"],
        },
        "evidence": {
            "candidate_objectives": "results/q1/candidate_objectives.csv",
            "operating_characteristics": "results/q1/operating_characteristics.csv",
            "decision_boundary": "results/q1/decision_boundary.csv",
            "crosscheck": "results/q1/cs_crosscheck.csv",
            "sensitivity": "results/q1/sensitivity_recommendations.csv",
            "figure": "results/q1/pareto_front.svg",
        },
        "warning": "UNDECIDED_CAP is evidence insufficiency; do not continue sampling outside the declared rule.",
    }
    (outdir / "code_to_writer.json").write_text(
        json.dumps(writer_handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    import confseq
    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
        "platform": platform.platform(), "random_seed": None,
        "confseq": {"version": "official source commit 5ffe733ca2447a2e28c2c91f3b00086173f2ab2c", "required": True,
                    "source": "https://github.com/gostevehoward/confseq",
                    "official_reference_value": float(confseq.boundaries.beta_binomial_log_mixture(10, 100, 100, 0.2, 0.8))},
        "git_commit": git_value("rev-parse", "HEAD"), "git_dirty": bool(git_value("status", "--porcelain")),
        "inputs": {
            str(HERE / "config.json"): sha256(HERE / "config.json"),
            str(CODE_DIR.parent / "B题.pdf"): sha256(CODE_DIR.parent / "B题.pdf"),
        },
        "command": "cd B题/代码 && python -m q1.run_q1",
        "tolerances": cfg["tolerances"],
    }
    (outdir / "repro_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="CUMCM 2024 B Q1 exact finite-grid search")
    parser.add_argument("--config", type=Path, default=HERE / "config.json")
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    summary = solve(load_config(args.config), args.outdir, args.quick)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
