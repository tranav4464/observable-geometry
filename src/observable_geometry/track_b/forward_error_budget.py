"""Conservative source-decision sensitivity to a bounded forward error.

The bound is standard triangle-inequality reasoning. It is not a calibrated
head-model uncertainty estimate or a new inverse method.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ForwardErrorRadius:
    """A sufficient open radius for preserving opposite decisions.

    A column error of at most ``epsilon`` is measured in whitened scalp norm
    per normalized source unit. All target source maps have L1 norm at most
    ``target_l1``; all admissible alternatives have L1 norm at most
    ``alternative_l1``. This permits arbitrary correlated or independent
    perturbations to each forward column, including the target columns.
    """

    epsilon_supremum: float
    excluded_margin: float
    feasible_margin: float
    total_source_l1: float


def certified_opposite_decision_radius(
    feasible_upper: float,
    excluded_lower: float,
    tolerance: float,
    target_l1: float,
    alternative_l1: float,
) -> ForwardErrorRadius:
    """Return a sufficient per-column error radius for a decision reversal.

    Every modeled residual changes by at most
    ``epsilon * (target_l1 + alternative_l1)``. The exclusion is certified
    only for epsilon strictly smaller than the returned supremum; feasibility
    may include equality. This follows from norm triangle inequalities and a
    uniform L1 budget, without assuming a distribution for forward error.
    """
    values = (feasible_upper, excluded_lower, tolerance, target_l1, alternative_l1)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("all inputs must be finite")
    if min(values) < 0 or target_l1 + alternative_l1 <= 0:
        raise ValueError("nonnegative residuals, tolerance and positive mass required")
    fm = tolerance - feasible_upper
    em = excluded_lower - tolerance
    if fm < 0 or em <= 0:
        raise ValueError("input certificates do not prove opposite decisions")
    total = target_l1 + alternative_l1
    return ForwardErrorRadius(min(fm, em) / total, em, fm, total)


def perturbed_certificate_envelopes(
    feasible_upper: float,
    excluded_lower: float,
    column_error: float,
    target_l1: float,
    alternative_l1: float,
) -> tuple[float, float]:
    """Return worst-case (feasible upper, excluded lower) certificates."""
    values = (feasible_upper, excluded_lower, column_error, target_l1, alternative_l1)
    if not all(math.isfinite(value) and value >= 0 for value in values):
        raise ValueError("finite nonnegative inputs required")
    drift = column_error * (target_l1 + alternative_l1)
    return feasible_upper + drift, max(0.0, excluded_lower - drift)
