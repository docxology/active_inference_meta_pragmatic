"""Real computation and filesystem integration for research artifacts."""

import csv
import json
from pathlib import Path
from dataclasses import replace

import numpy as np
import pytest

from analysis.experiments import (
    ExperimentConfig,
    binary_sensor_posterior,
    run_quadrant_experiment,
    mathematical_checks,
    reliability_sensitivity,
    paired_sign_flip_test,
)
from analysis.research_pipeline import run_pipeline
from core.probability import bayesian_update
from utils.manuscript import validate_manuscript, render_manuscript, manuscript_files
from utils.provenance import sha256, write_manifest
from utils.exceptions import ValidationError


def test_binary_batch_matches_sequential_bayes():
    rng = np.random.default_rng(16)
    observations = rng.integers(0, 2, (30, 5))
    reliabilities = np.array([0.51, 0.65, 0.9, 0.3, 0.8])
    batch = binary_sensor_posterior(observations, reliabilities)
    for values, actual in zip(observations, batch):
        prior = np.array([0.5, 0.5])
        for observation, r in zip(values, reliabilities):
            prior = bayesian_update(
                np.array([[r, 1 - r], [1 - r, r]]), int(observation), prior
            )
        assert actual == pytest.approx(prior[1], abs=1e-14)


@pytest.mark.parametrize(
    "observations,reliabilities",
    [
        ([1, 0], [0.8, 0.8]),
        ([[1, 0]], [0.8]),
        ([[2]], [0.8]),
        ([[0]], [1.0]),
        ([[0]], [np.nan]),
        ([[0]], [[0.8]]),
    ],
)
def test_batch_rejects_invalid(observations, reliabilities):
    with pytest.raises(ValidationError):
        binary_sensor_posterior(observations, reliabilities)


@pytest.mark.parametrize(
    "fields",
    [
        {"n_seeds": 1},
        {"n_trials": 0},
        {"n_training": 1},
        {"first_seed": -1},
        {"bootstrap_resamples": 10},
        {"sensor_reliabilities": (0.8,)},
        {"sensor_reliabilities": (np.nan,) * 5},
        {"assumed_reliability": 1},
        {"confidence_threshold": 0.1},
    ],
)
def test_experiment_contract(fields):
    with pytest.raises(ValidationError):
        replace(ExperimentConfig(), **fields).validate()


def test_experiment_reproducibility_units_and_raw_scores():
    config = ExperimentConfig(
        n_seeds=6, n_trials=80, n_training=80, bootstrap_resamples=100
    )
    a = run_quadrant_experiment(config)
    b = run_quadrant_experiment(config)
    assert a == b
    assert len(a["replicates"]) == 30 and len(a["trials"]) == 480
    assert len(a["comparisons"]) == 3
    rows = a["trials"][:80]
    for strategy in a["summary"]:
        p = np.array([r[strategy + "_p1"] for r in rows])
        state = np.array([r["state"] for r in rows])
        row = next(
            r for r in a["replicates"] if r["seed"] == 0 and r["strategy"] == strategy
        )
        assert row["accuracy"] == pytest.approx(np.mean((p > 0.5) == state))
        assert row["brier"] == pytest.approx(np.mean((p - state) ** 2))
    assert all(3 <= r["Q3_observations"] <= 5 for r in a["trials"])
    assert all(
        item["n_pairs"] == 6 and item["p_sign_flip_holm"] >= item["p_sign_flip"]
        for item in a["comparisons"].values()
    )
    # Equivalent fixed and true metadata assumptions must have no advantage.
    homogeneous = run_quadrant_experiment(
        replace(config, sensor_reliabilities=(0.8,) * 5)
    )
    assert homogeneous["comparisons"]["H1"]["accuracy_difference"]["mean"] == 0
    assert homogeneous["comparisons"]["H1"]["p_sign_flip"] == 1
    assert not homogeneous["comparisons"]["H1"]["paired_t_test"]["test_defined"]


def test_mathematical_checks_and_exact_sweep():
    result = mathematical_checks(5)
    assert result["passed"] and result["n_policy_checks"] == 20
    rows = reliability_sensitivity()
    assert len(rows) == 26
    assert rows[0]["information_gain"] == pytest.approx(0)
    assert rows[-1]["information_gain"] == pytest.approx(np.log(2))
    assert paired_sign_flip_test([0, 0, 0], n_resamples=100) == 1
    with pytest.raises(ValidationError):
        paired_sign_flip_test([0, 1], n_resamples=1)
    with pytest.raises(ValidationError):
        mathematical_checks(0)


def make_manuscript(root):
    directory = root / "manuscript"
    directory.mkdir()
    (directory / "references.bib").write_text(
        "@article{example, title={Example}, author={Author, A}, year={2026}, journal={Journal}, doi={10.1234/example}}"
    )
    (directory / "01_abstract.md").write_text("""# Abstract {#sec:abstract}

A short text with $q(s)$ and \\cite{example}.

```{=latex}
\\begin{equation}
F=H+G
\\label{eq:test}
\\end{equation}
```

See \\eqref{eq:test} and \\ref{sec:abstract}.
""")
    (directory / "AGENTS.md").write_text("Agent guidance excluded from publication")
    return directory


@pytest.mark.timeout(60)
def test_full_pipeline_and_hash_integrity(tmp_path):
    make_manuscript(tmp_path)
    config = ExperimentConfig(
        n_seeds=6, n_trials=80, n_training=80, bootstrap_resamples=100
    )
    result = run_pipeline(tmp_path, tmp_path / "results", config)
    assert result["stages_completed"] == [1, 2, 3, 4, 5, 6]
    assert result["manuscript_validation"]["valid"]
    data = json.loads((tmp_path / "results/summary.json").read_text())
    assert data["experiment"]["config"]["n_seeds"] == 6
    assert len(list(csv.DictReader((tmp_path / "results/replicates.csv").open()))) == 30
    manifest = json.loads((tmp_path / "results/manifest.json").read_text())
    for relative, digest in manifest["output_sha256"].items():
        assert sha256(tmp_path / "results" / relative) == digest
    text = (tmp_path / "results/manuscript.html").read_text()
    assert "<math" in text and "#bib-example" in text and "Agent guidance" not in text
    assert "MathJax" not in text
    assert run_pipeline(tmp_path, tmp_path / "checks", config, [1])[
        "stages_completed"
    ] == [1]
    with pytest.raises(ValidationError):
        run_pipeline(tmp_path, tmp_path / "bad", config, [7])


@pytest.mark.parametrize(
    "extra",
    [
        r"\ref{sec:missing}",
        r"\cite{unknown}",
        r"\label{eq:test}",
        r"\includegraphics{missing.png}",
    ],
)
def test_manuscript_rejects_unresolved_or_duplicate(extra, tmp_path):
    directory = make_manuscript(tmp_path)
    (directory / "02_more.md").write_text(extra)
    with pytest.raises(ValidationError):
        validate_manuscript(directory)


def test_math_and_figure_rendering(tmp_path):
    directory = make_manuscript(tmp_path)
    image = tmp_path / "image.png"
    image.write_bytes(b"test image bytes")
    (directory / "02_figures.md").write_text(r"""# Results {#sec:results}

$$G=F+H$$

```{=latex}
\begin{figure}[h]
\includegraphics{../image.png}
\caption{A figure & caption}
\label{fig:example}
\end{figure}
```
""")
    target = render_manuscript(directory, tmp_path / "render/index.html")
    content = target.read_text()
    assert 'src="../image.png"' in content and "A figure &amp; caption" in content
    assert "<math" in content and len(manuscript_files(directory)) == 2
    (directory / "references.bib").write_text(
        "@misc{example,title={One}}\n@misc{example,title={Two}}"
    )
    with pytest.raises(ValidationError):
        validate_manuscript(directory)


def test_invalid_registry_structure_is_preserved_before_replacement(tmp_path):
    from utils.figure_manager import FigureManager

    path = tmp_path / "registry.json"
    original = b"[]"
    path.write_bytes(original)
    manager = FigureManager(str(path))
    assert manager.figures == {}
    backups = list(tmp_path.glob("registry.json.corrupt-*"))
    assert len(backups) == 1 and backups[0].read_bytes() == original
    manager.register_figure("example.png", "An example")
    assert "fig:example" in json.loads(path.read_text())
    assert backups[0].read_bytes() == original
