"""Archived candidate: local sensitivity of lag covariance to VAR edges.

This candidate diagnostic is not the active Track B contribution and is not
calibrated or claimed novel. It remains in the codebase as historical work;
the current B2 design is specified in ``docs/track_b/B2_FORMAL_SPEC.md``.
It applies only to stable first-order linear-Gaussian VAR models.
"""
from __future__ import annotations

import numpy as np


def _as_square(value: np.ndarray, name: str) -> np.ndarray:
    matrix = np.asarray(value, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.isfinite(matrix).all():
        raise ValueError(f"{name} must be finite")
    return matrix


def _validate_stable_transition(transition: np.ndarray) -> np.ndarray:
    a = _as_square(transition, "transition")
    if np.max(np.abs(np.linalg.eigvals(a))) >= 1.0:
        raise ValueError("transition must be strictly stable (spectral radius < 1)")
    return a


def _validate_covariance(covariance: np.ndarray, size: int, name: str,
                         *, positive_definite: bool) -> np.ndarray:
    value = np.asarray(covariance, dtype=np.float64)
    if value.shape != (size, size) or not np.isfinite(value).all():
        raise ValueError(f"{name} must be a finite {size}x{size} matrix")
    if not np.allclose(value, value.T, rtol=1e-10, atol=1e-12):
        raise ValueError(f"{name} must be symmetric")
    eigmin = float(np.min(np.linalg.eigvalsh(value)))
    threshold = 1e-12 * max(float(np.linalg.norm(value, ord=2)), np.finfo(float).tiny)
    if positive_definite and eigmin <= threshold:
        raise ValueError(f"{name} must be positive definite")
    if not positive_definite and eigmin < -threshold:
        raise ValueError(f"{name} must be positive semidefinite")
    return (value + value.T) / 2


def stationary_covariance(transition: np.ndarray, process_covariance: np.ndarray,
                          *, rtol: float = 1e-12, max_iter: int = 10000) -> np.ndarray:
    """Solve ``Gamma = A Gamma A.T + Q`` by convergent Lyapunov iteration."""
    a = _validate_stable_transition(transition)
    q = _validate_covariance(process_covariance, len(a), "process_covariance",
                              positive_definite=False)
    if not np.isfinite(rtol) or rtol <= 0 or not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("rtol and max_iter must be positive")
    gamma = np.zeros_like(q)
    scale = max(1.0, float(np.linalg.norm(q, ord="fro")))
    for _ in range(max_iter):
        updated = a @ gamma @ a.T + q
        updated = (updated + updated.T) / 2
        if np.linalg.norm(updated - gamma, ord="fro") <= rtol * scale:
            return updated
        gamma = updated
    raise RuntimeError("stationary covariance iteration did not converge")


def edge_observation_covariance_derivative(
    transition: np.ndarray,
    process_covariance: np.ndarray,
    observation_operator: np.ndarray,
    target: int,
    source: int,
    lag: int,
    *,
    rtol: float = 1e-12,
    max_iter: int = 10000,
) -> np.ndarray:
    """Return ``d Cov(o[t], o[t-lag]) / d A[target, source]`` for lag >= 1."""
    a = _validate_stable_transition(transition)
    q = _validate_covariance(process_covariance, len(a), "process_covariance",
                              positive_definite=False)
    h = np.asarray(observation_operator, dtype=np.float64)
    if h.ndim != 2 or h.shape[1] != len(a) or not np.isfinite(h).all():
        raise ValueError("observation_operator must be finite with N columns")
    if not (isinstance(target, int) and isinstance(source, int)
            and 0 <= target < len(a) and 0 <= source < len(a)):
        raise ValueError("edge indices are out of range")
    if not isinstance(lag, int) or lag < 1:
        raise ValueError("lag must be a positive integer")
    if not np.isfinite(rtol) or rtol <= 0 or not isinstance(max_iter, int) or max_iter < 1:
        raise ValueError("rtol and max_iter must be positive")

    gamma = stationary_covariance(a, q, rtol=rtol, max_iter=max_iter)
    edge = np.zeros_like(a)
    edge[target, source] = 1.0
    forcing = edge @ gamma @ a.T + a @ gamma @ edge.T
    derivative_gamma = np.zeros_like(a)
    scale = max(1.0, float(np.linalg.norm(forcing, ord="fro")))
    for _ in range(max_iter):
        updated = a @ derivative_gamma @ a.T + forcing
        updated = (updated + updated.T) / 2
        if np.linalg.norm(updated - derivative_gamma, ord="fro") <= rtol * scale:
            derivative_gamma = updated
            break
        derivative_gamma = updated
    else:
        raise RuntimeError("edge covariance derivative iteration did not converge")

    power = a.copy()
    derivative_power = edge.copy()
    for _ in range(1, lag):
        derivative_power = derivative_power @ a + power @ edge
        power = power @ a
    return h @ (derivative_power @ gamma + power @ derivative_gamma) @ h.T


def edge_observation_sensitivity(
    transition: np.ndarray,
    process_covariance: np.ndarray,
    observation_operator: np.ndarray,
    observation_noise_covariance: np.ndarray,
    max_lag: int = 3,
) -> np.ndarray:
    """Compute standardized finite-lag covariance sensitivity for each edge.

    Diagonal entries are zero because self-edges are excluded from the Track B
    primary graph task. The value is an observation-operator-conditioned local
    sensitivity, not an edge-existence probability or causal confidence.
    """
    a = _validate_stable_transition(transition)
    q = _validate_covariance(process_covariance, len(a), "process_covariance",
                              positive_definite=False)
    h = np.asarray(observation_operator, dtype=np.float64)
    if h.ndim != 2 or h.shape[1] != len(a) or not np.isfinite(h).all():
        raise ValueError("observation_operator must be finite with N columns")
    r = _validate_covariance(observation_noise_covariance, h.shape[0],
                             "observation_noise_covariance", positive_definite=True)
    if not isinstance(max_lag, int) or max_lag < 1:
        raise ValueError("max_lag must be a positive integer")
    vals, vecs = np.linalg.eigh(r)
    whitening = (vecs / np.sqrt(vals)) @ vecs.T
    sensitivity = np.zeros_like(a)
    for target in range(len(a)):
        for source in range(len(a)):
            if target == source:
                continue
            for lag in range(1, max_lag + 1):
                derivative = edge_observation_covariance_derivative(
                    a, q, h, target, source, lag
                )
                standardized = whitening @ derivative @ whitening
                sensitivity[target, source] += float(np.sum(standardized ** 2))
    return sensitivity
