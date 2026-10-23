"""Metadata-only audit of paired EEG/iEEG reference declarations."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEV_SUBJECTS = {"sub-01", "sub-02", "sub-03"}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def audit(dataset_root: Path) -> dict[str, Any]:
    dataset_root = dataset_root.resolve()
    sessions: list[dict[str, Any]] = []
    for subject in sorted(DEV_SUBJECTS):
        subject_root = dataset_root / subject
        if not subject_root.is_dir():
            raise FileNotFoundError(subject_root)
        for eeg_json in sorted(subject_root.glob("ses-*/eeg/*_eeg.json")):
            session = next(part for part in eeg_json.parts if part.startswith("ses-"))
            ieeg_dir = dataset_root / subject / session / "ieeg"
            ieeg_json = ieeg_dir / eeg_json.name.replace("_eeg.json", "_ieeg.json")
            eeg_tsv = eeg_json.with_name(eeg_json.name.replace("_eeg.json", "_channels.tsv"))
            ieeg_tsv = ieeg_dir / eeg_tsv.name
            for required in (ieeg_json, eeg_tsv, ieeg_tsv):
                if not required.is_file():
                    raise FileNotFoundError(required)
            eeg_meta = json.loads(eeg_json.read_text(encoding="utf-8"))
            ieeg_meta = json.loads(ieeg_json.read_text(encoding="utf-8"))
            eeg_fields, eeg_rows = read_tsv(eeg_tsv)
            ieeg_fields, ieeg_rows = read_tsv(ieeg_tsv)
            sessions.append({
                "subject": subject,
                "session": session,
                "eeg_sidecar": str(eeg_json.relative_to(dataset_root)),
                "ieeg_sidecar": str(ieeg_json.relative_to(dataset_root)),
                "eeg_reference": eeg_meta.get("EEGReference"),
                "ieeg_reference": ieeg_meta.get("iEEGReference"),
                "eeg_hardware_filters": eeg_meta.get("HardwareFilters"),
                "ieeg_hardware_filters": ieeg_meta.get("HardwareFilters"),
                "eeg_software_filters": eeg_meta.get("SoftwareFilters"),
                "ieeg_software_filters": ieeg_meta.get("SoftwareFilters"),
                "eeg_channel_count": sum(row.get("type", "").upper() == "EEG" for row in eeg_rows),
                "ieeg_channel_count": sum(row.get("type", "").upper() == "SEEG" for row in ieeg_rows),
                "eeg_channels_has_reference_column": "reference" in eeg_fields,
                "ieeg_channels_has_reference_column": "reference" in ieeg_fields,
                "eeg_channels_has_status_column": "status" in eeg_fields,
                "ieeg_channels_has_status_column": "status" in ieeg_fields,
                "eeg_channels_cutoff_pairs": sorted({(row.get("low_cutoff", ""), row.get("high_cutoff", "")) for row in eeg_rows}),
                "ieeg_channels_cutoff_pairs": sorted({(row.get("low_cutoff", ""), row.get("high_cutoff", "")) for row in ieeg_rows}),
            })
    return {
        "audit_type": "development_paired_reference_metadata_only",
        "development_subjects_only": sorted(DEV_SUBJECTS),
        "session_count": len(sessions),
        "events_or_signal_files_read": False,
        "confirmation_participants_read": False,
        "sessions": sessions,
        "interpretation": (
            "Reference declarations define the intended recording reference, not verified physical implementation. "
            "A common intracranial reference means each channel voltage is relative to that reference. "
            "These declarations support prediction only of the recorded referenced signals under this protocol, "
            "not absolute source voltages or directly comparable amplitudes across reference systems."
        ),
    }


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
