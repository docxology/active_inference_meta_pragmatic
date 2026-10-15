"""Readable resource comparisons and descriptive calibration from held-out trials."""

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from utils.figure_manager import FigureManager
from .publication_style import PUBLICATION_STYLE, save_publication_figure

if TYPE_CHECKING:
    from .revision_figures import Evidence


def calibration_points(trials: list[dict[str, float]], strategy: str) -> np.ndarray:
    """Return occupied ten-bin means, event frequencies and counts, including p=1."""
    probability = np.array([row[strategy + "_p1"] for row in trials])
    states = np.array([row["state"] for row in trials])
    groups = np.minimum((probability * 10).astype(int), 9)
    rows = []
    for index in range(10):
        selected = groups == index
        if selected.any():
            rows.append(
                (probability[selected].mean(), states[selected].mean(), selected.sum())
            )
    return np.array(rows, dtype=float).reshape(-1, 3)


def create_resource_calibration(experiment: "Evidence", output_dir: Path) -> list[Path]:
    """Align strategy rows across accuracy/cost and separate calibration comparisons."""
    from .research_figures import COLORS, LABELS, MARKERS, LINE_STYLES

    output_dir.mkdir(parents=True, exist_ok=True)
    names = list(COLORS)
    with plt.rc_context(PUBLICATION_STYLE):
        fig, axes = plt.subplots(2, 2, figsize=(8.5, 9.5), layout="constrained")
        for index, strategy in enumerate(names):
            for axis, metric, scale in (
                (axes[0, 0], "accuracy", 100),
                (axes[0, 1], "mean_observations", 1),
            ):
                interval = experiment["summary"][strategy][metric]
                mean = scale * interval["mean"]
                axis.errorbar(
                    mean,
                    index,
                    xerr=[
                        [scale * (interval["mean"] - interval["lower_bound"])],
                        [scale * (interval["upper_bound"] - interval["mean"])],
                    ],
                    fmt=MARKERS[strategy],
                    color=COLORS[strategy],
                    ecolor="#23333D",
                    capsize=3,
                    markersize=7,
                )
                axis.annotate(
                    f"{mean:.2f}" if metric == "accuracy" else f"{mean:.3f}",
                    (mean, index),
                    xytext=(8, 0),
                    textcoords="offset points",
                    va="center",
                    color=COLORS[strategy],
                    fontsize=12,
                )
        for axis in axes[0]:
            axis.set(yticks=range(len(names)), ylim=(len(names) - 0.5, -0.5))
            axis.axhspan(2.55, 3.45, color="#F0F2E8", zorder=-1)
            axis.grid(axis="x", alpha=0.16)
        axes[0, 0].set(
            title="a  Prediction accuracy ↑",
            xlabel="Correct trials (%)",
            xlim=(45, 104),
            yticklabels=[LABELS[n] + ("*" if n == "Q4_learned" else "") for n in names],
        )
        axes[0, 1].set(
            title="b  Sensing resources",
            xlabel="Observations / trial",
            xlim=(0, 6.3),
            yticklabels=[],
        )
        for axis, strategies, title in (
            (
                axes[1, 0],
                ("Q1_fixed", "Q2_metadata", "Q4_learned"),
                "c  Fixed, metadata, learned",
            ),
            (
                axes[1, 1],
                ("Q3_adaptive", "Q2_misleading"),
                "d  Adaptive and misleading",
            ),
        ):
            axis.plot([0, 1], [0, 1], color="#777777", ls="--", lw=1.3)
            for strategy in strategies:
                points = calibration_points(experiment["trials"], strategy)
                axis.plot(
                    points[:, 0],
                    points[:, 1],
                    color=COLORS[strategy],
                    ls=LINE_STYLES[strategy],
                    lw=1.5,
                    alpha=0.85,
                    label=LABELS[strategy],
                )
                axis.scatter(
                    points[:, 0],
                    points[:, 1],
                    s=500 * points[:, 2] / len(experiment["trials"]),
                    color=COLORS[strategy],
                    zorder=3,
                )
            axis.set(
                title=title,
                xlabel="Mean forecast P(state = 1)",
                ylabel="Observed state-1 frequency",
                xlim=(-0.03, 1.03),
                ylim=(-0.03, 1.03),
                xticks=(0, 0.5, 1),
                yticks=(0, 0.5, 1),
            )
            axis.set_aspect("equal", adjustable="box")
            axis.legend(
                frameon=False,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.20),
                fontsize=12,
                markerscale=0.8,
            )
            axis.grid(alpha=0.12)
        fig.supxlabel(
            "Top: same strategy rows; marginal 95% seed intervals.\n"
            "* Learned model also uses separate labeled training.\n"
            f"Bottom: {len(experiment['trials']):,} trials/strategy; 10 bins; area scales with count.\n"
            "Dashed diagonal: agreement. No calibration intervals.",
            fontsize=12,
        )
        paths = []
        for extension in ("png", "pdf", "svg"):
            path = output_dir / f"resource_calibration.{extension}"
            save_publication_figure(fig, path)
            paths.append(path)
        plt.close(fig)
    FigureManager(str(output_dir / "figure_registry.json")).register_figure(
        "resource_calibration.png",
        "Aligned accuracy and sensing cost with separated descriptive calibration views.",
        label="fig:resource_calibration",
        section="discussion",
        generated_by="scripts/07_analysis_pipeline.py",
        alt_text="Aligned rows compare percentage accuracy and observations using means, distinct symbols and marginal seed intervals. The fitted-model row is shaded to flag separate training. Two lower calibration panels use line styles as well as color; point area scales with bin population. Dashed diagonals denote agreement. These pooled curves have no calibration uncertainty bands.",
    )
    return paths
