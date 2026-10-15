# Executed GNN active sensing and graphical abstract

The action-selection task complements the confidence-threshold sensor study with policies evaluated by exact normalized expected free energy. Its imported GNN model supplies world generation and agent computation. The scientific graphical abstract presents the inquiry roles and retained evidence.

## Model and execution

`analysis.active_sensing.active_sensing_model` declares four hidden states as binary context crossed with observation mode. Ordering is context-zero blind, context-one blind, context-zero informative, context-one informative. Action zero maps each context to its blind state; action one maps it to its informative state. Context is preserved by both column-stochastic transition slices. The fixed three-outcome likelihood emits a null outcome in blind mode and a noisy context indication in informative mode. Default reliability is 0.85, outcome preference logits are `(0.15,0,0)`, and initial beliefs are `(0.5,0.5,0,0)`.

The packaged `src/core/gnn_models/active_sensing.md` supplies the base model. Reliability/preference interventions revise its imported A/C values, retain its B/D tensors and pass each realization through `specified_model` into actual GNN Markdown, the pinned upstream `MarkdownGNNParser`, the supported categorical profile and the exact local runtime. GNN is the real specification/parser dependency. `ActiveInferenceFramework` evaluates both one-step policies and returns their actual posterior at precision 4. The experiment samples from that posterior; it does not confuse the returned minimum-score action with a sampled action. Core `bayesian_update` computes post-observation beliefs from the chosen transition and observed likelihood row. No schematic confidence or security score drives this task.

Let `I = log(2) - h(r)` and `Z = exp(c)+2`. Exact normalized EFE is `log(Z)-c` for blind and `log(Z)-I` for inspect. Consequently `P(inspect)=logistic(4*(I-c))`. The default exact probability is approximately 0.6182. Preferences are outcome logits, not measured rewards or observation costs. Finite precision retains stochastic choice even when one action has lower EFE.

## Design, statistics and controls

The canonical run has 30 independent seeds with world/action streams spawned from `SeedSequence(10000+seed)`, and 200 trials per seed. The trial count is half the original experiment's configured test count, with a minimum of two. World initial states, transitions and observations are sampled directly from the imported D, B and A tensors; shared categorical inverse-CDF uniforms retain the potential outcomes for both actions. Three strategies share each context and potential informative outcome: sampled EFE, always inspect and always blind. This gives 6,000 generated world trials and 18,000 scored strategy rows. Labels are used for scoring only; no fitting occurs. Known reliability and dynamics are privileged assumptions.

Each strategy produces one categorical observation per trial. `mean_inspections` counts informative observations, not all observations, time or energy. Seven outcomes are retained: accuracy, Brier loss, context log loss, inspection count, realized preference logit, selected normalized EFE and context posterior entropy. Bootstrap seed 314159 and 5,000 resamples provide marginal 95% intervals over seed means; two paired strategy contrasts across seven metrics give 14 exploratory estimates. No new p-values or significance family are introduced. Exact expectations are retained for all 21 strategy/metric combinations.

The exact grid contains 11 reliability values from 0.50 to 1.00 and 17 null-outcome logits from 0 to 0.80, totaling 187 models. Every point retains both EFE scores, policy probability, information gain and risk-plus-ambiguity identity residual. These deterministic grid points are not empirical replicates. GNN specifications are content-addressed in `results/active_sensing_gnn/`; `summary.json` identifies the selected models and simulation model digest.

Real-computation tests check context-preserving transitions, analytical posterior probabilities, the EFE crossover, actual softmax probabilities, a preference intervention reversing the chosen action, uninformative/perfect sensor limits, malformed design/model rejection, deterministic reproduction and agreement with known expectations. Such agreement checks computation within the declared model, not real-world validity.

## Retained files and figures

| File in `results/` | Meaning |
|---|---|
| `active_sensing_trials.csv` | Matched contexts, actions, outcomes, posteriors and seven scores |
| `active_sensing_seed_metrics.csv` | 90 seed-by-strategy rows |
| `active_sensing_estimates.csv` | 21 marginal estimates and exact reference expectations |
| `active_sensing_comparisons.csv` | 14 paired estimates with seed bootstrap intervals |
| `active_sensing_landscape.csv` | 187 exact GNN policy evaluations |
| `active_sensing_gnn/` | Materialized model specifications selected in summary metadata |

Two numbered figures distinguish exact policy surfaces from sampled outcomes. The graphical abstract combines the specification/execution/evaluation workflow, original sensor accuracy intervals, and the exact action-selection surface. All have PNG, SVG and PDF editions. Numerical panels are generated from actual evidence; no AI image-generation output is used in the selected cover.

```bash
uv run python scripts/07_analysis_pipeline.py --update-cover
uv run python scripts/08_render_with_template.py --template-root "$TEMPLATE_ROOT"
uv run python scripts/09_validate_documentation.py
```

`--update-cover` explicitly copies the generated abstract into `manuscript/assets/` and writes `graphical-abstract-provenance.json`; ordinary pipeline runs and tests write figures only into their requested output directory. The flag requires data export stage 4 or later. The selected cover follows `paper.cover.image` and `paper.cover.alt`; missing/out-of-tree assets or missing descriptions fail.

Publication links use `#cc0000`. The manuscript preamble configures PDF link/citation/URL color, while `assets/publication.css` is included in the recorded HTML source projection; the actual pinned template source is unmodified. The offline preview uses the same red.

## Materialization contract

Model materialization changes numerical assignments only within named GNN sections and preserves ontology annotations. Each realization is parsed, validated and executed; generated specification hashes bind the selected model bytes to the summary. Tests exercise assignment boundaries and reject malformed models. See [GNN models](gnn_models.md) and [outputs](output_conventions.md).
