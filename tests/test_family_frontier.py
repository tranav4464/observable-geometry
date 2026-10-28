import pytest
import json

from observable_geometry.cli import main

from observable_geometry.track_b.family_frontier import (
    DistanceInterval, FamilyComparison, compare_families,
)


def family(name, lower, upper):
    return FamilyComparison(name, DistanceInterval(lower, upper), "independently replayed input")


def test_exact_reversal_window_and_endpoint_semantics():
    result = compare_families(
        family("distant point", 3.476688, 3.476688),
        (family("two-hop uniform patch", 2.958835, 2.958835),),
        3.289707,
    )
    row = result["alternatives"][0]
    assert result["reference"]["status_at_tolerance"] == "excluded"
    assert row["status_at_tolerance"] == "fits"
    assert row["reference_excluded_alternative_fits"]
    assert row["bound_implied_reversal_tolerance_window"] == {
        "lower_inclusive": 2.958835, "upper_exclusive": 3.476688,
    }
    assert DistanceInterval(2.958835, 2.958835).status(2.958835) == "fits"
    assert DistanceInterval(3.476688, 3.476688).status(3.476688) == "fits"


def test_one_feasible_witness_does_not_prove_exclusion():
    result = compare_families(
        family("point", 3.5, 3.5),
        (family("two-patch feasible witness", 0.0, 1.6),),
        1.0,
    )
    assert result["alternatives"][0]["status_at_tolerance"] == "unresolved"
    assert result["alternatives"][0]["bound_implied_reversal_tolerance_window"] == {
        "lower_inclusive": 1.6, "upper_exclusive": 3.5,
    }


def test_interval_ambiguity_and_invalid_inputs():
    result = compare_families(
        family("point", 3.0, 3.4),
        (family("patch", 2.0, 3.2),),
        3.1,
    )
    assert result["reference"]["status_at_tolerance"] == "unresolved"
    assert result["alternatives"][0]["status_at_tolerance"] == "unresolved"
    assert result["alternatives"][0]["bound_implied_reversal_tolerance_window"] is None
    with pytest.raises(ValueError):
        DistanceInterval(3.0, 2.0)
    with pytest.raises(ValueError):
        compare_families(family("same", 2, 2), (family("same", 1, 1),), 1)


def test_cli_preserves_unknown_lower_bound_and_refuses_overwrite(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({
        "tolerance": 2.0,
        "cases": [{
            "id": "case-1",
            "reference": {"name": "point", "distance": {"lower": 4, "upper": 4}, "evidence": "direct replay"},
            "alternatives": [{"name": "two-patch witness", "distance": {"lower": 0, "upper": 3},
                              "evidence": "feasible witness only"}],
        }],
    }), encoding="utf-8")
    output = tmp_path / "result"
    args = ["family-frontier", "--spec", str(spec), "--output", str(output)]
    assert main(args) == 0
    result = json.loads((output / "result.json").read_text(encoding="utf-8"))
    assert result["input_evidence_status"] == "supplied_distance_bounds_not_replayed_by_this_command"
    assert result["cases"][0]["alternatives"][0]["status_at_tolerance"] == "unresolved"
    assert main(args) == 2
