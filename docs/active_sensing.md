# Executed GNN active sensing and graphical abstract

This revision adds an actual action-selection task alongside the original confidence-threshold sensor study. It also restores red hyperlinks in the PDF, template HTML and offline HTML, and replaces the selected cover with a data-generated scientific graphical abstract. The previous [GNN](revision_2026-10-14.md) and [diagnostic expansion](expansion_2026-10-14.md) records describe earlier artifact states.

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

Two new numbered figures distinguish exact policy surfaces from sampled outcomes. The graphical abstract combines the specification/execution/evaluation workflow, original sensor accuracy intervals, and the exact action-selection surface. All have PNG, SVG and PDF editions. Numerical panels are generated from actual evidence; no AI image-generation output is used in the selected cover.

```bash
uv run python scripts/07_analysis_pipeline.py --update-cover
uv run python scripts/08_render_with_template.py --template-root "$TEMPLATE_ROOT"
uv run python scripts/09_validate_documentation.py
```

`--update-cover` explicitly copies the generated abstract into `manuscript/assets/` and writes `graphical-abstract-provenance.json`; ordinary pipeline runs and tests write figures only into their requested output directory. The flag requires data export stage 4 or later. The selected cover follows `paper.cover.image` and `paper.cover.alt`; missing/out-of-tree assets or missing descriptions fail. The original conceptual cover remains preserved as historical source.

Publication links use `#cc0000`. The manuscript preamble configures PDF link/citation/URL color, while `assets/publication.css` is included in the recorded HTML source projection; the actual pinned template source is unmodified. The offline preview uses the same red.

## Corrections retained during validation

The source-level model materializer previously replaced every line beginning with A/B/C/D assignments, including their ontology labels. A real failing regression reproduced this defect. Replacement is now limited to the first numerical assignment in the ordered canonical template, preserving the ontology block. The active-sensing base specification also retains the proper labels. Model tensors and numerical estimates are unchanged. Earlier materialized bytes are preserved under ignored `output/active-sensing-evidence/pre-ontology-models/`, and the newly generated selected models replace them in the current results.

The first extended PDF exposed an overfull float with a clipped model-work diagram. The source now gives that figure explicit placement and a bounded aspect-preserving height. Failed/earlier receipts and rasterized pages are preserved; the final renderer is rerun and checked after the correction. No upstream GNN or template tracked source is modified.

## Historical action-study validation

The following receipts describe the preceding 604-test, 24-page build. See the [current revision](meta_pragmatic_revision.md) for the subsequent title, scholarship and exact world–agent robustness expansion. The current materializer scopes replacement to named sections, extending the first-assignment correction recorded above.

All 604 tests pass on actual Python 3.11.15, 3.12.13 and 3.13.14 environments, with environment and base-interpreter paths on GitVault. Unit/integration branch coverage is 94.00%; including actual pipeline and template CLI/worker execution yields 95.64%. The gate remains 90%, with the 95% target unchanged. The focused rules and Ruff error checks pass. The full pipeline and installed-wheel GNN/EFE study run successfully; the source distribution retains the new model and publication assets. Generated graphical-abstract SVG output is normalized for trailing whitespace before it is copied into manuscript assets.

The upstream GNN validator accepts all 247 selected/authored specifications: three packaged models, 57 sensor realizations and 187 action models. A deliberately malformed specification is rejected. The ontology regression fails before the correction and passes afterward. Its receipts and the original failed fixture/render outputs remain under ignored `output/active-sensing-evidence/`.

The actual unmodified template produces a 24-page PDF with eight numbered figures, a scientific graphical abstract, 35 references and 74 corresponding typeset expressions in HTML. Every PDF page is rasterized for inspection. The final compiler log has no overfull boxes or undefined references; remaining warnings concern ordinary float placement and unused table caption setup. The PDF is not tagged. HTML inspection observes nine loaded, described images, zero broken internal anchors and MathJax errors, and red computed color for all links. PDF linked-content text is red; black citation punctuation is distinguished from link content in text extraction. Wide and narrow viewport checks show no horizontal document overflow.

The retained run reports sampled-EFE accuracy 71.23% (marginal 95% interval 70.23–72.28%) and 0.617 informative observations per trial (0.607–0.626), against exact expectations 71.64% and 0.6182. Always inspect gives 84.90% accuracy and always blind gives 49.97%. These are exploratory, model-conditional results. They do not change the original H1–H3 family or establish biological validation.

The final manifest records 136 source-file and 345 output digests; the renderer receipt identifies 56 output digests. Source/output bytes and the corresponding 481 staged Git blobs are verified, together with all selected specification hashes and the renderer's authored/hydrated inputs. A deliberately corrupted output digest is rejected. All work remains local on `codex/gnn-manuscript-revision`; no commit or push is claimed.
