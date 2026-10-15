# Four Complementary Roles in Meta-Pragmatic Inquiry {#sec:quadrant_model}

## The two conceptual axes and four operational responsibilities

The horizontal axis distinguishes observations from information about their production, reliability, or provenance. The vertical axis distinguishes performing inference from monitoring, evaluating, or revising inference. A datum can be metadata relative to one task and ordinary data relative to another; classification must therefore specify the object-level task and monitored process.

| | Data | Metadata |
|---|---|---|
| Object-level cognition | Q1: infer states and evaluate actions | Q2: condition inference on source reliability or context |
| Meta-cognitive regulation | Q3: monitor uncertainty and alter processing or acquisition | Q4: evaluate or revise the reliability model, strategy, or representation |

The axes are analytically distinguishable, but we do not assert statistical independence or universal neural separability. One implementation can contain operations assigned to several quadrants. Neither a timestamp nor a confidence value alone makes a system meta-cognitive; there must be a specified monitoring/control relation. The OODA comparison in Section [3.8](#sec:ooda) makes the same distinction: these responsibilities cut across a perception--action loop rather than naming four successive stages.

The early map in Figure [1](#fig:quadrant_orientation) provides the shared orientation for these roles. A complementary revision-cycle diagram appears in Supplement [11.5](#sec:revision_mechanics), Figure [12](#fig:model_revision_map).

## Q1: infer hidden states and evaluate actions within a model

Q1 includes Equation [(1)](#eq:bayes) and policy evaluation in Equation [(3)](#eq:efe) under a fixed model. The experimental Q1 baseline uses the same inference rule as the other conditions, with a homogeneous reliability assumption. Its weakness is model misspecification, rather than the absence of any Bayesian operation. Correctly specified Q1 inference can match a metadata-aware strategy when metadata carries no additional information.

## Q2: contextualize evidence through source reliability

Q2 uses metadata $m$ by conditioning the likelihood, $p(o\mid s,m)$. In the sensor example, $m$ identifies sensor-specific reliability. This changes the evidence supplied to the same Bayesian update. The gain is conditional on the metadata being informative and trustworthy. If metadata is irrelevant, unavailable, or false, it may yield no gain or cause harm.

Alternative weighted decision objectives require their own derivation and justification; the supplementary discussion distinguishes such heuristics from normalized EFE.

## Q3: monitor uncertainty and regulate evidence acquisition

Q3 observes a property of the inference process and changes what the system does next. Here, maximum posterior probability determines whether another observation is acquired. The monitoring rule is bounded by an explicit sensing budget. The mechanism improves accuracy when new observations are sufficiently informative, but incurs cost and can fail under miscalibrated beliefs.

Posterior entropy and maximum posterior probability describe belief concentration. Calibration requires comparison with realized outcomes. The package's composite confidence and attention examples are illustrative control rules; their weights are not fitted psychological parameters or calibrated probabilities of correctness.

## Q4: evaluate model assumptions and justify their revision

Q4 evaluates the reliability model and changes its parameters. The implemented mechanism estimates likelihood reliabilities on a separate labeled training set and freezes them before test. This is model-level adaptation under external supervision. It is not unrestricted self-modification, a learned ontology, or evidence that an agent can independently choose appropriate goals.

A general framework-revision objective may combine predictive fit, resource cost, and constraints on permissible changes. The choice of those terms requires justification; lowering an in-sample objective is not enough. Held-out evaluation and bounded update rules distinguish improved fit from overfitting or drift. Revising preferences also requires an external criterion for whether the revision is desirable.

## Overlapping roles, comparative predictions, and falsifiability

The framework suggests testable contrasts: informative versus uninformative metadata, matched versus mismatched models, fixed versus adaptive sensing under comparable cost, and training-based revision versus held-out controls. A useful taxonomy should help define these contrasts without predetermining their outcomes. Evidence against a particular mechanism should remain possible. The current study gives one tractable example; broader tasks, correlated sensors, nonstationarity, and representation learning are future tests.
