# Methodology {#sec:methodology}

## Study type and inferential scope

This is a conceptual framework with a synthetic computational demonstration. The taxonomy was not derived from empirical clustering and is not tested as a biological partition. The experiment tests concrete mechanisms inspired by its quadrants. The mechanisms are implemented in `src/analysis/experiments.py`; the narrative quadrant class supplies definitions and examples, rather than four independently validated algorithms.

The design below is fixed in code and recorded in each output manifest. It is not a preregistered study. Historical numerical claims in earlier manuscript versions lacked a corresponding experiment and are superseded by the retained results reported here. No participant data, clinical outcomes, or deployment incidents are analyzed.

## Generative task and controls

Each test trial independently draws a binary hidden state from a uniform prior. Five conditionally independent binary sensors agree with that state with probabilities $(0.55,0.65,0.85,0.80,0.80)$. Every strategy sees the same pre-generated test states and observations within a seed. The first three sensors are the common initial evidence. The state remains fixed within a trial and resets independently between trials.

- **Q1 fixed:** inference assumes reliability 0.80 for each of the first three sensors.
- **Q2 metadata:** inference uses the true, sensor-specific reliabilities for the same three observations. This is an oracle-metadata condition.
- **Q3 adaptive:** starts from Q2, then acquires a fourth and, if needed, fifth observation while the maximum posterior probability is below 0.90. Its cost is the actual observation count, with a maximum of five.
- **Q4 learned:** estimates the first three reliabilities from 200 separate labeled training trials per seed, using a Beta(1,1) prior. Parameters are frozen before held-out evaluation. It uses exactly three test observations.
- **Misleading metadata:** uses claimed reliabilities $(0.95,0.85,0.55)$ for the first three sensors. This prespecified adverse control reverses the ordering of sensor quality.

Q3 changes available evidence, whereas Q4 changes fitted likelihood parameters. They are not matched to Q1 on every resource. We report these differences rather than attributing all gains to a generic meta-level capacity. The confidence score controlling Q3 is maximum posterior probability; it is not the composite heuristic returned by `MetaCognitiveSystem`.

## Replication, randomness, and outcomes

Thirty independent seeds (0--29) generate 400 held-out trials each. A `SeedSequence` spawns distinct training and test streams. Labels from test trials are used only for scoring. The training and held-out streams are not used to tune the threshold, prior, or hypotheses. Equal posterior probabilities select state zero deterministically.

The primary outcome is held-out accuracy. Secondary descriptive outcomes are mean Brier loss, logarithmic loss in nats, and observations per test trial. Lower loss is better. Accuracy alone may conceal confidence errors, and a high posterior is not evidence of calibration under misspecification.

The three directional predictions concern (H1) Q2 versus Q1 accuracy, (H2) Q3 versus Q2 accuracy with additional sensing, and (H3) Q4 versus Q1 accuracy after separate training. The comparisons are operationalizations of these mechanisms, not claims that every quadrant extension improves accuracy. Two-sided tests retain the possibility of harm.

## Statistical analysis

The inferential unit is a seed-level mean, yielding 30 paired replicates per comparison; the 12,000 test trials are not treated as 12,000 independent agent replicates. The common-random-number design reduces comparison noise. We report mean paired differences with 95% percentile-bootstrap intervals from 5,000 resamples of seeds, using bootstrap seed 42. Intervals are marginal, not simultaneous family-wise intervals.

Primary test evidence is a two-sided paired sign-flip test using 10,000 Monte Carlo resamples (seed 2718) with a plus-one correction. Its validity requires exchangeability of signs under the paired null; it is not an exact finite-sample test for arbitrary differences. Holm correction applies to the family of three primary comparisons. Paired t-tests and standardized within-pair differences $d_z=\overline{\Delta}/s_\Delta$ are supplementary. Effect-size conventions are explicit; large standardized differences across low-noise seed averages do not imply large population effects in human cognition.

The pipeline also checks 200 two-step policy evaluations across 50 randomly generated models against the risk-plus-ambiguity identity, and checks the VFE evidence decomposition. These check the implementation under specified numerical contracts, not the truth of the FEP as a physical theory. Deterministic and impossible-evidence cases are included in regression tests.

## Evidence retention

`results/trials.csv` retains test states, sensor outcomes, strategy probabilities, and Q3 sensing counts. `results/replicates.csv` retains all seed-level metrics. `results/summary.json` contains intervals, tests, design parameters and limitations; `results/efe_sensitivity.csv` contains the exact curves. `results/manifest.json` hashes source files, configuration, environment versions and output artifacts. The Git revision is the base revision; source digests identify the executed working-tree content.

```{=latex}
\begin{figure}[h]
\centering
\includegraphics[width=0.95\textwidth]{../results/figures/quadrant_experiment.png}
\caption{Synthetic held-out outcomes. Dots show independent seeds and intervals show 95 percent bootstrap confidence intervals for seed means. Q3 consumes additional observations and Q4 uses external labeled training. Misleading metadata is an adverse control.}
\label{fig:quadrant_experiment}
\end{figure}
```
