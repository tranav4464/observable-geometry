"""Read only fixed EDF headers for development recordings; never read samples."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEV_SUBJECTS = {"sub-01", "sub-02", "sub-03"}


def decode_field(raw: bytes) -> str:
    return raw.decode("latin-1", errors="replace").strip()


def read_edf_header(path: Path, dataset_root: Path) -> dict[str, Any]:
    # EDF fixed header includes the header byte count and number of signals.
    with path.open("rb") as handle:
        fixed = handle.read(256)
        if len(fixed) != 256:
            raise ValueError(f"Truncated fixed EDF header: {path}")
        declared_bytes = int(decode_field(fixed[184:192]))
        signal_count = int(decode_field(fixed[252:256]))
        expected_bytes = 256 + signal_count * 256
        if declared_bytes != expected_bytes:
            raise ValueError(
                f"Unexpected EDF header size for {path}: declared {declared_bytes}, expected {expected_bytes}"
            )
        rest = handle.read(declared_bytes - 256)
        if len(rest) != declared_bytes - 256:
            raise ValueError(f"Truncated per-signal EDF header: {path}")
    raw_header = fixed + rest

    # EDF stores each signal property as a contiguous array across channels.
    # `rest` begins immediately after the 256-byte fixed header, so its local
    # field offsets start at zero.
    cursor = 0
    labels = [decode_field(rest[cursor + 16 * i: cursor + 16 * (i + 1)]) for i in range(signal_count)]
    cursor += 16 * signal_count  # labels
    cursor += 80 * signal_count  # transducer
    dimensions = [decode_field(rest[cursor + 8 * i: cursor + 8 * (i + 1)]) for i in range(signal_count)]
    cursor += 8 * signal_count  # physical dimension
    cursor += 8 * signal_count  # physical minimum
    cursor += 8 * signal_count  # physical maximum
    cursor += 8 * signal_count  # digital minimum
    cursor += 8 * signal_count  # digital maximum
    prefilters = [decode_field(rest[cursor + 80 * i: cursor + 80 * (i + 1)]) for i in range(signal_count)]
    cursor += 80 * signal_count
    samples_per_record = [int(decode_field(rest[cursor + 8 * i: cursor + 8 * (i + 1)])) for i in range(signal_count)]

    return {
        "file": str(path.relative_to(dataset_root)),
        "header_bytes": declared_bytes,
        "signal_count_including_auxiliary_channels": signal_count,
        "header_sha256": hashlib.sha256(raw_header).hexdigest(),
        "samples_per_record": samples_per_record,
        "signals": [
            {"label": label, "physical_dimension": dimension, "prefiltering": prefilter}
            for label, dimension, prefilter in zip(labels, dimensions, prefilters)
        ],
        "sample_payload_read": False,
    }


def audit(dataset_root: Path) -> dict[str, Any]:
    dataset_root = dataset_root.resolve()
    recordings: list[dict[str, Any]] = []
    for subject in sorted(DEV_SUBJECTS):
        subject_root = dataset_root / subject
        if not subject_root.is_dir():
            raise FileNotFoundError(subject_root)
        for session_root in sorted(subject_root.glob("ses-*")):
            for modality in ("eeg", "ieeg"):
                modality_root = session_root / modality
                if not modality_root.is_dir():
                    continue
                edf_files = sorted(modality_root.glob("*.edf"))
                if len(edf_files) != 1:
                    raise ValueError(f"Expected exactly one EDF in {modality_root}, found {len(edf_files)}")
                record = read_edf_header(edf_files[0], dataset_root)
                record.update({"subject": subject, "session": session_root.name, "modality": modality})
                recordings.append(record)
    return {
        "audit_type": "development_fixed_edf_header_only",
        "development_subjects_only": sorted(DEV_SUBJECTS),
        "recording_count": len(recordings),
        "event_files_read": False,
        "sample_payload_read": False,
        "confirmation_participants_read": False,
        "recordings": recordings,
        "interpretation": (
            "EDF prefilter text records acquisition metadata, not independent verification of applied digital filters. "
            "Blank or conflicting text must remain unresolved; no sample payload is read by this script."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path("data/track_b/on004752_v1.0.0"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(audit(args.dataset_root), indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
