# Frequently asked questions

**Does a higher quadrant always perform better?** The taxonomy organizes mechanisms. The measured effects apply to one synthetic task, with privileged metadata, extra sensing or labeled training. Incorrect metadata harms this example.

**Is the experiment an EFE planning benchmark?** It measures state inference, sensing and reliability learning. Exact EFE identities and sensitivity curves are evaluated separately.

**Are 12,000 trials the statistical sample size?** There are 30 independent paired seed-level replicates. Trial rows support scoring and auditability; see [statistics](statistics.md).

**Is the software a clinical or security validation?** Structural/numerical checks and illustrative anomaly thresholds do not establish clinical benefit, absence of tampering or security effectiveness.

**Which rendering is authoritative?** Publication editions in `results/template/` use the pinned [template integration](rendering_pipeline.md). The standalone MathML HTML is a convenient offline preview. Numbered manuscript source is authoritative for authored content.

**Can the project run without template?** Numerical reproduction and the preview can. Publication PDF/HTML generation explicitly requires the template checkout, its Python environment and rendering tools.

**Can I change seeds or training?** Yes; use a separate output directory and report the new design. Do not present those estimates as the retained default manuscript run.
