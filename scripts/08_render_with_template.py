#!/usr/bin/env python3
"""Render combined PDF and HTML with the pinned docxology/template checkout."""

from __future__ import annotations
import argparse
import os
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
from utils.template_rendering import render_with_template, template_worker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template-root",
        type=Path,
        default=os.environ.get("TEMPLATE_ROOT"),
        required=not bool(os.environ.get("TEMPLATE_ROOT")),
    )
    parser.add_argument("--template-python", type=Path)
    parser.add_argument(
        "--output-dir", type=Path, default=project_root / "results/template"
    )
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        result = template_worker(project_root, args.template_root, args.output_dir)
    else:
        result = render_with_template(
            project_root, args.template_root, args.template_python, args.output_dir
        )
    print(result)


if __name__ == "__main__":
    main()
