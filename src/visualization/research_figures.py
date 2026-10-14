"""Source-backed, static manuscript figures; exact data are retained alongside them."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from utils.figure_manager import FigureManager

COLORS = {
    "Q1_fixed": "#333333",
    "Q2_metadata": "#176A9A",
    "Q3_adaptive": "#A65A17",
    "Q4_learned": "#596B2D",
    "Q2_misleading": "#93536F",
}
LABELS = {
    "Q1_fixed": "Q1 fixed",
    "Q2_metadata": "Q2 metadata",
    "Q3_adaptive": "Q3 adaptive",
    "Q4_learned": "Q4 learned",
    "Q2_misleading": "Q2 misleading",
}


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
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "savefig.dpi": 200,
    }
    with plt.rc_context(style):
        fig, axes = plt.subplots(2, 2, figsize=(10, 7), layout="constrained")
        for ax, metric, title in zip(
            axes.flat,
            ("accuracy", "brier", "log_loss", "mean_observations"),
            (
                "a  Classification accuracy",
                "b  Brier loss",
                "c  Log loss",
                "d  Sensing cost",
            ),
        ):
            for x, strategy in enumerate(COLORS):
                units = [
                    r[metric]
                    for r in experiment["replicates"]
                    if r["strategy"] == strategy
                ]
                offsets = np.linspace(-0.12, 0.12, len(units))
                ax.scatter(
                    x + offsets,
                    units,
                    s=13,
                    alpha=0.35,
                    color=COLORS[strategy],
                    edgecolors="none",
                )
                interval = experiment["summary"][strategy][metric]
                ax.errorbar(
                    x,
                    interval["mean"],
                    yerr=[
                        [interval["mean"] - interval["lower_bound"]],
                        [interval["upper_bound"] - interval["mean"]],
                    ],
                    fmt="o",
                    markersize=6,
                    color=COLORS[strategy],
                    capsize=4,
                    elinewidth=1.4,
                )
            ax.set_xticks(
                range(len(COLORS)), [LABELS[s].replace(" ", "\n", 1) for s in COLORS]
            )
            ax.set_title(title, loc="left")
            ax.grid(axis="y", alpha=0.2)
            ax.set_ylim(bottom=0)
            if metric == "accuracy":
                ax.set_ylim(0, 1)
                ax.set_ylabel("Correct / trials")
            elif metric == "mean_observations":
                ax.set_ylim(0, 5.5)
                ax.set_ylabel("Observations / trial")
            else:
                ax.set_ylabel(
                    "Loss / trial" + (" (nats)" if metric == "log_loss" else "")
                )
        fig.suptitle("Synthetic binary sensor task", fontsize=14)
        fig.supxlabel(
            f"Dots: {experiment['config']['n_seeds']} independent seeds; intervals: 95% bootstrap CI of seed means",
            fontsize=10,
        )
        for extension in ("png", "pdf", "svg"):
            target = output_dir / f"quadrant_experiment.{extension}"
            fig.savefig(target, bbox_inches="tight")
            paths.append(target)
        plt.close(fig)
        registry.register_figure(
            "quadrant_experiment.png",
            "Held-out accuracy, calibration losses and sensing cost in a synthetic binary task. Dots show independent seeds; bars show 95% percentile-bootstrap intervals for seed means. Q3 uses extra observations; Q4 uses separate labeled training. Misleading metadata is a prespecified adverse control.",
            label="fig:quadrant_experiment",
            section="methodology",
            generated_by="scripts/07_analysis_pipeline.py",
            alt_text="Four panels compare accuracy, Brier loss, log loss and observations per trial across five synthetic sensor strategies. Adaptive sensing has the highest accuracy and lowest losses while using about 3.9 observations; other strategies use three. True and learned reliability perform similarly, while misleading reliability has the lowest accuracy and highest losses. Dots represent independent seeds; bars represent 95 percent bootstrap intervals for seed means.",
        )
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout="constrained")
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
                "a  Information and observation noise",
                "b  Risk + ambiguity decomposition",
            ),
        ):
            ax.set(
                title=title,
                xlabel="Binary sensor reliability",
                ylabel="Nats / policy step",
                xlim=(0.5, 1),
                ylim=(0, None),
            )
            ax.legend(frameon=False, fontsize=9)
            ax.grid(alpha=0.2)
        for extension in ("png", "pdf", "svg"):
            target = output_dir / f"efe_sensitivity.{extension}"
            fig.savefig(target, bbox_inches="tight")
            paths.append(target)
        plt.close(fig)
        registry.register_figure(
            "efe_sensitivity.png",
            "Exact single-step EFE for a binary symmetric likelihood, uniform state prior, identity transition and C=(1,-1). Information gain grows as observations become less ambiguous. Normalized EFE equals risk plus ambiguity; these are exact calculations, not confidence intervals.",
            label="fig:efe_sensitivity",
            section="background",
            generated_by="scripts/07_analysis_pipeline.py",
            alt_text="Two exact line plots against binary sensor reliability from 0.5 to 1. Information gain rises from zero to log two as ambiguity falls from log two to zero. Outcome risk stays constant under uniform predicted outcomes, and normalized expected free energy decreases as ambiguity falls, remaining equal to risk plus ambiguity. These curves are mathematical evaluations without sampling intervals.",
        )
    return paths
