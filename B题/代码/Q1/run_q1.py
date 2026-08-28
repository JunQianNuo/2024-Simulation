"""Q1 主程序：跑通 Q1-M5 / Q1-A1 的完整流程并落盘结果。

流程（对应阶段3报告 §4）：
    0. 固定样本精确二项基准自检   -> U_0.90(22,0) ≈ 0.0994, L_0.95(2,2) ≈ 0.2236
    1. 构造 34 个候选的动作表     -> 双单侧 Beta-Binomial mixture CS
    2. 两套独立实现交叉核验       -> 端点差 > 1e-8 则 CS_CROSSCHECK_FAILED
    3. 精确路径 DP 评价 13 个 p   -> ASN / P50 / P90 / P(A) / P(R) / P(U)
    4. Pareto 前沿 + 拐点选择     -> 三个权重方案的敏感性
    5. 导出推荐方案的边界表       -> 题目要求的"具体结果"(1)(2)

用法：
    python -m q1.run_q1                    # 全网格，约 1-3 分钟
    python -m q1.run_q1 --quick            # 缩减网格，冒烟测试用
    python -m q1.run_q1 --outdir results/q1-custom  # 指定输出目录
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .schemas import Candidate, CandidateResult, Q1Problem, Status
from .bernoulli_cs import clopper_pearson_lower, clopper_pearson_upper
from .exact_path_dp import evaluate_at_p, first_accept_time_all_good
from .pareto_search import aggregate_objectives, pareto_front, recommend_three, select_knee
from .stopping_rule import apply_n_max, boundary_table, build_action_table, crosscheck_action_table

PACKAGE_DIR = Path(__file__).resolve().parent
CODE_DIR = PACKAGE_DIR.parent


# --------------------------------------------------------------------------
# 0. 固定样本基准自检
# --------------------------------------------------------------------------
def run_baseline_checks() -> dict[str, float]:
    u22 = clopper_pearson_upper(22, 0, 0.90)
    l22 = clopper_pearson_lower(2, 2, 0.95)
    closed_u = 1.0 - 0.1 ** (1 / 22)
    closed_l = 0.05 ** 0.5

    print("=" * 78)
    print("[0] 固定样本精确二项基准（仅数量级核验，不是序贯规则）")
    print(f"    U_0.90(22, 0) = {u22:.6f}   闭式 1-0.1^(1/22) = {closed_u:.6f}")
    print(f"    L_0.95( 2, 2) = {l22:.6f}   闭式 0.05^(1/2)   = {closed_l:.6f}")

    assert abs(u22 - closed_u) < 1e-10, "U_0.90(22,0) 与闭式不符"
    assert abs(l22 - closed_l) < 1e-10, "L_0.95(2,2) 与闭式不符"
    assert abs(u22 - 0.0994) < 5e-4, "U_0.90(22,0) 偏离阶段2报告的 0.0994"
    assert abs(l22 - 0.2236) < 5e-4, "L_0.95(2,2) 偏离阶段2报告的 0.2236"
    print("    ✓ 与阶段2报告 §4.2 的两个边界值一致")
    return {"U_0.90_22_0": u22, "L_0.95_2_2": l22}


# --------------------------------------------------------------------------
# 1-3. 网格评价
# --------------------------------------------------------------------------
def build_candidates(t_opts: list[int], n_maxs: list[int]) -> list[Candidate]:
    cands = [
        Candidate(t_opt=t, n_max=n)
        for t in t_opts
        for n in n_maxs
        if n >= t
    ]
    cands.sort(key=lambda c: (c.t_opt, c.n_max))
    return cands


def sweep_grid(
    problem: Q1Problem,
    candidates: list[Candidate],
    p_grid: list[float],
    tol_mass: float,
    tol_cs: float,
    prune: float,
    do_crosscheck: bool = True,
) -> list[CandidateResult]:
    """对每个候选构造动作表并精确评价。动作表只依赖 t_opt，按 t_opt 缓存复用。"""
    results: list[CandidateResult] = []

    by_t_opt: dict[int, list[Candidate]] = {}
    for c in candidates:
        by_t_opt.setdefault(c.t_opt, []).append(c)

    for t_opt, group in sorted(by_t_opt.items()):
        n_top = max(c.n_max for c in group)
        t0 = time.perf_counter()
        base_act = build_action_table(
            n_max=n_top,
            p0=problem.p0,
            alpha_R=problem.alpha_R,
            alpha_A=problem.alpha_A,
            t_opt=t_opt,
        )
        build_ms = (time.perf_counter() - t0) * 1e3

        cc_msgs: list[str] = []
        cc_ok = True
        if do_crosscheck:
            cc_ok, cc_msgs = crosscheck_action_table(
                base_act, problem.p0, problem.alpha_R, problem.alpha_A, t_opt, tol=tol_cs
            )
        flag = "✓" if cc_ok else "✗"
        print(f"    t_opt={t_opt:<5d} 动作表 N={n_top:<5d} ({build_ms:7.1f} ms)  交叉核验 {flag}")
        if not cc_ok:
            for m in cc_msgs[:5]:
                print(f"        {m}")

        for cand in group:
            t1 = time.perf_counter()
            act = apply_n_max(base_act, cand.n_max)
            points = [evaluate_at_p(act, p, cand.n_max, prune=prune) for p in p_grid]
            elapsed = (time.perf_counter() - t1) * 1e3

            warnings: list[str] = []
            status = Status.SUCCESS_EXACT
            worst_res = max(pt.mass_residual for pt in points)
            if worst_res > tol_mass:
                status = Status.PROB_CONSERVATION_FAILED
                warnings.append(f"概率守恒残差 {worst_res:.3e} > {tol_mass:.1e}")
            if not cc_ok:
                status = Status.CS_CROSSCHECK_FAILED
                warnings.extend(cc_msgs[:3])
            if max(pt.prob_undecided for pt in points) > 1e-12:
                warnings.append("存在非零未决概率（UNDECIDED_CAP，属模型正常输出）")

            results.append(
                CandidateResult(
                    candidate=cand,
                    points=points,
                    status=status,
                    warnings=warnings,
                    runtime_ms=elapsed,
                    first_accept_t_all_good=first_accept_time_all_good(act, cand.n_max),
                )
            )
    return results


# --------------------------------------------------------------------------
# 导出
# --------------------------------------------------------------------------
def export_tables(
    results: list[CandidateResult],
    p_grid: list[float],
    schemes: dict[str, list[float] | None],
    outdir: Path,
) -> pd.DataFrame:
    rows = []
    for r in results:
        for pt in r.points:
            rows.append(
                {
                    "t_opt": r.candidate.t_opt,
                    "N_max": r.candidate.n_max,
                    "p": pt.p,
                    "ASN": pt.asn,
                    "P50": pt.p50,
                    "P90": pt.p90,
                    "P_accept": pt.prob_accept,
                    "P_reject": pt.prob_reject,
                    "P_undecided": pt.prob_undecided,
                    "mass_residual": pt.mass_residual,
                    "status": r.status.value,
                }
            )
    oc = pd.DataFrame(rows)
    oc.to_csv(outdir / "q1_operating_characteristics.csv", index=False, encoding="utf-8-sig")

    agg = pd.DataFrame(
        [
            {
                "t_opt": r.candidate.t_opt,
                "N_max": r.candidate.n_max,
                "first_accept_all_good": r.first_accept_t_all_good,
                "status": r.status.value,
                "runtime_ms": round(r.runtime_ms, 1),
                **{f"ASN_w[{k}]": v for k, v in r.asn_weighted.items()},
                **{f"U_w[{k}]": v for k, v in r.undecided_weighted.items()},
            }
            for r in results
        ]
    )
    agg.to_csv(outdir / "q1_candidate_objectives.csv", index=False, encoding="utf-8-sig")
    return agg


def export_boundary(act: np.ndarray, cand: Candidate, outdir: Path) -> pd.DataFrame:
    bt = pd.DataFrame(boundary_table(act))
    bt.to_csv(outdir / "q1_decision_boundary.csv", index=False, encoding="utf-8-sig")
    return bt


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="2024 CUMCM B题 问题一 (Q1-M5 / Q1-A1)")
    ap.add_argument("--config", default=str(PACKAGE_DIR / "q1_grid.yaml"))
    ap.add_argument("--outdir", default=str(CODE_DIR / "results" / "q1"))
    ap.add_argument("--quick", action="store_true", help="缩减网格，冒烟测试")
    ap.add_argument("--no-crosscheck", action="store_true", help="跳过交叉核验（调试用）")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    problem = Q1Problem(
        p0=cfg["problem"]["p0"],
        alpha_R=cfg["problem"]["alpha_R"],
        alpha_A=cfg["problem"]["alpha_A"],
    )
    problem.validate()

    p_grid = list(cfg["representative_p"])
    schemes = dict(cfg["weight_schemes"])
    tol = cfg["tolerances"]

    t_opts = list(cfg["grid"]["t_opt"])
    n_maxs = list(cfg["grid"]["n_max"])
    if args.quick:
        t_opts, n_maxs = [50, 200], [200, 400]
        p_grid = [0.05, 0.09, 0.10, 0.12, 0.20]
        schemes = {"equal": None}

    run_baseline_checks()

    candidates = build_candidates(t_opts, n_maxs)
    print("=" * 78)
    print(f"[1] 候选网格：{len(candidates)} 个 (t_opt, N_max) 组合")
    if not args.quick:
        expected = cfg["grid"]["expected_candidates"]
        assert len(candidates) == expected, f"候选数应为 {expected}，实际 {len(candidates)}"
        print(f"    ✓ 与阶段3报告 §4.3 的 G={expected} 一致")

    print("=" * 78)
    print("[2-3] 构造动作表 + 交叉核验 + 精确路径 DP")
    t_start = time.perf_counter()
    results = sweep_grid(
        problem, candidates, p_grid,
        tol_mass=tol["prob_conservation"],
        tol_cs=tol["cs_crosscheck"],
        prune=tol["dp_prune"],
        do_crosscheck=not args.no_crosscheck,
    )
    print(f"    总耗时 {time.perf_counter() - t_start:.1f} s")

    worst = max(pt.mass_residual for r in results for pt in r.points)
    print(f"    概率守恒最差残差 = {worst:.3e}  (阈值 {tol['prob_conservation']:.0e})")
    assert worst <= tol["prob_conservation"], "概率守恒失败，DP 分流有漏"

    bad = [r for r in results if r.status not in (Status.SUCCESS_EXACT,)]
    if bad:
        print(f"    ⚠ {len(bad)} 个候选状态非 SUCCESS_EXACT，已按失败关闭标记")

    for r in results:
        aggregate_objectives(r, p_grid, schemes)

    print("=" * 78)
    print("[4] Pareto 前沿与权重敏感性")
    fronts: dict[str, list[CandidateResult]] = {}
    for name in schemes:
        front = pareto_front(results, scheme=name)
        fronts[name] = front
        knee = select_knee(front, scheme=name)
        tag = "一致" if knee["agree"] else "不一致 -> 报告三方案"
        print(f"    权重={name:<15s} 前沿 {len(front):2d} 点   拐点准则{tag}")
        for i, r in enumerate(front):
            mark = " <= 拐点" if i == knee["knee_idx"] else ""
            print(
                f"        {r.candidate.label:<26s} "
                f"ASN_w={r.asn_weighted[name]:9.2f}  "
                f"U_w={r.undecided_weighted[name]:.6f}{mark}"
            )

    main_front = fronts["equal"]
    three = recommend_three(main_front, "equal")
    rec = three["均衡型"]

    print("=" * 78)
    print("[5] 推荐方案与题目要求的具体结果")
    print(f"    省样本型：{three['省样本型'].candidate.label}")
    print(f"    均衡型  ：{three['均衡型'].candidate.label}   <- 主推荐")
    print(f"    低未决型：{three['低未决型'].candidate.label}")

    base_act = build_action_table(
        rec.candidate.n_max, problem.p0, problem.alpha_R, problem.alpha_A, rec.candidate.t_opt
    )
    act = apply_n_max(base_act, rec.candidate.n_max)
    bt = export_boundary(act, rec.candidate, outdir)

    first_acc = rec.first_accept_t_all_good
    print()
    print(f"    情形(2) 接收边界（90% 信度认定次品率不超过 10%）：")
    print(f"        全良品路径首次可接收样本量 n = {first_acc}")
    print(f"        对照固定样本基准 22 件：{'✓ 更保守，符合 time-uniform 预期' if first_acc and first_acc >= 22 else '✗ 早于固定样本基准，需复查'}")
    head = bt[bt["k_accept_max"].notna()].head(8)
    for _, row in head.iterrows():
        print(f"        n={int(row['n']):<5d} 次品数 <= {int(row['k_accept_max'])} 时接收")

    print()
    print(f"    情形(1) 拒收边界（95% 信度认定次品率超过 10%）：")
    hr = bt[bt["k_reject_min"].notna()].head(8)
    for _, row in hr.iterrows():
        print(f"        n={int(row['n']):<5d} 次品数 >= {int(row['k_reject_min'])} 时拒收")

    print()
    print("    推荐方案在各代表性 p 下的精确性能：")
    print(f"        {'p':>6s} {'ASN':>9s} {'P50':>6s} {'P90':>6s} {'P(接收)':>9s} {'P(拒收)':>9s} {'P(未决)':>9s}")
    for pt in rec.points:
        print(
            f"        {pt.p:6.2f} {pt.asn:9.2f} {pt.p50:6d} {pt.p90:6d} "
            f"{pt.prob_accept:9.5f} {pt.prob_reject:9.5f} {pt.prob_undecided:9.5f}"
        )

    export_tables(results, p_grid, schemes, outdir)

    summary = {
        "problem": "2024-CUMCM-B-Q1",
        "model": "Q1-M5",
        "algorithm": "Q1-A1",
        "status": Status.SUCCESS_EXACT.value,
        "n_candidates": len(candidates),
        "p_grid": p_grid,
        "worst_mass_residual": worst,
        "baseline": {"U_0.90(22,0)": clopper_pearson_upper(22, 0, 0.90),
                     "L_0.95(2,2)": clopper_pearson_lower(2, 2, 0.95)},
        "recommended": {
            "省样本型": three["省样本型"].candidate.label,
            "均衡型": three["均衡型"].candidate.label,
            "低未决型": three["低未决型"].candidate.label,
        },
        "first_accept_t_all_good": first_acc,
        "pareto_front_size": {k: len(v) for k, v in fronts.items()},
        "optimality_claim": (
            "预先声明的有限候选网格内的精确 Pareto 前沿；"
            "不宣称对连续 t_opt 或所有可能停止规则全局最优"
        ),
    }
    (outdir / "q1_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print()
    print("=" * 78)
    print(f"结果已写入 {outdir}/")
    print("    q1_operating_characteristics.csv  每个候选 × 每个 p 的精确性能")
    print(f"    q1_candidate_objectives.csv       {len(candidates)} 个候选的加权目标 (ASN_w, U_w)")
    print("    q1_decision_boundary.csv          推荐方案的接收/拒收边界表")
    print("    q1_summary.json                   运行摘要与最优性称谓")


if __name__ == "__main__":
    main()
