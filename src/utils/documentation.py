"""Validate the documentation hub and actual local Markdown link targets."""

from __future__ import annotations
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from .exceptions import ValidationError

_LINK = re.compile(r"!?\[[^\]\n]+\]\(([^)\n]+)\)")


def _targets(text: str) -> list[str]:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return [value.strip().strip("<>") for value in _LINK.findall(text)]


def validate_documentation(project_root: Path) -> dict:
    """Require indexed guides and existing local targets; report exact failures."""
    root = Path(project_root).resolve()
    hub = root / "docs/README.md"
    if not hub.is_file():
        raise ValidationError("Missing docs/README.md documentation hub")
    guides = sorted((root / "docs").glob("*.md"))
    indexed = {urlsplit(target).path for target in _targets(hub.read_text())}
    errors = [
        f"docs/{path.name}: missing from documentation hub"
        for path in guides
        if path != hub and path.name not in indexed
    ]
    files = [
        *guides,
        *[path for path in (root / "README.md", root / "AGENTS.md") if path.is_file()],
    ]
    files.extend(
        sorted(
            path
            for folder in ("src", "scripts", "manuscript", "doc")
            for path in (root / folder).rglob("*.md")
            if path.name in ("README.md", "AGENTS.md") or folder == "doc"
        )
    )
    checked = 0
    for path in files:
        for target in _targets(path.read_text()):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            checked += 1
            if not destination.exists():
                errors.append(f"{path.relative_to(root)}: missing link target {target}")
    if errors:
        raise ValidationError("Documentation validation failed:\n" + "\n".join(errors))
    return {
        "valid": True,
        "guides": len(guides),
        "files_checked": len(files),
        "local_links_checked": checked,
    }
