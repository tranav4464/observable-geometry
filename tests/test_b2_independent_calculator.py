"""Analytical checks for the independent B2 verifier; no neural data used."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "track_b" / "recompute_b2_gbf_cpu64.py"
SPEC = importlib.util.spec_from_file_location("b2_cpu64_verifier_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class IndependentB2CalculatorTests(unittest.TestCase):
    def setUp(self):
        # Exact algebraic signatures, not simulated or recorded EEG.
        self.leadfield = np.array([[1.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        self.covariance = np.eye(2, dtype=np.float64)
        self.coordinates = np.array(
            [[0.0, 0.0, 0.0], [0.03, 0.0, 0.0], [0.06, 0.0, 0.0]],
            dtype=np.float64,
        )

    def test_exact_duplicate_patterns_rank_first_and_return_float64(self):
        result = VERIFIER.independent_scores(
            self.leadfield, self.covariance, self.coordinates
        )
        self.assertEqual(result["indices"][0, 0], 1)
        self.assertEqual(result["indices"][1, 0], 0)
        self.assertEqual(float(result["scores"][0, 0]), 1.0)
        self.assertEqual(result["scores"].dtype, np.float64)
        self.assertEqual(result["counts"].tolist(), [2, 2, 2])

    def test_orthogonal_patterns_have_zero_cosine_and_source_index_tie_break(self):
        result = VERIFIER.independent_scores(
            self.leadfield, self.covariance, self.coordinates
        )
        self.assertEqual(result["indices"][2, :2].tolist(), [0, 1])
        np.testing.assert_allclose(result["scores"][2, :2], [0.0, 0.0], atol=0.0)

    def test_global_covariance_scale_preserves_normalized_scores(self):
        baseline = VERIFIER.independent_scores(
            self.leadfield, self.covariance, self.coordinates
        )
        scaled = VERIFIER.independent_scores(
            self.leadfield, self.covariance / 38.0, self.coordinates
        )
        np.testing.assert_array_equal(baseline["indices"], scaled["indices"])
        np.testing.assert_array_equal(baseline["valid"], scaled["valid"])
        np.testing.assert_allclose(
            baseline["scores"], scaled["scores"], rtol=1e-13, atol=1e-13,
            equal_nan=True,
        )

    def test_signal_outside_noise_support_is_rejected(self):
        singular_covariance = np.diag([1.0, 0.0])
        leadfield = np.array([[1.0, 1.0], [0.0, 1.0]])
        coordinates = np.array([[0.0, 0.0, 0.0], [0.03, 0.0, 0.0]])
        with self.assertRaisesRegex(ValueError, "outside covariance support"):
            VERIFIER.independent_scores(leadfield, singular_covariance, coordinates)


if __name__ == "__main__":
    unittest.main()
