# Quickstart

Run from this repository with Python 3.11 or newer. Numerical reproduction imports the pinned GNN reference parser. Set `GNN_ROOT` to the actual `Generalized_Notation_Notation` checkout at the revision in `src/core/gnn_models/upstream.lock.json`; canonical GitVault placement is detected automatically. Publication rendering uses the separately configured, pinned docxology/template checkout.

```bash
uv sync --locked --extra dev --extra research
uv run python scripts/07_analysis_pipeline.py --dry-run
MPLBACKEND=Agg uv run pytest --cov=src
uv run python scripts/07_analysis_pipeline.py
uv run python scripts/06_insert_all_figures.py --render
```

Open `results/manuscript.html` in a browser. The equations use native MathML and require no external JavaScript. Keep its `figures/` directory alongside it. Numeric data and estimates are in `trials.csv`, `replicates.csv`, `efe_sensitivity.csv` and `summary.json`; `manifest.json` records source and output hashes.

For a shorter run, use `--seeds 6 --trials 80 --training 80 --output-dir /path/to/new-run`. Such outputs are a separate design, not a reproduction of the retained manuscript estimates. The manuscript source refers to the canonical `results/figures/` assets; a custom output directory does not rewrite those authored references.

```python
from core.generative_models import create_simple_generative_model
from core.active_inference import ActiveInferenceFramework

model = create_simple_generative_model()
beliefs = model.perform_inference(0)          # observed category zero
soft = model.perform_inference([0.8, 0.2])    # normalized virtual evidence
agent = ActiveInferenceFramework(model, precision=2)
policy, info = agent.select_optimal_policy([[0], [1]], beliefs)
score, parts = agent.calculate_expected_free_energy(beliefs, policy)
assert abs(parts["normalized_total"] - parts["risk"] - parts["ambiguity"]) < 1e-12
```

The category and soft-evidence conventions differ deliberately. Invalid probabilities, mismatched dimensions and impossible evidence raise `utils.exceptions.ValidationError`. The tests include analytical expectations and real filesystem workflows; they use no mocks.

For publication editions, run `uv run python scripts/08_render_with_template.py --template-root /path/to/template` after installing the template environment and TeX tools. Then run `uv run python scripts/09_validate_documentation.py`. See [rendering](rendering_pipeline.md) for setup and [outputs](output_conventions.md) for provenance refresh order.
