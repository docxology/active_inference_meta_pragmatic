# Evidence Integrity, Source Trust, and Model Vulnerability {#sec:security}

## A scoped threat model for evidence and model commitments

We consider an attacker able to change observations, reported reliability, monitoring rules, or selected model parameters in a categorical artificial agent. The assets are the fidelity of state estimates, the integrity of preferences, and the validity of model revisions. We assume the evaluation state and held-out scoring code remain trusted. This is a conceptual and synthetic threat model; it does not establish attack prevalence, impact in deployed systems, or human cognitive vulnerability.

| Intervention | Example | Evidence or limitation |
|---|---|---|
| Observations (Q1) | Alter a sensor outcome | Can be studied as a controlled observation perturbation |
| Metadata (Q2) | Overstate reliability of a weak sensor | Measured adverse control in the binary task |
| Monitoring (Q3) | Alter a confidence threshold or sensing budget | Requires a separate monitoring-rule intervention |
| Model revision (Q4) | Poison training labels or permit preference drift | Requires a trusted update reference and held-out evaluation |

These locations need not be exclusive. Altering a likelihood matrix may affect both direct inference and metadata-conditioned inference. There is no measured monotonic ranking of danger or detectability across Q1--Q4.

## Misleading metadata as a measured synthetic failure case

The misleading-metadata condition claims high reliability for the weakest sensor and low reliability for the strongest. Held-out accuracy falls to 54.12%, compared with 84.68% under truthful reliability metadata. Log loss also increases. This demonstrates a specific misspecification failure under known ground truth. It does not establish the effectiveness of a detector, defense, or real-world influence operation.

## Trust, calibration, and the limits of diagnosis

An anomaly score can reveal a discrepancy without identifying its cause. A change may be benign, and a harmful intervention may remain close to the baseline. Likewise, a well-formed probability model can encode false information. The technical diagnostic contracts are retained in Supplement \ref{sec:revision_mechanics}; neither their thresholds nor the taxonomy establish calibrated security performance.

## Bounded integrity safeguards and unresolved assurance questions

A practical system can record trusted parameter versions, verify input provenance, constrain allowed revisions, retain rollback points, and test candidate changes on held-out data. These are design proposals requiring separate evaluation. Model hashes establish byte identity against a trusted reference; they do not establish the truth or appropriateness of that reference.

Preference specification remains a normative choice. An inspectable $C$ vector can help make that choice discussable, but its mathematical representation does not ensure alignment with human values \cite{gabriel2020artificial,amodei2016concrete}. Future security experiments should state attacker capabilities, clean and attacked distributions, detector calibration data, resource budgets, and false-positive/false-negative tradeoffs. No security efficacy claim is made here.

## The separate claims an assurance argument must establish

Specification provenance addresses **which model was executed**. Mathematical checks address **whether the declared calculation obeys its contracts**. Held-out controls address **how that mechanism behaves in a specified environment**. None answers the normative question **whether the objective should be adopted**. A defensible assurance argument states the trusted reference, permitted interventions, evaluation distribution, adoption criterion, and known failures separately. The misleading-metadata condition illustrates why a well-formed specification can still encode bad information.
