"""Independently verify a metadata-only WSGZP participant-fold manifest.

This verifier intentionally does not import the manifest builder. It reads
only participant and epoch TSV metadata, not EEG/SEEG signal arrays.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def verify(dataset_root: Path, download_manifest: Path, manifest_path: Path) -> dict:
    root = dataset_root.resolve()
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("manifest_id") != "WSGZP-PARTICIPANT-GROUPED-METADATA-DRAFT-2026-10-28-v1":
        errors.append("Unexpected manifest ID")
    if manifest.get("status") != "PRE_SIGNAL_DRAFT_NOT_PROTOCOL_LOCK":
        errors.append("Manifest is not clearly marked pre-signal and unlocked")
    if manifest.get("signal_samples_read") is not False:
        errors.append("Manifest does not declare that signal samples were unopened")

    participants_file = root / "participants.tsv"
    participant_ids = sorted(record["participant_id"] for record in rows(participants_file))
    if len(participant_ids) != len(set(participant_ids)):
        errors.append("Duplicate participant IDs in source table")
    expected_hashes = {
        "participants_tsv": digest(participants_file),
        "dataset_description_json": digest(root / "dataset_description.json"),
        "license": digest(root / "LICENSE"),
        "download_manifest": digest(download_manifest.resolve()),
    }
    for key, expected in expected_hashes.items():
        if manifest.get("inputs_sha256", {}).get(key) != expected:
            errors.append(f"Input hash mismatch: {key}")
    if manifest.get("participants") != participant_ids:
        errors.append("Participant inventory mismatch")

    source_paths = sorted((root / "derivatives" / "epochs").glob("sub-*/eeg/*_epochs.tsv"),
                          key=lambda path: path.relative_to(root).as_posix())
    source_records: dict[str, dict] = {}
    session_entities: set[str] = set()
    for path in source_paths:
        relative = path.relative_to(root).as_posix()
        parsed = re.match(r"derivatives/epochs/(sub-[^/]+)/eeg/", relative)
        if not parsed:
            errors.append(f"Unexpected EEG metadata path: {relative}")
            continue
        participant = parsed.group(1)
        source_rows = rows(path)
        if not source_rows or not {"trial_type", "duration", "zero_time"}.issubset(source_rows[0]):
            errors.append(f"Invalid EEG epoch metadata table: {relative}")
            continue
        conditions = {record["trial_type"] for record in source_rows}
        if len(conditions) != 1:
            errors.append(f"Multiple conditions in one run table: {relative}")
        session = re.search(r"(?:^|_)ses-([^_]+)", path.name)
        if session:
            session_entities.add(session.group(1))
        source_records[relative] = {
            "participant_id": participant,
            "source_sha256": digest(path),
            "n_metadata_rows": len(source_rows),
            "condition_label": next(iter(conditions), None),
        }
    if set(source_records) != {record["run_file"] for record in manifest.get("run_tables", [])}:
        errors.append("EEG epoch-table inventory differs from manifest")
    manifest_records = {record.get("run_file"): record for record in manifest.get("run_tables", [])}
    if len(manifest_records) != len(manifest.get("run_tables", [])):
        errors.append("Duplicate run-table record")
    for relative, source_record in source_records.items():
        stored = manifest_records.get(relative, {})
        for key, expected in source_record.items():
            if stored.get(key) != expected:
                errors.append(f"Run metadata mismatch for {relative}: {key}")
    if {record["participant_id"] for record in source_records.values()} != set(participant_ids):
        errors.append("Participant list differs from participants with EEG epoch tables")

    expected_folds = []
    for heldout in participant_ids:
        expected_folds.append({
            "fold_id": f"LOPO-{heldout}",
            "heldout_participants": [heldout],
            "training_participants": [person for person in participant_ids if person != heldout],
            "heldout_runs": sorted(relative for relative, record in source_records.items()
                                   if record["participant_id"] == heldout),
        })
    if manifest.get("outer_folds") != expected_folds:
        errors.append("Outer fold assignment does not hold out all data by participant")
    grouping = manifest.get("grouping", {})
    if grouping.get("outer_method") != "leave-one-participant-out":
        errors.append("Outer method is not leave-one-participant-out")
    if grouping.get("session_entities_found_in_eeg_epoch_filenames") != sorted(session_entities):
        errors.append("Session-entity inventory mismatch")
    if grouping.get("session_entity_present") is not bool(session_entities):
        errors.append("Session-entity presence flag mismatch")
    if len(participant_ids) < 2:
        errors.append("At least two participants are required for grouped evaluation")

    return {
        "verifier_id": "WSGZP-PARTICIPANT-GROUPED-METADATA-VERIFIER-2026-10-28-v1",
        "status": "PASS_METADATA_ONLY" if not errors else "FAIL",
        "signal_samples_read": False,
        "manifest_sha256": digest(manifest_path),
        "participants_verified": len(participant_ids),
        "run_tables_verified": len(source_records),
        "metadata_rows_verified": sum(record["n_metadata_rows"] for record in source_records.values()),
        "session_entity_present": bool(session_entities),
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--download-manifest", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.dataset_root, args.download_manifest, args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS_METADATA_ONLY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
