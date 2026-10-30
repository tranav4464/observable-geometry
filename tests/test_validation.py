import math
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import hashlib
import zipfile
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_foundation import (
    _is_vcs_metadata,
    _source_files,
    validate,
    validate_empirical_rows,
    validate_signature_arrays,
    verify_source_snapshot,
)
from geometry_basis_cache import _valid_basis


class FinalValidatorTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"GBFs_peak_error_mm": float(i + 1), "MNE_peak_error_mm": float(i + 2)}
            for i in range(6)
        ]
        self.summary = {
            "GBFs_median": 3.5, "GBFs_mean": 3.5,
            "MNE_median": 4.5, "MNE_mean": 4.5,
        }

    def test_rejects_nan_site_error(self):
        corrupt = [dict(row) for row in self.rows]
        corrupt[0]["GBFs_peak_error_mm"] = math.nan
        with self.assertRaisesRegex(ValueError, "must all be finite"):
            validate_empirical_rows(corrupt, self.summary)

    def test_rejects_summary_not_derived_from_site_errors(self):
        corrupt = dict(self.summary)
        corrupt["GBFs_median"] = 100.0
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate_empirical_rows(self.rows, corrupt)

    def test_rejects_negative_site_error(self):
        corrupt = [dict(row) for row in self.rows]
        corrupt[0]["GBFs_peak_error_mm"] = -1.0
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            validate_empirical_rows(corrupt, self.summary)

    def test_rejects_duplicate_site_identity(self):
        corrupt = [dict(row, condition=str(i)) for i, row in enumerate(self.rows)]
        corrupt[1]["condition"] = corrupt[0]["condition"]
        with self.assertRaisesRegex(ValueError, "identities must be unique"):
            validate_empirical_rows(corrupt, self.summary)

    def test_seal_rejects_existing_manifest_before_writing(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "run_manifest.json").write_text("sealed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fresh run ID"):
                validate(path, seal=True)
            self.assertFalse((path / "tracka_source_snapshot.zip").exists())

    def test_snapshot_inventory_contains_tests(self):
        self.assertIn(Path(__file__).resolve(), _source_files())

    def test_vcs_metadata_is_not_treated_as_scientific_input(self):
        self.assertTrue(_is_vcs_metadata("data/Localize-MI/.git/config"))
        self.assertTrue(_is_vcs_metadata(Path("data/Localize-MI/.git/objects/pack/example.pack")))
        self.assertFalse(_is_vcs_metadata("data/Localize-MI/dataset_description.json"))
        self.assertFalse(_is_vcs_metadata("data/payload/sub-01_epochs.npy"))

    def test_snapshot_content_is_checked_without_live_worktree(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "source.zip"
            original = b"print('ok')\n"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("tests/test_example.py", original)
            hashes = {"tests/test_example.py": hashlib.sha256(original).hexdigest()}
            verify_source_snapshot(path, hashes)
            wrong = {"tests/test_example.py": hashlib.sha256(b"altered").hexdigest()}
            with self.assertRaisesRegex(ValueError, "member hash mismatch"):
                verify_source_snapshot(path, wrong)

    def test_snapshot_rejects_missing_test_inventory(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "source.zip"
            content = b"code"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("src/example.py", content)
            hashes = {"src/example.py": hashlib.sha256(content).hexdigest()}
            with self.assertRaisesRegex(ValueError, "omits executable test"):
                verify_source_snapshot(path, hashes)

    def test_rejects_changed_frozen_similarity_threshold(self):
        z = {
            "source_coordinates": np.array([[0., 0., 0.]]),
            "valid_source": np.array([True]),
            "candidate_indices": np.full((1, 5), -1),
            "absolute_cosine": np.full((1, 5), np.nan),
            "raw_candidate_indices": np.full((1, 5), -1),
            "raw_absolute_cosine": np.full((1, 5), np.nan),
            "profiled_residual_at_unit_snr": np.full((1, 5), np.nan),
        }
        threshold = {"indptr": np.array([0, 0]), "indices": np.array([], dtype=int),
                     "absolute_cosine": np.array([]), "threshold": np.array(.5)}
        with self.assertRaisesRegex(ValueError, "Threshold ambiguity"):
            validate_signature_arrays(z, threshold, expected_count=1)

    def test_accepts_roundoff_zero_for_upstream_replaced_constant_mode(self):
        result = (np.array([-1e-17, .01]), np.array([2e-17, .02]),
                  np.ones((3, 2)), np.ones((4, 2)))
        self.assertTrue(_valid_basis(result, 2, 3, 4))

    def test_rejects_negative_nonconstant_eigenvalue(self):
        result = (np.array([0., -1e-6]), np.array([0., .02]),
                  np.ones((3, 2)), np.ones((4, 2)))
        self.assertFalse(_valid_basis(result, 2, 3, 4))


if __name__ == "__main__":
    unittest.main()
