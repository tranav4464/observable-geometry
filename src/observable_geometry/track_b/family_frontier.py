"""Threshold-free comparison of supplied source-family distance certificates.

This is interval bookkeeping over already computed fits, not a new source
inverse, a new statistical test, or a check that the supplied bounds are true.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class DistanceInterval:
    lower: float
    upper: float

    def __post_init__(self) -> None:
        if not (isfinite(self.lower) and isfinite(self.upper)):
            raise ValueError("distance bounds must be finite")
        if self.lower < 0 or self.upper < self.lower:
            raise ValueError("distance interval must be nonnegative and ordered")

    def status(self, tolerance: float) -> str:
        if not isfinite(tolerance) or tolerance < 0:
            raise ValueError("tolerance must be finite and nonnegative")
        if self.upper <= tolerance:
            return "fits"
        if self.lower > tolerance:
            return "excluded"
        return "unresolved"


@dataclass(frozen=True)
class FamilyComparison:
    name: str
    distance: DistanceInterval
    evidence: str

    def __post_init__(self) -> None:
        if (not isinstance(self.name, str) or not self.name.strip() or
                not isinstance(self.evidence, str) or not self.evidence.strip()):
            raise ValueError("family name and evidence label are required")


def compare_families(
    reference: FamilyComparison,
    alternatives: tuple[FamilyComparison, ...],
    tolerance: float,
) -> dict:
    """Find tolerance intervals where a reference exclusion is refuted.

    The returned half-open [lower, upper) window follows only if
    input lower/upper bounds are valid. It is not a population error guarantee.
    Families may differ in patch count and are never assumed nested.
    """
    if not alternatives:
        raise ValueError("at least one alternative family is required")
    names = (reference.name,) + tuple(x.name for x in alternatives)
    if len(names) != len(set(names)):
        raise ValueError("family names must be distinct")
    reference_status = reference.distance.status(tolerance)
    rows = []
    for alternative in alternatives:
        status = alternative.distance.status(tolerance)
        reversal_start = alternative.distance.upper
        reversal_end = reference.distance.lower
        window = (
            {"lower_inclusive": reversal_start, "upper_exclusive": reversal_end}
            if reversal_start < reversal_end else None
        )
        rows.append({
            "name": alternative.name,
            "distance": {"lower": alternative.distance.lower, "upper": alternative.distance.upper},
            "evidence": alternative.evidence,
            "status_at_tolerance": status,
            "reference_excluded_alternative_fits": reference_status == "excluded" and status == "fits",
            "bound_implied_reversal_tolerance_window": window,
        })
    return {
        "reference": {
            "name": reference.name,
            "distance": {"lower": reference.distance.lower, "upper": reference.distance.upper},
            "evidence": reference.evidence,
            "status_at_tolerance": reference_status,
        },
        "tolerance": tolerance,
        "alternatives": rows,
        "claim_boundary": (
            "Conditional on supplied distance bounds and declared source families. "
            "A reversal means an alternative fit refutes a reference-family exclusion "
            "at the stated tolerance; it does not identify a physiological source "
            "or calibrate a composite-classifier error."
        ),
    }
