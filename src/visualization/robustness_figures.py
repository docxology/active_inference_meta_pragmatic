from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from .publication_style import PUBLICATION_STYLE, save_publication_figure
import numpy as np

from analysis.model_robustness import RobustnessStudy
from utils.figure_manager import FigureManager


def create_robustness_figure(study: RobustnessStudy, output_dir: Path) -> list[Path]:
    paths: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(PUBLICATION_STYLE):
        fig, axes = plt.subplots(2, 2, figsize=(8.5, 8.0), layout="constrained")
        for axis, metric, title in zip(
            axes.flat[:3],
            ("accuracy", "brier", "log_loss"),
            ("a  Context accuracy ↑", "b  Brier loss ↓", "c  Log loss (nats) ↓"),
        ):
            for strategy, label, color in (
                ("EFE_sampled", "Sampled EFE", "#176A9A"),
                ("Always_inspect", "Always inspect", "#AE6B35"),
                ("Always_blind", "Always blind", "#656565"),
            ):
                rows = [row for row in study["metrics"] if row["strategy"] == strategy]
                axis.plot(
                    [row["world_reliability"] for row in rows],
                    [row[metric] for row in rows],
                    label=label,
                    color=color,
                    linewidth=2,
                    linestyle={
                        "EFE_sampled": "-",
                        "Always_inspect": "--",
                        "Always_blind": ":",
                    }[strategy],
                )
            axis.axvline(
                0.85, color="#222222", linestyle=":", label="Agent assumes 0.85"
            )
            axis.set(title=title, xlabel="Actual world reliability", xlim=(0.5, 1))
            if metric == "accuracy":
                axis.yaxis.set_major_formatter(PercentFormatter(xmax=1))
                axis.set_ylabel("Correct trials (%)")
            else:
                axis.set_ylabel(
                    "Loss / trial" + (" (nats)" if metric == "log_loss" else "")
                )
            axis.grid(alpha=0.15)
        axes[0, 0].legend(fontsize=12)
        axis = axes[1, 1]
        axis.plot(
            [0, 1], [0, 1], color="#999999", linestyle="--", label="Perfect calibration"
        )
        for r, color, marker, style in (
            (0.5, "#AE6B35", "s", "--"),
            (0.85, "#176A9A", "o", "-"),
            (1.0, "#527544", "^", "-."),
        ):
            cells = [
                row
                for row in study["calibration"]
                if row["strategy"] == "Always_inspect"
                and np.isclose(float(row["world_reliability"]), r)
            ]
            cells.sort(key=lambda row: float(row["forecast"]))
            axis.plot(
                [row["forecast"] for row in cells],
                [row["true_rate"] for row in cells],
                marker=marker,
                linestyle=style,
                color=color,
                label=f"World r = {r:g}",
            )
        axis.set(
            title="d  Exact inspection calibration",
            xlabel="Agent P(context = 1)",
            ylabel="World P(context = 1 | outcome)",
            xlim=(-0.03, 1.03),
            ylim=(-0.03, 1.03),
        )
        axis.legend(fontsize=12)
        fig.supxlabel(
            "Fixed agent: reliability 0.85, preferences and policy precision unchanged.\nCurves: exact world expectations; no sampling intervals.",
            fontsize=12,
        )
        for extension in ("png", "pdf", "svg"):
            path = output_dir / ("model_robustness." + extension)
            save_publication_figure(fig, path)
            paths.append(path)
        plt.close(fig)
    FigureManager(str(output_dir / "figure_registry.json")).register_figure(
        "model_robustness.png",
        "Exact world–agent reliability mismatch and calibration.",
        label="fig:model_robustness",
        section="discussion",
        generated_by="scripts/07_analysis_pipeline.py",
        alt_text="Three exact score panels vary actual reliability while the agent assumes 0.85; arrows indicate favorable score directions and a vertical reference marks the matched world. Distinct line styles identify policies. A fourth panel uses different symbols and line styles for exact calibration at three world reliabilities. The model remains fixed throughout.",
    )
    return paths
