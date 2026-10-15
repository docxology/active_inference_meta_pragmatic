"""A GNN-specified action task separating epistemic value and outcome preference."""

from __future__ import annotations

from typing import TypedDict

import numpy as np
from scipy.special import xlogy

from core.active_inference import ActiveInferenceFramework
from core.gnn import (
    MODEL_DIRECTORY,
    ImportedGNNModel,
    load_gnn_model,
    specified_model,
    verify_upstream,
)
from core.probability import bayesian_update
from core.simulation import sample_potential_outcomes
from utils.exceptions import ValidationError
from .diagnostics import paired_interval

Row = dict[str, str | int | float]


class SensingStudy(TypedDict):
    config: dict[str, int | float | str]
    specifications: dict[str, str]
    landscape: list[Row]
    trials: list[Row]
    seed_metrics: list[Row]
    estimates: list[Row]
    comparisons: list[Row]


def active_sensing_model(
    reliability: float = 0.85, safe_logit: float = 0.15
) -> ImportedGNNModel:
    """Encode context × observation mode; actions preserve context and set mode."""
    if not np.isfinite(reliability) or not 0.5 <= reliability <= 1:
        raise ValidationError("Sensing reliability must be finite in [0.5,1]")
    if not np.isfinite(safe_logit) or safe_logit < 0:
        raise ValidationError("Safe-outcome preference must be finite and nonnegative")
    base = load_gnn_model(MODEL_DIRECTORY / "active_sensing.md").model
    A, C = base.A.copy(), base.C.copy()
    A[1:, 2:] = [[reliability, 1 - reliability], [1 - reliability, reliability]]
    C[0] = safe_logit
    return specified_model(
        A,
        base.B,
        C,
        base.D,
        f"Active sensing r={reliability:.2f} safe_logit={safe_logit:.2f}",
    )


def _policy_terms(
    imported: ImportedGNNModel, precision: float = 4
) -> tuple[list[Row], np.ndarray]:
    framework = ActiveInferenceFramework(imported.model, precision=precision)
    _, selection = framework.select_optimal_policy(
        [np.array([0]), np.array([1])], imported.model.D
    )
    rows = []
    for action in range(2):
        _, parts = framework.calculate_expected_free_energy(
            imported.model.D, np.array([action])
        )
        rows.append({"action": action, **parts})
    return rows, np.asarray(selection["policy_probabilities"])


def run_active_sensing(
    n_seeds: int = 30, n_trials: int = 200, resamples: int = 5000
) -> SensingStudy:
    """Compare sampled EFE policies with two fixed baselines on common trials."""
    if any(
        not isinstance(v, int) or isinstance(v, bool) or v < 2
        for v in (n_seeds, n_trials)
    ):
        raise ValidationError("At least two independent seeds and trials required")
    paired_interval(np.array([0, 1]), resamples)
    revision = verify_upstream()
    specifications: dict[str, str] = {}
    landscape: list[Row] = []
    for reliability in np.linspace(0.5, 1, 11):
        for safe_logit in np.linspace(0, 0.8, 17):
            imported = active_sensing_model(
                round(float(reliability), 12), round(float(safe_logit), 12)
            )
            specifications[imported.specification_sha256] = imported.specification
            terms, probability = _policy_terms(imported)
            landscape.append(
                {
                    "reliability": float(reliability),
                    "safe_logit": float(safe_logit),
                    "inspect_probability": float(probability[1]),
                    "G_blind": float(terms[0]["normalized_total"]),
                    "G_inspect": float(terms[1]["normalized_total"]),
                    "inspect_information_gain": float(terms[1]["information_gain"]),
                    "identity_residual": max(
                        abs(
                            float(p["normalized_total"])
                            - float(p["risk"])
                            - float(p["ambiguity"])
                        )
                        for p in terms
                    ),
                }
            )
    imported = active_sensing_model()
    specifications[imported.specification_sha256] = imported.specification
    terms, probabilities = _policy_terms(imported)
    model = imported.model
    strategies = ("EFE_sampled", "Always_inspect", "Always_blind")
    trials: list[Row] = []
    metrics: list[Row] = []
    for seed in range(n_seeds):
        world_stream, action_stream = np.random.SeedSequence(10000 + seed).spawn(2)
        world_rng, action_rng = (
            np.random.default_rng(world_stream),
            np.random.default_rng(action_stream),
        )
        potential = sample_potential_outcomes(model, n_trials, world_rng)
        initial_states = potential.initial_states
        contexts = initial_states % 2
        potential_states = potential.next_states
        potential_outcomes = potential.observations
        choices = action_rng.choice(2, size=n_trials, p=probabilities)
        for strategy in strategies:
            local: list[Row] = []
            for trial, context in enumerate(contexts):
                action = (
                    int(choices[trial])
                    if strategy == "EFE_sampled"
                    else int(strategy == "Always_inspect")
                )
                outcome = int(potential_outcomes[trial, action])
                predicted_state = model.B[:, :, action] @ model.D
                posterior = bayesian_update(model.A, outcome, predicted_state)
                p1 = float(posterior[1] + posterior[3])
                truth_probability = p1 if context else 1 - p1
                row: Row = {
                    "seed": seed,
                    "trial": trial,
                    "strategy": strategy,
                    "context": int(context),
                    "initial_state": int(initial_states[trial]),
                    "next_state": int(potential_states[trial, action]),
                    "action": action,
                    "outcome": outcome,
                    "p_context1": p1,
                    "accuracy": float((p1 > 0.5) == context),
                    "brier": (p1 - context) ** 2,
                    "log_loss": float(-np.log(truth_probability)),
                    "mean_inspections": action,
                    "preference_logit": float(model.C[outcome]),
                    "normalized_G": float(terms[action]["normalized_total"]),
                    "posterior_entropy": float(-xlogy(p1, p1) - xlogy(1 - p1, 1 - p1)),
                }
                trials.append(row)
                local.append(row)
            metrics.append(
                {
                    "seed": seed,
                    "strategy": strategy,
                    **{
                        metric: float(np.mean([r[metric] for r in local]))
                        for metric in (
                            "accuracy",
                            "brier",
                            "log_loss",
                            "mean_inspections",
                            "preference_logit",
                            "normalized_G",
                            "posterior_entropy",
                        )
                    },
                }
            )
    estimates: list[Row] = []
    comparisons: list[Row] = []
    entropy = float(-xlogy(0.85, 0.85) - xlogy(0.15, 0.15))
    for strategy in strategies:
        inspect = (
            float(probabilities[1])
            if strategy == "EFE_sampled"
            else float(strategy == "Always_inspect")
        )
        exact = {
            "accuracy": 0.5 + 0.35 * inspect,
            "brier": 0.25 * (1 - inspect) + 0.85 * 0.15 * inspect,
            "log_loss": np.log(2) * (1 - inspect) + entropy * inspect,
            "mean_inspections": inspect,
            "preference_logit": 0.15 * (1 - inspect),
            "normalized_G": (1 - inspect) * float(terms[0]["normalized_total"])
            + inspect * float(terms[1]["normalized_total"]),
            "posterior_entropy": np.log(2) * (1 - inspect) + entropy * inspect,
        }
        for metric, expected in exact.items():
            values = np.array(
                [r[metric] for r in metrics if r["strategy"] == strategy], dtype=float
            )
            estimates.append(
                {
                    "strategy": strategy,
                    "metric": metric,
                    "exact_expectation": float(expected),
                    **paired_interval(values, resamples),
                }
            )
            if strategy != "EFE_sampled":
                treated = np.array(
                    [r[metric] for r in metrics if r["strategy"] == "EFE_sampled"],
                    dtype=float,
                )
                comparisons.append(
                    {
                        "treated": "EFE_sampled",
                        "control": strategy,
                        "metric": metric,
                        "n_pairs": n_seeds,
                        **paired_interval(treated - values, resamples),
                    }
                )
    if verify_upstream() != revision:
        raise ValidationError("GNN revision changed during the active-sensing study")
    return {
        "config": {
            "n_seeds": n_seeds,
            "n_trials": n_trials,
            "first_seed": 10000,
            "reliability": 0.85,
            "safe_logit": 0.15,
            "policy_precision": 4,
            "bootstrap_resamples": resamples,
            "upstream_revision": revision,
            "simulation_model_sha256": imported.specification_sha256,
            "status": "Exploratory synthetic action task; separate from H1-H3",
        },
        "specifications": specifications,
        "landscape": landscape,
        "trials": trials,
        "seed_metrics": metrics,
        "estimates": estimates,
        "comparisons": comparisons,
    }
