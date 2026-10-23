"""Metadata-only check of within-participant iEEG contact identity.

Reads only electrodes.tsv and channels.tsv for the authorized development
participants sub-01 through sub-03. It does not read events, signal files,
or any files from confirmation participants.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEV_SUBJECTS = {"sub-01", "sub-02", "sub-03"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def audit(dataset_root: Path) -> dict[str, Any]:
    dataset_root = dataset_root.resolve()
    result: dict[str, Any] = {
        "audit_type": "development_contact_identity_metadata_only",
        "development_subjects_only": sorted(DEV_SUBJECTS),
        "events_or_signal_files_read": False,
        "confirmation_participants_read": False,
        "participants": {},
    }
    for subject in sorted(DEV_SUBJECTS):
        subject_root = dataset_root / subject
        if not subject_root.is_dir():
            raise FileNotFoundError(subject_root)
        sessions: dict[str, dict[str, Any]] = {}
        electrode_files = sorted(subject_root.glob("ses-*/ieeg/*_electrodes.tsv"))
        for electrode_path in electrode_files:
            session = next(part for part in electrode_path.parts if part.startswith("ses-"))
            channel_path = electrode_path.with_name(electrode_path.name.replace("_electrodes.tsv", "_channels.tsv"))
            if not channel_path.is_file():
                raise FileNotFoundError(channel_path)
            electrodes = read_tsv(electrode_path)
            channels = read_tsv(channel_path)
            electrode_by_name = {row.get("name", ""): row for row in electrodes if row.get("name")}
            seeg_rows = [row for row in channels if row.get("type", "").upper() == "SEEG"]
            seeg_names = {row.get("name", "") for row in seeg_rows if row.get("name")}
            matched = seeg_names & electrode_by_name.keys()
            missing = sorted(seeg_names - electrode_by_name.keys())
            if missing:
                raise ValueError(f"{subject}/{session}: SEEG channels missing electrode metadata: {missing}")
            status_counts: dict[str, int] = {}
            for row in seeg_rows:
                status = row.get("status", "(unspecified)")
                status_counts[status] = status_counts.get(status, 0) + 1
            sessions[session] = {
                "electrodes_file": str(electrode_path.relative_to(dataset_root)),
                "channels_file": str(channel_path.relative_to(dataset_root)),
                "electrode_rows": len(electrodes),
                "seeg_channel_rows": len(seeg_rows),
                "seeg_names_matching_electrode_metadata": len(matched),
                "seeg_names": sorted(seeg_names),
                "seeg_status_counts": status_counts,
            }
        if not sessions:
            raise ValueError(f"No development electrode/channel metadata found for {subject}")
        session_names = sorted(sessions)
        common = set.intersection(*(set(sessions[name]["seeg_names"]) for name in session_names))
        union = set.union(*(set(sessions[name]["seeg_names"]) for name in session_names))
        result["participants"][subject] = {
            "session_count": len(sessions),
            "sessions": sessions,
            "common_seeg_contact_count_across_all_sessions": len(common),
            "common_seeg_contacts": sorted(common),
            "union_seeg_contact_count": len(union),
            "common_fraction_of_union": len(common) / len(union) if union else 0.0,
            "all_session_channel_names_join_electrode_metadata": all(
                session["seeg_channel_rows"] == session["seeg_names_matching_electrode_metadata"]
                for session in sessions.values()
            ),
        }
    result["interpretation"] = (
        "Stable names and metadata joins establish only that a same-label contact-level target can be defined "
        "within a development participant. They do not validate anatomical identity, prove unchanged electrode "
        "placement/physiology across sessions, establish a model task, or show predictive performance."
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path("data/track_b/on004752_v1.0.0"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(audit(args.dataset_root), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
