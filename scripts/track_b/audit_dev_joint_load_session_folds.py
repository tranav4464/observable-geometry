"""Metadata-only feasibility audit for joint held-load/held-session folds."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEV_SUBJECTS = ("sub-01", "sub-02", "sub-03")
LOADS = (4, 6, 8)


def read_events(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    for row in rows:
        for key in ("SetSize", "Artifact", "Correct"):
            if key not in row:
                raise ValueError(f"{path}: missing required event field {key}")
    return rows


def audit(root: Path) -> dict[str, Any]:
    subjects: list[dict[str, Any]] = []
    all_fold_counts: list[dict[str, Any]] = []
    for subject in DEV_SUBJECTS:
        subject_root = root / subject
        if not subject_root.is_dir():
            raise FileNotFoundError(subject_root)
        sessions: dict[str, list[dict[str, str]]] = {}
        for path in sorted(subject_root.glob("ses-*/eeg/*_events.tsv")):
            session = next(part for part in path.parts if part.startswith("ses-"))
            if session in sessions:
                raise ValueError(f"multiple event files for {subject}/{session}")
            sessions[session] = read_events(path)
        if len(sessions) < 2:
            raise ValueError(f"{subject}: fewer than two sessions")

        fold_records: list[dict[str, Any]] = []
        eligible_by_session_load: dict[tuple[str, int], int] = {}
        for session, rows in sessions.items():
            for load in LOADS:
                eligible_by_session_load[(session, load)] = sum(
                    int(row["SetSize"]) == load and int(row["Artifact"]) == 0
                    for row in rows
                )

        for test_session in sorted(sessions):
            test_rows = sessions[test_session]
            for test_load in LOADS:
                test_all = [r for r in test_rows if int(r["SetSize"]) == test_load]
                test_eligible = [r for r in test_all if int(r["Artifact"]) == 0]
                train_all = [
                    row
                    for session, rows in sessions.items()
                    if session != test_session
                    for row in rows
                    if int(row["SetSize"]) != test_load
                ]
                train_eligible = [r for r in train_all if int(r["Artifact"]) == 0]
                fold = {
                    "test_session": test_session,
                    "held_load": test_load,
                    "test_trials_total": len(test_all),
                    "test_trials_artifact0": len(test_eligible),
                    "test_trials_artifact1": len(test_all) - len(test_eligible),
                    "train_trials_total_other_loads_other_sessions": len(train_all),
                    "train_trials_artifact0": len(train_eligible),
                    "train_trials_artifact1": len(train_all) - len(train_eligible),
                    "train_correct_0_artifact0": sum(int(r["Correct"]) == 0 for r in train_eligible),
                    "test_correct_0_artifact0": sum(int(r["Correct"]) == 0 for r in test_eligible),
                }
                fold_records.append(fold)
                all_fold_counts.append({"subject": subject, **fold})

        subjects.append(
            {
                "subject": subject,
                "session_count": len(sessions),
                "session_names": sorted(sessions),
                "event_rows": sum(map(len, sessions.values())),
                "load_totals": {
                    str(load): sum(int(r["SetSize"]) == load for rows in sessions.values() for r in rows)
                    for load in LOADS
                },
                "artifact0_load_totals": {
                    str(load): sum(eligible_by_session_load[(s, load)] for s in sessions)
                    for load in LOADS
                },
                "folds": fold_records,
            }
        )

    eligible_test = [f["test_trials_artifact0"] for f in all_fold_counts]
    eligible_train = [f["train_trials_artifact0"] for f in all_fold_counts]
    zero_test_folds = [
        {"subject": f["subject"], "session": f["test_session"], "load": f["held_load"]}
        for f in all_fold_counts
        if f["test_trials_artifact0"] == 0
    ]
    return {
        "audit_type": "development_metadata_joint_held_load_session_feasibility",
        "dataset": "NEMAR on004752 v1.0.0",
        "development_subjects_only": list(DEV_SUBJECTS),
        "sessions_audited": sum(s["session_count"] for s in subjects),
        "fold_count": len(all_fold_counts),
        "provisional_fold_definition": "For subject p, test load k in {4,6,8} and session s: test only artifact==0 trials of load k from s; train only artifact==0 trials at the other two loads from all sessions other than s.",
        "artifact_rule_audited": "Artifact==1 excluded from this count; this is a feasibility audit, not a final locked preprocessing decision.",
        "correctness_rule": "Incorrect trials remain eligible because the candidate target is recorded signal prediction conditional on the task load, not correct-response prediction.",
        "signal_samples_read": False,
        "confirmation_participants_accessed": [],
        "synthetic_data_created": False,
        "summary": {
            "eligible_train_trials_min": min(eligible_train),
            "eligible_train_trials_median": sorted(eligible_train)[len(eligible_train) // 2],
            "eligible_test_trials_min": min(eligible_test),
            "eligible_test_trials_median": sorted(eligible_test)[len(eligible_test) // 2],
            "folds_with_zero_eligible_test_trials": zero_test_folds,
            "unique_training_correct0_counts": sorted({f["train_correct_0_artifact0"] for f in all_fold_counts}),
            "warning": "Fold feasibility does not establish sufficient power, stationarity, model fit, or independent population-level evidence. Only three development participants are included.",
        },
        "participants": subjects,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.dataset_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
