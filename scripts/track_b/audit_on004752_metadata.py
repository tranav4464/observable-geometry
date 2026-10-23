"""Metadata-only audit of NEMAR on004752/OpenNeuro ds004752.

Fetches a pinned GitHub tree and allowlisted small BIDS metadata only. It does
not request EDF/Zarr/signal payloads. The report stores file hashes and
aggregates, not participant-level raw trial content.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import statistics
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
COMMIT = "451405654ce2ae1c77c660d94156f82f626a0228"
TREE_URL = f"https://api.github.com/repos/nemarDatasets/on004752/git/trees/{COMMIT}?recursive=1"
RAW_BASE = f"https://raw.githubusercontent.com/nemarDatasets/on004752/{COMMIT}/"
OUT = ROOT / "outputs" / "track_b" / "data_acquisition" / "on004752_metadata_audit.json"
MAX_FILE_BYTES = 500_000
MAX_TOTAL_BYTES = 20_000_000
MAX_FILES = 1_000
ALLOW = re.compile(
    r"^(dataset_description\.json|participants\.tsv|"
    r"sub-\d+/sub-\d+_sessions\.tsv|"
    r"sub-\d+/ses-\d+/(eeg|ieeg)/sub-\d+_ses-\d+_task-verbalWM_run-\d+_"
    r"(channels\.tsv|events\.tsv|electrodes\.tsv|coordsystem\.json|"
    r"channels\.json|events\.json|electrodes\.json|eeg\.json|ieeg\.json))$"
)


def get(url: str, *, accept: str | None = None) -> bytes:
    headers = {"User-Agent": "ObservableGeometry-on004752-metadata-audit/1.0"}
    if accept:
        headers["Accept"] = accept
    for attempt in range(5):
        try:
            with urlopen(Request(url, headers=headers), timeout=30) as response:
                return response.read(MAX_TOTAL_BYTES + 1)
        except (HTTPError, URLError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable retry state")


def read_tsv(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t"))


def not_missing(value: str | None) -> bool:
    return bool(value and value.strip().lower() not in {"", "n/a", "na", "nan", "n/a"})


def summarize_channels(rows: list[dict[str, str]]) -> dict[str, object]:
    types = Counter(row.get("type", "") for row in rows)
    refs = Counter(row.get("reference", "") for row in rows if not_missing(row.get("reference")))
    statuses = Counter(row.get("status", "") for row in rows if not_missing(row.get("status")))
    return {"channel_count": len(rows), "types": dict(types), "reference_values": dict(refs), "status_values": dict(statuses), "columns": list(rows[0]) if rows else []}


def summarize_events(rows: list[dict[str, str]]) -> dict[str, object]:
    onsets = []
    for row in rows:
        if not_missing(row.get("onset")):
            onsets.append(float(row["onset"]))
    return {
        "event_count": len(rows),
        "columns": list(rows[0]) if rows else [],
        "trial_type_counts": dict(Counter(row.get("trial_type", "") for row in rows if not_missing(row.get("trial_type")))),
        "task_condition_counts": {
            field: dict(Counter(row.get(field, "") for row in rows if not_missing(row.get(field))))
            for field in ("SetSize", "Match", "Correct", "Artifact")
            if any(not_missing(row.get(field)) for row in rows)
        },
        "onset_range_seconds": [min(onsets), max(onsets)] if onsets else None,
        "event_fields": list(rows[0]) if rows else [],
    }


def main() -> None:
    tree_doc = json.loads(get(TREE_URL, accept="application/vnd.github+json").decode("utf-8"))
    if tree_doc.get("sha") != COMMIT or tree_doc.get("truncated"):
        raise RuntimeError("GitHub tree did not match the pinned commit or was truncated")
    tree = tree_doc["tree"]
    files = [item for item in tree if item.get("type") == "blob" and ALLOW.fullmatch(item["path"])]
    declared_bytes = sum(int(item.get("size", 0)) for item in files)
    if len(files) > MAX_FILES or declared_bytes > MAX_TOTAL_BYTES:
        raise RuntimeError(f"Metadata allowlist exceeds guard: files={len(files)}, bytes={declared_bytes}")
    if any(int(item.get("size", 0)) > MAX_FILE_BYTES for item in files):
        raise RuntimeError("An allowlisted metadata file exceeds the per-file size guard")

    def fetch(item: dict[str, object]) -> tuple[str, bytes]:
        path = str(item["path"])
        payload = get(RAW_BASE + path)
        if len(payload) > MAX_FILE_BYTES or len(payload) != int(item.get("size", 0)):
            raise RuntimeError(f"Size mismatch or guard for {path}: received={len(payload)} expected={item.get('size')}")
        return path, payload

    with ThreadPoolExecutor(max_workers=8) as pool:
        payloads = dict(pool.map(fetch, files))
    hashes = {path: hashlib.sha256(payload).hexdigest() for path, payload in sorted(payloads.items())}

    description = json.loads(payloads["dataset_description.json"].decode("utf-8"))
    participants = read_tsv(payloads["participants.tsv"])
    subjects = sorted({m.group(1) for p in payloads if (m := re.match(r"^(sub-\d+)/", p))})
    sessions: dict[str, dict[str, object]] = {}
    for path, payload in sorted(payloads.items()):
        match = re.match(r"^(sub-\d+)/(ses-\d+)/(eeg|ieeg)/", path)
        if not match:
            continue
        subject, session, modality = match.groups()
        key = f"{subject}/{session}"
        item = sessions.setdefault(key, {"subject": subject, "session": session, "modalities": {}})
        modality_summary = item["modalities"].setdefault(modality, {})
        if path.endswith("_channels.tsv"):
            modality_summary["channels"] = summarize_channels(read_tsv(payload))
        elif path.endswith("_events.tsv"):
            modality_summary["events"] = summarize_events(read_tsv(payload))
        elif path.endswith("_electrodes.tsv"):
            rows = read_tsv(payload)
            axes = ("x", "y", "z")
            with_xyz = [row for row in rows if all(not_missing(row.get(axis)) for axis in axes)]
            numeric_xyz = 0
            for row in with_xyz:
                try:
                    values = [float(row[axis]) for axis in axes]
                    if all(abs(value) < float("inf") for value in values):
                        numeric_xyz += 1
                except ValueError:
                    pass
            modality_summary["electrodes"] = {"contact_count": len(rows), "contacts_with_xyz_entries": len(with_xyz), "contacts_with_finite_numeric_xyz": numeric_xyz, "columns": list(rows[0]) if rows else []}
        elif path.endswith("_coordsystem.json"):
            modality_summary["coordsystem"] = json.loads(payload.decode("utf-8"))
        elif path.endswith(("_events.json", "_electrodes.json", "_eeg.json", "_ieeg.json", "_channels.json")):
            modality_summary.setdefault("sidecars", {})[Path(path).name.rsplit("_", 1)[-1].replace(".json", "")] = json.loads(payload.decode("utf-8"))

    event_alignment = {
        "paired_session_count": 0,
        "semantic_trial_table_matches": 0,
        "event_count_mismatches": [],
        "semantic_label_mismatches": [],
        "median_eeg_minus_ieeg_onset_seconds": None,
        "max_abs_eeg_minus_ieeg_onset_seconds": None,
        "notes": "Compare trial number and behavioral/task fields across modalities. Sampling rates vary by session, and event onsets use different modality sample grids; quantify offsets per paired session and resolve acquisition-trigger semantics before imposing an exact alignment criterion.",
    }
    onset_deltas = []
    for key, item in sessions.items():
        modalities = item["modalities"]
        if "eeg" not in modalities or "ieeg" not in modalities:
            continue
        ee = payloads.get(f"{item['subject']}/{item['session']}/eeg/{item['subject']}_{item['session']}_task-verbalWM_run-01_events.tsv")
        ie = payloads.get(f"{item['subject']}/{item['session']}/ieeg/{item['subject']}_{item['session']}_task-verbalWM_run-01_events.tsv")
        if ee is None or ie is None:
            continue
        event_alignment["paired_session_count"] += 1
        e_rows, i_rows = read_tsv(ee), read_tsv(ie)
        if len(e_rows) != len(i_rows):
            event_alignment["event_count_mismatches"].append(key)
            continue
        semantic_cols = ("nTrial", "duration", "SetSize", "ProbeLetter", "Match", "Correct", "ResponseTime", "Artifact")
        same = all(tuple(a.get(c, "") for c in semantic_cols) == tuple(b.get(c, "") for c in semantic_cols) for a, b in zip(e_rows, i_rows, strict=True))
        if same:
            event_alignment["semantic_trial_table_matches"] += 1
        else:
            event_alignment["semantic_label_mismatches"].append(key)
        for eeg_row, ieeg_row in zip(e_rows, i_rows, strict=True):
            if not_missing(eeg_row.get("onset")) and not_missing(ieeg_row.get("onset")):
                onset_deltas.append(float(eeg_row["onset"]) - float(ieeg_row["onset"]))
    if onset_deltas:
        event_alignment["median_eeg_minus_ieeg_onset_seconds"] = statistics.median(onset_deltas)
        event_alignment["max_abs_eeg_minus_ieeg_onset_seconds"] = max(abs(value) for value in onset_deltas)

    channel_counts = Counter()
    contact_counts = []
    event_condition_counts = {field: Counter() for field in ("SetSize", "Match", "Correct", "Artifact")}
    matched_subjects = set()
    paired_sessions = 0
    for item in sessions.values():
        mods = item["modalities"]
        if "eeg" in mods and "ieeg" in mods:
            matched_subjects.add(item["subject"])
            paired_sessions += 1
        for modality, summary in mods.items():
            for kind, count in summary.get("channels", {}).get("types", {}).items():
                channel_counts[f"{modality}:{kind}"] += count
            if modality == "ieeg" and "electrodes" in summary:
                contact_counts.append(summary["electrodes"]["contact_count"])
            if modality == "eeg" and "events" in summary:
                for field, counts in summary["events"].get("task_condition_counts", {}).items():
                    event_condition_counts[field].update(counts)

    sample_rates = Counter()
    cutoff_rows = Counter()
    for item in sessions.values():
        for modality, summary in item["modalities"].items():
            for path, payload in payloads.items():
                if path.startswith(f"{item['subject']}/{item['session']}/{modality}/") and path.endswith(("_eeg.json", "_ieeg.json")):
                    sidecar = json.loads(payload.decode("utf-8"))
                    sample_rates[f"{modality}:{sidecar.get('SamplingFrequency', 'unknown')}"] += 1
                    hardware = sidecar.get("HardwareFilters", {})
                    if hardware:
                        cutoff_rows[f"{modality}:highpass={hardware.get('HighpassFilter', {}).get('CutoffFrequency', 'unknown')}:lowpass={hardware.get('LowpassFilter', {}).get('CutoffFrequency', 'unknown')}"] += 1

    report = {
        "audit_type": "pinned_allowlisted_BIDS_metadata_only",
        "metadata_only": True,
        "signal_or_image_payloads_read": False,
        "repository": "https://github.com/nemarDatasets/on004752",
        "source_dataset": "https://doi.org/10.18112/openneuro.ds004752.v1.0.1",
        "commit": COMMIT,
        "dataset_description": description,
        "participant_rows": len(participants),
        "participant_ids": [row.get("participant_id", "") for row in participants],
        "subject_count_in_tree": len(subjects),
        "session_count_with_paired_eeg_ieeg": paired_sessions,
        "subjects_with_paired_session": sorted(matched_subjects),
        "allowlisted_file_count": len(files),
        "allowlisted_bytes_declared_and_verified": declared_bytes,
        "sha256_by_metadata_path": hashes,
        "aggregate_channel_counts_across_sessions": dict(channel_counts),
        "ieeg_contact_counts_per_contact_table": contact_counts,
        "task_condition_counts_across_paired_sessions_eeg_tables": {field: dict(counts) for field, counts in event_condition_counts.items()},
        "modality_sampling_rate_sidecar_counts": dict(sample_rates),
        "hardware_filter_sidecar_counts": dict(cutoff_rows),
        "event_alignment": event_alignment,
        "sessions": sessions,
        "scope_limit": "Metadata integrity and labels only. No EDF, Zarr, EEG, iEEG, MRI or other signal/image data were fetched. Public descriptions report MNI contact coordinates; this audit does not establish an individual-MRI forward model or source truth.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "commit", "participant_rows", "subject_count_in_tree", "session_count_with_paired_eeg_ieeg",
        "allowlisted_file_count", "allowlisted_bytes_declared_and_verified", "aggregate_channel_counts_across_sessions",
        "task_condition_counts_across_paired_sessions_eeg_tables", "modality_sampling_rate_sidecar_counts",
        "hardware_filter_sidecar_counts", "event_alignment",
    )}, indent=2))


if __name__ == "__main__":
    main()
