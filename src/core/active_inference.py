"""Active Inference Framework Implementation.

This module implements core Active Inference concepts including Expected Free Energy (EFE)
calculations, policy selection, and perception as inference. Active Inference treats
perception as a process of hypothesis testing and action selection as free energy minimization.

Key Concepts:
- Expected Free Energy (EFE): Epistemic + Pragmatic components
- Perception as Inference: Posterior beliefs over hidden states
- Action Selection: Policy selection minimizing expected free energy
- Generative Models: Probabilistic models of the world
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from .generative_models import GenerativeModel

import numpy as np
from numpy.typing import NDArray
from .probability import model_matrices, probability_vector, bayesian_update, entropy
from scipy.special import logsumexp, softmax, xlogy
from utils.exceptions import ValidationError
from utils.logging import get_logger

logger = get_logger(__name__)


class ActiveInferenceFramework:
    """Core Active Inference framework implementation.

    Implements the mathematical foundations of Active Inference including EFE calculations,
    policy selection, and perception as inference.
    """

    def __init__(
        self,
        generative_model: Union[Dict[str, NDArray], "GenerativeModel"],
        precision: float = 1.0,
    ) -> None:
        """Initialize Active Inference framework.

        Args:
            generative_model: Dictionary containing A, B, C, D matrices or GenerativeModel instance
            precision: Precision parameter for EFE calculations

        Raises:
            ValidationError: If generative model is malformed
        """
        # Handle both dictionary and GenerativeModel inputs
        if hasattr(generative_model, "A"):  # It's a GenerativeModel instance
            self.generative_model = {
                "A": generative_model.A,
                "B": generative_model.B,
                "C": generative_model.C,
                "D": generative_model.D,
            }
        else:  # It's already a dictionary
            self.generative_model = generative_model

        if not np.isfinite(precision) or precision <= 0:
            raise ValidationError("Precision must be finite and positive")
        self.precision = float(precision)
        self._validate_generative_model()

        # Extract dimensions for convenience
        self.n_states = self.generative_model["D"].shape[0]
        self.n_observations = self.generative_model["A"].shape[0]
        self.n_actions = (
            self.generative_model["B"].shape[2]
            if len(self.generative_model["B"].shape) > 2
            else 1
        )

        logger.info(
            f"Initialized Active Inference framework with precision {precision}"
        )

    def _validate_policy(self, policy: NDArray) -> None:
        """Validate that policy is valid.

        Args:
            policy: Policy array to validate

        Raises:
            ValidationError: If policy is invalid
        """
        policy = np.asarray(policy)

        if policy.ndim != 1 or policy.size == 0:
            raise ValidationError("Policy cannot be empty")

        if not np.issubdtype(policy.dtype, np.integer):
            raise ValidationError("Policy must contain integer action indices")

        # Check that all actions are valid (0 to n_actions-1)
        if np.any(policy < 0) or np.any(policy >= self.n_actions):
            raise ValidationError(
                f"Policy actions must be in range [0, {self.n_actions - 1}]"
            )

    def _validate_posterior_beliefs(self, posterior_beliefs: NDArray) -> None:
        """Require a state-sized finite normalized probability vector."""
        probability_vector(posterior_beliefs, self.n_states, "posterior beliefs")

    def _validate_generative_model(self) -> None:
        """Validate the same A/B/C/D contract as GenerativeModel."""
        if not isinstance(self.generative_model, dict):
            raise ValidationError(
                "Generative model must be a dictionary or GenerativeModel"
            )
        for key in ("A", "B", "C", "D"):
            if key not in self.generative_model:
                raise ValidationError(f"Missing required matrix: {key}")
        matrices = model_matrices(
            *(self.generative_model[k] for k in ("A", "B", "C", "D"))
        )
        self.generative_model = dict(zip(("A", "B", "C", "D"), matrices))

    def calculate_expected_free_energy(
        self,
        posterior_beliefs: NDArray,
        policy: NDArray,
        observations: Optional[NDArray] = None,
        aggregation: str = "mean",
    ) -> Tuple[float, Dict[str, float]]:
        """Evaluate open-loop EFE with exact zero support.

        The legacy score is -I(s;o) - E[C(o)]. `normalized_total` adds
        logsumexp(C) per step and equals risk + ambiguity for normalized
        preferences. Mean is the backward-compatible horizon convention;
        use aggregation='sum' for additive finite-horizon planning.
        `observations` is retained for compatibility; update beliefs first.
        """
        beliefs = probability_vector(
            posterior_beliefs, self.n_states, "posterior beliefs"
        )
        self._validate_policy(policy)
        policy = np.asarray(policy)
        if aggregation not in ("mean", "sum"):
            raise ValidationError("Aggregation must be 'mean' or 'sum'")
        A, B, C = (self.generative_model[k] for k in ("A", "B", "C"))
        column_entropies = -np.sum(xlogy(A, A), axis=0)
        shifted_C = C - np.max(C)
        normalized_log_preferences = shifted_C - logsumexp(shifted_C)
        values = []
        for action in policy:
            beliefs = B[:, :, action] @ beliefs
            outcomes = A @ beliefs
            ambiguity = float(beliefs @ column_entropies)
            information_gain = max(0.0, entropy(outcomes) - ambiguity)
            values.append(
                (
                    -information_gain,
                    -float(outcomes @ C),
                    ambiguity,
                    entropy(outcomes),
                    -float(outcomes @ normalized_log_preferences),
                )
            )
        reduced = (
            np.asarray(values).mean(axis=0)
            if aggregation == "mean"
            else np.asarray(values).sum(axis=0)
        )
        epistemic, pragmatic, ambiguity, outcome_entropy, normalized_cost = map(
            float, reduced
        )
        normalizer = float(logsumexp(C)) * (len(policy) if aggregation == "sum" else 1)
        total = epistemic + pragmatic
        components = {
            "epistemic": epistemic,
            "pragmatic": pragmatic,
            "total": total,
            "information_gain": -epistemic,
            "ambiguity": ambiguity,
            "outcome_entropy": outcome_entropy,
            "preference_normalizer": normalizer,
            "normalized_total": epistemic + normalized_cost,
            "risk": normalized_cost - outcome_entropy,
        }
        return total, components

    def _calculate_epistemic_affordance(
        self, posterior_beliefs: NDArray, policy: NDArray
    ) -> float:
        """Return negative expected information gain, averaged over policy steps."""
        return self.calculate_expected_free_energy(posterior_beliefs, policy)[1][
            "epistemic"
        ]

    def _calculate_pragmatic_value(
        self, posterior_beliefs: NDArray, policy: NDArray
    ) -> float:
        """Return negative expected preference logits, averaged over steps."""
        return self.calculate_expected_free_energy(posterior_beliefs, policy)[1][
            "pragmatic"
        ]

    def _calculate_entropy(self, beliefs: NDArray) -> float:
        """Return Shannon entropy in nats, preserving zero probabilities."""
        return entropy(probability_vector(beliefs))

    def select_optimal_policy(
        self,
        candidate_policies: List[NDArray],
        posterior_beliefs: Optional[NDArray] = None,
        aggregation: str = "mean",
    ) -> Tuple[NDArray, Dict]:
        """Select minimum EFE using current beliefs (D when omitted).

        Also report a normalized policy posterior softmax(-precision * G).
        Precision controls this posterior; it does not change argmin ranking.
        """
        if len(candidate_policies) == 0:
            raise ValidationError("Candidate policies cannot be empty")
        beliefs = (
            self._infer_posterior_beliefs()
            if posterior_beliefs is None
            else posterior_beliefs
        )
        scores = {}
        for i, policy in enumerate(candidate_policies):
            total, components = self.calculate_expected_free_energy(
                beliefs, policy, aggregation=aggregation
            )
            scores[f"policy_{i}"] = {
                "policy": policy,
                "efe_total": total,
                "efe_components": components,
                "efe_normalized": components["normalized_total"],
            }
        values = np.array([score["efe_normalized"] for score in scores.values()])
        if not np.all(np.isfinite(values)):
            raise ValidationError(
                "Policy evaluation produced non-finite normalized scores"
            )
        index = int(np.argmin(values))
        # Subtract the minimum before scaling to avoid overflow for large precision.
        with np.errstate(over="ignore"):
            logits = -self.precision * (values - values.min())
        probabilities = softmax(logits)
        return candidate_policies[index], {
            "optimal_policy": f"policy_{index}",
            "all_scores": scores,
            "selection_criteria": "minimize_EFE",
            "policy_probabilities": probabilities.tolist(),
            "precision": self.precision,
        }

    def _infer_posterior_beliefs(self) -> NDArray:
        """Return a copy of D when observations are unavailable."""
        return self.generative_model["D"].copy()

    def perception_as_inference(self, observations: NDArray) -> NDArray:
        """Implement perception as inference.

        Args:
            observations: Current sensory observations

        Returns:
            Posterior beliefs over hidden states
        """
        try:
            # Variational inference to minimize free energy
            posterior = self._variational_inference(observations)

            logger.debug(
                f"Perception as inference completed with {len(posterior)} state beliefs"
            )
            return posterior

        except Exception as e:
            logger.error(f"Error in perception as inference: {e}")
            raise ValidationError(f"Perception inference failed: {e}") from e

    def _variational_inference(self, observations: NDArray) -> NDArray:
        """Exact categorical or virtual-evidence Bayes update from D."""
        return bayesian_update(
            self.generative_model["A"], observations, self.generative_model["D"]
        )


def demonstrate_active_inference_concepts() -> Dict[str, Union[str, float]]:
    """Demonstrate core Active Inference concepts.

    Returns:
        Dictionary containing conceptual demonstrations and explanations
    """
    concepts = {
        "perception_as_inference": """
        Perception is treated as a process of hypothesis testing rather than
        direct sensory processing. The brain maintains probabilistic beliefs
        about the world and updates these beliefs to minimize surprise.
        """,
        "expected_free_energy": """
        Expected Free Energy (EFE) combines epistemic and pragmatic components:
        - Epistemic: Information gain through action
        - Pragmatic: Achievement of preferred outcomes
        Action selection minimizes EFE, balancing exploration and exploitation.
        """,
        "generative_models": """
        Generative models encode probabilistic relationships between:
        - Hidden states (unobserved causes)
        - Observations (sensory inputs)
        - Actions (interventions on the world)
        - Preferences (desired outcomes)
        """,
        "meta_pragmatic_aspect": """
        Active Inference is meta-pragmatic because it allows modelers to specify
        particular pragmatic considerations for the entities they model, going
        beyond simple reward functions to include epistemic motivations.
        """,
        "meta_epistemic_aspect": """
        Active Inference is meta-epistemic because it enables the specification
        of epistemic frameworks within which agents operate, allowing modelers
        to define how agents come to know and understand their environment.
        """,
    }

    # Simple numerical demonstration
    # B shape: (n_states, n_states, n_actions) — B[:, :, a] is the transition
    # matrix for action a.  Action 0 keeps states; action 1 switches them.
    _n = 2
    _B = np.zeros((_n, _n, _n))
    _B[:, :, 0] = np.eye(_n)  # stay
    _B[:, :, 1] = np.fliplr(np.eye(_n))  # switch
    simple_model = {
        "A": np.array([[0.8, 0.2], [0.2, 0.8]]),  # Observation likelihoods
        "B": _B,  # Transition probabilities (2, 2, 2)
        "C": np.array([1.0, -1.0]),  # Preferences
        "D": np.array([0.5, 0.5]),  # Prior beliefs
    }

    framework = ActiveInferenceFramework(simple_model)

    # Demonstrate EFE calculation
    posterior = np.array([0.6, 0.4])
    policy = np.array([0, 1])  # Simple two-step policy

    efe_total, efe_components = framework.calculate_expected_free_energy(
        posterior, policy
    )

    demonstration = {
        "concepts": concepts,
        "numerical_example": {
            "posterior_beliefs": posterior.tolist(),
            "policy": policy.tolist(),
            "efe_total": efe_total,
            "efe_components": efe_components,
        },
    }

    logger.info("Demonstrated Active Inference concepts with numerical example")
    return demonstration
