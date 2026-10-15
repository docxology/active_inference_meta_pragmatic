# Manuscript syntax

Numbered Markdown sections 01--11, 98 and 99 are the manuscript source. Supporting README/AGENTS/preamble/config files are excluded from section composition. Heading IDs use Pandoc syntax, for example `# Methodology {#sec:methodology}`.

Equations and figure environments use fenced raw-LaTeX blocks. Assign unique `eq:` and `fig:` labels and refer to them with `\eqref{...}` or `\ref{...}`. The preview renderer translates supported mathematics to MathML; the publication renderer uses the template's Pandoc/LaTeX path. Unsupported equations must fail rather than disappear.

Use `\cite{key}` with a unique entry in `manuscript/references.bib`. Author figure paths explicitly relative to the manuscript directory. The validator checks duplicate/unresolved labels, citation keys and missing figure files. Keep captions explicit about analytical curves versus sampled results and costs.

Configuration metadata belongs in `manuscript/config.yaml`. The preamble's fenced LaTeX contains only required packages and layout choices. Change source syntax to repair rendering issues; generated LaTeX and PDF files are derivatives.

The [editorial structure](editorial_structure.md) separates the main argument from technical supplements without changing numbered source discovery. Keep the abstract at two prose paragraphs, put shared quadrant orientation before downstream references, and define notation in `98_symbols_glossary.md`. Extensive mathematics and numerical protocol belong in `11_appendix.md`; their labels remain the cross-reference authority. New model diagrams must draw their tensor values/edges from the imported specifications and record model digests in the figure registry.
