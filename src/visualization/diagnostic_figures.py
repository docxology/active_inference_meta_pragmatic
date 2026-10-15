"""Paired scientific contrasts and stopping sensitivity with explicit units."""

from pathlib import Path

import matplotlib.pyplot as plt
from .publication_style import PUBLICATION_STYLE, save_publication_figure
import numpy as np

from utils.figure_manager import FigureManager


def create_diagnostic_figures(
    diagnostics: dict[str, list[dict[str, str | int | float]]], output_dir: Path
) -> list[Path]:
    """Render marginal seed intervals without interpreting overlap as a paired test."""
    contrasts = [
        ("Q2_metadata", "Q1_fixed", "Metadata − fixed"),
        ("Q3_adaptive", "Q2_metadata", "Adaptive − metadata"),
        ("Q4_learned", "Q2_metadata", "Learned − metadata"),
        ("Q2_misleading", "Q2_metadata", "Misleading − metadata"),
        ("Q3_adaptive", "Fixed_four", "Adaptive − fixed four"),
        ("Q3_adaptive", "Fixed_five", "Adaptive − fixed five"),
    ]
    paths = []
    with plt.rc_context(PUBLICATION_STYLE):
        fig, axes = plt.subplots(3, 1, figsize=(8.5, 9.0), layout="constrained")
        for axis, metric, label, scale in zip(
            axes,
            ("accuracy", "brier", "log_loss"),
            (
                "Accuracy difference (percentage points)",
                "Brier loss difference",
                "Log loss difference (nats)",
            ),
            (100, 1, 1),
        ):
            for y, (treated, control, _) in enumerate(contrasts):
                row = next(
                    r
                    for r in diagnostics["paired_estimates"]
                    if r["treated"] == treated
                    and r["control"] == control
                    and r["metric"] == metric
                )
                mean, low, high = (
                    float(row[key]) * scale for key in ("mean", "lower", "upper")
                )
                axis.errorbar(
                    mean,
                    y,
                    xerr=[[mean - low], [high - mean]],
                    fmt="o",
                    color="#176A9A",
                    ecolor="#23333D",
                    capsize=4,
                    markersize=6,
                )
            axis.axvline(0, color="#999999", ls="--", lw=1)
            axis.set(xlabel=label, yticks=range(6), ylim=(5.6, -0.6))
            axis.grid(axis="x", alpha=0.15)
            axis.set_title(
                {
                    "accuracy": "a  Accuracy: right favors first",
                    "brier": "b  Brier loss: left favors first",
                    "log_loss": "c  Log loss: left favors first",
                }[metric],
                loc="left",
                fontsize=13,
            )
        axes[0].set_yticklabels([r[2] for r in contrasts], fontsize=12)
        for axis in axes[1:]:
            axis.set_yticklabels([r[2] for r in contrasts], fontsize=12)
        fig.suptitle("Paired estimates across accuracy and proper losses", fontsize=13)
        fig.supxlabel(
            "Points: paired seed means; bars: marginal 95% intervals.\nAccuracy favors positive differences; losses favor negative differences.",
            fontsize=12,
        )
        for extension in ("png", "pdf", "svg"):
            target = output_dir / f"paired_diagnostics.{extension}"
            save_publication_figure(fig, target)
            paths.append(target)
        plt.close(fig)
        fig, axes = plt.subplots(1, 2, figsize=(8.5, 5.4), layout="constrained")
        for metric, axis, color, label in (
            ("accuracy", axes[0], "#176A9A", "Accuracy (%)"),
            ("mean_observations", axes[1], "#AE6B35", "Mean observations / trial"),
        ):
            selected = [
                r for r in diagnostics["stopping_summary"] if r["metric"] == metric
            ]
            x = np.array([r["threshold"] for r in selected], dtype=float)
            scale = 100 if metric == "accuracy" else 1
            means = np.array([float(r["mean"]) * scale for r in selected])
            lower = np.array([float(r["lower"]) * scale for r in selected])
            upper = np.array([float(r["upper"]) * scale for r in selected])
            axis.errorbar(
                x,
                means,
                yerr=[means - lower, upper - means],
                fmt="o-" if metric == "accuracy" else "s-",
                color=color,
                ecolor="#23333D",
                capsize=3,
                elinewidth=1.1,
            )
            axis.axvline(
                0.9, color="#777777", ls="--", lw=1, label="Original rule: 0.90"
            )
            axis.set(
                xlabel="Required posterior confidence",
                ylabel=label,
                xlim=(0.49, 1.01),
            )
            axis.grid(alpha=0.15)
            axis.legend(frameon=False, fontsize=12)
            axis.set_title(
                "a  Predictive performance"
                if metric == "accuracy"
                else "b  Acquired evidence",
                loc="left",
            )
        fig.suptitle("Stopping-rule sensitivity on common held-out trials", fontsize=13)
        fig.supxlabel(
            "Eleven evaluated thresholds; capped marginal 95% seed intervals.\nLines guide the eye. Reused data; no policy independently validated.",
            fontsize=12,
        )
        for extension in ("png", "pdf", "svg"):
            target = output_dir / f"stopping_sensitivity.{extension}"
            save_publication_figure(fig, target)
            paths.append(target)
        plt.close(fig)
    registry = FigureManager(str(output_dir / "figure_registry.json"))
    for name, caption, alt in (
        (
            "paired_diagnostics",
            "Exploratory paired seed contrasts in accuracy, Brier loss and logarithmic loss.",
            "Six matched strategy comparisons are shown in three aligned panels. Points are mean paired seed differences and bars are marginal 95 percent bootstrap intervals. Accuracy favors positive differences; proper losses favor negative differences. No simultaneous coverage is claimed.",
        ),
        (
            "stopping_sensitivity",
            "Exploratory stopping-threshold sensitivity at matched trials.",
            "Two line plots show held-out accuracy and mean observations across eleven confidence thresholds from 0.5 to 1. Capped bars at the evaluated thresholds show marginal seed-bootstrap intervals; connecting lines guide the eye. A vertical line marks the original threshold 0.9. These reused test trials do not validate an optimized threshold.",
        ),
    ):
        registry.register_figure(
            name + ".png",
            caption,
            label="fig:" + name,
            section="discussion",
            generated_by="scripts/07_analysis_pipeline.py",
            alt_text=alt,
        )
    return paths
