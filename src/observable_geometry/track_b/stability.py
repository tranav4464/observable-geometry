"""Decision stability over verified residual intervals.

This is interval arithmetic over existing certificates, not a new source
inverse, uncertainty calibration, or evidence that source families are nested.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ResidualInterval:
    """Certified bounds on the minimum whitened residual for one source family."""

    context: str
    model: str
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if not self.context or not self.model:
            raise ValueError("context and model names are required")
        if not all(math.isfinite(x) for x in (self.lower, self.upper)):
            raise ValueError("residual bounds must be finite")
        if self.lower < 0 or self.upper < self.lower:
            raise ValueError("invalid residual interval")

    def decision(self, tolerance: float) -> str:
        if not math.isfinite(tolerance) or tolerance < 0:
            raise ValueError("tolerance must be finite and nonnegative")
        if self.upper <= tolerance:
            return "alternative_feasible"
        if self.lower > tolerance:
            return "alternative_excluded"
        return "unresolved"


@dataclass(frozen=True)
class DisagreementBand:
    feasible_model: str
    excluded_model: str
    start_inclusive: float
    stop_exclusive: float


def compare(first: ResidualInterval, second: ResidualInterval, tolerance: float) -> dict:
    """Certified status and all tolerance bands showing opposite decisions.

    For residuals r_i in [l_i,u_i], model i is feasible when tau >= u_i;
    model j is excluded when tau < l_j. Thus [u_i,l_j) is sufficient for a
    disagreement. Missing bands do not prove agreement or equal residuals.
    """
    if first.context != second.context or first.model == second.model:
        raise ValueError("comparison needs one common target/family context and distinct models")
    a, b = first.decision(tolerance), second.decision(tolerance)
    bands = []
    for feasible, excluded in ((first, second), (second, first)):
        if feasible.upper < excluded.lower:
            bands.append(DisagreementBand(feasible.model, excluded.model,
                                          feasible.upper, excluded.lower))
    status = ("certified_disagreement" if
              {a, b} == {"alternative_feasible", "alternative_excluded"} else
              "unresolved" if "unresolved" in (a, b) else
              "both_feasible" if a == "alternative_feasible" else "both_excluded")
    return {"context": first.context, "models": (first.model, second.model),
            "decisions": (a, b), "status": status,
            "bands": [band.__dict__ for band in bands]}


def validate_nesting(larger: ResidualInterval, smaller: ResidualInterval) -> None:
    """Check a necessary interval condition for a separately PROVEN inclusion.

    The caller must establish family(smaller) subset family(larger), same
    forward and target. Geometry switches have no automatic inclusion.
    """
    if larger.context != smaller.context or larger.model == smaller.model:
        raise ValueError("incompatible nesting claim")
    if larger.lower > smaller.upper + 1e-8:
        raise ValueError("certificates contradict declared source-family inclusion")
