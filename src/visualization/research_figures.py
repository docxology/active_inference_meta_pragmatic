"""Source-backed, static manuscript figures; exact data are retained alongside them."""

from pathlib import Path

import matplotlib.pyplot as plt
from .publication_style import PUBLICATION_STYLE, save_publication_figure
import numpy as np

from utils.figure_manager import FigureManager

COLORS = {
    "Q1_fixed": "#245D87",
    "Q2_metadata": "#236E66",
    "Q3_adaptive": "#916133",
    "Q4_learned": "#6B5289",
    "Q2_misleading": "#93536F",
    "Fixed_four": "#4C616C",
    "Fixed_five": "#64733F",
}
LABELS = {
    "Q1_fixed": "Q1 fixed model",
    "Q2_metadata": "Q2 true metadata",
    "Q3_adaptive": "Q3 adaptive sensing",
    "Q4_learned": "Q4 fitted model",
    "Q2_misleading": "Q2 misleading",
    "Fixed_four": "Fixed four",
    "Fixed_five": "Fixed five",
}

MARKERS = dict(zip(COLORS, ("o", "s", "^", "D", "X", "v", "P")))
LINE_STYLES = dict(zip(COLORS, ("-", "--", "-.", ":", (0, (4, 1, 1, 1)), "-", "--")))


def create_research_figures(
    experiment: dict, sensitivity: list[dict], output_dir: Path
) -> list[Path]:
    """Plot seed distributions, bootstrap intervals, costs, and exact EFE terms."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    registry = FigureManager(str(output_dir / "figure_registry.json"))
    paths = []
    style = {
        "font.family": "DejaVu Sans",
        "font.size": 14,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "savefig.dpi": 200,
    }
    with plt.rc_context({**PUBLICATION_STYLE, **style}):
        fig, axes = plt.subplots(2, 2, figsize=(8.5, 8.0), layout="constrained")
        for ax, metric, title in zip(
            axes.flat,
            ("accuracy", "brier", "log_loss", "mean_observations"),
            (
                "a  Accuracy · higher is better",
                "b  Brier · lower is better",
                "c  Log loss · lower is better",
                "d  Observation budget",
            ),
        ):
            for x, strategy in enumerate(COLORS):
                scale = 100 if metric == "accuracy" else 1
                units = [
                    r[metric]
                    for r in experiment["replicates"]
                    if r["strategy"] == strategy
                ]
                offsets = np.linspace(-0.12, 0.12, len(units))
                ax.scatter(
                    x + offsets,
                    np.asarray(units) * scale,
                    s=13,
                    alpha=0.35,
                    color=COLORS[strategy],
                    edgecolors="none",
                    marker=MARKERS[strategy],
                )
                interval = experiment["summary"][strategy][metric]
                ax.errorbar(
                    x,
                    interval["mean"] * scale,
                    yerr=[
                        [(interval["mean"] - interval["lower_bound"]) * scale],
                        [(interval["upper_bound"] - interval["mean"]) * scale],
                    ],
                    fmt=MARKERS[strategy],
                    markersize=6,
                    color=COLORS[strategy],
                    ecolor="#24333D",
                    capsize=4,
                    elinewidth=1.4,
                )
            ax.set_xticks(
                range(len(COLORS)), ["Q1", "Q2", "Q3", "Q4", "Misled", "F4", "F5"]
            )
            ax.set_title(title, loc="left")
            ax.grid(axis="y", alpha=0.2)
            ax.set_ylim(bottom=0)
            if metric == "accuracy":
                ax.set_ylim(0, 100)
                ax.set_ylabel("Correct trials (%)")
            elif metric == "mean_observations":
                ax.set_ylim(0, 5.5)
                ax.set_ylabel("Observations / trial")
            else:
                ax.set_ylabel(
                    "Loss / trial" + (" (nats)" if metric == "log_loss" else "")
                )
        fig.suptitle("Synthetic binary sensor task", fontsize=14)
        fig.supxlabel(
            f"Q1 inference: fixed model · Q2 context: true reliability\nQ3 monitoring: adaptive sensing · Q4 revision: fitted reliability\nMisled: false metadata · F4/F5: four/five observations\nSmall symbols: {experiment['config']['n_seeds']} seeds. Dark bars: marginal 95% intervals.",
            fontsize=12,
        )
        for extension in ("png", "pdf", "svg"):
            target = output_dir / f"quadrant_experiment.{extension}"
            save_publication_figure(fig, target)
            paths.append(target)
        plt.close(fig)
        registry.register_figure(
            "quadrant_experiment.png",
            "Held-out accuracy, calibration losses and sensing cost in a synthetic binary task. Dots show independent seeds; bars show 95% percentile-bootstrap intervals for seed means. Q3 uses extra observations; Q4 uses separate labeled training. Misleading metadata is a prespecified adverse control.",
            label="fig:quadrant_experiment",
            section="methodology",
            generated_by="scripts/07_analysis_pipeline.py",
            alt_text="Four panels show percentage accuracy, Brier loss, logarithmic loss and observations under seven sensor strategies. Distinct symbols and colors identify conditions. Small symbols are independent seed means; large symbols and capped bars show averages and marginal seed-bootstrap intervals. A key expands the Q codes into roles and implemented mechanisms. Observation use excludes separate fitting data.",
        )
        fig, axes = plt.subplots(1, 2, figsize=(8.5, 5.2), layout="constrained")
        r = np.array([row["reliability"] for row in sensitivity])
        for key, label, color, linestyle in (
            ("information_gain", "Information gain", "#176A9A", "-"),
            ("ambiguity", "Ambiguity", "#A65A17", "--"),
        ):
            axes[0].plot(
                r,
                [row[key] for row in sensitivity],
                label=label,
                color=color,
                ls=linestyle,
                lw=2,
            )
        for key, label, color, linestyle in (
            ("normalized_total", "Normalized EFE", "#176A9A", "-"),
            ("risk", "Risk", "#596B2D", ":"),
            ("ambiguity", "Ambiguity", "#A65A17", "--"),
        ):
            axes[1].plot(
                r,
                [row[key] for row in sensitivity],
                label=label,
                color=color,
                ls=linestyle,
                lw=2,
            )
        for ax, title in zip(
            axes,
            (
                "a  Information versus ambiguity",
                "b  Exact EFE decomposition",
            ),
        ):
            ax.set(
                title=title,
                xlabel="Binary sensor reliability",
                ylabel="Nats / policy step",
                xlim=(0.5, 1),
                ylim=(0, None),
            )
            ax.legend(frameon=False, fontsize=12)
            ax.grid(alpha=0.2)
        axes[0].axhline(np.log(2), color="#87929A", ls=":", lw=1)
        axes[0].text(0.51, np.log(2) + 0.01, "Binary maximum: ln 2", fontsize=12)
        axes[0].set_ylim(0, 0.77)
        fig.supxlabel(
            "EFE = expected free energy. Information gain + ambiguity = ln 2.\nNormalized EFE = risk + ambiguity; all quantities are exact.",
            fontsize=12,
        )
        for extension in ("png", "pdf", "svg"):
            target = output_dir / f"efe_sensitivity.{extension}"
            save_publication_figure(fig, target)
            paths.append(target)
        plt.close(fig)
        registry.register_figure(
            "efe_sensitivity.png",
            "Exact single-step EFE for a binary symmetric likelihood, uniform state prior, identity transition and C=(1,-1). Information gain grows as observations become less ambiguous. Normalized EFE equals risk plus ambiguity; these are exact calculations, not confidence intervals.",
            label="fig:efe_sensitivity",
            section="background",
            generated_by="scripts/07_analysis_pipeline.py",
            alt_text="Two exact line plots decompose one-step expected free energy under uniform state beliefs. Information gain rises from zero to ln 2 as ambiguity falls; their sum stays ln 2. Outcome risk remains constant, while normalized expected free energy equals risk plus ambiguity. Distinct line styles identify terms. No empirical uncertainty is implied.",
        )
    from .revision_figures import create_revision_figures

    paths.extend(create_revision_figures(experiment, output_dir))
    return paths
