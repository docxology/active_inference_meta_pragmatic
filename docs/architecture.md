# Architecture

GNN import (`core.gnn`), section-scoped serialization (`core.gnn_serialization`), [world sampling](world_simulation.md), [exact world–agent evaluation](model_robustness.md), statistical summaries and figure production are separate modules. The pipeline composes them and owns exports; CLI scripts provide entry points. Every evaluated GNN realization is imported through the pinned reference parser before execution.

The standalone package uses a src layout with `core`, `framework`, `analysis`, `visualization`, and `utils` packages. The repository-level `src/__init__.py` reexports APIs for checkout use; canonical installed imports use the packages directly.

`core/probability.py` owns categorical probability contracts shared by models, inference, validation and diagnostics. This prevents row/column convention differences. `generative_models.py` and `active_inference.py` use those contracts; `free_energy_principle.py` distinguishes exact categorical mathematics from legacy illustrations.

`framework` contains the interpretive taxonomy, modeler examples, confidence/control heuristics and structural security diagnostics. These classes do not implement all of the hypothetical optimization equations in the earlier manuscript. `analysis/experiments.py` implements the concrete mechanisms evaluated in the retained study.

The research pipeline proceeds through mathematical checks, held-out experiments, source-backed figures, CSV/JSON export, manuscript validation/rendering, and a provenance manifest. Scripts are CLI/I/O coordinators; reusable calculations and plotting live in src. `core/gnn.py` imports the pinned upstream GNN parser and binds declared tensors to the exact categorical runtime. A separate adapter in `utils/template_rendering.py` invokes the pinned external docxology/template renderers for publication editions; neither adapter vendors upstream implementation code.

Training and held-out random streams are separate. Strategies share test states and sensor outcomes within a seed, preserving paired comparisons. Replicates retain the seed identity; trials retain states, observations and predictions. A manifest records configuration, source hashes, library versions and output digests. Its base Git revision can precede an uncommitted source change; source digests identify the executed content. The manifest excludes itself to avoid a hash cycle.

Manuscript references are authored explicitly. The validator checks numbered sections only, resolves citation keys against the curated BibTeX file, and verifies figure paths. The HTML renderer uses native MathML and linked references without external scripts. Figures remain beside the HTML artifact. Source Markdown is authoritative; rebuilding does not overwrite manuscript claims with estimates from a different configuration.

`utils/documentation.py` validates the modular docs index and actual local link targets. The optional template integration runs in its own interpreter and checks exact origin/revision/cleanliness. It uses the upstream canonical output layout for composition evidence, then retains successful editions under `results/template/`. See [rendering](rendering_pipeline.md).
