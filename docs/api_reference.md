# API reference

Installed imports use the top-level packages below. Public errors use `utils.exceptions.ValidationError`.

## Categorical models

`core.generative_models.GenerativeModel(A, B, C, D)` copies and validates all inputs. A is `(observations, states)`, B is `(next_states, current_states, actions)`, C is finite `(observations,)`, and D is normalized `(states,)`. A two-dimensional B becomes a singleton action axis.

- `predict_observations(state)`: state index or normalized belief vector → observation probabilities.
- `predict_state_transition(current_state, action)`: state index or normalized beliefs → next-state probabilities.
- `perform_inference(observation, prior_beliefs=None)`: category or normalized virtual evidence → posterior. Impossible evidence raises; exact zeros are preserved.
- `preference_distribution()`: stable normalized softmax(C).
- `calculate_preference_likelihood(observation, normalized=False)`: legacy exp(C) strength, or normalized probability; overflow is rejected.

## Active inference

`core.active_inference.ActiveInferenceFramework(generative_model, precision=1.0)` accepts a model or A/B/C/D dictionary. Precision must be positive and finite.

`calculate_expected_free_energy(posterior_beliefs, policy, observations=None, aggregation="mean")` returns `(score, components)`. The compatibility `observations` argument does not update beliefs. Update beliefs before evaluating the policy. Policies are nonempty, one-dimensional integer action sequences.

Components include `epistemic` (negative information gain), `pragmatic` (negative expected C), `total`, `information_gain`, `ambiguity`, `outcome_entropy`, `preference_normalizer`, `normalized_total`, and `risk`. `normalized_total = risk + ambiguity`. `aggregation="sum"` sums across future steps; the default averages. Planning propagates predicted beliefs open-loop without observation-contingent updates.

`select_optimal_policy(candidate_policies, posterior_beliefs=None, aggregation="mean")` returns the argmin policy and scores, with normalized `policy_probabilities`. Omitted beliefs use D. Precision controls the reported policy distribution.

## Variational free energy

`core.free_energy_principle.calculate_variational_free_energy(model, observation, beliefs, prior=None)` returns F and its energy, entropy, surprise and posterior-divergence decomposition. Infinite F is retained for posterior-support violations. Impossible evidence raises an error.

`FreeEnergyPrinciple(system_states, precision=1.0, generative_model=None)` retains schematic state-boundary and homeostatic demonstrations. With a model, `calculate_free_energy` delegates to the exact calculation. Without a model it declares `evaluation_kind="legacy_illustrative_score"`; its score and trajectories are not a validated physical FEP simulation.

## Statistics

`analysis.statistical_analysis.StatisticalAnalyzer(alpha=0.05)` requires one-dimensional finite samples. Confidence intervals require at least two observations and a level in (0,1).

- `calculate_descriptive_stats(data)`, `calculate_correlation(x, y, method="pearson")`, `calculate_confidence_interval(data, confidence_level=None, confidence=None)`.
- `perform_t_test(group1, group2, test_type="independent")`: Welch or paired test. Returns pooled-SD absolute and signed Cohen d, approximate Hedges g, and paired d_z separately. Undefined tests/effects are declared, not reported as a zero effect.
- `holm_adjust(p_values)`: family-wise correction.
- `bootstrap_mean_interval(data, confidence=0.95, n_resamples=5000, seed=42)`: percentile interval across the supplied independent units.
- `analyze_algorithm_performance(results, paired=False, higher_is_better=True)`: descriptive ranking, pairwise tests and Holm correction. Independent one-way ANOVA is omitted for paired data. Paired samples must refer to matched units in the same order.

## Research workflow

`analysis.experiments.ExperimentConfig` records seed/trial/training counts, sensor probabilities, confidence threshold and bootstrap count. `run_quadrant_experiment(config)` retains test trials, seed-level metrics, fitted training reliabilities, intervals and primary comparisons. `mathematical_checks()` evaluates exact identities; `reliability_sensitivity()` produces exact curves.

`analysis.research_pipeline.run_pipeline(project_root, output_dir, config=..., stages=None)` executes earlier dependencies for requested stages. Stage 5 validates and renders numbered manuscript sources; stage 6 hashes source and outputs. The CLI is `scripts/07_analysis_pipeline.py`.

## World and agent evaluation

`core.simulation.sample_potential_outcomes(world, n_trials, rng)` returns paired one-step world draws; see [sampling contracts](world_simulation.md). `analysis.model_robustness.exact_context_scores(world, agent, actions)` returns exact predictive scores and conditional calibration cells for the four-state context task; see [supported semantics and singularities](model_robustness.md). `reliability_robustness()` produces the retained fixed-agent sensitivity grid. These interfaces keep world sampling, agent inference and evaluation separate.

## Framework and utilities

`MetaCognitiveSystem` implements a heuristic confidence score, capacity-aware attention allocation, bounded strategy-effectiveness moving averages and illustrative control rules. These are not fitted psychological measures.

`CognitiveSecurityAnalyzer.detect_anomaly` validates input distributions and reports the epsilon used for smoothed KL. `validate_framework_integrity` verifies numerical structure and reports `tamper_absence_verified=False`. Its attack-surface weights are heuristic.

`utils.manuscript.validate_manuscript` rejects missing/duplicate labels, citations and missing figures. `render_manuscript` produces standalone MathML HTML from numbered sections; it excludes AGENTS/README/preamble files. `utils.provenance.write_manifest` records source and output digests and environment versions. `FigureManager` atomically persists a figure registry and preserves corrupted registry bytes before replacement.

## Documentation and publication integration

`utils.documentation.validate_documentation(project_root)` validates the docs hub and local Markdown targets. `utils.template_rendering.check_template_checkout(project_root, template_root)` checks the pinned upstream Git identity and tracked cleanliness. `render_with_template(project_root, template_root, template_python=None, output_dir=None)` validates the manuscript, invokes the separate template environment, and requires a renderer receipt. See [rendering setup](rendering_pipeline.md).
