# Statistical analysis

The inferential unit is an independent seed-level mean. The canonical run supplies 30 paired replicates, 150 condition-by-seed metric rows and 12,000 test-trial rows. Trial rows retain the observations and predictions needed to audit each metric; they are not treated as 12,000 independent agent replicates.

The primary accuracy contrasts are H1 Q2 minus Q1, H2 Q3 minus Q2 and H3 Q4 minus Q1. Mean paired differences receive marginal 95% percentile-bootstrap intervals with 5,000 seed resamples and bootstrap seed 42. A two-sided Monte Carlo paired sign-flip test uses 10,000 sign samples, seed 2718 and a plus-one correction. Holm adjustment applies to the three primary p-values. Sign exchangeability under the paired null is an assumption; the test is not exact for arbitrary distributions of paired differences. Marginal intervals do not supply simultaneous family-wise coverage.

Paired t-tests and `d_z = mean(difference) / sample_sd(difference)` are supplementary. Large standardized effects across low-noise synthetic seed averages do not imply large human-cognition effects. Independent-sample helpers separately report signed pooled Cohen d and Hedges g; those denominators must not be substituted for paired d_z.

The canonical mean accuracy gains are 8.325 percentage points for H1/H3 and 5.658 for H2. Retained intervals, corrected p-values and resource costs are in `results/summary.json`; use that file when quoting exact precision. Figures display seed distributions and marginal intervals, and plot accuracy, calibration loss and sensing cost together.

Helpers reject nonfinite samples, single-observation confidence intervals and constant correlations. Degenerate t-tests explicitly return `test_defined=False` with undefined t/p fields. Software validation, test coverage and numerical identity residuals are separate evidence from statistical findings.
