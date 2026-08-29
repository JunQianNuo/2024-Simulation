"""Generate publication-candidate Q1 figures from saved result artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "cumcm-q1-publication-figures-v1"
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import fontManager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results" / "q1"
FIGURES = RESULTS / "figures"
DPI = 360

COLORS = {
    "primary": "#1A6FC4",
    "orange": "#E28E2C",
    "purple": "#7B5FD6",
    "teal": "#258B82",
    "baseline": "#767676",
    "candidate": "#B8BDC3",
    "grid": "#D8D8D8",
    "text": "#111111",
    "accept_fill": "#C9DCF0",
    "continue_fill": "#ECECEC",
    "reject_fill": "#F5D9A0",
}

RECOMMENDATION_STYLES = {
    "sample_saving": {"label": "省样本方案", "color": COLORS["primary"], "marker": "o", "linestyle": "-"},
    "balanced": {"label": "平衡参考", "color": COLORS["orange"], "marker": "s", "linestyle": "--"},
    "low_undecided": {"label": "低未决方案", "color": COLORS["purple"], "marker": "^", "linestyle": "-."},
}


def _available_font(preferred: list[str]) -> str:
    available = {font.name for font in fontManager.ttflist}
    for name in preferred:
        if name in available:
            return name
    raise RuntimeError(f"No usable font found in {preferred}")


CHINESE_FONT = _available_font(["Noto Serif CJK SC", "Noto Serif CJK JP", "DejaVu Serif"])
LATIN_FONT = _available_font(["Times New Roman", "Liberation Serif", "DejaVu Serif"])

plt.rcParams.update({
    "font.family": CHINESE_FONT,
    "mathtext.fontset": "stix",
    "axes.unicode_minus": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": COLORS["text"],
    "axes.labelcolor": COLORS["text"],
    "text.color": COLORS["text"],
    "xtick.color": COLORS["text"],
    "ytick.color": COLORS["text"],
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5,
    "legend.fontsize": 8,
    "lines.linewidth": 1.8,
    "axes.linewidth": 0.9,
    "svg.fonttype": "none",
})


def read_json(name: str):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(row: dict[str, str], key: str) -> float:
    return float(row[key])


def integer(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def optional_number(row: dict[str, str], key: str) -> float:
    value = row[key].strip()
    return float(value) if value else np.nan


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evidence() -> dict:
    evidence = {
        "config": json.loads((HERE / "config.json").read_text(encoding="utf-8")),
        "summary": read_json("summary.json"),
        "writer": read_json("code_to_writer.json"),
        "candidates": read_csv("candidate_objectives.csv"),
        "pareto": read_csv("pareto_front.csv"),
        "boundary": read_csv("decision_boundary.csv"),
        "oc": read_csv("operating_characteristics.csv"),
        "recommendations": read_csv("recommendations.csv"),
        "sensitivity": read_csv("sensitivity_recommendations.csv"),
        "baseline": read_csv("baseline_comparison.csv"),
    }
    validate_evidence(evidence)
    return evidence


def validate_evidence(evidence: dict) -> None:
    summary, writer = evidence["summary"], evidence["writer"]
    if summary["status"] != "SUCCESS_EXACT" or len(evidence["candidates"]) != summary["candidate_count"]:
        raise RuntimeError("Q1 summary or candidate set is not validated")
    if summary["candidate_count"] != 34 or len(evidence["pareto"]) != summary["pareto_sizes"]["equal"]:
        raise RuntimeError("Q1 finite-grid/Pareto evidence is inconsistent")

    recommendations = {row["type"]: row for row in evidence["recommendations"]}
    if set(recommendations) != set(RECOMMENDATION_STYLES):
        raise RuntimeError("Q1 recommendation types are incomplete")
    for name, row in recommendations.items():
        expected = summary["recommendations"][name]
        if (integer(row, "t_opt"), integer(row, "N_max")) != (expected["t_opt"], expected["N_max"]):
            raise RuntimeError(f"summary/recommendations mismatch for {name}")
    balanced = recommendations["balanced"]
    writer_balanced = writer["balanced_reference"]
    if (integer(balanced, "t_opt"), integer(balanced, "N_max")) != (
        writer_balanced["t_opt"], writer_balanced["N_max"]
    ):
        raise RuntimeError("balanced reference differs across evidence files")

    key = (integer(balanced, "t_opt"), integer(balanced, "N_max"))
    selected_oc = [row for row in evidence["oc"] if (integer(row, "t_opt"), integer(row, "N_max")) == key]
    p_grid = evidence["config"]["p_grid"]
    if len(selected_oc) != len(p_grid) or sorted(number(row, "p") for row in selected_oc) != p_grid:
        raise RuntimeError("balanced operating-characteristic grid is incomplete")
    if len(evidence["boundary"]) != key[1] or [integer(row, "n") for row in evidence["boundary"]] != list(range(1, key[1] + 1)):
        raise RuntimeError("balanced decision boundary is incomplete")
    for row in selected_oc:
        total = sum(number(row, field) for field in ("P_accept", "P_reject", "P_undecided"))
        if abs(total - 1.0) > evidence["config"]["tolerances"]["mass"]:
            raise RuntimeError("operating-characteristic probabilities do not sum to one")
    if len(evidence["baseline"]) != 1 or evidence["baseline"][0]["role"] != "external_baseline_not_in_pareto_grid":
        raise RuntimeError("external baseline role is missing or ambiguous")
    evidence["recommendation_map"] = recommendations
    evidence["balanced_oc"] = sorted(selected_oc, key=lambda row: number(row, "p"))


def style_axis(ax, grid_axis="both") -> None:
    ax.grid(True, axis=grid_axis, color=COLORS["grid"], linewidth=0.65, alpha=0.75)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        label.set_fontfamily(LATIN_FONT)
        label.set_fontweight("normal")


def save_figure(fig, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    svg, png = stem.with_suffix(".svg"), stem.with_suffix(".png")
    fig.savefig(svg, bbox_inches="tight", metadata={"Date": None})
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    fig.savefig(png, dpi=DPI, bbox_inches="tight", facecolor="white", metadata={"Software": "Q1 plot_q1.py"})
    plt.close(fig)


def plot_decision_regions(evidence: dict) -> None:
    boundary = evidence["boundary"]
    balanced = evidence["recommendation_map"]["balanced"]
    n = np.array([integer(row, "n") for row in boundary], dtype=float)
    accept = np.array([optional_number(row, "k_accept_max") for row in boundary])
    reject = np.array([optional_number(row, "k_reject_min") for row in boundary])
    max_reject = int(np.nanmax(reject))
    y_top = min(int(n[-1]), int(np.ceil((max_reject * 1.12) / 10.0) * 10))
    feasible_top = np.minimum(n, y_top)
    accept_edge = accept + 0.5
    reject_edge = reject - 0.5
    continue_low = np.where(np.isfinite(accept_edge), accept_edge, 0.0)
    continue_high = np.where(np.isfinite(reject_edge), reject_edge, feasible_top)

    fig, ax = plt.subplots(figsize=(7.2, 4.7), constrained_layout=True)
    ax.fill_between(n, 0, np.minimum(accept_edge, feasible_top), where=np.isfinite(accept_edge),
                    step="post", color=COLORS["accept_fill"], alpha=0.95)
    ax.fill_between(n, continue_low, np.minimum(continue_high, feasible_top),
                    where=continue_high >= continue_low, step="post",
                    color=COLORS["continue_fill"], alpha=0.95)
    ax.fill_between(n, reject_edge, feasible_top,
                    where=np.isfinite(reject_edge) & (reject_edge <= feasible_top), step="post",
                    color=COLORS["reject_fill"], alpha=0.95)
    ax.plot(n, accept, color=COLORS["primary"], label="接收上界 $k_{A}(n)$")
    ax.plot(n, reject, color=COLORS["orange"], linestyle="--", label="拒收下界 $k_{R}(n)$")
    ax.plot(np.arange(1, y_top + 1), np.arange(1, y_top + 1), color=COLORS["baseline"],
            linestyle=":", linewidth=1.0, alpha=0.8)
    n_max = integer(balanced, "N_max")
    final_accept, final_reject = accept[-1], reject[-1]
    mid = (final_accept + final_reject) / 2
    ax.annotate(
        f"$N_{{max}}={n_max}$ 时仍在继续区\n$\\Rightarrow$ UNDECIDED_CAP（证据不足）",
        xy=(n_max, mid), xytext=(0.59, 0.70), textcoords="axes fraction",
        arrowprops={"arrowstyle": "->", "color": COLORS["baseline"], "linewidth": 1.0},
        fontsize=8.5, ha="left", va="center",
    )
    handles = [
        Patch(facecolor=COLORS["accept_fill"], edgecolor=COLORS["primary"], label="接收区"),
        Patch(facecolor=COLORS["continue_fill"], edgecolor=COLORS["baseline"], label="继续抽检区"),
        Patch(facecolor=COLORS["reject_fill"], edgecolor=COLORS["orange"], label="拒收区"),
        Line2D([], [], color=COLORS["primary"], label="接收上界"),
        Line2D([], [], color=COLORS["orange"], linestyle="--", label="拒收下界"),
    ]
    ax.legend(handles=handles, ncol=2, loc="upper left", frameon=True, framealpha=0.95)
    ax.set(xlim=(1, n_max), ylim=(0, y_top), xlabel="累计抽检数 $n$（件）", ylabel="累计次品数 $k$（件）",
           title=f"平衡参考方案的序贯决策区域  ($t_{{opt}}={integer(balanced, 't_opt')}$, $N_{{max}}={n_max}$)")
    ax.text(0.995, 0.015, f"为突出边界，纵轴显示至 $k={y_top}$；更高次品数均已进入拒收区。",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.3, color=COLORS["baseline"])
    style_axis(ax)
    save_figure(fig, FIGURES / "q1_decision_regions_balanced")


def plot_operating_characteristics(evidence: dict) -> None:
    rows = evidence["balanced_oc"]
    p = np.array([number(row, "p") for row in rows])
    p0 = float(evidence["config"]["problem"]["p0"])
    alpha_accept = float(evidence["config"]["problem"]["alpha_accept"])
    alpha_reject = float(evidence["config"]["problem"]["alpha_reject"])
    at_p0 = next(row for row in rows if number(row, "p") == p0)
    specs = [
        ("P_accept", "(a) 接收概率", COLORS["primary"], "o", "-"),
        ("P_reject", "(b) 拒收概率", COLORS["orange"], "s", "--"),
        ("P_undecided", "(c) 截尾未决概率", COLORS["purple"], "^", "-."),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 7.2), sharex=True, constrained_layout=True)
    for ax, (field, title, color, marker, linestyle) in zip(axes, specs):
        y = np.array([number(row, field) for row in rows])
        ax.plot(p, y, color=color, marker=marker, linestyle=linestyle, markersize=4.6)
        ax.axvline(p0, color=COLORS["baseline"], linestyle=":", linewidth=1.2)
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("概率")
        ax.set_title(title, loc="left", fontsize=9.5)
        style_axis(ax)
    axes[0].hlines(alpha_accept, p0, p.max(), color=COLORS["baseline"], linestyle="--", linewidth=1.0)
    axes[0].annotate(
        f"$p_0$ 右极限={number(at_p0, 'P_accept'):.3f} $\\leq {alpha_accept:.2f}$",
        xy=(p0, number(at_p0, "P_accept")), xytext=(0.125, 0.28),
        arrowprops={"arrowstyle": "->", "color": COLORS["baseline"]}, fontsize=8,
    )
    axes[1].hlines(alpha_reject, p.min(), p0, color=COLORS["baseline"], linestyle="--", linewidth=1.0)
    axes[1].annotate(
        f"$p=p_0$ 时={number(at_p0, 'P_reject'):.3f} $\\leq {alpha_reject:.2f}$",
        xy=(p0, number(at_p0, "P_reject")), xytext=(0.135, 0.20),
        arrowprops={"arrowstyle": "->", "color": COLORS["baseline"]}, fontsize=8,
    )
    axes[-1].set_xlabel("真实次品率 $p$")
    axes[-1].set_xticks([0.01, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.30])
    axes[-1].tick_params(axis="x", rotation=0)
    balanced = evidence["recommendation_map"]["balanced"]
    fig.suptitle(
        f"平衡参考方案的操作特性  ($t_{{opt}}={integer(balanced, 't_opt')}$, $N_{{max}}={integer(balanced, 'N_max')}$)",
        fontsize=11,
    )
    save_figure(fig, FIGURES / "q1_operating_characteristics_balanced")


def plot_recommendation_tradeoffs(evidence: dict) -> None:
    oc = evidence["oc"]
    p0 = float(evidence["config"]["problem"]["p0"])
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.65), constrained_layout=True)
    for name, style in RECOMMENDATION_STYLES.items():
        rec = evidence["recommendation_map"][name]
        key = (integer(rec, "t_opt"), integer(rec, "N_max"))
        rows = sorted(
            [row for row in oc if (integer(row, "t_opt"), integer(row, "N_max")) == key],
            key=lambda row: number(row, "p"),
        )
        p = [number(row, "p") for row in rows]
        label = f"{style['label']} ({key[0]}, {key[1]})"
        axes[0].plot(p, [number(row, "ASN") for row in rows], label=label,
                     color=style["color"], marker=style["marker"], linestyle=style["linestyle"], markersize=4.2)
        axes[1].plot(p, [number(row, "P_undecided") for row in rows], label=label,
                     color=style["color"], marker=style["marker"], linestyle=style["linestyle"], markersize=4.2)
    for ax in axes:
        ax.axvline(p0, color=COLORS["baseline"], linestyle=":", linewidth=1.2)
        ax.text(p0, 0.985, f"$p_0={p0:.2f}$", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=7.7, color=COLORS["baseline"])
        ax.set_xlabel("真实次品率 $p$")
        style_axis(ax)
    axes[0].set(title="(a) 平均抽检量", ylabel="平均抽检数 ASN（件）", ylim=(0, None))
    axes[1].set(title="(b) 截尾未决风险", ylabel="未决概率", ylim=(0, 1))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.055), ncol=3, frameon=False)
    fig.suptitle("三种偏好方案的效率—未决权衡", y=1.13, fontsize=11)
    save_figure(fig, FIGURES / "q1_recommendation_tradeoffs")


def plot_pareto_front(evidence: dict) -> None:
    candidates, front = evidence["candidates"], evidence["pareto"]
    x_key, y_key = "ASN_w[equal]", "U_w[equal]"
    fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)
    ax.scatter([number(row, x_key) for row in candidates], [number(row, y_key) for row in candidates],
               s=30, color=COLORS["candidate"], edgecolors="white", linewidths=0.45,
               label=f"{len(candidates)} 个有限候选", zorder=2)
    ax.plot([number(row, x_key) for row in front], [number(row, y_key) for row in front],
            color=COLORS["primary"], marker="o", markersize=3.8, label="等权 Pareto 前沿", zorder=3)
    offsets = {"sample_saving": (12, -24), "balanced": (12, -24), "low_undecided": (-116, 12)}
    for name, style in RECOMMENDATION_STYLES.items():
        row = evidence["recommendation_map"][name]
        x, y = number(row, x_key), number(row, y_key)
        ax.scatter(x, y, s=82, color=style["color"], marker=style["marker"],
                   edgecolors="white", linewidths=0.8, zorder=5, label=style["label"])
        ax.annotate(f"{style['label']}\n({integer(row, 't_opt')}, {integer(row, 'N_max')})", (x, y),
                    textcoords="offset points", xytext=offsets[name], fontsize=7.7,
                    arrowprops={"arrowstyle": "-", "color": style["color"], "linewidth": 0.8})
    baseline = evidence["baseline"][0]
    bx, by = number(baseline, x_key), number(baseline, y_key)
    ax.scatter(bx, by, s=88, marker="D", facecolors="white", edgecolors=COLORS["baseline"],
               linewidths=1.6, zorder=5, label="外部五阶段基线（非候选网格）")
    ax.annotate("外部基线\n不连入前沿", (bx, by), textcoords="offset points", xytext=(12, 10),
                fontsize=7.7, color=COLORS["baseline"])
    max_x = max([number(row, x_key) for row in candidates] + [bx])
    max_y = max([number(row, y_key) for row in candidates] + [by])
    ax.set(xlim=(0, max_x * 1.12), ylim=(0, max_y * 1.08),
           xlabel="等权平均抽检数 ASN（件）", ylabel="等权平均未决概率",
           title=f"{len(candidates)} 个有限候选的 ASN—未决率 Pareto 前沿")
    ax.legend(loc="upper right", ncol=2, frameon=True, framealpha=0.95)
    style_axis(ax)
    save_figure(fig, RESULTS / "pareto_front")


def figure_entries(evidence: dict, render_check: str) -> list[dict]:
    candidate_count = len(evidence["candidates"])
    grid_count = len(evidence["balanced_oc"])
    sensitivity_count = len(evidence["sensitivity"])
    return [
        {
            "file": "figures/q1_decision_regions_balanced.svg",
            "raster_file": "figures/q1_decision_regions_balanced.png",
            "title": "平衡参考方案的序贯决策区域",
            "type": "Type 3",
            "purpose": "展示接收、继续抽检和拒收三个动作区域及其边界。",
            "source": ["decision_boundary.csv", "recommendations.csv", "summary.json"],
            "claim_scope": "仅适用于当前 balanced reference；UNDECIDED_CAP 是证据不足，不是第四种质量判定。",
            "paper_candidate": "正文（方法/策略说明）",
            "render_check": render_check,
            "caption_zh": "图示平衡参考方案在累计抽检数与累计次品数平面上的序贯决策区域。接收上界与拒收下界之间需继续抽检；到达 N_max 仍未越界时记为 UNDECIDED_CAP，表示证据不足而非合格或不合格。",
        },
        {
            "file": "figures/q1_operating_characteristics_balanced.svg",
            "raster_file": "figures/q1_operating_characteristics_balanced.png",
            "title": "平衡参考方案的操作特性",
            "type": "Type 3",
            "purpose": "展示真实次品率改变时接收、拒收和未决概率的变化。",
            "source": ["operating_characteristics.csv", "recommendations.csv", "config.json"],
            "claim_scope": "仅连接 13 个已计算网格点以引导视线，不表示额外插值计算；接收错误约束指 p0 右极限。",
            "paper_candidate": "正文（操作特性/风险说明）",
            "render_check": render_check,
            "caption_zh": f"图示平衡参考方案在 {grid_count} 个已计算真实次品率上的接收、拒收和截尾未决概率。标称阈值附近的未决概率较高，反映了双单侧置信序列在边界附近需要更多证据；图中同时区分了 p=p0 的拒收风险与 p0 右极限的接收风险。",
        },
        {
            "file": "figures/q1_recommendation_tradeoffs.svg",
            "raster_file": "figures/q1_recommendation_tradeoffs.png",
            "title": "三种偏好方案的效率—未决权衡",
            "type": "Type 3",
            "purpose": "比较省样本、平衡参考和低未决方案在不同真实次品率下的 ASN 与未决概率。",
            "source": ["operating_characteristics.csv", "recommendations.csv", "config.json"],
            "claim_scope": "三方案代表不同运营偏好；不支持题目存在唯一给定最优方案或连续参数域全局最优。",
            "paper_candidate": "正文（方案权衡）",
            "render_check": render_check,
            "caption_zh": "图在相同的 13 个真实次品率上比较三种 Pareto 代表方案的平均抽检数和截尾未决概率。省样本方案强调检测效率，低未决方案强调降低证据不足的频率，平衡参考仅是两目标间的工程折中。",
        },
        {
            "file": "pareto_front.svg",
            "raster_file": "pareto_front.png",
            "title": f"{candidate_count} 个有限候选的 ASN—未决率 Pareto 前沿",
            "type": "Type 3",
            "purpose": "展示所有候选、等权 Pareto 前沿、三类推荐与外部五阶段基线。",
            "source": ["candidate_objectives.csv", "pareto_front.csv", "recommendations.csv", "baseline_comparison.csv"],
            "claim_scope": "精确 Pareto 仅指声明的 34 个有限候选内无 Monte Carlo 误差；外部基线不属于该网格且不连入前沿。",
            "paper_candidate": "正文（多目标结果）",
            "render_check": render_check,
            "caption_zh": f"图示 {candidate_count} 个预先声明候选在等权平均抽检数与等权未决概率之间的权衡，并标出 Pareto 前沿及三种偏好方案。外部五阶段基线仅作相同等权口径下的工程参照，不属于这 {candidate_count} 个候选的 Pareto 网格；本图不证明连续参数域或所有停止规则中的全局最优。",
        },
        {
            "file": "sensitivity_recommendations.csv",
            "title": "Q1 权重敏感性推荐表",
            "type": "Type 4",
            "purpose": "用紧凑精确表格展示 equal、near-threshold 和 far-threshold 权重下的推荐变化。",
            "source": ["sensitivity_recommendations.csv"],
            "claim_scope": "权重是公开的分析情景，不是题面事实；表格优于强行绘图。",
            "paper_candidate": "附录表",
            "render_check": f"PASS: {sensitivity_count}-row table loaded and cross-checked; no chart generated",
            "caption_zh": "表比较三种代表性次品率权重口径下的省样本、平衡与低未决推荐，用于说明工程参考依赖公开的评价权重。",
        },
    ]


def write_index(evidence: dict, render_check: str) -> None:
    (RESULTS / "figure_index.json").write_text(
        json.dumps(figure_entries(evidence, render_check), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_figure_manifest(render_check: str) -> None:
    inputs = [
        HERE / "config.json", RESULTS / "summary.json", RESULTS / "code_to_writer.json",
        RESULTS / "candidate_objectives.csv", RESULTS / "pareto_front.csv",
        RESULTS / "decision_boundary.csv", RESULTS / "operating_characteristics.csv",
        RESULTS / "recommendations.csv", RESULTS / "sensitivity_recommendations.csv",
        RESULTS / "baseline_comparison.csv",
    ]
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "cd B题/代码 && python -m q1.plot_q1",
        "python": sys.version,
        "platform": platform.platform(),
        "matplotlib": matplotlib.__version__,
        "numpy": np.__version__,
        "dpi": DPI,
        "fonts": {"chinese": CHINESE_FONT, "latin_fallback": LATIN_FONT, "math": "STIX"},
        "plot_source_sha256": sha256(HERE / "plot_q1.py"),
        "input_sha256": {str(path.relative_to(HERE.parent)): sha256(path) for path in inputs},
        "output_sha256": {str(path.relative_to(RESULTS)): sha256(path) for path in expected_outputs()},
        "render_check": render_check,
    }
    FIGURES.mkdir(parents=True, exist_ok=True)
    (FIGURES / "figure_repro_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def update_repro_manifest() -> None:
    path = RESULTS / "repro_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["source_sha256"]["q1/README.md"] = sha256(HERE / "README.md")
    manifest["plotting"] = {
        "command": "cd B题/代码 && python -m q1.plot_q1",
        "source": "q1/plot_q1.py",
        "source_sha256": sha256(HERE / "plot_q1.py"),
        "figure_manifest": "results/q1/figures/figure_repro_manifest.json",
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def expected_outputs() -> list[Path]:
    stems = [
        FIGURES / "q1_decision_regions_balanced",
        FIGURES / "q1_operating_characteristics_balanced",
        FIGURES / "q1_recommendation_tradeoffs",
        RESULTS / "pareto_front",
    ]
    return [stem.with_suffix(suffix) for stem in stems for suffix in (".svg", ".png")]


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Q1 publication-candidate figures from saved evidence")
    parser.add_argument("--mark-render-checked", action="store_true")
    args = parser.parse_args()
    evidence = load_evidence()
    if args.mark_render_checked:
        missing = [str(path) for path in expected_outputs() if not path.is_file() or path.stat().st_size == 0]
        if missing:
            raise RuntimeError(f"Cannot mark missing outputs as checked: {missing}")
        status = "PASS: final PNG inspected for glyphs, clipping, overlap, legends, empty panels and scale"
        write_index(evidence, status)
        write_figure_manifest(status)
        update_repro_manifest()
        print("Render check recorded as PASS")
        return

    plot_decision_regions(evidence)
    plot_operating_characteristics(evidence)
    plot_recommendation_tradeoffs(evidence)
    plot_pareto_front(evidence)
    missing = [str(path) for path in expected_outputs() if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise RuntimeError(f"Missing figure outputs: {missing}")
    status = "PENDING: generated successfully; final PNG visual inspection required"
    write_index(evidence, status)
    write_figure_manifest(status)
    update_repro_manifest()
    balanced = evidence["recommendation_map"]["balanced"]
    print(f"balanced reference verified: ({integer(balanced, 't_opt')}, {integer(balanced, 'N_max')})")
    print(f"fonts: Chinese={CHINESE_FONT}; Latin fallback={LATIN_FONT}; math=STIX")
    print(f"generated 4 SVG + 4 PNG at {DPI} dpi")


if __name__ == "__main__":
    main()
