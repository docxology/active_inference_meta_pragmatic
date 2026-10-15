# Testing Model Commitments Through Controlled Synthetic Studies {#sec:methodology}

The framework becomes scientifically useful when its roles identify interventions with observable consequences. The studies therefore compare concrete mechanisms rather than treating the quadrant names as algorithms. Their design is synthetic, fixed in code and not preregistered. No participant data or deployment outcomes are analyzed. Complete task parameters, randomization, statistical procedures and retained-file definitions are in Supplement \ref{sec:protocol}.

## Source reliability, evidence acquisition, and supervised learning

The sensor study compares a fixed reliability assumption with source-specific metadata, confidence-triggered acquisition and reliability learned from separate labeled training. Every strategy shares the same held-out contexts and potential sensor observations within each seed. A misleading-metadata control tests whether contextual information can make inference worse. Fixed sensing budgets distinguish the effects of additional evidence from those of a stopping rule.

Figure \ref{fig:quadrant_experiment} shows why a single ranking would obscure the argument. Reliable metadata improves a misspecified baseline in this environment; further evidence can improve predictions while consuming more observations. Fitting reliability is an externally supervised intervention and carries a training cost. Falsely reported metadata can undermine a mathematically valid update. These are consequences of explicit model choices, not evidence that higher-order processing is intrinsically superior.

```{=latex}
\begin{figure}[H]
\centering
\includegraphics[width=0.95\textwidth]{../results/figures/quadrant_experiment.png}
\caption{Predictive performance and observation use under seven explicit sensor strategies. Small symbols show 30 independent seed means; large symbols and capped dark bars show means and marginal 95 percent seed-bootstrap intervals. (a) Higher accuracy is better; (b,c) lower Brier and logarithmic loss is better; (d) acquired observations expose resource differences. Q1--Q4 refer to the implemented fixed-model, true-metadata, adaptive-sensing and fitted-model conditions, respectively; they do not test the full philosophical roles. Misled uses false metadata; F4/F5 use four/five reports. Counts exclude separate training. Paired contrasts, rather than overlap of these marginal intervals, address strategy differences.}
\label{fig:quadrant_experiment}
\end{figure}
```

## Action selection under explicit preferences and model assumptions

The separate action task samples the policy probabilities actually returned by EFE evaluation. Always-inspect and always-blind baselines share the generated contexts and potential informative outcomes. Preferences can make an uninformative action attractive; a policy can therefore sacrifice classification accuracy without violating its declared objective. The mechanism is inspected as an example of how information and value enter action, rather than as a universal prescription for sensing.

An exact comparison then fixes the agent's assumptions while varying the world's actual reliability. Each side has a separately imported GNN specification. Forecasts are evaluated using world probabilities, so a confident but mistaken likelihood becomes visible without attributing Monte Carlo noise to the discrepancy. This separation is essential to model criticism: the model's own expectations cannot be its only tribunal.

## Experimental units, uncertainty, and the scope of the evidence

Independent generated seeds are the unit of uncertainty. Paired seed estimates, proper scoring losses, observation counts and prespecified adverse controls provide complementary views of each mechanism. Training data remain separate from held-out evaluation. Bootstrap intervals are marginal; the primary sign-flip tests retain their stated exchangeability assumption and three-comparison Holm family \cite{efron1993bootstrap,holm1979sequential}. Exploratory sensitivity analyses introduce no new confirmatory rejection claims.

The exact reliability grid is finite enumeration, not a collection of empirical replications. Its curves receive neither sampling intervals nor p-values. Probabilistic scores assess forecast quality, while calibration examines agreement between forecasts and outcomes \cite{gneiting2007scoring,dawid1982calibrated}. Computational checks, synthetic behavior and philosophical interpretation support different conclusions; none substitutes for the others.
