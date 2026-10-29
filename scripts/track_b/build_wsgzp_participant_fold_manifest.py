"""Build a metadata-only, participant-grouped WSGZP evaluation manifest.

Reads participant tables and EEG/SEEG epoch metadata only. It never opens
neural sample arrays and never splits events or runs across participant folds.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def build_manifest(dataset_root: Path, download_manifest: Path) -> dict:
    root = dataset_root.resolve()
    download_manifest = download_manifest.resolve()
    required = [root / "participants.tsv", root / "dataset_description.json",
                root / "LICENSE", download_manifest]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    participant_rows = read_tsv(root / "participants.tsv")
    if not participant_rows or "participant_id" not in participant_rows[0]:
        raise ValueError("participants.tsv lacks participant_id or is empty")
    participants = sorted(row["participant_id"] for row in participant_rows)
    if len(participants) != len(set(participants)):
        raise ValueError("participants.tsv contains duplicate participant IDs")

    run_records = []
    expected_subjects = set(participants)
    found_subjects: set[str] = set()
    session_entities: set[str] = set()
    for path in sorted((root / "derivatives" / "epochs").glob("sub-*/eeg/*_epochs.tsv")):
        relative = path.relative_to(root).as_posix()
        match = re.match(r"derivatives/epochs/(sub-[^/]+)/eeg/", relative)
        if not match:
            raise ValueError(f"Unexpected epoch table path: {relative}")
        participant = match.group(1)
        if participant not in expected_subjects:
            raise ValueError(f"Epoch table has unlisted participant: {participant}")
        rows = read_tsv(path)
        if not rows or not {"trial_type", "duration", "zero_time"}.issubset(rows[0]):
            raise ValueError(f"Unexpected or empty EEG epochs table: {relative}")
        conditions = sorted({row["trial_type"] for row in rows})
        if len(conditions) != 1:
            raise ValueError(f"Expected one condition per run table: {relative}")
        found_subjects.add(participant)
        session = re.search(r"(?:^|_)ses-([^_]+)", path.name)
        if session:
            session_entities.add(session.group(1))
        run_records.append({
            "participant_id": participant,
            "run_file": relative,
            "source_sha256": sha256(path),
            "n_metadata_rows": len(rows),
            "condition_label": conditions[0],
            "split_unit": "participant; all runs/events remain in one outer fold",
        })

    if not run_records:
        raise ValueError("No EEG epochs.tsv tables found")
    if found_subjects != expected_subjects:
        missing = sorted(expected_subjects - found_subjects)
        raise ValueError(f"Participants without EEG epoch tables: {missing}")

    folds = [{
        "fold_id": f"LOPO-{participant}",
        "heldout_participants": [participant],
        "training_participants": [item for item in participants if item != participant],
        "heldout_runs": sorted(record["run_file"] for record in run_records
                                if record["participant_id"] == participant),
    } for participant in participants]

    return {
        "manifest_id": "WSGZP-PARTICIPANT-GROUPED-METADATA-DRAFT-2026-10-28-v1",
        "status": "PRE_SIGNAL_DRAFT_NOT_PROTOCOL_LOCK",
        "signal_samples_read": False,
        "data_source": "WSGZP/ccepcoreg extracted BIDS derivative metadata",
        "dataset_root": str(root),
        "inputs_sha256": {
            "participants_tsv": sha256(root / "participants.tsv"),
            "dataset_description_json": sha256(root / "dataset_description.json"),
            "license": sha256(root / "LICENSE"),
            "download_manifest": sha256(download_manifest),
        },
        "grouping": {
            "outer_method": "leave-one-participant-out",
            "unit": "participant; all runs, sessions, and event rows stay grouped",
            "session_entities_found_in_eeg_epoch_filenames": sorted(session_entities),
            "session_entity_present": bool(session_entities),
            "run_semantics": "BIDS run tables encode stimulation conditions; not assumed to be independent sessions",
            "inner_tuning": "nested participant-grouped folds within each outer training set; exact inner assignments are frozen separately before analysis",
        },
        "participants": participants,
        "outer_folds": folds,
        "run_tables": run_records,
        "limitations": [
            "Metadata-only inventory; no EEG/SEEG sample arrays or outcomes opened.",
            "This does not validate the participant coordinate frame or forward model.",
            "The inherited preprocessing and unknown ICA fitting pool mean results remain conditional on the released processed derivative.",
            "The manifest is not a locked confirmatory protocol and does not authorize signal access.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--download-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.dataset_root, args.download_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output.resolve()),
        "status": manifest["status"],
        "signal_samples_read": False,
        "participants": len(manifest["participants"]),
        "run_tables": len(manifest["run_tables"]),
        "metadata_rows": sum(record["n_metadata_rows"] for record in manifest["run_tables"]),
        "session_entity_present": manifest["grouping"]["session_entity_present"],
    }, indent=2))


if __name__ == "__main__":
    main()
