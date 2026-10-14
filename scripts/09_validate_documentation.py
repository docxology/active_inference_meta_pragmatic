#!/usr/bin/env python3
"""Validate the modular documentation hub and repository-local links."""

import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "src"))
from utils.documentation import validate_documentation

if __name__ == "__main__":
    print(json.dumps(validate_documentation(root), indent=2))
