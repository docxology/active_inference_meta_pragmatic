"""Data-backed graphical abstract and actual GNN/EFE action-task figures."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patheffects as effects
from matplotlib.ticker import PercentFormatter
from .publication_style import PUBLICATION_STYLE, save_publication_figure
import numpy as np

from analysis.active_sensing import SensingStudy
from utils.figure_manager import FigureManager
from .revision_figures import Evidence
from .graphical_abstract import create_graphical_abstract


def create_active_sensing_figures(
    study: SensingStudy, experiment: Evidence, output_dir: Path
) -> list[Path]:
    """Keep exact policy surfaces, sampled evidence and graphical summary distinct."""
    paths: list[Path] = []
    registry = FigureManager(str(output_dir / "figure_registry.json"))
    labels = {
        "EFE_sampled": "Sampled\nEFE",
        "Always_inspect": "Always\ninspect",
        "Always_blind": "Always\nblind",
    }
    colors = {
        "EFE_sampled": "#176A9A",
        "Always_inspect": "#AE6B35",
        "Always_blind": "#656565",
    }
    markers = {"EFE_sampled": "o", "Always_inspect": "s", "Always_blind": "^"}
    landscape = study["landscape"]
    r = np.array(sorted({float(row["reliability"]) for row in landscape}))
    c = np.array(sorted({float(row["safe_logit"]) for row in landscape}))
    delta = (
        np.array([float(row["G_inspect"]) - float(row["G_blind"]) for row in landscape])
        .reshape(len(r), len(c))
        .T
    )
    probabilities = (
        np.array([float(row["inspect_probability"]) for row in landscape])
        .reshape(len(r), len(c))
        .T
    )
    with plt.rc_context(PUBLICATION_STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(8.5, 5.6), layout="constrained")
        for axis, values, cmap, title, barlabel, limits in (
            (
                axes[0],
                delta,
                "RdBu_r",
                "a  Inspect − blind EFE",
                "G(inspect) − G(blind), nats",
                {"vmin": -0.8, "vmax": 0.8},
            ),
            (
                axes[1],
                probabilities,
                "viridis",
                "b  Inspection probability",
                "P(inspect)",
                {"vmin": 0, "vmax": 1},
            ),
        ):
            mesh = axis.pcolormesh(r, c, values, shading="nearest", cmap=cmap, **limits)
            contour = axis.contour(
                r, c, delta, levels=[0], colors="white", linewidths=1.8
            )
            contour.set_path_effects(
                [effects.Stroke(linewidth=3.2, foreground="#23333D"), effects.Normal()]
            )
            axis.scatter(
                [0.85],
                [0.15],
                marker="x",
                s=45,
                color="black",
                label="Simulated design",
            )
            axis.set(
                title=title,
                xlabel="Observation reliability",
                ylabel="Blind-outcome logit",
                xlim=(0.5, 1),
                ylim=(0, 0.8),
            )
            fig.colorbar(mesh, ax=axis, label=barlabel, shrink=0.8)
        fig.supxlabel(
            "Outlined contour: equal EFE and 50% inspection probability.\nNegative EFE difference favors inspection. Cross: retained study.",
            fontsize=12,
        )
        for ext in ("png", "pdf", "svg"):
            path = output_dir / f"active_sensing_landscape.{ext}"
            save_publication_figure(fig, path)
            paths.append(path)
        plt.close(fig)
        fig, axes = plt.subplots(2, 2, figsize=(8.5, 8.0), layout="constrained")
        for axis, metric, title in zip(
            axes.flat,
            ("accuracy", "brier", "log_loss", "mean_inspections"),
            (
                "a  Context accuracy",
                "b  Brier loss",
                "c  Log loss (nats)",
                "d  Inspections / trial",
            ),
        ):
            for index, (strategy, label) in enumerate(labels.items()):
                values = [
                    float(row[metric])
                    for row in study["seed_metrics"]
                    if row["strategy"] == strategy
                ]
                estimate = next(
                    row
                    for row in study["estimates"]
                    if row["strategy"] == strategy and row["metric"] == metric
                )
                axis.scatter(
                    np.full(len(values), index) + np.linspace(-0.08, 0.08, len(values)),
                    values,
                    s=15,
                    marker=markers[strategy],
                    color=colors[strategy],
                    alpha=0.45,
                )
                axis.errorbar(
                    index,
                    estimate["mean"],
                    yerr=[
                        [float(estimate["mean"]) - float(estimate["lower"])],
                        [float(estimate["upper"]) - float(estimate["mean"])],
                    ],
                    fmt="none",
                    ecolor="#23333D",
                    capsize=4,
                    elinewidth=1.5,
                )
                axis.scatter(
                    index,
                    estimate["mean"],
                    marker=markers[strategy],
                    s=38,
                    color=colors[strategy],
                    zorder=4,
                )
                axis.scatter(
                    index + 0.19,
                    estimate["exact_expectation"],
                    marker="D",
                    s=23,
                    facecolors="none",
                    edgecolors="black",
                    zorder=4,
                )
            axis.set(title=title, xticks=range(3), xticklabels=list(labels.values()))
            if metric == "accuracy":
                axis.yaxis.set_major_formatter(PercentFormatter(xmax=1))
                axis.set_ylabel("Correct trials (%)")
            elif metric == "mean_inspections":
                axis.set_ylabel("Inspections / trial")
            else:
                axis.set_ylabel(
                    "Loss / trial" + (" (nats)" if metric == "log_loss" else "")
                )
            axis.grid(axis="y", alpha=0.15)
        fig.supxlabel(
            "Small symbols: seed means. Capped bars: marginal 95% intervals.\nOpen diamonds: exact expectations. EFE = expected free energy.",
            fontsize=12,
        )
        for ext in ("png", "pdf", "svg"):
            path = output_dir / f"active_sensing_outcomes.{ext}"
            save_publication_figure(fig, path)
            paths.append(path)
        plt.close(fig)
        paths.extend(create_graphical_abstract(study, experiment, output_dir))
    for name, caption, alt in (
        (
            "active_sensing_landscape",
            "Exact GNN active-sensing policy landscape.",
            "Two heatmaps show inspection-minus-blind normalized expected free energy and inspection probability across reliability and preference logits. Negative score differences favor inspection. The outlined contour marks equal scores and inspection probability one half; a cross identifies the retained sampled design. These are exact GNN evaluations, not measured performance.",
        ),
        (
            "active_sensing_outcomes",
            "Held-out action-task outcomes with exact reference expectations.",
            "Four panels compare sampled expected-free-energy policies with always-inspect and always-blind baselines on accuracy, proper losses and inspection counts. Strategy-specific small symbols are independent seed means, capped dark bars give marginal seed intervals and displaced open diamonds show exact expectations. The three strategies share the same generated trials.",
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
