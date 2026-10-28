"""Three-valued source-attribution audit across a declared forward-model set.

The mathematics is a triangle-inequality certificate and an in-set
counterexample, not a new inverse algorithm or calibrated probability.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class EndpointChallenge:
    name: str
    parameter_value: float
    target_residual_lower: float
    alternative_residual_upper: float | None = None


@dataclass(frozen=True)
class RobustAuditInput:
    parameter_interval: tuple[float, float]
    tolerance: float
    anchor_target_residual_upper: float
    anchor_alternative_residual_lower: float
    anchor_alternative_residual_upper: float
    target_amplitude_abs_upper: float
    alternative_l1_budget: float
    target_column_radius: float
    alternative_column_radius_upper: float
    endpoints: tuple[EndpointChallenge, ...]


@dataclass(frozen=True)
class RobustAuditResult:
    anchor_decision: str
    interval_decision: str
    target_residual_upper_over_interval: float
    alternative_residual_lower_over_interval: float
    refuting_scenarios: tuple[str, ...]
    reason: str


def audit_robust_attribution(spec: RobustAuditInput) -> RobustAuditResult:
    """Certify, refute, or leave unresolved a target-only fit over an interval.

    The observed field is fixed. A target amplitude witness at the anchor can
    be reused at every model. Alternative coefficients have an L1 budget.
    The supplied radii must enclose every candidate column in the declared
    forward-model set, in the same whitened sensor norm and source units.
    Endpoint lower/upper certificates must be established separately.
    """
    values=(spec.tolerance,spec.anchor_target_residual_upper,
            spec.anchor_alternative_residual_lower,
            spec.anchor_alternative_residual_upper,
            spec.target_amplitude_abs_upper,spec.alternative_l1_budget,
            spec.target_column_radius,spec.alternative_column_radius_upper)
    if any(not math.isfinite(x) or x<0 for x in values):
        raise ValueError("audit quantities must be finite and nonnegative")
    if len(spec.parameter_interval)!=2 or any(not math.isfinite(x) for x in spec.parameter_interval):
        raise ValueError("finite parameter interval required")
    parameter_lo,parameter_hi=spec.parameter_interval
    if parameter_lo>parameter_hi:
        raise ValueError("parameter interval must be ordered")
    if spec.anchor_alternative_residual_lower>spec.anchor_alternative_residual_upper:
        raise ValueError("alternative residual certificate is inverted")
    if not spec.endpoints or len({x.name for x in spec.endpoints})!=len(spec.endpoints):
        raise ValueError("distinct in-set challenge scenarios are required")
    for endpoint in spec.endpoints:
        if (not endpoint.name or not math.isfinite(endpoint.parameter_value) or
            not parameter_lo<=endpoint.parameter_value<=parameter_hi):
            raise ValueError("challenge scenario is not within the declared parameter interval")
        if not math.isfinite(endpoint.target_residual_lower) or endpoint.target_residual_lower<0:
            raise ValueError("invalid endpoint target lower bound")
        if endpoint.alternative_residual_upper is not None and (
            not math.isfinite(endpoint.alternative_residual_upper) or
            endpoint.alternative_residual_upper<0
        ):
            raise ValueError("invalid endpoint alternative upper bound")
    tau=spec.tolerance
    target_fits=spec.anchor_target_residual_upper<=tau
    alt_excluded=spec.anchor_alternative_residual_lower>tau
    alt_fits=spec.anchor_alternative_residual_upper<=tau
    anchor=("target_only_fits" if target_fits and alt_excluded else
            "ambiguous_both_fit" if target_fits and alt_fits else
            "alternative_only_fits" if not target_fits and alt_fits else
            "neither_fits" if not target_fits and alt_excluded else
            "unresolved")
    target_upper=(spec.anchor_target_residual_upper+
                  spec.target_amplitude_abs_upper*spec.target_column_radius)
    alt_lower=max(0.0,spec.anchor_alternative_residual_lower-
                  spec.alternative_l1_budget*spec.alternative_column_radius_upper)
    refuted=tuple(x.name for x in spec.endpoints if
                  x.target_residual_lower>tau or
                  (x.alternative_residual_upper is not None and x.alternative_residual_upper<=tau))
    if refuted:
        interval="refuted_by_in_set_scenario"
        reason="At least one declared in-set scenario contradicts target-only fit."
    elif target_upper<=tau and alt_lower>tau:
        interval="certified_target_only"
        reason="One target witness fits and every bounded alternative is excluded throughout the set."
    else:
        interval="unresolved"
        reason="Available radius and scenario checks do not settle the universal claim."
    return RobustAuditResult(anchor,interval,target_upper,alt_lower,refuted,reason)
