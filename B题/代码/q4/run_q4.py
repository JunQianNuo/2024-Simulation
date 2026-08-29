"""Q4-M2/Q4-M3：将抽样不确定性传递到 Q2/Q3 的完整策略域。"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.optimize import differential_evolution, shgo
from scipy.stats import beta, t as student_t

from q2 import model as q2_model
from q3 import model as q3_model

HERE = Path(__file__).resolve().parent
OUTDIR = HERE.parent / "results" / "q4"
DEMO, CONFIG_PATH = HERE / "q4_demo_evidence.json", HERE / "config.json"
Q2_NAMES = ("p1", "p2", "pf")
Q3_NAMES = tuple([f"part_{i}" for i in range(1, 9)] + ["semi_1", "semi_2", "semi_3", "final"])
PRIORS = {"uniform": (1.0, 1.0), "jeffreys": (0.5, 0.5)}
TOL = 1e-9
DE_SEEDS = range(2024, 2034)


def load_q2_inputs():
    q2_dir = HERE.parent / "q2"
    return read_json(q2_dir / "table1.json"), read_json(q2_dir / "config.json")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_records(records, conditioning, label, default_plan):
    for name, expected in conditioning.items():
        item = records.get(name, {})
        if set(item) - {"N", "K", "conditioning", "stopping_rule", "t_opt"}:
            raise ValueError(f"INVALID_DATA: {label}.{name} 含未知字段")
        if not isinstance(item.get("N"), int) or not isinstance(item.get("K"), int):
            raise ValueError(f"INVALID_DATA: {label}.{name} 必须给出整数 N,K")
        if item["N"] <= 0 or not 0 <= item["K"] <= item["N"]:
            raise ValueError(f"INVALID_DATA: {label}.{name} 要求 N>0 且 0<=K<=N")
        if item.get("conditioning") != expected:
            raise ValueError(f"INVALID_CONDITIONING: {label}.{name} 应为 {expected}")
        rule = item.get("stopping_rule", default_plan)
        if rule not in {"fixed_n", "sequential_cs"}:
            raise ValueError(f"INVALID_DATA: {label}.{name} stopping_rule 非法")
        if rule == "sequential_cs" and (not isinstance(item.get("t_opt"), int) or item["t_opt"] <= 0):
            raise ValueError(f"INVALID_DATA: {label}.{name} 序贯证据需要正整数 t_opt")


def read_evidence(path):
    evidence = read_json(path)
    if set(evidence) - {"mode", "sampling_plan", "note", "q2", "q3"}:
        raise ValueError("INVALID_DATA: evidence 顶层 schema 不符")
    plan = evidence.get("sampling_plan", "fixed_n")
    if plan not in {"fixed_n", "mixed", "sequential_cs"}:
        raise ValueError("INVALID_DATA: sampling_plan 非法")
    for case_no in range(1, 7):
        key = f"case_{case_no}"; records = evidence.get("q2", {}).get(key, {})
        if set(records) != set(Q2_NAMES):
            raise ValueError(f"INVALID_DATA: q2.{key} 必须恰有 p1,p2,pf")
        validate_records(records, {"p1": "component", "p2": "component", "pf": "all_inputs_good"}, f"q2.{key}", plan)
    records = evidence.get("q3", {})
    if set(records) != set(Q3_NAMES):
        raise ValueError("INVALID_DATA: q3 必须恰有 12 个参数")
    cond = {**{f"part_{i}": "component" for i in range(1, 9)},
            **{f"semi_{i}": "all_inputs_good" for i in range(1, 4)}, "final": "all_inputs_good"}
    validate_records(records, cond, "q3", plan)
    return evidence


def point_estimates(records, names):
    return {name: records[name]["K"] / records[name]["N"] for name in names}


def simultaneous_interval(record, alpha_j, default_plan):
    n, k = record["N"], record["K"]
    if record.get("stopping_rule", default_plan) == "fixed_n":
        lo = 0.0 if k == 0 else float(beta.ppf(alpha_j / 2, k, n - k + 1))
        hi = 1.0 if k == n else float(beta.ppf(1 - alpha_j / 2, k + 1, n - k))
        return lo, hi, "clopper_pearson_fixed_n"
    from q1.confidence_sequence import crosscheck_endpoints
    row = crosscheck_endpoints(record["t_opt"], [(n, k)], alpha_j / 2, alpha_j / 2)[0]
    if row["max_abs_error"] > 1e-8:
        raise RuntimeError("CS_CROSSCHECK_FAILED")
    return row["official_lower"], row["official_upper"], "q1_beta_binomial_cs"


def q2_evaluator(case_no, parameters):
    cases, config = load_q2_inputs(); case = {**cases[case_no - 1], **parameters}
    return lambda policy: q2_model.evaluate_policy(policy, case, config)


def valid_profit(row):
    ok = row.get("status") == "SUCCESS_EXACT" or (row.get("status") == "NEAR_NONABSORBING" and row.get("high_precision_reward_solve", False))
    return float(row["expected_profit"]) if ok else -np.inf


def evaluate_set(policies, evaluator):
    rows = [evaluator(policy) for policy in policies]
    values = np.array([valid_profit(row) for row in rows])
    if not np.isfinite(values).any():
        raise RuntimeError("没有可吸收策略")
    return rows, values


def posterior_metrics(values, statuses, plan, batches):
    draws, count = values.shape; feasible = np.isfinite(values[0]); vf = values[:, feasible]
    if not np.all(np.isfinite(vf)):
        raise RuntimeError("策略吸收性随内部参数异常改变")
    sample_best = vf.max(axis=1); ties = np.isclose(vf, sample_best[:, None], rtol=1e-11, atol=1e-11)
    weights = ties / ties.sum(axis=1, keepdims=True)
    fields = {name: np.full(count, np.nan) for name in ("mean", "sd", "se", "q05", "q50", "q95", "optimal", "optimal_se", "negative", "regret")}
    fields["mean"][feasible] = vf.mean(0); fields["sd"][feasible] = vf.std(0, ddof=1)
    fields["se"][feasible] = fields["sd"][feasible] / math.sqrt(draws)
    fields["q05"][feasible], fields["q50"][feasible], fields["q95"][feasible] = np.quantile(vf, [.05, .5, .95], axis=0)
    fields["optimal"][feasible] = weights.mean(0); fields["optimal_se"][feasible] = weights.std(0, ddof=1) / math.sqrt(draws)
    fields["negative"][feasible] = (vf < 0).mean(0); fields["regret"][feasible] = (sample_best[:, None] - vf).mean(0)
    if not np.isclose(np.nansum(fields["optimal"]), 1.0) or np.nanmin(fields["regret"]) < -TOL:
        raise RuntimeError("Bayesian 概率/regret 自检失败")
    ranked = np.flatnonzero(feasible)[np.argsort(-fields["mean"][feasible])]; first, second = map(int, ranked[:2])
    paired = values[:, first] - values[:, second]; paired_se = paired.std(ddof=1) / math.sqrt(draws)
    halfwidth = float(student_t.ppf(.975, max(batches - 1, 1)) * paired_se)
    gap = float(fields["mean"][first] - fields["mean"][second])
    near = np.flatnonzero(feasible & ((fields["mean"][first] - fields["mean"]) <= max(plan["epsilon_profit"], halfwidth) + TOL)).tolist()
    fields.update({"statuses": statuses, "draws": draws, "best_index": first, "second_index": second,
                   "gap": gap, "paired_halfwidth_95": halfwidth, "near_indices": near,
                   "precision_pass": halfwidth <= plan["epsilon_profit"] and fields["optimal_se"][first] <= plan["epsilon_prob"]})
    return fields


def posterior_run(policies, records, names, prior, seed, plan, factory, adaptive):
    rng = np.random.default_rng(seed); a, b = prior
    alpha = np.array([a + records[n]["K"] for n in names]); beta_args = np.array([b + records[n]["N"] - records[n]["K"] for n in names])
    target = plan["max_draws"] if adaptive else plan["confirm_draws"]
    blocks, statuses, previous, stable = [], None, None, 0
    while sum(map(len, blocks)) < target:
        take = min(plan["batch_size"], target - sum(map(len, blocks))); block = np.empty((take, len(policies)))
        for i, draw in enumerate(rng.beta(alpha, beta_args, size=(take, len(names)))):
            rows, block[i] = evaluate_set(policies, factory(dict(zip(names, draw))))
            statuses = statuses or [row.get("status") for row in rows]
        blocks.append(block); joined = np.vstack(blocks)
        if len(joined) < plan["initial_draws"]:
            continue
        metrics = posterior_metrics(joined, statuses, plan, len(blocks)); pair = (metrics["best_index"], metrics["second_index"])
        stable = stable + 1 if pair == previous else 1; previous = pair
        if adaptive and len(blocks) >= plan["min_batches"] and stable >= plan["stable_checkpoints"] and metrics["precision_pass"]:
            metrics.update({"batches": len(blocks), "stable": stable, "stop_reason": "precision_and_stability_reached"}); return metrics
    metrics = posterior_metrics(np.vstack(blocks), statuses, plan, len(blocks))
    metrics.update({"batches": len(blocks), "stable": stable, "stop_reason": "fixed_confirmation_batch" if not adaptive else "B_max_reached"})
    return metrics


def bayes_frame(base, policies, explore, confirm, domain, prior, status, case_no=None):
    rows = []
    for i, (source, policy) in enumerate(zip(base, policies)):
        row = {**source, "domain": domain, "prior": prior, "mc_status": status,
               "posterior_mean_profit": explore["mean"][i], "posterior_profit_sd": explore["sd"][i], "mc_standard_error": explore["se"][i],
               "posterior_profit_p05": explore["q05"][i], "posterior_profit_p50": explore["q50"][i], "posterior_profit_p95": explore["q95"][i],
               "posterior_optimal_probability": explore["optimal"][i], "optimal_probability_mc_se": explore["optimal_se"][i],
               "negative_profit_probability": explore["negative"][i], "posterior_mean_regret": explore["regret"][i],
               "near_optimal_explore": i in explore["near_indices"], "near_optimal_confirm": i in confirm["near_indices"],
               "explore_draws": explore["draws"], "confirm_draws": confirm["draws"],
               "explore_gap": explore["gap"], "explore_paired_halfwidth_95": explore["paired_halfwidth_95"],
               "confirm_gap": confirm["gap"], "confirm_paired_halfwidth_95": confirm["paired_halfwidth_95"]}
        if domain == "q2": row["strategy_bits"] = "".join(map(str, policy))
        else: row.update({"strategy_id": int(policy), "strategy_bits": source["strategy_bits"]})
        if case_no: row["case"] = case_no
        rows.append(row)
    return pd.DataFrame(rows)


def run_bayes(domain, records, names, plan, quick, case_no=None):
    policies = list(itertools.product((0, 1), repeat=4)) if domain == "q2" else list(range(65536))
    factory = (lambda p: q2_evaluator(case_no, p)) if domain == "q2" else q3_model.make_q3_evaluator
    base, _ = evaluate_set(policies, factory(point_estimates(records, names))); frames, summary = [], {}
    for prior_name, prior in PRIORS.items():
        explore = posterior_run(policies, records, names, prior, plan["explore_seed"], plan, factory, True)
        confirm = posterior_run(policies, records, names, prior, plan["confirm_seed"], plan, factory, False)
        converged = explore["precision_pass"] and confirm["precision_pass"] and explore["stable"] >= 3 and explore["best_index"] == confirm["best_index"]
        status = "SUCCESS_MC_TOL" if converged and not quick else "MC_NOT_CONVERGED"
        frames.append(bayes_frame(base, policies, explore, confirm, domain, prior_name, status, case_no))
        label = (lambda i: "".join(map(str, policies[i]))) if domain == "q2" else (lambda i: int(policies[i]))
        summary[prior_name] = {"status": status, "explore_best": label(explore["best_index"]), "confirm_best": label(confirm["best_index"]),
                               "explore_draws": explore["draws"], "confirm_draws": confirm["draws"], "stable_checkpoints": explore["stable"],
                               "explore_gap": explore["gap"], "explore_paired_halfwidth_95": explore["paired_halfwidth_95"],
                               "near_optimal": [label(i) for i in sorted(set(explore["near_indices"]) | set(confirm["near_indices"]))]}
    return pd.concat(frames, ignore_index=True), summary


def interval_box(records, names, coverage, default_plan):
    alpha_j = (1 - coverage / 100) / len(names)
    data = [simultaneous_interval(records[n], alpha_j, default_plan) for n in names]
    return np.array([[x[0], x[1]] for x in data]), {n: data[i][2] for i, n in enumerate(names)}, alpha_j


def robust_search(domain, records, names, coverage, default_plan, quick, case_no=None):
    policies = list(itertools.product((0, 1), repeat=4)) if domain == "q2" else list(range(65536))
    factory = (lambda p: q2_evaluator(case_no, p)) if domain == "q2" else q3_model.make_q3_evaluator
    bounds, methods, alpha_j = interval_box(records, names, coverage, default_plan)
    base, nominal = evaluate_set(policies, factory(point_estimates(records, names)))
    rng = np.random.default_rng(9000 + coverage)
    if domain == "q2": points = np.array(list(itertools.product(*[(lo, hi) for lo, hi in bounds])))
    else: points = np.vstack([bounds[:, 0], bounds[:, 1], bounds.mean(1), rng.uniform(bounds[:, 0], bounds[:, 1], size=(4 if quick else 32, len(names)))])
    values = np.vstack([evaluate_set(policies, factory(dict(zip(names, p))))[1] for p in points])
    worst, arg = values.min(0), values.argmin(0); locations = points[arg].copy()
    agreement = np.ones(len(policies), dtype=bool)
    if domain == "q2" and not quick:
        for i, policy in enumerate(policies):
            if not np.isfinite(nominal[i]): continue
            objective = lambda x, d=policy: -valid_profit(factory(dict(zip(names, x)))(d))
            s = shgo(objective, bounds.tolist(), n=8192, iters=5, sampling_method="sobol")
            des = [differential_evolution(objective, bounds.tolist(), seed=seed, popsize=max(20, 10 * len(names)),
                                          maxiter=3000, tol=1e-9, atol=1e-10, polish=True) for seed in DE_SEEDS]
            candidates = [(worst[i], locations[i]), (-float(s.fun), np.asarray(s.x))]
            candidates.extend((-float(result.fun), np.asarray(result.x)) for result in des)
            worst[i], locations[i] = min(candidates, key=lambda item: item[0])
            objectives = np.array([float(s.fun), *[float(result.fun) for result in des]])
            agreement[i] = np.ptp(objectives) <= 1e-6
    rows = []
    for i, source in enumerate(base):
        row = {**source, "coverage": coverage, "nominal_profit": nominal[i], "worst_profit": worst[i],
               "worst_parameter_location": json.dumps(dict(zip(names, locations[i].tolist())), sort_keys=True),
               "robust_status": "ROBUST_NUMERICAL" if domain == "q2" and not quick and np.isfinite(worst[i]) and agreement[i] else "ROBUST_UNCERTIFIED"}
        if domain == "q2": row.update({"case": case_no, "strategy_bits": "".join(map(str, policies[i]))})
        rows.append(row)
    audit = {"bounds": {n: bounds[i].tolist() for i, n in enumerate(names)}, "interval_methods": methods,
             "alpha_per_parameter": alpha_j, "evaluated_box_points": len(points), "interval_certificate": False,
             "claim_limit": "无区间分支定界证书，仅能称数值稳健方案"}
    return pd.DataFrame(rows), audit


def select_bayes(frame):
    return frame[frame.near_optimal_explore | frame.near_optimal_confirm].copy()


def select_robust(frame):
    valid = frame[frame.robust_status.eq("ROBUST_NUMERICAL")].copy(); groups = [x for x in ("case", "coverage") if x in valid]
    maxima = valid.groupby(groups).worst_profit.transform("max") if groups else valid.worst_profit.max()
    return valid[np.isclose(valid.worst_profit, maxima, rtol=1e-10, atol=1e-10)].copy()


def validate_nominal_consistency(evidence):
    cases, config = load_q2_inputs()
    for case_no, case in enumerate(cases, 1):
        params = point_estimates(evidence["q2"][f"case_{case_no}"], Q2_NAMES)
        for policy in itertools.product((0, 1), repeat=4):
            if abs(valid_profit(q2_model.evaluate_policy(policy, case, config)) - valid_profit(q2_evaluator(case_no, params)(policy))) > TOL:
                raise RuntimeError("Q2 名义接口不一致")
    if point_estimates(evidence["q3"], Q3_NAMES) == q3_model.q3_nominal_parameters():
        evaluator = q3_model.make_q3_evaluator(q3_model.q3_nominal_parameters())
        for strategy in range(65536):
            if abs(valid_profit(q3_model.evaluate(strategy)) - valid_profit(evaluator(strategy))) > TOL:
                raise RuntimeError("Q3 名义接口不一致")


def json_default(value):
    if isinstance(value, (np.integer, np.floating, np.bool_)): return value.item()
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--evidence", default=str(DEMO)); parser.add_argument("--quick", action="store_true"); args = parser.parse_args()
    started = time.perf_counter(); config, evidence = read_json(CONFIG_PATH), read_evidence(args.evidence); validate_nominal_consistency(evidence)
    plans = config["quick_plan"] if args.quick else config["default_plan"]
    q2b, q2r, q2sum, q2rsum = [], [], {}, {}
    for case_no in range(1, 7):
        records = evidence["q2"][f"case_{case_no}"]; frame, info = run_bayes("q2", records, Q2_NAMES, plans["q2"], args.quick, case_no)
        q2b.append(frame); q2sum[f"case_{case_no}"] = info
        for coverage in config["robust_coverages"]:
            frame, info = robust_search("q2", records, Q2_NAMES, coverage, evidence.get("sampling_plan", "fixed_n"), args.quick, case_no)
            q2r.append(frame); q2rsum[f"case_{case_no}_{coverage}"] = info
    q2b, q2r = pd.concat(q2b, ignore_index=True), pd.concat(q2r, ignore_index=True)
    q3b, q3sum = run_bayes("q3", evidence["q3"], Q3_NAMES, plans["q3"], args.quick)
    q3r, q3rsum = [], {}
    for coverage in config["robust_coverages"]:
        frame, info = robust_search("q3", evidence["q3"], Q3_NAMES, coverage, evidence.get("sampling_plan", "fixed_n"), args.quick)
        q3r.append(frame); q3rsum[str(coverage)] = info
    q3r = pd.concat(q3r, ignore_index=True)
    if len(q2b) != 192 or len(q3b) != 131072: raise RuntimeError("INCOMPLETE_POLICY_SET")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    outputs = {"q2_bayesian_all_policies.csv": q2b, "q2_bayesian_near_optimal.csv": select_bayes(q2b),
               "q2_robust_all_policies.csv": q2r, "q2_robust_numerical_best.csv": select_robust(q2r),
               "q3_bayesian_all_policies.csv": q3b, "q3_bayesian_near_optimal.csv": select_bayes(q3b),
               "q3_robust_all_policies.csv": q3r, "q3_robust_numerical_best.csv": select_robust(q3r)}
    for name, frame in outputs.items(): frame.to_csv(OUTDIR / name, index=False, encoding="utf-8-sig")
    marker = "DEMO_ONLY_NOT_OFFICIAL_DATA" if evidence.get("mode") == "DEMO_ONLY_NOT_OFFICIAL_DATA" else "USER_SUPPLIED_EVIDENCE"
    used = {**evidence, "source_path": str(Path(args.evidence).resolve()), "evidence_marker": marker}
    (OUTDIR / "evidence_used.json").write_text(json.dumps(used, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"schema_version": config["schema_version"], "models": ["Q4-M2", "Q4-M3"], "algorithms": ["Q4-A1", "Q4-A2"],
               "evidence_marker": marker, "claim_scope": "题面无真实 N,K；默认输出仅为演示，不是企业观测结论。",
               "policy_domains": {"q2_per_case": 16, "q3": 65536}, "quick": args.quick, "q2_bayesian": q2sum, "q3_bayesian": q3sum,
               "q2_robust": q2rsum, "q3_robust": q3rsum, "robust_claim": "快速验收仅 ROBUST_UNCERTIFIED；正式 Q2 互证最高为 ROBUST_NUMERICAL；无区间证书不得称严格全局稳健最优。",
               "checks": {"q2_full_policy_coverage": len(q2b) == 192, "q3_full_policy_coverage": len(q3b) == 131072,
                          "optimal_probabilities_sum_to_one": bool(np.allclose(q2b.groupby(["case", "prior"]).posterior_optimal_probability.sum(), 1) and np.allclose(q3b.groupby("prior").posterior_optimal_probability.sum(), 1)),
                          "regret_nonnegative": bool(q2b.posterior_mean_regret.dropna().min() >= -TOL and q3b.posterior_mean_regret.dropna().min() >= -TOL),
                          "no_false_robust_certification": not q2r.robust_status.eq("ROBUST_CERTIFIED").any() and not q3r.robust_status.eq("ROBUST_CERTIFIED").any()},
               "runtime_seconds": time.perf_counter() - started}
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=json_default) + "\n", encoding="utf-8")
    writer = {
        "evidence_marker": marker,
        "accounting_unit": "最终交付一件合格品的期望净利润",
        "bayesian_claim": "快速验收批未达 MC 容差，只可报告近优集；正式运行达 SUCCESS_MC_TOL 后才可报领先策略。",
        "robust_claim": "快速验收仅 ROBUST_UNCERTIFIED；正式 Q2 互证最高为 ROBUST_NUMERICAL；无区间证书不可称严格全局稳健最优。",
        "q2_bayesian_near_optimal_file": "q2_bayesian_near_optimal.csv",
        "q3_bayesian_near_optimal_file": "q3_bayesian_near_optimal.csv",
        "q2_robust_numerical_file": "q2_robust_numerical_best.csv",
        "q3_robust_numerical_file": "q3_robust_numerical_best.csv",
        "limitations": ["题面未给真实 N,K，默认数值是演示", "矩形联合集忽略参数相关性", "完美检测、条件独立与回收件真实质量保留沿用 Q2/Q3 锁定假设"]
    }
    (OUTDIR / "code_to_writer.json").write_text(json.dumps(writer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    repro = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "command": f"python -m q4.run_q4{' --quick' if args.quick else ''}",
             "python": sys.version, "platform": platform.platform(), "versions": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__},
             "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip(),
             "config_sha256": hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(), "evidence_sha256": hashlib.sha256(Path(args.evidence).read_bytes()).hexdigest()}
    (OUTDIR / "reproducibility.json").write_text(json.dumps(repro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{marker} | Q2={len(q2b)} | Q3={len(q3b)} | {summary['runtime_seconds']:.1f}s")
    print("快速稳健结果为 ROBUST_UNCERTIFIED；无区间证书不得表述为严格全局稳健最优。")


if __name__ == "__main__": main()
