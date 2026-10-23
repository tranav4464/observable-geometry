import unittest

import numpy as np

from observable_geometry.track_b.physical import bipolar_line_quadrature, homogeneous_bipolar_signature


class HomogeneousBipolarTests(unittest.TestCase):
    def test_analytic_axis_and_contact_swap(self):
        sensors = np.array([[.03, 0, 0], [0, .03, 0]])
        contacts = np.array([[.005, 0, 0], [-.005, 0, 0]])
        result = homogeneous_bipolar_signature(sensors, contacts)
        self.assertAlmostEqual(result[0], 1 / .025 - 1 / .035)
        self.assertAlmostEqual(result[1], 0)
        np.testing.assert_allclose(
            homogeneous_bipolar_signature(sensors, contacts[::-1]), -result)

    def test_rejects_singularity_and_bad_coordinates(self):
        contacts = np.array([[0, 0, 0], [.01, 0, 0]])
        with self.assertRaises(ValueError):
            homogeneous_bipolar_signature(np.array([[.001, 0, 0]]), contacts)
        with self.assertRaises(ValueError):
            homogeneous_bipolar_signature(np.array([[float("nan"), 0, 0]]), contacts)

    def test_line_dipoles_reproduce_homogeneous_source_sink(self):
        sensors = np.array([[.03, 0, 0], [0, .03, 0], [.02, .01, .02]])
        contacts = np.array([[.005, 0, 0], [-.005, 0, 0]])
        positions, moments = bipolar_line_quadrature(contacts, 12)
        delta = sensors[:, None, :] - positions[None, :, :]
        dipole_potentials = np.einsum("snj,nj->s", delta / np.linalg.norm(delta, axis=2)[:, :, None] ** 3,
                                      moments)
        np.testing.assert_allclose(dipole_potentials,
                                   -homogeneous_bipolar_signature(sensors, contacts),
                                   rtol=1e-12, atol=1e-12)
        with self.assertRaises(ValueError):
            bipolar_line_quadrature(contacts, 0)
