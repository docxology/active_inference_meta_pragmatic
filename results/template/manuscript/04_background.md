# Background and Numerical Conventions {#sec:background}

## Discrete generative model

Let $s$ index hidden states, $o$ observations, and $a$ actions. The implementation uses $A_{o,s}=p(o\mid s)$, $B_{s',s,a}=p(s'\mid s,a)$, finite outcome preference logits $C_o$, and a normalized initial prior $D_s$. Columns of $A$ and of each action slice of $B$ sum to one. A two-dimensional $B$ is promoted to a single-action tensor. Arrays with incompatible dimensions, empty axes, negative probabilities, nonfinite values, or invalid normalization are rejected.

The normalized outcome preference is $p_C(o)=\exp(C_o)/\sum_j\exp(C_j)$. Logits are not probabilities; adding a constant to all entries leaves the normalized preference unchanged. Model validation copies inputs so that later mutation of caller-owned arrays does not silently change an initialized model. Public model arrays remain inspectable and mutable; callers must validate deliberate revisions.

## Bayesian state inference

For a categorical observation, Bayes' rule gives:

::: {#eq:bayes}
$$
q(s\mid o)=\frac{A_{o,s}D_s}{\sum_j A_{o,j}D_j}.
\tag{1}
$$
:::

For a normalized nonnegative virtual-evidence vector $e(o)$, the implementation uses $L_e(s)=\sum_o e(o)A_{o,s}$ and replaces $A_{o,s}$ with $L_e(s)$ in Equation [(1)](#eq:bayes). This convention models evidence about possible outcomes. It differs from a Jeffrey update, which mixes already-conditioned posteriors. A uniform evidence vector is uninformative because each likelihood column sums to one. Zero-probability states retain zero mass; evidence impossible under the model and prior raises an error instead of being repaired by clipping.

## Variational free energy

Given an explicit joint distribution and a normalized candidate posterior $q$, variational free energy is:

::: {#eq:vfe}
$$
F(q,o)=\sum_s q(s)\left[\log q(s)-\log p(o,s)\right]
=-\log p(o)+D_{\mathrm{KL}}\left[q(s)\Vert p(s\mid o)\right].
\tag{2}
$$
:::

Equation [(2)](#eq:vfe) bounds negative log evidence and reaches the bound at the exact posterior. Candidate beliefs assigning positive mass outside posterior support have infinite free energy. The exact implementation is `calculate_variational_free_energy`; the older model-free `FreeEnergyPrinciple.calculate_free_energy` path remains an explicitly labeled schematic score for compatibility. Its trajectories and state-boundary diagrams do not establish a variational bound, conditional independence, or the physical claims of the FEP. Supplying a generative model to that class selects the exact calculation.

## Expected free energy

For each future policy step, propagate $q_\tau=B(a_\tau)q_{\tau-1}$ and predict $q_o=Aq_\tau$. With an exact conditional update, state information gain is $I(s;o)=H(q_o)-\sum_s q_\tau(s)H(A_{:,s})$. Our normalized planning score is:

::: {#eq:efe}
$$
G_\tau=-I(s;o\mid\pi)-\sum_o q_o(o)\log p_C(o)
=D_{\mathrm{KL}}[q_o\Vert p_C]+\sum_s q_\tau(s)H(A_{:,s}).
\tag{3}
$$
:::

The equivalence in Equation [(3)](#eq:efe) follows by expanding mutual information and KL divergence. It is exact for this finite, known-likelihood predictive model. It does not include uncertainty about parameters, posterior approximation error, or observation-contingent replanning.

For compatibility, the returned `total` uses the raw-logit score $-I-\mathbb{E}[C]$. `normalized_total` adds `logsumexp(C)` per step and equals risk plus ambiguity. Normalized values are evaluated directly from stable log preferences to avoid cancellation under large constant logit shifts. Policy rankings agree mathematically for a fixed model and horizon convention. Mean aggregation is the legacy default; sum aggregation implements additive finite-horizon costs. Comparing different horizons or different preference models requires specifying this convention and normalization explicitly.

Policy selection accepts current posterior beliefs, with $D$ used when beliefs are omitted. It returns an argmin and a policy distribution proportional to $\exp(-\gamma G)$, where $\gamma>0$ is precision. Increasing precision concentrates this distribution; it does not change an exact argmin. Equal scores retain a uniform distribution. All entropy and KL quantities use natural logarithms and are measured in nats.

![Exact EFE sensitivity for a binary symmetric observation model, uniform state beliefs, identity dynamics and C=(1,-1). Curves are mathematical evaluations, without sampling intervals.](../figures/efe_sensitivity.png){#fig:efe_sensitivity width=95%}
