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

        self.precision = precision
        self._validate_generative_model()

        # Extract dimensions for convenience
        self.n_states = self.generative_model["D"].shape[0]
        self.n_observations = self.generative_model["A"].shape[0]
        self.n_actions = (
            self.generative_model["B"].shape[2] if len(self.generative_model["B"].shape) > 2 else 1
        )

        logger.info(f"Initialized Active Inference framework with precision {precision}")

    def _validate_policy(self, policy: NDArray) -> None:
        """Validate that policy is valid.

        Args:
            policy: Policy array to validate

        Raises:
            ValidationError: If policy is invalid
        """
        policy = np.asarray(policy)

        if policy.size == 0:
            raise ValidationError("Policy cannot be empty")

        if not np.issubdtype(policy.dtype, np.integer):
            raise ValidationError("Policy must contain integer action indices")

        # Check that all actions are valid (0 to n_actions-1)
        if np.any(policy < 0) or np.any(policy >= self.n_actions):
            raise ValidationError(f"Policy actions must be in range [0, {self.n_actions - 1}]")

    def _validate_posterior_beliefs(self, posterior_beliefs: NDArray) -> None:
        """Validate that posterior beliefs form a valid probability distribution.

        Args:
            posterior_beliefs: Array to validate

        Raises:
            ValidationError: If posterior beliefs are invalid
        """
        posterior_beliefs = np.asarray(posterior_beliefs)

        # Check for NaN or infinite values
        if not np.all(np.isfinite(posterior_beliefs)):
            raise ValidationError("Posterior beliefs contain NaN or infinite values")

        # Check for negative values
        if np.any(posterior_beliefs < 0):
            raise ValidationError("Posterior beliefs contain negative values")

        # Check normalization (sum close to 1)
        total = np.sum(posterior_beliefs)
        if not np.isclose(total, 1.0, atol=1e-6):
            raise ValidationError(f"Posterior beliefs do not sum to 1 (sum = {total:.6f})")

    def _validate_generative_model(self) -> None:
        """Validate generative model structure.

        Raises:
            ValidationError: If required matrices are missing or malformed
        """
        required_matrices = ["A", "B", "C", "D"]
        for matrix_name in required_matrices:
            if matrix_name not in self.generative_model:
                raise ValidationError(f"Missing required matrix: {matrix_name}")

        # Basic shape validation
        A = self.generative_model["A"]
        if len(A.shape) != 2:
            raise ValidationError("Matrix A must be 2-dimensional")

    def calculate_expected_free_energy(
        self,
        posterior_beliefs: NDArray,
        policy: NDArray,
        observations: Optional[NDArray] = None,
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate Expected Free Energy (EFE) for a given policy.

        EFE = Epistemic_Affordance + Pragmatic_Value

        Args:
            posterior_beliefs: Current posterior beliefs over hidden states
            policy: Action policy (sequence of actions)
            observations: Optional current observations

        Returns:
            Tuple of (total_EFE, component_dict) where component_dict contains:
            - 'epistemic': Epistemic affordance component
            - 'pragmatic': Pragmatic value component
        """
        try:
            # Validate inputs
            self._validate_posterior_beliefs(posterior_beliefs)
            self._validate_policy(policy)

            # Epistemic component: information gain from policy
            epistemic = self._calculate_epistemic_affordance(posterior_beliefs, policy)

            # Pragmatic component: expected cost/reward
            pragmatic = self._calculate_pragmatic_value(posterior_beliefs, policy)

            total_efe = epistemic + pragmatic

            components = {
                "epistemic": epistemic,
                "pragmatic": pragmatic,
                "total": total_efe,
            }

            logger.debug(
                f"EFE calculation: epistemic={epistemic:.4f}, pragmatic={pragmatic:.4f}, total={total_efe:.4f}"  # noqa: E501
            )

            return total_efe, components

        except Exception as e:
            logger.error(f"Error calculating EFE: {e}")
            raise ValidationError(f"EFE calculation failed: {e}") from e

    def _calculate_epistemic_affordance(self, posterior_beliefs: NDArray, policy: NDArray) -> float:
        """Calculate epistemic affordance (expected information gain).

        Epistemic affordance is the expected reduction in uncertainty about hidden
        states that results from executing the policy. Computed as the expected
        KL divergence between the posterior after observing outcomes and the
        predictive prior under the policy: E_Q(o|π)[KL(Q(s|o,π) || Q(s|π))].

        This equals the mutual information I(s; o | π), measuring how much
        observing outcomes under the policy would reduce state uncertainty.
        """
        A = self.generative_model["A"]
        B = self.generative_model["B"]

        n_states = len(posterior_beliefs)
        current_beliefs = posterior_beliefs.copy()
        total_epistemic = 0.0

        for action in policy:
            # Predicted next-state distribution under this action.
            # B convention: (n_states, n_states, n_actions) where B[:, :, a]
            # is the transition matrix for action a.  Fall back to identity
            # (no transition) if B does not conform to this shape.
            if (
                len(B.shape) == 3
                and B.shape[0] == n_states
                and B.shape[1] == n_states
                and action < B.shape[2]
            ):
                next_state_probs = B[:, :, action] @ current_beliefs
            else:
                next_state_probs = current_beliefs

            # Normalise to avoid drift
            next_state_probs = np.clip(next_state_probs, 1e-10, 1.0)
            next_state_probs = next_state_probs / next_state_probs.sum()

            # Predicted observation distribution: Q(o|π) = A @ Q(s|π)
            predicted_obs = A @ next_state_probs
            predicted_obs = np.clip(predicted_obs, 1e-10, 1.0)
            predicted_obs = predicted_obs / predicted_obs.sum()

            # Expected KL: sum_o Q(o|π) * KL(Q(s|o,π) || Q(s|π))
            expected_kl = 0.0
            for obs_idx in range(A.shape[0]):
                obs_prob = predicted_obs[obs_idx]
                if obs_prob < 1e-10:
                    continue
                # Bayesian update: Q(s|o,π) ∝ A[o,:] * Q(s|π)
                posterior_given_obs = A[obs_idx, :] * next_state_probs
                pgo_sum = posterior_given_obs.sum()
                if pgo_sum < 1e-10:
                    continue
                posterior_given_obs = posterior_given_obs / pgo_sum
                # KL(Q(s|o) || Q(s|π))
                kl = np.sum(
                    posterior_given_obs
                    * (np.log(posterior_given_obs + 1e-10) - np.log(next_state_probs + 1e-10))
                )
                expected_kl += obs_prob * kl

            total_epistemic += expected_kl
            current_beliefs = next_state_probs  # Propagate beliefs

        # Average over policy steps; epistemic term enters EFE negatively
        # (higher information gain reduces EFE)
        n_steps = max(1, len(policy))
        return -total_epistemic / n_steps

    def _calculate_pragmatic_value(self, posterior_beliefs: NDArray, policy: NDArray) -> float:
        """Calculate pragmatic value (expected preference divergence).

        Pragmatic value measures the expected divergence between the predicted
        observation distribution and the agent's preferences encoded in matrix C.
        A positive value indicates predicted observations conflict with preferences.
        """
        A = self.generative_model["A"]
        B = self.generative_model["B"]
        C = self.generative_model.get("C", np.zeros(A.shape[0]))

        n_states = len(posterior_beliefs)
        current_beliefs = posterior_beliefs.copy()
        total_pragmatic = 0.0

        for action in policy:
            if (
                len(B.shape) == 3
                and B.shape[0] == n_states
                and B.shape[1] == n_states
                and action < B.shape[2]
            ):
                next_state_probs = B[:, :, action] @ current_beliefs
            else:
                next_state_probs = current_beliefs

            next_state_probs = np.clip(next_state_probs, 1e-10, 1.0)
            next_state_probs = next_state_probs / next_state_probs.sum()

            # Expected observations under policy
            predicted_obs = A @ next_state_probs
            predicted_obs = np.clip(predicted_obs, 1e-10, 1.0)
            predicted_obs = predicted_obs / predicted_obs.sum()

            # Pragmatic cost: -E_Q(o)[log P(o)] = -Q(o)·C
            # Lower is better (preferred observations have high C values)
            pragmatic_cost = -np.sum(predicted_obs * C)
            total_pragmatic += pragmatic_cost
            current_beliefs = next_state_probs

        return total_pragmatic / max(1, len(policy))

    def _calculate_entropy(self, beliefs: NDArray) -> float:
        """Calculate Shannon entropy of a belief distribution."""
        beliefs = np.clip(beliefs, 1e-10, 1.0)
        return -np.sum(beliefs * np.log(beliefs))

    def select_optimal_policy(self, candidate_policies: List[NDArray]) -> Tuple[NDArray, Dict]:
        """Select optimal policy by minimizing EFE.

        Args:
            candidate_policies: List of candidate action policies

        Returns:
            Tuple of (optimal_policy, selection_info) where selection_info contains
            EFE values for all policies and selection criteria
        """
        try:
            policy_scores = {}

            for i, policy in enumerate(candidate_policies):
                posterior_beliefs = self._infer_posterior_beliefs()
                efe_total, efe_components = self.calculate_expected_free_energy(
                    posterior_beliefs, policy
                )
                policy_scores[f"policy_{i}"] = {
                    "policy": policy,
                    "efe_total": efe_total,
                    "efe_components": efe_components,
                }

            # Select policy with minimal EFE
            optimal_policy_key = min(
                policy_scores.keys(), key=lambda k: policy_scores[k]["efe_total"]
            )

            optimal_policy = policy_scores[optimal_policy_key]["policy"]
            selection_info = {
                "optimal_policy": optimal_policy_key,
                "all_scores": policy_scores,
                "selection_criteria": "minimize_EFE",
            }

            logger.info(f"Selected optimal policy: {optimal_policy_key}")
            return optimal_policy, selection_info

        except Exception as e:
            logger.error(f"Error selecting optimal policy: {e}")
            raise ValidationError(f"Policy selection failed: {e}") from e

    def _infer_posterior_beliefs(self) -> NDArray:
        """Return the prior belief distribution from the generative model.

        Uses the D matrix (prior over initial states) as the starting belief
        when no observation is available for inference.

        Returns:
            Prior belief distribution over hidden states from matrix D
        """
        D = self.generative_model["D"]
        D = np.clip(D, 1e-10, 1.0)
        return D / D.sum()

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

            logger.debug(f"Perception as inference completed with {len(posterior)} state beliefs")
            return posterior

        except Exception as e:
            logger.error(f"Error in perception as inference: {e}")
            raise ValidationError(f"Perception inference failed: {e}") from e

    def _variational_inference(self, observations: NDArray) -> NDArray:
        """Perform Bayesian belief update given observations.

        Computes posterior Q(s|o) ∝ P(o|s) * P(s) by multiplying the
        observation likelihood column A[o, :] with the prior D.

        Args:
            observations: One-hot or probability vector over observation indices

        Returns:
            Normalised posterior belief distribution over hidden states
        """
        A = self.generative_model["A"]
        D = self.generative_model["D"]

        # Identify the most likely observation index from the input vector
        obs_idx = int(np.argmax(observations))

        # Likelihood of each hidden state producing this observation
        likelihood = A[obs_idx, :]

        # Posterior ∝ likelihood × prior
        posterior = likelihood * D
        posterior = np.clip(posterior, 1e-10, 1.0)
        posterior = posterior / posterior.sum()

        return posterior


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
        "A": np.array([[0.8, 0.2], [0.3, 0.7]]),  # Observation likelihoods
        "B": _B,  # Transition probabilities (2, 2, 2)
        "C": np.array([1.0, -1.0]),  # Preferences
        "D": np.array([0.5, 0.5]),  # Prior beliefs
    }

    framework = ActiveInferenceFramework(simple_model)

    # Demonstrate EFE calculation
    posterior = np.array([0.6, 0.4])
    policy = np.array([0, 1])  # Simple two-step policy

    efe_total, efe_components = framework.calculate_expected_free_energy(posterior, policy)

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
