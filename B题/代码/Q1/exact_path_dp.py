"""Q1-A1 性能评价：精确路径概率递推（不使用 Monte Carlo）。

依据：阶段3算法设计报告 §4.4。

设 q_t(k; p) = 执行完时刻 t 的决策后，仍处于"继续"且累计 k 个次品的概率质量。
初始化 q_0(0) = 1。一步转移：

    q~_{t+1}(k) = (1-p) q_t(k) + p q_t(k-1)

再按动作表把 q~_{t+1} 分流到接收 / 拒收 / 未决 / 下一时刻的 q_{t+1}。于是

    E_p[tau] = sum_{t=0}^{N_max-1} P_p(tau > t) = sum_{t=0}^{N_max-1} sum_k q_t(k)

所有停止概率、分位数与 ASN 都由有限状态 DP 精确得到，只有浮点误差，
并且可以精确核对总概率是否为 1（阶段3报告要求 |sum - 1| <= 1e-10）。

为什么不用 MC：Pareto 前沿要比较 34 个候选在 13 个 p 上的两个目标，
MC 噪声会让相近候选的支配关系随种子翻转，前沿不可复现。
"""

from __future__ import annotations

import numpy as np

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.schemas import (
    ACT_ACCEPT,
    ACT_CONTINUE,
    ACT_REJECT,
    ACT_UNDECIDED,
    OperatingPoint,
)

__all__ = ["evaluate_at_p", "first_accept_time_all_good"]


def evaluate_at_p(
    act: np.ndarray,
    p: float,
    n_max: int,
    prune: float = 1e-18,
) -> OperatingPoint:
    """在真实次品率 p 下精确评价规则，返回 ASN / 分位数 / 三种终止概率。

    act 必须已经过 apply_n_max 处理（末行含 ACT_UNDECIDED）。
    """
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"p 必须在 [0,1]，收到 {p}")

    q = np.zeros(n_max + 2, dtype=np.float64)
    q[0] = 1.0                       # t = 0，尚未观测
    active = 0                       # 当前最大可能的 k

    stop_pmf = np.zeros(n_max + 1, dtype=np.float64)  # tau 的分布
    p_accept = 0.0
    p_reject = 0.0
    p_undecided = 0.0
    survival_sum = 1.0               # t=0 时 P(tau > 0) = 1

    for t in range(n_max):
        cur = q[: active + 1]
        nxt = np.empty(active + 2, dtype=np.float64)
        nxt[0] = (1.0 - p) * cur[0]
        if active >= 1:
            nxt[1 : active + 1] = (1.0 - p) * cur[1 : active + 1] + p * cur[:active]
        else:
            nxt[1:1] = 0.0
        nxt[active + 1] = p * cur[active]

        tt = t + 1
        row = act[tt, : active + 2]

        acc_mass = float(nxt[row == ACT_ACCEPT].sum())
        rej_mass = float(nxt[row == ACT_REJECT].sum())
        und_mass = float(nxt[row == ACT_UNDECIDED].sum())

        p_accept += acc_mass
        p_reject += rej_mass
        p_undecided += und_mass
        stop_pmf[tt] += acc_mass + rej_mass + und_mass

        cont = np.where(row == ACT_CONTINUE, nxt, 0.0)
        if prune > 0.0:
            cont[cont < prune] = 0.0

        active += 1
        q[: active + 1] = cont
        q[active + 1 :] = 0.0

        alive = float(cont.sum())
        if tt < n_max:
            survival_sum += alive
        if alive == 0.0:
            break

    total = p_accept + p_reject + p_undecided
    residual = abs(total - 1.0)

    # tau 的分位数：stop_pmf 的累积分布首次达到目标水平
    cdf = np.cumsum(stop_pmf)
    p50 = int(np.searchsorted(cdf, 0.50 * total, side="left"))
    p90 = int(np.searchsorted(cdf, 0.90 * total, side="left"))

    return OperatingPoint(
        p=float(p),
        asn=float(survival_sum),
        p50=p50,
        p90=p90,
        prob_accept=p_accept,
        prob_reject=p_reject,
        prob_undecided=p_undecided,
        mass_residual=residual,
    )


def first_accept_time_all_good(act: np.ndarray, n_max: int) -> int | None:
    """全良品路径 (k = 0) 首次可接收的样本量。

    用于与固定样本基准 U_{0.90}(22, 0) ≈ 0.0994 对照：
    time-uniform 方案更保守，该值应 **不早于** 22。
    """
    for t in range(1, n_max + 1):
        if act[t, 0] == ACT_ACCEPT:
            return t
    return None
