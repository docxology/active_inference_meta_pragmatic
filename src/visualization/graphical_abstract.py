"""A scientific graphical abstract connecting situated action and model criticism."""

from pathlib import Path

import matplotlib.pyplot as plt
from .conceptual_figures import draw_diagram_box
from .inquiry_roles import INQUIRY_ROLES
from .publication_style import PUBLICATION_STYLE, save_publication_figure
from analysis.active_sensing import SensingStudy
from .revision_figures import Evidence


def create_graphical_abstract(
    study: SensingStudy, experiment: Evidence, output_dir: Path
) -> list[Path]:
    """Separate a conceptual inquiry loop from two retained numerical demonstrations."""
    output_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(PUBLICATION_STYLE):
        fig = plt.figure(figsize=(8.5, 7.0))
        fig.text(
            0.5,
            0.96,
            "FOUR ROLES IN META-PRAGMATIC INQUIRY",
            ha="center",
            fontsize=18,
            weight="bold",
            color="#183D51",
        )
        fig.text(
            0.5,
            0.915,
            "Q = quadrant; Q1–Q4 name overlapping inquiry roles, not stages.",
            ha="center",
            fontsize=12,
            color="#46545C",
        )
        roles = fig.add_axes((0.025, 0.455, 0.95, 0.415))
        roles.set(xlim=(0, 1), ylim=(0, 1))
        roles.axis("off")
        for role, (x, y) in zip(
            INQUIRY_ROLES, ((0.02, 0.55), (0.525, 0.55), (0.02, 0.04), (0.525, 0.04))
        ):
            draw_diagram_box(roles, x, y, 0.455, 0.40, role.fill)
            roles.text(
                x + 0.2275,
                y + 0.29,
                role.code + "  " + role.title,
                ha="center",
                va="center",
                fontsize=15,
                weight="bold",
                color=role.ink,
            )
            roles.text(
                x + 0.2275,
                y + 0.125,
                role.operation,
                ha="center",
                va="center",
                fontsize=12,
                linespacing=1.4,
            )
        fig.text(
            0.5,
            0.425,
            "GNN = Generalized Notation Notation: executable model specifications.",
            ha="center",
            fontsize=12,
            color="#46545C",
        )
        fig.text(
            0.5,
            0.391,
            "Model execution → evaluated consequences → researcher-led revision",
            ha="center",
            fontsize=12,
            color="#183D51",
        )
        left = fig.add_axes((0.22, 0.18, 0.31, 0.15))
        for y, (name, color, marker) in enumerate(
            (
                ("Q1_fixed", INQUIRY_ROLES[0].ink, "o"),
                ("Q2_metadata", INQUIRY_ROLES[1].ink, "s"),
                ("Q2_misleading", "#93536F", "X"),
            )
        ):
            value = experiment["summary"][name]["accuracy"]
            left.errorbar(
                100 * value["mean"],
                y,
                xerr=[
                    [100 * (value["mean"] - value["lower_bound"])],
                    [100 * (value["upper_bound"] - value["mean"])],
                ],
                fmt=marker,
                color=color,
                ecolor="#202A30",
                capsize=4,
                ms=6,
            )
            left.text(
                100 * value["mean"] + 2.0,
                y,
                f"{100 * value['mean']:.1f}",
                va="center",
                fontsize=12,
                color=color,
            )
        left.set(
            title="a  Evidence can mislead",
            yticks=(0, 1, 2),
            yticklabels=("Fixed", "True metadata", "Misleading"),
            xlabel="Held-out accuracy (%)",
            xlim=(45, 101),
            ylim=(2.6, -0.6),
        )
        left.grid(axis="x", alpha=0.12)
        right = fig.add_axes((0.71, 0.18, 0.25, 0.15))
        probability = next(
            float(row["exact_expectation"])
            for row in study["estimates"]
            if row["strategy"] == "EFE_sampled" and row["metric"] == "mean_inspections"
        )
        for y, (label, value, color) in enumerate(
            (
                ("Blind", 1 - probability, "#8C969C"),
                ("Inspect", probability, "#286389"),
            )
        ):
            right.barh(y, 100 * value, height=0.42, color=color)
            right.text(
                100 * value + 2, y, f"{100 * value:.1f}", va="center", fontsize=12
            )
        right.set(
            title="b  Action selection",
            yticks=(0, 1),
            yticklabels=("Blind", "Inspect"),
            xlabel="Policy probability (%)",
            xlim=(0, 105),
            ylim=(1.7, -0.7),
            xticks=(0, 50, 100),
        )
        right.grid(axis="x", alpha=0.12)
        fig.text(
            0.5,
            0.055,
            "Sensor points: seed means and marginal 95% intervals.",
            ha="center",
            fontsize=12,
        )
        fig.text(
            0.5,
            0.025,
            "Action bars: exact policy from expected free energy. Both tasks are synthetic.",
            ha="center",
            fontsize=12,
            color="#46545C",
        )
        paths = []
        for extension in ("png", "pdf", "svg"):
            path = output_dir / f"scientific_graphical_abstract.{extension}"
            save_publication_figure(fig, path)
            paths.append(path)
        plt.close(fig)
    return paths
