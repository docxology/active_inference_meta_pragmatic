# Figure readability and publication verification

The [inquiry-role guide](inquiry_roles.md) defines Q1–Q4 on the cover and the shared names used across conceptual diagrams. Strategy keys, line styles, action labels and uncertainty encodings support comparisons across the figures.

All thirteen publication visuals, including the scientific graphical abstract, use the shared `visualization.publication_style` module. The source canvas is 8.5 inches wide. Base type is 14 points, tick and legend type is at least 12 points, and the exporter enforces a 12-point minimum on every Matplotlib text object before writing PNG, PDF and SVG. Final printed size also depends on the manuscript placement; inspect the rendered pages after any change.

The model and diagnostic comparisons use stacked panels where side-by-side panels compressed labels. The matrix atlas presents nine probability panels and explicit preference/prior vectors. Values and labels come from the three real imported GNN specifications. Signed preference logits remain distinct from normalized probabilities. The compact strategy codes in the main experiment have an explicit figure key.

Each numbered caption explains its encodings, units, uncertainty and scope. Conceptual maps, exact enumerations and paired seed estimates are identified separately. Marginal intervals are not substituted for intervals on paired contrasts; seed dots retain the independent experimental units. Resource counts remain visible alongside predictive scores.

## Reproduction

Run the research pipeline with `--update-cover` to explicitly refresh the source graphical abstract, then render through the pinned actual template. See [Rendering](rendering_pipeline.md) for the complete commands and [Outputs and provenance](output_conventions.md) for manifest order. Ordinary tests and pipeline runs do not silently replace the source cover.

`tests/test_publication_style.py` uses an actual four-point label as a negative control for the font floor, preserves larger type, and verifies real SVG/PDF exports. Integration tests execute every publication plotting module. Inspect all generated figures and the actual PDF pages; font-size assertions alone cannot detect overlap or a crowded caption.

The two-paragraph abstract emphasizes accountable inquiry. Section titles distinguish commitments, situated action, evidence and revision. The [scholarship record](meta_pragmatic_scholarship.md) documents source identities and reading limits. Hyperlinks remain red. The PDF is not claimed to be tagged or fully accessible.
