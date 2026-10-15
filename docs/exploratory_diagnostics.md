# Exploratory paired diagnostics

`analysis.diagnostics` analyzes the retained test predictions and five raw sensor outcomes. It fits no parameter and changes no original primary hypothesis. Script 07 runs it as part of stage 3 and exports its tables at stage 4. The threshold sweep executes the same real upstream GNN sensor specifications as the main experiment.

| Artifact in `results/` | Contents |
|---|---|
| `seed_metrics.csv` | Recomputed scores and costs for every strategy and seed |
| `paired_estimates.csv` | Six paired contrasts across four metrics; 24 rows |
| `calibration_bins.csv` | Occupied equal-width probability bins at 5, 10 and 20 bins, counts and represented seeds |
| `stopping_seed_metrics.csv` | Eleven fixed thresholds evaluated for each seed; 330 rows in the canonical run |
| `stopping_summary.csv` | Marginal intervals for four metrics at each threshold; 44 rows |

The six contrasts are metadata minus fixed, adaptive minus metadata, learned minus metadata, misleading minus metadata, adaptive minus fixed four, and adaptive minus fixed five. Every difference is treated minus control, so positive accuracy differences favor treatment and positive loss differences favor control. Costs are observations per trial, not time or energy. Scores are recomputed within each seed before comparison. Bootstrap seed 314159 and the configured number of resamples produce marginal 95% percentile intervals; the canonical count is 5,000. Reusing the bootstrap seed retains pairing across comparable estimates. Intervals have no simultaneous coverage guarantee.

Secondary binomial sign tests use the number of positive and negative nonzero differences, omit exact ties, and return one when all pairs tie. They test equal probabilities of the two signs conditional on a nonzero difference under independent seeds; they do not test the mean difference or require the sign-flip test's magnitude symmetry assumption. P-values are explicitly unadjusted and exploratory. No significant/non-significant labels are assigned, and the original H1–H3 Holm family is unchanged.

The eleven thresholds are 0.50, 0.55, ..., 1.00. Acquisition occurs when maximum posterior probability is strictly below the threshold, with at most five observations. The 0.50 endpoint reproduces three-observation metadata inference, 0.90 reproduces the original adaptive rule, and 1.00 reproduces five-observation inference for this strictly positive likelihood design. Thresholds reuse all held-out trials. Choosing one after inspection would make these trials selection data; it requires a fresh validation set.

Calibration tables estimate state-one frequency, not confidence in the predicted class. Probabilities exactly one enter the final bin. Empty bins have no empirical frequency and are omitted. Curves pool trials descriptively; the count and represented-seed columns expose sparse bins. Bin resolution is an analytical choice, not a calibrated uncertainty guarantee. Log loss uses the same machine-epsilon reporting floor as the original experiment; core Bayesian support remains exact.

The two new figures have PNG, SVG and PDF editions with registry descriptions. Tests use analytically known score differences, a binomial probability, exact endpoint bins, invalid inputs, and real GNN execution to reproduce the main study at thresholds 0.50, 0.90 and 1.00. See [statistics](statistics.md), [methods](methods.md), and [outputs](output_conventions.md).
