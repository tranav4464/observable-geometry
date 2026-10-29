"""Exploratory linear-span screen for measured-field source hypotheses.

This module profiles unrestricted linear least-squares spans. That is only a
relaxation of any coefficient-constrained source family: its residual is a
lower bound on the constrained family's best residual. A low span residual
means only "not excluded by this relaxation"; it does not prove a physically
admissible source fit. A high computed float64 residual for every supplied
variant is not a certified exclusion because this module does not bound
numerical error. Finite variants do not provide a continuous
forward-uncertainty bound. This module cannot decide spatial uniqueness or
ambiguity because it receives no spatial supports and does not certify
coverage of all admissible explanations.

No neural signal is generated here.  Synthetic/algebraic inputs belong only in
unit tests and must never be used for calibration or the primary result.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class FamilySpanResult:
    """Uncertified float64 span residual screen for a source family."""

    name: str
    residuals: tuple[float, ...]
    minimum_span_residual: float
    maximum_span_residual: float
    best_variant: int
    status: str
    exclusion_certified: bool = False


@dataclass(frozen=True)
class FamilySpanScreen:
    """Finite tested-family float64 screen, not a spatial certificate."""

    tolerance: float
    families: tuple[FamilySpanResult, ...]
    summary: str
    within_tolerance_family_names: tuple[str, ...]
    above_tolerance_family_names: tuple[str, ...]
    whitening_rank: int | None
    numerical_certification: str = "uncertified_float64_residuals"


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
    if (
        not np.isfinite(eigenvalue_rtol)
        or eigenvalue_rtol < 0.0
        or eigenvalue_rtol >= 1.0
    ):
        raise ValueError("eigenvalue_rtol must be finite and in [0, 1)")
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


def screen_family_spans(
    field: np.ndarray,
    family_variants: Mapping[str, Sequence[np.ndarray]],
    *,
    tolerance: float,
    noise_covariance: np.ndarray | None = None,
) -> FamilySpanScreen:
    """Screen whether each family is excluded by unrestricted LS spans.

    ``family_variants[name]`` contains one or more candidate design matrices.
    Each variant corresponds to a fixed point in a finite tested forward-model
    set. Least squares permits arbitrary signed coefficients and ignores source
    moment/support constraints. Its residual is therefore a lower bound for a
    source family contained in the supplied span. A family is marked
    ``above_tolerance_for_all_tested_variants`` records only that the computed
    float64 residual exceeded ``tolerance`` for every tested span. It is not a
    certified exclusion: floating-point least squares can err in either
    direction, and no residual error bound is computed here. The other status,
    ``within_tolerance_for_at_least_one_tested_variant``, likewise does not
    prove a feasible family member, physiological plausibility, or spatial
    ambiguity. This routine never issues ``unique_enough`` or a certified
    family exclusion.
    """
    y = np.asarray(field, dtype=np.float64)
    if y.ndim != 1 or y.size < 1 or not np.isfinite(y).all():
        raise ValueError("field must be a finite, nonempty vector")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    if not family_variants:
        raise ValueError("at least one source family is required")
    results: list[FamilySpanResult] = []
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
        status = (
            "above_tolerance_for_all_tested_variants"
            if lower > tolerance
            else "within_tolerance_for_at_least_one_tested_variant"
        )
        results.append(FamilySpanResult(
            name=str(name), residuals=tuple(residuals),
            minimum_span_residual=lower, maximum_span_residual=upper,
            best_variant=int(np.argmin(residuals)), status=status,
            exclusion_certified=False,
        ))
    within_tolerance = tuple(
        c.name for c in results
        if c.status == "within_tolerance_for_at_least_one_tested_variant"
    )
    above_tolerance = tuple(
        c.name for c in results
        if c.status == "above_tolerance_for_all_tested_variants"
    )
    summary = (
        "all_tested_float64_span_residuals_above_tolerance"
        if not within_tolerance
        else "one_or_more_float64_span_residuals_within_tolerance"
    )
    return FamilySpanScreen(
        tolerance=float(tolerance), families=tuple(results), summary=summary,
        within_tolerance_family_names=within_tolerance,
        above_tolerance_family_names=above_tolerance,
        whitening_rank=rank,
    )
