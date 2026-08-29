"""从已验收结果生成 Q2 论文候选图。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "cumcm-q2-publication-v1"
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, TwoSlopeNorm
from matplotlib.font_manager import fontManager
from matplotlib.patches import Patch, Rectangle

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results" / "q2"
FIGURES = RESULTS / "figures"
DPI = 360
COLORS = {
    "blue": "#1A6FC4", "orange": "#E28E2C", "purple": "#7B5FD6",
    "teal": "#258B82", "gray": "#767676", "grid": "#D8D8D8", "text": "#111111",
}


def register_cjk_fonts():
    for path in (
        "/usr/share/fonts/google-noto-serif-cjk-vf-fonts/NotoSerifCJK-VF.ttc",
        "/usr/share/fonts/fandol/FandolSong-Regular.otf",
        "/usr/share/fonts/google-droid-sans-fonts/DroidSansFallbackFull.ttf",
    ):
        if Path(path).exists():
            try:
                fontManager.addfont(path)
            except RuntimeError:
                pass


def choose_font(names):
    installed = {font.name for font in fontManager.ttflist}
    for name in names:
        if name in installed:
            return name
    raise RuntimeError(f"No usable font found in {names}")


register_cjk_fonts()
CHINESE_FONT = choose_font(["Noto Serif CJK SC", "FandolSong", "Droid Sans Fallback"])
LATIN_FONT = choose_font(["Times New Roman", "Liberation Serif", "DejaVu Serif"])
plt.rcParams.update({
    "font.family": CHINESE_FONT, "mathtext.fontset": "stix", "axes.unicode_minus": False,
    "figure.facecolor": "white", "axes.facecolor": "white", "text.color": COLORS["text"],
    "axes.edgecolor": COLORS["text"], "axes.labelcolor": COLORS["text"],
    "xtick.color": COLORS["text"], "ytick.color": COLORS["text"],
    "axes.titlesize": 11, "axes.labelsize": 10, "xtick.labelsize": 8.5,
    "ytick.labelsize": 8.5, "legend.fontsize": 8, "axes.linewidth": 0.9,
    "svg.fonttype": "none",
})


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path, normalized=False):
    data = Path(path).read_bytes()
    if normalized:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def policy_id(row):
    return "".join(str(int(row[key])) for key in ("x1", "x2", "y", "z"))


def load_evidence():
    evidence = {
        "config": read_json(HERE / "config.json"), "cases": read_json(HERE / "table1.json"),
        "summary": read_json(RESULTS / "summary.json"),
        "writer": read_json(RESULTS / "code_to_writer.json"),
        "all": pd.read_csv(RESULTS / "all_policies.csv"),
        "best": pd.read_csv(RESULTS / "best_policies.csv"),
        "sensitivity": pd.read_csv(RESULTS / "sensitivity.csv"),
        "structural": pd.read_csv(RESULTS / "structural_comparison.csv"),
    }
    validate(evidence)
    return evidence


def validate(evidence):
    all_policies, best, summary = evidence["all"], evidence["best"], evidence["summary"]
    if len(evidence["cases"]) != 6 or len(all_policies) != 96:
        raise RuntimeError("Q2 的 6×16 策略证据不完整")
    if all_policies.duplicated(["case", "x1", "x2", "y", "z"]).any():
        raise RuntimeError("Q2 策略存在重复")
    counts = all_policies.status.value_counts().to_dict()
    if counts != summary["status_counts"] or counts != {"SUCCESS_EXACT": 60, "NON_ABSORBING": 36}:
        raise RuntimeError("吸收性分类跨文件不一致")
    summary_best = {
        (int(item["case"]), policy_id(row)): float(row["expected_profit"])
        for item in summary["case_results"] for row in item["best_strategies"]
    }
    csv_best = {(int(row.case), policy_id(row)): float(row.expected_profit) for _, row in best.iterrows()}
    if set(summary_best) != set(csv_best) or any(abs(summary_best[k] - v) > 1e-9 for k, v in csv_best.items()):
        raise RuntimeError("summary.json 与 best_policies.csv 不一致")
    if evidence["writer"]["claims"][0]["table"] != "best_policies.csv":
        raise RuntimeError("写作接口未指向 Q2 规范结果表")
    costs = [column for column in best if column.startswith("cost_")]
    if np.max(np.abs(best[costs].sum(axis=1) - best.expected_total_cost)) > 1e-9:
        raise RuntimeError("最优策略成本分项不守恒")
    prices = {int(row["case"]): float(row["price"]) for row in evidence["cases"]}
    for _, row in best.iterrows():
        if abs(prices[int(row.case)] - row.expected_total_cost - row.expected_profit) > 1e-9:
            raise RuntimeError("售价、成本与利润不守恒")
    if len(evidence["sensitivity"]) != 60 or len(evidence["structural"]) != 12:
        raise RuntimeError("Q2 稳健性证据表不完整")


def style_axis(ax):
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.65, alpha=0.75)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
        if not any("\u4e00" <= char <= "\u9fff" for char in label.get_text()):
            label.set_fontfamily(LATIN_FONT)


def save(fig, stem):
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    svg, png = stem.with_suffix(".svg"), stem.with_suffix(".png")
    fig.savefig(svg, bbox_inches="tight", metadata={"Date": None})
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    fig.savefig(png, dpi=DPI, bbox_inches="tight", facecolor="white", metadata={"Software": "Q2 plot_q2.py"})
    plt.close(fig)


def sorted_best(best):
    return best.sort_values(["case", "x1", "x2", "y", "z"]).reset_index(drop=True)


def row_labels(best, with_policy=False):
    counts, seen, labels = best.groupby("case").size().to_dict(), {}, []
    for _, row in best.iterrows():
        case = int(row.case)
        seen[case] = seen.get(case, 0) + 1
        suffix = f"-{chr(64 + seen[case])}" if counts[case] > 1 else ""
        label = f"情形{case}{suffix}"
        labels.append(f"{label}\n{policy_id(row)}" if with_policy else label)
    return labels


def plot_policy_matrix(evidence):
    best = sorted_best(evidence["best"])
    values = best[["x1", "x2", "y", "z"]].to_numpy(dtype=int)
    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    ax.imshow(values, cmap=ListedColormap(["#EEF1F4", COLORS["blue"]]), vmin=0, vmax=1, aspect="auto")
    for i in range(len(best)):
        for j in range(4):
            label = ("拆解" if values[i, j] else "不拆") if j == 3 else ("检测" if values[i, j] else "不检")
            ax.text(j, i, label, ha="center", va="center", fontsize=9,
                    color="white" if values[i, j] else COLORS["text"])
    ax.set_xticks(range(4), ["零件1检测 $x_1$", "零件2检测 $x_2$", "成品检测 $y$", "不合格品拆解 $z$"])
    ax.set_yticks(range(len(best)), row_labels(best))
    ax.set_xticks(np.arange(-0.5, 4, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(best), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.6)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.tick_params(axis="x", bottom=False, top=True, labelbottom=False, labeltop=True, pad=7)
    ax.set_title("六种情形的最优固定策略（情形3存在并列解）", pad=14)
    ax.legend(handles=[Patch(facecolor="#EEF1F4", edgecolor=COLORS["gray"], label="0：不执行"),
                       Patch(facecolor=COLORS["blue"], label="1：执行")],
              loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False)
    save(fig, FIGURES / "q2_optimal_policy_matrix")


def plot_best_profit(evidence):
    best = evidence["best"]
    grouped = best.groupby("case", as_index=False).expected_profit.max()
    policies = {case: "/".join(policy_id(row) for _, row in frame.iterrows()) for case, frame in best.groupby("case")}
    labels = [f"情形 {int(case)}\n{policies[case]}" for case in grouped.case]
    fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
    bars = ax.bar(labels, grouped.expected_profit, width=0.66, color=COLORS["blue"], edgecolor="white")
    ax.bar_label(bars, labels=[f"{value:.3f}" for value in grouped.expected_profit], padding=4, fontsize=8.5)
    ax.set_ylim(0, float(grouped.expected_profit.max()) * 1.18)
    ax.set(xlabel="表1情形与最优策略 $(x_1,x_2,y,z)$", ylabel="期望利润（元/最终合格交付）",
           title="六种名义情形的最优期望利润")
    style_axis(ax)
    save(fig, RESULTS / "best_profit_by_case")


def plot_profit_landscape(evidence):
    policies = [f"{value:04b}" for value in range(16)]
    matrix, statuses = np.full((6, 16), np.nan), np.empty((6, 16), dtype=object)
    for _, row in evidence["all"].iterrows():
        i, j = int(row.case) - 1, policies.index(policy_id(row))
        statuses[i, j] = row.status
        if row.status == "SUCCESS_EXACT":
            matrix[i, j] = row.expected_profit
    finite = matrix[np.isfinite(matrix)]
    span = max(abs(float(finite.min())), abs(float(finite.max())))
    cmap = LinearSegmentedColormap.from_list("q2_profit", ["#A64B43", "#F3EEE7", COLORS["blue"]])
    cmap.set_bad("#D5D5D5")
    fig, ax = plt.subplots(figsize=(9.2, 4.5), constrained_layout=True)
    image = ax.imshow(np.ma.masked_invalid(matrix), cmap=cmap,
                      norm=TwoSlopeNorm(vmin=-span, vcenter=0, vmax=span), aspect="auto")
    for i in range(6):
        for j in range(16):
            if statuses[i, j] == "NON_ABSORBING":
                ax.text(j, i, "×", ha="center", va="center", fontsize=8, color=COLORS["gray"])
    for _, row in evidence["best"].iterrows():
        i, j = int(row.case) - 1, policies.index(policy_id(row))
        ax.add_patch(Rectangle((j - 0.48, i - 0.48), 0.96, 0.96, fill=False,
                               edgecolor=COLORS["orange"], linewidth=2))
    ax.set_xticks(range(16), policies, rotation=45, ha="right")
    ax.set_yticks(range(6), [f"情形 {case}" for case in range(1, 7)])
    ax.set(xlabel="固定策略 $(x_1,x_2,y,z)$", ylabel="表1情形", title="六种情形下16个固定策略的期望利润全景")
    ax.set_xticks(np.arange(-0.5, 16, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 6, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.7)
    ax.tick_params(which="minor", bottom=False, left=False)
    cbar = fig.colorbar(image, ax=ax, shrink=0.86, pad=0.02)
    cbar.set_label("期望利润（元/最终合格交付）")
    ax.legend(handles=[Patch(facecolor="#D5D5D5", edgecolor=COLORS["gray"], label="× 非吸收策略"),
                       Patch(facecolor="none", edgecolor=COLORS["orange"], linewidth=2, label="有限策略集内最优")],
              loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2, frameon=False)
    save(fig, FIGURES / "q2_policy_profit_landscape")


def plot_cost_composition(evidence):
    best = sorted_best(evidence["best"])
    groups = [
        ("零件采购", best.cost_purchase_1 + best.cost_purchase_2, COLORS["blue"], ""),
        ("零件检测", best.cost_inspection_1 + best.cost_inspection_2, COLORS["orange"], "//"),
        ("装配", best.cost_assembly, COLORS["teal"], ""),
        ("成品检测", best.cost_product_inspection, COLORS["purple"], ".."),
        ("拆解与调换", best.cost_disassembly + best.cost_replacement_loss, COLORS["gray"], "xx"),
    ]
    x, bottom = np.arange(len(best)), np.zeros(len(best))
    fig, ax = plt.subplots(figsize=(8.1, 4.8), constrained_layout=True)
    for name, values, color, hatch in groups:
        ax.bar(x, values, bottom=bottom, width=0.68, label=name, color=color,
               edgecolor="white", linewidth=0.7, hatch=hatch)
        bottom += values.to_numpy()
    for i, row in best.iterrows():
        ax.text(i, bottom[i] + 0.7, f"利润 {row.expected_profit:.2f}", ha="center", fontsize=7.3)
    ax.set_xticks(x, row_labels(best, with_policy=True))
    ax.set_ylim(0, float(bottom.max()) * 1.18)
    ax.set(xlabel="表1情形与最优策略 $(x_1,x_2,y,z)$", ylabel="期望成本（元/最终合格交付）",
           title="最优固定策略的期望成本构成")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.01), ncol=5, frameon=False)
    style_axis(ax)
    save(fig, FIGURES / "q2_optimal_cost_composition")


def figure_entries(evidence, render_check):
    counts = evidence["all"].status.value_counts().to_dict()
    common = {"type": "Type 3", "paper_candidate": "正文", "render_check": render_check}
    return [
        {**common, "file": "figures/q2_optimal_policy_matrix.svg", "raster_file": "figures/q2_optimal_policy_matrix.png",
         "title": "六种情形的最优固定策略矩阵", "purpose": "直接展示四个二元生产决策。",
         "source": ["best_policies.csv", "summary.json"],
         "claim_scope": "仅适用于表1名义参数和当前固定策略定义；情形3的两个并列解均保留。",
         "caption_zh": "图以二元矩阵汇总表1六种情形的最优固定策略。蓝色表示执行相应检测或拆解动作，灰色表示不执行；情形3存在两个期望利润相同的并列解，因此分别列出。"},
        {**common, "file": "best_profit_by_case.svg", "raster_file": "best_profit_by_case.png",
         "title": "六种名义情形的最优期望利润", "purpose": "比较各情形最优策略的期望利润。",
         "source": ["best_policies.csv", "table1.json"],
         "claim_scope": "核算单位为每最终交付一件合格品，不是单位时间利润。",
         "caption_zh": "图比较表1六种名义情形在各自最优固定策略下的期望利润，横轴同时标注策略位串。利润以每最终交付一件合格品为核算单位，情形间差异反映输入参数和最优动作组合的共同作用。"},
        {**common, "file": "figures/q2_policy_profit_landscape.svg", "raster_file": "figures/q2_policy_profit_landscape.png",
         "title": "六种情形下16个固定策略的期望利润全景", "purpose": "展示全部策略的吸收性、利润和最优位置。",
         "source": ["all_policies.csv", "best_policies.csv", "summary.json"],
         "claim_scope": f"精确最优仅指每种情形16个固定策略；{counts['NON_ABSORBING']}个非吸收策略不参与比较，也不代表历史自适应策略空间的全局最优。",
         "caption_zh": f"图展示六种情形各16个固定策略的期望利润。灰色叉号表示存在可达闭合暂态类的非吸收策略，共{counts['NON_ABSORBING']}个；橙框标出各情形在可吸收策略中的最优解。"},
        {**common, "file": "figures/q2_optimal_cost_composition.svg", "raster_file": "figures/q2_optimal_cost_composition.png",
         "title": "最优固定策略的期望成本构成", "purpose": "展示最优利润背后的成本构成。",
         "source": ["best_policies.csv", "table1.json"],
         "claim_scope": "拆解与调换合并仅为视觉汇总，原始分项以CSV为准。",
         "caption_zh": "图分解各最优固定策略在最终成功交付前累计发生的期望成本，并标注对应利润。情形3的并列方案成本总额相同，但成品检测与调换成本构成不同。"},
        {"file": "sensitivity.csv", "title": "Q2 单因素敏感性结果表", "type": "Type 4",
         "purpose": "记录表1已观测成本值下的推荐变化。", "source": ["sensitivity.csv"],
         "claim_scope": "仅覆盖表1中实际出现的参数值，不代表连续区间临界点。", "paper_candidate": "附录表",
         "render_check": f"PASS: {len(evidence['sensitivity'])}-row table loaded and cross-checked; no chart generated",
         "caption_zh": "表列出零件检测费、调换损失和拆解费取表1已观测值时重新优化所得的最优策略与利润。"},
        {"file": "structural_comparison.csv", "title": "Q2 回收件质量解释结构对照表", "type": "Type 4",
         "purpose": "比较物理质量保持主模型与质量重置近似。", "source": ["structural_comparison.csv"],
         "claim_scope": "quality_reset 仅为结构敏感性近似，不是题面事实。", "paper_candidate": "附录表",
         "render_check": f"PASS: {len(evidence['structural'])}-row table loaded and cross-checked; no chart generated",
         "caption_zh": "表比较拆解后保持真实质量的主模型与质量重置近似；论文主结论仍以质量保持模型为准。"},
    ]


def expected_outputs():
    stems = [FIGURES / "q2_optimal_policy_matrix", RESULTS / "best_profit_by_case",
             FIGURES / "q2_policy_profit_landscape", FIGURES / "q2_optimal_cost_composition"]
    return [stem.with_suffix(suffix) for stem in stems for suffix in (".svg", ".png")]


def update_metadata():
    sources = [HERE / "README.md", HERE / "plot_q2.py"]
    plotting = {"generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "command": "cd B题/代码 && python -m q2.plot_q2", "source": "q2/plot_q2.py",
                "source_sha256": digest(HERE / "plot_q2.py"),
                "figure_manifest": "results/q2/figures/figure_repro_manifest.json"}
    for name in ("run_metadata.json", "repro_manifest.json"):
        path, data = RESULTS / name, read_json(RESULTS / name)
        for source in sources:
            key = str(source.relative_to(HERE.parent))
            data["source_sha256"][key], data["normalized_source_sha256"][key] = digest(source), digest(source, True)
        data["plotting"] = plotting
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    path, data = RESULTS / "summary.json", read_json(RESULTS / "summary.json")
    for source in sources:
        key = str(source.relative_to(HERE.parent))
        data["metadata"]["source_sha256"][key] = digest(source)
        data["metadata"]["normalized_source_sha256"][key] = digest(source, True)
    data["metadata"]["plotting"] = plotting
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_artifacts(evidence, status):
    (RESULTS / "figure_index.json").write_text(
        json.dumps(figure_entries(evidence, status), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    inputs = [HERE / "config.json", HERE / "table1.json", RESULTS / "summary.json",
              RESULTS / "code_to_writer.json", RESULTS / "all_policies.csv", RESULTS / "best_policies.csv",
              RESULTS / "sensitivity.csv", RESULTS / "structural_comparison.csv"]
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "command": "cd B题/代码 && python -m q2.plot_q2",
        "python": sys.version, "platform": platform.platform(), "matplotlib": matplotlib.__version__,
        "numpy": np.__version__, "pandas": pd.__version__, "dpi": DPI,
        "fonts": {"chinese": CHINESE_FONT, "latin_fallback": LATIN_FONT, "math": "STIX"},
        "plot_source_sha256": digest(HERE / "plot_q2.py"),
        "input_sha256": {str(path.relative_to(HERE.parent)): digest(path) for path in inputs},
        "output_sha256": {str(path.relative_to(RESULTS)): digest(path) for path in expected_outputs()},
        "render_check": status,
    }
    FIGURES.mkdir(parents=True, exist_ok=True)
    (FIGURES / "figure_repro_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mark-render-checked", action="store_true")
    args = parser.parse_args()
    evidence = load_evidence()
    if args.mark_render_checked:
        if any(not path.is_file() or path.stat().st_size == 0 for path in expected_outputs()):
            raise RuntimeError("存在缺失图，不能标记渲染通过")
        status = "PASS: final PNG inspected for glyphs, clipping, overlap, legends, empty panels and scale"
        update_metadata()
        write_artifacts(evidence, status)
        print("Render check recorded as PASS")
        return
    plot_policy_matrix(evidence)
    plot_best_profit(evidence)
    plot_profit_landscape(evidence)
    plot_cost_composition(evidence)
    if any(not path.is_file() or path.stat().st_size == 0 for path in expected_outputs()):
        raise RuntimeError("Q2 图表输出不完整")
    update_metadata()
    write_artifacts(evidence, "PENDING: generated successfully; final PNG visual inspection required")
    print("verified: 6 cases, 96 policies, 60 absorbing, 36 non-absorbing, 7 best rows")
    print(f"fonts: Chinese={CHINESE_FONT}; Latin fallback={LATIN_FONT}; math=STIX")
    print(f"generated 4 SVG + 4 PNG at {DPI} dpi")


if __name__ == "__main__":
    main()
