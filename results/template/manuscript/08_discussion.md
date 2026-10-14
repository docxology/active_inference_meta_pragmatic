# Discussion {#sec:discussion}

## Interpretation of the numerical results

The experiment supports a narrow conclusion: using accurate source reliability can improve a misspecified inference baseline, and additional evidence can improve accuracy at additional cost. Estimating reliability from labeled training approximates the oracle condition in this task. These findings are compatible with standard Bayesian model specification and sequential evidence acquisition. They do not require that the four quadrants correspond to distinct computational or biological faculties.

Q2 and Q4 produce identical held-out classification accuracy in the retained run, while their Brier and log losses differ. In this parameter regime, fitted likelihood weights preserve the ordering of classification decisions across seeds. Equal accuracy therefore does not imply identical beliefs or perfect parameter recovery. Conversely, a sizable standardized seed-level effect largely reflects small variation in replicate means, so absolute percentage-point differences and sensing costs deserve priority.

## Contribution of the taxonomy

The taxonomy makes three questions explicit: what evidence is modeled, what information is available about its reliability, and which part of processing can be monitored or revised. It connects model specification to testable interventions and makes assumptions inspectable. It does not supersede established work on learning, monitoring/control, active learning, or hierarchical inference.

Changing $A$, $B$, $C$, or $D$ has different meanings: observation model revision, dynamics revision, preference revision, and prior revision. These should not all be treated as the same form of optimization. Empirical fit can assess some epistemic revisions, whereas preference revision additionally needs a justified normative reference.

## Limitations {#sec:limitations}

The task has two states, conditionally independent sensors, fixed reliabilities, and no changing state within a trial. Labels are available for training Q4, and true reliability is supplied to Q2/Q3. Q3 receives a larger sensing budget. Those assumptions favor the tested mechanisms; correlated observations, incorrect metadata, changing reliability, and costly acquisition can alter the result.

The experiment evaluates state estimation and sensing, not a full partially observable control task or long-horizon planning. EFE is checked separately through exact mathematical identities and a reliability sweep. No claim is made that the synthetic accuracy gains were caused by EFE policy selection. The package's narrative framework/modeler classes and schematic FEP visualizations remain educational demonstrations.

Confidence intervals concern this simulation design. Bootstrap seed resampling approximates variability over independent generated datasets, not uncertainty about all possible environments. Sign-flip tests require a symmetric/exchangeable null; they are supplementary to retained estimates and model assumptions. The three primary tests use Holm correction, while the displayed 95% intervals are marginal. No retrospective power calculation or fabricated regression fit is reported.

The manuscript is a working research document, without claimed peer review or independent replication. Bibliographic corrections are documented separately; bibliography links establish source identity, not independent confirmation of every interpretation. Synthetic failures do not support clinical or deployment guidance.

## Next empirical tests

Useful next tests would compare equal sensing budgets, include model-free and model-based decision baselines, introduce correlated and shifting sensor noise, vary training-label availability, and evaluate metadata provenance or corruption detectors on held-out attacks. Representation-changing Q4 mechanisms require complexity penalties and external evaluation. A biological study would need measured behavior, confidence reports, a fitted model, and appropriate metacognitive measures [@fleming2014measure], rather than mapping the quadrant labels directly onto neural structures.
