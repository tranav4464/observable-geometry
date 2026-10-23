"""Audit paired EEG/iEEG channel metadata without opening events or signals."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


INPUT_CHANNELS = ("A1", "A2", "C3", "C4", "F3", "F4", "O1", "O2")
EXCLUDED_PAIRS = {("sub-06", "ses-04"), ("sub-14", "ses-06")}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(dataset_root: Path) -> dict[str, Any]:
    root = dataset_root.resolve()
    participants: dict[str, Any] = {}
    pair_count = 0
    for subject_root in sorted(root.glob("sub-*")):
        subject = subject_root.name
        sessions: dict[str, Any] = {}
        for eeg_path in sorted(subject_root.glob("ses-*/eeg/*_channels.tsv")):
            session = eeg_path.parts[-3]
            ieeg_path = root / subject / session / "ieeg" / eeg_path.name.replace("_eeg_", "_ieeg_")
            if not ieeg_path.is_file():
                raise FileNotFoundError(f"Missing paired iEEG channels.tsv: {ieeg_path}")
            eeg_rows = [row for row in read_tsv(eeg_path) if row.get("type", "").upper() == "EEG"]
            ieeg_rows = [row for row in read_tsv(ieeg_path) if row.get("type", "").upper() == "SEEG"]
            eeg_names = [row["name"] for row in eeg_rows]
            ieeg_names = [row["name"] for row in ieeg_rows]
            if len(eeg_names) != len(set(eeg_names)) or len(ieeg_names) != len(set(ieeg_names)):
                raise ValueError(f"Duplicate channel label in {subject}/{session}")
            excluded = (subject, session) in EXCLUDED_PAIRS
            sessions[session] = {
                "eeg_channel_count": len(eeg_names),
                "ieeg_channel_count": len(ieeg_names),
                "required_eeg_inputs_present": sorted(set(INPUT_CHANNELS) & set(eeg_names)),
                "required_eeg_inputs_missing": sorted(set(INPUT_CHANNELS) - set(eeg_names)),
                "ieeg_channel_names": sorted(ieeg_names),
                "excluded_by_prespecified_parser_rule": excluded,
                "eeg_channels_file": str(eeg_path.relative_to(root)),
                "ieeg_channels_file": str(ieeg_path.relative_to(root)),
                "eeg_channels_sha256": sha256(eeg_path),
                "ieeg_channels_sha256": sha256(ieeg_path),
            }
            pair_count += 1
        if not sessions:
            continue
        eligible = [item for key, item in sessions.items() if (subject, key) not in EXCLUDED_PAIRS]
        eeg_ok = all(not item["required_eeg_inputs_missing"] for item in eligible)
        target_names = set.intersection(*(set(item["ieeg_channel_names"]) for item in eligible)) if eligible else set()
        participants[subject] = {
            "session_count": len(sessions),
            "eligible_session_count_after_fixed_exclusions": len(eligible),
            "all_required_eeg_inputs_present_in_eligible_sessions": eeg_ok,
            "stable_ieeg_label_intersection_count": len(target_names),
            "stable_ieeg_label_intersection": sorted(target_names),
            "sessions": sessions,
        }
    return {
        "audit_type": "all_participant_paired_channel_schema_metadata_only",
        "dataset": "NEMAR on004752 v1.0.0",
        "input_eeg_channels": list(INPUT_CHANNELS),
        "fixed_exclusions": [f"{s}/{e}" for s, e in sorted(EXCLUDED_PAIRS)],
        "paired_sessions_checked": pair_count,
        "expected_paired_sessions": 68,
        "events_read": False,
        "signal_samples_read": False,
        "participant_outcomes_or_load_counts_read": False,
        "participants": participants,
        "interpretation": (
            "Channel metadata can establish label availability and stable within-participant contact names only. "
            "It does not establish signal quality, anatomy, trial eligibility, predictive performance, or power. "
            "No events.tsv, EDF payload, or held-out outcome was opened."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path("data/track_b/on004752_v1.0.0"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.dataset_root)
    if report["paired_sessions_checked"] != report["expected_paired_sessions"]:
        raise ValueError(
            f"Expected {report['expected_paired_sessions']} paired sessions; "
            f"found {report['paired_sessions_checked']}"
        )
    if set(report["participants"]) != {f"sub-{i:02d}" for i in range(1, 16)}:
        raise ValueError("Participant inventory does not match the pinned 15-participant release")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    summary = {
        "paired_sessions_checked": report["paired_sessions_checked"],
        "participants": {
            key: {
                "sessions": value["session_count"],
                "eligible_sessions": value["eligible_session_count_after_fixed_exclusions"],
                "required_eeg_inputs_present": value["all_required_eeg_inputs_present_in_eligible_sessions"],
                "stable_contact_count": value["stable_ieeg_label_intersection_count"],
            }
            for key, value in report["participants"].items()
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
