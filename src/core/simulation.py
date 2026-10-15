"""Sample one-step categorical worlds with shared counterfactual random numbers."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .generative_models import GenerativeModel
from utils.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class PotentialOutcomes:
    """Columns are interventions, not independent replications of the world."""

    initial_states: NDArray[np.int64]
    next_states: NDArray[np.int64]
    observations: NDArray[np.int64]


def sample_potential_outcomes(
    world: GenerativeModel, n_trials: int, rng: np.random.Generator
) -> PotentialOutcomes:
    """Draw D, then B and A for every action using common trial-level uniforms.

    This coupling defines paired potential outcomes, not a claim that alternate
    actions can all be observed in one physical trial. Agent beliefs are absent.
    """
    if not isinstance(n_trials, int) or isinstance(n_trials, bool) or n_trials < 1:
        raise ValidationError("World sampling requires a positive integer trial count")
    initial = rng.choice(world.n_states, size=n_trials, p=world.D)
    transition_uniform = rng.random(n_trials)
    observation_uniform = rng.random(n_trials)
    states = np.empty((n_trials, world.n_actions), dtype=np.int64)
    observations = np.empty_like(states)
    for action in range(world.n_actions):
        transitions = np.cumsum(world.B[:, initial, action].T, axis=1)
        transitions[:, -1] = 1.0
        states[:, action] = (transition_uniform[:, None] >= transitions).sum(axis=1)
        likelihoods = np.cumsum(world.A[:, states[:, action]].T, axis=1)
        likelihoods[:, -1] = 1.0
        observations[:, action] = (observation_uniform[:, None] >= likelihoods).sum(
            axis=1
        )
    return PotentialOutcomes(initial, states, observations)
