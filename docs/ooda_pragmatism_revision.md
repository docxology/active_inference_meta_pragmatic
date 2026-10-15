# OODA, a condensed pragmatist argument and publication layout

This page preserves the preceding 52-reference, 0.70-inch-margin build and its receipts. The later [research integrity revision](research_integrity.md) adds the AI-assistance disclosure and updates the bibliography and margins.

## Source and conceptual connection

The paper cites Scott David, Richard J. Cordes and Daniel A. Friedman, *Active Inference in Modeling Conflict* (2021), preprint v1.2, [Zenodo 5759807](https://zenodo.org/records/5759807), DOI 10.5281/zenodo.5759807. Official metadata and the PDF title page establish its identity. The downloaded file matches Zenodo's published MD5; the portable [source receipt](ooda_sources.json) records its SHA-256 and reading scope. Selected passages on printed pages 17–18 and 37–38, including Figure 9, explicitly connect OODA and active inference; the discussion on page 53 frames qualitative implications. This is conceptual scholarship, not empirical support for our numerical results. The source's linked Boyd collection returned HTTP 403 and was not treated as directly consulted.

Section 3's new subsection compares observe–orient–decide–act with the actual sensor and action tasks. Q1 updates beliefs and evaluates policies; Q2 contextualizes evidence; Q3 regulates further observation; Q4 evaluates a reliability model under external supervision. Those responsibilities cross OODA functions. The table does not force a one-to-one mapping or turn the one-step action experiment into a strategic conflict simulation. Section 6 points back to that distinction. See [philosophy](philosophy.md) and [GNN methods](gnn_models.md).

## Condensation and retained philosophical distinctions

The opening pragmatism discussion is 47.1% shorter by whitespace-delimited word count, from 1,039 to 550 words including headings: each author now motivates a concrete modeling question, and the repetitive summary table is removed. All primary citations remain. Peirce concerns correction of commitments; James concerns experiential consequences and verification; Dewey concerns reflective inquiry and the reconstruction of ends; Addams concerns whose experience can challenge evaluation; Mead concerns shared meaning. Public criticism and social formation of purposes remain outside the implemented single-agent mechanisms. The focused bibliography now has 52 cited records. [American Pragmatism](american_pragmatism.md) preserves the consulted primary passages and the preceding visual build's historical receipts.

## Print layout and reproduction

`manuscript/preamble.md` supplies `geometry` with 0.70-inch margins (17.78 mm), reduced from the unmodified template's 0.75-inch default. Publication links remain red and contents include subsections. The [rendering guide](rendering_pipeline.md) owns the reproduction commands; [output conventions](output_conventions.md) owns the order of rendering and provenance refresh. The numerical experiments, formalism, GNN specifications and figures have not been redesigned by this editorial change. Their retained results must still reproduce before delivery.

## Verification record

All 629 tests pass on actual Python 3.11.15, 3.12.13 and 3.13.14 environments with virtual-environment and base-interpreter paths on GitVault. Unit/integration combined statement/branch coverage is 94.53%; including actual pinned-template parent and worker execution gives 95.90% (96.88% statements and 92.65% branch opportunities). The documentation and manuscript validators and focused Ruff error checks pass. The rebuilt wheel installs outside the checkout and runs the documented numerical example; an invalid probability vector is rejected. These are authoring and software checks, not independent review.

The unchanged pinned template produces a 41-page PDF with 0.70-inch margins, 52 references, twelve numbered figures and the first-page graphical abstract. All pages were inspected as raster images, with full-size checks of the OODA table and the notation break corrected after the first render. Each long notation table now begins with its subsection heading. The final LaTeX log has no overfull boxes, unresolved references/citations or oversized floats. The two-level contents and red links are retained. The PDF is not tagged.

Browser content checks at the observed 1,169-pixel viewport find 13 loaded, described images, 52 references, 155 rendered mathematical expressions, no MathJax errors, no broken internal anchors and no horizontal document overflow. An initial preview transport failed to request eight images; its failures remain in the operational receipts. A fresh local server with a larger connection backlog loaded all thirteen original image URLs without altering the edition. Requested browser resizing did not change the measured viewport, so a new mobile-layout result is not claimed for this revision.

The sensor experiment, action-study and exact robustness summaries reproduce identically to the preceding build. All thirteen PNG graphics are byte-identical to that build; source/output and rendering provenance are refreshed for the new manuscript and editions. Operational logs, downloaded primary evidence and rasterized pages remain under ignored `output/ooda-revision-20261015/`. Changes are local and staged; no commit, push, upload or publication was performed.
