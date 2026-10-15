import numpy as np
import pytest
from scipy.special import softmax

from analysis.active_sensing import active_sensing_model, run_active_sensing
from core.active_inference import ActiveInferenceFramework
from core.probability import bayesian_update
from utils.exceptions import ValidationError


@pytest.mark.parametrize(
    "r,c", [(0.4, 0.1), (1.1, 0.1), (np.nan, 0.1), (0.8, -1), (0.8, np.inf)]
)
def test_active_sensing_rejects_invalid_model(r, c):
    with pytest.raises(ValidationError):
        active_sensing_model(r, c)


def test_imported_gnn_dynamics_and_exact_policy_boundary():
    r = 0.85
    model = active_sensing_model(r, 0.15).model
    np.testing.assert_allclose(model.B.sum(axis=0), 1)
    for current in range(4):
        for action in range(2):
            assert model.B[current % 2 + 2 * action, current, action] == 1
    prior = model.B[:, :, 1] @ model.D
    posterior = bayesian_update(model.A, 1, prior)
    assert posterior[2] == pytest.approx(r)
    framework = ActiveInferenceFramework(model, precision=4)
    _, blind = framework.calculate_expected_free_energy(model.D, np.array([0]))
    _, inspect = framework.calculate_expected_free_energy(model.D, np.array([1]))
    information = np.log(2) + r * np.log(r) + (1 - r) * np.log(1 - r)
    assert blind["information_gain"] == 0
    assert inspect["information_gain"] == pytest.approx(information)
    assert inspect["normalized_total"] - blind["normalized_total"] == pytest.approx(
        0.15 - information
    )
    _, choice = framework.select_optimal_policy([np.array([0]), np.array([1])], model.D)
    np.testing.assert_allclose(
        choice["policy_probabilities"],
        softmax(
            -4 * np.array([blind["normalized_total"], inspect["normalized_total"]])
        ),
    )
    assert choice["optimal_policy"] == "policy_1"
    changed = ActiveInferenceFramework(active_sensing_model(r, 0.8).model)
    action, _ = changed.select_optimal_policy([np.array([0]), np.array([1])])
    assert action.tolist() == [0]


@pytest.mark.parametrize(
    "seeds,trials,resamples", [(1, 20, 100), (3, 1, 100), (True, 20, 100), (3, 20, 99)]
)
def test_study_rejects_invalid_design(seeds, trials, resamples):
    with pytest.raises(ValidationError):
        run_active_sensing(seeds, trials, resamples)


def test_uninformative_and_perfect_gnn_limits():
    for reliability, expected in [(0.5, 0), (1, np.log(2))]:
        model = active_sensing_model(reliability, 0).model
        framework = ActiveInferenceFramework(model)
        _, parts = framework.calculate_expected_free_energy(model.D, np.array([1]))
        assert parts["information_gain"] == pytest.approx(expected)
    model = active_sensing_model(0.5, 0).model
    _, result = ActiveInferenceFramework(model).select_optimal_policy(
        [np.array([0]), np.array([1])]
    )
    assert result["policy_probabilities"] == pytest.approx([0.5, 0.5])


@pytest.mark.timeout(40)
def test_actual_sensing_study_reproduces_and_matches_analytic_expectations():
    from core.gnn import import_gnn

    a = run_active_sensing(4, 80, 100)
    b = run_active_sensing(4, 80, 100)
    assert a == b
    assert len(a["landscape"]) == 187
    assert len(a["trials"]) == 960
    assert len(a["comparisons"]) == 14
    assert max(row["identity_residual"] for row in a["landscape"]) < 1e-12
    assert a["config"]["simulation_model_sha256"] in a["specifications"]
    model = import_gnn(
        a["specifications"][a["config"]["simulation_model_sha256"]]
    ).model
    for row in a["trials"]:
        assert model.D[row["initial_state"]] > 0
        assert model.B[row["next_state"], row["initial_state"], row["action"]] == 1
        assert model.A[row["outcome"], row["next_state"]] > 0
        assert row["next_state"] % 2 == row["context"]
        if row["strategy"] == "Always_blind":
            assert row["p_context1"] == 0.5
            assert row["action"] == 0
        if row["strategy"] == "Always_inspect":
            assert row["p_context1"] == pytest.approx(
                0.85 if row["outcome"] == 2 else 0.15
            )
    for row in a["estimates"]:
        if row["metric"] in ("accuracy", "mean_inspections"):
            assert abs(row["mean"] - row["exact_expectation"]) < 0.10
