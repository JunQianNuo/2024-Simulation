"""Q1-M5 的求解：候选网格上的 Pareto 前沿与拐点选择。

依据：阶段2报告 (Q1-O1)(Q1-O2)(Q1-OPT)；阶段3报告 §4.5。

    ASN_w(eta, N_max) = sum_k w_k E_{p_k}[tau]        (Q1-O1)
    U_w(eta, N_max)   = sum_k w_k P_{p_k}(delta = U)  (Q1-O2)

    min (ASN_w, U_w)  s.t. (Q1-C1), (Q1-C2), tau <= N_max

两个目标都是"越小越好"。约束 (Q1-C1)(Q1-C2) 由置信序列构造性满足，
所以网格里的每个候选都是可行解，搜索只需在可行域内比较两个目标。

"精确 Pareto"的口径（必须写进论文，不能夸大）：
    只指**预先声明的有限候选网格内**无随机评价误差，
    不宣称对连续 t_opt 或所有可能停止规则全局最优。
"""

from __future__ import annotations

import numpy as np

from .schemas import CandidateResult

__all__ = ["aggregate_objectives", "pareto_front", "select_knee", "recommend_three"]


def aggregate_objectives(
    result: CandidateResult,
    p_grid: list[float],
    weight_schemes: dict[str, list[float] | None],
) -> None:
    """按各权重方案计算 (ASN_w, U_w)，就地写回 result。"""
    asn = np.array([result.point_at(p).asn for p in p_grid])
    und = np.array([result.point_at(p).prob_undecided for p in p_grid])

    for name, w in weight_schemes.items():
        if w is None:
            weights = np.full(len(p_grid), 1.0 / len(p_grid))
        else:
            weights = np.asarray(w, dtype=float)
            if weights.size != len(p_grid):
                raise ValueError(f"权重方案 {name} 长度与代表性 p 集合不符")
            weights = weights / weights.sum()
        result.asn_weighted[name] = float(asn @ weights)
        result.undecided_weighted[name] = float(und @ weights)


def pareto_front(
    results: list[CandidateResult],
    scheme: str = "equal",
) -> list[CandidateResult]:
    """返回非支配候选，按 ASN_w 升序。

    支配定义：a 支配 b <=> a 的两个目标都不劣于 b，且至少一个严格更优。
    """
    pts = [(r.asn_weighted[scheme], r.undecided_weighted[scheme]) for r in results]
    keep: list[CandidateResult] = []
    for i, (a_i, u_i) in enumerate(pts):
        dominated = False
        for j, (a_j, u_j) in enumerate(pts):
            if i == j:
                continue
            if (a_j <= a_i and u_j <= u_i) and (a_j < a_i or u_j < u_i):
                dominated = True
                break
        if not dominated:
            keep.append(results[i])
    keep.sort(key=lambda r: r.asn_weighted[scheme])
    return keep


def _normalize(front: list[CandidateResult], scheme: str) -> np.ndarray:
    a = np.array([r.asn_weighted[scheme] for r in front], dtype=float)
    u = np.array([r.undecided_weighted[scheme] for r in front], dtype=float)
    span_a = a.max() - a.min()
    span_u = u.max() - u.min()
    an = (a - a.min()) / span_a if span_a > 0 else np.zeros_like(a)
    un = (u - u.min()) / span_u if span_u > 0 else np.zeros_like(u)
    return np.column_stack([an, un])


def select_knee(front: list[CandidateResult], scheme: str = "equal") -> dict[str, object]:
    """两个独立准则选拐点，一致才推荐唯一方案。

    准则 1：到理想点 (0, 0) 的最小归一化距离。
    准则 2：最大曲率（离散二阶差分的模），即前沿弯折最剧烈处。

    阶段3报告 §4.5 明确要求：两准则不一致时**不强行给唯一解**，
    而是报告"省样本型 / 均衡型 / 低未决型"三个方案供论文比较。
    """
    if len(front) == 1:
        return {"agree": True, "ideal_idx": 0, "curvature_idx": 0, "knee_idx": 0}

    xy = _normalize(front, scheme)
    dist = np.linalg.norm(xy, axis=1)
    ideal_idx = int(np.argmin(dist))

    if len(front) >= 3:
        d2 = np.diff(xy, n=2, axis=0)
        curvature = np.linalg.norm(d2, axis=1)
        curvature_idx = int(np.argmax(curvature)) + 1
    else:
        curvature_idx = ideal_idx

    agree = ideal_idx == curvature_idx
    return {
        "agree": agree,
        "ideal_idx": ideal_idx,
        "curvature_idx": curvature_idx,
        "knee_idx": ideal_idx if agree else ideal_idx,
    }


def recommend_three(front: list[CandidateResult], scheme: str = "equal") -> dict[str, CandidateResult]:
    """省样本型 / 均衡型 / 低未决型三个 Pareto 方案。"""
    knee = select_knee(front, scheme)
    return {
        "省样本型": front[0],                       # ASN_w 最小
        "均衡型": front[int(knee["knee_idx"])],     # 拐点
        "低未决型": front[-1],                      # U_w 最小
    }
