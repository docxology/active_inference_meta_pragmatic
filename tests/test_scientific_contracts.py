"""Analytical checks of probability support, free energy, and statistical units."""

import numpy as np
import pytest
from scipy.special import logsumexp
from scipy import stats

from core.active_inference import ActiveInferenceFramework
from core.generative_models import GenerativeModel, create_simple_generative_model
from core.probability import (
    probability_vector,
    model_matrices,
    observation_likelihood,
    bayesian_update,
    entropy,
)
from core.free_energy_principle import (
    calculate_variational_free_energy,
    FreeEnergyPrinciple,
)
from analysis.validation import ValidationFramework
from analysis.statistical_analysis import StatisticalAnalyzer
from analysis.data_generator import DataGenerator
from framework.meta_cognition import MetaCognitiveSystem
from framework.cognitive_security import CognitiveSecurityAnalyzer
from utils.exceptions import ValidationError


def model():
    return GenerativeModel(
        [[0.9, 0.2], [0.1, 0.8]], [[0.7, 0.1], [0.3, 0.9]], [1.0, -1.0], [0.6, 0.4]
    )


@pytest.mark.parametrize(
    "invalid",
    [[], [[0.5, 0.5]], [-0.1, 1.1], [0.4, 0.4], [np.nan, 1], [np.inf, 0], ["x", 1]],
)
def test_probability_contract(invalid):
    with pytest.raises(ValidationError):
        probability_vector(invalid)


@pytest.mark.parametrize(
    "name,invalid",
    [
        ("A", np.ones((2, 2))),
        ("A", np.ones(2)),
        ("A", np.zeros((0, 2))),
        ("A", [[np.nan, 0.2], [0.1, 0.8]]),
        ("B", np.ones((2, 2, 0))),
        ("B", np.ones((2, 3, 1))),
        ("B", np.ones(2)),
        ("B", [[0.8, 0.4], [0.3, 0.7]]),
        ("C", [np.inf, 0]),
        ("C", [[1, 2]]),
        ("C", [1, 2, 3]),
        ("D", [-0.2, 1.2]),
        ("D", [1, 1]),
    ],
)
def test_all_model_matrices_reject_invalid(name, invalid):
    m = model()
    data = {k: getattr(m, k) for k in "ABCD"}
    data[name] = invalid
    with pytest.raises(ValidationError):
        GenerativeModel(**data)
    with pytest.raises(ValidationError):
        ActiveInferenceFramework(data)


def test_asymmetric_column_stochastic_transition_and_copy():
    m = model()
    np.testing.assert_allclose(m.predict_state_transition([0.6, 0.4], 0), [0.46, 0.54])
    assert ValidationFramework().validate_generative_model(
        {k: getattr(m, k) for k in "ABCD"}
    )["valid"]
    original = np.array([[0.7, 0.1], [0.3, 0.9]])
    copied = GenerativeModel(m.A, original, m.C, m.D)
    original[:] = 0
    np.testing.assert_allclose(copied.predict_state_transition(0, 0), [0.7, 0.3])
    assert copied.B.shape == (2, 2, 1)


@pytest.mark.parametrize(
    "operation,arguments",
    [
        ("predict_observations", (-1,)),
        ("predict_observations", ([0.5],)),
        ("predict_state_transition", (0, -1)),
        ("predict_state_transition", (-1, 0)),
        ("predict_state_transition", (0, 0.5)),
        ("perform_inference", (-1,)),
        ("perform_inference", ([0, 0],)),
        ("perform_inference", ([0.5, 0.5, 0.0],)),
    ],
)
def test_public_inference_rejects_invalid(operation, arguments):
    with pytest.raises(ValidationError):
        getattr(model(), operation)(*arguments)


def test_soft_evidence_is_not_argmax_and_preserves_prior_if_uniform():
    m = model()
    expected = (m.A.T @ [0.8, 0.2]) * m.D
    expected /= expected.sum()
    np.testing.assert_allclose(m.perform_inference([0.8, 0.2]), expected)
    np.testing.assert_allclose(
        ActiveInferenceFramework(m).perception_as_inference([0.8, 0.2]), expected
    )
    np.testing.assert_allclose(m.perform_inference([0.5, 0.5]), m.D)
    assert not np.allclose(m.perform_inference([0.8, 0.2]), m.perform_inference(0))


def test_exact_zero_support_and_impossible_evidence():
    m = GenerativeModel(np.eye(2), np.eye(2), [0, 0], [1, 0])
    np.testing.assert_array_equal(m.perform_inference(0), [1, 0])
    with pytest.raises(ValidationError):
        m.perform_inference(1)
    with pytest.raises(ValidationError):
        calculate_variational_free_energy(m, 1, [1, 0])
    f, parts = calculate_variational_free_energy(m, 0, [0.5, 0.5])
    assert np.isinf(f) and np.isinf(parts["posterior_divergence"])
    assert entropy([1, 0]) == 0


def test_exact_vfe_bound_and_equality_at_posterior():
    m = model()
    posterior = m.perform_inference(0)
    f, parts = calculate_variational_free_energy(m, 0, posterior)
    assert f == pytest.approx(-np.log(m.A[0] @ m.D))
    assert parts["posterior_divergence"] == pytest.approx(0, abs=1e-15)
    arbitrary = np.array([0.2, 0.8])
    f, parts = calculate_variational_free_energy(m, 0, arbitrary)
    assert f == pytest.approx(
        parts["surprise"] + np.sum(arbitrary * np.log(arbitrary / posterior))
    )
    states = {k: np.ones(2) for k in ("internal", "external", "sensory")}
    exact = FreeEnergyPrinciple(states, generative_model=m).calculate_free_energy(
        0, posterior
    )
    assert exact[0] == pytest.approx(-np.log(m.A[0] @ m.D))
    assert (
        FreeEnergyPrinciple(states).calculate_free_energy([0.5, 0.5], [0.5, 0.5])[1][
            "evaluation_kind"
        ]
        == "illustrative_score"
    )


def test_deterministic_information_and_efe_identities():
    m = GenerativeModel(np.eye(2), np.eye(2), [1, -1], [0.5, 0.5])
    ai = ActiveInferenceFramework(m)
    _, parts = ai.calculate_expected_free_energy([0.5, 0.5], [0])
    assert parts["information_gain"] == pytest.approx(np.log(2))
    assert parts["ambiguity"] == 0
    assert parts["normalized_total"] == pytest.approx(
        parts["risk"] + parts["ambiguity"]
    )
    total, _ = ai.calculate_expected_free_energy([0.5, 0.5], [0, 0], aggregation="sum")
    assert total == pytest.approx(2 * parts["total"])
    shifted = GenerativeModel(m.A, m.B, m.C + 1000, m.D)
    _, shift = ActiveInferenceFramework(shifted).calculate_expected_free_energy(
        [0.5, 0.5], [0]
    )
    assert shift["normalized_total"] == pytest.approx(parts["normalized_total"])
    assert shifted.preference_distribution().sum() == pytest.approx(1)


@pytest.mark.parametrize(
    "beliefs,policy,aggregation",
    [
        ([0.5], [0], "mean"),
        ([0.5, 0.5], [[0]], "mean"),
        ([0.5, 0.5], [], "mean"),
        ([0.5, 0.5], [0.5], "mean"),
        ([0.5, 0.5], [-1], "mean"),
        ([0.5, 0.5], [0], "bad"),
    ],
)
def test_efe_input_contract(beliefs, policy, aggregation):
    with pytest.raises(ValidationError):
        ActiveInferenceFramework(model()).calculate_expected_free_energy(
            beliefs, policy, aggregation=aggregation
        )


@pytest.mark.parametrize("precision", [0, -1, np.nan, np.inf])
def test_precision_contract(precision):
    with pytest.raises(ValidationError):
        ActiveInferenceFramework(model(), precision)


def test_selection_uses_updated_beliefs_and_precision():
    m = create_simple_generative_model()
    policies = [[0], [1]]
    a = ActiveInferenceFramework(m, 1)
    b = ActiveInferenceFramework(m, 10)
    assert a.select_optimal_policy(policies, [0.9, 0.1])[0] == [0]
    assert a.select_optimal_policy(policies, [0.1, 0.9])[0] == [1]
    assert (
        b.select_optimal_policy(policies, [0.9, 0.1])[1]["policy_probabilities"][0]
        > a.select_optimal_policy(policies, [0.9, 0.1])[1]["policy_probabilities"][0]
    )
    with pytest.raises(ValidationError):
        a.select_optimal_policy([])


def test_validators_reject_false_identity_and_propagate_overall_failure():
    v = ValidationFramework()
    result = v.validate_theoretical_correctness(
        "incorrect",
        {"efe_components": {"epistemic": -1, "pragmatic": 2, "total": 4}},
        {},
    )
    assert not result["overall_correctness"]
    report = v.create_validation_report([result, {"valid": True}, {}])
    assert report["summary"]["passed"] == 1 and report["summary"]["failed"] == 2
    with pytest.raises(ValidationError):
        v.validate_probability_distribution(np.empty((0, 0)))


@pytest.mark.parametrize("values", [[1], [1, np.nan], [[1, 2], [3, 4]], []])
def test_stats_reject_non_samples(values):
    analyzer = StatisticalAnalyzer()
    with pytest.raises(ValidationError):
        analyzer.calculate_confidence_interval(values)


def test_holm_and_paired_effect_size_against_hand_calculation():
    analyzer = StatisticalAnalyzer()
    np.testing.assert_allclose(
        analyzer.holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06]
    )
    a = np.array([1.0, 3, 5, 4, 7])
    b = np.array([0.0, 2, 1, 3, 5])
    result = analyzer.perform_t_test(a, b, "paired")
    assert result["paired_d_z"] == pytest.approx((a - b).mean() / np.std(a - b, ddof=1))
    assert result["t_statistic"] == pytest.approx(stats.ttest_rel(a, b).statistic)
    assert analyzer.bootstrap_mean_interval(
        a, seed=9, n_resamples=100
    ) == analyzer.bootstrap_mean_interval(a, seed=9, n_resamples=100)


@pytest.mark.parametrize(
    "method,args",
    [
        ("holm_adjust", ([np.nan],)),
        ("holm_adjust", ([],)),
        ("bootstrap_mean_interval", ([1, 2], 1.1)),
        ("bootstrap_mean_interval", ([1, 2], 0.95, 10)),
        ("calculate_confidence_interval", ([1, 2], 1.1)),
        ("calculate_correlation", ([1, 1], [1, 2])),
    ],
)
def test_statistical_parameters(method, args):
    with pytest.raises(ValidationError):
        getattr(StatisticalAnalyzer(), method)(*args)


def test_generator_single_observation_and_arbitrary_actions():
    gen = DataGenerator(42)
    np.testing.assert_array_equal(
        gen.generate_observation_matrix(2, 1, 1), np.ones((1, 2))
    )
    for actions in (1, 2, 4):
        B = gen.generate_transition_matrix(3, actions)
        np.testing.assert_allclose(B.sum(axis=0), 1)
    with pytest.raises(ValidationError):
        gen.generate_observation_matrix(noise_level=2)


def test_capacity_and_security_validation():
    meta = MetaCognitiveSystem()
    resources = meta.adjust_attention_allocation(
        {"confidence_score": 0.9}, {"a": 1, "b": 3, "c": 0}
    )
    assert resources == {"a": 0.25, "b": 0.75, "c": 0}
    with pytest.raises(ValidationError):
        meta.assess_inference_confidence([0.5, 0.5], np.nan)
    with pytest.raises(ValidationError):
        meta.adjust_attention_allocation({"confidence_score": 0.1}, {"a": 0})
    security = CognitiveSecurityAnalyzer()
    with pytest.raises(ValidationError):
        security.detect_anomaly([-1, 2], [0.5, 0.5])
    with pytest.raises(ValidationError):
        security.detect_anomaly([0.5, 0.5], [0.5, 0.5], -1)
    m = model()
    params = {k: getattr(m, k) for k in "ABCD"}
    params["B"] = np.ones((3, 3)) / 3
    assert not security.validate_framework_integrity(params)["is_valid"]
    assert not security.validate_framework_integrity({k: np.array([]) for k in "ABCD"})[
        "is_valid"
    ]


def test_preference_normalization_and_overflow_contract():
    m = model()
    m.C = np.array([1000.0, -1000.0])
    assert m.calculate_preference_likelihood(0, normalized=True) == 1
    with pytest.raises(ValidationError):
        m.calculate_preference_likelihood(0)
    with pytest.raises(ValidationError):
        m.calculate_preference_likelihood(-1, normalized=True)


def test_strategy_adaptation_tracks_bounded_history():
    meta = MetaCognitiveSystem(adaptation_rate=0.25)
    first = meta.evaluate_strategy_effectiveness(
        "strategy",
        {k: 1 for k in ("accuracy", "efficiency", "adaptability", "robustness")},
    )
    second = meta.evaluate_strategy_effectiveness(
        "strategy",
        {k: 0 for k in ("accuracy", "efficiency", "adaptability", "robustness")},
    )
    assert first["effectiveness_score"] == pytest.approx(1)
    assert second["effectiveness_score"] == pytest.approx(0.75)
    with pytest.raises(ValidationError):
        meta.evaluate_strategy_effectiveness("strategy", {"accuracy": np.nan})


def test_large_preference_shift_and_roundoff_normalization():
    m = model()
    m.C = np.array([1e20, 1e20])
    np.testing.assert_allclose(m.preference_distribution(), [0.5, 0.5])
    neutral = GenerativeModel(m.A, m.B, [0, 0], m.D)
    _, large = ActiveInferenceFramework(m).calculate_expected_free_energy(m.D, [0])
    _, base = ActiveInferenceFramework(neutral).calculate_expected_free_energy(m.D, [0])
    assert large["normalized_total"] == pytest.approx(base["normalized_total"])
    normalized = GenerativeModel(m.A * (1 + 1e-7), m.B * (1 + 1e-7), m.C, m.D)
    np.testing.assert_allclose(normalized.A.sum(axis=0), 1, rtol=0, atol=1e-15)
    np.testing.assert_allclose(normalized.B.sum(axis=0), 1, rtol=0, atol=1e-15)


def test_policy_distribution_survives_large_constant_preference_shift():
    # One action preserves uncertain state beliefs, another sets a known state.
    # Neutral preferences should favor the informative action under exact EFE.
    B = np.zeros((2, 2, 2))
    B[:, :, 0] = np.eye(2)
    B[:, :, 1] = np.array([[1.0, 1.0], [0.0, 0.0]])
    m = GenerativeModel(np.eye(2), B, [1e20, 1e20], [0.5, 0.5])
    chosen, info = ActiveInferenceFramework(m).select_optimal_policy([[1], [0]])
    assert chosen == [0]
    assert info["policy_probabilities"][1] > info["policy_probabilities"][0]
