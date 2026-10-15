# Exact world–agent mismatch analysis

The agent's declared likelihood is a hypothesis about the world. `analysis.model_robustness` keeps those two objects separate and evaluates their consequences by finite enumeration. This extends the [matched active-sensing task](active_sensing.md); it does not fit a revised agent.

## Design

The agent remains at reliability 0.85, blind-outcome preference logit 0.15 and precision 4. Twenty-one world reliabilities span 0.50 to 1.00. Every realization is materialized and imported through the real pinned upstream GNN parser. The fixed agent's EFE posterior and the always-inspect/blind baselines are evaluated under each world's joint next-state/outcome distribution.

The exact scores integrate over next state, outcome and action. Context is next-state parity. The API requires four states, three outcomes and two actions. These dimensions and the meaning of parity are part of the task contract, not a generic label-inference API. The two inputs must share state/outcome/action semantics.

```python
import numpy as np
from analysis.active_sensing import active_sensing_model
from analysis.model_robustness import exact_context_scores

scores, cells = exact_context_scores(
    active_sensing_model(0.5), active_sensing_model(0.85), np.array([0., 1.])
)
assert abs(scores["brier"] - 0.3725) < 1e-12
```

## Interpretation and singularities

Accuracy may hide probabilistic failure. At world reliability 0.50, always inspect and always blind are both at chance. Their exact Brier losses differ: 0.3725 versus 0.25. The inspector reports 0.15 or 0.85 even though the world's conditional probability is 0.50. The fixed EFE mixture inherits part of that loss.

Only zero-mass events are omitted. An observation impossible under the agent raises `ValidationError`; a positive world event with zero forecast probability also raises. The implementation never substitutes clipped finite log loss for an infinite mathematical risk. Such singular cases require an explicit evaluation policy in a future extension. The retained grid uses an interior agent reliability and is finite.

## Retained evidence

| Artifact in `results/` | Meaning |
|---|---|
| `model_robustness_metrics.csv` | 63 exact strategy-by-world score rows |
| `model_robustness_calibration.csv` | Exact conditional frequencies, forecasts and world masses |
| `robustness_gnn/` | 21 content-addressed world/agent specifications |
| `figures/model_robustness.{png,pdf,svg}` | Exact score curves and inspection-calibration panel |
| `summary.json` → `model_robustness` | Fixed design, selected model digests and row counts |

Reproduce with the [pipeline commands](quickstart.md). Tests compare the enumerator against independent closed forms at four reliabilities and three action mixtures, and exercise invalid dimensions/probabilities, impossible observations and zero forecasts. Curves have no Monte Carlo uncertainty; grid points are not independent samples and receive no confidence intervals or p-values. The existing [statistical families](statistics.md) are unchanged.
