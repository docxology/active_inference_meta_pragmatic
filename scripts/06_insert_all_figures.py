#!/usr/bin/env python3
"""Validate manuscript references, citations and figure files; optionally render HTML.

Manuscript figure placement is explicit in source. This replaces stale automatic
insertion maps that could silently skip or attach figures to unrelated sections.
"""

import argparse
import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))
from utils.manuscript import validate_manuscript, render_manuscript


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    result = validate_manuscript(project_root / "manuscript")
    if args.render:
        render_manuscript(
            project_root / "manuscript", project_root / "results/manuscript.html"
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
