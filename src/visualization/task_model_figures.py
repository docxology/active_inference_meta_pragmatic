"""Diagrams derived from the retained sensor design and actual imported GNN."""

from pathlib import Path

import matplotlib.pyplot as plt
from .publication_style import PUBLICATION_STYLE, save_publication_figure
import numpy as np

from analysis.active_sensing import active_sensing_model
from analysis.experiments import ExperimentConfig
from core.gnn import sensor_model
from utils.figure_manager import FigureManager
from .conceptual_figures import draw_diagram_box, save_diagram


def create_executed_model_diagram(
    config: ExperimentConfig, output_dir: Path
) -> list[Path]:
    """Derive sensor labels and action edges from the retained design and real GNN."""
    config.validate()
    imported = active_sensing_model()
    model = imported.model
    sensors = [sensor_model(r) for r in config.sensor_reliabilities]
    output_dir.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(PUBLICATION_STYLE):
        fig, axes = plt.subplots(2, 1, figsize=(8.5, 9.0), layout="constrained")
        for axis in axes:
            axis.set(xlim=(0, 1), ylim=(0, 1))
            axis.axis("off")
        left, right = axes
        left.set_title(
            "a  Sensor study: reliability and evidence acquisition",
            weight="bold",
            fontsize=12,
        )
        draw_diagram_box(left, 0.27, 0.77, 0.46, 0.12, "#E5EDF4")
        left.text(
            0.50,
            0.83,
            "Hidden context 0 or 1\nUniform prior; fixed within trial",
            ha="center",
            va="center",
            fontsize=12,
        )
        for index, sensor in enumerate(sensors):
            reliability = sensor.model.A[0, 0]
            x = 0.055 + 0.19 * index
            left.annotate(
                "",
                (x + 0.065, 0.57),
                (0.50, 0.77),
                arrowprops={"arrowstyle": "->", "color": "#78909C", "lw": 1},
            )
            draw_diagram_box(left, x, 0.43, 0.13, 0.13, "#DFF0EE")
            left.text(
                x + 0.065,
                0.495,
                f"Sensor {index + 1}\n{100 * reliability:.0f}% correct",
                ha="center",
                va="center",
                fontsize=12,
            )
        left.plot([0.055, 0.565], [0.395, 0.395], color="#78909C", lw=1.2)
        left.plot([0.625, 0.945], [0.395, 0.395], color="#916133", lw=1.2)
        left.text(
            0.31,
            0.32,
            "Shared initial evidence\n(sensors 1–3)",
            ha="center",
            va="center",
            fontsize=12,
        )
        left.text(
            0.79,
            0.32,
            "Fourth / fifth:\nfixed budget or\nconfidence-triggered",
            ha="center",
            fontsize=12,
            color="#916133",
            va="center",
        )
        draw_diagram_box(left, 0.04, 0.09, 0.92, 0.14, "#F4F5F6")
        left.text(
            0.50,
            0.16,
            f"Learned reliability: {config.n_training} separate labeled training trials\nFit likelihoods → freeze → score held-out forecasts",
            ha="center",
            va="center",
            fontsize=12,
        )
        right.set_title(
            "b  Action study: interventions change observation mode",
            weight="bold",
            fontsize=11,
        )
        positions = ((0.25, 0.77), (0.75, 0.77), (0.25, 0.43), (0.75, 0.43))
        for state, (x, y) in enumerate(positions):
            draw_diagram_box(
                right,
                x - 0.18,
                y - 0.075,
                0.36,
                0.15,
                "#E5EDF4" if state < 2 else "#DFF0EE",
            )
            right.text(
                x,
                y,
                f"s{state}: context {state % 2}\n"
                + ("Blind → null outcome" if state < 2 else "Informative observation"),
                ha="center",
                va="center",
                fontsize=12,
            )
        for action, color, label in (
            (0, "#916133", "blind"),
            (1, "#245D87", "inspect"),
        ):
            for current in range(4):
                target = int(np.argmax(model.B[:, current, action]))
                if current != target:
                    x, y = positions[current]
                    end_x, end_y = positions[target]
                    offset = -0.045 if action == 0 else 0.045
                    right.annotate(
                        "",
                        (end_x + offset, end_y + (0.09 if target >= 2 else -0.09)),
                        (x + offset, y + (-0.09 if current < 2 else 0.09)),
                        arrowprops={"arrowstyle": "->", "color": color, "lw": 1.7},
                    )
            right.text(
                0.50, 0.65 - 0.055 * action, label, color=color, ha="center", fontsize=9
            )
        right.text(
            0.50,
            0.27,
            f"Inspection reports the context with r = {model.A[1, 2]:.2f}\nEach action sets mode from either row; context is preserved",
            ha="center",
            fontsize=12,
            va="center",
        )
        right.text(
            0.50,
            0.145,
            f"Initial prior: {model.D.tolist()}\nPreference logits: {model.C.tolist()}",
            ha="center",
            va="center",
            fontsize=12,
        )
        fig.supxlabel(
            "A: observation likelihoods · B: action-dependent state transitions\nC: preference logits · D: initial beliefs · External labels score forecasts.",
            fontsize=12,
        )
        paths = save_diagram(fig, output_dir, "executed_models")
    FigureManager(str(output_dir / "figure_registry.json")).register_figure(
        "executed_models.png",
        "The two retained synthetic models and their evaluation boundary.",
        label="fig:executed_models",
        section="background",
        generated_by="scripts/07_analysis_pipeline.py",
        parameters={
            "action_model_sha256": imported.specification_sha256,
            "sensor_model_sha256": [s.specification_sha256 for s in sensors],
        },
        alt_text="A binary context feeds five potential sensor reports; percentage labels give the probability of reporting the true context. Brackets distinguish shared initial evidence from optional additional observations. A separate panel shows the four imported action states and mode-changing transitions that preserve context. Likelihoods, dynamics, preferences, prior beliefs and external scoring are explicitly distinguished.",
    )
    return paths
