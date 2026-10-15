# Technical Supplement: Formal Models and Statistical Protocols {#sec:appendix}

This supplement retains the mathematical and experimental detail behind the main argument. The model atlas makes executable assumptions inspectable; the full protocol preserves parameters, inferential units, controls and qualifications. Supplement \ref{sec:symbols} consolidates notation for the main paper and this companion.

## Imported GNN tensors behind the experimental model diagrams {#sec:model_atlas}

```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=0.98\textwidth,height=0.78\textheight,keepaspectratio]{../results/figures/canonical_model_atlas.png}
\caption{Actual imported GNN tensors make the model declarations inspectable. Each group prints likelihood A and action-specific transition B probabilities, with cell boundaries and all zero entries retained. A has outcome rows and hidden-state columns; B has after-action rows and before-action columns. Actions are named stay/switch or blind/inspect; the binary sensor's single B slice is repeated for layout. White means zero support and dark blue means probability one. Signed preference logits C and normalized initial beliefs D appear below each group. The stay/switch model is an analytical software control, not an additional experimental study.}
\label{fig:canonical_model_atlas}
\end{figure}
```

## Categorical probability contracts and exact Bayesian inference {#sec:formal_contracts}

### The discrete generative model and its tensor conventions

Let $s$ index hidden states, $o$ observations, and $a$ actions. The implementation uses $A_{o,s}=p(o\mid s)$, $B_{s',s,a}=p(s'\mid s,a)$, finite outcome preference logits $C_o$, and a normalized initial prior $D_s$. Columns of $A$ and of each action slice of $B$ sum to one. A two-dimensional $B$ is promoted to a single-action tensor. Arrays with incompatible dimensions, empty axes, negative probabilities, nonfinite values, or invalid normalization are rejected.

The normalized outcome preference is $p_C(o)=\exp(C_o)/\sum_j\exp(C_j)$. Logits are not probabilities; adding a constant to all entries leaves the normalized preference unchanged. Model validation copies inputs so that later mutation of caller-owned arrays does not silently change an initialized model. Public model arrays remain inspectable and mutable; callers must validate deliberate revisions.

### The supported GNN profile and executable import boundary

Canonical GNN model files live under `src/core/gnn_models/`. The binary-sensor specification declares static identity dynamics; the stay-switch agent declares two action-conditioned transition slices. Both declare the same axis conventions used by the runtime. Each numerical intervention is materialized as GNN Markdown, parsed by the actual upstream `MarkdownGNNParser`, checked against this project's supported profile, and converted into the matrices consumed by inference.

The adapter rejects missing or duplicate sections, parser warnings, unsupported flags and model families, contradictory dimensions, malformed tensors, invalid probabilities, and unsupported dependency graphs. It verifies the upstream Git origin, pinned revision, and tracked source state before importing the parser. An absent checkout does not select a substitute parser or an undeclared model. Tensor changes are tested through changes in executed beliefs and policy choices, not merely through successful parsing.

This boundary makes the specification executable without confusing syntax validity with scientific adequacy. The experiment retains the exact materialized sensor specifications and their digests. Random-model identity checks and the reliability sweep also pass through GNN import. Direct tensor constructors remain available as a low-level numerical API and as independent test oracles.

### Bayesian state inference with hard and virtual evidence

For a categorical observation, Bayes' rule gives:

```{=latex}
\begin{equation}
q(s\mid o)=\frac{A_{o,s}D_s}{\sum_j A_{o,j}D_j}.
\label{eq:bayes}
\end{equation}
```

For a normalized nonnegative virtual-evidence vector $e(o)$, the implementation uses $L_e(s)=\sum_o e(o)A_{o,s}$ and replaces $A_{o,s}$ with $L_e(s)$ in Equation \eqref{eq:bayes}. This convention models evidence about possible outcomes. It differs from a Jeffrey update, which mixes already-conditioned posteriors. A uniform evidence vector is uninformative because each likelihood column sums to one. Zero-probability states retain zero mass; evidence impossible under the model and prior raises an error instead of being repaired by clipping.

### Exact variational free energy and the evidence bound

Given an explicit joint distribution and a normalized candidate posterior $q$, variational free energy is:

```{=latex}
\begin{equation}
F(q,o)=\sum_s q(s)\left[\log q(s)-\log p(o,s)\right]
=-\log p(o)+D_{\mathrm{KL}}\left[q(s)\Vert p(s\mid o)\right].
\label{eq:vfe}
\end{equation}
```

Equation \eqref{eq:vfe} bounds negative log evidence and reaches the bound at the exact posterior. Candidate beliefs assigning positive mass outside posterior support have infinite free energy. The exact implementation is `calculate_variational_free_energy`; the older model-free `FreeEnergyPrinciple.calculate_free_energy` path remains an explicitly labeled schematic score for compatibility. Its trajectories and state-boundary diagrams do not establish a variational bound, conditional independence, or the physical claims of the FEP. Supplying a generative model to that class selects the exact calculation.

### Normalized expected free energy and categorical policy selection

For each future policy step, propagate $q_\tau=B(a_\tau)q_{\tau-1}$ and predict $q_o=Aq_\tau$. With an exact conditional update, state information gain is $I(s;o)=H(q_o)-\sum_s q_\tau(s)H(A_{:,s})$. Our normalized planning score is:

```{=latex}
\begin{equation}
G_\tau=-I(s;o\mid\pi)-\sum_o q_o(o)\log p_C(o)
=D_{\mathrm{KL}}[q_o\Vert p_C]+\sum_s q_\tau(s)H(A_{:,s}).
\label{eq:efe}
\end{equation}
```

The equivalence in Equation \eqref{eq:efe} follows by expanding mutual information and KL divergence. It is exact for this finite, known-likelihood predictive model. It does not include uncertainty about parameters, posterior approximation error, or observation-contingent replanning.

For compatibility, the returned `total` uses the raw-logit score $-I-\mathbb{E}[C]$. `normalized_total` adds `logsumexp(C)` per step and equals risk plus ambiguity. Normalized values are evaluated directly from stable log preferences to avoid cancellation under large constant logit shifts. Policy rankings agree mathematically for a fixed model and horizon convention. Mean aggregation is the legacy default; sum aggregation implements additive finite-horizon costs. Comparing different horizons or different preference models requires specifying this convention and normalization explicitly.

Policy selection accepts current posterior beliefs, with $D$ used when beliefs are omitted. It returns an argmin and a policy distribution proportional to $\exp(-\gamma G)$, where $\gamma>0$ is precision. Increasing precision concentrates this distribution; it does not change an exact argmin. Equal scores retain a uniform distribution. All entropy and KL quantities use natural logarithms and are measured in nats.

```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{../results/figures/efe_sensitivity.png}
\caption{An exact one-step decomposition separates information, ambiguity and outcome risk. For a binary symmetric likelihood, uniform state beliefs, identity transitions and C=(1,-1), (a) information gain rises toward the binary maximum ln 2 while ambiguity falls, and their sum stays ln 2. (b) Uniform predicted outcomes keep risk constant, so normalized expected free energy equals risk plus ambiguity throughout. Axis units are nats per policy step; distinct line styles identify the terms. The figure evaluates declared mathematics without fitted effects, sampling uncertainty or evidence that an agent's assumptions fit its world.}
\label{fig:efe_sensitivity}
\end{figure}
```

## Complete synthetic experimental design and statistical protocol {#sec:protocol}

### Study type and inferential scope

This is a conceptual framework with a synthetic computational demonstration. The taxonomy was not derived from empirical clustering and is not tested as a biological partition. The experiment tests concrete mechanisms inspired by its quadrants. The mechanisms are implemented in `src/analysis/experiments.py`; the narrative quadrant class supplies definitions and examples, rather than four independently validated algorithms.

The design below is fixed in code and recorded in each output manifest. It is not a preregistered study. Historical numerical claims in earlier manuscript versions lacked a corresponding experiment and are superseded by the retained results reported here. No participant data, clinical outcomes, or deployment incidents are analyzed.

### The binary sensor task and its resource-matched controls

Each test trial independently draws a binary hidden state from a uniform prior. Five conditionally independent binary sensors agree with that state with probabilities $(0.55,0.65,0.85,0.80,0.80)$. Every strategy sees the same pre-generated test states and observations within a seed. The first three sensors are the common initial evidence. The state remains fixed within a trial and resets independently between trials.

- **Q1 fixed:** inference assumes reliability 0.80 for each of the first three sensors.
- **Q2 metadata:** inference uses the true, sensor-specific reliabilities for the same three observations. This is an oracle-metadata condition.
- **Q3 adaptive:** starts from Q2, then acquires a fourth and, if needed, fifth observation while the maximum posterior probability is below 0.90. Its cost is the actual observation count, with a maximum of five.
- **Q4 learned:** estimates the first three reliabilities from 200 separate labeled training trials per seed, using a Beta(1,1) prior. Parameters are frozen before held-out evaluation. It uses exactly three test observations.
- **Misleading metadata:** uses claimed reliabilities $(0.95,0.85,0.55)$ for the first three sensors. This prespecified adverse control reverses the ordering of sensor quality.
- **Fixed four / fixed five:** use true reliability with exactly four or five observations on every trial. These added descriptive comparators separate a fixed sensing budget from the confidence-triggered stopping rule. They are additions to this revision, not preregistered tests.

Q3 changes available evidence, whereas Q4 changes fitted likelihood parameters. They are not matched to Q1 on every resource. We report these differences rather than attributing all gains to a generic meta-level capacity. The confidence score controlling Q3 is maximum posterior probability; it is not the composite heuristic returned by `MetaCognitiveSystem`.

### An action task driven by expected free energy

A separate exploratory task directly executes active inference action selection. Four hidden states encode binary context crossed with observation mode: two blind-mode states and two informative-mode states. Two actions preserve context while setting the mode. The blind action produces a null outcome; inspection produces one of two context-indicating outcomes with reliability $r=0.85$. The declared likelihood is

```{=latex}
\begin{equation}
A=\begin{pmatrix}1&1&0&0\\0&0&r&1-r\\0&0&1-r&r\end{pmatrix},\qquad
C=(c,0,0),\quad D=(1/2,1/2,0,0),\quad c=0.15.
\label{eq:active_sensing_model}
\end{equation}
```

Each transition slice deterministically maps the current context to the action's mode. Every model is materialized as GNN and parsed through the actual upstream reference parser before the local categorical runtime consumes its tensors. The two one-step policies are scored by normalized EFE. Actions are sampled from the actual returned policy posterior at precision 4, rather than replacing it with an unrelated confidence rule.

For this uniform-context design, inspection supplies information $I=\log 2-h(r)$, where $h$ is binary entropy in nats. The normalized score difference is $G_{\mathrm{inspect}}-G_{\mathrm{blind}}=c-I$. Thus, increasing the preference for the null outcome can reverse the minimum-EFE action even when information quality is fixed. The sampled policy has inspection probability $[1+\exp(4(c-I))]^{-1}$; finite precision retains both actions. This is a designed tradeoff, not an independently learned preference or a claim that the sampled policy minimizes expected score without regularization.

Thirty independent seeds, offset by 10,000 from the first task, generate 200 context/outcome trials each. The world draws initial states from the imported $D$, next states from the imported action slice of $B$, and outcomes from the imported $A$. Separate world and action random streams prevent action sampling from altering the world draws. Sampled EFE, always inspect, and always blind share each generated context and potential informative outcome. Context labels score predictions only; no parameter is fitted. Both actions produce a categorical observation, while the inspection count records whether that observation is informative. It is not an energy or wall-clock measurement.

The study retains 18,000 strategy-trial rows, 90 seed metrics, marginal 95% seed-bootstrap intervals, paired differences against both fixed baselines, and exact expectations under the declared model. Accuracy, Brier loss, log loss, inspection count, preferred-outcome logit, selected normalized EFE and posterior entropy are reported. No new significance family is introduced. An exact 11-by-17 reliability/preference grid separately evaluates action scores and probabilities; the grid is not a set of independent empirical replicates.

### Separating the world from the agent's model

The matched action task deliberately uses the same world and agent parameters. To expose the limitation of that match, an additional exact analysis fixes the agent's assumed reliability at $\rho=0.85$, its preferences at $c=0.15$, and its policy precision at 4, while varying actual world reliability $r$ over 21 values from 0.50 to 1.00. Each world and the fixed agent are imported from their own content-addressed GNN specification. The policy remains the agent's returned EFE distribution; evaluation uses world probabilities. No parameter is fitted and no policy is selected from this grid.

Let $a$ denote an action, $s'$ the next state, and $y(s')$ its context, encoded by state-index parity. For world matrices carrying subscript $w$, the exact joint distribution is

```{=latex}
\begin{equation}
p_w(s',o\mid a)=A_w(o,s')\sum_s B_w(s',s,a)D_w(s).
\label{eq:world_joint}
\end{equation}
```

The agent independently computes $\hat p_a(o)=q_{\mathrm{agent}}(y=1\mid o,a)$. For any binary scoring loss $\ell$, its exact expected value under strategy $\pi$ is

```{=latex}
\begin{equation}
R_\ell(\pi;w,\mathrm{agent})=\sum_{a,s',o}\pi(a)p_w(s',o\mid a)\ell\!\left(\hat p_a(o),y(s')\right).
\label{eq:world_risk}
\end{equation}
```

Zero-mass events contribute nothing. Positive-probability world observations impossible under the agent fail explicitly; zero forecast probability for a possible context likewise fails rather than being clipped to an arbitrary finite logarithmic loss. The present grid avoids these singularities because $\rho$ is interior to the unit interval. Accuracy uses the same deterministic tie rule as the sampled study.

For inspection, independent closed-form checks are

```{=latex}
\begin{equation}
R_{\mathrm{Brier}}=r(1-\rho)^2+(1-r)\rho^2,\qquad
R_{\log}=-r\log\rho-(1-r)\log(1-\rho).
\label{eq:mismatch_scores}
\end{equation}
```

The blind baseline has accuracy $1/2$, Brier loss $1/4$, and log loss $\log 2$. The EFE strategy mixes its two action-specific scores using the fixed agent policy. Calibration cells retain each action, outcome, world probability mass, agent forecast and world conditional context frequency. These are exact conditional probabilities, not binned sample estimates. The 63 strategy-by-world rows are deterministic evaluations, with no bootstrap intervals, p-values or claim of 63 independent replications. Reusable world sampling and exact scoring are separate modules from the study driver.

### Independent seeds, random streams, and scored outcomes

Thirty independent seeds (0--29) generate 400 held-out trials each. A `SeedSequence` spawns distinct training and test streams. Labels from test trials are used only for scoring. The training and held-out streams are not used to tune the threshold, prior, or hypotheses. Equal posterior probabilities select state zero deterministically.

The primary outcome is held-out accuracy. Secondary descriptive outcomes are mean Brier loss, logarithmic loss in nats, and observations per test trial. Lower loss is better. Accuracy alone may conceal confidence errors, and a high posterior is not evidence of calibration under misspecification. The added reliability diagram uses ten fixed bins over the unit interval, pooling held-out trials descriptively; it supplies no trial-independent confidence intervals.

The three directional predictions concern (H1) Q2 versus Q1 accuracy, (H2) Q3 versus Q2 accuracy with additional sensing, and (H3) Q4 versus Q1 accuracy after separate training. The comparisons are operationalizations of these mechanisms, not claims that every quadrant extension improves accuracy. Two-sided tests retain the possibility of harm.

### Paired seed-level uncertainty, tests, and multiplicity control

The inferential unit is a seed-level mean, yielding 30 paired replicates per comparison; the 12,000 test trials are not treated as 12,000 independent agent replicates. The common-random-number design reduces comparison noise. We report mean paired differences with 95% percentile-bootstrap intervals from 5,000 resamples of seeds, using bootstrap seed 42 \cite{efron1993bootstrap}. Intervals are marginal, not simultaneous family-wise intervals.

Primary test evidence is a two-sided paired sign-flip test using 10,000 Monte Carlo resamples (seed 2718) with a plus-one correction. Its validity requires exchangeability of signs under the paired null; it is not an exact finite-sample test for arbitrary differences. Holm correction applies to the family of three primary comparisons \cite{holm1979sequential}. Paired t-tests and standardized within-pair differences $d_z=\overline{\Delta}/s_\Delta$ are supplementary. Effect-size conventions are explicit; large standardized differences across low-noise seed averages do not imply large population effects in human cognition. The new fixed-budget comparisons are descriptive and are not silently added to the original three-test family.

The pipeline also checks 200 two-step policy evaluations across 50 randomly generated models against the risk-plus-ambiguity identity, and checks the VFE evidence decomposition. These check the implementation under specified numerical contracts, not the truth of the FEP as a physical theory. Deterministic and impossible-evidence cases are included in regression tests.

### Retained trials, fitted specifications, and computational evidence

An exploratory extension recomputes paired seed differences for six contrasts across accuracy, Brier loss, log loss, and sensing cost. It uses 5,000 seed-bootstrap resamples with seed 314159 for marginal 95% intervals. Secondary binomial sign tests count positive and negative nonzero differences, omit ties, and return one when all differences tie. They concern sign balance, not a zero mean, and their unadjusted values are not used for new rejection claims. The original three-test family remains the primary analysis.

The extension also evaluates eleven fixed stopping thresholds from 0.50 to 1.00 in steps of 0.05 on the same five sensor outcomes per test trial. No threshold is selected. This assesses sensitivity rather than providing independent policy validation. Probability-calibration tables retain occupied-bin counts and represented seeds at 5, 10, and 20 equal-width bins, with probability one assigned to the final bin. They are descriptive pooled summaries without inferential intervals.

`results/trials.csv` retains test states, sensor outcomes, strategy probabilities, and Q3 sensing counts. `results/replicates.csv` retains all seed-level metrics. `results/summary.json` contains intervals, tests, design parameters and limitations; `results/efe_sensitivity.csv` contains the exact curves. `results/manifest.json` hashes source files, configuration, environment versions and output artifacts. The Git revision is the base revision; source digests identify the executed working-tree content.

`results/gnn/` retains the imported sensor realizations, including fitted training parameters. Their content hashes bind the reported probabilities to executable specifications. For each seed, the learned condition consumes 200 labeled training trials involving three sensors; this training resource is separate from its three held-out observations per trial. The oracle conditions receive true reliability as privileged information. The cost figure measures observations, not an unmeasured monetary or energy cost.

The retained sensor outcomes are displayed in the main paper, Figure \ref{fig:quadrant_experiment}.

## Paired contrasts, stopping rules, and policy surfaces {#sec:sensitivity_supplement}

### Paired predictive contrasts and the confidence-based stopping decision

Figure \ref{fig:paired_diagnostics} evaluates the same matched seeds across classification accuracy and proper losses. The direction of an accuracy gain and the direction of a loss improvement are opposite; presenting both makes this distinction visible. In particular, comparing learned reliability with oracle metadata exposes probabilistic differences that equal classification accuracy conceals. These secondary estimates have marginal intervals and are exploratory. Their unadjusted binomial sign tests concern the balance of positive and negative nonzero seed differences; they are not tests of the mean effect and do not join the original Holm family.

```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{../results/figures/paired_diagnostics.png}
\caption{Paired differences preserve the common experimental units. Each row is the first named strategy minus the second on the same 30 seeds; points estimate the mean paired difference and capped dark bars show marginal 95 percent percentile-bootstrap intervals. (a) Positive accuracy differences favor the first strategy; (b,c) negative Brier or logarithmic-loss differences favor it. The dashed zero reference denotes equal scores. Accuracy uses percentage points and log loss uses nats; panel scales differ. These six exploratory comparisons do not have simultaneous interval coverage and do not expand the prespecified primary Holm testing family.}
\label{fig:paired_diagnostics}
\end{figure}
```

Relative to fixed four-observation inference, the adaptive rule has a mean paired accuracy difference of 3.592 percentage points, with a marginal 95% interval of [3.117, 4.042]. Relative to fixed five-observation inference, its difference is -0.400 percentage points, with interval [-0.650, -0.158]. These estimates describe the tradeoff in this simulation. They do not establish equivalence to fixed-five inference; an equivalence claim would require a justified margin and an appropriate design.

The stopping threshold expresses a procedural commitment about when current confidence warrants ending observation. Figure \ref{fig:stopping_sensitivity} varies that commitment while holding each seed's generated states and five sensor outcomes fixed. Confidence can be useful for allocating evidence in a correctly specified task, but the misleading-metadata condition shows why confidence alone cannot justify the model that produces it. A model revision practice therefore needs checks directed at the likelihood and data source as well as checks directed at posterior uncertainty.

```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{../results/figures/stopping_sensitivity.png}
\caption{The stopping threshold jointly changes prediction and sensing resources. Eleven required posterior-confidence thresholds are evaluated using the same retained states and potential reports. (a) Accuracy and (b) observation count show seed means with capped marginal 95 percent bootstrap intervals; markers denote evaluated thresholds, and connecting lines only guide the eye. The dashed reference identifies the original 0.90 rule. Higher thresholds can acquire additional reports up to the five-observation budget. This reused-data sensitivity analysis neither independently validates a selected threshold nor assigns a price to predictive errors or observation cost.}
\label{fig:stopping_sensitivity}
\end{figure}
```

There is no application-independent exchange rate between an accurate decision and an additional observation. A deployment loss could price each observation and each decision error, but a different price could change the preferred rule. The threshold sweep deliberately reports both outcomes rather than selecting a utility function after seeing the results. Label acquisition for Q4, knowledge of reliability for oracle conditions, and computational overhead remain additional resources outside the per-trial sensing count.

The exported calibration tables repeat the descriptive binning at 5, 10, and 20 bins, preserving counts and represented seeds in every occupied bin. Empty bins are omitted rather than assigned an invented observed frequency. Greater visual agreement at one resolution would not establish calibration at all resolutions, in small subgroups, or after environmental change. These diagnostics make uncertainty inspectable without turning a particular display convention into a scientific guarantee.

### Executed EFE policy selection and its exact model expectations

The new action task distinguishes information quality from the preference for a null observation. Figure \ref{fig:active_sensing_landscape} shows the exact crossover of the two action scores and the finite-precision policy posterior. The state representation includes observation mode, so the likelihood remains fixed while actions alter the predicted state distribution through $B$. This avoids attributing action-dependent sensing to a likelihood matrix whose meaning changes outside the declared model.

```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{../results/figures/active_sensing_landscape.png}
\caption{Exact EFE policy consequences of changing information quality and outcome preference. The 187 cells represent separately materialized GNN reliability/logit combinations. (a) Inspection minus blind normalized expected free energy is in nats; negative values favor inspection. (b) The corresponding inspection probability uses policy precision 4. The outlined white contour denotes equal EFE and hence probability one half for these two policies. The cross locates the retained sampled design. Actions change observation mode while preserving context. These are model evaluations, not independent experimental replicates; they have no sampling intervals.}
\label{fig:active_sensing_landscape}
\end{figure}
```

Figure \ref{fig:active_sensing_outcomes} compares the sampled policy with its fixed baselines and analytical expectations. A policy that sometimes chooses the preferred null observation can obtain fewer informative observations and lower context accuracy than always inspecting. EFE therefore need not maximize classification accuracy alone. The preference vector and policy precision help explain that behavior; they are substantive commitments, not estimated facts about a biological agent.

The sampled action outcomes are displayed in the main paper, Figure \ref{fig:active_sensing_outcomes}.

The exact reference expectations separate Monte Carlo variability from a change in the theoretical prediction. They are conditional on the same known generative model, so agreement supports computational consistency within this task rather than model adequacy in the world. Paired estimates and all seven metrics remain in the retained evidence, including resource and preference quantities that an accuracy-only ranking would omit.

In the retained action run, sampled EFE achieves 71.23% context accuracy with a marginal 95% interval of [70.23, 72.28]%, using 0.617 informative observations per trial with interval [0.607, 0.626]. The exact model predicts 71.64% accuracy and an inspection probability of 0.6182. Always inspecting achieves 84.90% accuracy, while always taking the blind action achieves 49.97%. These values describe the declared one-step task and its chosen preferences; they do not establish superiority of one policy for every objective.

## Model revision mechanics and the limits of integrity diagnostics {#sec:revision_mechanics}

```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth,height=0.76\textheight,keepaspectratio]{../results/figures/model_revision_map.png}
\caption{Inquiry roles and research procedures provide complementary descriptions of model work. (a) Q1 infers and acts; Q2 contextualizes evidence; Q3 monitors inquiry; Q4 evaluates and revises assumptions. Their responsibilities overlap. (b) Specification, execution, held-out evaluation and justified criticism form a proposed workflow. Arrows indicate procedural relations, not measured neural or causal connections. The experiments implement a bounded computational evaluation cycle and a supervised fitted-model comparison. Public participation, the authority to alter ends and open-ended autonomous revision remain outside the implemented mechanism.}
\label{fig:model_revision_map}
\end{figure}
```

An alternative weighted score $\widetilde G=w_e(-I)+w_p(-\mathbb E[C])+w_m K(m)$ can be useful as a designed decision objective. Arbitrary weights and an added metadata cost do not automatically preserve a variational derivation. Such scores must be labeled heuristics unless a corresponding generative model and derivation are supplied.

### Diagnostics and their limits

`CognitiveSecurityAnalyzer.detect_anomaly` requires valid normalized belief distributions before applying a disclosed smoothing epsilon to KL divergence. The smoothing makes the diagnostic finite when a baseline assigns zero mass, and therefore it is not the unsmoothed support-sensitive KL used in the exact inference identities. Thresholds are user-specified and are not calibrated false-positive rates. Distribution shift can be benign, and an attack can remain close to a baseline.

`validate_framework_integrity` checks shape, finiteness, compatibility, nonnegativity, and stochasticity. A malicious model can satisfy every one of these contracts. Structural validity therefore cannot establish absence of tampering. The result explicitly records that tamper absence was not verified. The attack-surface scores and Gaussian parameter-drift demonstrations are author-specified illustrations, not measured risk scores or probability-preserving attack simulations.

## Derivations, retained results, and reproduction

### Algebraic derivation checks and analytical reference cases {#sec:mathematical_foundations}

Expanding $D_{\mathrm{KL}}(q_o\Vert p_C)$ gives $-H(q_o)-\mathbb E[\log p_C]$. Adding ambiguity $\mathbb E_{q_s}H(A_{:,s})$ gives $-I(s;o)-\mathbb E[\log p_C]$, establishing Equation \eqref{eq:efe}. Replacing normalized log preferences with logits subtracts $\log\sum_o\exp(C_o)$ per policy step. This constant affects reported magnitudes but not a fixed-model, fixed-convention policy ranking.

For VFE, substitute $p(o,s)=p(s\mid o)p(o)$ into Equation \eqref{eq:vfe}. The log-evidence term factors out of the normalized expectation, leaving posterior KL divergence. With $q=p(s\mid o)$ the divergence is zero. Exact-zero handling uses $0\log0=0$ and retains infinite divergences for support violations.

Tests additionally compare batched binary log-odds inference with sequential core Bayesian updates, check asymmetric column-stochastic transitions, and check preference-shift and horizon-aggregation identities. Mathematical identity tests complement software coverage; coverage alone does not establish theoretical correctness.

### Retained sensor-study estimates and primary paired contrasts {#sec:validation_results}

| Condition | Accuracy (%) | Brier loss | Log loss (nats) | Observations/trial |
|---|---:|---:|---:|---:|
| Q1_fixed | 76.36 | 0.1781 | 0.5519 | 3.000 |
| Q2_metadata | 84.68 | 0.1235 | 0.4051 | 3.000 |
| Q3_adaptive | 90.34 | 0.0812 | 0.2896 | 3.892 |
| Q4_learned | 84.68 | 0.1258 | 0.4114 | 3.000 |
| Q2_misleading | 54.12 | 0.3306 | 1.1861 | 3.000 |
| Fixed_four | 86.75 | 0.0924 | 0.3017 | 4.000 |
| Fixed_five | 90.74 | 0.0708 | 0.2361 | 5.000 |

| Contrast | Difference (points) | 95% interval | $d_z$ | Holm $p$ |
|---|---:|---|---:|---:|
| H1 | 8.325 | [7.442, 9.217] | 3.439 | 0.00030 |
| H2 | 5.658 | [5.058, 6.267] | 3.275 | 0.00030 |
| H3 | 8.325 | [7.442, 9.217] | 3.439 | 0.00030 |

These estimates are computed from `results/summary.json`. Accuracy differences are in percentage points. Each comparison uses 30 paired seed means. The primary p-values are Monte Carlo sign-flip estimates at finite resolution, with Holm correction across H1--H3. The intervals are marginal percentile-bootstrap intervals; they are not adjusted simultaneous intervals. The supplementary paired t-tests and full seed-level data are retained in the artifact set.

### Active-sensing outcomes and the distinction between scores and preferences

| Action strategy | Accuracy (%) | Brier loss | Log loss (nats) | Inspections/trial |
|---|---:|---:|---:|---:|
| Sampled EFE | 71.23 | 0.1747 | 0.5270 | 0.617 |
| Always inspect | 84.90 | 0.1282 | 0.4244 | 1.000 |
| Always blind | 49.97 | 0.2500 | 0.6931 | 0.000 |

These are means over 30 paired seeds, each with 200 generated world trials. The action world is sampled from the actual imported GNN D/B/A tensors and every posterior uses the same declared numerical contracts. The 187-point exact policy grid has a maximum risk-plus-ambiguity identity residual of $1.11\times10^{-16}$. Full marginal intervals, exact expectations and 14 paired comparisons are retained in the active-sensing CSV tables. These exploratory analyses introduce no additional hypothesis-test family.

The minimum-EFE action and the sampled action have different meanings. At the declared precision, the policy posterior retains stochastic choice. Always inspecting is a comparator with a larger informative-sensing budget, rather than an algorithm that estimates or optimizes the supplied preference vector. Thus, the results do not establish universal superiority, autonomous goal revision or empirical validity of the environment model.

### Modular implementation and asymptotic computational complexity {#sec:implementation_architecture}

`core` defines categorical models and exact inference. `framework` supplies the taxonomy, monitoring illustrations, and structural security diagnostics. `analysis` contains generators, statistics, validation, experiments, and pipeline orchestration. `visualization` creates educational and experiment figures; `utils` supplies manuscript validation and provenance. No parent repository infrastructure is required by the research pipeline.

For a dense model with $N_s$ states, $N_o$ outcomes, $N_a$ available actions and a policy of $T$ steps, a single policy costs approximately $\mathcal O(T(N_s^2+N_oN_s))$ for transitions and predictions, with $\mathcal O(N_oN_s)$ likelihood entropy preprocessing. Evaluating $N_\pi$ candidate policies multiplies the per-policy cost by $N_\pi$. The available-action count identifies the transition tensor's third axis; it is not an additional factor when evaluating a fixed sequence. The implementation does not claim sparse scaling or measured support for 1,000-state models. No runtime table is reported without a retained benchmark protocol and hardware description.

### Reproduction with pinned GNN and publication-renderer dependencies {#sec:reproducibility}

Run from a clean checkout:

First provide the real upstream GNN checkout through `GNN_ROOT`, pinned by `src/core/gnn_models/upstream.lock.json`. The supported package minimum is Python 3.11; the recorded scientific environment is Python 3.12. No upstream pipeline or native backend is silently substituted for the local exact categorical runtime.

```bash
uv sync --locked --extra dev --extra research --python 3.12
MPLBACKEND=Agg uv run --python 3.12 pytest --cov=src --cov-report=term-missing
uv run --python 3.12 python scripts/07_analysis_pipeline.py
```

The pipeline writes the source-backed results and standalone HTML manuscript to `results/`. Changing seed counts, trial counts, training size, numerical libraries or model configuration creates a different run, which must be described as such. Random-number generators are local; reproducibility does not rely on global `numpy.random.seed`. Source and output digests support verification within a recorded environment. PDF figure metadata or library/platform differences can change binary hashes without changing numerical estimates.

The older scripts 01--05 generate educational diagrams under `output/figures/`; those illustrations are separate from the retained experiment evidence. Script 06 validates the manuscript rather than inserting unreviewed or stale figures automatically.
