# Outputs and provenance

Current [world–agent robustness outputs](model_robustness.md) add two CSV tables, a three-format figure and `results/robustness_gnn/`. Their selected specification digests are in `summary.json`. Existing sensor and action-study selections retain their own directories; identical models can appear in more than one study's evidence set. The manifest binds each path's bytes.

| Location | Contents |
|---|---|
| `results/trials.csv` | Held-out states, observations, predictions and sensing counts |
| `results/replicates.csv` | Seed identifiers and condition-level accuracy/loss/cost |
| `results/summary.json` | Configuration, estimates, tests, limits and mathematical checks |
| `results/efe_sensitivity.csv` | Exact model-based EFE curves |
| `results/gnn/` | Content-addressed GNN sensor realizations selected by the current summary |
| `results/figures/` | Registered research PNG/PDF/SVG figures |
| `results/manuscript.html` | Offline MathML preview |
| `results/template/` | Upstream-rendered publication editions and rendering receipt |
| `results/manifest.json` | Source, environment, configuration and output digests |
| `output/` | Ignored educational figures and rendering intermediates |

The default evidence is synthetic and retained in Git. Runtime environments, caches, coverage files, build products and compiler intermediates are ignored. Keep HTML assets/figures beside the edition when copying it.

`utils.provenance.write_manifest` records SHA-256 digests and versions without embedding credentials or machine-specific source paths. Its Git field is a base revision; the source hashes identify the executed working tree. It excludes itself to avoid a self-referential hash cycle. `renderer_manifest.json` separately pins the external template and tools.

The correct rebuild order is research pipeline, template rendering, visual/content checks, then manifest refresh. A rerender changes artifact digests and therefore requires a refreshed research manifest. A custom experiment is distinct evidence and must not silently replace the default manuscript's estimates.

Git attributes preserve the exact bytes of retained outputs across checkouts. CSV CRLF record separators and Matplotlib SVG path whitespace are valid producer formatting; their scoped whitespace rules do not relax source-code checks. Before publication, staged Git blobs are checked against the recorded source/output digests.

The authoritative GNN selection is `experiment.gnn.specifications` in `results/summary.json`. The sensor study retains 57 selected realizations. Directory contents must agree with each study's selected digests; a directory scan must not widen that selection.
