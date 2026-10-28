"""Conditional, two-sided source-family fit audit for a fixed whitened field.

All sensor vectors must already use the same reference and noise whitening.
This is finite-union constrained least squares with ordinary weak dual bounds;
neither the mathematics nor a fit state is a calibrated source probability.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np
from scipy.optimize import minimize


@dataclass(frozen=True)
class CappedBranch:
    """One convex alternative: A @ w, 0 <= w <= caps, sum(w) <= budget.

    Signed source polarity belongs in the columns of ``atoms``. Separate
    polarity/patch possibilities must be passed as separate branches.
    """

    name: str
    atoms: np.ndarray
    caps: np.ndarray
    budget: float


@dataclass(frozen=True)
class BranchCertificate:
    name: str
    lower: float
    upper: float
    weights: np.ndarray
    dual_direction: np.ndarray
    solver_success: bool
    solver_message: str


@dataclass(frozen=True)
class ModelAudit:
    model_name: str
    target_amplitude: float
    target_residual: float
    alternative_lower: float
    alternative_upper: float
    decision: str
    branches: tuple[BranchCertificate, ...]


def capped_support(scores: np.ndarray, caps: np.ndarray, budget: float) -> float:
    """Support of a capped nonnegative L1 ball, by the fractional-knapsack rule."""
    s = np.asarray(scores, dtype=np.float64)
    c = np.asarray(caps, dtype=np.float64)
    if s.ndim != 1 or c.shape != s.shape or not np.isfinite(s).all():
        raise ValueError("scores and caps must be finite matching vectors")
    if not np.isfinite(c).all() or (c < 0).any() or not isfinite(budget) or budget < 0:
        raise ValueError("caps and budget must be finite and nonnegative")
    remaining = float(budget)
    value = 0.0
    for index in np.argsort(-s, kind="stable"):
        if s[index] <= 0 or remaining <= 0:
            break
        amount = min(float(c[index]), remaining)
        value += float(s[index]) * amount
        remaining -= amount
    return value


def _check_vector(value: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.isfinite(array).all():
        raise ValueError(f"{name} must be a finite nonempty vector")
    return array


def certify_branch(y: np.ndarray, branch: CappedBranch) -> BranchCertificate:
    """Return a feasible fit and an independently checkable weak-dual bound.

    A failed optimizer never yields a false positive certificate: the feasible
    witness and the dual direction remain valid, although the gap may widen.
    """
    field = _check_vector(y, "field")
    matrix = np.asarray(branch.atoms, dtype=np.float64)
    caps = np.asarray(branch.caps, dtype=np.float64)
    if not branch.name or matrix.ndim != 2 or matrix.shape[0] != field.size or matrix.shape[1] == 0:
        raise ValueError("branch name and atom matrix dimensions are required")
    if not np.isfinite(matrix).all() or caps.shape != (matrix.shape[1],):
        raise ValueError("branch atoms/caps have invalid shape or nonfinite values")
    if not np.isfinite(caps).all() or (caps < 0).any() or not isfinite(branch.budget) or branch.budget < 0:
        raise ValueError("caps and budget must be finite and nonnegative")

    gram = matrix.T @ matrix
    linear = matrix.T @ field
    fit = minimize(
        lambda w: float(0.5 * w @ gram @ w - linear @ w),
        np.zeros(matrix.shape[1]),
        jac=lambda w: gram @ w - linear,
        method="SLSQP",
        bounds=[(0.0, float(x)) for x in caps],
        constraints=[{"type": "ineq", "fun": lambda w: branch.budget - np.sum(w),
                      "jac": lambda w: -np.ones_like(w)}],
        options={"ftol": 1e-12, "maxiter": 500},
    )
    # Repair numerical constraint overshoot before calling the point feasible.
    weights = np.clip(np.asarray(fit.x, dtype=np.float64), 0.0, caps)
    if not np.isfinite(weights).all():
        raise ArithmeticError("optimizer returned nonfinite weights")
    mass = float(weights.sum())
    if mass > branch.budget:
        weights *= branch.budget / mass
    residual = field - matrix @ weights
    upper = float(np.linalg.norm(residual))
    if upper > 0:
        direction = residual / upper
        lower = max(0.0, float(direction @ field - capped_support(direction @ matrix, caps, branch.budget)))
    else:
        direction = np.zeros_like(field)
        lower = 0.0
    if lower > upper + 1e-8 * max(1.0, upper):
        raise ArithmeticError("dual bound exceeds feasible residual")
    return BranchCertificate(branch.name, lower, upper, weights, direction,
                             bool(fit.success), str(fit.message))


def audit_model(
    y: np.ndarray,
    target_atom: np.ndarray,
    target_amplitude_interval: tuple[float, float],
    alternative_branches: tuple[CappedBranch, ...],
    tolerance: float,
    *,
    model_name: str,
) -> ModelAudit:
    """Classify a fixed field against the favored and alternative families.

    ``target_atom`` is one whitened forward signature at unit amplitude. The
    target family is an amplitude interval along that atom. A branch lower
    above tolerance proves exclusion; a feasible upper at/below tolerance
    proves inclusion. Otherwise the result is unresolved, not forced.
    """
    field = _check_vector(y, "field")
    atom = _check_vector(target_atom, "target atom")
    if atom.shape != field.shape or not model_name:
        raise ValueError("target atom must match field and model name is required")
    if not isinstance(target_amplitude_interval, tuple) or len(target_amplitude_interval) != 2:
        raise ValueError("target amplitude interval must be a pair")
    lo, hi = target_amplitude_interval
    if not isfinite(lo) or not isfinite(hi) or lo > hi or not isfinite(tolerance) or tolerance < 0:
        raise ValueError("amplitude interval and tolerance must be finite and ordered")
    if not alternative_branches or len({b.name for b in alternative_branches}) != len(alternative_branches):
        raise ValueError("at least one uniquely named alternative branch is required")
    atom_norm2 = float(atom @ atom)
    alpha = float(np.clip((atom @ field) / atom_norm2, lo, hi)) if atom_norm2 > 0 else float(lo)
    target_residual = float(np.linalg.norm(field - alpha * atom))
    records = tuple(certify_branch(field, b) for b in alternative_branches)
    alt_lower = min(r.lower for r in records)
    alt_upper = min(r.upper for r in records)

    target_fits = target_residual <= tolerance
    if alt_upper <= tolerance:
        decision = "ambiguous_both_fit" if target_fits else "alternative_only_fits"
    elif alt_lower > tolerance:
        decision = "target_only_fits" if target_fits else "neither_fits_abstain"
    else:
        decision = "unresolved_alternative_bounds"
    return ModelAudit(model_name, alpha, target_residual, alt_lower, alt_upper,
                      decision, records)
