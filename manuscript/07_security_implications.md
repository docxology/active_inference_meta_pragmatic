# Security and Information Integrity {#sec:security}

## Scoped threat model

We consider an attacker able to change observations, reported reliability, monitoring rules, or selected model parameters in a categorical artificial agent. The assets are the fidelity of state estimates, the integrity of preferences, and the validity of model revisions. We assume the evaluation state and held-out scoring code remain trusted. This is a conceptual and synthetic threat model; it does not establish attack prevalence, impact in deployed systems, or human cognitive vulnerability.

| Intervention | Example | Evidence or limitation |
|---|---|---|
| Observations (Q1) | Alter a sensor outcome | Can be studied as a controlled observation perturbation |
| Metadata (Q2) | Overstate reliability of a weak sensor | Measured adverse control in the binary task |
| Monitoring (Q3) | Alter a confidence threshold or sensing budget | Requires a separate monitoring-rule intervention |
| Model revision (Q4) | Poison training labels or permit preference drift | Requires a trusted update reference and held-out evaluation |

These locations need not be exclusive. Altering a likelihood matrix may affect both direct inference and metadata-conditioned inference. There is no measured monotonic ranking of danger or detectability across Q1--Q4.

## Measured metadata failure

The misleading-metadata condition claims high reliability for the weakest sensor and low reliability for the strongest. Held-out accuracy falls to 54.12%, compared with 84.68% under truthful reliability metadata. Log loss also increases. This demonstrates a specific misspecification failure under known ground truth. It does not establish the effectiveness of a detector, defense, or real-world influence operation.

## Diagnostics and their limits

`CognitiveSecurityAnalyzer.detect_anomaly` requires valid normalized belief distributions before applying a disclosed smoothing epsilon to KL divergence. The smoothing makes the diagnostic finite when a baseline assigns zero mass, and therefore it is not the unsmoothed support-sensitive KL used in the exact inference identities. Thresholds are user-specified and are not calibrated false-positive rates. Distribution shift can be benign, and an attack can remain close to a baseline.

`validate_framework_integrity` checks shape, finiteness, compatibility, nonnegativity, and stochasticity. A malicious model can satisfy every one of these contracts. Structural validity therefore cannot establish absence of tampering. The result explicitly records that tamper absence was not verified. The attack-surface scores and Gaussian parameter-drift demonstrations are author-specified illustrations, not measured risk scores or probability-preserving attack simulations.

## Bounded safeguards and open questions

A practical system can record trusted parameter versions, verify input provenance, constrain allowed revisions, retain rollback points, and test candidate changes on held-out data. These are design proposals requiring separate evaluation. Model hashes establish byte identity against a trusted reference; they do not establish the truth or appropriateness of that reference.

Preference specification remains a normative choice. An inspectable $C$ vector can help make that choice discussable, but its mathematical representation does not ensure alignment with human values \cite{gabriel2020artificial,amodei2016concrete}. Future security experiments should state attacker capabilities, clean and attacked distributions, detector calibration data, resource budgets, and false-positive/false-negative tradeoffs. No security efficacy claim is made here.
