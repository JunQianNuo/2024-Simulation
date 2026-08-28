"""Q1 单元测试 / 性质测试。

覆盖阶段3算法设计报告 §4.7 的五项检查：
    1. 固定样本基准      U_0.90(22,0) ≈ 0.0994, L_0.95(2,2) ≈ 0.2236
    2. CS 交叉实现       两套独立实现端点差 <= 1e-8
    3. 概率守恒          接收 + 拒收 + 未决 = 1 ± 1e-10
    4. 硬约束            (Q1-C1) 与 (Q1-C2) 在全网格上成立
    5. 阈值附近长尾      高未决率允许存在，但必须能被检出并报告

运行：
    cd B题/代码 && python -m pytest q1/test_q1.py -v
"""

from __future__ import annotations

import numpy as np
import pytest

from .schemas import ACT_ACCEPT, ACT_CONTINUE, ACT_REJECT, ACT_UNDECIDED
from .bernoulli_cs import (
    clopper_pearson_lower,
    clopper_pearson_upper,
    cs_interval,
    log_mixture_at,
    log_mixture_triangle_at_p0,
    mixture_prior,
)
from .exact_path_dp import evaluate_at_p, first_accept_time_all_good
from .stopping_rule import apply_n_max, build_action_table, crosscheck_action_table

P0 = 0.10
ALPHA_R = 0.05
ALPHA_A = 0.10


# --------------------------------------------------------------------------
# 1. 固定样本基准
# --------------------------------------------------------------------------
def test_fixed_sample_baselines():
    assert clopper_pearson_upper(22, 0, 0.90) == pytest.approx(1 - 0.1 ** (1 / 22), abs=1e-12)
    assert clopper_pearson_lower(2, 2, 0.95) == pytest.approx(0.05 ** 0.5, abs=1e-12)
    assert clopper_pearson_upper(22, 0, 0.90) == pytest.approx(0.0994, abs=5e-4)
    assert clopper_pearson_lower(2, 2, 0.95) == pytest.approx(0.2236, abs=5e-4)


def test_fixed_sample_21_does_not_clear_threshold():
    """22 是"全良品下 90% 上界首次低于 10%"的最小固定样本量。"""
    assert clopper_pearson_upper(21, 0, 0.90) > P0
    assert clopper_pearson_upper(22, 0, 0.90) <= P0


# --------------------------------------------------------------------------
# 2. mixture 与端点反演
# --------------------------------------------------------------------------
def test_triangle_matches_pointwise():
    """向量化三角表与逐点求值一致（gammaln 外和展开无误）。"""
    a, b = mixture_prior(100, P0)
    tri = log_mixture_triangle_at_p0(60, P0, a, b)
    rng = np.random.default_rng(7)
    for _ in range(200):
        t = int(rng.integers(0, 61))
        k = int(rng.integers(0, t + 1))
        assert tri[t, k] == pytest.approx(log_mixture_at(t, k, P0, a, b), abs=1e-10)


def test_mixture_is_convex_in_p():
    """log M_t(p) 关于 p 严格凸 -> C_t 是区间，端点求根才稳定。"""
    a, b = mixture_prior(100, P0)
    ps = np.linspace(0.01, 0.99, 400)
    for t, k in [(50, 5), (200, 30), (17, 0), (17, 17)]:
        g = np.array([log_mixture_at(t, k, p, a, b) for p in ps])
        assert np.all(np.diff(g, n=2) > -1e-9)


def test_cs_interval_contains_mle_and_shrinks():
    a, b = mixture_prior(100, P0)
    prev_width = np.inf
    for t in (50, 200, 800, 3200):
        k = int(round(0.10 * t))
        L, U = cs_interval(t, k, ALPHA_A, a, b)
        assert L <= k / t <= U
        width = U - L
        assert width < prev_width
        prev_width = width


def test_action_table_crosscheck():
    """两套独立实现（p0 处凸性判据 vs brentq 端点反演）必须一致。"""
    act = build_action_table(400, P0, ALPHA_R, ALPHA_A, t_opt=100)
    ok, msgs = crosscheck_action_table(act, P0, ALPHA_R, ALPHA_A, 100, n_probe=300)
    assert ok, "CS_CROSSCHECK_FAILED: " + "; ".join(msgs[:5])


# --------------------------------------------------------------------------
# 3. 动作表结构
# --------------------------------------------------------------------------
def test_accept_and_reject_are_disjoint_and_monotone():
    act = build_action_table(300, P0, ALPHA_R, ALPHA_A, t_opt=50)
    for t in range(1, 301):
        row = act[t, : t + 1]
        assert not (np.any(row == ACT_ACCEPT) and np.any(row == ACT_REJECT) and
                    np.flatnonzero(row == ACT_ACCEPT).max() >=
                    np.flatnonzero(row == ACT_REJECT).min())
        # 次品越多越倾向拒收：接收区在左、拒收区在右，各自连续
        acc = np.flatnonzero(row == ACT_ACCEPT)
        rej = np.flatnonzero(row == ACT_REJECT)
        if acc.size:
            assert acc.max() - acc.min() == acc.size - 1
            assert acc.min() == 0
        if rej.size:
            assert rej.max() - rej.min() == rej.size - 1
            assert rej.max() == t


def test_undecided_only_on_last_row():
    act = apply_n_max(build_action_table(200, P0, ALPHA_R, ALPHA_A, t_opt=50), 200)
    for t in range(0, 200):
        assert not np.any(act[t, : t + 1] == ACT_UNDECIDED)
    assert np.any(act[200, :201] == ACT_UNDECIDED)


def test_time_uniform_is_more_conservative_than_fixed_22():
    """anytime-valid 保证要付代价：全良品接收时刻不应早于固定样本的 22 件。"""
    for t_opt in (25, 50, 100, 200, 400):
        act = apply_n_max(build_action_table(3200, P0, ALPHA_R, ALPHA_A, t_opt), 3200)
        first = first_accept_time_all_good(act, 3200)
        assert first is not None and first >= 22, f"t_opt={t_opt} 在 n={first} 就接收，早于固定样本基准"


# --------------------------------------------------------------------------
# 4. 硬约束 (Q1-C1) / (Q1-C2) —— 本文件最重要的测试
# --------------------------------------------------------------------------
@pytest.mark.parametrize("t_opt,n_max", [(25, 200), (50, 400), (100, 800), (200, 1600)])
def test_error_constraints_hold(t_opt, n_max):
    """(Q1-C1) sup_{p<=p0} P(拒收) <= 0.05；(Q1-C2) sup_{p>p0} P(接收) <= 0.10。

    在 p 的细网格上精确计算（非 MC），因此这是对约束的**数值验证**，
    而不是抽样估计。理论保证来自 Ville 不等式，这里是实现层面的确认。
    """
    act = apply_n_max(build_action_table(n_max, P0, ALPHA_R, ALPHA_A, t_opt), n_max)

    below = np.concatenate([np.linspace(0.001, 0.099, 25), [P0]])
    for p in below:
        pt = evaluate_at_p(act, float(p), n_max)
        assert pt.prob_reject <= ALPHA_R + 1e-9, (
            f"(Q1-C1) 违反：p={p:.4f} 拒收概率 {pt.prob_reject:.6f} > {ALPHA_R}"
        )

    above = np.linspace(0.1005, 0.60, 30)
    for p in above:
        pt = evaluate_at_p(act, float(p), n_max)
        assert pt.prob_accept <= ALPHA_A + 1e-9, (
            f"(Q1-C2) 违反：p={p:.4f} 接收概率 {pt.prob_accept:.6f} > {ALPHA_A}"
        )


# --------------------------------------------------------------------------
# 5. DP 正确性
# --------------------------------------------------------------------------
@pytest.mark.parametrize("p", [0.0, 0.01, 0.05, 0.10, 0.15, 0.30, 0.80, 1.0])
def test_probability_conservation(p):
    act = apply_n_max(build_action_table(400, P0, ALPHA_R, ALPHA_A, t_opt=100), 400)
    pt = evaluate_at_p(act, p, 400)
    assert pt.mass_residual < 1e-10, f"p={p} 概率守恒残差 {pt.mass_residual:.3e}"


def test_asn_bounded_by_n_max():
    act = apply_n_max(build_action_table(200, P0, ALPHA_R, ALPHA_A, t_opt=50), 200)
    for p in (0.02, 0.10, 0.25):
        pt = evaluate_at_p(act, p, 200)
        assert 1.0 <= pt.asn <= 200.0
        assert 1 <= pt.p50 <= pt.p90 <= 200


def test_dp_against_brute_force_enumeration():
    """小 N_max 下，用逐条路径穷举核对 DP 的三个终止概率与 ASN。"""
    n_max = 12
    act = apply_n_max(build_action_table(n_max, P0, ALPHA_R, ALPHA_A, t_opt=25), n_max)
    p = 0.23

    acc = rej = und = 0.0
    esum = 0.0
    for mask in range(1 << n_max):
        # 逐件生成一条完整路径，遇到停止即结算
        prob = 1.0
        k = 0
        for t in range(1, n_max + 1):
            bit = (mask >> (t - 1)) & 1
            prob *= p if bit else (1 - p)
            k += bit
            a = act[t, k]
            if a != ACT_CONTINUE:
                # 该路径在 t 停止；后续 bit 无意义，只统计一次
                if mask >> t:  # 后缀非零则这条路径已被 mask 的前缀代表过
                    prob = 0.0
                break
        else:
            a = ACT_CONTINUE
        if prob == 0.0:
            continue
        esum += prob * t
        if a == ACT_ACCEPT:
            acc += prob
        elif a == ACT_REJECT:
            rej += prob
        else:
            und += prob

    pt = evaluate_at_p(act, p, n_max)
    assert acc == pytest.approx(pt.prob_accept, abs=1e-12)
    assert rej == pytest.approx(pt.prob_reject, abs=1e-12)
    assert und == pytest.approx(pt.prob_undecided, abs=1e-12)
    assert esum == pytest.approx(pt.asn, abs=1e-12)


def test_extreme_p_behaviour():
    act = apply_n_max(build_action_table(400, P0, ALPHA_R, ALPHA_A, t_opt=50), 400)
    good = evaluate_at_p(act, 0.0, 400)
    bad = evaluate_at_p(act, 1.0, 400)
    assert good.prob_accept == pytest.approx(1.0, abs=1e-12)
    assert bad.prob_reject == pytest.approx(1.0, abs=1e-12)
    assert bad.asn < good.asn  # 全次品比全良品更快越界
