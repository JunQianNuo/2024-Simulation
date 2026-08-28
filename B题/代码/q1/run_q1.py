"""2024 CUMCM B题问题一：固定五阶段抽样的精确评价。"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import beta, binom


p0 = 0.10
STAGES = [40, 80, 160, 320, 800]
ALPHA_REJECT = [0.01, 0.01, 0.01, 0.01, 0.01]
ALPHA_ACCEPT = [0.04, 0.025, 0.015, 0.012, 0.008]

P_GRID = [
    0.01, 0.03, 0.05, 0.07, 0.08, 0.09, 0.10,
    0.11, 0.12, 0.13, 0.15, 0.20, 0.30,
]
OUTDIR = Path(__file__).resolve().parent.parent / "results" / "q1"


def cp_lower(n: int, x: int, alpha: float) -> float:
    """单侧 Clopper--Pearson 下置信界。"""
    return 0.0 if x == 0 else float(beta.ppf(alpha, x, n - x + 1))


def cp_upper(n: int, x: int, alpha: float) -> float:
    """单侧 Clopper--Pearson 上置信界。"""
    return 1.0 if x == n else float(beta.ppf(1.0 - alpha, x + 1, n - x))


def boundaries() -> list[dict[str, int | None]]:
    rows = []
    for n, alpha_r, alpha_a in zip(STAGES, ALPHA_REJECT, ALPHA_ACCEPT):
        reject = [x for x in range(n + 1) if cp_lower(n, x, alpha_r) > p0]
        accept = [x for x in range(n + 1) if cp_upper(n, x, alpha_a) <= p0]
        rows.append({
            "n": n,
            "k_accept_max": max(accept) if accept else None,
            "k_reject_min": min(reject) if reject else None,
        })
    return rows


def evaluate(p: float, plan: list[dict[str, int | None]]) -> dict[str, float | int]:
    """以阶段节点为状态的精确二项路径 DP；不使用蒙特卡洛。"""
    alive = np.array([1.0])
    previous_n = 0
    asn = 0.0
    accept = reject = undecided = 0.0
    stop_mass: list[tuple[int, float]] = []

    for index, row in enumerate(plan):
        n = int(row["n"])
        increment = n - previous_n
        asn += increment * float(alive.sum())
        alive = np.convolve(alive, binom.pmf(np.arange(increment + 1), increment, p))

        x = np.arange(n + 1)
        accept_mask = x <= row["k_accept_max"] if row["k_accept_max"] is not None else np.zeros(n + 1, dtype=bool)
        reject_mask = x >= row["k_reject_min"] if row["k_reject_min"] is not None else np.zeros(n + 1, dtype=bool)
        a_mass = float(alive[accept_mask].sum())
        r_mass = float(alive[reject_mask].sum())
        accept += a_mass
        reject += r_mass

        if index == len(plan) - 1:
            u_mass = float(alive[~(accept_mask | reject_mask)].sum())
            undecided += u_mass
            stop_mass.append((n, a_mass + r_mass + u_mass))
        else:
            stop_mass.append((n, a_mass + r_mass))
            alive[accept_mask | reject_mask] = 0.0

        previous_n = n

    total = accept + reject + undecided
    cumulative = 0.0
    p50 = p90 = STAGES[-1]
    for n, mass in stop_mass:
        cumulative += mass
        if cumulative >= 0.50 * total and p50 == STAGES[-1]:
            p50 = n
        if cumulative >= 0.90 * total:
            p90 = n
            break
    return {
        "p": p, "ASN": asn, "P50": p50, "P90": p90,
        "P_accept": accept, "P_reject": reject, "P_undecided": undecided,
        "mass_residual": abs(total - 1.0),
    }


def self_check(rows: list[dict[str, float | int]]) -> None:
    if not np.isclose(sum(ALPHA_REJECT), 0.05) or not np.isclose(sum(ALPHA_ACCEPT), 0.10):
        raise RuntimeError("阶段错误预算之和不符合 0.05 / 0.10")
    for row in rows:
        total = float(row["P_accept"]) + float(row["P_reject"]) + float(row["P_undecided"])
        if abs(total - 1.0) > 1e-10:
            raise RuntimeError(f"p={row['p']}: 概率守恒失败 ({total:.16f})")
        if float(row["p"]) <= p0 and float(row["P_reject"]) > 0.05 + 1e-10:
            raise RuntimeError(f"p={row['p']}: 拒收概率超过 0.05")
        if float(row["p"]) > p0 and float(row["P_accept"]) > 0.10 + 1e-10:
            raise RuntimeError(f"p={row['p']}: 接收概率超过 0.10")


def write_outputs(plan: list[dict[str, int | None]], rows: list[dict[str, float | int]]) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    with (OUTDIR / "operating_characteristics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (OUTDIR / "decision_boundary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["n", "k_accept_max", "k_reject_min"])
        writer.writeheader()
        writer.writerows(plan)
    summary = {
        "problem": "2024-CUMCM-B-Q1",
        "method": "pre-specified five-stage group-sequential sampling with one-sided Clopper-Pearson bounds",
        "p0": p0, "stages": STAGES,
        "alpha_reject": ALPHA_REJECT, "alpha_accept": ALPHA_ACCEPT,
        "p_grid": P_GRID, "worst_mass_residual": max(float(r["mass_residual"]) for r in rows),
        "decision_at_n800": "undecided / recommend additional inspection when neither boundary is met",
    }
    (OUTDIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    plan = boundaries()
    rows = [evaluate(p, plan) for p in P_GRID]
    self_check(rows)  # 先验收，后写最终结果。
    write_outputs(plan, rows)

    print("固定五阶段计划:", STAGES)
    print("阶段边界（x <= 接收上限；x >= 拒收下限）：")
    for row in plan:
        print(f"  n={row['n']:>3}: 接收 <= {row['k_accept_max']}, 拒收 >= {row['k_reject_min']}")
    print("\n代表性次品率的精确路径 DP：")
    print("  p      ASN     P50  P90   P(接收)    P(拒收)    P(未决)")
    for row in rows:
        print(f"  {float(row['p']):.2f}  {float(row['ASN']):7.3f}  {int(row['P50']):3d}  {int(row['P90']):3d}  {float(row['P_accept']):.6f}  {float(row['P_reject']):.6f}  {float(row['P_undecided']):.6f}")
    print(f"\n自检通过；概率守恒最差残差: {max(float(r['mass_residual']) for r in rows):.3e}")
    print(f"结果已写入: {OUTDIR}")


if __name__ == "__main__":
    main()
