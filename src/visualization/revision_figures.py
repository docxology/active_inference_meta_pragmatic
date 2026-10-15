"""Conceptual diagrams and descriptive plots tied to the retained trial table."""

from pathlib import Path
from typing import TypedDict

import matplotlib.pyplot as plt
from .publication_style import PUBLICATION_STYLE, save_publication_figure
from .inquiry_roles import INQUIRY_ROLES
from matplotlib.patches import FancyBboxPatch

from utils.figure_manager import FigureManager


class Interval(TypedDict):
    mean: float
    lower_bound: float
    upper_bound: float


class Evidence(TypedDict):
    trials: list[dict[str, float]]
    summary: dict[str, dict[str, Interval]]


def create_revision_figures(experiment: Evidence, output_dir: Path) -> list[Path]:
    """Keep empirical resource/calibration plots separate from the conceptual map."""
    from .resource_calibration import create_resource_calibration

    paths = create_resource_calibration(experiment, output_dir)
    registry = FigureManager(str(output_dir / "figure_registry.json"))
    with plt.rc_context(PUBLICATION_STYLE):
        fig, axes = plt.subplots(2, 1, figsize=(8.5, 9.0), layout="constrained")
        for axis in axes:
            axis.set(xlim=(0, 1), ylim=(0, 1))
            axis.axis("off")
        cells = [
            (
                0.05,
                0.52,
                INQUIRY_ROLES[0].code + " | " + INQUIRY_ROLES[0].title,
                "Update state beliefs\nEvaluate a declared policy",
                "#E8ECEF",
            ),
            (
                0.53,
                0.52,
                INQUIRY_ROLES[1].code + " | " + INQUIRY_ROLES[1].title,
                "Condition on reliability\nCheck source assumptions",
                "#DDEDF0",
            ),
            (
                0.05,
                0.07,
                INQUIRY_ROLES[2].code + " | " + INQUIRY_ROLES[2].title,
                "Evaluate uncertainty\nAcquire bounded evidence",
                "#F3E7D9",
            ),
            (
                0.53,
                0.07,
                INQUIRY_ROLES[3].code + " | " + INQUIRY_ROLES[3].title,
                "Fit on separate training\nEvaluate before adoption",
                INQUIRY_ROLES[3].fill,
            ),
        ]
        for x, y, title, body, color in cells:
            axes[0].add_patch(
                FancyBboxPatch(
                    (x, y),
                    0.40,
                    0.34,
                    boxstyle="round,pad=0.02",
                    facecolor=color,
                    edgecolor="#67757A",
                    lw=0.8,
                )
            )
            axes[0].text(
                x + 0.2, y + 0.24, title, ha="center", weight="bold", fontsize=13
            )
            axes[0].text(x + 0.2, y + 0.12, body, ha="center", va="center", fontsize=12)
        axes[0].text(0.25, 0.93, "Task evidence", ha="center", fontsize=12)
        axes[0].text(0.73, 0.93, "Evidence about evidence", ha="center", fontsize=12)
        axes[0].text(
            0.5,
            0.01,
            "Roles may overlap; the taxonomy is conceptual.",
            ha="center",
            fontsize=12,
        )
        for index, (title, body) in enumerate(
            [
                ("Specify", "GNN source + tensor conventions"),
                ("Execute", "Exact Bayesian inference + policy scores"),
                ("Evaluate", "Held-out scores + resources + adverse controls"),
                (
                    "Criticize and justify",
                    "Explicit adoption criteria + accountable revision",
                ),
            ]
        ):
            y = 0.76 - index * 0.23
            axes[1].add_patch(
                FancyBboxPatch(
                    (0.12, y),
                    0.76,
                    0.14,
                    boxstyle="round,pad=0.015",
                    facecolor="#F3F1E9",
                    edgecolor="#67757A",
                    lw=0.8,
                )
            )
            axes[1].text(0.5, y + 0.095, title, ha="center", weight="bold")
            axes[1].text(0.5, y + 0.035, body, ha="center", fontsize=12)
            if index < 3:
                axes[1].annotate(
                    "",
                    xy=(0.5, y - 0.065),
                    xytext=(0.5, y - 0.02),
                    arrowprops={"arrowstyle": "->", "color": "#67757A"},
                )
        axes[0].set_title(
            "a  Four overlapping responsibilities", loc="left", weight="bold"
        )
        axes[1].set_title(
            "b  From specification to justified revision", loc="left", weight="bold"
        )
        for extension in ("png", "pdf", "svg"):
            path = output_dir / f"model_revision_map.{extension}"
            save_publication_figure(fig, path)
            paths.append(path)
        plt.close(fig)
        registry.register_figure(
            "model_revision_map.png",
            "Conceptual taxonomy and executable revision cycle, not an empirical cognitive architecture.",
            label="fig:model_revision_map",
            section="quadrant_model",
            generated_by="scripts/07_analysis_pipeline.py",
            alt_text="Four boxes repeat the full inquiry-role names and concrete operations. Below, arrows connect specification, exact execution, external evaluation and justified revision. These are overlapping conceptual responsibilities and a proposed procedural workflow, not a causal neural diagram or a demonstration of autonomous revision.",
        )
    return paths
