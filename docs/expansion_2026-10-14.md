# Further statistical and scholarship expansion

This is the earlier expansion record. The subsequent [active-sensing and graphical-abstract revision](active_sensing.md) supersedes its cover, manuscript, figure, test and digest counts.

This expansion builds on [the GNN revision](revision_2026-10-14.md) in the same owned worktree and branch. It preserves the original experiment design and H1–H3 family, adding exploratory analyses of the retained evidence. It is version 1.2.0 working-tree content over base `c59dd008b5e7b6fd9faec1e3d522889fc143de74`.

## Scientific additions

- Six paired contrasts across accuracy, Brier loss, log loss and observation cost, yielding 24 estimates with marginal bootstrap intervals and explicitly unadjusted secondary sign tests.
- Eleven fixed stopping thresholds on common test outcomes, retaining 330 seed-by-threshold metric rows and 44 aggregate estimates. No tuned policy is selected or independently validated.
- Exported occupied calibration bins at 5, 10 and 20 resolutions, with counts and represented seeds; 210 independently recomputed seed-by-strategy rows.
- Two new evidence figures in PNG/PDF/SVG, bringing the manuscript to six numbered figures plus its conceptual first-page cover.
- Eight further primary records, giving 35 cited records. Expanded synthesis distinguishes Bayesian workflow, predictive evaluation, classifier and probability calibration, simulation-based calibration, resource rationality and sensitivity analysis. Reading/access scope is retained in [the source supplement](scholarship_revision_2026-10-14.md).

Public APIs and exact meanings of the exploratory tables are documented in [exploratory diagnostics](exploratory_diagnostics.md). The original study's 30 independent seeds, 12,000 held-out trials, separate training, actual GNN parser import and model limitations remain explicit.

## Validation and artifact record

Focused real-computation checks passed before canonical reproduction: 44 tests, including 19 new diagnostic tests. Analytical controls check known accuracy/Brier differences, exact binomial probabilities, endpoint bin allocation, invalid inputs, all-tied pairs and original-rule reproduction through the real GNN parser.

All 584 tests pass independently on actual external Python 3.11.15, 3.12.13 and 3.13.14 environments. Virtual-environment and base-interpreter prefixes resolve on GitVault. Unit/integration branch coverage is 93.53%; including actual unmodified template CLI and worker execution raises it to 95.20%. Both new modules have 100% measured statement/branch coverage in the full suite. The 90% gate and 95% target are unchanged.

The full canonical pipeline passes. It retains 159 occupied calibration-bin rows, 210 seed metric rows, 24 paired estimates, 330 stopping-seed rows and 44 stopping-summary rows. Manuscript validation finds 13 sections, 27 labels, 35 unique cited/bibliographic records and six numbered figures. Documentation validation checks 24 indexed guides, 41 files and 73 local links. The focused Python rules checker and focused Ruff error checks pass for the added files.

The wheel and source distribution build. The rebuilt wheel reinstalls in an external environment and runs from outside the checkout: the imported diagnostics resolve to site-packages, analytical scores pass, and the actual GNN model import succeeds. The declared minimum remains Python 3.11.

The actual template remains pinned and tracked-clean at `192c8bda16c08d06ae2fee4eac71d56901d3ad22`. Its combined PDF is 20 pages. Every page was rasterized and inspected, including cover, equations, all six figures, statistical tables and all references. The compiler reports no undefined references or overfull boxes; its retained warnings concern an adjusted float specifier and unused table caption setup. The PDF is not tagged. The HTML contains seven loaded images with descriptions, 35 references and 63 MathJax expressions, with zero MathJax errors and broken internal anchors. Desktop 1280px and mobile 390px widths show no horizontal document overflow. The separate offline MathML edition is regenerated from the same source.

The refreshed manifest records 125 source-file and 130 output digests; the template receipt additionally identifies 42 renderer outputs. Physical bytes and the corresponding 255 staged Git blobs are checked against the research digests. A deliberately corrupted digest is rejected as a negative control. The 57 selected GNN specifications also match both their declared content hashes and the exact current selection.

Evidence is retained under ignored `output/expansion-evidence/`, including the final provenance receipt. This record does not claim independent external review, publication, a commit, or a remote push. All owned changes are staged on `codex/gnn-manuscript-revision`; main remains at the recorded base commit.
