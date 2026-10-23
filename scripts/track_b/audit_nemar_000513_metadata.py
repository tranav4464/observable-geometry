"""Download and audit metadata only for NEMAR nm000513 v1.0.1.

This script deliberately excludes all signal payloads (EDF, BrainVision,
MAT, NPY, Zarr arrays). It is a dataset/estimand feasibility check, not an
analysis of EEG or SEEG outcomes.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
BASE = "https://data.nemar.org/nm000513/v1.0.1"
OUT = ROOT / "outputs" / "track_b" / "candidate_data" / "nm000513_v1.0.1_metadata"
REPORT = ROOT / "outputs" / "track_b" / "data_acquisition" / "nemar_nm000513_metadata_audit.json"
ALLOWED = re.compile(
    r"^(dataset_description\.json|participants\.tsv|"
    r"sub-0[1-7]/ieeg/sub-0[1-7]_space-Other_electrodes\.tsv|"
    r"sub-0[1-7]/ieeg/sub-0[1-7]_task-iis_acq-net[1-9]_(channels|events)\.tsv|"
    r"sub-0[1-7]/ieeg/sub-0[1-7]_task-iis_acq-net[1-9]_ieeg\.json)$"
)
SIGNAL_SUFFIXES = {".edf", ".eeg", ".npy", ".mat", ".zarr", ".fif", ".set"}


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "TrackB-metadata-audit/1.0"})
    with urlopen(request, timeout=90) as response:
        return response.read()


def read_tsv(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(payload.decode("utf-8-sig").splitlines(), delimiter="\t"))


def main() -> None:
    manifest_bytes = fetch(f"{BASE}/manifest.json")
    manifest = json.loads(manifest_bytes)
    selected = [entry for entry in manifest if ALLOWED.fullmatch(entry["path"])]
    if not selected:
        raise RuntimeError("Pinned manifest returned no allowlisted metadata files")
    unexpected = [entry["path"] for entry in selected if Path(entry["path"]).suffix.lower() in SIGNAL_SUFFIXES]
    if unexpected:
        raise RuntimeError(f"Signal payload entered metadata allowlist: {unexpected}")

    fetched: dict[str, bytes] = {}
    file_records = []
    for entry in sorted(selected, key=lambda item: item["path"]):
        relative = Path(entry["path"])
        destination = (OUT / relative).resolve()
        if not destination.is_relative_to(OUT.resolve()):
            raise RuntimeError(f"Path escaped metadata output directory: {entry['path']}")
        payload = fetch(entry["url"])
        if len(payload) != entry["size"]:
            raise RuntimeError(f"Size mismatch for {entry['path']}: {len(payload)} != {entry['size']}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        fetched[entry["path"]] = payload
        file_records.append({
            "path": entry["path"],
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "manifest_checksum_algorithm": entry.get("checksum_algorithm"),
            "manifest_checksum": entry.get("checksum"),
        })

    run_rows: dict[str, dict[str, object]] = {}
    total_events = 0
    for path, payload in fetched.items():
        if not path.endswith("_events.tsv"):
            continue
        rows = read_tsv(payload)
        total_events += len(rows)
        run = Path(path).name.replace("_events.tsv", "")
        run_rows[run] = {
            "participant": run.split("_")[0],
            "event_count": len(rows),
            "event_columns": list(rows[0]) if rows else [],
            "event_types": dict(Counter(row.get("trial_type", "") for row in rows)),
            "onset_range_seconds": [
                min((float(row["onset"]) for row in rows), default=None),
                max((float(row["onset"]) for row in rows), default=None),
            ],
        }

    participants = read_tsv(fetched["participants.tsv"])
    electrode_rows = [
        row
        for path, payload in fetched.items()
        if path.endswith("_electrodes.tsv")
        for row in read_tsv(payload)
    ]
    coordinate_rows = [
        row for row in electrode_rows
        if any(row.get(axis, "n/a").lower() not in {"", "n/a", "na", "n/a ", "nan"} for axis in ("x", "y", "z"))
    ]
    channel_summaries = {}
    for path, payload in fetched.items():
        if path.endswith("_channels.tsv"):
            run = Path(path).name.replace("_channels.tsv", "")
            rows = read_tsv(payload)
            channel_summaries[run] = {
                "channel_count": len(rows),
                "types": dict(Counter(row.get("type", "") for row in rows)),
                "statuses": dict(Counter(row.get("status", "") for row in rows)),
                "reference_labels": sorted({row.get("reference", "") for row in rows if row.get("reference")}),
            }
    sidecars = {
        Path(path).name: json.loads(payload.decode("utf-8-sig"))
        for path, payload in fetched.items()
        if path.endswith("_ieeg.json")
    }
    description = json.loads(fetched["dataset_description.json"].decode("utf-8-sig"))

    summary = {
        "dataset_id": "nm000513",
        "version": "v1.0.1",
        "source_manifest": f"{BASE}/manifest.json",
        "metadata_only": True,
        "signal_payloads_read": False,
        "manifest_metadata_files": len(selected),
        "participants": len(participants),
        "participant_ids": [row.get("participant_id") for row in participants],
        "networks_runs": len(run_rows),
        "event_epoch_total": total_events,
        "events_by_run": run_rows,
        "channels_by_run": channel_summaries,
        "electrode_contacts_listed": len(electrode_rows),
        "electrode_contacts_with_any_x_y_z_coordinate": len(coordinate_rows),
        "contact_coordinate_coverage": "not available in released metadata" if not coordinate_rows else "partial or present; inspect rows",
        "recording_sidecars": sidecars,
        "dataset_description": description,
        "files": file_records,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "metadata_only": True,
        "participants": len(participants),
        "networks_runs": len(run_rows),
        "event_epoch_total": total_events,
        "electrode_contacts_with_any_x_y_z_coordinate": len(coordinate_rows),
        "metadata_files": len(selected),
        "report": str(REPORT),
    }, indent=2))


if __name__ == "__main__":
    main()
