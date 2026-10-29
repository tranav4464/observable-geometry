import json
import tempfile
import unittest
from pathlib import Path

from scripts.track_b.build_wsgzp_participant_fold_manifest import build_manifest
from scripts.track_b.verify_wsgzp_participant_fold_manifest import verify


def make_fixture(tmp_path: Path):
    root = tmp_path / "dataset"
    (root / "derivatives" / "epochs" / "sub-01" / "eeg").mkdir(parents=True)
    (root / "derivatives" / "epochs" / "sub-02" / "eeg").mkdir(parents=True)
    (root / "participants.tsv").write_text(
        "participant_id\tage\nsub-01\t30\nsub-02\t40\n", encoding="utf-8"
    )
    (root / "dataset_description.json").write_text("{}", encoding="utf-8")
    (root / "LICENSE").write_text("test license", encoding="utf-8")
    download = tmp_path / "download.json"
    download.write_text("{}", encoding="utf-8")
    for participant, run in (("sub-01", "01"), ("sub-01", "02"), ("sub-02", "01")):
        path = root / "derivatives" / "epochs" / participant / "eeg" / f"{participant}_task-test_run-{run}_epochs.tsv"
        path.write_text(
            "duration\tzero_time\ttrial_type\n1.0\t0.3\tstim-A\n1.0\t0.3\tstim-A\n",
            encoding="utf-8",
        )
    return root, download


class ParticipantFoldManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp_path = Path(self.temp.name)

    def test_grouped_manifest_holds_all_runs_by_participant(self):
        root, download = make_fixture(self.tmp_path)
        manifest = build_manifest(root, download)
        manifest_path = self.tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        result = verify(root, download, manifest_path)

        self.assertEqual(result["status"], "PASS_METADATA_ONLY")
        self.assertFalse(result["signal_samples_read"])
        self.assertEqual(result["participants_verified"], 2)
        self.assertEqual(result["run_tables_verified"], 3)
        fold = next(item for item in manifest["outer_folds"]
                    if item["heldout_participants"] == ["sub-01"])
        self.assertEqual(len(fold["heldout_runs"]), 2)
        self.assertNotIn("partition_indices_zero_based", manifest["run_tables"][0])

    def test_verifier_rejects_a_run_removed_from_heldout_participant(self):
        root, download = make_fixture(self.tmp_path)
        manifest = build_manifest(root, download)
        manifest["outer_folds"][0]["heldout_runs"].pop()
        manifest_path = self.tmp_path / "tampered.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        result = verify(root, download, manifest_path)

        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Outer fold assignment" in error for error in result["errors"]))
