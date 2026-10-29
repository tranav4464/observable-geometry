"""Validate WSGZP EEG coordinate sidecars without copying neural data.

Builds a temporary metadata-only BIDS fixture from the released coordinate
sidecars/electrode tables and runs a pinned BIDS Validator. The source dataset
is read-only; no EEG/iEEG recordings, NPY payloads, or MRI images are copied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


VALIDATOR_PACKAGE = "bids-validator@1.14.10"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_fixture(
    dataset_root: Path, fixture_root: Path, participant: str
) -> list[dict[str, str]]:
    """Copy one participant's coordinate JSON/electrodes TSV into a BIDS fixture."""
    dataset_root = dataset_root.resolve(strict=True)
    if fixture_root.exists():
        raise FileExistsError(f"Refusing to overwrite existing fixture: {fixture_root}")
    root_description = json.loads((dataset_root / "dataset_description.json").read_text(encoding="utf-8"))
    bids_version = root_description.get("BIDSVersion")
    if bids_version != "1.6.0":
        raise ValueError(f"Expected the source dataset's declared BIDSVersion 1.6.0, got {bids_version!r}")

    derivative_root = dataset_root / "derivatives" / "epochs"
    if not derivative_root.is_dir():
        raise FileNotFoundError(f"Missing expected derivative folder: {derivative_root}")

    copied: list[dict[str, str]] = []
    if re.fullmatch(r"sub-[A-Za-z0-9]+", participant) is None:
        raise ValueError("participant must be a simple BIDS sub-<label> directory name")
    subject_path = dataset_root / participant
    if not subject_path.is_dir():
        raise FileNotFoundError(f"Participant directory not found: {subject_path}")

    fixture_root.mkdir(parents=True)
    description: dict[str, Any] = {
        "Name": "WSGZP coordinate-sidecar schema fixture (metadata only)",
        "BIDSVersion": bids_version,
        "DatasetType": "derivative",
        "GeneratedBy": [{"Name": "Observable Geometry metadata-only validator fixture"}],
        "Authors": ["Observable Geometry validation workflow"],
    }
    (fixture_root / "dataset_description.json").write_text(
        json.dumps(description, indent=2) + "\n", encoding="utf-8"
    )

    subject = subject_path.name
    source_eeg = derivative_root / subject / "eeg"
    output_eeg = fixture_root / subject / "eeg"
    coordsystem = source_eeg / f"{subject}_task-ccepcoreg_coordsystem.json"
    electrodes = source_eeg / f"{subject}_task-ccepcoreg_electrodes.tsv"
    if not coordsystem.is_file() or not electrodes.is_file():
        raise FileNotFoundError(f"Missing coordinate metadata for {subject}")
    output_eeg.mkdir(parents=True)
    for source in (coordsystem, electrodes):
        destination = output_eeg / source.name
        shutil.copyfile(source, destination)
        copied.append({
            "subject": subject,
            "name": source.name,
            "sha256_source": sha256(source),
            "sha256_fixture": sha256(destination),
        })
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--participant", default="sub-01")
    args = parser.parse_args()
    output_dir = args.output_directory.resolve()
    dataset_root = args.dataset_root.resolve(strict=True)
    if output_dir == dataset_root or output_dir.is_relative_to(dataset_root):
        raise ValueError("Output directory must be outside the source dataset")
    output_dir.mkdir(parents=True, exist_ok=False)
    fixture = output_dir / "fixture"
    copied = build_fixture(dataset_root, fixture, args.participant)

    npx = shutil.which("npx")
    if npx is None:
        raise RuntimeError("npx was not found; install Node.js/npm to run the pinned BIDS Validator")
    version_command = [npx, "--yes", f"--package={VALIDATOR_PACKAGE}", "bids-validator", "--version"]
    version = subprocess.run(version_command, check=True, capture_output=True, text=True)
    validator_version = version.stdout.strip()
    if validator_version != "1.14.10":
        raise RuntimeError(f"Expected BIDS Validator 1.14.10, got {validator_version!r}")

    result_path = output_dir / "validator.json"
    command = [npx, "--yes", f"--package={VALIDATOR_PACKAGE}", "bids-validator", str(fixture), "--ignoreNiftiHeaders", "--json"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    result_path.write_text(result.stdout, encoding="utf-8")
    (output_dir / "validator.stderr.log").write_text(result.stderr, encoding="utf-8")
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Validator did not emit JSON; see {output_dir / 'validator.stderr.log'}") from exc

    coordinate_errors: list[dict[str, str]] = []
    for group in report.get("issues", {}).get("errors", []):
        for issue in group.get("files", []):
            evidence = str(issue.get("evidence") or "")
            file_info = issue.get("file") or {}
            relative_path = str(file_info.get("relativePath") or "")
            if (
                "CoordinateSystem should be equal to one of the allowed values" in evidence
                and relative_path.endswith("_coordsystem.json")
            ):
                coordinate_errors.append({"path": relative_path, "evidence": evidence})
    expected_paths = {
        f"/{item['subject']}/eeg/{item['name']}"
        for item in copied if item["name"].endswith("_coordsystem.json")
    }
    expected = {
        (path, field)
        for path in expected_paths
        for field in (".EEGCoordinateSystem", ".AnatomicalLandmarkCoordinateSystem")
    }
    observed = {
        (item["path"], field)
        for item in coordinate_errors
        for field in (".EEGCoordinateSystem", ".AnatomicalLandmarkCoordinateSystem")
        if field in item["evidence"]
    }
    if result.returncode == 0 or observed != expected:
        raise RuntimeError(
            "Validator did not reproduce the expected coordinate-keyword errors. "
            f"exit={result.returncode}; expected={len(expected)} field errors; observed={len(observed)}; "
            f"see {result_path}"
        )

    manifest = {
        "scope": "coordinate metadata only; no neural recordings, NPY payloads, or MRI images copied",
        "declared_bids_version": "1.6.0",
        "validator_package": VALIDATOR_PACKAGE,
        "validator_version": validator_version,
        "validator_exit_code": result.returncode,
        "subjects": len(expected_paths),
        "metadata_files_copied": len(copied),
        "coordinate_fields_rejected": len(observed),
        "validator_diagnostic_entry_count": len(coordinate_errors),
        "coordinate_keyword_errors": coordinate_errors,
        "fixture_files": copied,
        "validator_json_sha256": sha256(result_path),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "validator_version": validator_version,
        "subjects": len(expected_paths),
        "metadata_files_copied": len(copied),
        "coordinate_fields_rejected": len(observed),
        "validator_diagnostic_entry_count": len(coordinate_errors),
        "manifest": str(output_dir / "manifest.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
