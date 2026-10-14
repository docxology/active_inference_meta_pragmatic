.PHONY: install test reproduce validate render
install:
	uv sync --locked --extra dev --extra research

test:
	MPLBACKEND=Agg uv run pytest --cov=src --cov-report=term-missing

reproduce:
	uv run python scripts/07_analysis_pipeline.py

validate:
	uv run python scripts/06_insert_all_figures.py --render
	uv run python scripts/09_validate_documentation.py

render:
	uv run python scripts/08_render_with_template.py --template-root "$(TEMPLATE_ROOT)"
