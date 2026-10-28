"""Behavioral and independent mathematical checks for the two-sided audit."""
import itertools

import numpy as np
import pytest
from scipy.optimize import linprog

from observable_geometry.track_b.two_sided_audit import (
    CappedBranch, audit_model, capped_support, certify_branch,
)


def test_capped_support_matches_independent_linear_program():
    scores = np.array([3.0, -2.0, 1.5, 2.0])
    caps = np.array([0.3, 1.0, 0.8, 0.2])
    budget = 0.9
    reference = linprog(-scores, A_ub=np.ones((1, 4)), b_ub=[budget],
                        bounds=list(zip(np.zeros(4), caps)), method="highs")
    assert reference.success
    assert capped_support(scores, caps, budget) == pytest.approx(-reference.fun, abs=1e-12)


def test_branch_certificate_bounds_bruteforce_continuous_minimum():
    y = np.array([0.7, 0.3])
    branch = CappedBranch("two-atoms", np.eye(2), np.array([0.4, 0.4]), 0.6)
    cert = certify_branch(y, branch)
    # The optimum is w=(0.4, 0.2); independently inspect a dense feasible grid.
    grid = np.linspace(0, 0.4, 401)
    brute = min(np.linalg.norm(y - np.array([a, b]))
                for a, b in itertools.product(grid, repeat=2) if a + b <= 0.60000001)
    assert cert.lower <= brute + 1e-10
    assert cert.upper >= brute - 1e-10
    assert cert.upper - cert.lower < 1e-6
    assert cert.weights.sum() <= branch.budget + 1e-12
    assert np.all(cert.weights <= branch.caps + 1e-12)


@pytest.mark.parametrize("y,target,alternative,expected", [
    ([1., 0.], [1., 0.], [0., 1.], "target_only_fits"),
    ([1., 0.], [1., 0.], [1., 0.], "ambiguous_both_fit"),
    ([0., 1.], [1., 0.], [0., 1.], "alternative_only_fits"),
    ([1., 1.], [1., 0.], [0., 1.], "neither_fits_abstain"),
])
def test_four_states(y, target, alternative, expected):
    branch = CappedBranch("competitor", np.asarray(alternative)[:, None],
                          np.array([1.0]), 1.0)
    result = audit_model(np.asarray(y), np.asarray(target), (0.0, 1.0),
                         (branch,), 0.25, model_name="toy")
    assert result.decision == expected


def test_incomplete_dual_proof_stays_unresolved(monkeypatch):
    from observable_geometry.track_b import two_sided_audit as module
    from observable_geometry.track_b.two_sided_audit import BranchCertificate

    def loose(_y, branch):
        return BranchCertificate(branch.name, 0.0, 2.0, np.array([0.0]),
                                 np.array([1.0]), False, "budget exhausted")

    monkeypatch.setattr(module, "certify_branch", loose)
    branch = CappedBranch("competitor", np.array([[1.0]]), np.array([1.0]), 1.0)
    result = audit_model(np.array([1.0]), np.array([1.0]), (0.0, 1.0),
                         (branch,), 0.5, model_name="toy")
    assert result.decision == "unresolved_alternative_bounds"
