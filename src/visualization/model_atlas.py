"""Matrix atlas of all three packaged models, using actual upstream GNN imports."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from core.gnn import MODEL_DIRECTORY, load_gnn_model
from utils.figure_manager import FigureManager
from .publication_style import PUBLICATION_STYLE, save_publication_figure


def create_model_atlas(output_dir: Path) -> list[Path]:
    """Display imported A/B matrices and explicit preference/prior vectors."""
    output_dir.mkdir(parents=True, exist_ok=True)
    models = [
        load_gnn_model(MODEL_DIRECTORY / name)
        for name in ("binary_sensor.md", "control_agent.md", "active_sensing.md")
    ]
    with plt.rc_context(PUBLICATION_STYLE):
        fig = plt.figure(figsize=(8.5, 8.8), layout="constrained")
        grid = fig.add_gridspec(6, 3, height_ratios=(1, 0.23, 1, 0.23, 1.3, 0.23))
        for row, (imported, title) in enumerate(
            zip(
                models,
                (
                    "Binary sensor · one action",
                    "Stay / switch · two actions",
                    "Active sensing · two actions",
                ),
            )
        ):
            model = imported.model
            tensors = (model.A, model.B[:, :, 0], model.B[:, :, -1])
            for column, (tensor, label) in enumerate(
                zip(
                    tensors,
                    (
                        "A · likelihood",
                        "B · a0: " + ("blind" if row == 2 else "stay"),
                        "B · "
                        + (
                            "a1: inspect"
                            if row == 2
                            else "a1: switch"
                            if row == 1
                            else "a0: repeated"
                        ),
                    ),
                )
            ):
                axis = fig.add_subplot(grid[2 * row, column])
                axis.imshow(tensor, cmap="Blues", vmin=0, vmax=1, aspect="auto")
                for index, value in np.ndenumerate(tensor):
                    axis.text(
                        index[1],
                        index[0],
                        f"{value:g}",
                        ha="center",
                        va="center",
                        fontsize=14,
                        color="white" if value > 0.65 else "#192C38",
                    )
                axis.set_title(label, fontsize=14)
                axis.set_xticks(range(tensor.shape[1]))
                axis.set_yticks(range(tensor.shape[0]))
                axis.set_xticks(np.arange(tensor.shape[1] + 1) - 0.5, minor=True)
                axis.set_yticks(np.arange(tensor.shape[0] + 1) - 0.5, minor=True)
                axis.grid(which="minor", color="#B7C4CD", linewidth=0.5)
                axis.tick_params(which="minor", length=0)
                axis.set_xlabel(
                    "Hidden state" if column == 0 else "State before action"
                )
                if column == 0:
                    axis.set_ylabel("Outcome")
                else:
                    axis.set_ylabel("State after action")
            note = fig.add_subplot(grid[2 * row + 1, :])
            note.axis("off")
            preference = ", ".join(f"{v:g}" for v in model.C)
            prior = ", ".join(f"{v:g}" for v in model.D)
            note.text(0.5, 0.6, title, ha="center", weight="bold", fontsize=14)
            note.text(
                0.5,
                -0.1,
                f"C logits = [{preference}]    D probabilities = [{prior}]",
                ha="center",
                fontsize=13,
            )
        fig.supxlabel(
            "Matrices show probabilities from 0 (white) to 1 (dark blue).\nThe binary sensor’s single B slice is repeated; C is not a probability.",
            fontsize=12,
        )
        paths = []
        for extension in ("png", "pdf", "svg"):
            path = output_dir / ("canonical_model_atlas." + extension)
            save_publication_figure(fig, path)
            paths.append(path)
        plt.close(fig)
    FigureManager(str(output_dir / "figure_registry.json")).register_figure(
        "canonical_model_atlas.png",
        "Imported GNN likelihoods and dynamics, with explicit preference and prior vectors.",
        label="fig:canonical_model_atlas",
        section="appendix",
        generated_by="scripts/07_analysis_pipeline.py",
        parameters={"specification_sha256": [m.specification_sha256 for m in models]},
        alt_text="Three imported GNN models display likelihood A and two action-specific B slices, with cell boundaries and every probability printed. Columns in A are hidden states; B maps before-action columns to after-action rows. White marks zero support and dark blue probability one. Preference logits and prior probabilities are printed below. The single binary transition slice is repeated.",
    )
    return paths
