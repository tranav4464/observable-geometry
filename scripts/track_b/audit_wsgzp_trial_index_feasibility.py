"""Metadata-only check of WSGZP EEG bad-trial masks against exported epochs.

This script reads BIDS epoch TSV rows, JSON bad-trial masks, and NumPy headers
only. It never materializes EEG/SEEG sample arrays. A count match is a
candidate row-index correspondence, not proof of mask semantics, temporal
independence, or EEG/SEEG trial pairing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tsv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return sum(1 for _ in csv.DictReader(stream, delimiter="\t"))


def npy_header(path: Path) -> dict[str, Any]:
    """Read only the .npy header; do not access the array payload."""
    with path.open("rb") as stream:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            shape, fortran_order, dtype = np.lib.format.read_array_header_1_0(stream)
        elif version in {(2, 0), (3, 0)}:
            shape, fortran_order, dtype = np.lib.format.read_array_header_2_0(stream)
        else:
            raise ValueError(f"Unsupported .npy header version {version}: {path}")
        return {
            "version": list(version),
            "shape": list(shape),
            "dtype": str(dtype),
            "fortran_order": bool(fortran_order),
            "header_bytes": stream.tell(),
        }


def audit(dataset_root: Path, badtrials_path: Path) -> dict[str, Any]:
    badtrials = json.loads(badtrials_path.read_text(encoding="utf-8"))
    runs: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []

    for subject, subject_runs in sorted(badtrials.items()):
        for run, mask in sorted(subject_runs.items()):
            stem = f"{subject}_task-ccepcoreg_{run}_epochs"
            eeg_dir = dataset_root / "derivatives" / "epochs" / subject / "eeg"
            tsv_path = eeg_dir / f"{stem}.tsv"
            npy_path = eeg_dir / f"{stem}.npy"
            if not tsv_path.is_file() or not npy_path.is_file():
                missing.append({
                    "subject": subject,
                    "run": run,
                    "missing_tsv": str(not tsv_path.is_file()),
                    "missing_npy": str(not npy_path.is_file()),
                })
                continue

            retained_rows = tsv_rows(tsv_path)
            header = npy_header(npy_path)
            mask_len = len(mask)
            zero_count = sum(value == 0 for value in mask)
            one_count = sum(value == 1 for value in mask)
            mask_binary = all(value in (0, 1) for value in mask)
            array_rows = header["shape"][0] if header["shape"] else None
            count_match = mask_binary and zero_count == retained_rows == array_rows
            runs.append({
                "subject": subject,
                "run": run,
                "badtrial_mask_length": mask_len,
                "mask_zero_count_candidate_retained": zero_count,
                "mask_one_count_candidate_rejected": one_count,
                "mask_contains_only_zero_or_one": mask_binary,
                "exported_epoch_tsv_rows": retained_rows,
                "npy_header_shape": header["shape"],
                "npy_first_axis_matches_tsv": array_rows == retained_rows,
                "zero_count_matches_exported_rows": count_match,
                "candidate_kept_original_indices_if_zero_means_rejected": [
                    index for index, value in enumerate(mask) if value == 0
                ] if count_match else None,
                "mask_semantics_independently_documented": False,
                "trial_order_preservation_independently_documented": False,
                "event_onsets_available": False,
                "temporal_nonoverlap_verified": False,
                "paired_ieeg_trial_identity_available": False,
            })

    exact = sum(item["zero_count_matches_exported_rows"] for item in runs)
    return {
        "audit_id": "WSGZP-TRIAL-INDEX-FEASIBILITY-2026-10-28-v1",
        "dataset_root": str(dataset_root.resolve()),
        "badtrials_path": str(badtrials_path.resolve()),
        "badtrials_sha256": sha256_file(badtrials_path),
        "signal_sample_values_read": False,
        "npy_headers_only": True,
        "run_count": len(runs),
        "count_match_runs": exact,
        "count_mismatch_runs": len(runs) - exact,
        "missing_metadata_pairs": missing,
        "interpretation": (
            "Count agreement supports only a candidate mask-to-exported-row "
            "mapping if zero means rejected and row order was preserved. It "
            "does not establish event timing, non-overlap, preprocessing "
            "independence, or EEG/SEEG row pairing."
        ),
        "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--badtrials", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.dataset_root, args.badtrials)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "audit_id", "run_count", "count_match_runs", "count_mismatch_runs",
        "missing_metadata_pairs", "signal_sample_values_read", "badtrials_sha256"
    )}, indent=2))


if __name__ == "__main__":
    main()
