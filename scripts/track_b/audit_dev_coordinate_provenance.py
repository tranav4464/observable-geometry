"""Metadata-only audit of on004752 electrode-coordinate provenance.

This script only inspects filenames, electrode JSON column descriptions, and
electrode TSV headers for development participants sub-01 through sub-03. It
does not read events, signals, or any files from confirmation participants.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEV_SUBJECTS = {"sub-01", "sub-02", "sub-03"}


def sidecars_in_bids_inheritance_chain(electrodes_tsv: Path, dataset_root: Path) -> list[str]:
    """Return coordsystem sidecars discoverable along the BIDS inheritance chain."""
    found: list[str] = []
    current = electrodes_tsv.parent
    while True:
        found.extend(str(path.relative_to(dataset_root)) for path in current.glob("*_coordsystem.json"))
        if current == dataset_root:
            break
        if dataset_root not in current.parents:
            raise ValueError(f"{electrodes_tsv} is outside dataset root {dataset_root}")
        current = current.parent
    return sorted(set(found))


def read_electrode_column_descriptions(json_path: Path) -> dict[str, Any]:
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    wanted = ("x", "y", "z", "AnatomicalLocation")
    return {key: payload.get(key) for key in wanted}


def audit(dataset_root: Path) -> dict[str, Any]:
    dataset_root = dataset_root.resolve()
    files: list[dict[str, Any]] = []
    for subject in sorted(DEV_SUBJECTS):
        subject_root = dataset_root / subject
        if not subject_root.is_dir():
            raise FileNotFoundError(f"Required development folder is missing: {subject_root}")
        for tsv in sorted(subject_root.rglob("*_electrodes.tsv")):
            if "ieeg" not in tsv.parts:
                continue
            json_path = tsv.with_suffix(".json")
            if not json_path.is_file():
                raise FileNotFoundError(f"Electrode column-description JSON missing: {json_path}")
            header = tsv.open("r", encoding="utf-8").readline().rstrip("\r\n").split("\t")
            files.append(
                {
                    "subject": subject,
                    "electrodes_tsv": str(tsv.relative_to(dataset_root)),
                    "has_space_entity": "_space-" in tsv.name,
                    "header": header,
                    "coordsystem_sidecars_in_inheritance_chain": sidecars_in_bids_inheritance_chain(
                        tsv, dataset_root
                    ),
                    "column_descriptions": read_electrode_column_descriptions(json_path),
                }
            )

    sidecar_paths = sorted(
        str(path.relative_to(dataset_root))
        for subject in sorted(DEV_SUBJECTS)
        for path in (dataset_root / subject).rglob("*_coordsystem.json")
    )
    counts_by_subject = {
        subject: sum(record["subject"] == subject for record in files)
        for subject in sorted(DEV_SUBJECTS)
    }
    unique_descriptions = {
        key: sorted(
            {
                json.dumps(record["column_descriptions"].get(key), sort_keys=True)
                for record in files
            }
        )
        for key in ("x", "y", "z", "AnatomicalLocation")
    }
    return {
        "audit_type": "metadata_only_coordinate_provenance",
        "development_subjects_only": sorted(DEV_SUBJECTS),
        "events_or_signal_files_read": False,
        "confirmation_participants_read": False,
        "electrode_tsv_count": len(files),
        "electrode_tsv_count_by_subject": counts_by_subject,
        "space_entity_count": sum(item["has_space_entity"] for item in files),
        "coordsystem_sidecar_count_under_development_subjects": len(sidecar_paths),
        "coordsystem_sidecar_paths_under_development_subjects": sidecar_paths,
        "files_with_no_inherited_coordsystem_sidecar": [
            item["electrodes_tsv"]
            for item in files
            if not item["coordsystem_sidecars_in_inheritance_chain"]
        ],
        "unique_electrode_json_column_descriptions": unique_descriptions,
        "files": files,
        "interpretation": (
            "The dataset's electrode-column JSON can describe x/y/z as MNI coordinates and name an anatomical-labeling atlas, "
            "but without an inherited coordsystem sidecar or space entity it does not identify the exact MNI template, "
            "coordinate convention, units, or transform needed to independently reproduce contact-to-atlas assignment."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=Path("data/track_b/on004752_v1.0.0"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.dataset_root)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
