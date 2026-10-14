#!/usr/bin/env python3
"""Generate Cognitive Security Figures.

This script creates visualizations for the cognitive security analysis:
- Attack surface diagram across quadrants
- Defense layer architecture
- Anomaly detection threshold plot

IMPORTANT: This script follows the thin orchestrator pattern - all business
logic is in src/ modules, this script only orchestrates the workflow.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Ensure src/ is on path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import src/ modules
from framework.cognitive_security import CognitiveSecurityAnalyzer
from utils.figure_manager import FigureManager
from utils.logging import get_logger
from visualization import VisualizationEngine

logger = get_logger(__name__)


def main() -> None:
    """Generate cognitive security visualizations."""
    logger.info("Generating cognitive security figures...")

    # Setup output directory
    output_dir = project_root / "output" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize components
    analyzer = CognitiveSecurityAnalyzer()
    viz_engine = VisualizationEngine(output_dir=str(output_dir))
    figure_manager = FigureManager(str(output_dir / "figure_registry.json"))

    # Generate figures
    create_attack_surface_diagram(analyzer, viz_engine, figure_manager)
    create_defense_architecture_diagram(analyzer, viz_engine, figure_manager)
    create_anomaly_detection_plot(analyzer, viz_engine, figure_manager)

    logger.info("Cognitive security figures completed")


def create_attack_surface_diagram(
    analyzer: CognitiveSecurityAnalyzer,
    viz_engine: VisualizationEngine,
    figure_manager: FigureManager,
) -> None:
    """Create attack surface comparison across quadrants with attack budget."""
    fig, ax = viz_engine.create_figure(figsize=(12, 7))

    # Analyze all quadrants
    quadrants = []
    vulnerability_scores = []
    meta_exposures = []
    n_vectors = []

    for q in range(1, 5):
        result = analyzer.analyze_attack_surface(q)
        quadrants.append(f"Q{q}\n{result['quadrant_name']}")
        vulnerability_scores.append(result["vulnerability_score"])
        meta_exposures.append(result["meta_level_exposure"])
        n_vectors.append(len(result["attack_vectors"]))

    # Attack budget: resource cost required by attacker per quadrant
    attack_budget = [0.3, 0.15, 0.22, 0.4]

    x = np.arange(len(quadrants))
    width = 0.25

    bars1 = ax.bar(
        x - width,
        vulnerability_scores,
        width,
        label="Vulnerability Score",
        color="#E74C3C",
        alpha=0.8,
    )
    bars2 = ax.bar(
        x,
        meta_exposures,
        width,
        label="Meta-Level Exposure",
        color="#3498DB",
        alpha=0.8,
    )
    bars3 = ax.bar(
        x + width,
        attack_budget,
        width,
        label="Attack Budget",
        color="#C0392B",
        alpha=0.7,
    )

    ax.set_xlabel("Quadrant")
    ax.set_ylabel("Score (0-1)")
    ax.set_title("Cognitive Security: Attack Surface by Quadrant")
    ax.set_xticks(x)
    ax.set_xticklabels(quadrants, fontsize=10, rotation=30, ha="right")
    ax.legend(loc="upper left")
    ax.set_ylim(0, 1.2)

    # Detection threshold reference line
    ax.axhline(
        y=0.5,
        color="#7F8C8D",
        linestyle="--",
        linewidth=1.5,
        label="Detection Threshold (0.5)",
        alpha=0.8,
    )
    ax.text(3.6, 0.52, "Detection\nThreshold", fontsize=8, color="#7F8C8D", va="bottom")

    # Add attack vector counts as text
    for i, n in enumerate(n_vectors):
        top = max(vulnerability_scores[i], meta_exposures[i], attack_budget[i])
        ax.text(i, top + 0.06, f"{n} vectors", ha="center", fontsize=9, style="italic")

    plt.tight_layout()
    saved = viz_engine.save_figure(fig, "cognitive_security_attack_surface")
    logger.info(f"Saved attack surface diagram: {saved['png']}")
    print(saved["png"])

    figure_manager.register_figure(
        filename="cognitive_security_attack_surface.png",
        caption="Attack surface analysis across the four quadrants of the meta-pragmatic "
        "framework, showing vulnerability score, meta-level exposure, and "
        "attack budget required per quadrant.",
        section="security_implications",
        generated_by="05_generate_security_figures.py",
    )
    plt.close(fig)


def create_defense_architecture_diagram(
    analyzer: CognitiveSecurityAnalyzer,
    viz_engine: VisualizationEngine,
    figure_manager: FigureManager,
) -> None:
    """Create defense layer architecture diagram."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "Defense Layer Architecture by Quadrant", fontsize=16, fontweight="bold", y=0.98
    )

    colors = ["#E8F4FD", "#FFF3E0", "#F3E5F5", "#E8F5E8"]

    for q in range(1, 5):
        result = analyzer.analyze_attack_surface(q)
        row, col = divmod(q - 1, 2)
        ax = axes[row, col]

        # Draw defense layers as horizontal bars
        defenses = result["defense_mechanisms"]
        y_pos = np.arange(len(defenses))

        # Color intensity based on layer depth
        layer_colors = [
            plt.cm.Blues(0.3 + 0.7 * i / len(defenses)) for i in range(len(defenses))
        ]

        ax.barh(y_pos, [1.0] * len(defenses), color=layer_colors, edgecolor="gray")
        ax.set_yticks(y_pos)
        ax.set_yticklabels([d[:50] for d in defenses], fontsize=8)
        ax.set_xlim(0, 1.2)
        ax.set_xticks([])
        ax.set_title(
            f"Q{q}: {result['quadrant_name']}\n"
            f"(vulnerability: {result['vulnerability_score']:.2f})",
            fontsize=11,
            fontweight="bold",
        )
        ax.set_facecolor(colors[q - 1])

    plt.tight_layout()
    saved = viz_engine.save_figure(fig, "cognitive_security_defense_layers")
    logger.info(f"Saved defense architecture: {saved['png']}")
    print(saved["png"])

    figure_manager.register_figure(
        filename="cognitive_security_defense_layers.png",
        caption="Defense layer architecture across quadrants showing available protective mechanisms",
        section="security_implications",
        generated_by="05_generate_security_figures.py",
    )
    plt.close(fig)


def create_anomaly_detection_plot(
    analyzer: CognitiveSecurityAnalyzer,
    viz_engine: VisualizationEngine,
    figure_manager: FigureManager,
) -> None:
    """Create anomaly detection threshold visualization with enhanced annotations."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ── Left panel: KL divergence for varying belief perturbations ──
    baseline = np.array([1.0 / 3, 1.0 / 3, 1.0 / 3])
    alphas = np.linspace(0.01, 0.99, 50)
    kl_values = []
    severities = []

    for alpha in alphas:
        perturbed = np.array([alpha, (1 - alpha) / 2, (1 - alpha) / 2])
        result = analyzer.detect_anomaly(perturbed, baseline, threshold=0.1)
        kl_values.append(result["kl_divergence"])
        severities.append(result["severity"])

    severity_colors = {
        "low": "#27AE60",
        "medium": "#F39C12",
        "high": "#E74C3C",
        "critical": "#8E44AD",
    }
    point_colors = [severity_colors[s] for s in severities]

    ax1.scatter(alphas, kl_values, c=point_colors, s=20, alpha=0.8, zorder=3)
    ax1.axhline(
        y=0.1,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label="Detection threshold (0.1)",
    )

    # Explicit colour legend for severity levels
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#27AE60",
            markersize=8,
            label="Normal (low KL)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#F39C12",
            markersize=8,
            label="Attacked (medium KL)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#E74C3C",
            markersize=8,
            label="High severity",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#8E44AD",
            markersize=8,
            label="Critical severity",
        ),
        Line2D([0], [0], color="red", linestyle="--", label="Detection threshold"),
    ]
    ax1.legend(handles=legend_elements, fontsize=8, loc="upper left")
    ax1.set_xlabel("Belief concentration (\u03b1)")
    ax1.set_ylabel("KL Divergence from uniform baseline")
    ax1.set_title("Anomaly Detection: KL Divergence vs Belief Concentration")

    # ── Right panel: Parameter drift over time ──
    params = {"A": np.eye(3), "D": np.array([1.0 / 3, 1.0 / 3, 1.0 / 3])}
    drift_result = analyzer.simulate_parameter_drift(
        params, noise_level=0.05, steps=100
    )

    threshold_val = drift_result["detection_threshold"]

    # Grey shaded baseline period (steps 0-5)
    ax2.axvspan(0, 5, alpha=0.15, color="grey", label="Baseline period (t=0–5)")

    for name, trajectory in drift_result["drift_trajectory"].items():
        traj_arr = np.array(trajectory)
        ax2.plot(traj_arr, label=f"Matrix {name}", linewidth=1.8)

        # Vertical dashed lines at first crossing of detection threshold
        crossings = np.where(traj_arr > threshold_val)[0]
        if len(crossings) > 0:
            first_cross = crossings[0]
            ax2.axvline(
                x=first_cross, color="#7F8C8D", linestyle=":", linewidth=1.2, alpha=0.7
            )

    ax2.axhline(
        y=threshold_val,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label="Detection threshold",
    )

    # Steady-state detection accuracy annotation
    final_vals = [
        np.array(traj)[-10:].mean()
        for traj in drift_result["drift_trajectory"].values()
    ]
    detected_frac = sum(v > threshold_val for v in final_vals) / len(final_vals)
    ax2.text(
        0.97,
        0.97,
        f"Steady-state\ndetection: {detected_frac:.0%}",
        transform=ax2.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
    )

    ax2.set_xlabel("Time Steps")
    ax2.set_ylabel("Frobenius Norm Drift")
    ax2.set_title("Parameter Drift Simulation")
    ax2.legend(fontsize=8, loc="upper left")

    plt.tight_layout()
    saved = viz_engine.save_figure(fig, "cognitive_security_anomaly_detection")
    logger.info(f"Saved anomaly detection plot: {saved['png']}")
    print(saved["png"])

    figure_manager.register_figure(
        filename="cognitive_security_anomaly_detection.png",
        caption="Anomaly detection thresholds and parameter drift simulation. "
        "Left: KL divergence coloured by severity (Normal=green, "
        "Attacked=orange/red, Critical=purple). "
        "Right: parameter drift with baseline period shaded, "
        "threshold-crossing markers, and steady-state detection rate.",
        section="security_implications",
        generated_by="05_generate_security_figures.py",
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
