"""Probability contracts shared by inference, validation, and diagnostics.

All conditional probability matrices are column stochastic: the first axis
indexes the destination/outcome. Zeros retain their exact support.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.special import xlogy

from utils.exceptions import ValidationError


def probability_vector(
    value: ArrayLike, size: int | None = None, name: str = "distribution"
) -> NDArray:
    """Return a finite, nonempty normalized vector, or reject the input."""
    try:
        result = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{name} must contain numeric probabilities") from exc
    if (
        result.ndim != 1
        or result.size == 0
        or (size is not None and result.size != size)
    ):
        raise ValidationError(
            f"{name} must be a nonempty 1-dimensional vector of length {size}"
        )
    if not np.all(np.isfinite(result)) or np.any(result < 0):
        raise ValidationError(
            f"{name} contains NaN, infinite, or negative probabilities"
        )
    if not np.isclose(result.sum(), 1.0, atol=1e-6, rtol=0):
        raise ValidationError(f"{name} is not properly normalized; must sum to 1")
    return result / result.sum()


def model_matrices(
    A: ArrayLike, B: ArrayLike, C: ArrayLike, D: ArrayLike
) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    """Validate and copy A/B/C/D; promote a single-action 2-D B to 3-D."""
    try:
        A, B, C, D = (np.array(v, dtype=float, copy=True) for v in (A, B, C, D))
    except (TypeError, ValueError) as exc:
        raise ValidationError("Model matrices must be numeric arrays") from exc
    D = probability_vector(D, name="prior beliefs (D)")
    if A.ndim != 2 or min(A.shape) == 0:
        raise ValidationError("Matrix A must be nonempty and 2-dimensional")
    if A.shape[1] != D.size:
        raise ValidationError("A matrix columns must match D length")
    if B.ndim == 2:
        B = B[:, :, None]
    if B.ndim != 3 or B.shape[:2] != (D.size, D.size) or B.shape[2] == 0:
        raise ValidationError(
            "B matrix first two dimensions must match states with at least one action"
        )
    if C.ndim != 1:
        raise ValidationError("Matrix C must be 1-dimensional")
    if C.shape != (A.shape[0],):
        raise ValidationError("C matrix length must match A rows")
    if not np.all(np.isfinite(C)):
        raise ValidationError("C must be finite")
    for name, matrix in (("A", A), ("B", B)):
        if not np.all(np.isfinite(matrix)) or np.any(matrix < 0):
            raise ValidationError(
                f"{name} contains NaN, infinite, or negative probabilities"
            )
        if not np.allclose(matrix.sum(axis=0), 1.0, atol=1e-6, rtol=0):
            raise ValidationError(
                f"{name} columns is not properly normalized; must sum to 1"
            )
    A /= A.sum(axis=0, keepdims=True)
    B /= B.sum(axis=0, keepdims=True)
    return A, B, C, D


def observation_likelihood(A: NDArray, observation: ArrayLike) -> NDArray:
    """Likelihood over states from a category or normalized soft evidence.

    A vector e is virtual evidence: L(s) = sum_o e(o) A[o,s]. It is
    neither an argmax category nor a Jeffrey posterior mixture.
    """
    if isinstance(observation, (int, np.integer)) and not isinstance(observation, bool):
        if not 0 <= observation < A.shape[0]:
            raise ValidationError("Observation index out of range")
        return A[int(observation)].copy()
    evidence = probability_vector(observation, A.shape[0], "observation evidence")
    return A.T @ evidence


def bayesian_update(A: NDArray, observation: ArrayLike, prior: ArrayLike) -> NDArray:
    """Exact categorical/virtual-evidence Bayes update; reject impossible evidence."""
    prior = probability_vector(prior, A.shape[1], "prior beliefs")
    joint = observation_likelihood(A, observation) * prior
    evidence = joint.sum()
    if evidence <= 0:
        raise ValidationError("Observation is impossible under the model and prior")
    return joint / evidence


def entropy(probabilities: ArrayLike) -> float:
    """Shannon entropy in nats, with 0 log 0 = 0."""
    return float(-np.sum(xlogy(probabilities, probabilities)))
