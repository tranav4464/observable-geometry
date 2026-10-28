"""Decision semantics of a conditional interval attribution audit."""
from dataclasses import replace
import json

import pytest

from observable_geometry.track_b.robust_attribution import (
    EndpointChallenge, RobustAuditInput, audit_robust_attribution,
)
from observable_geometry.cli import main


def example() -> RobustAuditInput:
    return RobustAuditInput(
        parameter_interval=(0.006,0.012),
        tolerance=1.0,
        anchor_target_residual_upper=0.5,
        anchor_alternative_residual_lower=1.8,
        anchor_alternative_residual_upper=1.9,
        target_amplitude_abs_upper=1.0,
        alternative_l1_budget=2.0,
        target_column_radius=0.1,
        alternative_column_radius_upper=0.1,
        endpoints=(EndpointChallenge("held",0.01,0.3,1.7),),
    )


def test_universal_certificate_and_in_set_counterexample() -> None:
    supported=audit_robust_attribution(example())
    assert supported.anchor_decision=="target_only_fits"
    assert supported.interval_decision=="certified_target_only"
    assert supported.target_residual_upper_over_interval==pytest.approx(0.6)
    assert supported.alternative_residual_lower_over_interval==pytest.approx(1.6)

    # One genuine member of the declared model set is enough to disprove a
    # universal target-only statement, even with a hopelessly loose radius.
    refuted=audit_robust_attribution(replace(
        example(),target_column_radius=100.0,alternative_column_radius_upper=100.0,
        endpoints=(EndpointChallenge("held",0.012,1.2,1.7),)))
    assert refuted.anchor_decision=="target_only_fits"
    assert refuted.interval_decision=="refuted_by_in_set_scenario"
    assert refuted.refuting_scenarios==("held",)


def test_unresolved_does_not_become_false_exclusion() -> None:
    result=audit_robust_attribution(replace(
        example(),alternative_column_radius_upper=0.5,
        endpoints=(EndpointChallenge("held",0.01,0.3,None),)))
    assert result.interval_decision=="unresolved"
    assert result.alternative_residual_lower_over_interval==pytest.approx(0.8)


def test_duplicate_scenario_and_inverted_certificate_rejected() -> None:
    with pytest.raises(ValueError):
        audit_robust_attribution(replace(example(),endpoints=(
            EndpointChallenge("same",0.01,0.3),EndpointChallenge("same",0.012,0.4))))
    with pytest.raises(ValueError):
        audit_robust_attribution(replace(example(),anchor_alternative_residual_lower=2.0))
    with pytest.raises(ValueError):
        audit_robust_attribution(replace(example(),endpoints=(EndpointChallenge("out",0.02,1.2),)))


def test_cli_discloses_that_supplied_bounds_were_not_replayed(tmp_path) -> None:
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps({
        "parameter_interval": [0.0, 1.0], "tolerance": 1.0,
        "anchor_target_residual_upper": 0.5,
        "anchor_alternative_residual_lower": 1.8,
        "anchor_alternative_residual_upper": 1.9,
        "target_amplitude_abs_upper": 1.0,
        "alternative_l1_budget": 2.0,
        "target_column_radius": 0.1,
        "alternative_column_radius_upper": 0.1,
        "endpoints": [{"name":"held","parameter_value":1.0,
                       "target_residual_lower":0.3,
                       "alternative_residual_upper":1.7}],
    }), encoding="utf-8")
    output = tmp_path / "run"
    assert main(["robust-audit", "--spec", str(spec_path), "--output", str(output)]) == 0
    report = json.loads((output / "result.json").read_text(encoding="utf-8"))
    assert report["result"]["interval_decision"] == "certified_target_only"
    assert report["input_evidence_status"] == "supplied_bounds_not_replayed_by_this_command"
