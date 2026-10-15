"""Exact predictive evaluation with distinct GNN world and agent specifications."""

from __future__ import annotations

from typing import TypedDict

import numpy as np
from numpy.typing import ArrayLike

from core.active_inference import ActiveInferenceFramework
from core.gnn import ImportedGNNModel
from core.probability import bayesian_update, probability_vector
from utils.exceptions import ValidationError
from .active_sensing import Row, active_sensing_model


class RobustnessStudy(TypedDict):
    config: dict[str, float | str]
    specifications: dict[str, str]
    metrics: list[Row]
    calibration: list[Row]


def exact_context_scores(
    world: ImportedGNNModel,
    agent: ImportedGNNModel,
    actions: ArrayLike,
) -> tuple[dict[str, float], list[Row]]:
    """Enumerate a four-state context×mode world; score the agent's context belief.

    Context is next-state parity. Both models must use the active-sensing state,
    action and observation conventions. Positive world events that the agent
    declares impossible fail explicitly rather than inventing a posterior.
    """
    w, a = world.model, agent.model
    if any((m.n_states, m.n_observations, m.n_actions) != (4, 3, 2) for m in (w, a)):
        raise ValidationError("Context scores require four-state active-sensing models")
    p = probability_vector(actions, 2, "Action probabilities")
    totals = {key: 0.0 for key in ("accuracy", "brier", "log_loss", "mean_inspections")}
    calibration: list[Row] = []
    for action in range(2):
        joint = w.A * (w.B[:, :, action] @ w.D)[None, :]
        for outcome in range(3):
            mass = float(joint[outcome].sum()) * float(p[action])
            if mass == 0:
                continue
            posterior = bayesian_update(a.A, outcome, a.B[:, :, action] @ a.D)
            forecast = float(posterior[1::2].sum())
            true_rate = float(joint[outcome, 1::2].sum() / joint[outcome].sum())
            accuracy = true_rate if forecast > 0.5 else 1 - true_rate
            brier = true_rate * (1 - forecast) ** 2 + (1 - true_rate) * forecast**2
            log_loss = 0.0
            for rate, probability in (
                (true_rate, forecast),
                (1 - true_rate, 1 - forecast),
            ):
                if rate > 0:
                    if probability == 0:
                        raise ValidationError(
                            "Positive world event has zero forecast probability"
                        )
                    log_loss -= rate * float(np.log(probability))
            for key, value in (
                ("accuracy", accuracy),
                ("brier", brier),
                ("log_loss", log_loss),
                ("mean_inspections", action),
            ):
                totals[key] += mass * value
            calibration.append(
                {
                    "action": action,
                    "outcome": outcome,
                    "mass": mass,
                    "forecast": forecast,
                    "true_rate": true_rate,
                }
            )
    return totals, calibration


def reliability_robustness() -> RobustnessStudy:
    """Freeze an agent at r=.85 and enumerate worlds from uninformative to perfect."""
    agent = active_sensing_model()
    _, selection = ActiveInferenceFramework(
        agent.model, precision=4
    ).select_optimal_policy([np.array([0]), np.array([1])], agent.model.D)
    probabilities = np.asarray(selection["policy_probabilities"], dtype=float)
    specifications = {agent.specification_sha256: agent.specification}
    metrics: list[Row] = []
    calibration: list[Row] = []
    for reliability in np.linspace(0.5, 1, 21):
        world = active_sensing_model(round(float(reliability), 12))
        specifications[world.specification_sha256] = world.specification
        for strategy, actions in (
            ("EFE_sampled", probabilities),
            ("Always_inspect", np.array([0.0, 1.0])),
            ("Always_blind", np.array([1.0, 0.0])),
        ):
            scores, cells = exact_context_scores(world, agent, actions)
            metrics.append(
                {
                    "world_reliability": float(reliability),
                    "strategy": strategy,
                    **scores,
                }
            )
            calibration.extend(
                {"world_reliability": float(reliability), "strategy": strategy, **cell}
                for cell in cells
            )
    return {
        "config": {
            "agent_reliability": 0.85,
            "safe_logit": 0.15,
            "policy_precision": 4.0,
            "agent_specification_sha256": agent.specification_sha256,
            "status": "Exact finite enumeration; fixed agent, varying world; no fitted policy or sampling intervals",
        },
        "specifications": specifications,
        "metrics": metrics,
        "calibration": calibration,
    }
