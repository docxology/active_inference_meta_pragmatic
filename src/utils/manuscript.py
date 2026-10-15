"""Strict manuscript validation and standalone HTML rendering with MathML."""

from __future__ import annotations

import html
import os
import re
from pathlib import Path

from utils.exceptions import ValidationError


def manuscript_files(directory: Path) -> list[Path]:
    """Return numbered manuscript sections, excluding agent guidance and preamble."""
    return sorted(
        p for p in Path(directory).glob("*.md") if re.match(r"^\d\d_", p.name)
    )


def validate_manuscript(directory: Path) -> dict:
    """Reject duplicate or unresolved labels/citations and missing figure files."""
    import bibtexparser

    directory = Path(directory)
    text = "\n".join(p.read_text() for p in manuscript_files(directory))
    entries = bibtexparser.loads((directory / "references.bib").read_text()).entries
    keys = [e["ID"] for e in entries]
    labels = re.findall(r"\\label\{([^}]+)\}|\{#([^}]+)\}", text)
    labels = [a or b for a, b in labels]
    refs = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", text)
    citations = [
        key.strip()
        for group in re.findall(r"\\cite\{([^}]+)\}", text)
        for key in group.split(",")
    ]
    duplicates = sorted({label for label in labels if labels.count(label) > 1})
    missing_refs = sorted(set(refs) - set(labels))
    missing_cites = sorted(set(citations) - set(keys))
    missing_figures = [
        path
        for path in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", text)
        if not (directory / path).is_file()
    ]
    issues = []
    if duplicates:
        issues.append(f"Duplicate labels: {duplicates}")
    if len(keys) != len(set(keys)):
        issues.append("Duplicate bibliography keys")
    if missing_refs:
        issues.append(f"Unresolved references: {missing_refs}")
    if missing_cites:
        issues.append(f"Unresolved citations: {missing_cites}")
    if missing_figures:
        issues.append(f"Missing figures: {missing_figures}")
    if issues:
        raise ValidationError("; ".join(issues))
    return {
        "valid": True,
        "sections": len(manuscript_files(directory)),
        "labels": len(labels),
        "unique_citations": len(set(citations)),
        "bibliography_entries": len(keys),
        "figures": len(re.findall(r"\\includegraphics", text)),
    }


def render_manuscript(directory: Path, destination: Path) -> Path:
    """Render numbered Markdown, equations, linked citations and figures to HTML.

    MathML renders without external scripts. Source Markdown remains authoritative.
    """
    import bibtexparser
    import markdown
    from latex2mathml.converter import convert

    directory, destination = Path(directory).resolve(), Path(destination).resolve()
    validate_manuscript(directory)
    text = "\n\n".join(
        p.read_text()
        for p in manuscript_files(directory)
        if not p.name.startswith("99_")
    )
    label_titles = {
        label: title
        for title, label in re.findall(r"^#{1,6} (.*?) \{#([^}]+)\}$", text, re.M)
    }
    entries = {
        e["ID"]: e
        for e in bibtexparser.loads((directory / "references.bib").read_text()).entries
    }
    equation_labels = re.findall(r"\\label\{(eq:[^}]+)\}", text)
    label_titles.update({label: f"({i+1})" for i, label in enumerate(equation_labels)})
    citations = list(
        dict.fromkeys(
            key.strip()
            for group in re.findall(r"\\cite\{([^}]+)\}", text)
            for key in group.split(",")
        )
    )
    numbers = {key: i + 1 for i, key in enumerate(citations)}
    tokens = {}

    def stash(value):
        key = f"MANUSCRIPTPLACEHOLDER{len(tokens)}END"
        tokens[key] = value
        return key

    def math(value, display=False, label=None):
        try:
            value = re.sub(r"\\label\{[^}]+\}", "", value)
            value = re.sub(
                r"\\(?:begin|end)\{(?:equation\*?|align\*?)\}", "", value
            ).strip()
            rendered = convert(value, display="block" if display else "inline")
        except Exception as exc:
            raise ValidationError(f"Equation rendering failed: {value[:100]}") from exc
        return stash(
            f'<div class="equation" id="{html.escape(label)}">{rendered}</div>'
            if display and label
            else rendered
        )

    def raw_block(match):
        block = match.group(1)
        if "\\begin{figure}" in block:
            target = re.search(
                r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", block
            ).group(1)
            caption = re.search(r"\\caption\{(.*?)\}\s*\\label", block, re.S).group(1)
            label = re.search(r"\\label\{([^}]+)\}", block).group(1)
            rel = os.path.relpath(directory / target, destination.parent)
            return stash(
                f'<figure id="{html.escape(label)}"><img src="{html.escape(rel)}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>'
            )
        label_match = re.search(r"\\label\{([^}]+)\}", block)
        return math(block, True, label_match.group(1) if label_match else None)

    text = re.sub(r"```\{=latex\}\s*\n(.*?)\n```", raw_block, text, flags=re.S)
    text = re.sub(r"\$\$(.*?)\$\$", lambda m: math(m.group(1), True), text, flags=re.S)
    text = re.sub(r"(?<!\\)\$([^$\n]+)\$", lambda m: math(m.group(1)), text)
    text = re.sub(
        r"\\cite\{([^}]+)\}",
        lambda m: ", ".join(
            f'<a href="#bib-{key.strip()}">[{numbers[key.strip()]}]</a>'
            for key in m.group(1).split(",")
        ),
        text,
    )
    text = re.sub(
        r"\\(?:eqref|ref)\{([^}]+)\}",
        lambda m: f'<a href="#{m.group(1)}">{html.escape(label_titles.get(m.group(1), m.group(1)))}</a>',
        text,
    )
    text = re.sub(
        r"^(#{1,6}) (.*?) \{#([^}]+)\}$",
        lambda m: f'<h{len(m.group(1))} id="{m.group(3)}">{m.group(2)}</h{len(m.group(1))}>',
        text,
        flags=re.M,
    )
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "toc"])
    for key, value in tokens.items():
        body = body.replace(key, value)
    bibliography = []
    for key in citations:
        entry = entries[key]
        label = ". ".join(
            entry.get(field, "").replace("{", "").replace("}", "").replace("\\&", "&")
            for field in ("author", "year", "title", "journal")
            if entry.get(field)
        )
        url = entry.get("url") or (
            "https://doi.org/" + entry["doi"] if entry.get("doi") else None
        )
        item = html.escape(label)
        if url:
            item += f' <a href="{html.escape(url)}">Source</a>'
        bibliography.append(f'<li id="bib-{key}">{item}</li>')
    body += (
        '<h1 id="sec:references">References</h1><ol>'
        + "\n".join(bibliography)
        + "</ol>"
    )
    configuration = (
        (directory / "config.yaml").read_text()
        if (directory / "config.yaml").exists()
        else ""
    )
    names = re.findall(r'^\s*- name:\s*"([^"]+)"', configuration, re.M)
    titles = re.findall(r'^\s*title:\s*"([^"]+)"', configuration, re.M)
    title = html.escape(titles[0] if titles else "Active Inference as a Meta-Pragmatic and Meta-Epistemic Method")
    author_line = " · ".join(html.escape(name) for name in names)
    body = (
        "<header><h1>" + title + "</h1><p>"
        + author_line
        + "</p><p>Working manuscript · Synthetic computational demonstration</p></header>"
        + body
    )
    css = "body{max-width:900px;margin:40px auto;padding:0 24px;font:17px/1.6 Georgia,serif;color:#222}h1,h2,h3{line-height:1.25}a:any-link{color:#cc0000}img{max-width:100%}figure{margin:28px 0}figcaption{font-size:14px}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}.equation{overflow-x:auto;margin:20px 0}pre{white-space:pre-wrap;background:#f4f4f4;padding:12px}@media print{body{font-size:11pt;margin:0}h1,h2,h3{break-after:avoid}figure,table{break-inside:avoid}}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + title + '</title><style>'
        + css
        + "</style><body>"
        + body
        + "</body></html>"
    )
    return destination
