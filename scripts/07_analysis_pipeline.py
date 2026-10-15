#!/usr/bin/env python3
"""Reproduce checks, held-out experiments, figures, data and manuscript HTML."""

from __future__ import annotations
import argparse
import json
import os
import sys
import shutil
import hashlib
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
os.environ.setdefault("MPLBACKEND", "Agg")
from analysis.experiments import ExperimentConfig
from analysis.research_pipeline import STAGES, run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stages", nargs="+", type=int, choices=range(1, 7))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=project_root / "results")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--trials", type=int, default=400)
    parser.add_argument("--training", type=int, default=200)
    parser.add_argument(
        "--update-cover",
        action="store_true",
        help="Copy the data-generated graphical abstract into manuscript assets",
    )
    args = parser.parse_args()
    config = ExperimentConfig(
        n_seeds=args.seeds, n_trials=args.trials, n_training=args.training
    )
    config.validate()
    stages = list(range(1, max(args.stages) + 1)) if args.stages else list(STAGES)
    if args.update_cover and max(stages) < 4:
        parser.error("--update-cover requires data export stage 4 or later")
    if args.dry_run:
        print(
            json.dumps(
                {
                    "output_dir": str(args.output_dir),
                    "stages": [STAGES[s] for s in stages],
                },
                indent=2,
            )
        )
        return
    result = run_pipeline(project_root, args.output_dir, config, args.stages)
    if args.update_cover:
        assets = project_root / "manuscript/assets"
        selected = {}
        for extension in ("png", "pdf", "svg"):
            source = (
                args.output_dir
                / "figures"
                / ("scientific_graphical_abstract." + extension)
            )
            shutil.copy2(source, assets / source.name)
            selected[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
        (assets / "graphical-abstract-provenance.json").write_text(
            json.dumps(
                {
                    "kind": "Scientific graphical abstract generated from retained synthetic estimates and exact GNN/EFE evaluations",
                    "generator": "src/visualization/graphical_abstract.py",
                    "research_config": result["experiment"]["config"],
                    "active_sensing_config": result["active_sensing"]["config"],
                    "assets_sha256": selected,
                    "data_sources": [
                        "results/summary.json",
                        "results/active_sensing_estimates.csv",
                    ],
                    "ai_image_generation": False,
                },
                indent=2,
            )
            + "\n"
        )
        if max(stages) >= 6:
            from utils.provenance import write_manifest

            write_manifest(
                project_root, args.output_dir, result["experiment"]["config"]
            )
    print(
        json.dumps(
            {
                "stages_completed": result["stages_completed"],
                "checks": result["mathematical_checks"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
