"""Build a metadata-only, deterministic WSGZP EEG repetition split manifest.

This script reads only participant lists, dataset metadata, and EEG epochs.tsv
tables. It never opens EEG/SEEG sample arrays. The manifest is explicitly a
pre-signal draft until the scientific protocol is locked.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--download-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.dataset_root.resolve()
    download_manifest = args.download_manifest.resolve()
    participants_path = root / "participants.tsv"
    description_path = root / "dataset_description.json"
    license_path = root / "LICENSE"
    for path in (participants_path, description_path, license_path, download_manifest):
        if not path.is_file():
            raise FileNotFoundError(path)

    with participants_path.open(encoding="utf-8-sig", newline="") as stream:
        participants_rows = list(csv.DictReader(stream, delimiter="\t"))
    subjects = sorted(row["participant_id"] for row in participants_rows)
    if not subjects or len(subjects) != len(set(subjects)):
        raise ValueError("Participant table is empty or has duplicate IDs")

    run_records = []
    seen_paths: set[str] = set()
    for subject in subjects:
        event_files = sorted((root / "derivatives" / "epochs" / subject / "eeg").glob("*_epochs.tsv"))
        if not event_files:
            raise FileNotFoundError(f"No EEG epochs.tsv tables for {subject}")
        for path in event_files:
            rel = path.relative_to(root).as_posix()
            if rel in seen_paths:
                raise ValueError(f"Duplicate epoch table: {rel}")
            seen_paths.add(rel)
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream, delimiter="\t"))
            if not rows or not {"trial_type", "duration", "zero_time"}.issubset(rows[0]):
                raise ValueError(f"Unexpected or empty epochs table: {rel}")
            conditions = sorted({row["trial_type"] for row in rows})
            if len(conditions) != 1:
                raise ValueError(f"Expected one stimulation condition per run: {rel}")

            partitions = {name: [] for name in ("A", "B", "C")}
            for row_index in range(len(rows)):
                partitions[("A", "B", "C")[row_index % 3]].append(row_index)
            if any(not idxs for idxs in partitions.values()):
                raise ValueError(f"Run too small for three disjoint repetition partitions: {rel}")
            if sorted(i for indices in partitions.values() for i in indices) != list(range(len(rows))):
                raise AssertionError(f"Partition assignment is not exhaustive/disjoint: {rel}")

            run_records.append({
                "participant_id": subject,
                "run_file": rel,
                "source_sha256": sha256(path),
                "n_epochs_from_tsv_rows": len(rows),
                "condition_count": len(conditions),
                "condition_label": conditions[0],
                "row_order_assumption": "0-based order of rows in this EEG epochs.tsv table",
                "partition_rule": "row_index modulo 3: 0->A, 1->B, 2->C",
                "partition_indices_zero_based": partitions,
                "partition_counts": {key: len(value) for key, value in partitions.items()},
            })

    participants_with_runs = sorted({record["participant_id"] for record in run_records})
    if participants_with_runs != subjects:
        raise ValueError("Participant table and EEG epoch-table subjects do not match")
    outer_folds = [
        {"heldout_participant": heldout,
         "training_participants": [subject for subject in subjects if subject != heldout]}
        for heldout in subjects
    ]
    counts = [record["n_epochs_from_tsv_rows"] for record in run_records]
    partition_min = {
        key: min(record["partition_counts"][key] for record in run_records)
        for key in ("A", "B", "C")
    }
    manifest = {
        "manifest_id": "WSGZP-EEG-THREE-PARTITION-METADATA-DRAFT-2026-10-28-v1",
        "status": "PRE_SIGNAL_DRAFT_NOT_PROTOCOL_LOCK",
        "signal_samples_read": False,
        "data_source": "WSGZP/ccepcoreg extracted BIDS derivative metadata",
        "dataset_root": str(root),
        "inputs_sha256": {
            "participants_tsv": sha256(participants_path),
            "dataset_description_json": sha256(description_path),
            "license": sha256(license_path),
            "download_manifest": sha256(download_manifest),
        },
        "outer_split": "leave-one-participant-out; all runs from held-out participant stay held out",
        "outer_folds": outer_folds,
        "within_run_split": {
            "unit": "EEG epochs.tsv row index only; no event-level EEG/SEEG pairing is implied",
            "groups": ["A: fit/construct", "B: finalize candidate decision", "C: untouched evaluation"],
            "allocation": "zero-based row index modulo 3, interleaved in table order",
            "n_run_tables": len(run_records),
            "n_total_metadata_epochs": sum(counts),
            "epoch_count_min_median_max": [min(counts), sorted(counts)[len(counts) // 2], max(counts)],
            "minimum_partition_sizes": partition_min,
            "independence_caveat": "Disjoint row partitions do not guarantee statistical independence; within-run dependence must be assessed and reported.",
        },
        "run_tables": run_records,
        "limitations": [
            "The original continuous EEG/SEEG and trigger/rejection logs are absent; preprocessing is inherited.",
            "The row-index partition is a proposal based on metadata, not a scientifically locked split.",
            "Do not align EEG and SEEG epochs by row index; their counts differ and no shared trial IDs are present.",
            "No neural sample arrays or outcomes were opened.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "manifest_id": manifest["manifest_id"],
        "status": manifest["status"],
        "signal_samples_read": False,
        "participants": len(subjects),
        "run_tables": len(run_records),
        "n_total_metadata_epochs": sum(counts),
        "epoch_count_min_median_max": manifest["within_run_split"]["epoch_count_min_median_max"],
        "minimum_partition_sizes": partition_min,
    }, indent=2))


if __name__ == "__main__":
    main()
