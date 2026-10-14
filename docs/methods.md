# Experimental methods

`analysis.experiments.ExperimentConfig` fixes the canonical synthetic design: 30 independent seeds, 400 held-out trials per seed and 200 separate labeled training trials per seed. Each trial has a uniform binary state and five conditionally independent binary sensors with reliabilities `(0.55, 0.65, 0.85, 0.80, 0.80)`. A seed's strategies share its test states and sensor outcomes; training and test streams are spawned separately with `numpy.random.SeedSequence`.

| Condition | Mechanism | Resources |
|---|---|---|
| Q1 fixed | Assumes reliability 0.80 for the first three sensors | Three test observations |
| Q2 metadata | Uses the true first-three sensor reliabilities | Three observations and privileged metadata |
| Q3 adaptive | Adds sensor four/five while maximum posterior is below 0.90 | Three to five observations |
| Q4 learned | Fits first-three reliabilities with Beta(1,1) updating, then freezes them | Three observations plus separate labeled training |
| Misleading metadata | Assumes `(0.95, 0.85, 0.55)` for the first three sensors | Three observations and incorrect metadata |

The state is fixed within a trial and independently reset between trials. Equal posterior probabilities select state zero. Held-out labels are used for scoring. The threshold, prior and contrasts are fixed in code; this is not a preregistered study. Outcomes are accuracy, Brier loss, log loss in nats and actual observation count.

The design measures state estimation, acquisition and reliability learning. It does not compare full EFE planners or establish a biological quadrant partition. Q2 has an oracle advantage, Q3 purchases extra evidence, and Q4 uses external labels. These costs constrain any comparison. See [statistics](statistics.md) for the seed-level inference and [theory](theoretical_primer.md) for the separate EFE/VFE identities.

`--seeds`, `--trials` and `--training` create a different design. Use a separate `--output-dir` and disclose changes; the authored paper's default estimates are not automatically rewritten for a custom experiment.
