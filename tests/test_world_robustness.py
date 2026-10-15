import numpy as np
import pytest

from analysis.active_sensing import active_sensing_model
from analysis.model_robustness import exact_context_scores, reliability_robustness
from core.gnn import load_gnn_model, specified_model
from core.simulation import sample_potential_outcomes
from utils.exceptions import ValidationError


@pytest.mark.parametrize("trials", [0, -1, True, 1.5])
def test_sampling_rejects_invalid_trial_count(trials):
    with pytest.raises(ValidationError, match="positive integer"):
        sample_potential_outcomes(
            load_gnn_model().model, trials, np.random.default_rng(1)
        )


def test_world_sampling_executes_asymmetric_transitions_and_likelihoods():
    model = specified_model(
        [[0.9, 0.2], [0.1, 0.8]], [[0.7, 0.4], [0.3, 0.6]], [0, 0], [1, 0]
    ).model
    sample = sample_potential_outcomes(model, 20000, np.random.default_rng(42))
    assert np.all(sample.initial_states == 0)
    assert np.mean(sample.next_states[:, 0] == 0) == pytest.approx(0.7, abs=0.01)
    assert np.mean(sample.observations[:, 0] == 0) == pytest.approx(0.69, abs=0.01)
    repeat = sample_potential_outcomes(model, 20000, np.random.default_rng(42))
    np.testing.assert_array_equal(sample.observations, repeat.observations)


def test_paired_sampling_preserves_original_random_stream():
    model = active_sensing_model().model
    rng = np.random.default_rng(103)
    initial = rng.choice(4, 40, p=model.D)
    transitions, observations = rng.random(40), rng.random(40)
    actual = sample_potential_outcomes(model, 40, np.random.default_rng(103))
    np.testing.assert_array_equal(actual.initial_states, initial)
    for action in range(2):
        expected_state = (
            transitions[:, None] >= np.cumsum(model.B[:, initial, action].T, axis=1)
        ).sum(axis=1)
        expected_obs = (
            observations[:, None] >= np.cumsum(model.A[:, expected_state].T, axis=1)
        ).sum(axis=1)
        np.testing.assert_array_equal(actual.next_states[:, action], expected_state)
        np.testing.assert_array_equal(actual.observations[:, action], expected_obs)


@pytest.mark.parametrize("r", [0.5, 0.6, 0.85, 1.0])
def test_exact_world_scores_match_independent_closed_forms(r):
    for inspect in (0.0, 0.37, 1.0):
        scores, cells = exact_context_scores(
            active_sensing_model(r),
            active_sensing_model(),
            np.array([1 - inspect, inspect]),
        )
        assert scores["accuracy"] == pytest.approx((1 - inspect) * 0.5 + inspect * r)
        assert scores["brier"] == pytest.approx(
            (1 - inspect) * 0.25 + inspect * (r * 0.15**2 + (1 - r) * 0.85**2)
        )
        assert scores["log_loss"] == pytest.approx(
            (1 - inspect) * np.log(2)
            - inspect * (r * np.log(0.85) + (1 - r) * np.log(0.15))
        )
        assert sum(cell["mass"] for cell in cells) == pytest.approx(1)
        assert scores["mean_inspections"] == pytest.approx(inspect)


@pytest.mark.parametrize("actions", [[1], [0, 0], [-1, 2], [np.nan, 1], [[0, 1]]])
def test_invalid_action_probabilities_fail(actions):
    with pytest.raises(ValidationError, match="Action probabilities"):
        exact_context_scores(
            active_sensing_model(), active_sensing_model(), np.array(actions)
        )


def test_dimension_mismatch_fails():
    with pytest.raises(ValidationError, match="four-state"):
        exact_context_scores(load_gnn_model(), active_sensing_model(), np.array([0, 1]))


def test_zero_forecast_on_positive_world_event_is_not_clipped():
    with pytest.raises(ValidationError, match="zero forecast"):
        exact_context_scores(
            active_sensing_model(0.5), active_sensing_model(1), np.array([0, 1])
        )


def test_world_observation_impossible_under_agent_fails():
    base = active_sensing_model().model
    likelihood = base.A.copy()
    likelihood[:, 2:] = [[0, 0], [1, 1], [0, 0]]
    wrong = specified_model(likelihood, base.B, base.C, base.D)
    with pytest.raises(ValidationError, match="Observation is impossible"):
        exact_context_scores(active_sensing_model(), wrong, np.array([0, 1]))


def test_exact_robustness_keeps_agent_fixed_and_retains_executed_specs():
    study = reliability_robustness()
    assert len(study["metrics"]) == 63
    assert len(study["specifications"]) == 21
    assert study["config"]["agent_specification_sha256"] in study["specifications"]
    rows = [row for row in study["metrics"] if row["strategy"] == "EFE_sampled"]
    assert len({row["mean_inspections"] for row in rows}) == 1
    assert rows[0]["accuracy"] == pytest.approx(0.5)
    assert rows[-1]["accuracy"] > 0.8
    cells = [
        row
        for row in study["calibration"]
        if row["strategy"] == "Always_inspect"
        and np.isclose(row["world_reliability"], 0.85)
    ]
    assert all(row["forecast"] == pytest.approx(row["true_rate"]) for row in cells)
