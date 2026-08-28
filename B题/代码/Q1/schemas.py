"""Q1 的输入/输出契约与状态码。

依据：B题阶段3算法设计报告 §2.1、§2.2、§13。
状态码遵循"失败关闭"原则：非法或未认证的结果不得被当作普通有限结果使用。
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


# --------------------------------------------------------------------------
# 状态码（阶段3报告 §13，仅保留 Q1 相关项）
# --------------------------------------------------------------------------
class Status(str, Enum):
    SUCCESS_EXACT = "SUCCESS_EXACT"                # 确定性全搜索与数值检查通过
    UNDECIDED_CAP = "UNDECIDED_CAP"                # 到 N_max 未越界，作为模型输出
    CS_CROSSCHECK_FAILED = "CS_CROSSCHECK_FAILED"  # 两套独立实现端点差超容差
    PROB_CONSERVATION_FAILED = "PROB_CONSERVATION_FAILED"
    INVALID_DATA = "INVALID_DATA"


# 动作编码。DP 与动作表共用，uint8 存储。
ACT_CONTINUE = 0
ACT_ACCEPT = 1
ACT_REJECT = 2
ACT_UNDECIDED = 3

ACT_NAME = {
    ACT_CONTINUE: "C",
    ACT_ACCEPT: "A",
    ACT_REJECT: "R",
    ACT_UNDECIDED: "U",
}


@dataclass(frozen=True)
class Q1Problem:
    """Q1 题面参数。p0=0.10、95% 拒收信度、90% 接收信度。"""

    p0: float = 0.10
    alpha_R: float = 0.05
    alpha_A: float = 0.10

    def validate(self) -> None:
        if not 0.0 < self.p0 < 1.0:
            raise ValueError(f"{Status.INVALID_DATA}: p0 必须在 (0,1)，收到 {self.p0}")
        for name, a in (("alpha_R", self.alpha_R), ("alpha_A", self.alpha_A)):
            if not 0.0 < a < 1.0:
                raise ValueError(f"{Status.INVALID_DATA}: {name} 必须在 (0,1)，收到 {a}")


@dataclass(frozen=True)
class Candidate:
    """一个候选停止规则 = (调节时间尺度, 最大抽样量)。

    t_opt 控制 mixture 边界最紧的时间尺度；对应 intrinsic time
    v_opt = p0 * (1 - p0) * t_opt（阶段3报告 §4.3）。
    """

    t_opt: int
    n_max: int

    def __post_init__(self) -> None:
        if self.n_max < self.t_opt:
            raise ValueError(
                f"{Status.INVALID_DATA}: 要求 n_max >= t_opt，收到 ({self.t_opt}, {self.n_max})"
            )

    @property
    def label(self) -> str:
        return f"t_opt={self.t_opt},N_max={self.n_max}"


@dataclass
class OperatingPoint:
    """单个真实 p 下，某候选规则的精确性能。全部由路径 DP 得到，无 MC 误差。"""

    p: float
    asn: float                # E_p[tau]
    p50: int                  # tau 的中位数
    p90: int                  # tau 的 90 分位
    prob_accept: float
    prob_reject: float
    prob_undecided: float
    mass_residual: float      # |P_A + P_R + P_U - 1|

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CandidateResult:
    """一个候选规则在全部代表性 p 上的评价结果 + 加权聚合目标。"""

    candidate: Candidate
    points: list[OperatingPoint]
    asn_weighted: dict[str, float] = field(default_factory=dict)
    undecided_weighted: dict[str, float] = field(default_factory=dict)
    status: Status = Status.SUCCESS_EXACT
    warnings: list[str] = field(default_factory=list)
    runtime_ms: float = 0.0
    # 关键工程量：全良品路径首次可接收的样本量（用于与固定样本 22 件对照）
    first_accept_t_all_good: int | None = None

    def point_at(self, p: float, tol: float = 1e-12) -> OperatingPoint:
        for pt in self.points:
            if abs(pt.p - p) < tol:
                return pt
        raise KeyError(f"代表性集合中没有 p={p}")
