"""Metadata-only audit for the extracted iES-CCEP/WSGZP BIDS release.

The script reads JSON/TSV metadata and NumPy array headers only. It never
materializes EEG/iEEG samples, and it refuses to operate on unexpected file
layouts rather than silently guessing modality or coordinate conventions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import numpy as np


def read_json_metadata(path: Path) -> tuple[Any, bool]:
    """Parse JSON, allowing only a trailing-comma repair and report that repair."""
    raw = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(raw), False
    except json.JSONDecodeError:
        # This narrowly handles a common BIDS export defect without rewriting
        # the source. It is not a general JSON5 parser; malformed structures
        # still fail closed.
        repaired = re.sub(r",\s*([}\]])", r"\1", raw)
        if repaired == raw:
            raise
        return json.loads(repaired), True


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def npy_header(path: Path) -> dict[str, Any]:
    """Read only the NPY header; do not map or read signal samples."""
    with path.open("rb") as stream:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            shape, fortran_order, dtype = np.lib.format.read_array_header_1_0(stream)
        elif version in ((2, 0), (3, 0)):
            shape, fortran_order, dtype = np.lib.format.read_array_header_2_0(stream)
        else:  # pragma: no cover - guarded by NumPy's NPY version support
            raise ValueError(f"Unsupported NPY version {version}: {path}")
    return {
        "shape": list(shape),
        "dtype": str(dtype),
        "fortran_order": bool(fortran_order),
    }


def expected_file(path: Path, errors: list[str], label: str) -> bool:
    exists = path.is_file()
    if not exists:
        errors.append(f"missing {label}: {path.name}")
    return exists


def eeg_coordinate_contract(meta: dict[str, Any], bids_version: str | None) -> dict[str, Any]:
    """Flag EEG coordinate declarations that violate or underspecify BIDS.

    BIDS 1.6.0 does not list ``T1w`` as an EEG coordinate-system keyword.
    ``T1w`` is used as a space/file label elsewhere, but does not by itself
    define the coordinate-system convention required here. This metadata
    finding does not establish that the numeric locations are anatomically
    wrong or recover the missing transform provenance.
    """
    system = meta.get("EEGCoordinateSystem")
    description = meta.get("EEGCoordinateSystemDescription")
    landmark_system = meta.get("AnatomicalLandmarkCoordinateSystem")
    if system == "T1w" or landmark_system == "T1w":
        if bids_version == "1.6.0":
            status = "BIDS_1_6_COORDINATE_KEYWORD_NOT_ALLOWED"
            note = (
                "BIDS 1.6.0 does not list T1w as an EEG coordinate-system keyword. "
                "The label also does not define the axes/origin convention or establish "
                "the digitizer-to-MRI transform. This is metadata nonconformance, not "
                "proof that the numeric electrode locations are anatomically wrong."
            )
        else:
            status = "COORDINATE_KEYWORD_REQUIRES_VERSION_CHECK"
            note = (
                "T1w does not by itself define the axes/origin convention or establish "
                "the digitizer-to-MRI transform. Check this keyword against the exact "
                "BIDS schema used by the dataset; do not infer anatomical error from "
                "the metadata alone."
            )
    elif system == "Other" and not description:
        status = "DESCRIPTION_REQUIRED_FOR_OTHER"
        note = "BIDS requires EEGCoordinateSystemDescription when EEGCoordinateSystem is Other."
    else:
        status = "NO_TARGETED_WARNING"
        note = None
    return {
        "declared_bids_version": bids_version,
        "coordinate_system": system,
        "anatomical_landmark_coordinate_system": landmark_system,
        "coordinate_system_description_present": bool(description),
        "coordinate_semantics_status": status,
        "coordinate_semantics_note": note,
    }


def coordinate_summary(
    path: Path, sidecar: Path, errors: list[str], label: str, dataset_root: Path,
    bids_version: str | None = None,
) -> dict[str, Any]:
    if not expected_file(path, errors, f"{label} coordinate table"):
        return {"available": False}
    if not expected_file(sidecar, errors, f"{label} coordinate sidecar"):
        return {"available": False, "table": path.name}
    rows = read_tsv(path)
    meta, trailing_comma_repaired = read_json_metadata(sidecar)
    columns = set(rows[0]) if rows else set()
    has_xyz = {"x", "y", "z"}.issubset(columns)
    finite_xyz = True
    if has_xyz:
        for row in rows:
            try:
                finite_xyz &= all(np.isfinite(float(row[key])) for key in ("x", "y", "z"))
            except (TypeError, ValueError):
                finite_xyz = False
    result = {
        "available": bool(rows),
        "file": path.name,
        "sidecar": sidecar.name,
        "n_rows": len(rows),
        "columns": sorted(columns),
        "coordinate_units": meta.get("EEGCoordinateUnits") or meta.get("iEEGCoordinateUnits"),
        "coordinate_system": meta.get("EEGCoordinateSystem") or meta.get("iEEGCoordinateSystem"),
        "intended_for": meta.get("IntendedFor"),
        "intended_for_target_exists": (
            (dataset_root / str(meta["IntendedFor"]).lstrip("/" )).is_file()
            if meta.get("IntendedFor") else None
        ),
        "has_xyz": has_xyz,
        "finite_xyz": bool(finite_xyz),
        "names_unique": len({row.get("name", "") for row in rows}) == len(rows),
        "sha256_table": sha256(path),
        "sha256_sidecar": sha256(sidecar),
        "sidecar_had_trailing_comma": trailing_comma_repaired,
    }
    if label == "scalp EEG":
        result["bids_coordinate_contract"] = eeg_coordinate_contract(meta, bids_version)
    return result


def audit_subject(subject_dir: Path, deriv_root: Path, bids_version: str | None = None) -> dict[str, Any]:
    subject = subject_dir.name
    errors: list[str] = []
    anat = subject_dir / "anat" / f"{subject}_T1w.nii"
    if not expected_file(anat, errors, "participant MRI"):
        anat_summary = {"available": False}
    else:
        anat_summary = {"available": True, "name": anat.name, "bytes": anat.stat().st_size,
                        "sha256": sha256(anat)}

    eeg_dir = deriv_root / subject / "eeg"
    ieeg_dir = deriv_root / subject / "ieeg"
    eeg_prefix = f"{subject}_task-ccepcoreg"
    eeg_coords = coordinate_summary(
        eeg_dir / f"{eeg_prefix}_electrodes.tsv",
        eeg_dir / f"{eeg_prefix}_coordsystem.json", errors, "scalp EEG", subject_dir.parent,
        bids_version,
    )
    ieeg_coords = coordinate_summary(
        ieeg_dir / f"{eeg_prefix}_space-T1w_electrodes.tsv",
        ieeg_dir / f"{eeg_prefix}_space-T1w_coordsystem.json", errors, "SEEG T1w", subject_dir.parent,
    )
    ieeg_mni = coordinate_summary(
        ieeg_dir / f"{eeg_prefix}_space-MNI152NLin2009aSym_electrodes.tsv",
        ieeg_dir / f"{eeg_prefix}_space-MNI152NLin2009aSym_coordsystem.json", errors, "SEEG MNI", subject_dir.parent,
    )

    geometry_paths = {
        "eeg": eeg_dir / f"{eeg_prefix}_electrodes.tsv",
        "ieeg": ieeg_dir / f"{eeg_prefix}_space-T1w_electrodes.tsv",
    }
    geometry_names: dict[str, set[str]] = {}
    for modality, geometry_path in geometry_paths.items():
        if geometry_path.is_file():
            geometry_names[modality] = {
                row.get("name", "") for row in read_tsv(geometry_path) if row.get("name")
            }

    modalities: dict[str, dict[str, Any]] = {}
    run_sets: dict[str, set[str]] = {}
    for modality, folder in (("eeg", eeg_dir), ("ieeg", ieeg_dir)):
        run_files = sorted(folder.glob(f"{subject}_task-ccepcoreg_run-*_epochs.npy"))
        runs: dict[str, Any] = {}
        run_set: set[str] = set()
        refs: set[str] = set()
        filters: set[tuple[str, str, str]] = set()
        sfreqs: set[str] = set()
        unit_values: set[str] = set()
        good_counts: list[int] = []
        bad_counts: list[int] = []
        for array_path in run_files:
            match = re.search(r"_run-(\d+)_epochs\.npy$", array_path.name)
            if not match:
                errors.append(f"unrecognized run name: {array_path.name}")
                continue
            run = match.group(1)
            run_set.add(run)
            stem = array_path.name.removesuffix("_epochs.npy")
            channels_path = folder / f"{stem}_channels.tsv"
            epochs_path = folder / f"{stem}_epochs.tsv"
            json_path = folder / f"{stem}_epochs.json"
            if not all(expected_file(p, errors, f"{modality} run {run} metadata")
                       for p in (channels_path, epochs_path, json_path)):
                continue
            header = npy_header(array_path)
            channels = read_tsv(channels_path)
            epochs = read_tsv(epochs_path)
            meta, trailing_comma_repaired = read_json_metadata(json_path)
            if len(header["shape"]) != 3:
                errors.append(f"{modality} run {run} array is not 3D: {header['shape']}")
            elif header["shape"][0] != len(epochs):
                errors.append(f"{modality} run {run} epoch count differs from TSV")
            elif header["shape"][1] != len(channels):
                errors.append(f"{modality} run {run} channel count differs from TSV")
            for channel in channels:
                refs.add(channel.get("reference", ""))
                filters.add((channel.get("low_cutoff", ""), channel.get("high_cutoff", ""),
                             channel.get("sampling_frequency", "")))
                sfreqs.add(channel.get("sampling_frequency", ""))
                unit_values.add(channel.get("units", ""))
            statuses = [c.get("status", "").lower() for c in channels]
            channel_geometry_missing = sorted({c.get("name", "") for c in channels
                                                if c.get("name")} - geometry_names.get(modality, set()))
            channel_geometry_missing_good = sorted(c.get("name", "") for c in channels
                                                   if c.get("status", "").lower() == "good"
                                                   and c.get("name", "") in channel_geometry_missing)
            good_counts.append(sum(status == "good" for status in statuses))
            bad_counts.append(sum(status == "bad" for status in statuses))
            runs[run] = {
                "n_epochs": len(epochs),
                "array_shape_header_only": header["shape"],
                "array_dtype": header["dtype"],
                "array_bytes": array_path.stat().st_size,
                "channels": len(channels),
                "channels_good": sum(status == "good" for status in statuses),
                "channels_bad": sum(status == "bad" for status in statuses),
                "channel_names_without_exact_native_geometry": channel_geometry_missing,
                "good_channel_names_without_exact_native_geometry": channel_geometry_missing_good,
                "duration_values_s": sorted({r.get("duration", "") for r in epochs}),
                "zero_time_values_s": sorted({r.get("zero_time", "") for r in epochs}),
                "stimulation_descriptions": sorted({r.get("trial_type", "") for r in epochs}),
                "stimulation_description_counts": dict(sorted(Counter(
                    row.get("trial_type", "") for row in epochs
                ).items())),
                "epoch_tsv_columns": sorted(epochs[0]) if epochs else [],
                "has_unique_epoch_identifier": any(
                    key in (set(epochs[0]) if epochs else set())
                    for key in ("trial_id", "event_id", "sample", "onset")
                ),
                "baseline_correction": meta.get("BaselineCorrection"),
                "baseline_method": meta.get("BaselineCorrectionMethod"),
                "baseline_period_s": meta.get("BaselinePeriod"),
                "json_trailing_comma_repaired_for_reading": trailing_comma_repaired,
                "source_file_declared": meta.get("Sources"),
                "source_file_present": False,
                "metadata_hashes": {
                    p.name: sha256(p) for p in (channels_path, epochs_path, json_path)
                },
            }
            source_rel = str(meta.get("Sources", "")).lstrip("/")
            runs[run]["source_file_present"] = bool(source_rel and (subject_dir.parent / source_rel).is_file())
        modalities[modality] = {
            "run_count": len(run_set),
            "runs": runs,
            "references": sorted(refs),
            "filter_sampling_contracts": [list(x) for x in sorted(filters)],
            "sampling_frequencies": sorted(sfreqs),
            "units": sorted(unit_values),
            "good_channels_range": [min(good_counts), max(good_counts)] if good_counts else None,
            "bad_channels_range": [min(bad_counts), max(bad_counts)] if bad_counts else None,
            "n_epochs_total": sum(r["n_epochs"] for r in runs.values()),
            "npy_bytes_total": sum(r["array_bytes"] for r in runs.values()),
        }
        run_sets[modality] = run_set

    paired_runs = sorted(run_sets.get("eeg", set()) & run_sets.get("ieeg", set()))
    eeg_only = sorted(run_sets.get("eeg", set()) - run_sets.get("ieeg", set()))
    ieeg_only = sorted(run_sets.get("ieeg", set()) - run_sets.get("eeg", set()))
    if eeg_only or ieeg_only:
        errors.append(f"unpaired EEG/iEEG runs: EEG-only={eeg_only}, iEEG-only={ieeg_only}")

    paired_epoch_inventory = []
    for run in paired_runs:
        eeg_run = modalities["eeg"]["runs"].get(run)
        ieeg_run = modalities["ieeg"]["runs"].get(run)
        if eeg_run is None or ieeg_run is None:
            continue
        paired_epoch_inventory.append({
            "run": run,
            "eeg_epochs": eeg_run["n_epochs"],
            "ieeg_epochs": ieeg_run["n_epochs"],
            "same_trial_type_counts": eeg_run["stimulation_description_counts"]
                == ieeg_run["stimulation_description_counts"],
            "same_trial_type_set": set(eeg_run["stimulation_descriptions"])
                == set(ieeg_run["stimulation_descriptions"]),
            "eeg_has_unique_epoch_identifier": eeg_run["has_unique_epoch_identifier"],
            "ieeg_has_unique_epoch_identifier": ieeg_run["has_unique_epoch_identifier"],
        })

    return {
        "participant": subject,
        "mri": anat_summary,
        "scalp_electrode_geometry": eeg_coords,
        "seeg_native_geometry": ieeg_coords,
        "seeg_mni_geometry": ieeg_mni,
        "paired_run_count": len(paired_runs),
        "paired_runs": paired_runs,
        "paired_epoch_inventory": paired_epoch_inventory,
        "modalities": modalities,
        "metadata_errors": errors,
        "metadata_status": "PASS" if not errors else "REVIEW",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.dataset_root.resolve()
    errors: list[str] = []
    required = ["dataset_description.json", "LICENSE", "participants.tsv", "participants.json"]
    for name in required:
        if not (root / name).is_file():
            errors.append(f"missing root file {name}")
    deriv_root = root / "derivatives" / "epochs"
    if not deriv_root.is_dir():
        errors.append("missing derivatives/epochs directory")
    if errors:
        raise SystemExit("Dataset root failed required-file checks: " + "; ".join(errors))

    root_desc, root_desc_repaired = read_json_metadata(root / "dataset_description.json")
    bids_version = root_desc.get("BIDSVersion")
    participants = read_tsv(root / "participants.tsv")
    subjects = [row["participant_id"] for row in participants]
    subject_reports = [audit_subject(root / subject, deriv_root, bids_version) for subject in subjects]
    deriv_desc, deriv_desc_repaired = read_json_metadata(deriv_root / "dataset_description.json")
    license_text = (root / "LICENSE").read_text(encoding="utf-8-sig", errors="replace")
    license_first_line = next((line.strip() for line in license_text.splitlines() if line.strip()), "")

    all_runs = sum(s["paired_run_count"] for s in subject_reports)
    eeg_epochs = sum(s["modalities"].get("eeg", {}).get("n_epochs_total", 0) for s in subject_reports)
    ieeg_epochs = sum(s["modalities"].get("ieeg", {}).get("n_epochs_total", 0) for s in subject_reports)
    report = {
        "audit_id": "WSGZP-METADATA-2026-10-29-v2",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_root": str(root),
        "data_boundary": "Metadata and NPY headers only; signal samples were not loaded by this audit.",
        "dataset_name": root_desc.get("Name"),
        "bids_version": root_desc.get("BIDSVersion"),
        "license_label": root_desc.get("License"),
        "license_file_first_nonempty_line": license_first_line,
        "license_sha256": sha256(root / "LICENSE"),
        "root_metadata_hashes": {name: sha256(root / name) for name in required if name != "LICENSE"},
        "derivative_description": deriv_desc,
        "json_format_warnings": [
            name for name, repaired in (
                ("dataset_description.json", root_desc_repaired),
                ("derivatives/epochs/dataset_description.json", deriv_desc_repaired),
            ) if repaired
        ],
        "coordinate_sidecar_warnings": sorted({
            "Scalp EEG coordsystem sidecars reference missing *_T1.nii paths; "
            "the corresponding participant files are *_T1w.nii."
            for subject in subject_reports
            if subject["scalp_electrode_geometry"].get("intended_for")
            and subject["scalp_electrode_geometry"].get("intended_for_target_exists") is False
        }),
        "eeg_coordinate_contract_warnings": sorted({
            subject["scalp_electrode_geometry"]["bids_coordinate_contract"]["coordinate_semantics_note"]
            for subject in subject_reports
            if subject["scalp_electrode_geometry"].get("bids_coordinate_contract", {}).get("coordinate_semantics_note")
        }),
        "derivative_description_sha256": sha256(deriv_root / "dataset_description.json"),
        "participant_count": len(subjects),
        "participants": subjects,
        "paired_run_count": all_runs,
        "paired_run_epoch_count_mismatch_count": sum(
            item["eeg_epochs"] != item["ieeg_epochs"]
            for subject in subject_reports for item in subject["paired_epoch_inventory"]
        ),
        "paired_runs_with_matching_trial_type_counts": sum(
            item["same_trial_type_counts"]
            for subject in subject_reports for item in subject["paired_epoch_inventory"]
        ),
        "paired_runs_with_same_trial_type_set": sum(
            item["same_trial_type_set"]
            for subject in subject_reports for item in subject["paired_epoch_inventory"]
        ),
        "paired_runs_with_unique_epoch_identifiers": sum(
            item["eeg_has_unique_epoch_identifier"] and item["ieeg_has_unique_epoch_identifier"]
            for subject in subject_reports for item in subject["paired_epoch_inventory"]
        ),
        "good_channel_geometry_mismatch_count": sum(
            len(run.get("good_channel_names_without_exact_native_geometry", []))
            for subject in subject_reports
            for modality in subject["modalities"].values()
            for run in modality["runs"].values()
        ),
        "participants_with_good_channel_geometry_mismatch": sorted({
            subject["participant"] for subject in subject_reports
            if any(run.get("good_channel_names_without_exact_native_geometry")
                   for modality in subject["modalities"].values()
                   for run in modality["runs"].values())
        }),
        "eeg_epoch_count_from_tsv": eeg_epochs,
        "ieeg_epoch_count_from_tsv": ieeg_epochs,
        "participant_metadata_failures": [s["participant"] for s in subject_reports if s["metadata_status"] != "PASS"],
        "participants_detail": subject_reports,
        "aggregate": {
            "has_individual_mri": all(s["mri"].get("available") for s in subject_reports),
            "has_scalp_geometry": all(s["scalp_electrode_geometry"].get("available") for s in subject_reports),
            "has_native_seeg_geometry": all(s["seeg_native_geometry"].get("available") for s in subject_reports),
            "has_mni_seeg_geometry": all(s["seeg_mni_geometry"].get("available") for s in subject_reports),
            "all_eeg_ieeg_runs_paired": all(s["paired_run_count"] == s["modalities"]["eeg"]["run_count"] == s["modalities"]["ieeg"]["run_count"] for s in subject_reports),
            "unprocessed_source_files_available": any(r.get("source_file_present") for s in subject_reports for modality in s["modalities"].values() for r in modality["runs"].values()),
        },
        "metadata_status": "PASS" if (
            not any(s["metadata_errors"] for s in subject_reports)
            and not root_desc_repaired and not deriv_desc_repaired
        ) else "REVIEW",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "audit_id", "participant_count", "paired_run_count", "eeg_epoch_count_from_tsv",
        "ieeg_epoch_count_from_tsv", "paired_run_epoch_count_mismatch_count",
        "paired_runs_with_same_trial_type_set", "paired_runs_with_unique_epoch_identifiers",
        "good_channel_geometry_mismatch_count", "participants_with_good_channel_geometry_mismatch",
        "license_label", "license_file_first_nonempty_line",
        "aggregate", "participant_metadata_failures", "metadata_status",
    )} | {"output": str(args.output.resolve())}, indent=2))


if __name__ == "__main__":
    main()
