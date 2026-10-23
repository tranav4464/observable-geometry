"""Audit development event metadata for leave-one-source-load-out tuning."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


SUBJECTS = ("sub-01", "sub-02", "sub-03")
LOADS = (4, 6, 8)


def _read_events(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or not {"SetSize", "Artifact"}.issubset(rows[0]):
        raise ValueError(f"Missing or empty SetSize/Artifact event table: {path}")
    for row in rows:
        if int(row["SetSize"]) not in LOADS or int(row["Artifact"]) not in (0, 1):
            raise ValueError(f"Unexpected task label or artifact value in {path}")
    return rows


def _count(rows: list[dict[str, str]]) -> dict[str, int]:
    return {
        "all_trials": len(rows),
        "artifact_zero_trials": sum(int(row["Artifact"]) == 0 for row in rows),
        "artifact_one_trials": sum(int(row["Artifact"]) == 1 for row in rows),
    }


def audit(dataset_root: Path) -> dict[str, Any]:
    participants: list[dict[str, Any]] = []
    folds: list[dict[str, Any]] = []
    for subject in SUBJECTS:
        sessions: dict[str, list[dict[str, str]]] = {}
        for path in sorted((dataset_root / subject).glob("ses-*/eeg/*_events.tsv")):
            session = next(part for part in path.parts if part.startswith("ses-"))
            if session in sessions:
                raise ValueError(f"Multiple event tables for {subject}/{session}")
            sessions[session] = _read_events(path)
        if len(sessions) < 2:
            raise ValueError(f"Expected multiple development sessions for {subject}")

        load_counts: dict[str, dict[str, int]] = {}
        for load in LOADS:
            selected = [
                row for rows in sessions.values() for row in rows
                if int(row["SetSize"]) == load
            ]
            load_counts[str(load)] = _count(selected)

        participant_folds: list[dict[str, Any]] = []
        for outer_held_load in LOADS:
            source_loads = [load for load in LOADS if load != outer_held_load]
            for inner_validation_load in source_loads:
                inner_fit_load = next(load for load in source_loads if load != inner_validation_load)
                fit_rows = [
                    row for rows in sessions.values() for row in rows
                    if int(row["SetSize"]) == inner_fit_load
                ]
                validation_rows = [
                    row for rows in sessions.values() for row in rows
                    if int(row["SetSize"]) == inner_validation_load
                ]
                fold = {
                    "subject": subject,
                    "outer_held_load": outer_held_load,
                    "inner_fit_load": inner_fit_load,
                    "inner_validation_load": inner_validation_load,
                    "fit": _count(fit_rows),
                    "validation": _count(validation_rows),
                    "sessions_fit": sorted(sessions),
                    "sessions_validation": sorted(sessions),
                    "session_transfer_tested": False,
                }
                participant_folds.append(fold)
                folds.append(fold)
        participants.append({
            "subject": subject,
            "session_count": len(sessions),
            "trials_by_load": load_counts,
            "inner_folds": participant_folds,
        })

    eligible_fit = [fold["fit"]["artifact_zero_trials"] for fold in folds]
    eligible_validation = [fold["validation"]["artifact_zero_trials"] for fold in folds]
    all_fit = [fold["fit"]["all_trials"] for fold in folds]
    all_validation = [fold["validation"]["all_trials"] for fold in folds]
    return {
        "audit_type": "development_metadata_inner_leave_one_source_load_out_feasibility",
        "dataset": "NEMAR on004752 v1.0.0",
        "development_subjects_only": list(SUBJECTS),
        "signal_samples_read": False,
        "confirmation_participants_accessed": [],
        "synthetic_data_created": False,
        "eligibility": "All trials are counted; Artifact==0 is a descriptive count only, not a final signal-quality rule.",
        "design": "For each outer held load k, the two other loads form a two-fold inner CV: fit on one complete load and validate on the other, across all sessions.",
        "fold_summary": {
            "count": len(folds),
            "expected_count": len(SUBJECTS) * len(LOADS) * 2,
            "minimum_fit_all_trials": min(all_fit),
            "minimum_validation_all_trials": min(all_validation),
            "minimum_fit_artifact_zero_trials": min(eligible_fit),
            "minimum_validation_artifact_zero_trials": min(eligible_validation),
            "empty_fit_artifact_zero_folds": sum(value == 0 for value in eligible_fit),
            "empty_validation_artifact_zero_folds": sum(value == 0 for value in eligible_validation),
        },
        "participants": participants,
        "folds": folds,
        "limitation": "Counts establish split feasibility only, not statistical power, session independence, model convergence, transfer performance, or utility. Inner and outer evaluations share sessions; this design tests load transfer only.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.dataset_root)
    summary = result["fold_summary"]
    if summary["count"] != summary["expected_count"]:
        raise ValueError(f"Unexpected fold count: {summary}")
    if summary["empty_fit_artifact_zero_folds"] or summary["empty_validation_artifact_zero_folds"]:
        raise ValueError(f"Empty descriptive folds: {summary}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
