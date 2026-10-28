"""Experimental task-level limit from an explicit source counterexample.

This is a conditional Gaussian two-hypothesis calculation, not a new
information-theoretic theorem, a physiological source validator, or a claim
that a particular EEG recording came from either source map.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import erfc, isfinite, sqrt

import numpy as np

from .classical_baselines import gaussian_ideal_observer


@dataclass(frozen=True)
class GaussianSourceClaimLimit:
    """Lower error bound for a declared disjoint two-class source task."""

    whitened_mean_distance: float
    conditional_minimax_error_lower_bound: float
    covariance_rank: int
    independent_observations: int
    target_source_l1_am: float
    alternative_source_l1_am: float
    alternative_l1_budget_am: float
    claim_boundary: str


def gaussian_source_claim_limit(
    gain_v_per_am: np.ndarray,
    noise_cov_v2: np.ndarray,
    target_source_am: np.ndarray,
    alternative_source_am: np.ndarray,
    excluded_target_region: np.ndarray,
    alternative_l1_budget_am: float,
    *,
    independent_observations: int = 1,
    rank_relative_tolerance: float = 1e-10,
) -> GaussianSourceClaimLimit:
    """Audit a focal-versus-distant source witness and bound task error.

    The task is to distinguish a declared target map with activity inside
    ``excluded_target_region`` from an alternative with no activity there.
    Both sensor observations are assumed Gaussian with the *same* supplied
    covariance. With equal prior probabilities, the optimal error for this
    fixed pair is Phi(-sqrt(n) * d / 2), where d is the whitened distance.
    Because the two declared source classes contain this pair, that fixed-pair
    error lower-bounds the worst-case error of any classifier over the classes.
    If covariance already describes an averaged evoked response, use n=1 for
    one such response; do not multiply by its averaging count again.
    """
    gain = np.asarray(gain_v_per_am, dtype=np.float64)
    cov = np.asarray(noise_cov_v2, dtype=np.float64)
    target = np.asarray(target_source_am, dtype=np.float64)
    alternative = np.asarray(alternative_source_am, dtype=np.float64)
    excluded = np.asarray(excluded_target_region)
    if gain.ndim != 2 or not np.isfinite(gain).all():
        raise ValueError("gain must be a finite sensor-by-source matrix")
    sensors, sources = gain.shape
    if sensors == 0 or sources == 0:
        raise ValueError("gain must be nonempty")
    if cov.shape != (sensors, sensors) or not np.isfinite(cov).all():
        raise ValueError("noise covariance must be a finite sensor square matrix")
    if not np.allclose(cov, cov.T, rtol=1e-10, atol=1e-20):
        raise ValueError("noise covariance must be symmetric")
    if target.shape != (sources,) or alternative.shape != (sources,):
        raise ValueError("source vectors must match the gain source count")
    if not np.isfinite(target).all() or not np.isfinite(alternative).all():
        raise ValueError("source vectors must be finite")
    if excluded.shape != (sources,) or excluded.dtype != np.dtype("bool"):
        raise ValueError("excluded target region must be a boolean source mask")
    if not np.any(excluded) or np.all(excluded):
        raise ValueError("the target region must be nonempty and leave alternatives")
    if not isfinite(alternative_l1_budget_am) or alternative_l1_budget_am <= 0:
        raise ValueError("alternative L1 budget must be positive and finite")
    if isinstance(independent_observations, bool) or not isinstance(independent_observations, int) or independent_observations < 1:
        raise ValueError("independent observations must be a positive integer")
    if not isfinite(rank_relative_tolerance) or not 0 < rank_relative_tolerance < 1:
        raise ValueError("rank relative tolerance must lie between zero and one")
    if np.linalg.norm(target[excluded], ord=1) <= 0:
        raise ValueError("target has no activity in the declared target region")
    # Source magnitudes are in A*m. A relative check keeps ordinary
    # floating-point witness replay robust without allowing material leakage.
    alternative_l1 = float(np.linalg.norm(alternative, ord=1))
    leakage = float(np.linalg.norm(alternative[excluded], ord=1))
    if leakage > 1e-10 * max(alternative_l1_budget_am, alternative_l1):
        raise ValueError("alternative is active inside the excluded target region")
    if alternative_l1 > alternative_l1_budget_am * (1 + 1e-7):
        raise ValueError("alternative exceeds its declared L1 source budget")
    baseline = gaussian_ideal_observer(
        gain @ target, gain @ alternative, cov, rtol=rank_relative_tolerance
    )
    distance = float(baseline["mahalanobis_distance"])
    error_bound = 0.5 * erfc(sqrt(independent_observations) * distance / (2 * sqrt(2)))
    return GaussianSourceClaimLimit(
        whitened_mean_distance=distance,
        conditional_minimax_error_lower_bound=error_bound,
        covariance_rank=int(baseline["covariance_rank"]),
        independent_observations=independent_observations,
        target_source_l1_am=float(np.linalg.norm(target, ord=1)),
        alternative_source_l1_am=alternative_l1,
        alternative_l1_budget_am=float(alternative_l1_budget_am),
        claim_boundary=(
            "Conditional on the supplied gain, source classes and equal-covariance "
            "Gaussian noise; the saved covariance applies to each independent "
            "observation. This is an algorithm-independent worst-case error "
            "lower bound, not a physiological or empirical EEG accuracy claim."
        ),
    )
