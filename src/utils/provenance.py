"""Standard-library provenance for reproducible scientific outputs."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    """Hash file bytes without embedding machine-specific paths."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(project_root: Path, output_dir: Path, config: dict) -> Path:
    """Record source, environment, configuration and output digests.

    Git revision is a base revision; source digests identify the actual executed
    working-tree content. The manifest excludes itself to avoid a hash cycle.
    """
    project_root, output_dir = Path(project_root).resolve(), Path(output_dir).resolve()
    try:
        revision = subprocess.run(
            ["git", "-C", str(project_root), "rev-parse", "HEAD"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        revision = None
    sources = {}
    for folder in ("src", "scripts", "manuscript", "docs", "tests"):
        for path in sorted((project_root / folder).rglob("*")):
            if path.is_file() and path.suffix in (
                ".py",
                ".md",
                ".bib",
                ".yaml",
                ".json",
            ):
                sources[str(path.relative_to(project_root))] = sha256(path)
    for filename in ("pyproject.toml", "uv.lock", "README.md", "template.lock.json"):
        path = project_root / filename
        if path.exists():
            sources[filename] = sha256(path)
    outputs = {
        str(path.relative_to(output_dir)): sha256(path)
        for path in sorted(output_dir.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    versions = {
        name: importlib.metadata.version(name)
        for name in (
            "numpy",
            "scipy",
            "matplotlib",
            "pandas",
            "psutil",
            "markdown",
            "bibtexparser",
            "latex2mathml",
        )
    }
    payload = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_git_revision": revision,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "versions": versions,
        "config": config,
        "source_sha256": sources,
        "output_sha256": outputs,
        "data_kind": "synthetic",
    }
    target = output_dir / "manifest.json"
    target.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    return target
