"""Inventory repeated WSGZP run-level stimulation conditions from BIDS TSVs.

This metadata-only audit reads epoch TSVs for EEG and iEEG. It does not open
NPY/FIF recordings or inspect signal values. Identical run descriptions are
candidate same-condition repeats, not proof that runs were independently
acquired or temporally independent.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


RUN_RE = re.compile(r"^(sub-[A-Za-z0-9]+)_task-ccepcoreg_run-([A-Za-z0-9]+)_epochs\.tsv$")
POSSIBLE_EVENT_KEYS = {"event_id", "epoch_id", "trial_id", "sample", "onset"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_epoch_tsv(path: Path) -> dict[str, Any]:
    match = RUN_RE.match(path.name)
    if match is None:
        raise ValueError(f"Unexpected epoch TSV name: {path.name}")
    subject, run = match.groups()
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        columns = list(reader.fieldnames or [])
        if "trial_type" not in columns:
            raise ValueError(f"Missing trial_type column: {path}")
        rows = list(reader)
    conditions = sorted({(row.get("trial_type") or "").strip() for row in rows})
    if not rows or any(not condition for condition in conditions):
        raise ValueError(f"Empty epoch table or missing trial_type values: {path}")
    return {
        "participant": subject,
        "run": run,
        "n_epochs": len(rows),
        "trial_types": conditions,
        "columns": columns,
        "possible_event_key_columns": sorted(POSSIBLE_EVENT_KEYS.intersection(columns)),
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
    }


def audit(dataset_root: Path) -> dict[str, Any]:
    epoch_root = dataset_root / "derivatives" / "epochs"
    records: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    missing: list[str] = []
    for subject_dir in sorted(epoch_root.glob("sub-*")):
        for modality in ("eeg", "ieeg"):
            modality_dir = subject_dir / modality
            files = sorted(modality_dir.glob("*_epochs.tsv")) if modality_dir.is_dir() else []
            for path in files:
                record = read_epoch_tsv(path)
                key = (record["participant"], record["run"])
                if modality in records[key]:
                    raise ValueError(f"Duplicate {modality} run table for {key}")
                records[key][modality] = record

    paired_runs: list[dict[str, Any]] = []
    for (subject, run), modalities in sorted(records.items()):
        if set(modalities) != {"eeg", "ieeg"}:
            missing.append(f"{subject}/run-{run}: missing {({'eeg','ieeg'} - set(modalities))}")
            continue
        eeg, ieeg = modalities["eeg"], modalities["ieeg"]
        paired_runs.append({
            "participant": subject,
            "run": run,
            "same_trial_type_set": eeg["trial_types"] == ieeg["trial_types"],
            "trial_types": eeg["trial_types"],
            "eeg_epoch_count": eeg["n_epochs"],
            "ieeg_epoch_count": ieeg["n_epochs"],
            "eeg_columns": eeg["columns"],
            "ieeg_columns": ieeg["columns"],
            "eeg_possible_event_key_columns": eeg["possible_event_key_columns"],
            "ieeg_possible_event_key_columns": ieeg["possible_event_key_columns"],
            "eeg_tsv_sha256": eeg["sha256"],
            "ieeg_tsv_sha256": ieeg["sha256"],
        })

    condition_runs: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for run in paired_runs:
        condition_runs[(run["participant"], tuple(run["trial_types"]))].append(run)
    repeats: list[dict[str, Any]] = []
    for (subject, trial_types), run_records in sorted(condition_runs.items()):
        if len(run_records) < 2:
            continue
        for first, second in itertools.combinations(sorted(run_records, key=lambda r: r["run"]), 2):
            repeats.append({
                "participant": subject,
                "trial_types": list(trial_types),
                "run_a": first["run"],
                "run_b": second["run"],
                "eeg_epochs_a_b": [first["eeg_epoch_count"], second["eeg_epoch_count"]],
                "ieeg_epochs_a_b": [first["ieeg_epoch_count"], second["ieeg_epoch_count"]],
                "eeg_seeg_trial_pairing_available": False,
                "independent_acquisition_confirmed": False,
            })

    return {
        "audit_id": "WSGZP-REPEAT-RUN-CONDITION-INVENTORY-2026-10-29-v3",
        "dataset_root": str(dataset_root.resolve()),
        "run_id_semantics": (
            "The pinned repository contains one helper that assigns run_id "
            "as a sequential within-subject counter and another that assigns "
            "run_nr from sorted filenames. The exporter consumes an external "
            "runs_table.csv, which is not included, so the released run-ID "
            "mapping's chronology, session meaning, and independence cannot "
            "be established from the repository alone."
        ),
        "run_id_semantics_sources": [
            "https://github.com/iTCf/ccepcoreg/blob/"
            "8721fc04328c00b131659915dfbfa569bd342b54/fx_bids.py#L876-L961",
            "https://github.com/iTCf/ccepcoreg/blob/"
            "8721fc04328c00b131659915dfbfa569bd342b54/export_bids.py#L365-L450",
        ],
        "signal_samples_read": False,
        "recording_arrays_opened": False,
        "epoch_tsv_run_pair_count": len(paired_runs),
        "missing_modality_run_tables": missing,
        "run_pairs_with_identical_eeg_ieeg_condition_sets": sum(
            record["same_trial_type_set"] for record in paired_runs
        ),
        "same_participant_exact_condition_repeat_pair_count": len(repeats),
        "participants_with_exact_condition_repeats": sorted({r["participant"] for r in repeats}),
        "repeat_pairs": repeats,
        "interpretation": (
            "An identical condition string in two distinct run tables is a candidate "
            "run-level repeat only. The BIDS release does not establish acquisition "
            "independence, run spacing, or EEG-SEEG event pairing. These candidates "
            "cannot support a confirmatory repeatability claim until those facts and "
            "the preprocessing dependency are confirmed."
        ),
        "runs": paired_runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.dataset_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "audit_id", "epoch_tsv_run_pair_count",
        "same_participant_exact_condition_repeat_pair_count",
        "participants_with_exact_condition_repeats", "missing_modality_run_tables",
        "signal_samples_read",
    )}, indent=2))


if __name__ == "__main__":
    main()
