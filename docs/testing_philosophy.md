# Testing and validation

The extracted [world sampler](world_simulation.md) is checked against stochastic transition/observation frequencies and the original seeded draw sequence. The [exact robustness evaluator](model_robustness.md) is checked against independent closed-form scores, with separate negative controls for impossible observations and zero forecast support. GNN serialization tests preserve authored nonparameter assignments and reject missing/duplicate sections. Integration tests require actual new CSV/model/figure exports.

Tests use real numerical computations, generated data and temporary files. No mocking framework is used. Important contracts are checked against analytical expectations: asymmetric column-stochastic transitions, exact zero support, categorical/virtual evidence, impossible evidence, preference-shift invariance, VFE evidence bounds, EFE risk-plus-ambiguity identities, paired statistics and actual workflow artifacts.

```bash
MPLBACKEND=Agg uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/07_analysis_pipeline.py
uv run python scripts/06_insert_all_figures.py
uv run python scripts/09_validate_documentation.py
uv build
```

The coverage gate is 90%, with 95% a target. Coverage is a software exercise metric, not a theoretical-correctness percentage. The research pipeline tests multiple random models and policies, while deterministic regressions check edge cases. Package smoke checks install the wheel outside the checkout to catch src-layout import failures.

CI is configured to validate the research package on Python 3.11, 3.12 and 3.13, including reproduction, manuscript/documentation validation and package building. Both jobs check out the pinned GNN source and set `GNN_ROOT`. A separate job checks out the pinned public template, installs its rendering requirements and generates the publication editions. Local PDF/HTML review additionally checks readable equations, citations, tables, figures, internal links and layout.

On 2026-10-14, all 534 tests passed locally on Python 3.10, 3.12 and 3.13. Python 3.10 on Apple Silicon uses the scoped SciPy 1.14.1 compatibility fallback. Unit/integration branch coverage was 93.43%; combining these checks with actual template-worker/CLI execution gave 95.04%. The GitHub Actions run could not start because the account's Actions budget prevented further use; local success is not reported as cloud CI success.

The declared Python minimum concerns the research package; the external template may require a newer interpreter. Keep its environment separate. Numerical validation and CI do not independently replicate the science or certify biological/security claims.
