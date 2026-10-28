"""Measured-field source-family observability certificate.

This module is the computation layer for COG-2026-10-28-v1.  It accepts an
observed sensor field and *candidate forward explanations* supplied by a
participant-specific model.  Candidate fields are hypotheses; the observed
field must come from measured data in the scientific runs.

The result is deliberately conservative.  A family is called ``fit`` only
when every declared forward-model variant fits within the tolerance.  It is
called ``excluded`` only when every variant is outside the tolerance.  Anything
between those two cases is ``sensitive``.  This prevents a favourable single
head-model variant from being reported as a robust attribution.

No neural signal is generated here.  Synthetic/algebraic inputs belong only in
unit tests and must never be used for calibration or the primary result.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class FamilyCertificate:
    """Residual interval and conservative status for one source family."""

    name: str
    residuals: tuple[float, ...]
    lower_residual: float
    upper_residual: float
    best_variant: int
    status: str


@dataclass(frozen=True)
class ObservabilityCertificate:
    """Complete family comparison for one measured field."""

    tolerance: float
    families: tuple[FamilyCertificate, ...]
    decision: str
    fitted_family_names: tuple[str, ...]
    excluded_family_names: tuple[str, ...]
    sensitive_family_names: tuple[str, ...]
    whitening_rank: int | None


def whiten_field_and_design(
    field: np.ndarray,
    design: np.ndarray,
    noise_covariance: np.ndarray,
    *,
    eigenvalue_rtol: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Whiten a sensor field and candidate design using a PSD covariance.

    The supported covariance subspace is retained.  This is a numerical
    contract, not a claim that the covariance is physiologically complete.
    """
    y = np.asarray(field, dtype=np.float64)
    a = np.asarray(design, dtype=np.float64)
    cov = np.asarray(noise_covariance, dtype=np.float64)
    if y.ndim != 1 or a.ndim != 2 or a.shape[0] != y.size:
        raise ValueError("field and design dimensions are inconsistent")
    if cov.shape != (y.size, y.size):
        raise ValueError("noise covariance must match the sensor dimension")
    if not (np.isfinite(y).all() and np.isfinite(a).all() and np.isfinite(cov).all()):
        raise ValueError("field, design and covariance must be finite")
    scale = max(float(np.linalg.norm(cov)), np.finfo(np.float64).tiny)
    if float(np.linalg.norm(cov - cov.T)) > 1e-8 * scale:
        raise ValueError("noise covariance is not symmetric")
    values, vectors = np.linalg.eigh((cov + cov.T) * 0.5)
    spectral = max(float(np.max(np.abs(values))), np.finfo(np.float64).tiny)
    if float(values.min()) < -eigenvalue_rtol * spectral:
        raise ValueError("noise covariance is not positive semidefinite")
    keep = values > eigenvalue_rtol * spectral
    if not keep.any():
        raise ValueError("noise covariance has zero supported rank")
    projection = vectors[:, keep].T
    return (
        (projection @ y) / np.sqrt(values[keep]),
        (projection @ a) / np.sqrt(values[keep, None]),
        int(keep.sum()),
    )


def _least_squares_residual(field: np.ndarray, design: np.ndarray) -> float:
    """Profile unrestricted coefficients and return a float64 residual."""
    if design.ndim != 2 or design.shape[0] != field.size or design.shape[1] < 1:
        raise ValueError("each family variant needs a nonempty sensor-by-basis matrix")
    coefficients, *_ = np.linalg.lstsq(design, field, rcond=None)
    residual = field - design @ coefficients
    return float(np.linalg.norm(residual))


def certify_observability(
    field: np.ndarray,
    family_variants: Mapping[str, Sequence[np.ndarray]],
    *,
    tolerance: float,
    noise_covariance: np.ndarray | None = None,
    require_all_variants: bool = True,
) -> ObservabilityCertificate:
    """Compare a measured sensor field against declared source families.

    ``family_variants[name]`` contains one or more candidate design matrices.
    Each variant corresponds to a fixed point in the declared forward-model
    uncertainty set.  Coefficients are profiled by least squares; a future
    protocol may replace this with a constrained solver, but must preserve the
    same interval/status contract.

    ``require_all_variants=True`` makes ``fit`` mean the residual upper bound is
    within tolerance and ``excluded`` mean the residual lower bound is above it.
    If false, status is an exploratory best-variant status and must not be used
    for the primary COG decision.
    """
    y = np.asarray(field, dtype=np.float64)
    if y.ndim != 1 or y.size < 1 or not np.isfinite(y).all():
        raise ValueError("field must be a finite, nonempty vector")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    if not family_variants:
        raise ValueError("at least one source family is required")
    certificates: list[FamilyCertificate] = []
    rank: int | None = None
    for name, variants in family_variants.items():
        if not name or not variants:
            raise ValueError("each family needs a name and at least one variant")
        residuals: list[float] = []
        for variant in variants:
            matrix = np.asarray(variant, dtype=np.float64)
            if noise_covariance is not None:
                whitened_y, whitened_matrix, rank_here = whiten_field_and_design(
                    y, matrix, noise_covariance
                )
                rank = rank_here if rank is None else rank
                if rank != rank_here:
                    raise ValueError("all family variants must share covariance rank")
                residuals.append(_least_squares_residual(whitened_y, whitened_matrix))
            else:
                if matrix.ndim != 2 or matrix.shape[0] != y.size:
                    raise ValueError("family variant has the wrong sensor dimension")
                if not np.isfinite(matrix).all():
                    raise ValueError("family variant must be finite")
                residuals.append(_least_squares_residual(y, matrix))
        lower = float(min(residuals))
        upper = float(max(residuals))
        if require_all_variants:
            status = "fit" if upper <= tolerance else "excluded" if lower > tolerance else "sensitive"
        else:
            status = "fit" if lower <= tolerance else "excluded"
        certificates.append(FamilyCertificate(
            name=str(name), residuals=tuple(residuals), lower_residual=lower,
            upper_residual=upper, best_variant=int(np.argmin(residuals)), status=status,
        ))
    fitted = tuple(c.name for c in certificates if c.status == "fit")
    excluded = tuple(c.name for c in certificates if c.status == "excluded")
    sensitive = tuple(c.name for c in certificates if c.status == "sensitive")
    if len(fitted) == 1 and not sensitive:
        decision = "unique_enough"
    elif len(fitted) >= 1 or sensitive:
        decision = "ambiguous"
    else:
        decision = "unsupported"
    return ObservabilityCertificate(
        tolerance=float(tolerance), families=tuple(certificates), decision=decision,
        fitted_family_names=fitted, excluded_family_names=excluded,
        sensitive_family_names=sensitive, whitening_rank=rank,
    )
