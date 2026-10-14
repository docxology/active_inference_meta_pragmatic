# Symbols and Glossary {#sec:symbols}

| Symbol | Meaning and convention |
|---|---|
| $s,s'$ | Current and destination hidden states |
| $o,a,\pi$ | Outcome, action, and open-loop action sequence |
| $A_{o,s}$ | Column-stochastic observation likelihood |
| $B_{s',s,a}$ | Column-stochastic state transition for action $a$ |
| $C_o$ | Finite outcome preference logit |
| $D_s$ | Initial normalized state prior |
| $e(o)$ | Normalized virtual evidence weights |
| $p_C(o)$ | Softmax-normalized preference distribution |
| $q_s,q_o$ | Predictive state and outcome distributions |
| $F,G$ | Variational and expected free energy, in nats |
| $H,I,D_{\mathrm{KL}}$ | Shannon entropy, mutual information, KL divergence |
| $\gamma$ | Positive policy precision |
| $d_z$ | Mean paired difference divided by SD of paired differences |
| Q1--Q4 | Operational taxonomy labels, not natural cognitive kinds |

**Metadata** is information about the source, production or reliability of task-level evidence. **Monitoring** evaluates a property of inference; **control** changes processing based on that evaluation. **Calibration** concerns agreement between probabilistic predictions and observed outcomes, and differs from posterior concentration. **Structural integrity** denotes validity of a model's numerical contracts; it does not establish absence of malicious alteration.
