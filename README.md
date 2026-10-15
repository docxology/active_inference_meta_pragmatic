# Active Inference as a Meta-Pragmatic Framework

A working research implementation of categorical active inference and a data/metadata × cognition/meta-cognition taxonomy. The manuscript joins a conceptual argument to reproducible **synthetic** sensor and EFE action studies, plus exact world–agent mismatch analysis. Real upstream GNN imports bind model specifications to execution. The framework connects declared models, decisions, external evaluation and accountable revision; its numerical evidence is bounded to these tasks.

## Reproduce the research

The first public release is **v1.0.0**: [GitHub release](https://github.com/docxology/active_inference_meta_pragmatic/releases/tag/v1.0.0), [Zenodo preprint and reproducibility archive](https://zenodo.org/records/23397453), DOI **10.5281/zenodo.23397453**. [Release history](CHANGELOG.md) explains the earlier private development labels and preserved commits; [publication documentation](docs/release_v1.0.0.md) separates the release cut from remote verification.

Python 3.12 is the recorded environment; package support starts at Python 3.11, matching the pinned GNN parser's supported minimum. Set `GNN_ROOT` to the real Generalized_Notation_Notation checkout at the revision in `src/core/gnn_models/upstream.lock.json`; canonical GitVault placement is detected automatically.

```bash
uv sync --locked --extra dev --extra research
MPLBACKEND=Agg uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/07_analysis_pipeline.py
```

For pip users: `python -m pip install -e '.[dev,research]'`, followed by `python scripts/07_analysis_pipeline.py`.

The pipeline produces CSV evidence, JSON estimates/tests, PNG/PDF/SVG figures, an offline HTML preview with MathML, and source/environment/output hashes in `results/`. `--dry-run` creates no outputs. `--stages 1 2` runs the requested stages and their dependencies. `--seeds`, `--trials`, and `--training` change the design and must be disclosed when reporting a new run.

The expanded manuscript cites 53 records and includes twelve numbered figures plus a scientific graphical abstract on the first page. [Executed active sensing](docs/active_sensing.md) adds actual GNN/EFE policy sampling, paired held-out outcomes, exact expectations and an exact reliability/preference surface. [Exploratory diagnostics](docs/exploratory_diagnostics.md) retain 24 paired accuracy/loss/cost estimates, calibration tables at three resolutions, and an eleven-threshold stopping sweep. These analyses preserve the original three-test Holm family and identify the limits of reusing test data. PDF and HTML hyperlinks are red.

Publication editions use the pinned [docxology/template](https://github.com/docxology/template) combined renderers:

```bash
uv run python scripts/08_render_with_template.py --template-root /path/to/template
uv run python scripts/09_validate_documentation.py
```

The template checkout, its separate Python environment, Pandoc, XeLaTeX and BibTeX are required for this step. The PDF/HTML editions and renderer receipt are retained in `results/template/`; [rendering setup and output details](docs/rendering_pipeline.md) explain the pin and prerequisites.

## What is implemented

- Column-stochastic A/B matrices, finite preference logits C, normalized state prior D, and shared validation contracts.
- Real upstream GNN parser import, authored executable models, strict profile admission and retained materialized specifications.
- Exact categorical and normalized virtual-evidence Bayes updates, including zero support and impossible-evidence handling.
- Open-loop EFE with information gain, preferences, normalized risk and ambiguity, explicit mean/sum horizon aggregation, and policy precision.
- Exact categorical variational free energy and evidence-bound checks.
- Paired seed-level statistics, bootstrap intervals, design-specific effect sizes and Holm correction.
- Bounded synthetic reliability learning and adaptive sensing, with misleading metadata and fixed four-/five-observation resource comparators.
- Educational quadrant, modeler, confidence/attention and security diagnostics, with their limits documented.

## Basic use

The installed packages use `core`, `framework`, `analysis`, `visualization`, and `utils` imports.

```python
from core.generative_models import create_simple_generative_model
from core.active_inference import ActiveInferenceFramework
from core.free_energy_principle import calculate_variational_free_energy

model = create_simple_generative_model()
agent = ActiveInferenceFramework(model)
posterior = model.perform_inference([0.8, 0.2])  # normalized virtual evidence
policy, details = agent.select_optimal_policy([[0], [1]], posterior)
score, components = agent.calculate_expected_free_energy(posterior, policy)
free_energy, bound = calculate_variational_free_energy(model, 0, posterior)
```

`total` is the legacy raw-logit EFE score; `normalized_total` adds the preference log-normalizer and equals `risk + ambiguity`. The default horizon aggregation is the mean; pass `aggregation="sum"` for additive costs. A soft evidence vector is integrated through `A.T @ evidence`; it is not reduced to its largest entry. Uniform evidence preserves the prior.

The older model-free `FreeEnergyPrinciple` methods return explicitly labeled illustrative scores and trajectories. Use an explicit generative model or `calculate_variational_free_energy` for a genuine variational bound. Security integrity checks establish structural validity; they cannot establish absence of tampering.

## Retained results

The default run uses 30 independent seeds, 400 held-out trials per seed, and separate training for the learned condition. Accuracy is 76.36% for fixed reliability, 84.68% for true reliability metadata, 90.34% for adaptive sensing, 84.68% for learned reliability, and 54.12% for misleading metadata. Adaptive sensing averages 3.89 observations per trial; the other original conditions use three. Added fixed four- and five-observation schedules achieve 86.75% and 90.74%. These results apply to the specified binary task. The manuscript and `results/summary.json` report paired differences, uncertainty, costs and assumptions.

The paper, *Active Inference as a Meta-Pragmatic Framework: Executable Models, Evidence, and the Discipline of Revision*, connects executable specification to evidence, values and fallible inquiry. Its 53 cited records include the requested Zenodo works, an explicit OODA comparison, primary readings of Peirce, James, Dewey, Addams and Mead, and COPE's authorship guidance. The [OODA revision](docs/ooda_pragmatism_revision.md) records the condensed argument; [research integrity](docs/research_integrity.md) documents AI assistance, author responsibility, supplied affiliations, access conditions and the current 0.35-inch page margins. Twelve numbered figures include an early quadrant map, diagrams of the executed models and a supplementary atlas of actual GNN tensors. The two-paragraph abstract states the proposal, methods, qualitative findings and limits, with the complete repository URL displayed as a link. Extensive methods, sensitivity analyses and notation are consolidated in technical supplements. The first-page scientific graphical abstract remains generated from retained numerical evidence. All publication figures use larger shared typography, clearer panel layouts and explanatory captions; see [figure readability](docs/figure_readability.md). See [main paper and supplements](docs/editorial_structure.md), [scholarship scope](docs/meta_pragmatic_scholarship.md), [world sampling](docs/world_simulation.md) and [exact robustness](docs/model_robustness.md).

## Repository guide

| Location | Purpose |
|---|---|
| `src/core/` | Probability contracts, inference and free-energy mathematics |
| `src/framework/` | Taxonomy, illustrative meta-cognition/modeler/security APIs |
| `src/analysis/` | Generators, statistics, validation and experiments |
| `src/visualization/` | Educational and source-backed experiment figures |
| `src/utils/` | Figure registry, Markdown, manuscript rendering, provenance |
| `scripts/01_*.py` through `05_*.py` | Educational diagrams under `output/figures/` |
| `scripts/06_insert_all_figures.py` | Strict manuscript validation; `--render` builds HTML |
| `scripts/07_analysis_pipeline.py` | Standalone research workflow |
| `scripts/08_render_with_template.py` | Pinned template PDF/HTML publication editions |
| `scripts/09_validate_documentation.py` | Documentation index and local-link validation |
| `manuscript/` | Numbered manuscript source and curated bibliography |
| `results/` | Retained numerical evidence, manuscript and figures |
| `docs/` | Methods, API, architecture, scholarship and review notes |

[Documentation index](docs/README.md) · [Quickstart](docs/quickstart.md) · [Methods and interpretation](docs/theoretical_primer.md) · [API](docs/api_reference.md) · [Architecture](docs/architecture.md) · [Scholarship audit](docs/scholarship_audit.md) · [Review record](docs/review_2026-10-13.md)

## Citation and license

Cite Daniel Ari Friedman, *Active Inference as a Meta-Pragmatic Framework: Executable Models, Evidence, and the Discipline of Revision*, version 1.0.0, DOI [10.5281/zenodo.23397453](https://doi.org/10.5281/zenodo.23397453). [CITATION.cff](CITATION.cff) supplies machine-readable author, affiliation, ORCID and release metadata. This is a preprint; public availability and DOI registration do not imply peer review. Funding and competing-interest declarations remain unspecified.

Software license: [Apache-2.0](LICENSE).
