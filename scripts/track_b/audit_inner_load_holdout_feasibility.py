"""Check nested leave-one-load-out inner folds using development events only."""
from __future__ import annotations

import csv
import json
from pathlib import Path

DATA = Path("data/track_b/on004752_v1.0.0")
OUT = Path("outputs/track_b/20261023T_b2_inner_load_holdout_audit/fold_counts.json")
SUBJECTS = ("sub-01", "sub-02", "sub-03")
LOADS = (4, 6, 8)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> None:
    participants = []
    for subject in SUBJECTS:
        sessions = {}
        for path in sorted((DATA / subject).glob("ses-*/eeg/*_events.tsv")):
            session = next(part for part in path.parts if part.startswith("ses-"))
            eligible = [r for r in read_rows(path) if int(r["Artifact"]) == 0]
            sessions[session] = eligible
        all_rows = [dict(r, _session=s) for s, rows in sessions.items() for r in rows]
        outer = []
        for held in LOADS:
            outer_training = [r for r in all_rows if int(r["SetSize"]) != held]
            inner = []
            inner_loads = [load for load in LOADS if load != held]
            for validation_load in inner_loads:
                training_load = next(load for load in inner_loads if load != validation_load)
                train = [r for r in outer_training if int(r["SetSize"]) == training_load]
                val = [r for r in outer_training if int(r["SetSize"]) == validation_load]
                by_session = {
                    s: {
                        "train_trials": sum(r["_session"] == s for r in train),
                        "validation_trials": sum(r["_session"] == s for r in val),
                    }
                    for s in sorted(sessions)
                }
                inner.append({
                    "validation_load": validation_load,
                    "training_load": training_load,
                    "train_trials": len(train),
                    "validation_trials": len(val),
                    "train_sessions": sorted({r["_session"] for r in train}),
                    "validation_sessions": sorted({r["_session"] for r in val}),
                    "by_session": by_session,
                })
            outer.append({"outer_held_load": held, "inner_folds": inner})
        participants.append({"participant": subject, "session_count": len(sessions), "outer_splits": outer})

    folds = [f for p in participants for o in p["outer_splits"] for f in o["inner_folds"]]
    train_counts = [f["train_trials"] for f in folds]
    val_counts = [f["validation_trials"] for f in folds]
    all_nonempty = bool(folds) and min(train_counts) > 0 and min(val_counts) > 0
    report = {
        "run_id": "20261023T_b2_inner_load_holdout_audit",
        "dataset": "NEMAR on004752 v1.0.0",
        "scope": "Artifact==0 event metadata only, development participants sub-01..03; no EDF samples read",
        "outer_design": "Hold one set size across all sessions; train on the other two",
        "inner_design": "Two folds per outer split; in each, train on one entire set size and validate on the other entire set size. All eligible trials of a load stay together across sessions.",
        "confirmation_event_rows_or_signal_samples_opened": False,
        "synthetic_data_created": False,
        "model_fitted": False,
        "all_inner_train_and_validation_folds_nonempty": all_nonempty,
        "train_trial_range": [min(train_counts), max(train_counts)],
        "validation_trial_range": [min(val_counts), max(val_counts)],
        "participants": participants,
        "interpretation": "Feasibility only. One-load inner training estimates tuning stability under a load shift but is a smaller training set than outer training; it does not estimate performance or prove the selected hyperparameters are optimal.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": all_nonempty, "fold_count": len(folds), "train_trial_range": report["train_trial_range"], "validation_trial_range": report["validation_trial_range"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
