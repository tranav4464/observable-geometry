"""Standard linear-Gaussian building blocks; none are claimed as a new algorithm.

Inputs must share channel order, reference, physical units and source convention.
Prior covariance fixes the scale in which information fractions are interpreted.
"""
from dataclasses import dataclass
import numpy as np


def _matrix(x, name):
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or not np.isfinite(x).all():
        raise ValueError(f"{name} must be a finite 2D matrix")
    return x


def _psd_eigh(x, name, rtol=1e-10):
    x = _matrix(x, name)
    if x.shape[0] != x.shape[1] or np.linalg.norm(x-x.T) > 1e-8 * max(np.linalg.norm(x), np.finfo(float).tiny):
        raise ValueError(f"{name} must be symmetric and square")
    values, vectors = np.linalg.eigh(x)
    scale = max(float(np.max(np.abs(values))), np.finfo(float).tiny)
    if values.min() < -rtol * scale:
        raise ValueError(f"{name} must be positive semidefinite")
    return values, vectors, scale


def average_reference(data, leadfield, noise_cov):
    """Apply the SAME reference projection to observations, forward and noise."""
    x = _matrix(data, "data")
    leadfield = _matrix(leadfield, "leadfield")
    noise_cov = _matrix(noise_cov, "noise_cov")
    c = x.shape[0]
    if leadfield.shape[0] != c or noise_cov.shape != (c, c):
        raise ValueError("channel dimensions disagree")
    r = np.eye(c) - np.ones((c, c)) / c
    return r @ x, r @ leadfield, r @ noise_cov @ r.T


@dataclass
class GeometryFit:
    source_mean: np.ndarray
    source_std: np.ndarray
    coefficient_mean: np.ndarray
    coefficient_covariance: np.ndarray
    singular_values: np.ndarray
    information_fractions: np.ndarray
    coefficient_resolution: np.ndarray
    noise_rank: int
    forward_rank: int
    whitened_residual_norm: float


def fit_linear_geometry(data, leadfield, basis, noise_cov, prior_cov, rtol=1e-10):
    """Posterior under x=L Phi a+noise, a~N(0,Q), noise~N(0,C).

    Rank-deficient reference covariance is supported. A zero-noise direction with
    nonzero observations/forward values is rejected, not silently discarded.
    Uncertainty is conditional on the supplied model and prior, NOT calibrated
    source-location confidence. source_std is marginal amplitude uncertainty.
    """
    x = _matrix(data, "data")
    l = _matrix(leadfield, "leadfield")
    phi = _matrix(basis, "basis")
    q = _matrix(prior_cov, "prior_cov")
    c, _ = x.shape
    if l.shape[0] != c or l.shape[1] != phi.shape[0] or q.shape != (phi.shape[1],) * 2:
        raise ValueError("data/leadfield/basis/prior dimensions disagree")
    if np.shape(noise_cov) != (c, c):
        raise ValueError("noise covariance channel count disagrees")
    d, u, scale = _psd_eigh(noise_cov, "noise_cov", rtol)
    keep = d > rtol * scale
    if not keep.any():
        raise ValueError("noise covariance has zero supported rank")
    projector = u[:, keep] @ u[:, keep].T
    for value, name in ((x, "data"), (l, "leadfield")):
        remainder = value - projector @ value
        if np.linalg.norm(remainder) > 1e-7 * max(np.linalg.norm(value), np.finfo(float).tiny):
            raise ValueError(f"{name} contains an unsupported noise direction; check reference/rank")
    w = u[:, keep].T / np.sqrt(d[keep])[:, None]
    qd, qu, qscale = _psd_eigh(q, "prior_cov", rtol)
    if np.min(qd) <= rtol * qscale:
        raise ValueError("prior_cov must be positive definite at the specified tolerance")
    qroot = (qu * np.sqrt(qd)) @ qu.T
    a = w @ l @ phi
    b = a @ qroot
    _, singular, vt = np.linalg.svd(b, full_matrices=True)
    padded = np.zeros(phi.shape[1])
    padded[:len(singular)] = singular
    fractions = padded ** 2 / (1 + padded ** 2)
    cu = (vt.T * (1 / (1 + padded ** 2))) @ vt
    ca = qroot @ cu @ qroot.T
    mean = ca @ a.T @ (w @ x)
    source = phi @ mean
    source_var = np.einsum("ij,jk,ik->i", phi, ca, phi)
    threshold = rtol * singular.max() if singular.size else 0.0
    return GeometryFit(source, np.sqrt(np.maximum(source_var, 0)), mean, ca,
                       padded, fractions, ca @ a.T @ a,
                       int(keep.sum()), int((singular > threshold).sum()),
                       float(np.linalg.norm(w @ x - a @ mean)))


def robust_sensor_scores(covariances, conditional_rows, conditional_noise_variances, target):
    """Worst-case target-variance reduction over a finite supplied model ensemble.

    Rows are candidate measurements AFTER conditioning out current-sensor noise
    correlation. Inputs must use a FIXED reference and shared coefficient basis.
    This is a standard Gaussian variance update with a conservative aggregation.
    The finite ensemble is a sensitivity set, not a guaranteed physical bound.
    """
    cov = np.asarray(covariances, dtype=float)
    rows = np.asarray(conditional_rows, dtype=float)
    noises = np.asarray(conditional_noise_variances, dtype=float)
    target = _matrix(target, "target")
    if cov.ndim != 3 or rows.ndim != 3 or noises.shape != rows.shape[:2]:
        raise ValueError("expected covariance MxKxK, rows MxExK, noise MxE")
    m, k, k2 = cov.shape
    if k != k2 or rows.shape[0] != m or rows.shape[2] != k or target.shape[1] != k:
        raise ValueError("ensemble dimensions disagree")
    if not np.isfinite(rows).all() or not np.isfinite(noises).all() or (noises <= 0).any():
        raise ValueError("candidate rows must be finite and noise variances positive")
    reductions = np.empty(rows.shape[:2])
    for model in range(m):
        _psd_eigh(cov[model], "posterior covariance")
        projected = rows[model] @ cov[model]
        numerator = np.sum((projected @ target.T) ** 2, axis=1)
        denominator = noises[model] + np.sum(projected * rows[model], axis=1)
        reductions[model] = numerator / denominator
    worst_case = np.min(reductions, axis=0)
    return {"per_model_reduction": reductions, "worst_case_reduction": worst_case,
            "ranking": np.argsort(-worst_case, kind="stable")}
