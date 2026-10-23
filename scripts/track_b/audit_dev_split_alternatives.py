"""Compare development-only metadata counts for load and session holdouts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


SUBJECTS = ("sub-01", "sub-02", "sub-03")
LOADS = (4, 6, 8)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    for row in rows:
        if not {"SetSize", "Artifact"}.issubset(row):
            raise ValueError(f"Missing SetSize/Artifact columns in {path}")
    return rows


def stats(folds: list[dict[str, Any]], train_key: str, test_key: str) -> dict[str, Any]:
    train = sorted(f[train_key] for f in folds)
    test = sorted(f[test_key] for f in folds)
    return {
        "fold_count": len(folds),
        "train_min": train[0],
        "train_median": train[len(train) // 2],
        "test_min": test[0],
        "test_median": test[len(test) // 2],
        "empty_test_folds": sum(n == 0 for n in test),
    }


def audit(root: Path) -> dict[str, Any]:
    all_load: list[dict[str, Any]] = []
    all_session: list[dict[str, Any]] = []
    subjects: list[dict[str, Any]] = []
    for subject in SUBJECTS:
        sessions: dict[str, list[dict[str, str]]] = {}
        for path in sorted((root / subject).glob("ses-*/eeg/*_events.tsv")):
            session = next(part for part in path.parts if part.startswith("ses-"))
            sessions[session] = read_rows(path)
        if len(sessions) < 2:
            raise ValueError(f"Insufficient sessions for {subject}")
        subj_load, subj_session = [], []
        for load in LOADS:
            test = [r for rows in sessions.values() for r in rows if int(r["SetSize"]) == load and int(r["Artifact"]) == 0]
            train = [r for rows in sessions.values() for r in rows if int(r["SetSize"]) != load and int(r["Artifact"]) == 0]
            fold = {"subject": subject, "held_load": load, "train_eligible": len(train), "test_eligible": len(test)}
            subj_load.append(fold)
            all_load.append(fold)
        for held_session in sorted(sessions):
            test = [r for r in sessions[held_session] if int(r["Artifact"]) == 0]
            train = [r for session, rows in sessions.items() if session != held_session for r in rows if int(r["Artifact"]) == 0]
            fold = {"subject": subject, "held_session": held_session, "train_eligible": len(train), "test_eligible": len(test)}
            subj_session.append(fold)
            all_session.append(fold)
        subjects.append({"subject": subject, "session_count": len(sessions), "load_holdout_folds": subj_load, "session_holdout_folds": subj_session})
    return {
        "audit_type": "development_metadata_split_alternative_feasibility",
        "dataset": "NEMAR on004752 v1.0.0",
        "development_subjects_only": list(SUBJECTS),
        "signal_samples_read": False,
        "confirmation_participants_accessed": [],
        "synthetic_data_created": False,
        "eligibility": "Artifact==0 counted; Artifact==1 excluded for descriptive feasibility only. Not a final rule.",
        "arms": {
            "within_participant_held_load_across_sessions": {
                "meaning": "Train on the other two set sizes across all sessions; test the wholly unseen set size across all sessions. Does not estimate session transfer.",
                **stats(all_load, "train_eligible", "test_eligible"),
                "folds": all_load,
            },
            "within_participant_held_session_all_loads": {
                "meaning": "Train on all set sizes in all but one session; test all loads in the held session. Does not estimate held-load transfer.",
                **stats(all_session, "train_eligible", "test_eligible"),
                "folds": all_session,
            },
        },
        "participants": subjects,
        "limitation": "Counts establish only nonempty metadata splits. They do not establish sufficient statistical power, adequate participant count, target quality, model fit, or utility.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.dataset_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {x: y for x, y in v.items() if x != "folds"} for k, v in result["arms"].items()}, indent=2))


if __name__ == "__main__":
    main()
