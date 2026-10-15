"""Exploratory paired estimates and resource sensitivity on retained test trials."""

from __future__ import annotations

from typing import TypedDict

import numpy as np
from numpy.typing import NDArray
from scipy.stats import binomtest

from core.gnn import sensor_model
from utils.exceptions import ValidationError
from .experiments import gnn_sensor_posterior


class Estimate(TypedDict):
    mean: float
    lower: float
    upper: float


def paired_interval(values: NDArray, resamples: int = 5000) -> Estimate:
    """Percentile interval for a mean over independent seed differences."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.isfinite(values).all():
        raise ValidationError("At least two finite seed values required")
    if not isinstance(resamples, int) or isinstance(resamples, bool) or resamples < 100:
        raise ValidationError("At least 100 bootstrap resamples required")
    rng = np.random.default_rng(314159)
    means = rng.choice(values, size=(resamples, len(values))).mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return {"mean": float(values.mean()), "lower": float(low), "upper": float(high)}


def prediction_diagnostics(
    states: NDArray,
    seeds: NDArray,
    predictions: dict[str, NDArray],
    costs: dict[str, NDArray],
    resamples: int = 5000,
) -> dict[str, list[dict[str, str | int | float]]]:
    """Retain bin counts and paired seed estimates without new significance claims."""
    states, seeds = np.asarray(states), np.asarray(seeds)
    if states.ndim != 1 or seeds.shape != states.shape or len(np.unique(seeds)) < 2:
        raise ValidationError(
            "Matched one-dimensional states and independent seeds required"
        )
    if (
        not np.isin(states, [0, 1]).all()
        or not np.isfinite(seeds).all()
        or np.any(seeds != np.floor(seeds))
    ):
        raise ValidationError("Binary states and finite seed identifiers required")
    if not predictions or predictions.keys() != costs.keys():
        raise ValidationError("Prediction and cost strategies must match")
    bins, rows, comparisons = [], [], []
    for strategy, raw in predictions.items():
        p, cost = np.asarray(raw, dtype=float), np.asarray(costs[strategy], dtype=float)
        if p.shape != states.shape or cost.shape != states.shape:
            raise ValidationError("Probabilities and costs must match trial rows")
        if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
            raise ValidationError("Probabilities must be finite in [0,1]")
        if not np.isfinite(cost).all() or np.any(cost < 0):
            raise ValidationError("Observation costs must be finite and nonnegative")
        # Exact zero support receives the same finite reporting floor as the main study.
        clipped = np.clip(p, np.finfo(float).eps, 1 - np.finfo(float).eps)
        losses = {
            "accuracy": ((p > 0.5) == states).astype(float),
            "brier": (p - states) ** 2,
            "log_loss": -(states * np.log(clipped) + (1 - states) * np.log1p(-clipped)),
            "mean_observations": cost,
        }
        for seed in np.unique(seeds):
            chosen = seeds == seed
            rows.append(
                {
                    "strategy": strategy,
                    "seed": int(seed),
                    **{
                        metric: float(value[chosen].mean())
                        for metric, value in losses.items()
                    },
                }
            )
        for n_bins in (5, 10, 20):
            groups = np.minimum((p * n_bins).astype(int), n_bins - 1)
            for index in range(n_bins):
                chosen = groups == index
                if chosen.any():
                    bins.append(
                        {
                            "strategy": strategy,
                            "n_bins": n_bins,
                            "bin": index,
                            "count": int(chosen.sum()),
                            "n_seeds": int(len(np.unique(seeds[chosen]))),
                            "predicted": float(p[chosen].mean()),
                            "observed": float(states[chosen].mean()),
                        }
                    )
    names = list(predictions)
    for treated, control in (
        ("Q2_metadata", "Q1_fixed"),
        ("Q3_adaptive", "Q2_metadata"),
        ("Q4_learned", "Q2_metadata"),
        ("Q2_misleading", "Q2_metadata"),
        ("Q3_adaptive", "Fixed_four"),
        ("Q3_adaptive", "Fixed_five"),
    ):
        if treated not in names or control not in names:
            continue
        for metric in ("accuracy", "brier", "log_loss", "mean_observations"):
            a = np.array(
                [r[metric] for r in rows if r["strategy"] == treated], dtype=float
            )
            b = np.array(
                [r[metric] for r in rows if r["strategy"] == control], dtype=float
            )
            delta = a - b
            positive, negative = int((delta > 0).sum()), int((delta < 0).sum())
            comparisons.append(
                {
                    "treated": treated,
                    "control": control,
                    "metric": metric,
                    **paired_interval(delta, resamples),
                    "n_pairs": len(delta),
                    "positive": positive,
                    "negative": negative,
                    "ties": int((delta == 0).sum()),
                    "sign_test_p_unadjusted": float(
                        binomtest(positive, positive + negative).pvalue
                    )
                    if positive + negative
                    else 1.0,
                }
            )
    return {
        "calibration_bins": bins,
        "seed_metrics": rows,
        "paired_estimates": comparisons,
    }


def stopping_sensitivity(
    observations: NDArray,
    states: NDArray,
    seeds: NDArray,
    reliabilities: tuple[float, ...],
    resamples: int = 5000,
) -> dict[str, list[dict[str, str | int | float]]]:
    """Evaluate eleven fixed thresholds on common trials; do not select a winner."""
    observations = np.asarray(observations)
    if observations.shape != (len(states), 5) or len(reliabilities) != 5:
        raise ValidationError("Five observation columns and reliabilities required")
    models = [sensor_model(r) for r in reliabilities]
    posteriors = {
        n: gnn_sensor_posterior(observations[:, :n], models[:n]) for n in (3, 4, 5)
    }
    rows, summaries = [], []
    for threshold in np.linspace(0.5, 1, 11):
        p, cost = posteriors[3].copy(), np.full(len(states), 3)
        for n in (4, 5):
            acquire = np.maximum(p, 1 - p) < threshold
            p[acquire] = posteriors[n][acquire]
            cost[acquire] += 1
        diagnostic = prediction_diagnostics(
            states, seeds, {"threshold": p}, {"threshold": cost}, resamples
        )
        metrics = diagnostic["seed_metrics"]
        rows.extend(
            {
                "threshold": float(threshold),
                **{
                    key: float(row[key])
                    for key in (
                        "seed",
                        "accuracy",
                        "brier",
                        "log_loss",
                        "mean_observations",
                    )
                },
            }
            for row in metrics
        )
        for metric in ("accuracy", "brier", "log_loss", "mean_observations"):
            estimate = paired_interval(
                np.array([row[metric] for row in metrics], dtype=float), resamples
            )
            summaries.append(
                {"threshold": float(threshold), "metric": metric, **estimate}
            )
    return {"stopping_seed_metrics": rows, "stopping_summary": summaries}
