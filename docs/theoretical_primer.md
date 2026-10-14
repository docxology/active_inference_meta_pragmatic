# Theory and interpretation

A categorical generative model maps hidden states to observations (A), propagates states under actions (B), expresses preferred outcomes as logits (C), and initializes beliefs (D). Each probability column of A/B sums to one. C becomes a preference distribution through softmax; it is not itself a probability vector.

State inference conditions on observed evidence. Exact variational free energy additionally evaluates a candidate distribution against an explicit joint model, and equals negative log evidence plus KL divergence to the exact posterior. Without a joint model, an arbitrary energy-minus-entropy score is not automatically a variational bound.

The implementation's normalized EFE is negative information gain minus expected log outcome preference. For its known categorical likelihood, this equals outcome risk plus expected observation ambiguity. The legacy raw-logit return omits the additive preference normalizer. Mean and sum aggregation are explicit because a finite-horizon objective and an average per-step score are different conventions.

The quadrant framework distinguishes task evidence from information about its reliability, and direct inference from monitoring/revision. These are analytical distinctions. Metadata-aware inference can be ordinary Bayesian inference under an appropriate likelihood. Adaptive acquisition can improve accuracy by spending more observations. Reliability learning requires data and an evaluation split. None of those mechanisms guarantees benefit when metadata is false, observations are correlated, or costs dominate.

The retained experiment measures these concrete mechanisms in a binary sensor setting. It is not a full EFE planning benchmark: EFE identities and reliability sensitivity are checked separately. Narrative examples, composite confidence scores, FEP boundary illustrations, attack-surface weights and parameter-drift thresholds remain educational heuristics. See the manuscript for the generative assumptions, statistical units, costs and adverse control.
