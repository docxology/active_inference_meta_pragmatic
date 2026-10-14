"""Actual Git checkout and filesystem checks for publication integration."""

import json
import subprocess

import pytest

from utils.documentation import validate_documentation
from utils.exceptions import ValidationError
from utils.template_rendering import check_template_checkout, prepare_web_sources
from utils.figure_manager import FigureManager


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def checkout(tmp_path):
    template = tmp_path / "template"
    template.mkdir()
    git(template, "init")
    git(template, "config", "user.name", "Test")
    git(template, "config", "user.email", "test@example.invalid")
    git(
        template, "remote", "add", "origin", "https://github.com/docxology/template.git"
    )
    (template / "source.txt").write_text("Actual tracked source\n")
    git(template, "add", "source.txt")
    git(template, "commit", "-m", "Test fixture")
    pin = {
        "repository": "https://github.com/docxology/template",
        "revision": git(template, "rev-parse", "HEAD"),
    }
    (tmp_path / "template.lock.json").write_text(json.dumps(pin))
    return template, pin


def test_template_checkout_tracks_actual_revision(tmp_path):
    template, pin = checkout(tmp_path)
    assert check_template_checkout(tmp_path, template) == pin
    (template / "ignored-untracked.txt").write_text("Runtime output")
    assert check_template_checkout(tmp_path, template) == pin
    git(
        template, "remote", "set-url", "origin", "git@github.com:docxology/template.git"
    )
    assert check_template_checkout(tmp_path, template) == pin


@pytest.mark.parametrize("change", ["origin", "revision", "tracked"])
def test_template_rejects_wrong_or_modified_checkout(tmp_path, change):
    template, pin = checkout(tmp_path)
    if change == "origin":
        git(
            template, "remote", "set-url", "origin", "https://github.com/other/template"
        )
    elif change == "revision":
        pin["revision"] = "0" * 40
        (tmp_path / "template.lock.json").write_text(json.dumps(pin))
    else:
        (template / "source.txt").write_text("Changed renderer\n")
    with pytest.raises(ValidationError):
        check_template_checkout(tmp_path, template)


def test_non_git_template_rejected(tmp_path):
    (tmp_path / "template.lock.json").write_text(
        json.dumps(
            {
                "repository": "https://github.com/docxology/template",
                "revision": "0" * 40,
            }
        )
    )
    with pytest.raises(ValidationError, match="Git checkout"):
        check_template_checkout(tmp_path, tmp_path / "absent")


def test_documentation_actual_links_and_index(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# Docs\n[Methods](methods.md)\n")
    (docs / "methods.md").write_text(
        "# Methods\n[Hub](README.md)\n[Record](https://example.invalid)\n```\n[Example](missing.md)\n```\n"
    )
    result = validate_documentation(tmp_path)
    assert result["valid"] and result["guides"] == 2
    assert result["local_links_checked"] == 2
    (docs / "methods.md").write_text("[Missing](absent.md)")
    with pytest.raises(ValidationError, match="missing link target"):
        validate_documentation(tmp_path)


def test_documentation_unindexed_guide_rejected(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/README.md").write_text("# Documentation")
    (tmp_path / "docs/unindexed.md").write_text("# New guide")
    with pytest.raises(ValidationError, match="missing from documentation hub"):
        validate_documentation(tmp_path)


def test_documentation_requires_hub(tmp_path):
    with pytest.raises(ValidationError, match="documentation hub"):
        validate_documentation(tmp_path)


def web_projection_fixture(root):
    manuscript = root / "manuscript"
    manuscript.mkdir()
    for name in ("config.yaml", "references.bib", "preamble.md"):
        (manuscript / name).write_text("Source metadata\n")
    source = manuscript / "01_abstract.md"
    source.write_text(r"""# Abstract {#sec:abstract}
Literature \cite{one,two}; Section \ref{sec:abstract}, Equation \eqref{eq:test}.

```{=latex}
\begin{equation}
F=G+H
\label{eq:test}
\end{equation}
```

```{=latex}
\begin{figure}[h]
\includegraphics[width=0.95\textwidth]{../results/figures/test.png}
\caption{Retained evidence.}
\label{fig:test}
\end{figure}
```
""")
    aux = root / "compiled.aux"
    aux.write_text(r"""\newlabel{sec:abstract}{{1}{1}{Abstract}{section.1}{}}
\newlabel{eq:test}{{2}{1}{}{equation.2}{}}
\newlabel{fig:test}{{3}{1}{}{figure.3}{}}
""")
    return source, aux


def test_web_projection_preserves_authorship_and_actual_numbers(tmp_path):
    source, aux = web_projection_fixture(tmp_path)
    original = source.read_bytes()
    files, record = prepare_web_sources(tmp_path, [source], aux)
    text = files[0].read_text()
    assert source.read_bytes() == original
    assert "[@one; @two]" in text
    assert "[1](#sec:abstract)" in text
    assert "[(2)](#eq:test)" in text and r"\tag{2}" in text
    assert "F=G+H" in text and "{#eq:test}" in text
    assert "![Retained evidence.](../figures/test.png){#fig:test width=95%}" in text
    assert record["reference_numbers"]["eq:test"] == "2"
    assert record["pdf_aux_sha256"] and record["hydrated_source_sha256"]


def test_web_projection_missing_pdf_number_rejected(tmp_path):
    source, aux = web_projection_fixture(tmp_path)
    aux.write_text("")
    with pytest.raises(ValidationError, match="reference number"):
        prepare_web_sources(tmp_path, [source], aux)


def test_web_projection_unsupported_figure_rejected(tmp_path):
    source, aux = web_projection_fixture(tmp_path)
    source.write_text(source.read_text().replace(r"\caption{Retained evidence.}", ""))
    with pytest.raises(ValidationError, match="Unsupported figure"):
        prepare_web_sources(tmp_path, [source], aux)


def test_accessible_figure_registry_roundtrip(tmp_path):
    path = tmp_path / "figure_registry.json"
    manager = FigureManager(str(path))
    manager.register_figure("plot.png", "Caption", alt_text="A measured comparison.")
    assert (
        json.loads(path.read_text())["fig:plot"]["alt_text"] == "A measured comparison."
    )
    assert (
        FigureManager(str(path)).figures["fig:plot"].alt_text
        == "A measured comparison."
    )
    with pytest.raises(ValidationError, match="alt text"):
        manager.register_figure("bad.png", "Caption", alt_text=" ")
