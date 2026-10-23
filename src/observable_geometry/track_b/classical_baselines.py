"""Classical Gaussian pair-discrimination baselines for Track B.

These are standard signal-detection quantities, included as comparators rather
than claimed as a new method. Their Bayes error is valid only for one draw from
two Gaussian hypotheses with known means, a shared covariance, and equal priors.
"""
from __future__ import annotations

import math
import numpy as np


def gaussian_ideal_observer(mean_a, mean_b, covariance, rtol: float = 1e-10) -> dict:
    """Return squared Mahalanobis distance and equal-prior ideal-observer error.

    A singular covariance is allowed (e.g. average-referenced EEG) only when
    both means lie in its supported subspace. Unsupported zero-noise components
    are rejected rather than silently projected away.
    """
    a = np.asarray(mean_a, dtype=float)
    b = np.asarray(mean_b, dtype=float)
    c = np.asarray(covariance, dtype=float)
    if (a.ndim != 1 or b.shape != a.shape or c.shape != (a.size, a.size)
            or not np.isfinite(a).all() or not np.isfinite(b).all()
            or not np.isfinite(c).all()):
        raise ValueError("means must be finite vectors and covariance a matching finite matrix")
    if not np.isfinite(rtol) or rtol <= 0:
        raise ValueError("rtol must be finite and positive")
    scale = max(float(np.linalg.norm(c, ord=2)), np.finfo(float).tiny)
    if np.linalg.norm(c - c.T, ord=2) > 1e-8 * scale:
        raise ValueError("covariance must be symmetric")
    values, vectors = np.linalg.eigh((c + c.T) / 2)
    spectral_scale = max(float(np.max(np.abs(values))), np.finfo(float).tiny)
    if values.min() < -rtol * spectral_scale:
        raise ValueError("covariance must be positive semidefinite")
    keep = values > rtol * spectral_scale
    if not keep.any():
        raise ValueError("covariance has zero supported rank")
    basis = vectors[:, keep]
    projector = basis @ basis.T
    for mean, name in ((a, "mean_a"), (b, "mean_b")):
        if np.linalg.norm(mean - projector @ mean) > 1e-7 * max(
                np.linalg.norm(mean), np.finfo(float).tiny):
            raise ValueError(f"{name} has a component outside covariance support")
    delta = basis.T @ (a - b)
    d_squared = float(np.sum(delta * delta / values[keep]))
    distance = math.sqrt(max(d_squared, 0.0))
    # Phi(-d/2) = 0.5 * erfc(d / (2 sqrt(2))).
    bayes_error = 0.5 * math.erfc(distance / (2.0 * math.sqrt(2.0)))
    return {"squared_mahalanobis_distance": d_squared,
            "mahalanobis_distance": distance,
            "equal_prior_single_observation_bayes_error": bayes_error,
            "covariance_rank": int(keep.sum()),
            "assumptions": ["Gaussian hypotheses", "known means", "shared covariance",
                            "equal priors", "single observation"]}
