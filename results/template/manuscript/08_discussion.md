# Interpreting Experimental Evidence and Justifying Model Revision {#sec:discussion}

## What the controlled experiments establish about these mechanisms

The experiment supports a narrow conclusion: using accurate source reliability can improve a misspecified inference baseline, and additional evidence can improve accuracy at additional cost. Estimating reliability from labeled training approximates the oracle condition in this task. These findings are compatible with standard Bayesian model specification and sequential evidence acquisition. They do not require that the four quadrants correspond to distinct computational or biological faculties.

Q2 and Q4 produce identical held-out classification accuracy in the retained run, while their Brier and log losses differ. In this parameter regime, fitted likelihood weights preserve the ordering of classification decisions across seeds. Equal accuracy therefore does not imply identical beliefs or perfect parameter recovery. Conversely, a sizable standardized seed-level effect largely reflects small variation in replicate means, so absolute percentage-point differences and sensing costs deserve priority.

## What the four-role taxonomy contributes to model criticism

The taxonomy makes three questions explicit: what evidence is modeled, what information is available about its reliability, and which part of processing can be monitored or revised. It connects model specification to testable interventions and makes assumptions inspectable. It does not supersede established work on learning, monitoring/control, active learning, or hierarchical inference.

Changing $A$, $B$, $C$, or $D$ has different meanings: observation model revision, dynamics revision, preference revision, and prior revision. These should not all be treated as the same form of optimization. Empirical fit can assess some epistemic revisions, whereas preference revision additionally needs a justified normative reference.

## Meta-epistemic practice as fallible inquiry

The philosophical proposal is methodological: model specification should be open to criticism through its consequences. Inference is conditional on a representation; inquiry includes asking whether that representation excludes a relevant possibility. Gelman and Shalizi's account of model checking and revision supplies a useful precedent for this distinction [@gelman2013philosophy]. Our taxonomy does not resolve the disagreement between confirmation-based and criticism-based philosophies of Bayesian practice. It makes the distinction visible in an executable case.

Metadata has no intrinsic privilege. Reliability information becomes evidence only through a model of its source, relevance, and trustworthiness. A posterior can be exact conditional on false metadata. GNN makes that conditioning inspectable; it does not eliminate the need for independent evidence about the source. Fallibility therefore applies to the likelihood, its reliability estimate, the monitoring rule, and the evaluator's own reference.

## Meta-pragmatic practice and the authority to revise

Preference logits specify a ranking of outcomes, not a complete ethics. An informational objective, a sensing budget, and an adoption threshold embody different judgments. Our interpretation connects the evaluation of those judgments to James's emphasis on practical consequences [@james1907pragmatism], without equating usefulness with unconstrained truth or morality. Better prediction under one scoring rule cannot authorize a change in whose interests the system serves.

The modeler and the modeled agent must also be distinguished. Here the researcher declares the task, external labels supervise learning, and a fixed rule triggers sensing. The experiment does not show an agent independently inventing a representation or legitimating its own ends. An autonomous revision mechanism would additionally need an admissible change space, an independent evaluation reference, and a rule for accepting or rejecting the change. Those requirements are design proposals.

## Comparing prediction quality, sensing resources, and calibration

![Prediction, sensing resources and descriptive calibration answer distinct questions. (a,b) Aligned strategy rows show percentage accuracy and observations per trial, with numeric means, distinct symbols and marginal 95 percent intervals over 30 paired seeds. Shading marks the fitted model's separate labeled training, excluded from the observation count. (c,d) Two views separate the pooled calibration comparisons across 12,000 held-out trials per strategy. Line style supplements color; point area scales with occupied-bin population. Points use mean forecasts and observed state frequencies in ten fixed bins, with empty bins omitted. The dashed diagonal denotes agreement. These curves have no calibration uncertainty bands.](../figures/resource_calibration.png){#fig:resource_calibration width=95%}

The fixed-budget comparators make the resource tradeoff explicit. Their results should be read together with Q3's stopping rule and average cost; a single accuracy ranking does not identify an optimal procedure. A decision about whether extra observations are worthwhile needs a stated cost function. No wall-clock, energy, or monetary performance is inferred from observation counts. This connects the computational comparison to bounded rationality while leaving application-specific valuations open [@simon1955behavioral].

In the retained run, fixed four-observation inference achieves 86.75% accuracy and fixed five-observation inference achieves 90.74%. Q3 achieves 90.34% at a mean 3.892 observations. The stopping rule allocates observations to less confident trials; it can therefore outperform a fixed four-observation schedule while using fewer observations on average. These are descriptive results in one design, not a claim of universal dominance or a new multiplicity-adjusted comparison. Fixed five-observation inference has lower retained Brier and logarithmic losses than Q3, so similar classification accuracy does not mean that early stopping preserves all probabilistic information.

Probabilistic quality is likewise multidimensional. Accuracy discards the strength of a belief, proper losses penalize probability errors, and the reliability diagram displays empirical agreement with predicted probabilities [@gneiting2007scoring; @dawid1982calibrated]. The diagram is descriptive for this task and binning scheme; it is not a guarantee under distribution shift.

Bröcker and Smith show why bin populations, forecast distributions and sampling variation complicate the visual reading of reliability diagrams [@brocker2007reliability]. Figure [4](#fig:resource_calibration) therefore separates comparisons and exposes bin occupancy through point area. Its pooled lines remain descriptive. We do not implement their consistency-resampling procedure, and a visually smooth curve or a small distance from the diagonal is not a statistical calibration test.

## Stopping inquiry requires an explicit resource-sensitive judgment

The stopping rule expresses a procedural commitment about when present confidence warrants ending observation. Extra evidence may improve prediction while demanding resources; a resource saving does not by itself establish an acceptable error cost. Simon's bounded rationality and resource-rational analysis motivate evaluating this tradeoff rather than hiding it in a single performance score [@simon1955behavioral; @lieder2020resource].

The detailed paired contrasts and threshold sweep remain in Supplement [11.4](#sec:sensitivity_supplement), Figures [9](#fig:paired_diagnostics) and [10](#fig:stopping_sensitivity). They expose analytical choices without selecting and validating a new policy on the same trials.

## Action selection reveals the preferences and assumptions of a model

Figure [5](#fig:active_sensing_outcomes) compares EFE policy sampling with fixed observation strategies. The sampled agent sometimes accepts a blind observation because its objective combines preferred outcomes with information. Always inspecting obtains more informative evidence, while always remaining blind supplies an explicit limiting case. These comparisons explain what the selected mechanism does under its stated commitments; they do not establish that accuracy alone is the appropriate end.

![Sampled action policies compared with exact expectations under the declared world. Small strategy-specific symbols show the 30 paired seed means, larger symbols show their averages, and capped dark bars give marginal 95 percent seed-bootstrap intervals. Open diamonds are exact expectations displaced slightly to the right for visibility. (a) Context accuracy favors larger values; (b,c) proper losses favor smaller values; (d) inspection counts expose informative-observation use. All three strategies share 6,000 generated world trials, yielding 18,000 scored rows rather than independent replications. EFE means expected free energy; its preference-sensitive action objective is distinct from maximizing accuracy.](../figures/active_sensing_outcomes.png){#fig:active_sensing_outcomes width=95%}

The exact policy surface in Supplement [11.4](#sec:sensitivity_supplement), Figure [11](#fig:active_sensing_landscape), shows how changing information quality or the preference for the blind outcome changes action probabilities. This is a designed consequence of the model, not the discovery of an independently justified preference. The distinction links an executable policy to the philosophical question of who may authorize its commitments.

## Exact inference and confident error in a misspecified world

Figure [6](#fig:model_robustness) separates the agent's model from the world's likelihood. At actual reliability 0.50, inspection is uninformative. The agent nevertheless reports inspection posteriors of 0.15 or 0.85 because it retains its assumed reliability of 0.85. Its EFE action probabilities also remain fixed. Always inspecting then has exact Brier loss 0.3725, worse than the blind baseline's 0.25, although both classify at chance. This is a proper-score failure hidden by equal accuracy. The case establishes a consequence of the specified mismatch, not a universal argument against information-seeking action.

![Correct computation can produce inaccurate predictions under an incorrect world model. (a--c) The agent holds its assumed reliability at 0.85, with preferences and policy precision fixed, while actual reliability varies. Line styles identify the sampled EFE policy and fixed-action baselines; arrows indicate favorable score directions. The vertical reference marks the matched likelihood. (d) Distinct symbols and line styles compare inspection forecasts with exact world conditional frequencies at three actual reliabilities; the diagonal denotes calibration. Every curve is an exact world expectation, not an empirical estimate or uncertainty interval. No automatic model repair is implemented.](../figures/model_robustness.png){#fig:model_robustness width=95%}

The practical response requires evidence about reliability, a permitted update, and fresh evaluation of its consequences. Recomputing an exact posterior under the same incorrect likelihood does not provide that evidence. This is the meta-pragmatic distinction in executable form: action selection follows declared commitments, while criticism asks what would warrant retaining or changing them. The analysis holds the agent fixed to reveal the failure; it does not implement autonomous detection or repair of misspecification.

## Limitations of the synthetic design and philosophical interpretation {#sec:limitations}

The task has two states, conditionally independent sensors, fixed reliabilities, and no changing state within a trial. Labels are available for training Q4, and true reliability is supplied to Q2/Q3. Q3 receives a larger sensing budget. Those assumptions favor the tested mechanisms; correlated observations, incorrect metadata, changing reliability, and costly acquisition can alter the result.

The original sensor experiment evaluates state estimation and confidence-triggered sensing; its gains are not attributed to EFE. The separate action task does execute EFE-based policy sampling and Bayesian context inference, but it is a one-step categorical control example with known dynamics and likelihood. Neither task establishes long-horizon, continuous, hierarchical or representation-learning performance. The package's narrative framework/modeler classes and schematic FEP visualizations remain educational demonstrations.

Confidence intervals concern this simulation design. Bootstrap seed resampling approximates variability over independent generated datasets, not uncertainty about all possible environments. Sign-flip tests require a symmetric/exchangeable null; they are supplementary to retained estimates and model assumptions. The three primary tests use Holm correction, while the displayed 95% intervals are marginal. No retrospective power calculation or fabricated regression fit is reported.

The manuscript is a working research document, without claimed peer review or independent replication. Bibliographic corrections are documented separately; bibliography links establish source identity, not independent confirmation of every interpretation. Synthetic failures do not support clinical or deployment guidance.

## From controlled synthetic examples to independent empirical tests

Useful next tests would compare equal sensing budgets, include model-free and model-based decision baselines, introduce correlated and shifting sensor noise, vary training-label availability, and evaluate metadata provenance or corruption detectors on held-out attacks. Representation-changing Q4 mechanisms require complexity penalties and external evaluation. A biological study would need measured behavior, confidence reports, a fitted model, and appropriate metacognitive measures [@fleming2014measure], rather than mapping the quadrant labels directly onto neural structures.
