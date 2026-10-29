from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "track_b"))
from audit_wsgzp_electrode_mri_proximity import nearest_tissue_distances_mm


def test_proximity_uses_declared_world_coordinates_and_voxel_spacing():
    volume = np.zeros((20, 20, 20), dtype=np.uint8)
    volume[8:13, 8:13, 8:13] = 100
    affine = np.eye(4)
    points = np.array([[10.0, 10.0, 10.0], [15.0, 10.0, 10.0]])
    d = nearest_tissue_distances_mm(volume, affine, points, threshold=10, step=1)
    assert d[0] == pytest.approx(0)
    assert d[1] == pytest.approx(3)


def test_proximity_rejects_empty_tissue_mask():
    with pytest.raises(ValueError, match="No MRI voxels"):
        nearest_tissue_distances_mm(np.zeros((4, 4, 4)), np.eye(4), np.zeros((1, 3)))
