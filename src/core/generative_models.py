"""Generative Models Implementation.

This module implements generative model concepts central to Active Inference.
Generative models encode probabilistic relationships between hidden states,
observations, actions, and preferences through matrices A, B, C, and D.

Key Components:
- A matrix: Observation likelihoods P(o|s) - how hidden states generate observations
- B matrix: Transition probabilities P(s'|s,a) - how actions change states
- C matrix: Preference priors - desired outcomes and avoidance
- D matrix: Prior beliefs P(s) - initial state distribution

The modeler specifies these matrices to define the agent's understanding of its world.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray
from .probability import (
    model_matrices,
    probability_vector,
    observation_likelihood,
    bayesian_update,
)
from scipy.special import softmax
from utils.exceptions import ValidationError
from utils.logging import get_logger

logger = get_logger(__name__)


class GenerativeModel:
    """Implementation of Active Inference generative models.

    A generative model consists of four matrices (A, B, C, D) that encode
    the probabilistic relationships defining an agent's understanding of its world.
    """

    def __init__(self, A: NDArray, B: NDArray, C: NDArray, D: NDArray) -> None:
        """Initialize generative model with A, B, C, D matrices.

        Args:
            A: Observation likelihood matrix P(o|s) [n_observations × n_states]
            B: Transition matrix P(s'|s,a) [n_states × n_states × n_actions]
            C: Preference matrix (log priors over observations) [n_observations]
            D: Prior beliefs P(s) [n_states]

        Raises:
            ValidationError: If matrices have incompatible dimensions
        """
        self.A, self.B, self.C, self.D = model_matrices(A, B, C, D)

        self._validate_matrices()
        self.n_states = self.D.size
        self.n_observations = self.A.shape[0]
        self.n_actions = self.B.shape[2]

        logger.info(
            f"Initialized generative model: {self.n_states} states, "
            f"{self.n_observations} observations, {self.n_actions} actions"
        )

    def _validate_matrices(self) -> None:
        """Validate all probability, shape, finiteness, and support contracts."""
        self.A, self.B, self.C, self.D = model_matrices(self.A, self.B, self.C, self.D)

    def predict_observations(self, state: Union[int, NDArray]) -> NDArray:
        """Predict P(o) from a state index or normalized belief vector."""
        if isinstance(state, (int, np.integer)) and not isinstance(state, bool):
            if not 0 <= state < self.n_states:
                raise ValidationError("State index out of range")
            return self.A[:, int(state)].copy()
        return self.A @ probability_vector(state, self.n_states, "state beliefs")

    def predict_state_transition(
        self, current_state: Union[int, NDArray], action: int
    ) -> NDArray:
        """Predict next-state beliefs using B[next_state, current_state, action]."""
        if (
            not isinstance(action, (int, np.integer))
            or isinstance(action, bool)
            or not 0 <= action < self.n_actions
        ):
            raise ValidationError("Action must be an integer index in range")
        if isinstance(current_state, (int, np.integer)) and not isinstance(
            current_state, bool
        ):
            if not 0 <= current_state < self.n_states:
                raise ValidationError("State index out of range")
            return self.B[:, int(current_state), int(action)].copy()
        return self.B[:, :, int(action)] @ probability_vector(
            current_state, self.n_states, "state beliefs"
        )

    def calculate_preference_likelihood(
        self, observation: Union[int, NDArray], normalized: bool = False
    ) -> float:
        """Return preference strength, or normalized preference probability.

        The unnormalized exp(C) path rejects overflow. Use normalized=True
        or preference_distribution() for shift-invariant probabilities.
        """
        try:
            with np.errstate(over="raise"):
                preference = (
                    self.preference_distribution() if normalized else np.exp(self.C)
                )
            if isinstance(observation, (int, np.integer)) and not isinstance(
                observation, bool
            ):
                if not 0 <= observation < self.n_observations:
                    raise ValidationError("Observation index out of range")
                return float(preference[int(observation)])
            evidence = probability_vector(
                observation, self.n_observations, "observation evidence"
            )
            return float(preference @ evidence)
        except (FloatingPointError, ValueError, TypeError) as exc:
            raise ValidationError(
                "Unnormalized preference overflow; use normalized=True"
            ) from exc

    def perform_inference(
        self, observation: NDArray, prior_beliefs: Optional[NDArray] = None
    ) -> NDArray:
        """Update beliefs from a category or normalized virtual evidence vector.

        Soft evidence uses L(s) = A.T @ observation. Impossible observations
        raise ValidationError rather than inventing support with clipping.
        """
        return bayesian_update(
            self.A, observation, self.D if prior_beliefs is None else prior_beliefs
        )

    def preference_distribution(self) -> NDArray:
        """Return normalized outcome preferences using stable log-softmax."""
        return softmax(self.C)

    def demonstrate_modeler_specifications(self) -> Dict[str, Union[str, Dict]]:
        """Demonstrate how the modeler specifies different aspects of the agent.

        Returns:
            Dictionary showing modeler specification examples
        """
        specifications = {
            "epistemic_specification": {
                "generative_model_design": """
                The modeler specifies the agent's epistemic framework through matrices A and D.
                A defines how states generate observations (what the agent can know).
                D defines prior beliefs (what the agent assumes initially).
                """,
                "matrix_A_role": "Defines observation likelihoods - what is knowable",
                "matrix_D_role": "Defines prior knowledge - initial assumptions",
                "modeler_power": "Complete control over epistemic boundaries and assumptions",
            },
            "pragmatic_specification": {
                "description": """
                The modeler specifies pragmatic considerations through matrix C.
                C defines preference priors (what outcomes are desired or avoided).
                This enables specification of particular pragmatic frameworks.
                """,
                "matrix_C_role": "Defines value/goal structure - what matters to the agent",
                "pragmatic_framework": "Modeler defines the pragmatic landscape",
                "meta_pragmatic": "Modeler specifies pragmatic considerations for the modeled entity",  # noqa: E501
            },
            "dynamic_specification": {
                "description": """
                The modeler specifies system dynamics through matrix B.
                B defines how actions influence state transitions.
                This controls the agent's ability to influence its world.
                """,
                "matrix_B_role": "Defines action consequences - what the agent can control",
                "intervention_power": "Modeler specifies causal relationships",
                "agency_framework": "Modeler defines the boundaries of agency",
            },
            "meta_level_implications": {
                "epistemic_meta": """
                By specifying A and D, the modeler defines not just what the agent believes,
                but the very structure of how those beliefs are formed. This is meta-epistemic
                because it specifies the epistemic framework within which the agent operates.
                """,
                "pragmatic_meta": """
                By specifying C, the modeler defines particular pragmatic considerations
                for the modeled entity. This is meta-pragmatic because it allows specification
                of pragmatic frameworks beyond simple reward functions.
                """,
            },
        }

        logger.info(
            "Demonstrated modeler specification capabilities in generative models"
        )
        return specifications


def create_simple_generative_model() -> GenerativeModel:
    """Create a simple generative model for demonstration.

    Returns:
        Simple GenerativeModel instance with basic matrices
    """
    from .gnn import MODEL_DIRECTORY, load_gnn_model

    return load_gnn_model(MODEL_DIRECTORY / "control_agent.md").model


def demonstrate_generative_model_concepts() -> Dict[str, Union[str, Dict]]:
    """Demonstrate key generative model concepts and their roles.

    Returns:
        Dictionary containing demonstrations and explanations
    """
    # Create simple model
    model = create_simple_generative_model()

    # Demonstrate inference
    observation = np.array([1.0, 0.0])  # Observed state 0
    posterior = model.perform_inference(observation)

    # Demonstrate prediction
    predicted_obs = model.predict_observations(0)  # From state 0

    # Demonstrate transition
    next_state = model.predict_state_transition(0, 1)  # State 0 + Action 1

    # Demonstrate preferences
    pref_obs_0 = model.calculate_preference_likelihood(0)
    pref_obs_1 = model.calculate_preference_likelihood(1)

    # Modeler specifications
    specifications = model.demonstrate_modeler_specifications()

    demonstration = {
        "model_structure": {
            "n_states": model.n_states,
            "n_observations": model.n_observations,
            "n_actions": model.n_actions,
            "matrices": {
                "A_shape": model.A.shape,
                "B_shape": model.B.shape,
                "C_shape": model.C.shape,
                "D_shape": model.D.shape,
            },
        },
        "inference_demo": {
            "observation": observation.tolist(),
            "posterior_beliefs": posterior.tolist(),
            "inference_interpretation": "Observation favors state 0, posterior reflects this",
        },
        "prediction_demo": {
            "state": 0,
            "predicted_observations": predicted_obs.tolist(),
            "prediction_interpretation": "State 0 most likely generates observation 0",
        },
        "transition_demo": {
            "current_state": 0,
            "action": 1,
            "next_state_distribution": next_state.tolist(),
            "transition_interpretation": "Action 1 switches from state 0 to state 1",
        },
        "preference_demo": {
            "preference_obs_0": pref_obs_0,
            "preference_obs_1": pref_obs_1,
            "preference_interpretation": "System prefers observation 0, avoids observation 1",
        },
        "modeler_specifications": specifications,
        "key_insights": {
            "modeler_power": """
            The generative model framework gives the modeler complete control over
            specifying both epistemic (A, D matrices) and pragmatic (C matrix)
            aspects of the modeled agent.
            """,
            "meta_epistemic": """
            By defining matrices A and D, the modeler specifies not just what the
            agent believes, but the very structure of how beliefs are formed and updated.
            """,
            "meta_pragmatic": """
            By defining matrix C, the modeler specifies particular pragmatic considerations
            for the modeled entity, enabling goal-directed behavior beyond simple rewards.
            """,
            "active_inference_foundation": """
            The A, B, C, D matrices form the foundation of Active Inference,
            enabling perception as inference, EFE calculations, and policy selection.
            """,
        },
    }

    logger.info("Demonstrated generative model concepts with complete working example")
    return demonstration
