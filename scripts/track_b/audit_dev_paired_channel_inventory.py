"""Metadata-only paired EEG/iEEG channel inventory for development subjects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_dev_contact_stability import read_tsv


DEV_SUBJECTS = {"sub-01", "sub-02", "sub-03"}


def audit(dataset_root: Path) -> dict[str, Any]:
    dataset_root = dataset_root.resolve()
    result: dict[str, Any] = {
        "audit_type": "development_paired_channel_metadata_only",
        "development_subjects_only": sorted(DEV_SUBJECTS),
        "events_or_signal_files_read": False,
        "confirmation_participants_read": False,
        "participants": {},
    }
    for subject in sorted(DEV_SUBJECTS):
        subject_root = dataset_root / subject
        if not subject_root.is_dir():
            raise FileNotFoundError(subject_root)
        sessions: dict[str, Any] = {}
        for eeg_channels_path in sorted(subject_root.glob("ses-*/eeg/*_channels.tsv")):
            session = next(part for part in eeg_channels_path.parts if part.startswith("ses-"))
            eeg_json_path = eeg_channels_path.with_name(eeg_channels_path.name.replace("_channels.tsv", "_eeg.json"))
            ieeg_channels_path = dataset_root / subject / session / "ieeg" / eeg_channels_path.name.replace("_eeg_", "_ieeg_")
            if not eeg_json_path.is_file() or not ieeg_channels_path.is_file():
                raise FileNotFoundError(f"Missing paired channel metadata for {subject}/{session}")
            eeg_rows = read_tsv(eeg_channels_path)
            ieeg_rows = read_tsv(ieeg_channels_path)
            eeg_types = [row for row in eeg_rows if row.get("type", "").upper() == "EEG"]
            ieeg_types = [row for row in ieeg_rows if row.get("type", "").upper() == "SEEG"]
            sidecar = json.loads(eeg_json_path.read_text(encoding="utf-8"))
            status_coverage = {
                "eeg_rows_with_status": sum("status" in row and row["status"] for row in eeg_rows),
                "ieeg_rows_with_status": sum("status" in row and row["status"] for row in ieeg_rows),
            }
            sessions[session] = {
                "eeg_channels_file": str(eeg_channels_path.relative_to(dataset_root)),
                "ieeg_channels_file": str(ieeg_channels_path.relative_to(dataset_root)),
                "eeg_channel_count": len(eeg_types),
                "eeg_channel_names": sorted(row["name"] for row in eeg_types),
                "eeg_units": sorted({row.get("units", "") for row in eeg_types}),
                "eeg_sampling_rates_hz": sorted({row.get("sampling_frequency", "") for row in eeg_types}),
                "eeg_low_cutoffs_hz": sorted({row.get("low_cutoff", "") for row in eeg_types}),
                "eeg_high_cutoffs_hz": sorted({row.get("high_cutoff", "") for row in eeg_types}),
                "eeg_reference_description": sidecar.get("EEGReference"),
                "ieeg_channel_count": len(ieeg_types),
                "ieeg_units": sorted({row.get("units", "") for row in ieeg_types}),
                "ieeg_sampling_rates_hz": sorted({row.get("sampling_frequency", "") for row in ieeg_types}),
                "channel_status_coverage": status_coverage,
            }
        if not sessions:
            raise ValueError(f"No development EEG channel metadata found for {subject}")
        names_by_session = [set(info["eeg_channel_names"]) for info in sessions.values()]
        common = set.intersection(*names_by_session)
        union = set.union(*names_by_session)
        result["participants"][subject] = {
            "session_count": len(sessions),
            "sessions": sessions,
            "eeg_names_common_to_all_sessions": sorted(common),
            "eeg_common_count": len(common),
            "eeg_union_count": len(union),
            "eeg_common_fraction_of_union": len(common) / len(union) if union else 0.0,
        }
    result["interpretation"] = (
        "Channel names, types, units, sampling metadata and declared EEG reference are metadata evidence only. "
        "They do not prove channel quality, identical reference circuitry across recordings, or predictive performance. "
        "An absent status field is not evidence that all channels are good."
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path("data/track_b/on004752_v1.0.0"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(audit(args.dataset_root), indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
