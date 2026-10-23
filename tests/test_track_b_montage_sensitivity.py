import numpy as np
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "track_b"))
from montage_sensitivity import average_reference_subset


def test_subset_reference_removes_common_sensor_offset_and_projects_covariance():
    gain = np.array([[1.0, -2.0], [3.0, 4.0], [-1.0, 2.0], [5.0, 1.0]])
    base = np.array([[2.0, 0.3, 0.0, 0.0], [0.3, 1.5, 0.2, 0.0], [0.0, 0.2, 1.2, 0.1], [0.0, 0.0, 0.1, 0.8]])
    indices = np.array([0, 2, 3])
    common_gain_offset = np.array([[8.0, -3.0]])
    common_noise = 2.5 * np.ones((4, 4))

    projected_gain, projected_cov = average_reference_subset(gain, base, indices)
    shifted_gain, shifted_cov = average_reference_subset(gain + common_gain_offset, base + common_noise, indices)

    np.testing.assert_allclose(projected_gain, shifted_gain, atol=1e-14)
    np.testing.assert_allclose(projected_cov, shifted_cov, atol=1e-14)
    np.testing.assert_allclose(projected_gain.sum(axis=0), 0.0, atol=1e-14)
    np.testing.assert_allclose(projected_cov, projected_cov.T, atol=1e-14)
    assert np.linalg.eigvalsh(projected_cov).min() >= -1e-12


@pytest.mark.parametrize("indices", [np.array([0]), np.array([0, 0]), np.array([-1, 2]), np.array([0, 4])])
def test_subset_reference_rejects_invalid_indices(indices):
    gain = np.ones((4, 2))
    covariance = np.eye(4)
    with pytest.raises(ValueError):
        average_reference_subset(gain, covariance, indices)
