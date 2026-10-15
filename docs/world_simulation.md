# Categorical world sampling

`core.simulation.sample_potential_outcomes(world, n_trials, rng)` samples initial states from `D`, next states from each action slice of `B`, and observations from `A`. It accepts an explicitly constructed or [GNN-imported model](gnn_models.md). A separate agent may use different tensors.

The returned frozen `PotentialOutcomes` container has `initial_states` with shape `(n_trials,)`, and `next_states` / `observations` with shape `(n_trials,n_actions)`. Frozen fields do not make NumPy buffers immutable; consumers must not mutate shared results. Trial counts must be positive integers; booleans are rejected.

The sampler draws one transition uniform and one observation uniform per trial and reuses each across alternate actions. This is common-random-number coupling for paired comparisons. Action columns are alternate potential outcomes of the same trial, not independent world replications. The final CDF entry is set to one to prevent validated floating-point normalization tolerance from producing an out-of-range index.

Random draw order is initial-state draws, transition uniforms, then observation uniforms. The extracted sampler preserves the active-sensing study's original seeded results. World randomness and action-selection randomness remain distinct streams in that driver. The simulator accepts no agent posterior or score, preventing action RNG consumption from changing the world draws.

Tests execute asymmetric stochastic transitions and likelihoods on 20,000 fixed-seed trials, check expected frequencies, reproduce draws exactly, and check the deterministic random-stream sequence. Deterministic and zero-support models are covered by the existing [GNN tests](testing_philosophy.md). Sampling is one step; no long-horizon simulator, counterfactual-identification theorem or biological mechanism is implied.
