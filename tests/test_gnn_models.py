from pathlib import Path

import numpy as np
import pytest

from analysis.experiments import (
    ExperimentConfig,
    gnn_sensor_posterior,
    run_quadrant_experiment,
)
from core.active_inference import ActiveInferenceFramework
from core.gnn import (
    MODEL_DIRECTORY,
    import_gnn,
    load_gnn_model,
    sensor_model,
    specified_model,
    verify_upstream,
)
from utils.exceptions import ValidationError
from core.gnn_serialization import serialize_categorical


def test_section_serialization_preserves_nonparameter_assignments():
    template = (
        (MODEL_DIRECTORY / "binary_sensor.md")
        .read_text()
        .replace("## Equations", "## Equations\nA=An authored mathematical description")
    )
    content = serialize_categorical(
        template, np.eye(2), np.eye(2), [0, 0], [0.5, 0.5], "Preserved annotation"
    )
    assert "A=An authored mathematical description" in content
    assert "A=LikelihoodMatrix" in content
    np.testing.assert_array_equal(import_gnn(content).model.A, np.eye(2))


@pytest.mark.parametrize("template", ["", "## ModelName\nOne\n## ModelName\nTwo\n"])
def test_section_serialization_rejects_incomplete_or_ambiguous_template(template):
    with pytest.raises(ValidationError, match="exactly one"):
        serialize_categorical(
            template, np.eye(2), np.eye(2), [0, 0], [0.5, 0.5], "Example"
        )


def test_reference_import_executes_declared_bayes():
    imported = load_gnn_model()
    actual = imported.model.perform_inference(np.array([1.0, 0.0]))
    np.testing.assert_allclose(actual, [0.8, 0.2], atol=1e-14)


def test_reliability_revision_changes_executed_posterior():
    observations = np.array([[1, 0], [0, 1]])
    actual = gnn_sensor_posterior(observations, [sensor_model(0.9), sensor_model(0.6)])
    np.testing.assert_allclose(actual, [6 / 7, 1 / 7], atol=1e-14)


def test_asymmetric_gnn_transition_uses_destination_axis():
    imported = specified_model(
        [[0.9, 0.2], [0.1, 0.8]], [[0.9, 0.4], [0.1, 0.6]], [1, -1], [0.7, 0.3]
    )
    np.testing.assert_allclose(
        imported.model.predict_state_transition([0.7, 0.3], 0), [0.75, 0.25]
    )


def test_declared_preferences_control_policy_choice():
    imported = load_gnn_model(MODEL_DIRECTORY / "control_agent.md")
    chosen, _ = ActiveInferenceFramework(imported.model).select_optimal_policy(
        [[0], [1]], posterior_beliefs=[0.9, 0.1]
    )
    np.testing.assert_array_equal(chosen, [0])


@pytest.mark.parametrize(
    "old,new",
    [
        ("A[2,2,type=float]", "A[3,2,type=float]"),
        ("D=[0.5,0.5]", "D=[0.5,0.0]"),
        ("A=[[0.8,0.2],[0.2,0.8]]", "A=[[0.8,-0.2],[0.2,1.2]]"),
        ("num_hidden_states: 2", "num_hidden_states: 4"),
        ("s>A", "s>o"),
        ("GNN v1", "GNN v3 multiagent"),
        ("ActInfPOMDP", "ContinuousGaussian"),
        ("Static", "Dynamic\nContinuousTime=t"),
        ("s[2,type=float]", "s[3,type=float]"),
        ("u[1,type=int]", "u[1,type=int]\nextra[2,type=float]"),
        ("## Signature", "## Footer\nDuplicate\n## Signature"),
        ("D=[0.5,0.5]", "D=[0.5,0.5]\nD=[1.0,0.0]"),
        ("A=[[0.8,0.2],[0.2,0.8]]", "A=not_a_matrix"),
    ],
)
def test_invalid_gnn_is_rejected(old, new):
    content = (MODEL_DIRECTORY / "binary_sensor.md").read_text().replace(old, new)
    with pytest.raises((ValidationError, ValueError)):
        import_gnn(content)


def test_missing_checkout_fails_closed(tmp_path: Path):
    with pytest.raises(ValidationError):
        verify_upstream(tmp_path)


def test_gnn_zero_support_is_preserved():
    imported = specified_model(np.eye(2), np.eye(2), [0, 0], [1, 0])
    actual = gnn_sensor_posterior(np.array([[0]]), [imported])
    np.testing.assert_array_equal(actual, [0])


def test_impossible_gnn_evidence_is_rejected():
    imported = specified_model(np.eye(2), np.eye(2), [0, 0], [1, 0])
    with pytest.raises(ValidationError, match="Impossible"):
        gnn_sensor_posterior(np.array([[1]]), [imported])


@pytest.mark.parametrize(
    "observations", [np.array([1]), np.array([[2]]), np.array([[0, 1]])]
)
def test_invalid_sensor_observations_are_rejected(observations):
    with pytest.raises(ValidationError):
        gnn_sensor_posterior(observations, [sensor_model(0.8)])


def test_fixed_budget_costs_are_real_and_adaptive_cost_is_retained():
    result = run_quadrant_experiment(
        ExperimentConfig(n_seeds=3, n_trials=20, n_training=20, bootstrap_resamples=100)
    )
    costs = {
        row["strategy"]: row["mean_observations"]
        for row in result["replicates"]
        if row["seed"] == 0
    }
    assert costs["Fixed_four"] == 4 and costs["Fixed_five"] == 5
    assert costs["Q2_metadata"] == 3
    assert costs["Q3_adaptive"] == np.mean(
        [row["Q3_observations"] for row in result["trials"] if row["seed"] == 0]
    )


def test_uninformative_metadata_has_no_effect():
    observations = np.array([[0, 1, 0], [1, 1, 0]])
    fixed = gnn_sensor_posterior(observations, [sensor_model(0.8)] * 3)
    metadata = gnn_sensor_posterior(
        observations, [sensor_model(r) for r in [0.8, 0.8, 0.8]]
    )
    np.testing.assert_array_equal(metadata, fixed)


def test_dynamic_agent_is_not_admitted_as_a_static_sensor():
    agent = load_gnn_model(MODEL_DIRECTORY / "control_agent.md")
    with pytest.raises(ValidationError):
        gnn_sensor_posterior(np.array([[0]]), [agent])


def test_different_sensor_priors_are_rejected():
    different_prior = specified_model(
        [[0.8, 0.2], [0.2, 0.8]], np.eye(2), [0, 0], [0.9, 0.1]
    )
    with pytest.raises(ValidationError):
        gnn_sensor_posterior(np.array([[0, 1]]), [sensor_model(0.8), different_prior])


@pytest.mark.parametrize("name", ["", "\nInjected", "\rInjected"])
def test_invalid_materialized_model_names_are_rejected(name):
    with pytest.raises(ValidationError):
        specified_model(np.eye(2), np.eye(2), [0, 0], [0.5, 0.5], name)


def test_wrong_repository_does_not_satisfy_the_upstream_pin():
    project = Path(__file__).resolve().parents[1]
    with pytest.raises(ValidationError):
        verify_upstream(project)


def test_materialization_preserves_ontology_annotations():
    from core.gnn import sensor_model

    source = sensor_model(0.73).specification
    ontology = source.split("## ActInfOntologyAnnotation\n", 1)[1].split(
        "## ModelParameters", 1
    )[0]
    assert ontology.strip().splitlines() == [
        "A=LikelihoodMatrix",
        "B=TransitionMatrix",
        "C=PreferenceVector",
        "D=PriorBelief",
    ]
