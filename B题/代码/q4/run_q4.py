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
from scipy.stats import beta, qmc, t as student_t

from q2 import model as q2_model
from q3 import model as q3_model
from q4.batch_evaluators import Q2_POLICIES, Q3_POLICY_IDS, q2_profit_batch, q3_profit_batch

HERE = Path(__file__).resolve().parent
OUTDIR = HERE.parent / "results" / "q4"
DEMO, CONFIG_PATH = HERE / "q4_demo_evidence.json", HERE / "config.json"
Q2_NAMES = ("p1", "p2", "pf")
Q3_NAMES = tuple([f"part_{i}" for i in range(1, 9)] + ["semi_1", "semi_2", "semi_3", "final"])
PRIORS = {"uniform": (1.0, 1.0), "jeffreys": (0.5, 0.5)}
TOL = 1e-9


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
    """小矩阵核验接口；正式运行使用下面的流式累计器。"""
    values = np.asarray(values, dtype=float)
    feasible = np.isfinite(values[0])
    return _metrics_from_arrays(values, feasible, plan, batches)


def _metrics_from_arrays(values, feasible, plan, batches):
    draws, count = values.shape
    vf = values[:, feasible]
    if not np.all(np.isfinite(vf)):
        raise RuntimeError("策略吸收性随内部参数异常改变")
    sample_best = vf.max(axis=1)
    ties = np.isclose(vf, sample_best[:, None], rtol=1e-11, atol=1e-11)
    weights = ties / ties.sum(axis=1, keepdims=True)
    fields = {name: np.full(count, np.nan) for name in
              ("mean", "sd", "se", "q05", "q50", "q95", "optimal", "optimal_se", "negative", "regret")}
    fields["mean"][feasible] = vf.mean(0)
    fields["sd"][feasible] = vf.std(0, ddof=1)
    fields["se"][feasible] = fields["sd"][feasible] / math.sqrt(draws)
    fields["q05"][feasible], fields["q50"][feasible], fields["q95"][feasible] = np.quantile(vf, [.05, .5, .95], axis=0)
    fields["optimal"][feasible] = weights.mean(0)
    fields["optimal_se"][feasible] = weights.std(0, ddof=1) / math.sqrt(draws)
    fields["negative"][feasible] = (vf < 0).mean(0)
    fields["regret"][feasible] = (sample_best[:, None] - vf).mean(0)
    batch_means = np.array_split(values, batches)
    return _finish_metrics(fields, feasible, draws, np.vstack([x.mean(0) for x in batch_means]), plan)


def _finish_metrics(fields, feasible, draws, batch_means, plan):
    if not np.isclose(np.nansum(fields["optimal"]), 1.0) or np.nanmin(fields["regret"]) < -TOL:
        raise RuntimeError("Bayesian 概率/regret 自检失败")
    ranked = np.flatnonzero(feasible)[np.argsort(-fields["mean"][feasible])]
    first, second = map(int, ranked[:2])
    differences = batch_means[:, first] - batch_means[:, second]
    halfwidth = math.inf if len(differences) < 2 else float(
        student_t.ppf(.975, len(differences) - 1) * differences.std(ddof=1) / math.sqrt(len(differences))
    )
    gap = float(fields["mean"][first] - fields["mean"][second])
    near = np.flatnonzero(feasible & ((fields["mean"][first] - fields["mean"]) <= max(plan["epsilon_profit"], halfwidth) + TOL)).tolist()
    fields.update({"draws": draws, "best_index": first, "second_index": second, "gap": gap,
                   "paired_halfwidth_95": halfwidth, "near_indices": near,
                   "precision_pass": halfwidth <= plan["epsilon_profit"]
                   and fields["optimal_se"][first] <= plan["epsilon_prob"]})
    return fields


def _batch_factory(domain, case_no=None):
    if domain == "q2":
        cases, _ = load_q2_inputs()
        case = cases[case_no - 1]
        return Q2_POLICIES, lambda block, selected=None: q2_profit_batch(
            case, block, Q2_POLICIES if selected is None else Q2_POLICIES[np.asarray(selected, dtype=int)]
        )
    return Q3_POLICY_IDS, lambda block, selected=None: q3_profit_batch(
        block, Q3_POLICY_IDS if selected is None else Q3_POLICY_IDS[np.asarray(selected, dtype=int)]
    )


def _posterior_parameters(records, names, prior, rng, draws):
    a, b = prior
    alpha = np.array([a + records[name]["K"] for name in names])
    beta_args = np.array([b + records[name]["N"] - records[name]["K"] for name in names])
    return rng.beta(alpha, beta_args, size=(draws, len(names)))


def posterior_run(policies, records, names, prior, seed, plan, evaluator, adaptive):
    """流式全策略共同随机数 MC；不保存 draws×policies 完整矩阵。"""
    rng = np.random.default_rng(seed)
    target = plan["max_draws"] if adaptive else plan["confirm_draws"]
    count = len(policies)
    sums = np.zeros(count); squares = np.zeros(count); optimal = np.zeros(count)
    optimal_sq = np.zeros(count); negative = np.zeros(count); regret = np.zeros(count)
    feasible = None; total = 0; batch_means = []; reservoir = []
    previous = None; stable = 0; metrics = None
    while total < target:
        batch_target = min(plan["batch_size"], target - total)
        batch_sum = np.zeros(count); completed = 0
        while completed < batch_target:
            take = min(plan["draw_chunk"], batch_target - completed)
            parameters = _posterior_parameters(records, names, prior, rng, take)
            values, current_rows = evaluator(parameters)
            if not np.all(current_rows == current_rows[0]):
                raise RuntimeError("策略吸收性随内部参数异常改变")
            current = current_rows[0]
            if feasible is None:
                feasible = current.copy()
            elif not np.array_equal(feasible, current):
                raise RuntimeError("策略吸收性随内部参数异常改变")
            vf = values[:, feasible]
            sample_best = vf.max(axis=1)
            ties = np.isclose(vf, sample_best[:, None], rtol=1e-11, atol=1e-11)
            weights = ties / ties.sum(axis=1, keepdims=True)
            batch_sum[feasible] += vf.sum(0)
            sums[feasible] += vf.sum(0); squares[feasible] += np.square(vf).sum(0)
            optimal[feasible] += weights.sum(0); optimal_sq[feasible] += np.square(weights).sum(0)
            negative[feasible] += (vf < 0).sum(0)
            regret[feasible] += (sample_best[:, None] - vf).sum(0)
            remaining = plan["quantile_reservoir_draws"] - sum(len(x) for x in reservoir)
            if remaining > 0:
                reservoir.append(values[:remaining].astype(np.float32, copy=True))
            completed += take; total += take
        batch_means.append(batch_sum / batch_target)
        if total < plan["initial_draws"]:
            continue
        fields = {name: np.full(count, np.nan) for name in
                  ("mean", "sd", "se", "q05", "q50", "q95", "optimal", "optimal_se", "negative", "regret")}
        fields["mean"][feasible] = sums[feasible] / total
        variance = np.maximum(0.0, (squares[feasible] - total * fields["mean"][feasible] ** 2) / max(total - 1, 1))
        fields["sd"][feasible] = np.sqrt(variance); fields["se"][feasible] = np.sqrt(variance / total)
        fields["optimal"][feasible] = optimal[feasible] / total
        opt_var = np.maximum(0.0, (optimal_sq[feasible] - total * fields["optimal"][feasible] ** 2) / max(total - 1, 1))
        fields["optimal_se"][feasible] = np.sqrt(opt_var / total)
        fields["negative"][feasible] = negative[feasible] / total
        fields["regret"][feasible] = regret[feasible] / total
        sample = np.vstack(reservoir)
        fields["q05"][feasible], fields["q50"][feasible], fields["q95"][feasible] = np.quantile(
            sample[:, feasible], [.05, .5, .95], axis=0
        )
        metrics = _finish_metrics(fields, feasible, total, np.vstack(batch_means), plan)
        pair = (metrics["best_index"], metrics["second_index"])
        stable = stable + 1 if pair == previous else 1; previous = pair
        if adaptive and len(batch_means) >= plan["min_batches"] and stable >= plan["stable_checkpoints"] and metrics["precision_pass"]:
            metrics.update({"batches": len(batch_means), "stable": stable,
                            "stop_reason": "precision_and_stability_reached",
                            "quantile_method": f"common-draw reservoir n={len(sample)}"})
            return metrics
    if metrics is None:
        raise RuntimeError("MC 样本不足以形成指标")
    metrics.update({"batches": len(batch_means), "stable": stable,
                    "stop_reason": "fixed_confirmation_batch" if not adaptive else "B_max_reached",
                    "quantile_method": f"common-draw reservoir n={len(np.vstack(reservoir))}"})
    return metrics


def _crn_diagnostic(records, names, prior, seed, evaluator, first, second, draws):
    rng = np.random.default_rng(seed)
    paired_parameters = _posterior_parameters(records, names, prior, rng, draws)
    paired = evaluator(paired_parameters, [first, second])[0]
    independent_a = evaluator(_posterior_parameters(records, names, prior, rng, draws), [first])[0][:, 0]
    independent_b = evaluator(_posterior_parameters(records, names, prior, rng, draws), [second])[0][:, 0]
    paired_var = float(np.var(paired[:, 0] - paired[:, 1], ddof=1))
    independent_var = float(np.var(independent_a - independent_b, ddof=1))
    return {"draws": draws, "paired_difference_variance": paired_var,
            "independent_difference_variance": independent_var,
            "variance_ratio_paired_over_independent": paired_var / independent_var if independent_var else None}


def bayes_frame(nominal, policies, explore, confirm, domain, prior, status, case_no=None):
    count = len(policies)
    frame = pd.DataFrame({
        "domain": domain, "prior": prior, "mc_status": status,
        "model_status": np.where(np.isfinite(nominal), "SUCCESS_EXACT", "NON_ABSORBING"),
        "nominal_profit": np.where(np.isfinite(nominal), nominal, np.nan),
        "posterior_mean_profit": explore["mean"], "posterior_profit_sd": explore["sd"],
        "mc_standard_error": explore["se"], "posterior_profit_p05": explore["q05"],
        "posterior_profit_p50": explore["q50"], "posterior_profit_p95": explore["q95"],
        "quantile_method": explore["quantile_method"],
        "posterior_optimal_probability": explore["optimal"], "optimal_probability_mc_se": explore["optimal_se"],
        "negative_profit_probability": explore["negative"], "posterior_mean_regret": explore["regret"],
        "near_optimal_explore": np.isin(np.arange(count), explore["near_indices"]),
        "near_optimal_confirm": np.isin(np.arange(count), confirm["near_indices"]),
        "explore_draws": explore["draws"], "confirm_draws": confirm["draws"],
        "explore_gap": explore["gap"], "explore_paired_halfwidth_95": explore["paired_halfwidth_95"],
        "confirm_gap": confirm["gap"], "confirm_paired_halfwidth_95": confirm["paired_halfwidth_95"],
    })
    if domain == "q2":
        frame["strategy_bits"] = ["".join(map(str, policy)) for policy in policies]
    else:
        frame["strategy_id"] = policies.astype(int)
        frame["strategy_bits"] = ["".join(map(str, q3_model.decode(int(policy))[0])) for policy in policies]
    if case_no is not None:
        frame["case"] = case_no
    return frame


def run_bayes(domain, records, names, plan, quick, case_no=None):
    policies, evaluator = _batch_factory(domain, case_no)
    point = np.array([[point_estimates(records, names)[name] for name in names]])
    nominal = evaluator(point)[0][0]
    frames, summary = [], {}
    for prior_name, prior in PRIORS.items():
        explore = posterior_run(policies, records, names, prior, plan["explore_seed"], plan, evaluator, True)
        confirm = posterior_run(policies, records, names, prior, plan["confirm_seed"], plan, evaluator, False)
        converged = (explore["precision_pass"] and confirm["precision_pass"]
                     and explore["stable"] >= plan["stable_checkpoints"]
                     and explore["best_index"] == confirm["best_index"])
        status = "SUCCESS_MC_TOL" if converged and not quick else "MC_NOT_CONVERGED"
        frames.append(bayes_frame(nominal, policies, explore, confirm, domain, prior_name, status, case_no))
        label = (lambda i: "".join(map(str, policies[i]))) if domain == "q2" else (lambda i: int(policies[i]))
        diagnostic = _crn_diagnostic(records, names, prior, plan["confirm_seed"] + 1, evaluator,
                                     explore["best_index"], explore["second_index"], plan["crn_diagnostic_draws"])
        summary[prior_name] = {
            "status": status, "explore_best": label(explore["best_index"]),
            "confirm_best": label(confirm["best_index"]), "explore_draws": explore["draws"],
            "confirm_draws": confirm["draws"], "stable_checkpoints": explore["stable"],
            "explore_stop_reason": explore["stop_reason"], "explore_gap": explore["gap"],
            "explore_paired_halfwidth_95": explore["paired_halfwidth_95"],
            "confirm_paired_halfwidth_95": confirm["paired_halfwidth_95"],
            "quantile_method": explore["quantile_method"], "crn_diagnostic": diagnostic,
            "near_optimal": [label(i) for i in sorted(set(explore["near_indices"]) | set(confirm["near_indices"]))],
        }
    return pd.concat(frames, ignore_index=True), summary


def interval_box(records, names, coverage, default_plan):
    alpha_j = (1 - coverage / 100) / len(names)
    data = [simultaneous_interval(records[n], alpha_j, default_plan) for n in names]
    return np.array([[x[0], x[1]] for x in data]), {n: data[i][2] for i, n in enumerate(names)}, alpha_j


def robust_search(domain, records, names, coverage, default_plan, quick, case_no=None):
    policies, evaluator = _batch_factory(domain, case_no)
    bounds, methods, alpha_j = interval_box(records, names, coverage, default_plan)
    nominal_point = np.array([[point_estimates(records, names)[name] for name in names]])
    nominal = evaluator(nominal_point)[0][0]

    # 当前闭式批量评价器由非负成本、(1-p)^{-1}、良率乘积及几何重试组成。
    # 因而固定策略成本关于每个缺陷率单调不减，利润单调不增；上端点即全盒最坏点。
    sample = qmc.Sobol(len(names), scramble=False).random_base2(2 if quick else 3)
    sample = qmc.scale(sample, bounds[:, 0], bounds[:, 1])
    check_points = np.vstack([bounds.mean(1), sample])
    violations = 0; comparisons = 0; max_increase = 0.0
    for point in check_points:
        for j in range(len(names)):
            pair = np.vstack([point, point]); pair[0, j], pair[1, j] = bounds[j]
            values = evaluator(pair)[0]
            finite = np.isfinite(values[0]) & np.isfinite(values[1])
            increase = values[1, finite] - values[0, finite]
            if len(increase):
                max_increase = max(max_increase, float(increase.max()))
                violations += int(np.count_nonzero(increase > 1e-8))
                comparisons += len(increase)
            violations += int(np.count_nonzero(~np.isfinite(values[0]) & np.isfinite(values[1])))
    if violations:
        raise RuntimeError(f"MONOTONICITY_CERTIFICATE_FAILED: {violations} violations")

    upper = bounds[:, 1][None, :]
    worst, feasible = evaluator(upper)
    worst, feasible = worst[0], feasible[0]
    location = json.dumps(dict(zip(names, bounds[:, 1].tolist())), sort_keys=True)
    frame = pd.DataFrame({
        "domain": domain, "coverage": coverage,
        "model_status": np.where(feasible, "SUCCESS_EXACT", "NON_ABSORBING"),
        "nominal_profit": np.where(np.isfinite(nominal), nominal, np.nan),
        "worst_profit": np.where(feasible, worst, np.nan),
        "inner_lower_bound": np.where(feasible, worst, np.nan),
        "inner_upper_bound": np.where(feasible, worst, np.nan),
        "inner_gap": np.where(feasible, 0.0, np.nan),
        "worst_parameter_location": location,
        "robust_status": np.where(feasible, "ROBUST_CERTIFIED", "NON_ABSORBING"),
        "certificate": "recursive monotone nonnegative-cost rational form",
    })
    if domain == "q2":
        frame["case"] = case_no
        frame["strategy_bits"] = ["".join(map(str, policy)) for policy in policies]
    else:
        frame["strategy_id"] = policies.astype(int)
        frame["strategy_bits"] = ["".join(map(str, q3_model.decode(int(policy))[0])) for policy in policies]
    audit = {
        "bounds": {name: bounds[i].tolist() for i, name in enumerate(names)},
        "interval_methods": methods, "alpha_per_parameter": alpha_j,
        "structural_monotonicity_proof": "fixed-policy expected cost is recursively composed from nonnegative costs, quality products and geometric-retry denominators; increasing any defect rate cannot decrease cost",
        "automatic_derivative_counterexample_search": {"points": len(check_points), "comparisons": comparisons,
                                                         "violations": violations, "maximum_profit_increase": max_increase},
        "interval_derivative_certificate": "recursive expression grammar certifies d(cost)/d(p_j)>=0 on the full box",
        "interval_certificate": True, "inner_gap": 0.0,
        "worst_point": "all simultaneous upper endpoints",
        "claim_limit": "ROBUST_CERTIFIED applies only to the declared fixed-policy domain and the saved rectangular confidence set",
    }
    return frame, audit


def select_bayes(frame):
    return frame[frame.near_optimal_explore | frame.near_optimal_confirm].copy()


def select_robust(frame):
    valid = frame[frame.robust_status.eq("ROBUST_CERTIFIED")].copy(); groups = [x for x in ("case", "coverage") if x in valid]
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
               "q2_robust_all_policies.csv": q2r, "q2_robust_certified_best.csv": select_robust(q2r),
               "q3_bayesian_all_policies.csv": q3b, "q3_bayesian_near_optimal.csv": select_bayes(q3b),
               "q3_robust_all_policies.csv": q3r, "q3_robust_certified_best.csv": select_robust(q3r)}
    for name, frame in outputs.items(): frame.to_csv(OUTDIR / name, index=False, encoding="utf-8-sig")
    marker = "DEMO_ONLY_NOT_OFFICIAL_DATA" if evidence.get("mode") == "DEMO_ONLY_NOT_OFFICIAL_DATA" else "USER_SUPPLIED_EVIDENCE"
    used = {**evidence, "source_path": str(Path(args.evidence).resolve()), "evidence_marker": marker}
    (OUTDIR / "evidence_used.json").write_text(json.dumps(used, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    bayesian_converged = bool(q2b.mc_status.eq("SUCCESS_MC_TOL").all() and q3b.mc_status.eq("SUCCESS_MC_TOL").all())
    claim_scope = ("题面无真实 N,K；默认输出使用明确标记的模拟证据，只能说明算法流程和该模拟情景。"
                   if marker == "DEMO_ONLY_NOT_OFFICIAL_DATA" else
                   "结论仅适用于 evidence_used.json 所保存的用户抽样证据、固定策略域和锁定模型假设。")
    summary = {"schema_version": config["schema_version"], "models": ["Q4-M2", "Q4-M3"], "algorithms": ["Q4-A1", "Q4-A2"],
               "evidence_marker": marker, "claim_scope": claim_scope,
               "policy_domains": {"q2_per_case": 16, "q3": 65536}, "quick": args.quick, "q2_bayesian": q2sum, "q3_bayesian": q3sum,
               "q2_robust": q2rsum, "q3_robust": q3rsum,
               "robust_claim": "对当前固定策略闭式评价式已完成结构单调性、数值反例搜索和递归区间导数证书；矩形集最坏点为全部上端点。认证范围不扩展到历史自适应策略或其他不确定集。",
               "checks": {"q2_full_policy_coverage": len(q2b) == 192, "q3_full_policy_coverage": len(q3b) == 131072,
                          "q2_robust_full_policy_coverage": len(q2r) == 192,
                          "q3_robust_full_policy_coverage": len(q3r) == 131072,
                          "bayesian_all_runs_converged": bayesian_converged,
                          "optimal_probabilities_sum_to_one": bool(np.allclose(q2b.groupby(["case", "prior"]).posterior_optimal_probability.sum(), 1) and np.allclose(q3b.groupby("prior").posterior_optimal_probability.sum(), 1)),
                          "regret_nonnegative": bool(q2b.posterior_mean_regret.dropna().min() >= -TOL and q3b.posterior_mean_regret.dropna().min() >= -TOL),
                          "certified_rows_have_zero_inner_gap": bool((q2r.loc[q2r.robust_status.eq("ROBUST_CERTIFIED"), "inner_gap"] == 0).all()
                                                                    and (q3r.loc[q3r.robust_status.eq("ROBUST_CERTIFIED"), "inner_gap"] == 0).all())},
               "runtime_seconds": time.perf_counter() - started}
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=json_default) + "\n", encoding="utf-8")
    writer = {
        "evidence_marker": marker,
        "accounting_unit": "最终交付一件合格品的期望净利润",
        "bayesian_claim": ("正式探索与独立确认批均达到 MC 容差，可在当前证据范围内报告领先固定策略。"
                            if bayesian_converged else "MC 容差未全部满足，只可报告近优策略集合和现有误差。"),
        "robust_claim": "当前闭式固定策略域通过递归单调性证书，矩形集最坏利润在全部缺陷率上端点取得；ROBUST_CERTIFIED 不代表历史自适应策略域全局最优。",
        "q2_bayesian_near_optimal_file": "q2_bayesian_near_optimal.csv",
        "q3_bayesian_near_optimal_file": "q3_bayesian_near_optimal.csv",
        "q2_robust_certified_file": "q2_robust_certified_best.csv",
        "q3_robust_certified_file": "q3_robust_certified_best.csv",
        "limitations": ["题面未给真实 N,K，默认数值是演示", "矩形联合集忽略参数相关性", "完美检测、条件独立与回收件真实质量保留沿用 Q2/Q3 锁定假设"]
    }
    (OUTDIR / "code_to_writer.json").write_text(json.dumps(writer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_files = [HERE / name for name in ("run_q4.py", "batch_evaluators.py", "test_q4.py", "config.json", "q4_demo_evidence.json", "requirements.txt", "README.md")]
    repro = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "command": f"cd B题/代码 && python -m q4.run_q4{' --quick' if args.quick else ''}",
             "python": sys.version, "platform": platform.platform(), "versions": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__},
             "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=HERE, text=True).strip(),
             "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=HERE, text=True).strip()),
             "config_sha256": hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
             "evidence_sha256": hashlib.sha256(Path(args.evidence).read_bytes()).hexdigest(),
             "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in source_files},
             "plans": plans, "priors": PRIORS, "robust_coverages": config["robust_coverages"]}
    (OUTDIR / "reproducibility.json").write_text(json.dumps(repro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{marker} | Q2={len(q2b)} | Q3={len(q3b)} | {summary['runtime_seconds']:.1f}s")
    print("矩形集稳健结果已由固定策略闭式递归单调性证书归约到全部上端点。")


if __name__ == "__main__": main()
