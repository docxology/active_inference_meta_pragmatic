# Utilities

Logging and exceptions are local. `FigureManager` registers and atomically persists figure metadata; corrupt registries are preserved before replacement. `MarkdownIntegration` detects headings and inserts explicit LaTeX figure blocks.

`manuscript.py` validates numbered sections and renders a standalone MathML HTML document. `provenance.py` hashes scientific sources, configuration, environment versions and outputs. See the repository API reference for supported contracts.

`documentation.py` validates the docs hub and local links. `template_rendering.py` invokes the pinned external combined renderers and records the HTML citation/equation/figure projection against actual PDF reference numbers. Figure registries retain accessible alt text. See [rendering](../../docs/rendering_pipeline.md).
