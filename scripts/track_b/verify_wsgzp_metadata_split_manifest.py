"""Independently replay a WSGZP metadata-only EEG split manifest.

This implementation does not import the manifest builder. It rereads only
the participant table and EEG epochs.tsv source metadata, then verifies hashes,
row counts, partition coverage and the leave-one-participant-out folds.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def verify(dataset_root: Path, manifest_path: Path) -> dict:
    root, manifest_path = dataset_root.resolve(), manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("status") != "PRE_SIGNAL_DRAFT_NOT_PROTOCOL_LOCK":
        errors.append("Unexpected manifest status")
    if manifest.get("signal_samples_read") is not False:
        errors.append("Manifest does not state signal samples were unopened")
    participants_path = root / "participants.tsv"
    participant_ids = sorted(row["participant_id"] for row in read_rows(participants_path))
    if len(participant_ids) != len(set(participant_ids)):
        errors.append("Participant table contains duplicate IDs")
    expected_meta_hashes = {
        "participants_tsv": digest(participants_path),
        "dataset_description_json": digest(root / "dataset_description.json"),
        "license": digest(root / "LICENSE"),
    }
    for name, sha in expected_meta_hashes.items():
        if manifest.get("inputs_sha256", {}).get(name) != sha:
            errors.append(f"Input hash mismatch: {name}")

    records = manifest.get("run_tables", [])
    record_map = {record.get("run_file"): record for record in records}
    if len(record_map) != len(records):
        errors.append("Duplicate run-file record")
    expected_paths = sorted(
        (root / "derivatives" / "epochs").glob("*/eeg/*_epochs.tsv"),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    expected_relpaths = {path.relative_to(root).as_posix() for path in expected_paths}
    if set(record_map) != expected_relpaths:
        errors.append("Run-table inventory differs from the extracted EEG metadata")

    total_epochs = 0
    min_sizes = {"A": None, "B": None, "C": None}
    for path in expected_paths:
        rel = path.relative_to(root).as_posix()
        record = record_map.get(rel)
        if record is None:
            continue
        rows = read_rows(path)
        n = len(rows)
        total_epochs += n
        if record.get("source_sha256") != digest(path):
            errors.append(f"Source TSV hash mismatch: {rel}")
        if record.get("n_epochs_from_tsv_rows") != n:
            errors.append(f"Epoch row count mismatch: {rel}")
        if len({row.get("trial_type") for row in rows}) != 1:
            errors.append(f"Run does not contain exactly one trial_type: {rel}")
        if record.get("condition_label") != rows[0].get("trial_type"):
            errors.append(f"Condition label mismatch: {rel}")
        expected = {key: list(range(i, n, 3)) for i, key in enumerate(("A", "B", "C"))}
        if record.get("partition_indices_zero_based") != expected:
            errors.append(f"Partition row assignment mismatch: {rel}")
        expected_counts = {key: len(indices) for key, indices in expected.items()}
        if record.get("partition_counts") != expected_counts:
            errors.append(f"Partition counts mismatch: {rel}")
        if any(value <= 0 for value in expected_counts.values()):
            errors.append(f"Empty partition in run: {rel}")
        for key, value in expected_counts.items():
            current = min_sizes[key]
            min_sizes[key] = value if current is None else min(current, value)

    if manifest.get("outer_folds") != [
        {"heldout_participant": heldout,
         "training_participants": [subject for subject in participant_ids if subject != heldout]}
        for heldout in participant_ids
    ]:
        errors.append("Leave-one-participant-out fold specification mismatch")
    reported_split = manifest.get("within_run_split", {})
    if reported_split.get("n_run_tables") != len(expected_paths):
        errors.append("Run table count summary mismatch")
    if reported_split.get("n_total_metadata_epochs") != total_epochs:
        errors.append("Total metadata epoch count summary mismatch")
    if reported_split.get("minimum_partition_sizes") != min_sizes:
        errors.append("Minimum partition size summary mismatch")

    return {
        "verifier_id": "WSGZP-EEG-THREE-PARTITION-METADATA-VERIFIER-2026-10-28-v1",
        "status": "PASS_METADATA_ONLY" if not errors else "FAIL",
        "signal_samples_read": False,
        "manifest_sha256": digest(manifest_path),
        "dataset_root": str(root),
        "participants": len(participant_ids),
        "run_tables_verified": len(expected_paths),
        "metadata_epochs_verified": total_epochs,
        "minimum_partition_sizes_verified": min_sizes,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.dataset_root, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS_METADATA_ONLY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
