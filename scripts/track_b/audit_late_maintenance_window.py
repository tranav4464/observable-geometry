"""Verify the late-maintenance window against development event indices only."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path("data/track_b/on004752_v1.0.0")
OUT = Path("outputs/track_b/20261023T_b2_task_window_source_audit/pinned_event_index_audit.json")
SUBJECTS = ("sub-01", "sub-02", "sub-03")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def event_file(session: Path, modality: str) -> Path:
    paths = list((session / modality).glob("*_events.tsv"))
    if len(paths) != 1:
        raise RuntimeError(f"Expected one {modality} events file in {session}, found {len(paths)}")
    return paths[0]


def main() -> None:
    sessions = []
    total_trials = 0
    load_counts: Counter[int] = Counter()
    for subject in SUBJECTS:
        for session in sorted((ROOT / subject).glob("ses-*")):
            eeg_path = event_file(session, "eeg")
            ieeg_path = event_file(session, "ieeg")
            eeg_rows, ieeg_rows = read_tsv(eeg_path), read_tsv(ieeg_path)
            if not eeg_rows or len(eeg_rows) != len(ieeg_rows):
                raise RuntimeError(f"{session}: missing or unpaired event rows")
            local_load_counts: Counter[int] = Counter()
            for eeg, ieeg in zip(eeg_rows, ieeg_rows):
                if eeg["nTrial"] != ieeg["nTrial"] or eeg["SetSize"] != ieeg["SetSize"]:
                    raise RuntimeError(f"{session}: modality trial/load mismatch at trial {eeg['nTrial']}")
                if int(eeg["SetSize"]) not in (4, 6, 8):
                    raise RuntimeError(f"{session}: unexpected load {eeg['SetSize']}")
                if float(eeg["duration"]) != 8.0 or float(ieeg["duration"]) != 8.0:
                    raise RuntimeError(f"{session}: event duration differs from 8 seconds")
                for row, fs, expected in ((eeg, 200, 1600), (ieeg, 2000, 16000)):
                    beg = int(row["begSample"])
                    end = int(row["endSample"])
                    event_start0 = beg - 1
                    event_stop_exclusive = end
                    if event_stop_exclusive - event_start0 != expected:
                        raise RuntimeError(f"{session}: unexpected {fs} Hz event sample count")
                    crop_start0 = event_start0 + 4 * fs
                    crop_stop_exclusive = event_start0 + 6 * fs
                    if crop_start0 >= crop_stop_exclusive or crop_stop_exclusive > event_stop_exclusive:
                        raise RuntimeError(f"{session}: [4,6) s crop lies outside the event epoch")
                    if crop_start0 - event_start0 != 4 * fs or crop_stop_exclusive - event_start0 != 6 * fs:
                        raise RuntimeError(f"{session}: crop index arithmetic failed")
                local_load_counts[int(eeg["SetSize"])] += 1
                load_counts[int(eeg["SetSize"])] += 1
            sessions.append({
                "participant": subject,
                "session": session.name,
                "paired_trials": len(eeg_rows),
                "native_eeg_hz": 200,
                "native_ieeg_hz": 2000,
                "late_maintenance_window_trial_relative_s": [4.0, 6.0],
                "eeg_samples_from_event_start": [800, 1200],
                "ieeg_samples_from_event_start": [8000, 12000],
                "load_counts": {str(k): local_load_counts[k] for k in (4, 6, 8)},
                "eeg_events_sha256": sha256(eeg_path),
                "ieeg_events_sha256": sha256(ieeg_path),
            })
            total_trials += len(eeg_rows)

    report = {
        "run_id": "20261023T_b2_task_window_source_audit",
        "decision": "Do the pinned development event indices support the source-verified late-maintenance crop?",
        "dataset": "NEMAR on004752 v1.0.0 / OpenNeuro ds004752 v1.0.1",
        "scope": "event metadata only for sub-01 through sub-03; all paired events in 14 sessions",
        "source_mapping": "Published task methods define late maintenance as [-2,0) relative to probe; NEMAR crosswalk places probe at trial onset +6 s; therefore trial-relative [4,6) s.",
        "event_rows_read": total_trials,
        "sessions_checked": len(sessions),
        "all_pass": len(sessions) == 14 and total_trials > 0,
        "no_signal_samples_read": True,
        "no_reserved_participant_events_or_signals_read": True,
        "synthetic_data_used": False,
        "load_counts_total": {str(k): load_counts[k] for k in (4, 6, 8)},
        "sessions": sessions,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "sessions": len(sessions), "event_rows": total_trials,
                      "all_pass": report["all_pass"], "signal_samples_read": False,
                      "reserved_participants_opened": False}, indent=2))


if __name__ == "__main__":
    main()
