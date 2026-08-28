"""Q4-M2/Q4-M3：后验 Monte Carlo 与 Bonferroni 区间下的全策略比较。"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta

from q2 import run_q2 as q2
from q3 import run_q3 as q3


OUTDIR = Path(__file__).resolve().parent.parent / "results" / "q4"
DEMO = Path(__file__).resolve().parent / "q4_demo_evidence.json"
EXPLORE_SEED, CONFIRM_SEED = 2024, 12024
TOL = 1e-9
MC_Z = 3.0
PRIORS = {"uniform": (1.0, 1.0), "jeffreys": (0.5, 0.5)}
Q2_NAMES = ("p1", "p2", "pf")
Q3_NAMES = tuple([f"part_{i}" for i in range(1, 9)] + ["semi_1", "semi_2", "semi_3", "final"])
DEFAULT_PLAN = {"q2": {"explore_min": 5000, "confirm_min": 2000, "batch": 500, "explore_max": 10000, "confirm_max": 5000}, "q3": {"explore_min": 100, "confirm_min": 100, "batch": 20, "explore_max": 1000, "confirm_max": 1000}}
QUICK_PLAN = {"q2": {"explore_min": 100, "confirm_min": 75, "batch": 25, "explore_max": 100, "confirm_max": 75}, "q3": {"explore_min": 10, "confirm_min": 10, "batch": 10, "explore_max": 10, "confirm_max": 10}}
MODEL_CONTRACT = {"fixed_strategy": True, "perfect_detection": True, "one_sale_revenue": True, "real_quality_recovery": True, "independent_defects": True}


def decode_q2(policy):
    bits = "".join(map(str, policy))
    return {"x1": policy[0], "x2": policy[1], "y": policy[2], "z": policy[3], "strategy_bits": bits, "strategy_code": f"q2:{bits}"}


def read_evidence(path):
    evidence = json.loads(Path(path).read_text(encoding="utf-8"))
    if evidence.get("sampling_plan") != "fixed_n":
        raise ValueError("INVALID_DATA: 仅 fixed_n 证据可使用固定时点 Clopper–Pearson 联合区间；自适应停止需提供可用 Q1 置信序列记录")
    if set(evidence) - {"mode", "sampling_plan", "note", "q2", "q3"} or "q2" not in evidence or "q3" not in evidence:
        raise ValueError("INVALID_DATA: evidence 顶层字段不符合 schema")
    for case_no in range(1, 7):
        key = f"case_{case_no}"
        if set(evidence["q2"].get(key, {})) != set(Q2_NAMES):
            raise ValueError(f"INVALID_DATA: q2.{key} 必须恰有 p1,p2,pf")
        validate_records(evidence["q2"][key], {"p1": "component", "p2": "component", "pf": "all_inputs_good"}, key)
    if set(evidence["q3"]) != set(Q3_NAMES):
        raise ValueError("INVALID_DATA: q3 参数名必须恰为 8 个 part、3 个 semi 和 final")
    validate_records(evidence["q3"], {**{f"part_{i}": "component" for i in range(1, 9)}, **{f"semi_{i}": "all_inputs_good" for i in range(1, 4)}, "final": "all_inputs_good"}, "q3")
    return evidence


def validate_records(records, required_conditioning, label):
    for name, expected in required_conditioning.items():
        item = records[name]
        if set(item) != {"N", "K", "conditioning"} or not isinstance(item["N"], int) or not isinstance(item["K"], int):
            raise ValueError(f"INVALID_DATA: {label}.{name} 必须为整数 N,K 和 conditioning")
        if item["N"] <= 0 or not 0 <= item["K"] <= item["N"]:
            raise ValueError(f"INVALID_DATA: {label}.{name} 要求 N>0 且 0<=K<=N")
        if item["conditioning"] != expected:
            raise ValueError(f"INVALID_CONDITIONING: {label}.{name} 应为 {expected!r}，实际为 {item['conditioning']!r}")


def point_estimates(records, names):
    return {name: records[name]["K"] / records[name]["N"] for name in names}


def cp_interval(record, alpha):
    n, k = record["N"], record["K"]
    return (0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1)),
            1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k)))


def q2_evaluator(case_no, params):
    case = dict(q2.CASES[case_no - 1]); case.update(params)
    return lambda policy: q2.evaluate_policy(policy, case)


def evaluate_set(policies, evaluator):
    rows = [evaluator(policy) for policy in policies]
    values = np.array([row.get("expected_profit", -np.inf) if row.get("status") == "SUCCESS_EXACT" else -np.inf for row in rows])
    if not np.isfinite(values).any():
        raise RuntimeError("参数样本下没有可行策略")
    return rows, values


def bayes_metrics(values, statuses):
    """对同一批共同随机数结果汇总；paired_se 是前二名的配对 MC 标准误。"""
    count, n = values.shape
    feasible = np.isfinite(values[0])
    if not np.all(np.isfinite(values[:, feasible])):
        raise RuntimeError("同一固定策略的可行性不应随内部 (0,1) 缺陷率改变")
    best = values.max(axis=1)
    ties = np.isclose(values, best[:, None], rtol=1e-11, atol=1e-11)
    opt = (ties / ties.sum(axis=1, keepdims=True)).sum(axis=0) / count
    regret = best[:, None] - values
    mean = np.full(n, np.nan); sd = np.full(n, np.nan); se = np.full(n, np.nan); p05 = np.full(n, np.nan); p95 = np.full(n, np.nan); negative = np.full(n, np.nan); mean_regret = np.full(n, np.nan)
    vf = values[:, feasible]; mean[feasible] = vf.mean(axis=0); sd[feasible] = vf.std(axis=0, ddof=1) if count > 1 else 0; se[feasible] = sd[feasible] / np.sqrt(count)
    if count >= 20: p05[feasible] = np.quantile(vf, .05, axis=0); p95[feasible] = np.quantile(vf, .95, axis=0)
    negative[feasible] = (vf < 0).mean(axis=0); mean_regret[feasible] = regret[:, feasible].mean(axis=0)
    result = {"status": statuses, "mean": mean, "sd": sd, "se": se, "p05": p05, "p95": p95, "opt": np.where(feasible, opt, np.nan), "negative": negative, "regret": mean_regret, "draws": count}
    if not np.allclose(np.nansum(result["opt"]), 1.0, atol=1e-12) or np.nanmin(regret) < -TOL:
        raise RuntimeError("Bayesian 最优频率或 regret 自检失败")
    order = np.argsort(-np.where(feasible, result["mean"], -np.inf))
    result["best_index"], result["second_index"] = int(order[0]), int(order[1])
    result["gap"] = float(result["mean"][order[0]] - result["mean"][order[1]])
    paired = values[:, order[0]] - values[:, order[1]]
    result["paired_se"] = float(paired.std(ddof=1) / np.sqrt(count)) if count > 1 else np.inf
    result["gap_pass"] = bool(count >= 20 and result["gap"] > MC_Z * result["paired_se"])
    result["near_indices"] = np.flatnonzero(feasible & ((result["mean"][order[0]] - result["mean"]) <= MC_Z * result["paired_se"] + TOL)).tolist()
    return result


def bayes_sequential(policies, records, names, prior, seed, minimum, maximum, batch_size, evaluator_factory):
    """每批都用同一参数抽样评价完整策略域，达到配对差距阈值后才停止。"""
    a, b = prior
    if a <= 0 or b <= 0: raise ValueError("Beta 先验参数必须为正")
    rng = np.random.default_rng(seed); values=[]; statuses=None; draws=0; batches=0
    alpha=np.array([a + records[n]["K"] for n in names]); beta_args=np.array([b + records[n]["N"]-records[n]["K"] for n in names])
    while draws < maximum:
        take=min(batch_size, maximum-draws); block=np.empty((take,len(policies)))
        for i, draw in enumerate(rng.beta(alpha, beta_args, size=(take,len(names)))):
            rows,block[i]=evaluate_set(policies,evaluator_factory(dict(zip(names,draw))))
            if statuses is None: statuses=[r["status"] for r in rows]
        values.append(block); draws+=take; batches+=1
        joined=np.vstack(values)
        if draws >= minimum:
            result=bayes_metrics(joined,statuses)
            if result["gap_pass"]:
                result.update({"stop_reason":"gap_exceeds_3_paired_se","batches":batches})
                return result
    result=bayes_metrics(np.vstack(values),statuses)
    result.update({"stop_reason":"B_max_reached_without_gap_tolerance","batches":batches})
    return result


def make_bayes_rows(base_rows, policies, explore, confirm, domain, prior_name, final_status, case_no=None):
    rows = []
    for i, (base, policy) in enumerate(zip(base_rows, policies)):
        row = dict(base)
        row.update({"domain": domain, "prior": prior_name, "batch": "explore", "mc_status": final_status, "posterior_mean_profit": explore["mean"][i], "posterior_profit_sd": explore["sd"][i], "mc_standard_error": explore["se"][i], "posterior_profit_p05": explore["p05"][i], "posterior_profit_p95": explore["p95"][i], "posterior_optimal_frequency": explore["opt"][i], "negative_profit_probability": explore["negative"][i], "mean_regret_to_sample_best": explore["regret"][i], "near_optimal_explore": i in explore["near_indices"], "explore_draws": explore["draws"], "explore_batches": explore["batches"], "explore_gap_to_second": explore["gap"], "explore_paired_mc_se": explore["paired_se"], "explore_stop_reason": explore["stop_reason"], "confirm_posterior_mean_profit": confirm["mean"][i], "confirm_mc_standard_error": confirm["se"][i], "confirm_optimal_frequency": confirm["opt"][i], "near_optimal_confirm": i in confirm["near_indices"], "confirm_draws": confirm["draws"], "confirm_batches": confirm["batches"], "confirm_gap_to_second": confirm["gap"], "confirm_paired_mc_se": confirm["paired_se"], "confirm_stop_reason": confirm["stop_reason"]})
        row.update(decode_q2(policy) if domain == "q2" else {"strategy_id": policy, "strategy_bits": base["strategy_bits"], "strategy_code": f"q3:{base['strategy_bits']}"})
        if case_no is not None: row["case"] = case_no
        rows.append(row)
    return pd.DataFrame(rows)


def monotonicity_check(policies, names, lower, upper, evaluator_factory, seed):
    rng = np.random.default_rng(seed); counterexamples = []
    selected = [policies[i] for i in rng.choice(len(policies), size=min(8, len(policies)), replace=False)]
    for policy in selected:
        base = rng.uniform(lower, upper)
        for j, name in enumerate(names):
            higher = base.copy(); higher[j] = base[j] + .5 * (upper[j] - base[j])
            lo = evaluator_factory(dict(zip(names, base)))(policy); hi = evaluator_factory(dict(zip(names, higher)))(policy)
            if lo.get("status") == hi.get("status") == "SUCCESS_EXACT" and hi["expected_profit"] > lo["expected_profit"] + TOL:
                counterexamples.append({"strategy": str(policy), "parameter": name, "low_profit": lo["expected_profit"], "high_profit": hi["expected_profit"], "low": float(base[j]), "high": float(higher[j])})
    return counterexamples


def structural_monotonicity_conditions(domain):
    """把单调耦合论证依赖的模型条件转为可审计的代码断言。"""
    if domain == "q2":
        nonnegative = all(all(case[k] >= 0 for k in ("buy1", "test1", "buy2", "test2", "assembly", "test_product", "replacement", "disassembly")) and case["price"] >= 0 for case in q2.CASES)
        only_costs = set(q2.COMPONENTS) == {"purchase_1", "purchase_2", "inspection_1", "inspection_2", "assembly", "product_inspection", "disassembly", "replacement_loss"}
    else:
        nonnegative = all(all(v >= 0 for v in leaf[1:]) for leaf in q3.LEAVES.values()) and all(all(v >= 0 for v in node[2:]) for node in q3.NODES.values()) and q3.PRICE >= 0 and q3.REPLACEMENT >= 0
        only_costs = set(q3.COSTS) == {"purchase", "part_inspection", "semi_inspection", "final_inspection", "semi_assembly", "final_assembly", "semi_disassembly", "final_disassembly", "replacement_loss"}
    return {**MODEL_CONTRACT, "nonnegative_costs": bool(nonnegative), "no_extra_or_negative_income": bool(only_costs)}


def robust_rows(policies, names, records, evaluator_factory, nominal_params, bayes_by_prior, domain, case_no=None):
    intervals = {coverage: np.array([cp_interval(records[n], alpha / len(names)) for n in names]) for coverage, alpha in ((90, .10), (95, .05))}
    nominal_rows, nominal_profit = evaluate_set(policies, evaluator_factory(nominal_params))
    rows = []
    checks = {}
    structure = structural_monotonicity_conditions(domain)
    for coverage, bounds in intervals.items():
        counter = monotonicity_check(policies, names, bounds[:, 0], bounds[:, 1], evaluator_factory, 9000 + coverage)
        certified = all(structure.values()) and not counter
        worst_rows, worst_profit = evaluate_set(policies, evaluator_factory(dict(zip(names, bounds[:, 1])))) if certified else (None, None)
        if worst_profit is not None and np.any(worst_profit[np.isfinite(worst_profit)] > nominal_profit[np.isfinite(worst_profit)] + TOL):
            raise RuntimeError(f"{domain} 稳健最坏利润高于 nominal 利润")
        checks[coverage] = {"counterexamples": counter, "structure_conditions": structure, "finite_difference_passed": not counter, "bounds": {n: [float(x) for x in bounds[i]] for i, n in enumerate(names)}, "worst_rows": worst_rows, "worst_profit": worst_profit}
    for i, (base, policy) in enumerate(zip(nominal_rows, policies)):
        row = dict(base); row.update({"domain": domain, "nominal_profit": nominal_profit[i], "uniform_posterior_mean_profit": bayes_by_prior["uniform"]["mean"][i], "jeffreys_posterior_mean_profit": bayes_by_prior["jeffreys"]["mean"][i]})
        row.update(decode_q2(policy) if domain == "q2" else {"strategy_id": policy, "strategy_bits": base["strategy_bits"], "strategy_code": f"q3:{base['strategy_bits']}"})
        if case_no is not None: row["case"] = case_no
        for coverage in (90, 95):
            check = checks[coverage]
            certified = all(check["structure_conditions"].values()) and check["finite_difference_passed"]
            row[f"robust_status_{coverage}"] = "ROBUST_CERTIFIED_BY_MONOTONICITY" if certified else "ROBUST_UNCERTIFIED"
            row[f"worst_profit_{coverage}"] = check["worst_profit"][i] if certified else np.nan
        rows.append(row)
    return pd.DataFrame(rows), checks


def best_robust(frame, coverage):
    valid = frame[frame[f"robust_status_{coverage}"].eq("ROBUST_CERTIFIED_BY_MONOTONICITY")].copy()
    best = valid[f"worst_profit_{coverage}"].max(); return valid[np.isclose(valid[f"worst_profit_{coverage}"], best, rtol=1e-10, atol=1e-10)].copy()


def mc_status(explore, confirm, quick):
    if quick or not (explore["gap_pass"] and confirm["gap_pass"]): return "MC_NOT_CONVERGED"
    return "SUCCESS_MC_TOL" if explore["best_index"] == confirm["best_index"] else "MC_NOT_CONVERGED"


def run_q2(evidence, plan, quick):
    policies = list(itertools.product((0, 1), repeat=4)); all_bayes=[]; all_robust=[]; best_bayes=[]; best_robust_rows=[]; summary={}
    for case_no in range(1, 7):
        records=evidence["q2"][f"case_{case_no}"]; nominal=point_estimates(records,Q2_NAMES); factory=lambda p, c=case_no: q2_evaluator(c,p)
        base_rows,_=evaluate_set(policies,factory(nominal)); per_prior={}; info={}
        for prior_name, prior in PRIORS.items():
            ex=bayes_sequential(policies,records,Q2_NAMES,prior,EXPLORE_SEED,plan["explore_min"],plan["explore_max"],plan["batch"],factory); co=bayes_sequential(policies,records,Q2_NAMES,prior,CONFIRM_SEED,plan["confirm_min"],plan["confirm_max"],plan["batch"],factory); per_prior[prior_name]=ex
            status=mc_status(ex,co,quick)
            frame=make_bayes_rows(base_rows,policies,ex,co,"q2",prior_name,status,case_no); all_bayes.append(frame)
            b=frame.iloc[[ex["best_index"]]].copy(); b["selection_batch"]="explore"; b["confirmation_status"]=status; b["explore_gap_to_second"]=ex["gap"]; b["confirm_gap_to_second"]=co["gap"]; b["confirm_best_strategy_bits"]="".join(map(str, policies[co["best_index"]])); best_bayes.append(b)
            if status == "MC_NOT_CONVERGED":
                c=frame.iloc[[co["best_index"]]].copy(); c["selection_batch"]="confirm_near_optimal"; c["posterior_mean_profit"]=co["mean"][co["best_index"]]; c["mc_standard_error"]=co["se"][co["best_index"]]; c["confirmation_status"]=status; c["explore_gap_to_second"]=ex["gap"]; c["confirm_gap_to_second"]=co["gap"]; c["confirm_best_strategy_bits"]="".join(map(str, policies[co["best_index"]])); best_bayes.append(c)
            info[prior_name]={"explore_best_bits":"".join(map(str, policies[ex["best_index"]])),"confirm_best_bits":"".join(map(str, policies[co["best_index"]])),"status":status,"explore":{"draws":ex["draws"],"batches":ex["batches"],"stop_reason":ex["stop_reason"],"gap":ex["gap"],"paired_mc_se":ex["paired_se"],"near_optimal_bits":["".join(map(str,policies[i])) for i in ex["near_indices"]]},"confirm":{"draws":co["draws"],"batches":co["batches"],"stop_reason":co["stop_reason"],"gap":co["gap"],"paired_mc_se":co["paired_se"],"near_optimal_bits":["".join(map(str,policies[i])) for i in co["near_indices"]]}}
        robust, checks=robust_rows(policies,Q2_NAMES,records,factory,nominal,per_prior,"q2",case_no); all_robust.append(robust)
        for coverage in (90,95):
            b=best_robust(robust,coverage); b["coverage"] = coverage; best_robust_rows.append(b)
        summary[f"case_{case_no}"]={"bayesian":info,"robust":{str(k):{"status":"ROBUST_CERTIFIED_BY_MONOTONICITY" if all(v["structure_conditions"].values()) and v["finite_difference_passed"] else "ROBUST_UNCERTIFIED","counterexamples":v["counterexamples"],"structure_conditions":v["structure_conditions"],"finite_difference_passed":v["finite_difference_passed"],"intervals":v["bounds"]} for k,v in checks.items()}}
    return pd.concat(all_bayes,ignore_index=True),pd.concat(best_bayes,ignore_index=True),pd.concat(all_robust,ignore_index=True),pd.concat(best_robust_rows,ignore_index=True),summary


def run_q3(evidence, plan, quick):
    policies=list(range(65536)); records=evidence["q3"]; nominal=point_estimates(records,Q3_NAMES); factory=lambda p: q3.make_q3_evaluator(p)
    base_rows,_=evaluate_set(policies,factory(nominal)); per_prior={}; all_bayes=[]; best_bayes=[]; info={}
    for prior_name,prior in PRIORS.items():
        ex=bayes_sequential(policies,records,Q3_NAMES,prior,EXPLORE_SEED,plan["explore_min"],plan["explore_max"],plan["batch"],factory); co=bayes_sequential(policies,records,Q3_NAMES,prior,CONFIRM_SEED,plan["confirm_min"],plan["confirm_max"],plan["batch"],factory); per_prior[prior_name]=ex
        status=mc_status(ex,co,quick); frame=make_bayes_rows(base_rows,policies,ex,co,"q3",prior_name,status); all_bayes.append(frame)
        b=frame.iloc[[ex["best_index"]]].copy(); b["selection_batch"]="explore"; b["confirmation_status"]=status; b["explore_gap_to_second"]=ex["gap"]; b["confirm_gap_to_second"]=co["gap"]; b["confirm_best_strategy_id"]=int(policies[co["best_index"]]); b["confirm_best_strategy_bits"]=base_rows[co["best_index"]]["strategy_bits"]; best_bayes.append(b)
        if status == "MC_NOT_CONVERGED":
            c=frame.iloc[[co["best_index"]]].copy(); c["selection_batch"]="confirm_near_optimal"; c["posterior_mean_profit"]=co["mean"][co["best_index"]]; c["mc_standard_error"]=co["se"][co["best_index"]]; c["confirmation_status"]=status; c["explore_gap_to_second"]=ex["gap"]; c["confirm_gap_to_second"]=co["gap"]; c["confirm_best_strategy_id"]=int(policies[co["best_index"]]); c["confirm_best_strategy_bits"]=base_rows[co["best_index"]]["strategy_bits"]; best_bayes.append(c)
        info[prior_name]={"explore_best_id":int(policies[ex["best_index"]]),"confirm_best_id":int(policies[co["best_index"]]),"status":status,"explore":{"draws":ex["draws"],"batches":ex["batches"],"stop_reason":ex["stop_reason"],"gap":ex["gap"],"paired_mc_se":ex["paired_se"],"near_optimal_ids":[int(policies[i]) for i in ex["near_indices"]]},"confirm":{"draws":co["draws"],"batches":co["batches"],"stop_reason":co["stop_reason"],"gap":co["gap"],"paired_mc_se":co["paired_se"],"near_optimal_ids":[int(policies[i]) for i in co["near_indices"]]}}
    robust,checks=robust_rows(policies,Q3_NAMES,records,factory,nominal,per_prior,"q3"); best_rows=[]
    for coverage in (90,95): b=best_robust(robust,coverage);b["coverage"]=coverage;best_rows.append(b)
    summary={"bayesian":info,"robust":{str(k):{"status":"ROBUST_CERTIFIED_BY_MONOTONICITY" if all(v["structure_conditions"].values()) and v["finite_difference_passed"] else "ROBUST_UNCERTIFIED","counterexamples":v["counterexamples"],"structure_conditions":v["structure_conditions"],"finite_difference_passed":v["finite_difference_passed"],"intervals":v["bounds"]} for k,v in checks.items()}}
    return pd.concat(all_bayes,ignore_index=True),pd.concat(best_bayes,ignore_index=True),robust,pd.concat(best_rows,ignore_index=True),summary


def validate_nominal_consistency(evidence):
    for c in range(1,7):
        params=point_estimates(evidence["q2"][f"case_{c}"],Q2_NAMES)
        for policy in itertools.product((0,1),repeat=4):
            a=q2.evaluate_policy(policy,q2.CASES[c-1]); b=q2_evaluator(c,params)(policy)
            if a.get("status")!=b.get("status") or abs(a.get("expected_profit",0)-b.get("expected_profit",0))>TOL: raise RuntimeError("Q2 名义参数一致性检查失败")
    params=point_estimates(evidence["q3"],Q3_NAMES); f=q3.make_q3_evaluator(params)
    for strategy in range(65536):
        a=q3.evaluate(strategy); b=f(strategy)
        if a.get("status")!=b.get("status") or abs(a.get("expected_profit",0)-b.get("expected_profit",0))>TOL: raise RuntimeError("Q3 名义参数一致性检查失败")


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--evidence",default=str(DEMO)); parser.add_argument("--quick",action="store_true",help="小样本流程调试；结果一律 MC_NOT_CONVERGED"); args=parser.parse_args()
    plan = QUICK_PLAN if args.quick else DEFAULT_PLAN
    evidence=read_evidence(args.evidence); validate_nominal_consistency(evidence)
    q2ba,q2bb,q2ra,q2rb,q2sum=run_q2(evidence,plan["q2"],args.quick); q3ba,q3bb,q3ra,q3rb,q3sum=run_q3(evidence,plan["q3"],args.quick)
    if len(q2ba)!=6*16*2 or len(q2ra)!=6*16 or len(q3ba)!=65536*2 or len(q3ra)!=65536: raise RuntimeError("INCOMPLETE_POLICY_SET")
    OUTDIR.mkdir(parents=True,exist_ok=True)
    outputs={"q2_bayesian_all_policies.csv":q2ba,"q2_bayesian_best_policies.csv":q2bb,"q2_robust_all_policies.csv":q2ra,"q2_robust_best_policies.csv":q2rb,"q3_bayesian_all_policies.csv":q3ba,"q3_bayesian_best_policies.csv":q3bb,"q3_robust_all_policies.csv":q3ra,"q3_robust_best_policies.csv":q3rb}
    for name,frame in outputs.items(): frame.to_csv(OUTDIR/name,index=False,encoding="utf-8-sig")
    evidence_used=dict(evidence); evidence_used["source_path"]=str(Path(args.evidence)); evidence_used["demo_marker"]="DEMO_ONLY_NOT_OFFICIAL_DATA" if evidence.get("mode")=="DEMO_ONLY_NOT_OFFICIAL_DATA" else "USER_SUPPLIED_EVIDENCE"
    (OUTDIR/"evidence_used.json").write_text(json.dumps(evidence_used,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    checks={"evidence_schema_and_conditioning":"PASS","beta_posterior_parameters":"PASS","q2_nominal_evaluator_consistency":"PASS","q3_nominal_evaluator_consistency":"PASS","bayesian_optimal_frequency_sums_to_one":"PASS","bayesian_regret_nonnegative":"PASS","q2_full_policy_coverage":len(q2ra)==96,"q3_full_policy_coverage":len(q3ra)==65536,"robust_worst_not_above_nominal":"PASS","demo_marker_written":evidence_used["demo_marker"]=="DEMO_ONLY_NOT_OFFICIAL_DATA","q2_nominal_status_counts":q2ra.status.value_counts().to_dict(),"q3_nominal_status_counts":q3ra.status.value_counts().to_dict(),"max_q2_linear_residual":float(q2ra.loc[q2ra.status.eq("SUCCESS_EXACT"),"linear_residual"].max()),"max_q3_local_residual":float(q3ra.loc[q3ra.status.eq("SUCCESS_EXACT"),"max_local_equation_residual"].max())}
    summary={"model_bayesian":"Q4-M2","model_robust":"Q4-M3","algorithms":["Q4-A1", "Q4-A2"],"evidence_marker":evidence_used["demo_marker"],"sampling_plan":"fixed_n","policy_domains":{"q2_per_case":16,"q3":65536},"mc":{"quick":args.quick,"explore_seed":EXPLORE_SEED,"confirm_seed":CONFIRM_SEED,"z_for_paired_gap":MC_Z,"plan":plan,"rule":"仅当探索和独立确认最优策略相同，且两批最优—第二名配对差距均大于 3 倍配对 MC 标准误时为 SUCCESS_MC_TOL；否则 MC_NOT_CONVERGED。"},"checks":checks,"q2":q2sum,"q3":q3sum,"robust_statement":"结构性单调耦合论证成立且被代码条件校验、有限差分实现抽查同时通过时，固定策略在矩形 Bonferroni 区间的最坏点为全部缺陷率上界；有限差分并非唯一认证依据。","q3_evaluator":"复用修正后的回收再检测局部闭环评价器；回收件再次检测计费但不重复采购。"}
    (OUTDIR/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("证据:", evidence_used["demo_marker"], "| Q2 策略:",len(q2ra),"| Q3 策略:",len(q3ra))
    for title,frame in (("Q2 Bayesian",q2bb),("Q2 Robust",q2rb),("Q3 Bayesian",q3bb),("Q3 Robust",q3rb)):
        cols=[c for c in ["case","prior","coverage","strategy_id","strategy_bits","x1","x2","y","z","posterior_mean_profit","worst_profit_90","worst_profit_95","confirmation_status","robust_status_90"] if c in frame]
        print("\n"+title); print(frame[cols].to_string(index=False,float_format=lambda x:f"{x:.5f}"))
    print("结果目录:",OUTDIR)


if __name__ == "__main__": main()
