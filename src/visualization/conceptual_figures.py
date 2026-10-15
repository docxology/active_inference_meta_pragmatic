"""Conceptual quadrant orientation and shared diagram drawing primitives."""

from pathlib import Path

import matplotlib.pyplot as plt
from .publication_style import PUBLICATION_STYLE, save_publication_figure
from .inquiry_roles import INQUIRY_ROLES
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

from utils.figure_manager import FigureManager


def draw_diagram_box(
    axis: Axes, x: float, y: float, width: float, height: float, color: str
) -> None:
    axis.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.012",
            facecolor=color,
            edgecolor="#8C9BA1",
            linewidth=0.9,
        )
    )


def save_diagram(fig: Figure, output_dir: Path, name: str) -> list[Path]:
    paths = []
    for extension in ("png", "pdf", "svg"):
        path = output_dir / (name + "." + extension)
        save_publication_figure(fig, path)
        paths.append(path)
    plt.close(fig)
    return paths


def create_quadrant_orientation(output_dir: Path) -> list[Path]:
    """Show relational roles, their two axes and a distinct failure for each role."""
    output_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(PUBLICATION_STYLE):
        fig, axis = plt.subplots(figsize=(8.5, 7.0), layout="constrained")
        axis.set(xlim=(-0.15, 1.02), ylim=(-0.08, 1.08))
        axis.axis("off")
        cells = (
            (
                0.02,
                0.52,
                "What should be believed\nand done?",
                "Failure: misspecified likelihood",
            ),
            (
                0.53,
                0.52,
                "Which source model\nis warranted?",
                "Failure: unreliable metadata",
            ),
            (
                0.02,
                0.06,
                "Is more evidence\nworth its cost?",
                "Failure: confident early stopping",
            ),
            (
                0.53,
                0.06,
                "What warrants revising\nthese commitments?",
                "Failure: unjustified model change",
            ),
        )
        for role, (x, y, question, failure) in zip(INQUIRY_ROLES, cells):
            draw_diagram_box(axis, x, y, 0.45, 0.37, role.fill)
            axis.text(
                x + 0.225,
                y + 0.315,
                role.code + "  " + role.title,
                ha="center",
                fontsize=14,
                weight="bold",
                color=role.ink,
            )
            axis.text(
                x + 0.225,
                y + 0.22,
                question,
                ha="center",
                fontsize=12,
                style="italic",
            )
            axis.text(x + 0.225, y + 0.12, role.operation, ha="center", fontsize=12)
            axis.text(
                x + 0.225, y + 0.025, failure, ha="center", fontsize=12, color="#535D63"
            )
        axis.text(
            0.245, 1.015, "TASK EVIDENCE", ha="center", weight="bold", fontsize=12
        )
        axis.text(
            0.755,
            1.015,
            "EVIDENCE ABOUT ITS SOURCE",
            ha="center",
            weight="bold",
            fontsize=12,
        )
        axis.text(
            -0.10,
            0.705,
            "INFERENCE IN A MODEL",
            rotation=90,
            va="center",
            ha="center",
            fontsize=12,
            weight="bold",
        )
        axis.text(
            -0.10,
            0.245,
            "REGULATION OF INQUIRY",
            rotation=90,
            va="center",
            ha="center",
            fontsize=12,
            weight="bold",
        )
        axis.text(
            0.50,
            0.475,
            "",
            ha="center",
            fontsize=12,
            color="#53676F",
        )
        axis.text(
            0.50,
            -0.035,
            "Roles may overlap. This map does not establish a hierarchy\nof cognitive faculties or guarantee improved performance.",
            ha="center",
            fontsize=12,
        )
        paths = save_diagram(fig, output_dir, "quadrant_orientation")
    FigureManager(str(output_dir / "figure_registry.json")).register_figure(
        "quadrant_orientation.png",
        "Four questions in a meta-pragmatic practice of active inference.",
        label="fig:quadrant_orientation",
        section="abstract",
        generated_by="scripts/07_analysis_pipeline.py",
        alt_text="A conceptual two-by-two map labels all four roles in full: Q1 infer and act, Q2 contextualize evidence, Q3 monitor inquiry, and Q4 evaluate and revise. Task versus source evidence forms the columns; inference versus regulation forms the rows. Each role has a question, concrete operation and failure case. The responsibilities overlap.",
    )
    return paths
