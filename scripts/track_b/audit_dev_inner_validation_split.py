"""Check five-fold inner-validation counts on development event metadata only."""
from __future__ import annotations

import csv
import json
from pathlib import Path


SUBJECTS = ("sub-01", "sub-02", "sub-03")
LOADS = (4, 6, 8)
N_FOLDS = 5
DATA = Path("data/track_b/on004752_v1.0.0")
OUT = Path("outputs/track_b/20261023T234000Z_b2_inner_validation_feasibility/inner_validation_counts.json")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main() -> None:
    reports: list[dict] = []
    for subject in SUBJECTS:
        sessions: dict[str, list[dict]] = {}
        for path in sorted((DATA / subject).glob("ses-*/eeg/*_events.tsv")):
            session = next(part for part in path.parts if part.startswith("ses-"))
            rows = read_rows(path)
            eligible = [r for r in rows if int(r["Artifact"]) == 0]
            by_load: dict[int, list[dict]] = {load: [] for load in LOADS}
            for row in sorted(eligible, key=lambda r: int(r["nTrial"])):
                by_load[int(row["SetSize"])].append(row)
            for load, load_rows in by_load.items():
                for index, row in enumerate(load_rows):
                    row["_inner_fold"] = index % N_FOLDS
                    row["_load"] = load
                    row["_session"] = session
            sessions[session] = eligible
        participant_folds = []
        for outer_held_load in LOADS:
            outer_train = [r for records in sessions.values() for r in records if r["_load"] != outer_held_load]
            fold_counts = []
            for fold in range(N_FOLDS):
                val = [r for r in outer_train if r["_inner_fold"] == fold]
                train = [r for r in outer_train if r["_inner_fold"] != fold]
                by_load = {
                    str(load): {
                        "train_trials": sum(r["_load"] == load for r in train),
                        "validation_trials": sum(r["_load"] == load for r in val),
                    }
                    for load in LOADS if load != outer_held_load
                }
                sessions_in_validation = sorted({r["_session"] for r in val})
                fold_counts.append({
                    "fold": fold,
                    "train_trials": len(train),
                    "validation_trials": len(val),
                    "validation_load_counts": by_load,
                    "validation_sessions": sessions_in_validation,
                })
            participant_folds.append({"outer_held_load": outer_held_load, "inner_folds": fold_counts})
        reports.append({"participant": subject, "session_count": len(sessions), "outer_splits": participant_folds})

    all_counts = [f["validation_trials"] for p in reports for s in p["outer_splits"] for f in s["inner_folds"]]
    all_train = [f["train_trials"] for p in reports for s in p["outer_splits"] for f in s["inner_folds"]]
    report = {
        "run_id": "20261023T234000Z_b2_inner_validation_feasibility",
        "dataset": "NEMAR on004752 v1.0.0",
        "scope": "Development-only event metadata for sub-01 through sub-03; no EDF samples read.",
        "outer_design": "One held set size across all sessions; other two set sizes are outer training data.",
        "inner_design_candidate": "Five deterministic folds of complete Artifact==0 trials, assigned round-robin by nTrial within each session x set-size stratum. Validation trials stay whole; no windows or samples from a trial cross folds.",
        "confirmation_participants_accessed": [],
        "synthetic_data_created": False,
        "folds_nonempty": all(x > 0 for x in all_counts) and all(x > 0 for x in all_train),
        "validation_trial_count_range": [min(all_counts), max(all_counts)],
        "inner_train_trial_count_range": [min(all_train), max(all_train)],
        "participants": reports,
        "limitation": "Counts establish only that the candidate split is nonempty. They do not establish power, data independence across sessions, model convergence, or transfer performance.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=False)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS" if report["folds_nonempty"] else "FAIL", "folds_nonempty": report["folds_nonempty"], "validation_range": report["validation_trial_count_range"], "train_range": report["inner_train_trial_count_range"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
