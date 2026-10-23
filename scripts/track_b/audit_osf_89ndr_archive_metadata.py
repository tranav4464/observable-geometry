"""Audit only allowlisted BIDS metadata in the public Zauli et al. archive.

This uses HTTP Range requests against the pinned OSF file g5dcs. It never
downloads EEG/SEEG arrays, MRI images, or other signal/image payloads. It
fetches only small allowlisted TSV/JSON/license metadata entries.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import struct
import time
import threading
import zlib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
URL = "https://files.de-1.osf.io/v1/resources/89ndr/providers/osfstorage/658d91437094e948cba1749f"
FILE_ID = "g5dcs"
OUT = ROOT / "outputs" / "track_b" / "data_acquisition" / "osf_89ndr_archive_metadata.json"
TAIL_BYTES = 200_000
MAX_DIRECTORY_BYTES = 20_000_000
MAX_METADATA_BYTES = 300_000
_RANGE_METRICS_LOCK = threading.Lock()
_RANGE_METRICS = {"requests": 0, "bytes": 0}
METADATA_PATH = re.compile(
    r"^coreg-spikes/(participants\.(tsv|json)|LICENSE\.txt|"
    r"sub-\d{2}/anat/sub-\d{2}_T1w\.json|"
    r"derivatives/epochs/sub-\d{2}/(eeg|ieeg)/"
    r"sub-\d{2}(_space-[^/]+)?_(coordsystem\.json|electrodes\.tsv)|"
    r"derivatives/epochs/sub-\d{2}/(eeg|ieeg)/sub-\d{2}_task-rest_run-\d{2}_(channels\.tsv|epochs\.tsv|epochs\.json))$"
)


def ranged_get(start: int, end: int, total_size: int) -> bytes:
    expected_length = end - start + 1
    for attempt in range(6):
        request = Request(URL, headers={"Range": f"bytes={start}-{end}", "User-Agent": "TrackB-OSF-metadata-audit/1.0"})
        try:
            with urlopen(request, timeout=120) as response:
                content_range = response.headers.get("Content-Range", "")
                expected = f"bytes {start}-{end}/{total_size}"
                if response.status != 206 or content_range != expected:
                    if not (response.status == 200 and response.headers.get("Content-Length") == str(expected_length)):
                        raise RuntimeError(f"Range request was not honored: status={response.status}, range={content_range!r}")
                payload = response.read(expected_length + 1)
                if len(payload) != expected_length:
                    raise RuntimeError("Short range response")
                with _RANGE_METRICS_LOCK:
                    _RANGE_METRICS["requests"] += 1
                    _RANGE_METRICS["bytes"] += len(payload)
                return payload
        except HTTPError as exc:
            if exc.code != 429 or attempt == 5:
                raise
            retry_after = exc.headers.get("Retry-After")
            delay = min(60, int(retry_after)) if retry_after and retry_after.isdigit() else min(60, 2 ** (attempt + 1))
            time.sleep(delay)
    raise RuntimeError("OSF range retry limit reached")


def read_metadata_entry(entry: dict[str, object], total_size: int) -> bytes:
    offset = int(entry["local_header_offset"])
    compressed_size = int(entry["compressed_bytes"])
    if compressed_size > MAX_METADATA_BYTES:
        raise RuntimeError(f"Compressed metadata file exceeds size guard: {entry['path']}")
    fixed = ranged_get(offset, offset + 29, total_size)
    local = struct.Struct("<4s5H3L2H")
    signature, _version, _flags, method, _time, _date, _crc, _csize, _usize, name_len, extra_len = local.unpack(fixed)
    if signature != b"PK\x03\x04" or method != int(entry["compression_method"]):
        raise RuntimeError(f"Local ZIP header mismatch for {entry['path']}")
    content_start = offset + 30 + name_len + extra_len
    header_and_data = ranged_get(offset + 30, content_start + compressed_size - 1, total_size)
    local_name = header_and_data[:name_len].decode("utf-8", errors="replace")
    if local_name != entry["path"]:
        raise RuntimeError(f"ZIP name mismatch: {local_name!r} != {entry['path']!r}")
    compressed = header_and_data[name_len + extra_len:]
    if method == 0:
        payload = compressed
    elif method == 8:
        payload = zlib.decompress(compressed, -15)
    else:
        raise RuntimeError(f"Unsupported ZIP compression method {method} for {entry['path']}")
    if len(payload) != int(entry["uncompressed_bytes"]):
        raise RuntimeError(f"Uncompressed metadata size mismatch for {entry['path']}")
    if (zlib.crc32(payload) & 0xFFFFFFFF) != int(entry["crc32"]):
        raise RuntimeError(f"CRC mismatch for {entry['path']}")
    return payload


def main() -> None:
    request = Request(URL, method="HEAD", headers={"User-Agent": "TrackB-OSF-metadata-audit/1.0"})
    with urlopen(request, timeout=60) as response:
        total_size = int(response.headers["Content-Length"])
        filename_meta = response.headers.get("X-Waterbutler-Metadata", "")
    # The exact OSF object is pinned by its public GUID and expected archive size.
    if FILE_ID != "g5dcs" or total_size != 2_076_272_259:
        raise RuntimeError(f"Pinned OSF object metadata changed: size={total_size}")

    tail_start = max(0, total_size - TAIL_BYTES)
    tail = ranged_get(tail_start, total_size - 1, total_size)
    eocd_sig = b"PK\x05\x06"
    eocd_at = tail.rfind(eocd_sig)
    if eocd_at < 0 or len(tail) - eocd_at < 22:
        raise RuntimeError("ZIP end-of-central-directory record not found")
    fields = struct.unpack_from("<4s4H2LH", tail, eocd_at)
    _, disk, central_disk, entries_disk, entries_total, central_size, central_offset, comment_len = fields
    if disk or central_disk or entries_disk != entries_total:
        raise RuntimeError("Multi-disk ZIP archives are unsupported")
    if 0xFFFFFFFF in (central_size, central_offset) or 0xFFFF in (entries_total,):
        raise RuntimeError("ZIP64 archive is unsupported by this metadata-only auditor")
    if central_size > MAX_DIRECTORY_BYTES or central_offset + central_size > total_size:
        raise RuntimeError("Invalid or unexpectedly large central directory")
    directory = ranged_get(central_offset, central_offset + central_size - 1, total_size)

    entries = []
    pos = 0
    header = struct.Struct("<4s6H3L5H2L")
    while pos < len(directory):
        if directory[pos:pos + 4] != b"PK\x01\x02" or pos + 46 > len(directory):
            raise RuntimeError(f"Malformed central-directory entry at byte {pos}")
        values = header.unpack_from(directory, pos)
        compressed_size, uncompressed_size = values[8], values[9]
        name_len, extra_len, entry_comment_len = values[10], values[11], values[12]
        record_end = pos + 46 + name_len + extra_len + entry_comment_len
        if record_end > len(directory):
            raise RuntimeError("Truncated central-directory entry")
        name = directory[pos + 46:pos + 46 + name_len].decode("utf-8", errors="replace")
        if compressed_size == 0xFFFFFFFF or uncompressed_size == 0xFFFFFFFF:
            raise RuntimeError("ZIP64 entry sizes are unsupported")
        entries.append({
            "path": name,
            "compressed_bytes": compressed_size,
            "uncompressed_bytes": uncompressed_size,
            "compression_method": values[4],
            "crc32": values[7],
            "local_header_offset": values[16],
        })
        pos = record_end

    if len(entries) != entries_total:
        raise RuntimeError(f"Central-directory count mismatch: parsed={len(entries)} expected={entries_total}")

    suffix_counts = Counter(Path(item["path"]).suffix.lower() for item in entries if not item["path"].endswith("/"))
    subject_ids = sorted({match.group(1) for item in entries if (match := re.search(r"(?:^|/)sub-([A-Za-z0-9]+)(?:/|$)", item["path"]))})
    metadata_entries = [item for item in entries if METADATA_PATH.fullmatch(item["path"])]
    if len(metadata_entries) > 256:
        raise RuntimeError(f"Allowlisted metadata file count exceeds guard: {len(metadata_entries)}")
    if any(int(item["uncompressed_bytes"]) > MAX_METADATA_BYTES for item in metadata_entries):
        raise RuntimeError("Allowlisted metadata file exceeds the size guard")
    # Fetch only the allowlisted metadata payloads, concurrently. No arbitrary
    # archive member is opened, and the compressed/uncompressed size guards
    # remain in force for every file.
    with ThreadPoolExecutor(max_workers=2) as pool:
        payloads = list(pool.map(lambda item: read_metadata_entry(item, total_size), metadata_entries))
    read_metadata = {item["path"]: payload for item, payload in zip(metadata_entries, payloads, strict=True)}
    metadata_hashes = {path: hashlib.sha256(payload).hexdigest() for path, payload in read_metadata.items()}

    participants = []
    participant_payload = read_metadata.get("coreg-spikes/participants.tsv")
    if participant_payload:
        participants = list(csv.DictReader(io.StringIO(participant_payload.decode("utf-8-sig")), delimiter="\t"))
    event_summaries = {}
    channel_summaries = {}
    electrode_summaries = {}
    sidecar_summaries = {}
    for path, payload in read_metadata.items():
        if path.endswith("_epochs.tsv"):
            rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t"))
            trial_types = Counter(row.get("trial_type", "") for row in rows)
            event_summaries[path] = {
                "row_count": len(rows),
                "columns": list(rows[0]) if rows else [],
                "trial_type_counts": dict(trial_types),
                "zero_time_range": [
                    min((float(row["zero_time"]) for row in rows if row.get("zero_time")), default=None),
                    max((float(row["zero_time"]) for row in rows if row.get("zero_time")), default=None),
                ],
                "duration_range": [
                    min((float(row["duration"]) for row in rows if row.get("duration")), default=None),
                    max((float(row["duration"]) for row in rows if row.get("duration")), default=None),
                ],
            }
        elif path.endswith("_channels.tsv"):
            rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t"))
            types = Counter(row.get("type", "") for row in rows)
            channel_summaries[path] = {"channel_count": len(rows), "types": dict(types)}
        elif path.endswith("_electrodes.tsv"):
            rows = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig")), delimiter="\t"))
            coord_rows = [row for row in rows if all(row.get(axis, "n/a").lower() not in {"", "n/a", "na", "nan"} for axis in ("x", "y", "z"))]
            electrode_summaries[path] = {"contact_count": len(rows), "contacts_with_xyz": len(coord_rows), "columns": list(rows[0]) if rows else []}
        elif path.endswith("_epochs.json") or path.endswith("_coordsystem.json") or path.endswith("_T1w.json"):
            try:
                sidecar_summaries[path] = json.loads(payload.decode("utf-8-sig"))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSON metadata at {path}") from exc
    report = {
        "audit_type": "allowlisted_zip_metadata_only",
        "metadata_only": True,
        "metadata_file_payloads_read": True,
        "signal_or_image_payloads_read": False,
        "osf_project": "89ndr",
        "osf_file_guid": FILE_ID,
        "download_url": URL,
        "archive_size_bytes": total_size,
        "central_directory_entry_count": len(entries),
        "subject_ids_from_paths": subject_ids,
        "subject_count_from_paths": len(subject_ids),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "candidate_bids_metadata_paths": [item["path"] for item in metadata_entries],
        "metadata_sha256": metadata_hashes,
        "participants_rows": participants,
        "event_epoch_summaries": event_summaries,
        "channel_summaries": channel_summaries,
        "electrode_coordinate_summaries": electrode_summaries,
        "metadata_sidecars": sidecar_summaries,
        "archive_entries": entries,
        "range_request_count": _RANGE_METRICS["requests"],
        "range_bytes_requested": _RANGE_METRICS["bytes"],
        "metadata_compressed_payload_bytes": sum(int(item["compressed_bytes"]) for item in metadata_entries),
        "metadata_uncompressed_payload_bytes": sum(int(item["uncompressed_bytes"]) for item in metadata_entries),
        "index_bytes_requested": TAIL_BYTES + central_size,
        "osf_waterbutler_metadata_present": bool(filename_meta),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "audit_type", "metadata_only", "metadata_file_payloads_read", "signal_or_image_payloads_read", "archive_size_bytes",
        "central_directory_entry_count", "subject_ids_from_paths", "suffix_counts", "range_bytes_requested",
    )}, indent=2))


if __name__ == "__main__":
    main()
