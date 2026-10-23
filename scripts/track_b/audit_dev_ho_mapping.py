"""Metadata-only feasibility audit of development iEEG contacts against HO atlas.

Reads only electrodes.tsv for sub-01 through sub-03. It never opens events,
signals, or any data from confirmation participants. Coordinates are reported
as generic MNI by the release, so all atlas assignments are explicitly
provisional pending identification of the exact MNI template/normalization.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from importlib.metadata import version
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import nibabel as nib
import numpy as np
from nilearn.datasets import fetch_atlas_harvard_oxford


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def lookup(atlas, xyz: np.ndarray) -> tuple[str | None, int | None]:
    image = atlas.maps
    voxel = np.rint(nib.affines.apply_affine(np.linalg.inv(image.affine), xyz)).astype(int)
    if np.any(voxel < 0) or np.any(voxel >= np.asarray(image.shape[:3])):
        return None, None
    label_id = int(np.asarray(image.dataobj)[tuple(voxel)])
    lut = atlas.lut
    row = lut.loc[lut["index"] == label_id]
    if row.empty or label_id == 0:
        return None, label_id
    return str(row.iloc[0]["name"]), label_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data/track_b/on004752_v1.0.0"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data_root = args.data_root.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)

    atlases = {
        "cortical": fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm"),
        "subcortical": fetch_atlas_harvard_oxford("sub-maxprob-thr25-2mm"),
    }
    atlas_hashes = {}
    for key, atlas in atlases.items():
        atlas_digest = hashlib.sha256()
        atlas_digest.update(np.ascontiguousarray(atlas.maps.dataobj).tobytes())
        atlas_digest.update(np.ascontiguousarray(atlas.maps.affine).tobytes())
        atlas_hashes[key] = atlas_digest.hexdigest()

    contacts = []
    subjects = [f"sub-{i:02d}" for i in range(1, 4)]
    coord_sidecars = []
    for subject in subjects:
        for table in sorted((data_root / subject).glob("ses-*/ieeg/*_electrodes.tsv")):
            coord_sidecars.extend(table.parent.glob("*_coordsystem.json"))
            with table.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f, delimiter="\t"):
                    xyz = np.array([float(row[k]) if row.get(k, "n/a") not in ("", "n/a", "NaN") else np.nan
                                    for k in ("x", "y", "z")], dtype=float)
                    labels = {}
                    for atlas_kind, atlas in atlases.items():
                        labels[atlas_kind] = lookup(atlas, xyz)[0] if np.isfinite(xyz).all() else None
                    cortical = labels["cortical"]
                    subcortical = labels["subcortical"]
                    deep_gray = {
                        "Left Thalamus", "Left Caudate", "Left Putamen", "Left Pallidum",
                        "Brain-Stem", "Left Hippocampus", "Left Amygdala", "Left Accumbens",
                        "Right Thalamus", "Right Caudate", "Right Putamen", "Right Pallidum",
                        "Right Hippocampus", "Right Amygdala", "Right Accumbens",
                    }
                    if cortical and subcortical in deep_gray:
                        assigned = None
                        status = "cortical_deepgray_overlap"
                    elif cortical:
                        assigned = f"cortical:{cortical}"
                        status = "provisional_single_atlas_label"
                    elif subcortical in deep_gray:
                        assigned = f"subcortical:{subcortical}"
                        status = "provisional_single_atlas_label"
                    else:
                        assigned = None
                        status = "white_matter_ventricle_or_outside_atlas"
                    contacts.append({
                        "subject": subject,
                        "session": table.parent.parent.name,
                        "electrode": row.get("name"),
                        "x_mni_mm": xyz[0] if np.isfinite(xyz).all() else None,
                        "y_mni_mm": xyz[1] if np.isfinite(xyz).all() else None,
                        "z_mni_mm": xyz[2] if np.isfinite(xyz).all() else None,
                        "brainnetome_label": row.get("AnatomicalLocation"),
                        "ho_cortical_label": labels["cortical"],
                        "ho_subcortical_label": labels["subcortical"],
                        "provisional_ho_label": assigned,
                        "mapping_status": status,
                        "source_table": table.relative_to(data_root).as_posix(),
                        "source_table_sha256": sha256(table),
                    })

    by_subject = {}
    labels_by_subject: dict[str, set[str]] = defaultdict(set)
    counts_by_subject: dict[str, Counter] = defaultdict(Counter)
    for contact in contacts:
        subject = contact["subject"]
        counts_by_subject[subject][contact["mapping_status"]] += 1
        if contact["provisional_ho_label"]:
            labels_by_subject[subject].add(contact["provisional_ho_label"])
    for subject in subjects:
        by_subject[subject] = {
            "contact_count": sum(counts_by_subject[subject].values()),
            "status_counts": dict(sorted(counts_by_subject[subject].items())),
            "provisionally_mapped_contact_count": sum(
                c["subject"] == subject and c["provisional_ho_label"] is not None for c in contacts
            ),
            "provisional_label_count": len(labels_by_subject[subject]),
            "provisional_labels": sorted(labels_by_subject[subject]),
        }
    shared_labels = sorted(set.intersection(*(labels_by_subject[s] for s in subjects))) if subjects else []

    csv_path = out / "contact_mapping.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(contacts[0]) if contacts else [])
        writer.writeheader()
        writer.writerows(contacts)
    report = {
        "audit_type": "development-only metadata feasibility; no neural signal or event data loaded",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_release": "NEMAR on004752 v1.0.0",
        "participants_inspected": subjects,
        "participants_not_inspected": [f"sub-{i:02d}" for i in range(4, 16)],
        "input_files": "Only *_electrodes.tsv for sub-01 through sub-03",
        "source_table_count": len({c["source_table"] for c in contacts}),
        "script_sha256": sha256(Path(__file__).resolve()),
        "software": {
            "python": platform.python_version(),
            "nilearn": version("nilearn"),
            "nibabel": version("nibabel"),
            "numpy": version("numpy"),
        },
        "coordsystem_sidecars_found": [p.relative_to(data_root).as_posix() for p in coord_sidecars],
        "coordinate_system_caveat": "Dataset sidecar describes x/y/z as MNI coordinates but provides no coordsystem.json naming the exact MNI template/normalization. Lookup in MNI152NLin6Asym Harvard-Oxford atlas is provisional and is not a validated contact-to-region crosswalk.",
        "atlas": {
            "source": "Nilearn Harvard-Oxford maximum-probability atlases, 2 mm, threshold 25",
            "template": str(atlases["cortical"].template).strip(),
            "method": "Round MNI millimeter coordinates to nearest voxel in each atlas affine. Use a non-background cortical label when present; otherwise accept only named deep-gray/brainstem subcortical labels. Exclude white matter, ventricles, and unmatched coordinates. No neighborhood smoothing or manual reassignment.",
            "sha256_nifti": atlas_hashes,
            "labels_including_background": {key: int(len(atlas.labels)) for key, atlas in atlases.items()},
        },
        "subject_summary": by_subject,
        "labels_shared_by_all_development_participants": shared_labels,
        "total_contacts": len(contacts),
        "provisionally_mapped_contacts": sum(c["provisional_ho_label"] is not None for c in contacts),
        "limitations": [
            "The generic MNI coordinate declaration does not verify compatibility with MNI152NLin6Asym.",
            "A point lookup in a 2 mm population atlas does not account for contact size, registration error, tissue class, or postoperative brain shift.",
            "This is a target-feasibility audit only; it does not validate WBEN's C matrix or any model prediction.",
            "Labels are not used to select or tune a model in this audit.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out / "SESSION.md").write_text(
        "# Development-only Harvard–Oxford contact-mapping audit\n\n"
        "This metadata-only audit reads electrode coordinates for sub-01 through sub-03 and maps each point to the nearest voxel in the official Nilearn Harvard–Oxford 2 mm maximum-probability cortical and subcortical atlases (25% threshold). It does not load event or neural signal files and does not inspect sub-04 through sub-15.\n\n"
        "The dataset calls coordinates MNI but has no `coordsystem.json` identifying the exact template. Therefore every atlas label is provisional and cannot yet be treated as a valid WBEN contact-to-region mapping. See `audit.json` for counts, hashes, and limits, and `contact_mapping.csv` for the row-level audit.\n",
        encoding="utf-8",
    )
    print(json.dumps({k: report[k] for k in ("total_contacts", "provisionally_mapped_contacts", "labels_shared_by_all_development_participants", "subject_summary", "coordsystem_sidecars_found")}, indent=2))


if __name__ == "__main__":
    main()
