# Appendix {#sec:appendix}

## Derivation checks {#sec:mathematical_foundations}

Expanding $D_{\mathrm{KL}}(q_o\Vert p_C)$ gives $-H(q_o)-\mathbb E[\log p_C]$. Adding ambiguity $\mathbb E_{q_s}H(A_{:,s})$ gives $-I(s;o)-\mathbb E[\log p_C]$, establishing Equation \eqref{eq:efe}. Replacing normalized log preferences with logits subtracts $\log\sum_o\exp(C_o)$ per policy step. This constant affects reported magnitudes but not a fixed-model, fixed-convention policy ranking.

For VFE, substitute $p(o,s)=p(s\mid o)p(o)$ into Equation \eqref{eq:vfe}. The log-evidence term factors out of the normalized expectation, leaving posterior KL divergence. With $q=p(s\mid o)$ the divergence is zero. Exact-zero handling uses $0\log0=0$ and retains infinite divergences for support violations.

Tests additionally compare batched binary log-odds inference with sequential core Bayesian updates, check asymmetric column-stochastic transitions, and check preference-shift and horizon-aggregation identities. Mathematical identity tests complement software coverage; coverage alone does not establish theoretical correctness.

## Retained experiment results {#sec:validation_results}

| Condition | Accuracy (%) | Brier loss | Log loss (nats) | Observations/trial |
|---|---:|---:|---:|---:|
| Q1_fixed | 76.36 | 0.1781 | 0.5519 | 3.000 |
| Q2_metadata | 84.68 | 0.1235 | 0.4051 | 3.000 |
| Q3_adaptive | 90.34 | 0.0812 | 0.2896 | 3.892 |
| Q4_learned | 84.68 | 0.1258 | 0.4114 | 3.000 |
| Q2_misleading | 54.12 | 0.3306 | 1.1861 | 3.000 |

| Contrast | Difference (percentage points) | 95% bootstrap interval | Paired d_z | Holm sign-flip p |
|---|---:|---|---:|---:|
| H1 | 8.325 | [7.442, 9.217] | 3.439 | 0.00030 |
| H2 | 5.658 | [5.058, 6.267] | 3.275 | 0.00030 |
| H3 | 8.325 | [7.442, 9.217] | 3.439 | 0.00030 |

These estimates are computed from `results/summary.json`. Each comparison uses 30 paired seed means. The primary p-values are Monte Carlo sign-flip estimates at finite resolution, with Holm correction across H1--H3. The intervals are marginal percentile-bootstrap intervals; they are not adjusted simultaneous intervals. The supplementary paired t-tests and full seed-level data are retained in the artifact set.

## Implementation and complexity {#sec:implementation_architecture}

`core` defines categorical models and exact inference. `framework` supplies the taxonomy, monitoring illustrations, and structural security diagnostics. `analysis` contains generators, statistics, validation, experiments, and pipeline orchestration. `visualization` creates educational and experiment figures; `utils` supplies manuscript validation and provenance. No parent repository infrastructure is required by the research pipeline.

For a dense model with S states, O observations, A candidate actions and horizon H, a single H-step policy costs approximately $O(H(S^2+OS))$ for transitions and predictions, with $O(OS)$ likelihood entropy preprocessing. Evaluating K candidate policies multiplies the per-policy cost by K. The implementation does not claim sparse scaling or measured support for 1,000-state models. No runtime table is reported without a retained benchmark protocol and hardware description.

## Reproduction protocol {#sec:reproducibility}

Run from a clean checkout:

```bash
uv sync --locked --extra dev --extra research --python 3.12
MPLBACKEND=Agg uv run --python 3.12 pytest --cov=src --cov-report=term-missing
uv run --python 3.12 python scripts/07_analysis_pipeline.py
```

The pipeline writes the source-backed results and standalone HTML manuscript to `results/`. Changing seed counts, trial counts, training size, numerical libraries or model configuration creates a different run, which must be described as such. Random-number generators are local; reproducibility does not rely on global `numpy.random.seed`. Source and output digests support verification within a recorded environment. PDF figure metadata or library/platform differences can change binary hashes without changing numerical estimates.

The older scripts 01--05 generate educational diagrams under `output/figures/`; those illustrations are separate from the retained experiment evidence. Script 06 validates the manuscript rather than inserting unreviewed or stale figures automatically.
