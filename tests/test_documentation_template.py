"""Actual Git checkout and filesystem checks for publication integration."""

import json
import subprocess

import pytest

from utils.documentation import validate_documentation
from utils.exceptions import ValidationError
from utils.template_rendering import check_template_checkout, prepare_web_sources
from utils.figure_manager import FigureManager
from utils.template_rendering import _cover_details


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


def test_cover_uses_declared_asset_and_requires_description(tmp_path):
    (tmp_path / "abstract.png").write_bytes(b"real asset fixture")
    config = tmp_path / "config.yaml"
    config.write_text(
        "paper:\n  cover:\n    image: abstract.png\n    alt: Scientific abstract\n"
    )
    path, description = _cover_details(tmp_path)
    assert path == tmp_path / "abstract.png" and description == "Scientific abstract"
    config.write_text("paper:\n  cover:\n    image: abstract.png\n")
    with pytest.raises(ValidationError, match="description"):
        _cover_details(tmp_path)
    config.write_text(
        "paper:\n  cover:\n    image: missing.png\n    alt: Scientific abstract\n"
    )
    with pytest.raises(ValidationError, match="existing"):
        _cover_details(tmp_path)
    config.write_text(
        "paper:\n  cover:\n    image: ../outside.png\n    alt: Scientific abstract\n"
    )
    with pytest.raises(ValidationError, match="existing"):
        _cover_details(tmp_path)
    config.write_text("paper:\n  title: No cover\n")
    assert _cover_details(tmp_path) == (None, "")


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
    (tmp_path / "manuscript/config.yaml").write_text(
        "paper:\n  title: Projection fixture\n"
    )
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


@pytest.mark.parametrize(
    "configuration",
    [
        "scalar",
        "0",
        "paper: scalar",
        "paper:\n  cover: scalar",
        "paper:\n  cover:\n    image: 0\n    alt: Description",
    ],
)
def test_malformed_cover_configuration_rejected(tmp_path, configuration):
    (tmp_path / "config.yaml").write_text(configuration)
    with pytest.raises(ValidationError):
        _cover_details(tmp_path)


def test_projection_carries_selected_cover_and_red_link_style(tmp_path):
    source, aux = web_projection_fixture(tmp_path)
    assets = tmp_path / "manuscript/assets"
    assets.mkdir()
    (assets / "graph.png").write_bytes(b"graphical abstract fixture")
    (assets / "publication.css").write_text("a:any-link{color:#cc0000!important}")
    (tmp_path / "manuscript/config.yaml").write_text(
        "paper:\n  cover:\n    image: assets/graph.png\n    alt: Scientific graphical abstract\n"
    )
    files, _ = prepare_web_sources(tmp_path, [source], aux)
    assert "../figures/graph.png" in files[0].read_text()
    assert "Scientific graphical abstract" in files[0].read_text()
    assert "color:#cc0000!important" in files[0].read_text()


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
