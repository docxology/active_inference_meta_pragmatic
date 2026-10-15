# Release history

## 1.0.0 — 2026-10-15

First public release of *Active Inference as a Meta-Pragmatic Framework: Executable Models, Evidence, and the Discipline of Revision* and its reproducible research software. Manuscript/research archive DOI: [10.5281/zenodo.23397453](https://doi.org/10.5281/zenodo.23397453). This is a preprint, without claimed peer review or independent replication.

- Import actual upstream GNN specifications through the pinned reference parser; retain the categorical execution boundary and specification hashes.
- Correct probability contracts, Bayesian evidence semantics, transition orientation, exact VFE and normalized EFE.
- Retain separate training and held-out evaluation, 30 independent sensor-study seeds, paired inference, bootstrap intervals, sign-flip tests, Holm correction and resource accounting.
- Add executed EFE action selection, exact world–agent mismatch analysis, proper-score diagnostics and adverse metadata controls.
- Provide the two-paragraph abstract, 53 cited sources, twelve numbered figures, scientific graphical abstract, technical supplement and common notation reference.
- Include the author's affiliations and ORCID, AI-assistance disclosure, modular documentation, pinned-template PDF/HTML editions and source/output provenance.

### How earlier development labels relate to this release

Internal source and manuscript markers included 1.1.0, 1.2 and 1.2.0 before a public release series existed. They were development labels, not prior GitHub releases or Zenodo versions. The author selected **1.0.0 as the first public release**. Existing commits are preserved; no history is rewritten to conceal that transition.

| Commit | Date | Historical role |
|---|---|---|
| `21a93690d263a70dcd9bceb50d755abfde472413` | 2026-06-12 | Initial private project snapshot; superseded scientific claims are not current results. |
| `5d18bc120d73c285ce46fff82e917406815de251` | 2026-10-14 | Rebuilt methods, evidence, documentation and actual template rendering. |
| `c59dd008b5e7b6fd9faec1e3d522889fc143de74` | 2026-10-14 | Scoped Python 3.10 Apple Silicon compatibility in the earlier dependency set. Current package support starts at Python 3.11. |
| `58b28717afcb37080a47571294650f01281cd9bc` | 2026-10-15 | Reviewed GNN/manuscript checkpoint immediately before public release preparation. |

The annotated `v1.0.0` tag identifies the release tree. GitHub preserves its ancestry; the release's Git bundle retains that same history for offline inspection. Later publication-verification commits may advance `main` without moving the tag. [Release documentation](docs/release_v1.0.0.md) distinguishes local checks, remote publication and archival verification.
