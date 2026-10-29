from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "track_b"))
from audit_wsgzp_net_geometry import pairwise_shape_fit


def test_pairwise_shape_fit_is_invariant_to_rigid_pose():
    reference_m = np.array([
        [0.00, 0.00, 0.10], [0.04, 0.02, 0.08], [-0.05, 0.01, 0.07],
        [0.01, -0.06, 0.03], [0.00, 0.03, -0.08],
    ])
    angle = 0.7
    rotation = np.array([
        [np.cos(angle), -np.sin(angle), 0.0],
        [np.sin(angle), np.cos(angle), 0.0],
        [0.0, 0.0, 1.0],
    ])
    actual_mm = (1.07 * (reference_m @ rotation.T) + np.array([0.03, -0.02, 0.11])) * 1000
    result = pairwise_shape_fit(actual_mm, reference_m)
    assert result["isotropic_scale_actual_over_template"] == pytest.approx(1.07)
    assert result["pairwise_distance_correlation"] == pytest.approx(1.0)
    assert result["pairwise_distance_rmse_mm_after_scale"] < 1e-10


def test_pairwise_shape_fit_rejects_mismatched_shapes():
    with pytest.raises(ValueError, match="same N x 3"):
        pairwise_shape_fit(np.zeros((4, 3)), np.zeros((5, 3)))
