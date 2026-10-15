import numpy as np
import pytest

from analysis.diagnostics import (
    paired_interval,
    prediction_diagnostics,
    stopping_sensitivity,
)
from utils.exceptions import ValidationError


@pytest.mark.parametrize(
    "values,resamples",
    [([1], 100), ([1, np.nan], 100), ([[1, 2]], 100), ([1, 2], 99), ([1, 2], True)],
)
def test_paired_interval_rejects_invalid(values, resamples):
    with pytest.raises(ValidationError):
        paired_interval(np.array(values), resamples)


def test_paired_interval_constant_and_reproducible():
    assert paired_interval(np.ones(6)) == {"mean": 1, "lower": 1, "upper": 1}
    assert paired_interval(np.arange(6)) == paired_interval(np.arange(6))


def test_diagnostics_known_scores_signs_and_endpoint_bins():
    states = np.tile([0, 1], 4)
    seeds = np.repeat([10, 20, 30, 40], 2)
    evidence = prediction_diagnostics(
        states,
        seeds,
        {"Q2_metadata": states.astype(float), "Q1_fixed": np.full(8, 0.5)},
        {"Q2_metadata": np.full(8, 3), "Q1_fixed": np.full(8, 3)},
        100,
    )
    accuracy = next(
        r for r in evidence["paired_estimates"] if r["metric"] == "accuracy"
    )
    brier = next(r for r in evidence["paired_estimates"] if r["metric"] == "brier")
    assert accuracy["mean"] == 0.5
    assert accuracy["positive"] == 4
    assert accuracy["sign_test_p_unadjusted"] == pytest.approx(0.125)
    assert brier["mean"] == -0.25
    cost = next(
        r for r in evidence["paired_estimates"] if r["metric"] == "mean_observations"
    )
    assert cost["ties"] == 4 and cost["sign_test_p_unadjusted"] == 1
    bins = [
        r
        for r in evidence["calibration_bins"]
        if r["strategy"] == "Q2_metadata" and r["n_bins"] == 10
    ]
    assert [r["bin"] for r in bins] == [0, 9]
    assert sum(r["count"] for r in bins) == 8
    assert all(r["predicted"] == r["observed"] for r in bins)


@pytest.mark.parametrize(
    "states,seeds,p,cost",
    [
        ([0, 1], [0], [0.2, 0.8], [3, 3]),
        ([0, 1], [0, 0], [0.2, 0.8], [3, 3]),
        ([0, 2], [0, 1], [0.2, 0.8], [3, 3]),
        ([0, 1], [0, np.nan], [0.2, 0.8], [3, 3]),
        ([0, 1], [0, 1.5], [0.2, 0.8], [3, 3]),
        ([0, 1], [0, 1], [0.2], [3, 3]),
        ([0, 1], [0, 1], [0.2, np.inf], [3, 3]),
        ([0, 1], [0, 1], [-0.2, 0.8], [3, 3]),
        ([0, 1], [0, 1], [0.2, 0.8], [-3, 3]),
        ([0, 1], [0, 1], [0.2, 0.8], [np.inf, 3]),
    ],
)
def test_prediction_diagnostics_rejects_invalid(states, seeds, p, cost):
    with pytest.raises(ValidationError):
        prediction_diagnostics(
            np.array(states),
            np.array(seeds),
            {"a": np.array(p)},
            {"a": np.array(cost)},
            100,
        )


def test_strategy_keys_must_match():
    with pytest.raises(ValidationError):
        prediction_diagnostics(np.array([0, 1]), np.array([0, 1]), {}, {})
    with pytest.raises(ValidationError):
        prediction_diagnostics(
            np.array([0, 1]),
            np.array([0, 1]),
            {"a": np.array([0, 1])},
            {"b": np.ones(2)},
        )


def test_threshold_endpoints_and_original_rule_reproduce_retained_trials():
    from analysis.experiments import ExperimentConfig, run_quadrant_experiment

    config = ExperimentConfig(
        n_seeds=3, n_trials=30, n_training=20, bootstrap_resamples=100
    )
    experiment = run_quadrant_experiment(config)
    trials = experiment["trials"]
    result = stopping_sensitivity(
        np.array([[r[f"sensor_{j}"] for j in range(5)] for r in trials]),
        np.array([r["state"] for r in trials]),
        np.array([r["seed"] for r in trials]),
        config.sensor_reliabilities,
        100,
    )
    for threshold, strategy in [
        (0.5, "Q2_metadata"),
        (0.9, "Q3_adaptive"),
        (1, "Fixed_five"),
    ]:
        for row in result["stopping_seed_metrics"]:
            if row["threshold"] == pytest.approx(threshold):
                reference = next(
                    r
                    for r in experiment["replicates"]
                    if r["seed"] == row["seed"] and r["strategy"] == strategy
                )
                for metric in ("accuracy", "brier", "log_loss", "mean_observations"):
                    assert row[metric] == pytest.approx(reference[metric])
    with pytest.raises(ValidationError):
        stopping_sensitivity(
            np.zeros((2, 4)), np.array([0, 1]), np.array([0, 1]), (0.8,) * 5, 100
        )
