"""Q1-A1 停止规则：由双单侧置信序列生成 (t, K_t) 动作表。

依据：阶段2报告 (Q1-ALG)、(Q1-T)；阶段3报告 §4.2。

    a(t, K_t) = R,  若 L_t^R > p0            (95% 信度认定超标 -> 拒收)
                A,  若 U_t^A <= p0           (90% 信度认定不超标 -> 接收)
                U,  若 t = N_max 且未越界    (工程截尾，未决)
                C,  其他                     (继续抽样)

    tau = min{ inf{t : 越界}, N_max }

两条错误预算相互独立：
    L_t^R 来自 alpha_R = 0.05 的置信序列  ->  满足 (Q1-C1)
    U_t^A 来自 alpha_A = 0.10 的置信序列  ->  满足 (Q1-C2)

覆盖论证（这是"信度"二字的落点，写论文时要写进去）：
    真实 p <= p0 时，拒收只可能发生在某个 t 使 L_t^R > p >= ... 的事件上，
    即 p 落在 C_t(0.05) 之外，由 Ville 不等式该事件概率 <= 0.05。
    真实 p >  p0 时同理，接收概率 <= 0.10。
    注意保证是**对整条路径**成立的，不是逐个时点成立，所以允许随时停止。
"""

from __future__ import annotations

import numpy as np

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.schemas import ACT_ACCEPT, ACT_CONTINUE, ACT_REJECT, ACT_UNDECIDED, Status
from q1.bernoulli_cs import cs_interval, log_mixture_triangle_at_p0, mixture_prior

__all__ = ["build_action_table", "apply_n_max", "crosscheck_action_table", "boundary_table"]


def build_action_table(
    n_max: int,
    p0: float,
    alpha_R: float,
    alpha_A: float,
    t_opt: int,
    t_opt_R: int | None = None,
    t_opt_A: int | None = None,
) -> np.ndarray:
    """构造动作表 act[t, k]，t = 0..n_max，k = 0..t，取值见 common.schemas 的 ACT_*。

    此处**不**写入 ACT_UNDECIDED；截尾由 apply_n_max 施加，
    这样同一张表可以被不同 N_max 的候选复用（表只依赖 t_opt）。

    实现要点：判定不需要求根。log M_t(p) 关于 p 严格凸、极小点 p_hat = k/t，故
        p0 <  L_t(alpha) <=> logM_t(p0) >= log(1/alpha) 且 p_hat >  p0
        U_t(alpha) <= p0 <=> logM_t(p0) >= log(1/alpha) 且 p_hat <= p0
    只在 p0 一点求值即可，整个三角表由 gammaln 外和一次算出。
    """
    tR = t_opt if t_opt_R is None else t_opt_R
    tA = t_opt if t_opt_A is None else t_opt_A

    aR, bR = mixture_prior(tR, p0)
    logM_R = log_mixture_triangle_at_p0(n_max, p0, aR, bR)
    if tA == tR:
        logM_A = logM_R
    else:
        aA, bA = mixture_prior(tA, p0)
        logM_A = log_mixture_triangle_at_p0(n_max, p0, aA, bA)

    thr_R = np.log(1.0 / alpha_R)
    thr_A = np.log(1.0 / alpha_A)

    act = np.full((n_max + 1, n_max + 1), 255, dtype=np.uint8)  # 255 = 非法/未填
    act[0, 0] = ACT_CONTINUE  # t=0 无观测，必然继续

    t_idx = np.arange(n_max + 1)
    for t in range(1, n_max + 1):
        k = t_idx[: t + 1]
        p_hat = k / t
        crossed_R = logM_R[t, : t + 1] >= thr_R
        crossed_A = logM_A[t, : t + 1] >= thr_A

        reject = crossed_R & (p_hat > p0)
        accept = crossed_A & (p_hat <= p0)

        # R 与 A 不可能同时成立：两个区间都包含 p_hat，故 L <= p_hat <= U，
        # 而 reject 要求 p0 < L，accept 要求 U <= p0，矛盾。断言之。
        if np.any(reject & accept):
            bad = int(np.argmax(reject & accept))
            raise AssertionError(
                f"{Status.INVALID_DATA}: (t={t}, k={bad}) 同时触发接收与拒收，"
                "说明置信序列实现有误"
            )

        row = np.full(t + 1, ACT_CONTINUE, dtype=np.uint8)
        row[accept] = ACT_ACCEPT
        row[reject] = ACT_REJECT
        act[t, : t + 1] = row

    return act


def apply_n_max(act: np.ndarray, n_max: int) -> np.ndarray:
    """截断到 N_max 并把末行仍为 C 的状态标记为 U（工程截尾，未决）。"""
    sub = act[: n_max + 1, : n_max + 1].copy()
    last = sub[n_max, : n_max + 1]
    last[last == ACT_CONTINUE] = ACT_UNDECIDED
    sub[n_max, : n_max + 1] = last
    return sub


def crosscheck_action_table(
    act: np.ndarray,
    p0: float,
    alpha_R: float,
    alpha_A: float,
    t_opt: int,
    n_probe: int = 400,
    tol: float = 1e-8,
    seed: int = 20240905,
) -> tuple[bool, list[str]]:
    """第二套独立实现的交叉核验（阶段3报告 §4.2 强制要求）。

    第一套：在 p0 处直接求值 + 凸性判据（build_action_table 用的）。
    第二套：brentq 反演出端点 (L_t, U_t)，再按 L_t > p0 / U_t <= p0 判定。
    两者若在任一抽查状态上给出不同动作，或端点与阈值的差异超过 tol，
    返回 CS_CROSSCHECK_FAILED 所需的失败信息。
    """
    rng = np.random.default_rng(seed)
    a, b = mixture_prior(t_opt, p0)
    n_max = act.shape[0] - 1
    msgs: list[str] = []

    # 抽查：覆盖小 t 全部状态 + 大 t 随机状态
    probes: list[tuple[int, int]] = []
    for t in range(1, min(25, n_max) + 1):
        probes.extend((t, k) for k in range(t + 1))
    if n_max > 25:
        for _ in range(n_probe):
            t = int(rng.integers(26, n_max + 1))
            k = int(rng.integers(0, t + 1))
            probes.append((t, k))

    for t, k in probes:
        LR, _ = cs_interval(t, k, alpha_R, a, b)
        _, UA = cs_interval(t, k, alpha_A, a, b)
        if not np.isfinite(LR) or not np.isfinite(UA):
            msgs.append(f"(t={t},k={k}) 端点反演返回 NaN")
            continue

        expect = ACT_CONTINUE
        if LR > p0:
            expect = ACT_REJECT
        elif UA <= p0:
            expect = ACT_ACCEPT

        got = int(act[t, k])
        if got == ACT_UNDECIDED:
            got = ACT_CONTINUE  # 截尾不参与本项核验
        if got != expect:
            gap = min(abs(LR - p0), abs(UA - p0))
            if gap > tol:
                msgs.append(
                    f"(t={t},k={k}) 动作不一致：直接判据={got} 端点判据={expect} "
                    f"L_R={LR:.12f} U_A={UA:.12f}"
                )

    return (len(msgs) == 0), msgs


def boundary_table(act: np.ndarray) -> list[dict[str, object]]:
    """把动作表压成论文可读的边界表。

    动作在 k 上单调（次品越多越倾向拒收），故每个 t 只需两个阈值：
        k_reject_min : 触发拒收的最小次品数，None 表示该 t 不可能拒收
        k_accept_max : 允许接收的最大次品数，None 表示该 t 不可能接收
    """
    n_max = act.shape[0] - 1
    rows: list[dict[str, object]] = []
    for t in range(1, n_max + 1):
        row = act[t, : t + 1]
        rej = np.flatnonzero(row == ACT_REJECT)
        acc = np.flatnonzero(row == ACT_ACCEPT)
        rows.append(
            {
                "n": t,
                "k_reject_min": int(rej[0]) if rej.size else None,
                "k_accept_max": int(acc[-1]) if acc.size else None,
            }
        )
    return rows
