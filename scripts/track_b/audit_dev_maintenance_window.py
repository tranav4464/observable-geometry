"""Verify task-phase mapping using development BIDS event metadata only.

No EDF payloads, signal values, held-out participants, or generated signals are read.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEV_SUBJECTS = ("sub-01", "sub-02", "sub-03")
SAMPLE_RATES = {"eeg": 200, "ieeg": 2000}
EPOCH_SECONDS = 8.0
MAINTENANCE_LAST_TWO_SECONDS = (4.0, 6.0)
ANALYSIS_RATE = 50


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    pairs = []
    for subject in DEV_SUBJECTS:
        subject_dir = args.dataset_root / subject
        for eeg_events in sorted((subject_dir).glob("ses-*/eeg/*_events.tsv")):
            stem = eeg_events.name.removesuffix("_events.tsv")
            session = eeg_events.parent.parent.name
            ieeg_events = subject_dir / session / "ieeg" / f"{stem}_events.tsv"
            if not ieeg_events.is_file():
                continue
            modalities = {"eeg": read_rows(eeg_events), "ieeg": read_rows(ieeg_events)}
            if len(modalities["eeg"]) != len(modalities["ieeg"]):
                raise ValueError(f"paired event-row count differs: {eeg_events}")
            for modality, rows in modalities.items():
                fs = SAMPLE_RATES[modality]
                for i, row in enumerate(rows, 1):
                    beg, end = int(row["begSample"]), int(row["endSample"])
                    duration = float(row["duration"])
                    # BIDS events use a zero-based time origin; begSample is one-based.
                    span = (end - beg + 1) / fs
                    if abs(duration - EPOCH_SECONDS) > 1e-9 or abs(span - EPOCH_SECONDS) > 1e-9:
                        raise ValueError(f"unexpected event epoch: {eeg_events} row {i}")
                    if "nTrial" in row and int(row["nTrial"]) != i:
                        raise ValueError(f"trial order mismatch: {eeg_events} row {i}")
            pairs.append({
                "subject": subject,
                "session": session,
                "n_trials": len(modalities["eeg"]),
                "eeg_event_file": str(eeg_events),
                "ieeg_event_file": str(ieeg_events),
                "duration_seconds": EPOCH_SECONDS,
            })

    if len(pairs) != 14:
        raise ValueError(f"expected 14 authorized development pairs, found {len(pairs)}")

    start, stop = MAINTENANCE_LAST_TWO_SECONDS
    result = {
        "scope": "metadata-only event audit; development participants sub-01 through sub-03",
        "confirmation_data_accessed": False,
        "edf_payloads_read": False,
        "signals_read": False,
        "synthetic_data_created": False,
        "source_phase_timing_seconds_relative_to_probe": {
            "encoding": [-5.0, -3.0],
            "maintenance": [-3.0, 0.0],
            "probe_onset": 0.0,
        },
        "paired_epoch_probe_onset_seconds_from_epoch_start": 6.0,
        "candidate_window_seconds_from_zero_based_epoch_start": [start, stop],
        "candidate_interval_convention": "half-open",
        "sample_rate_hz": ANALYSIS_RATE,
        "sample_slice_zero_based": [int(start * ANALYSIS_RATE), int(stop * ANALYSIS_RATE)],
        "samples_per_trial": int((stop - start) * ANALYSIS_RATE),
        "pairs_verified": len(pairs),
        "trials_verified": sum(p["n_trials"] for p in pairs),
        "pairs": pairs,
        "interpretation": (
            "The source task timing and paired-epoch alignment place the final two seconds of "
            "maintenance at [4,6) s from epoch start. This establishes a candidate window only; "
            "it does not establish signal quality, sample-level phase alignment, model performance, "
            "statistical power, or novelty."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "pairs_verified", "trials_verified", "candidate_window_seconds_from_zero_based_epoch_start",
        "sample_slice_zero_based", "samples_per_trial", "edf_payloads_read", "confirmation_data_accessed"
    )}, indent=2))


if __name__ == "__main__":
    main()
