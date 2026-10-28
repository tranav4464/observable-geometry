import pytest

from observable_geometry.track_b.stability import ResidualInterval, compare, validate_nesting


def test_band_contains_the_fixed_threshold_only_for_certified_flip():
    fine = ResidualInterval("target6103_pair0_point", "fine", .796138, .796139)
    coarse = ResidualInterval("target6103_pair0_point", "cps", 1.278934, 1.278935)
    result = compare(fine, coarse, 1.0)
    assert result["status"] == "certified_disagreement"
    assert result["bands"] == [dict(feasible_model="fine", excluded_model="cps",
                                    start_inclusive=.796139, stop_exclusive=1.278934)]
    assert compare(fine, coarse, .796139)["status"] == "certified_disagreement"
    assert compare(fine, coarse, 1.278934)["status"] != "certified_disagreement"


def test_negative_control_can_disagree_at_a_different_threshold():
    # Both exclude at the registered tolerance of one. That does not mean their
    # decisions agree at every tolerance, and absence of a band means unknown.
    fine = ResidualInterval("heldout_target1890", "fine", 3.879411, 3.879413)
    coarse = ResidualInterval("heldout_target1890", "cps", 4.236735, 4.236737)
    assert compare(fine, coarse, 1)["status"] == "both_excluded"
    assert compare(fine, coarse, 4)["status"] == "certified_disagreement"


def test_invalid_evidence_and_cross_target_comparisons_rejected():
    with pytest.raises(ValueError):
        ResidualInterval("target", "model", float("nan"), 2)
    with pytest.raises(ValueError):
        ResidualInterval("target", "model", 2, 1)
    with pytest.raises(ValueError):
        compare(ResidualInterval("a", "fine", 0, 1),
                ResidualInterval("b", "cps", 2, 3), 1)


def test_nesting_detects_impossible_interval_order():
    large = ResidualInterval("same_target", "less_smooth", 2.0, 2.1)
    small = ResidualInterval("same_target", "more_smooth", .5, .6)
    with pytest.raises(ValueError, match="contradict"):
        validate_nesting(large, small)
