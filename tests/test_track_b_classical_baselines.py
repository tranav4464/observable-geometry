import math
import unittest

import numpy as np

from observable_geometry.track_b.classical_baselines import gaussian_ideal_observer


class GaussianIdealObserverTests(unittest.TestCase):
    def test_matches_closed_form_mahalanobis_and_error(self):
        result = gaussian_ideal_observer([2.0, 1.0], [0.0, 0.0], np.diag([4.0, 1.0]))
        self.assertAlmostEqual(result["squared_mahalanobis_distance"], 2.0)
        self.assertAlmostEqual(result["mahalanobis_distance"], math.sqrt(2.0))
        self.assertAlmostEqual(
            result["equal_prior_single_observation_bayes_error"],
            0.5 * math.erfc(0.5))

    def test_supports_average_reference_rank_deficiency(self):
        covariance = np.array([[1.0, -1.0], [-1.0, 1.0]])
        result = gaussian_ideal_observer([1.0, -1.0], [0.0, 0.0], covariance)
        self.assertEqual(result["covariance_rank"], 1)
        self.assertAlmostEqual(result["squared_mahalanobis_distance"], 1.0)

    def test_rejects_mean_outside_noise_support(self):
        covariance = np.array([[1.0, -1.0], [-1.0, 1.0]])
        with self.assertRaisesRegex(ValueError, "outside covariance support"):
            gaussian_ideal_observer([1.0, 0.0], [0.0, 0.0], covariance)

    def test_rejects_invalid_covariance(self):
        with self.assertRaisesRegex(ValueError, "positive semidefinite"):
            gaussian_ideal_observer([1.0, 0.0], [0.0, 0.0], np.diag([1.0, -0.1]))


if __name__ == "__main__":
    unittest.main()
