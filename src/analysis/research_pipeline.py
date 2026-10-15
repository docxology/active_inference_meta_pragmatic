"""Standalone research pipeline with explicit dependencies and artifact provenance."""

from __future__ import annotations
import csv
import json
from pathlib import Path

from .experiments import (
    ExperimentConfig,
    run_quadrant_experiment,
    mathematical_checks,
    reliability_sensitivity,
)
from visualization.research_figures import create_research_figures
from utils.provenance import write_manifest
from utils.manuscript import render_manuscript, validate_manuscript
from utils.exceptions import ValidationError
import numpy as np
from .diagnostics import prediction_diagnostics, stopping_sensitivity
from visualization.diagnostic_figures import create_diagnostic_figures
from .active_sensing import run_active_sensing
from visualization.active_sensing_figures import create_active_sensing_figures
from .model_robustness import reliability_robustness
from visualization.robustness_figures import create_robustness_figure
from visualization.conceptual_figures import create_quadrant_orientation
from visualization.task_model_figures import create_executed_model_diagram
from visualization.model_atlas import create_model_atlas

STAGES = {
    1: "Mathematical checks",
    2: "Held-out experiments",
    3: "Figures and sensitivity",
    4: "Data export",
    5: "Manuscript validation and rendering",
    6: "Provenance manifest",
}


def _csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(
    project_root: Path,
    output_dir: Path,
    config: ExperimentConfig = ExperimentConfig(),
    stages: list[int] | None = None,
) -> dict:
    """Run requested stages with preceding dependencies; fail on invalid results."""
    config.validate()
    stages = stages or list(STAGES)
    if any(stage not in STAGES for stage in stages):
        raise ValidationError("Stage numbers must be 1-6")
    # Later stages require the evidence produced by earlier stages.
    executed = list(range(1, max(stages) + 1))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checks = mathematical_checks()
    if not checks["passed"]:
        raise ValidationError("Mathematical identity checks failed")
    result = {"stages_completed": executed, "mathematical_checks": checks}
    if max(stages) >= 2:
        experiment = run_quadrant_experiment(config)
        result["experiment"] = {
            k: v for k, v in experiment.items() if k not in ("trials", "replicates")
        }
    if max(stages) >= 3:
        create_quadrant_orientation(output_dir / "figures")
        create_executed_model_diagram(config, output_dir / "figures")
        create_model_atlas(output_dir / "figures")
        sensitivity = reliability_sensitivity()
        create_research_figures(experiment, sensitivity, output_dir / "figures")
        trial_rows = experiment["trials"]
        states = np.array([row["state"] for row in trial_rows])
        seeds = np.array([row["seed"] for row in trial_rows])
        predictions = {
            name: np.array([row[name + "_p1"] for row in trial_rows])
            for name in experiment["summary"]
        }
        costs = {
            name: np.array(
                [
                    row["Q3_observations"]
                    if name == "Q3_adaptive"
                    else 4
                    if name == "Fixed_four"
                    else 5
                    if name == "Fixed_five"
                    else 3
                    for row in trial_rows
                ]
            )
            for name in predictions
        }
        diagnostics = prediction_diagnostics(
            states, seeds, predictions, costs, config.bootstrap_resamples
        )
        observations = np.array(
            [[row[f"sensor_{j}"] for j in range(5)] for row in trial_rows]
        )
        diagnostics.update(
            stopping_sensitivity(
                observations,
                states,
                seeds,
                config.sensor_reliabilities,
                config.bootstrap_resamples,
            )
        )
        result["exploratory_analysis"] = {
            "status": "Exploratory; same held-out trials; no threshold selected or validated",
            "intervals": "Marginal 95% seed percentile bootstrap; 5000 resamples by default; seed 314159",
            "sign_tests": "Unadjusted secondary binomial sign tests of positive versus negative nonzero seed differences, not mean effects",
            "counts": {name: len(rows) for name, rows in diagnostics.items()},
        }
        create_diagnostic_figures(diagnostics, output_dir / "figures")
        sensing = run_active_sensing(
            config.n_seeds, max(2, config.n_trials // 2), config.bootstrap_resamples
        )
        result["active_sensing"] = {
            key: value
            for key, value in sensing.items()
            if key not in ("trials", "seed_metrics", "landscape", "specifications")
        }
        result["active_sensing"]["specification_sha256"] = list(
            sensing["specifications"]
        )
        create_active_sensing_figures(sensing, experiment, output_dir / "figures")
        robustness = reliability_robustness()
        result["model_robustness"] = {
            "config": robustness["config"],
            "specification_sha256": list(robustness["specifications"]),
            "metric_rows": len(robustness["metrics"]),
            "calibration_rows": len(robustness["calibration"]),
        }
        create_robustness_figure(robustness, output_dir / "figures")
    if max(stages) >= 4:
        _csv(output_dir / "replicates.csv", experiment["replicates"])
        _csv(output_dir / "trials.csv", experiment["trials"])
        _csv(output_dir / "efe_sensitivity.csv", sensitivity)
        for name, diagnostic_rows in diagnostics.items():
            _csv(output_dir / (name + ".csv"), diagnostic_rows)
        for name in ("trials", "seed_metrics", "landscape", "estimates", "comparisons"):
            _csv(output_dir / ("active_sensing_" + name + ".csv"), sensing[name])
        sensing_models = output_dir / "active_sensing_gnn"
        sensing_models.mkdir(exist_ok=True)
        for digest, content in sensing["specifications"].items():
            (sensing_models / (digest + ".md")).write_text(content)
        for name in ("metrics", "calibration"):
            _csv(output_dir / ("model_robustness_" + name + ".csv"), robustness[name])
        robustness_models = output_dir / "robustness_gnn"
        robustness_models.mkdir(exist_ok=True)
        for digest, content in robustness["specifications"].items():
            (robustness_models / (digest + ".md")).write_text(content)
        specification_dir = output_dir / "gnn"
        specification_dir.mkdir(exist_ok=True)
        for digest, content in experiment["gnn"]["specifications"].items():
            (specification_dir / (digest + ".md")).write_text(content)
        (output_dir / "summary.json").write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n"
        )
    if max(stages) >= 5:
        result["manuscript_validation"] = validate_manuscript(
            Path(project_root) / "manuscript"
        )
        render_manuscript(
            Path(project_root) / "manuscript", output_dir / "manuscript.html"
        )
        (output_dir / "summary.json").write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n"
        )
    if max(stages) >= 6:
        write_manifest(project_root, output_dir, result["experiment"]["config"])
    return result
