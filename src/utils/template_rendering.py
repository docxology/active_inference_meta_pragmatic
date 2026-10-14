"""Pinned docxology/template integration; project computations remain local."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from .exceptions import ValidationError


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def check_template_checkout(project_root: Path, template_root: Path) -> dict:
    """Reject the wrong origin, revision, or modified tracked renderer source."""
    pin = json.loads((Path(project_root) / "template.lock.json").read_text())
    template_root = Path(template_root).resolve()
    try:
        origin = _git(template_root, "remote", "get-url", "origin")
        revision = _git(template_root, "rev-parse", "HEAD")
        modified = _git(template_root, "status", "--porcelain", "--untracked-files=no")
    except subprocess.CalledProcessError as exc:
        raise ValidationError("Template root must be a Git checkout") from exc
    normalized = origin.removesuffix(".git").removesuffix("/")
    if normalized == "git@github.com:docxology/template":
        normalized = "https://github.com/docxology/template"
    if normalized != pin["repository"] or revision != pin["revision"]:
        raise ValidationError("Template checkout does not match template.lock.json")
    if modified:
        raise ValidationError(
            "Template has modified tracked files; use the pinned clean checkout"
        )
    return pin


def render_with_template(
    project_root: Path,
    template_root: Path,
    template_python: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Validate inputs, invoke the template environment, and require its receipt."""
    from .manuscript import validate_manuscript

    project_root, template_root = (
        Path(project_root).resolve(),
        Path(template_root).resolve(),
    )
    check_template_checkout(project_root, template_root)
    validate_manuscript(project_root / "manuscript")
    # Resolving a venv's Python symlink would lose its environment prefix.
    interpreter = Path(template_python or template_root / ".venv/bin/python").absolute()
    if not interpreter.is_file():
        raise ValidationError(
            "Install the template environment or pass --template-python"
        )
    output_dir = Path(output_dir or project_root / "results/template").resolve()
    command = [
        str(interpreter),
        str(project_root / "scripts/08_render_with_template.py"),
        "--template-root",
        str(template_root),
        "--output-dir",
        str(output_dir),
        "--worker",
    ]
    environment = dict(os.environ)
    environment.pop("VIRTUAL_ENV", None)
    subprocess.run(
        command, cwd=project_root, env=environment, stdin=subprocess.DEVNULL, check=True
    )
    receipt = output_dir / "renderer_manifest.json"
    if not receipt.is_file():
        raise ValidationError("Template rendering did not produce a renderer manifest")
    return receipt


def prepare_web_sources(
    project_root: Path, sources: list[Path], aux_file: Path
) -> tuple[list[Path], dict]:
    """Project HTML syntax using actual PDF reference numbers; preserve authorship."""
    import shutil

    auxiliary = Path(aux_file).read_text()
    numbers = dict(re.findall(r"\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}", auxiliary))
    destination = Path(project_root) / "output/manuscript"
    destination.mkdir(parents=True, exist_ok=True)
    for filename in ("config.yaml", "references.bib", "preamble.md"):
        shutil.copy2(
            Path(project_root) / "manuscript" / filename, destination / filename
        )
    projected = []
    for source in sources:
        text = source.read_text()
        text = re.sub(
            r"\\cite(?:p|t)?\{([^{}]+)\}",
            lambda match: "["
            + "; ".join("@" + key.strip() for key in match[1].split(","))
            + "]",
            text,
        )

        def reference(match):
            label = match[2]
            if label not in numbers:
                raise ValidationError(
                    f"Compiled PDF has no reference number for {label}"
                )
            value = numbers[label]
            if match[1] == "eqref":
                value = "(" + value + ")"
            return f"[{value}](#{label})"

        text = re.sub(r"\\(eqref|ref)\{([^{}]+)\}", reference, text)

        def project_block(match):
            block = match[0]
            label = re.search(r"\\label\{([^{}]+)\}", block)
            if not label:
                return block
            key = label[1]
            if key not in numbers:
                raise ValidationError(f"Compiled PDF has no reference number for {key}")
            if r"\begin{equation}" in block:
                body = re.search(
                    r"\\begin\{equation\}(.*?)\\end\{equation\}", block, re.DOTALL
                )[1]
                body = re.sub(r"\\label\{[^{}]+\}", "", body).strip()
                return f"::: {{#{key}}}\n$$\n{body}\n\\tag{{{numbers[key]}}}\n$$\n:::"
            if r"\begin{figure}" in block:
                image = re.search(
                    r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}", block
                )
                caption = re.search(r"\\caption\{(.*?)\}\s*\\label", block, re.DOTALL)
                if image is None or caption is None:
                    raise ValidationError(f"Unsupported figure projection for {key}")
                return f"![{caption[1]}]({image[1]}){{#{key} width=95%}}"
            return block

        text = re.sub(
            r"```\{=latex\}\s*\n.*?\n```", project_block, text, flags=re.DOTALL
        )
        text = text.replace("../results/figures/", "../figures/")
        target = destination / source.name
        target.write_text(text)
        projected.append(target)
    return projected, {
        "algorithm": "latex-citations-and-pdf-aux-references-v1",
        "pdf_aux_sha256": hashlib.sha256(auxiliary.encode()).hexdigest(),
        "reference_numbers": {
            key: value
            for key, value in numbers.items()
            if key.startswith(("sec:", "eq:", "fig:"))
        },
        "hydrated_source_sha256": {
            str(path.relative_to(project_root)): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in projected
        },
    }


def template_worker(project_root: Path, template_root: Path, output_dir: Path) -> Path:
    """Run the upstream combined renderers without copying or patching them."""
    project_root, template_root, output_dir = (
        Path(project_root).resolve(),
        Path(template_root).resolve(),
        Path(output_dir).resolve(),
    )
    pin = check_template_checkout(project_root, template_root)
    sys.path.insert(0, str(template_root))
    from infrastructure.rendering import RenderManager, RenderingConfig

    manuscript = project_root / "manuscript"
    sources = sorted(
        path for path in manuscript.glob("*.md") if re.match(r"^\d{2}_", path.name)
    )
    # Upstream composition custody expects the canonical project/output layout.
    # Retain publication editions separately from ignored compiler intermediates.
    import shutil

    runtime = project_root / "output"
    shutil.copytree(
        project_root / "results/figures", runtime / "figures", dirs_exist_ok=True
    )
    config = RenderingConfig(
        manuscript_dir=str(manuscript),
        figures_dir=str(runtime / "figures"),
        output_dir=str(runtime),
        pdf_dir=str(runtime / "pdf"),
        web_dir=str(runtime / "web"),
        template_dir=str(template_root / "infrastructure/rendering/templates"),
        web_asset_mode="cdn",
    )
    manager = RenderManager(
        config=config, manuscript_dir=manuscript, figures_dir=runtime / "figures"
    )
    pdf = manager.render_combined_pdf(
        sources, manuscript, project_name=project_root.name
    )
    web_sources, projection = prepare_web_sources(
        project_root, sources, runtime / "pdf/_combined_manuscript.aux"
    )
    web = manager.render_combined_web(
        web_sources, runtime / "manuscript", project_name=project_root.name
    )
    if not pdf.is_file() or not web.is_file():
        raise ValidationError("Both template PDF and HTML editions are required")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "pdf").mkdir(exist_ok=True)
    shutil.copy2(pdf, output_dir / "pdf" / pdf.name)
    shutil.copytree(runtime / "web", output_dir / "web", dirs_exist_ok=True)
    shutil.copytree(
        runtime / "manuscript", output_dir / "manuscript", dirs_exist_ok=True
    )
    shutil.copytree(
        project_root / "results/figures", output_dir / "figures", dirs_exist_ok=True
    )
    shutil.copy2(
        runtime / "reports/manuscript_composition.json",
        output_dir / "manuscript_composition.json",
    )
    pdf, web = output_dir / "pdf" / pdf.name, output_dir / "web" / web.name
    versions = {}
    for name in ("pandoc", "xelatex", "bibtex"):
        versions[name] = subprocess.run(
            [name, "--version"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()[0]
    artifacts = [
        pdf,
        *sorted((output_dir / "web").rglob("*")),
        *sorted((output_dir / "figures").rglob("*")),
        *sorted((output_dir / "manuscript").rglob("*")),
        output_dir / "manuscript_composition.json",
    ]
    payload = {
        "schema_version": 1,
        "renderer": pin["repository"],
        "revision": pin["revision"],
        "html_projection": projection,
        "tools": versions,
        "source_sha256": {
            str(path.relative_to(project_root)): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in [
                *sources,
                manuscript / "config.yaml",
                manuscript / "preamble.md",
                manuscript / "references.bib",
                project_root / "template.lock.json",
            ]
        },
        "output_sha256": {
            str(path.relative_to(output_dir)): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in artifacts
            if path.is_file() and path.name != "_combined_manuscript.md"
        },
        "pdf": str(pdf.relative_to(output_dir)),
        "html": str(web.relative_to(output_dir)),
    }
    target = output_dir / "renderer_manifest.json"
    target.write_text(json.dumps(payload, indent=2) + "\n")
    return target
