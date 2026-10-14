# Workflows

From the repository root, install research extras with `uv sync --locked --extra dev --extra research`.

- `uv run python scripts/07_analysis_pipeline.py`: reproduce checks, held-out synthetic experiment, figures, evidence, manuscript HTML and provenance in `results/`.
- `uv run python scripts/07_analysis_pipeline.py --dry-run`: inspect stages without output writes.
- `uv run python scripts/06_insert_all_figures.py --render`: validate authored references and rebuild HTML.
- Scripts `01_generate_quadrant_matrix.py` through `05_generate_security_figures.py` create educational illustrations under `output/figures/`. Those figures do not constitute the retained experiment.

The standalone pipeline has six stages. Requested later stages execute preceding dependencies. CLI failures propagate as nonzero exit status.

- `uv run python scripts/08_render_with_template.py --template-root /path/to/template`: produce the pinned template PDF/HTML editions and rendering receipt.
- `uv run python scripts/09_validate_documentation.py`: validate the modular documentation index and actual local links.

See [rendering](../docs/rendering_pipeline.md) and [documentation](../docs/README.md).
