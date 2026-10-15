"""Reproducible synthetic tests of concrete quadrant-inspired mechanisms.

These operationalizations do not constitute evidence for four natural cognitive
kinds. Seeds, rather than trials within a seed, are the inferential units.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import product

import numpy as np
from scipy.special import expit
from scipy import stats

from core.active_inference import ActiveInferenceFramework
from core.free_energy_principle import calculate_variational_free_energy
from core.probability import bayesian_update
from core.gnn import ImportedGNNModel, sensor_model, specified_model, verify_upstream
from utils.exceptions import ValidationError
from .statistical_analysis import StatisticalAnalyzer


@dataclass(frozen=True)
class ExperimentConfig:
    """Fixed design; changing it requires a new recorded experiment."""

    n_seeds: int = 30
    n_trials: int = 400
    n_training: int = 200
    first_seed: int = 0
    sensor_reliabilities: tuple[float, ...] = (0.55, 0.65, 0.85, 0.8, 0.8)
    assumed_reliability: float = 0.8
    confidence_threshold: float = 0.9
    bootstrap_resamples: int = 5000

    def validate(self) -> None:
        """Require sufficient independent units, finite probabilities, and budget."""
        for name in (
            "n_seeds",
            "n_trials",
            "n_training",
            "first_seed",
            "bootstrap_resamples",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or value < (0 if name == "first_seed" else 2):
                raise ValidationError(f"{name} must be a valid integer")
        if self.bootstrap_resamples < 100:
            raise ValidationError("At least 100 bootstrap resamples required")
        r = np.asarray(self.sensor_reliabilities)
        if r.shape != (5,) or not np.all(np.isfinite(r)) or np.any((r <= 0) | (r >= 1)):
            raise ValidationError("Exactly five sensor reliabilities in (0,1) required")
        if (
            not np.isfinite(self.assumed_reliability)
            or not 0 < self.assumed_reliability < 1
        ):
            raise ValidationError("Assumed reliability must be in (0,1)")
        if (
            not np.isfinite(self.confidence_threshold)
            or not 0.5 <= self.confidence_threshold <= 1
        ):
            raise ValidationError("Confidence threshold must be in [0.5,1]")


def binary_sensor_posterior(
    observations: np.ndarray, reliabilities: np.ndarray
) -> np.ndarray:
    """P(s=1) for conditionally independent binary sensors and a uniform prior.

    The log-odds calculation equals sequential categorical Bayes updates with
    A=[[r,1-r],[1-r,r]]. This batching is checked against the core implementation.
    """
    observations = np.asarray(observations)
    reliabilities = np.asarray(reliabilities, dtype=float)
    if observations.ndim != 2 or observations.shape[1] != reliabilities.size:
        raise ValidationError(
            "Observations must be (trials, sensors) matching reliabilities"
        )
    if np.any((observations != 0) & (observations != 1)):
        raise ValidationError("Observations must be binary categories")
    if (
        reliabilities.ndim != 1
        or not reliabilities.size
        or np.any(~np.isfinite(reliabilities))
        or np.any((reliabilities <= 0) | (reliabilities >= 1))
    ):
        raise ValidationError("Reliabilities must be a nonempty vector in (0,1)")
    return expit((2 * observations - 1) @ np.log(reliabilities / (1 - reliabilities)))


def _metrics(probabilities: np.ndarray, states: np.ndarray, cost: np.ndarray) -> dict:
    """Accuracy, Brier loss, log loss, and actual sensing cost per seed."""
    prediction = probabilities > 0.5
    p = np.clip(probabilities, np.finfo(float).eps, 1 - np.finfo(float).eps)
    return {
        "accuracy": float(np.mean(prediction == states)),
        "brier": float(np.mean((probabilities - states) ** 2)),
        "log_loss": float(-np.mean(states * np.log(p) + (1 - states) * np.log1p(-p))),
        "mean_observations": float(np.mean(cost)),
    }


def gnn_sensor_posterior(
    observations: np.ndarray, models: list[ImportedGNNModel]
) -> np.ndarray:
    """Execute imported static GNN likelihoods, preserving exact Bayesian support."""
    observations = np.asarray(observations)
    if not models or observations.ndim != 2 or observations.shape[1] != len(models):
        raise ValidationError("Observation columns must match the imported GNN sensors")
    if np.any((observations != 0) & (observations != 1)):
        raise ValidationError("Observations must be binary categories")
    posterior = np.tile(models[0].model.D, (len(observations), 1))
    for index, imported in enumerate(models):
        model = imported.model
        if (
            model.A.shape != (2, 2)
            or model.n_actions != 1
            or not np.array_equal(model.B[:, :, 0], np.eye(2))
        ):
            raise ValidationError(
                "Sensor profile requires binary outcomes and static identity dynamics"
            )
        if not np.array_equal(model.D, models[0].model.D):
            raise ValidationError("All sensors must declare the same initial prior")
        joint = posterior * model.A[observations[:, index].astype(int)]
        evidence = joint.sum(axis=1, keepdims=True)
        if np.any(evidence == 0):
            raise ValidationError(
                "Impossible observations under the imported GNN model"
            )
        posterior = joint / evidence
    return posterior[:, 1]


def paired_sign_flip_test(
    differences: np.ndarray, seed: int = 2718, n_resamples: int = 10000
) -> float:
    """Two-sided Monte Carlo paired sign-flip test with a +1 correction."""
    differences = StatisticalAnalyzer._sample(differences)
    if not isinstance(n_resamples, int) or n_resamples < 100:
        raise ValidationError("At least 100 sign-flip resamples required")
    observed = abs(float(differences.mean()))
    rng = np.random.default_rng(seed)
    exceedances = 0
    for start in range(0, n_resamples, 256):
        size = min(256, n_resamples - start)
        signs = rng.choice([-1, 1], size=(size, differences.size))
        exceedances += int(
            np.sum(np.abs((signs * differences).mean(axis=1)) >= observed - 1e-14)
        )
    return (exceedances + 1) / (n_resamples + 1)


def run_quadrant_experiment(config: ExperimentConfig = ExperimentConfig()) -> dict:
    """Run matched held-out comparisons, retaining seed and trial-level evidence.

    Q1 assumes homogeneous reliability for three sensors. Q2 knows each sensor's
    reliability. Q3 uses Q2 beliefs to acquire up to two extra observations when
    confidence is low. Q4 estimates the three reliabilities from separate labeled
    training trials with a Beta(1,1) prior, then freezes them for held-out testing.
    """
    config.validate()
    rows, trials, learned = [], [], []
    reliability = np.asarray(config.sensor_reliabilities)
    verify_upstream()
    oracle_models = [sensor_model(float(r)) for r in reliability]
    fixed_models = [sensor_model(config.assumed_reliability)] * 3
    misleading_models = [sensor_model(r) for r in (0.95, 0.85, 0.55)]
    specifications = {
        model.specification_sha256: model.specification
        for model in [*oracle_models, *fixed_models, *misleading_models]
    }
    strategies = (
        "Q1_fixed",
        "Q2_metadata",
        "Q3_adaptive",
        "Q4_learned",
        "Q2_misleading",
        "Fixed_four",
        "Fixed_five",
    )
    for seed in range(config.first_seed, config.first_seed + config.n_seeds):
        train_stream, test_stream = np.random.SeedSequence(seed).spawn(2)
        train_rng, test_rng = (
            np.random.default_rng(train_stream),
            np.random.default_rng(test_stream),
        )
        # Training labels are available only here; no held-out states enter fitting.
        correct_training = train_rng.random((config.n_training, 3)) < reliability[:3]
        fitted = (correct_training.sum(axis=0) + 1) / (config.n_training + 2)
        learned.append({"seed": seed, "reliabilities": fitted.tolist()})
        fitted_models = [sensor_model(float(r)) for r in fitted]
        specifications.update(
            {m.specification_sha256: m.specification for m in fitted_models}
        )
        states = test_rng.integers(0, 2, config.n_trials)
        correct_test = test_rng.random((config.n_trials, 5)) < reliability
        observations = np.where(correct_test, states[:, None], 1 - states[:, None])
        first_three = observations[:, :3]
        fixed = gnn_sensor_posterior(first_three, fixed_models)
        metadata = gnn_sensor_posterior(first_three, oracle_models[:3])
        fitted_posterior = gnn_sensor_posterior(first_three, fitted_models)
        adaptive = metadata.copy()
        cost = np.full(config.n_trials, 3)
        for n_sensors in (4, 5):
            acquire = np.maximum(adaptive, 1 - adaptive) < config.confidence_threshold
            expanded = gnn_sensor_posterior(
                observations[:, :n_sensors], oracle_models[:n_sensors]
            )
            adaptive[acquire] = expanded[acquire]
            cost[acquire] += 1
        misleading = gnn_sensor_posterior(first_three, misleading_models)
        four = gnn_sensor_posterior(observations[:, :4], oracle_models[:4])
        five = gnn_sensor_posterior(observations, oracle_models)
        probabilities = (
            fixed,
            metadata,
            adaptive,
            fitted_posterior,
            misleading,
            four,
            five,
        )
        costs = (
            np.full(config.n_trials, 3),
            np.full(config.n_trials, 3),
            cost,
            np.full(config.n_trials, 3),
            np.full(config.n_trials, 3),
            np.full(config.n_trials, 4),
            np.full(config.n_trials, 5),
        )
        for strategy, p, sensing in zip(strategies, probabilities, costs):
            rows.append(
                {"seed": seed, "strategy": strategy, **_metrics(p, states, sensing)}
            )
        for i in range(config.n_trials):
            trials.append(
                {
                    "seed": seed,
                    "trial": i,
                    "state": int(states[i]),
                    **{f"sensor_{j}": int(observations[i, j]) for j in range(5)},
                    **{
                        f"{strategy}_p1": float(p[i])
                        for strategy, p in zip(strategies, probabilities)
                    },
                    "Q3_observations": int(cost[i]),
                }
            )
    analyzer = StatisticalAnalyzer()
    summary = {}
    for strategy in strategies:
        subset = [row for row in rows if row["strategy"] == strategy]
        summary[strategy] = {
            metric: analyzer.bootstrap_mean_interval(
                [r[metric] for r in subset], n_resamples=config.bootstrap_resamples
            )
            for metric in ("accuracy", "brier", "log_loss", "mean_observations")
        }
    comparisons = {}
    for name, treated, control in (
        ("H1", "Q2_metadata", "Q1_fixed"),
        ("H2", "Q3_adaptive", "Q2_metadata"),
        ("H3", "Q4_learned", "Q1_fixed"),
    ):
        a = np.array([r["accuracy"] for r in rows if r["strategy"] == treated])
        b = np.array([r["accuracy"] for r in rows if r["strategy"] == control])
        delta = a - b
        test = analyzer.perform_t_test(a, b, test_type="paired")
        comparisons[name] = {
            "treated": treated,
            "control": control,
            "accuracy_difference": analyzer.bootstrap_mean_interval(
                delta, n_resamples=config.bootstrap_resamples
            ),
            "paired_t_test": test,
            "p_sign_flip": paired_sign_flip_test(delta),
            "independent_unit": "seed",
            "n_pairs": config.n_seeds,
        }
    corrected = analyzer.holm_adjust([r["p_sign_flip"] for r in comparisons.values()])
    for row, p in zip(comparisons.values(), corrected):
        row["p_sign_flip_holm"] = p
        row["reject_at_0_05"] = p < 0.05
    return {
        "config": asdict(config),
        "data_kind": "synthetic",
        "replicates": rows,
        "trials": trials,
        "learned_reliabilities": learned,
        "summary": summary,
        "comparisons": comparisons,
        "gnn": {
            "upstream_revision": verify_upstream(),
            "specifications": specifications,
        },
        "limitations": [
            "Known reliability is privileged metadata, not a free benefit.",
            "Q3 consumes more observations; accuracy and sensing cost must be considered jointly.",
            "Q4 requires external labeled training; it does not establish autonomous framework optimization.",
            "Results concern this binary sensor task, not biological cognition or security efficacy.",
        ],
    }


def mathematical_checks(n_models: int = 50, seed: int = 1729) -> dict:
    """Numerical identities checked against independent algebraic expressions."""
    if not isinstance(n_models, int) or n_models < 1:
        raise ValidationError("n_models must be positive")
    rng = np.random.default_rng(seed)
    efe_error, vfe_error = [], []
    for _ in range(n_models):
        A = rng.dirichlet(np.ones(3), size=2).T
        B = np.stack([rng.dirichlet(np.ones(2), size=2).T for _ in range(2)], axis=2)
        model = specified_model(
            A,
            B,
            rng.normal(size=3),
            rng.dirichlet(np.ones(2)),
            "Random categorical identity check",
        ).model
        framework = ActiveInferenceFramework(model)
        beliefs = rng.dirichlet(np.ones(2))
        for policy in product(range(2), repeat=2):
            _, parts = framework.calculate_expected_free_energy(beliefs, policy)
            efe_error.append(
                abs(parts["normalized_total"] - (parts["risk"] + parts["ambiguity"]))
            )
        posterior = bayesian_update(A, 0, model.D)
        q = rng.dirichlet(np.ones(2))
        free_energy, parts = calculate_variational_free_energy(model, 0, q)
        expected_kl = float(np.sum(q * np.log(q / posterior)))
        vfe_error.append(abs(free_energy - (parts["surprise"] + expected_kl)))
    return {
        "seed": seed,
        "n_models": n_models,
        "n_policy_checks": len(efe_error),
        "max_efe_identity_error": max(efe_error),
        "max_vfe_identity_error": max(vfe_error),
        "passed": max(efe_error + vfe_error) < 1e-12,
    }


def reliability_sensitivity() -> list[dict]:
    """Exact policy terms over a prespecified observation-reliability grid."""
    rows = []
    for r in np.linspace(0.5, 1.0, 26):
        model = specified_model(
            [[r, 1 - r], [1 - r, r]], np.eye(2), [1.0, -1.0], [0.5, 0.5]
        ).model
        _, parts = ActiveInferenceFramework(model).calculate_expected_free_energy(
            [0.5, 0.5], [0]
        )
        rows.append({"reliability": float(r), **parts})
    return rows
