# Supplemental Notation for Models, Objectives, and Statistics {#sec:symbols}

This is the common notation reference for the main paper and technical supplement. Symbols denote quantities within a specified model; they do not by themselves identify a biological mechanism or justify a normative objective. The tensor atlas in Figure \ref{fig:canonical_model_atlas} shows the concrete conventions used by the packaged models.

```{=latex}
\clearpage
```

## States, observations, and executable model components

| Symbol | Meaning and convention |
|---|---|
| $s,s'$ | Current and next hidden-state indices; the first transition axis is the destination |
| $o$ | Categorical observation or outcome index |
| $a$ | Action index; action 0 is blind and action 1 is inspect in the action study |
| $j$ | Dummy summation index over the state or outcome set indicated by the expression |
| $m$ | Metadata about an observation's source, reliability, context or provenance |
| $A,\ A_{o,s}$ | Observation likelihood $p(o\mid s)$; columns sum to one |
| $A_{:,s}$ | Full outcome distribution conditional on state $s$; colon selects all outcomes |
| $B,\ B_{s',s,a}$ | Transition likelihood $p(s'\mid s,a)$; each action slice is column stochastic |
| $B(a)$ | Matrix slice of $B$ for action $a$; multiplying a state column vector predicts its successor |
| $C,\ C_o$ | Finite outcome preference logits, not probabilities or measured rewards |
| $D,\ D_s$ | Normalized initial state prior |
| $p_C(o)$ | Softmax-normalized outcome preference induced by $C$ |
| $p(o,s),\ p(o),\ p(s\mid o)$ | Joint model probability, evidence and exact conditional posterior |
| $p(o\mid s,m)$ | Observation likelihood conditioned on metadata |
| $q,\ q(s),\ q_s$ | Candidate, posterior or predictive state distribution, specified by context |
| $q_o$ | Predictive outcome distribution |
| $e(o)$ | Normalized nonnegative virtual-evidence weights over possible observations |
| $L_e(s)$ | Evidence likelihood induced by the weighted sum of observation likelihoods |
| $r$ | Actual informative-observation reliability; $r_i$ is the reliability of sensor $i$ |
| $\rho$ | Agent-assumed informative-observation reliability in the mismatch analysis |
| $c$ | Blind/null-outcome preference logit in the action task |
| $w$ | World subscript; distinguishes world probabilities/tensors from agent assumptions |
| $p_w(s',o\mid a)$ | World joint distribution of next state and outcome given action |
| $y(s')$ | Binary context label given by next-state parity in the four-state action model |
| $\hat p_a(o)$ | Agent forecast of context 1 after outcome $o$ under action $a$ |

The action model orders states as blind context 0, blind context 1, informative context 0, informative context 1. Outcomes are null, indication of context 0, indication of context 1. The diagram's labels s0–s3 denote those state indices, not four state factors. The single-factor GNN profile admits a categorical state variable; the product interpretation is an authored meaning for its categories.

```{=latex}
\clearpage
```

## Information measures, evaluative objectives, and policy selection

| Symbol | Meaning and convention |
|---|---|
| $F(q,o)$ | Exact variational free energy for a candidate posterior and explicit joint model |
| $G,\ G_\tau$ | Normalized expected free energy, or its contribution at policy step $\tau$ |
| $G_{\mathrm{inspect}},G_{\mathrm{blind}}$ | Normalized EFE for the two one-step sensing policies |
| $\pi$ | An open-loop action sequence when used as a policy; $\pi(a)$ denotes a one-step action distribution in the world-risk expression |
| $\tau,\ q_\tau,\ a_\tau$ | Policy step, predicted state distribution and prescribed action at that step |
| $\gamma$ | Positive policy precision multiplying negative EFE before normalization |
| $H(\cdot)$ | Shannon entropy; distinct from the horizon notation used in some external literature |
| $h(r)$ | Binary entropy at reliability $r$ |
| $I,\ I(s;o\mid\pi)$ | Expected state information gain under the specified policy |
| $D_{\mathrm{KL}}[q\Vert p]$ | KL divergence; infinite when $q$ gives positive mass where $p$ is zero |
| $\mathbb E_q[\cdot]$ | Expectation under distribution $q$; omitted subscripts are specified locally |
| $\log,\exp$ | Natural logarithm and exponential; information quantities use nats |
| $\ell(\hat p,y)$ | Binary scoring loss applied to a forecast and realized context label |
| $R_\ell(\pi;w,\mathrm{agent})$ | Exact expected scoring loss under world probabilities and an agent's forecasts |
| $R_{\mathrm{Brier}},R_{\log}$ | Exact Brier and logarithmic risks |
| $r(o),\beta$ | Reward function and positive scale in the related-work mapping from reward to preference; $r(o)$ is not sensor reliability |
| $\widetilde G$ | Illustrative weighted decision score, not the executed normalized EFE |
| $w_e,w_p,w_m$ | Authored heuristic weights for information, preference and metadata terms |
| $K(m)$ | Authored metadata penalty in that illustrative weighted score |

**total** is the compatibility API's raw-logit score; **normalized_total** is its normalized counterpart. Their fixed-model relationship and horizon conventions are stated in Supplement \ref{sec:formal_contracts}. Adding a constant to all preference logits leaves normalized preferences unchanged. These API fields are not interchangeable when comparing models with different preference normalizers.

```{=latex}
\clearpage
```

## Statistical estimands, uncertainty, and computational notation

| Symbol or term | Meaning and convention |
|---|---|
| $\Delta,\overline{\Delta},s_\Delta$ | Paired seed-level difference, its mean and its sample standard deviation |
| $d_z=\overline{\Delta}/s_\Delta$ | Standardized within-pair difference; undefined for zero variation unless explicitly handled |
| H1–H3 | The three primary paired accuracy comparisons; their exact contrasts are in the protocol |
| $p$-value | Tail evidence from the named test; distinct from model probabilities written as $p(\cdot)$ |
| Beta(1,1) | Uniform prior over a sensor reliability in the supervised fitting procedure |
| $N_s,N_o,N_a$ | Counts of hidden states, outcomes and available actions |
| $N_\pi,T$ | Number of evaluated candidate policies and number of steps in each policy |
| $\mathcal O(\cdot)$ | Asymptotic dense arithmetic cost, not an observed runtime benchmark |
| Seed | Independent generated-dataset unit for paired uncertainty estimation |
| Trial | A held-out context and potential observations within a seed |
| Marginal interval | An interval for one stated quantity, without simultaneous familywise coverage |
| Sign flip | Paired resampling test requiring the stated sign-exchangeability assumption |

## Conceptual terms and epistemic boundaries

**Q1–Q4** name inferential, contextual, monitoring and revision roles in Figure \ref{fig:quadrant_orientation}; they are not measured natural cognitive kinds. **Metadata** is information about the source, production or reliability of task-level evidence. Its role depends on the task relation.

**Monitoring** evaluates a property of inference; **control** changes processing on that basis. **Calibration** concerns agreement between probabilistic forecasts and observed frequencies, rather than posterior concentration. Proper losses measure forecast quality and need not be pure calibration statistics.

**Meta-epistemic practice** examines the representation, acquisition and reliability of evidence. **Meta-pragmatic practice** examines action, preferred consequences, budgets and the criteria authorizing revision. **Structural integrity** denotes validity of numerical contracts; it does not establish truthful metadata, absence of tampering or legitimacy of preferences.
