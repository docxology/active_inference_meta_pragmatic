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
        sensitivity = reliability_sensitivity()
        create_research_figures(experiment, sensitivity, output_dir / "figures")
    if max(stages) >= 4:
        _csv(output_dir / "replicates.csv", experiment["replicates"])
        _csv(output_dir / "trials.csv", experiment["trials"])
        _csv(output_dir / "efe_sensitivity.csv", sensitivity)
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
