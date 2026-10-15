# Figure readability and publication verification

The latest [inquiry-role figure revision](inquiry_role_figures.md) defines Q1–Q4 directly on the cover and uses shared role names across conceptual diagrams. It also strengthens the strategy keys, line styles, action labels and uncertainty encodings described below.

All thirteen publication visuals, including the scientific graphical abstract, use the shared `visualization.publication_style` module. The source canvas is 8.5 inches wide. Base type is 14 points, tick and legend type is at least 12 points, and the exporter enforces a 12-point minimum on every Matplotlib text object before writing PNG, PDF and SVG. Final printed size also depends on the manuscript placement; inspect the rendered pages after any change.

The model and diagnostic comparisons use stacked panels where side-by-side panels compressed labels. The matrix atlas presents nine probability panels and explicit preference/prior vectors. Values and labels come from the three real imported GNN specifications. Signed preference logits remain distinct from normalized probabilities. The compact strategy codes in the main experiment have an explicit figure key.

Each numbered caption explains its encodings, units, uncertainty and scope. Conceptual maps, exact enumerations and paired seed estimates are identified separately. Marginal intervals are not substituted for intervals on paired contrasts; seed dots retain the independent experimental units. Resource counts remain visible alongside predictive scores.

## Reproduction

Run the research pipeline with `--update-cover` to explicitly refresh the source graphical abstract, then render through the pinned actual template. See [Rendering](rendering_pipeline.md) for the complete commands and [Outputs and provenance](output_conventions.md) for manifest order. Ordinary tests and pipeline runs do not silently replace the source cover.

`tests/test_publication_style.py` uses an actual four-point label as a negative control for the font floor, preserves larger type, and verifies real SVG/PDF exports. Integration tests execute every publication plotting module. Inspect all generated figures and the actual PDF pages; font-size assertions alone cannot detect overlap or a crowded caption.

The revised two-paragraph abstract emphasizes accountable inquiry. Section titles distinguish commitments, situated action, evidence and revision. The [scholarship record](meta_pragmatic_scholarship.md) documents the two additional primary references and the limits of the reading. Hyperlinks remain red. The PDF is not claimed to be tagged or fully accessible.

## Verified preceding typography revision

The counts below belong to the preceding build. The subsequent [cover and identity revision](cover_identity_revision.md) updates Figure 4, the author identity, scholarship and contents.

The actual pinned template produces a 39-page combined PDF with every numbered figure retained in its intended section. Page inspection identified deferred floats in the first enlarged build; explicit placement corrected them. The failed layout and its page images remain in the ignored revision evidence directory. Final LaTeX logs contain no overfull boxes or unresolved references. All thirteen SVGs contain live text with a minimum source font size of 12 points.

All 627 tests pass across Python 3.11, 3.12 and 3.13. Unit/integration coverage is 94.49% combined statement/branch coverage; actual template parent and worker execution brings it to 95.84% (96.83% statements and 92.57% branch opportunities). The shared exporter has 100% statement and branch coverage. The built wheel installs outside the checkout and generates real GNN model diagrams and atlas artifacts.

Manuscript validation resolves 44 citations, 44 bibliography entries and twelve numbered figures. The cover adds the thirteenth described image. The template HTML renders 153 mathematical expressions, with no MathJax errors or broken internal anchors. All images load, all hyperlinks compute to red, and observed desktop/mobile widths of 1280/390 pixels have no horizontal document overflow. Documentation validation covers 31 indexed guides, 48 files and 127 local links.

The retained experiment, active-sensing and exact mismatch summaries are compared with the preceding run; this is an editorial and visualization revision. These checks establish authoring and software evidence, not independent scientific review. Final source/output manifests and staged Git blobs bind the delivered artifacts to their actual source bytes.
