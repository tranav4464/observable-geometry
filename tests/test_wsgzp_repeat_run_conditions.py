import csv

from scripts.track_b.audit_wsgzp_repeat_run_conditions import audit


def write_epochs(path, condition, n):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["duration", "trial_type", "zero_time"],
            delimiter="\t",
        )
        writer.writeheader()
        for _ in range(n):
            writer.writerow({"duration": "1", "trial_type": condition, "zero_time": "0.3"})


def test_finds_same_condition_run_repeats_without_claiming_independence(tmp_path):
    root = tmp_path / "dataset"
    condition = "K'7-8 5ma 0.5ms 0.5hz parallel gr_wh"
    for run, eeg_n, ieeg_n in (("01", 37, 40), ("02", 36, 39)):
        stem = f"sub-14_task-ccepcoreg_run-{run}_epochs.tsv"
        write_epochs(root / "derivatives/epochs/sub-14/eeg" / stem, condition, eeg_n)
        write_epochs(root / "derivatives/epochs/sub-14/ieeg" / stem, condition, ieeg_n)

    result = audit(root)

    assert result["epoch_tsv_run_pair_count"] == 2
    assert result["run_pairs_with_identical_eeg_ieeg_condition_sets"] == 2
    assert result["same_participant_exact_condition_repeat_pair_count"] == 1
    assert result["participants_with_exact_condition_repeats"] == ["sub-14"]
    repeat = result["repeat_pairs"][0]
    assert repeat["eeg_epochs_a_b"] == [37, 36]
    assert repeat["ieeg_epochs_a_b"] == [40, 39]
    assert repeat["independent_acquisition_confirmed"] is False
    assert result["signal_samples_read"] is False
    assert "sequential within-subject counter" in result["run_id_semantics"]
    assert "not included" in result["run_id_semantics"]
    assert len(result["run_id_semantics_sources"]) == 2


def test_does_not_count_eeg_ieeg_condition_mismatch_as_a_repeat(tmp_path):
    root = tmp_path / "dataset"
    for run in ("01", "02"):
        eeg_condition = f"stim-A-{run}"
        ieeg_condition = "stim-A" if run == "01" else "stim-B"
        stem = f"sub-01_task-ccepcoreg_run-{run}_epochs.tsv"
        write_epochs(root / "derivatives/epochs/sub-01/eeg" / stem, eeg_condition, 2)
        write_epochs(root / "derivatives/epochs/sub-01/ieeg" / stem, ieeg_condition, 2)

    result = audit(root)

    assert result["run_pairs_with_identical_eeg_ieeg_condition_sets"] == 0
    assert result["same_participant_exact_condition_repeat_pair_count"] == 0
