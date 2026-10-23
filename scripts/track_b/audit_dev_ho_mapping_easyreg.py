"""Metadata-only EasyReg point-transform audit for development contacts.

Reads only *_electrodes.tsv files for sub-01 through sub-03, the pinned
MNI152Lin -> MNI152NLin6Asym EasyReg coordinate fields, and Harvard-Oxford
atlas images. It does not read events, neural signals, or reserved subjects.

The transform is a candidate standard-template crosswalk, not subject-specific
electrode registration and not the unreported WBEN contact-assignment rule.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import nibabel as nib
import numpy as np
from nilearn.datasets import fetch_atlas_harvard_oxford
from scipy.ndimage import map_coordinates


SOURCE_COMMIT = "8b3bb0e8ba47a8a2b7c42b801e23b6b7cecf5c26"
SOURCE_URL = (
    "https://github.com/LeonDLotter/NiSpace-data/tree/"
    f"{SOURCE_COMMIT}/transform/MNI152NLin6Asym"
)
BACKWARD_SHA256 = "5a27b143ed3b3013a0dad948d8f1c11e4c4407c42791f77dcff3580db6fea0d1"
FORWARD_SHA256 = "104ed155844b10dda01a659aa1cb1cbd6ce09cdf73032d90d899f6b2e8607c8c"
DEEP_GRAY = {
    "Left Thalamus", "Left Caudate", "Left Putamen", "Left Pallidum",
    "Brain-Stem", "Left Hippocampus", "Left Amygdala", "Left Accumbens",
    "Right Thalamus", "Right Caudate", "Right Putamen", "Right Pallidum",
    "Right Hippocampus", "Right Amygdala", "Right Accumbens",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sample_ras(field: np.ndarray, affine: np.ndarray, xyz: np.ndarray) -> np.ndarray:
    """Linearly sample an absolute-RAS coordinate field at RAS mm points."""
    vox = nib.affines.apply_affine(np.linalg.inv(affine), xyz)
    return np.stack(
        [
            map_coordinates(
                field[..., axis], vox.T, order=1, mode="constant", cval=np.nan,
                prefilter=False,
            )
            for axis in range(3)
        ],
        axis=1,
    )


def atlas_label(atlas, xyz: np.ndarray) -> str | None:
    image = atlas.maps
    voxel = np.rint(
        nib.affines.apply_affine(np.linalg.inv(image.affine), xyz)
    ).astype(int)
    if np.any(voxel < 0) or np.any(voxel >= np.asarray(image.shape[:3])):
        return None
    label_id = int(np.asarray(image.dataobj)[tuple(voxel)])
    row = atlas.lut.loc[atlas.lut["index"] == label_id]
    if label_id == 0 or row.empty:
        return None
    return str(row.iloc[0]["name"])


def combined_label(cortical: str | None, subcortical: str | None) -> str | None:
    if cortical and subcortical in DEEP_GRAY:
        return None
    if cortical:
        return f"cortical:{cortical}"
    if subcortical in DEEP_GRAY:
        return f"subcortical:{subcortical}"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data/track_b/on004752_v1.0.0"))
    parser.add_argument("--transform-dir", type=Path, required=True)
    parser.add_argument("--old-map", type=Path, default=Path(
        "outputs/track_b/20261022T190700Z_b2_ho_mapping_audit_v3/contact_mapping.csv"
    ))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    data_root = args.data_root.resolve()
    transform_dir = args.transform_dir.resolve()
    backward_path = transform_dir / "from-MNI152Lin_to-MNI152NLin6Asym_dir-backward_field.nii.gz"
    forward_path = transform_dir / "from-MNI152Lin_to-MNI152NLin6Asym_dir-forward_field.nii.gz"
    for path, expected in ((backward_path, BACKWARD_SHA256), (forward_path, FORWARD_SHA256)):
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"Transform checksum mismatch for {path.name}: {actual}")

    # NiSpace-data calls the backward field the source->target point map; the
    # paired forward field maps target points back to source for round-trip QC.
    backward_img = nib.load(str(backward_path))
    forward_img = nib.load(str(forward_path))
    backward = np.asarray(backward_img.dataobj, dtype=np.float32)
    forward = np.asarray(forward_img.dataobj, dtype=np.float32)
    atlases = {
        "cortical": fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm"),
        "subcortical": fetch_atlas_harvard_oxford("sub-maxprob-thr25-2mm"),
    }
    atlas_hashes = {}
    for key, atlas in atlases.items():
        h = hashlib.sha256()
        h.update(np.ascontiguousarray(atlas.maps.dataobj).tobytes())
        h.update(np.ascontiguousarray(atlas.maps.affine).tobytes())
        atlas_hashes[key] = h.hexdigest()

    old_map: dict[tuple[str, str, str], str | None] = {}
    with args.old_map.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            old_map[(row["subject"], row["session"], row["electrode"])] = (
                row.get("provisional_ho_label") or None
            )

    rows: list[dict[str, object]] = []
    roundtrip_errors: list[float] = []
    transform_outside = 0
    subjects = [f"sub-{i:02d}" for i in range(1, 4)]
    coord_sidecars: list[str] = []
    for subject in subjects:
        for table in sorted((data_root / subject).glob("ses-*/ieeg/*_electrodes.tsv")):
            coord_sidecars.extend(
                p.relative_to(data_root).as_posix()
                for p in table.parent.glob("*_coordsystem.json")
            )
            with table.open("r", encoding="utf-8-sig", newline="") as stream:
                for contact in csv.DictReader(stream, delimiter="\t"):
                    try:
                        source_xyz = np.asarray(
                            [[float(contact[k]) for k in ("x", "y", "z")]],
                            dtype=float,
                        )
                    except (TypeError, ValueError):
                        continue
                    target_xyz = sample_ras(backward, backward_img.affine, source_xyz)[0]
                    if not np.isfinite(target_xyz).all():
                        transform_outside += 1
                        continue
                    recovered_source = sample_ras(
                        forward, forward_img.affine, target_xyz[None, :]
                    )[0]
                    roundtrip_error = None
                    if np.isfinite(recovered_source).all():
                        roundtrip_error = float(np.linalg.norm(recovered_source - source_xyz[0]))
                        roundtrip_errors.append(roundtrip_error)
                    cortical = atlas_label(atlases["cortical"], target_xyz)
                    subcortical = atlas_label(atlases["subcortical"], target_xyz)
                    mapped = combined_label(cortical, subcortical)
                    key = (subject, table.parent.parent.name, contact["name"])
                    previous = old_map.get(key)
                    rows.append({
                        "subject": subject,
                        "session": table.parent.parent.name,
                        "electrode": contact["name"],
                        "source_x_mni152lin_mm": source_xyz[0, 0],
                        "source_y_mni152lin_mm": source_xyz[0, 1],
                        "source_z_mni152lin_mm": source_xyz[0, 2],
                        "target_x_mni152nlin6asym_mm": target_xyz[0],
                        "target_y_mni152nlin6asym_mm": target_xyz[1],
                        "target_z_mni152nlin6asym_mm": target_xyz[2],
                        "roundtrip_error_mm": roundtrip_error,
                        "brainnetome_label_from_release": contact.get("AnatomicalLocation", ""),
                        "ho_cortical_label": cortical,
                        "ho_subcortical_label": subcortical,
                        "easyreg_mapped_label": mapped,
                        "identity_lookup_label_withdrawn": previous,
                        "label_changed_vs_identity_lookup": previous != mapped,
                        "source_table": table.relative_to(data_root).as_posix(),
                        "source_table_sha256": sha256(table),
                    })

    labels_by_subject: dict[str, set[str]] = defaultdict(set)
    summary_by_subject: dict[str, Counter] = defaultdict(Counter)
    jointly_assigned = 0
    same_label_if_both_assigned = 0
    changed_labels: Counter = Counter()
    for row in rows:
        subject = str(row["subject"])
        label = row["easyreg_mapped_label"]
        old = row["identity_lookup_label_withdrawn"]
        if label:
            labels_by_subject[subject].add(str(label))
            summary_by_subject[subject]["assigned"] += 1
        else:
            summary_by_subject[subject]["not_assigned"] += 1
        if old and label:
            jointly_assigned += 1
            if old == label:
                same_label_if_both_assigned += 1
            else:
                changed_labels[f"{old} -> {label}"] += 1
        elif old and not label:
            changed_labels[f"{old} -> UNASSIGNED"] += 1
        elif label and not old:
            changed_labels[f"UNASSIGNED -> {label}"] += 1

    csv_path = out / "contact_mapping_easyreg.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    shared = sorted(set.intersection(*(labels_by_subject[s] for s in subjects)))
    errs = np.asarray(roundtrip_errors, dtype=float)
    report = {
        "audit_type": "development-only metadata transform and atlas lookup; no neural signals or events loaded",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "NEMAR on004752 v1.0.0",
        "participants_inspected": subjects,
        "participants_not_inspected": [f"sub-{i:02d}" for i in range(4, 16)],
        "input_files": "Only *_electrodes.tsv for sub-01 through sub-03, pinned transform fields, and atlas files",
        "source_coordinate_space": "MNI152Lin inferred from the pinned dataset localization script's SPM12 OldNorm default; BIDS sidecar absent and row-level provenance unproven",
        "target_coordinate_space": "MNI152NLin6Asym",
        "transform": {
            "method": "Published EasyReg/SynthSeg template-to-template fields from NiSpace-data; linear interpolation of absolute RAS-mm coordinates",
            "source_commit": SOURCE_COMMIT,
            "source_url": SOURCE_URL,
            "license": "NiSpace-data repository declares CC BY-NC-SA 4.0; do not redistribute transform files or derived mapping artifacts without checking license obligations",
            "backward_field_sha256": sha256(backward_path),
            "forward_field_sha256": sha256(forward_path),
            "source_to_target_field": "dir-backward_field, defined on source grid; matches NiSpace-data docs for point-forward source-to-target mapping",
            "target_to_source_field": "dir-forward_field, used only for round-trip consistency check",
            "finite_source_points": len(rows),
            "outside_source_field": transform_outside,
            "roundtrip_count": int(errs.size),
            "roundtrip_error_mm": {
                "median": float(np.median(errs)) if errs.size else None,
                "p95": float(np.quantile(errs, .95)) if errs.size else None,
                "maximum": float(np.max(errs)) if errs.size else None,
            },
        },
        "atlas": {
            "source": "Nilearn Harvard-Oxford max-probability atlases, 2 mm, threshold 25",
            "template": "MNI152NLin6Asym",
            "assignment": "Nearest voxel in transformed coordinate; use cortical label, else named deep-gray/brainstem subcortical label; cortical/subcortical overlap is unassigned",
            "sha256_image_and_affine": atlas_hashes,
        },
        "contact_count": len(rows),
        "outside_transform_field": transform_outside,
        "assigned_count": sum(bool(r["easyreg_mapped_label"]) for r in rows),
        "assigned_fraction": sum(bool(r["easyreg_mapped_label"]) for r in rows) / len(rows) if rows else None,
        "shared_labels_across_development_participants": shared,
        "per_subject": {s: dict(summary_by_subject[s]) for s in subjects},
        "comparison_with_withdrawn_identity_lookup": {
            "historical_lookup_assigned": sum(bool(r["identity_lookup_label_withdrawn"]) for r in rows),
            "assigned_by_both": jointly_assigned,
            "same_label_when_both_assigned": same_label_if_both_assigned,
            "same_label_fraction_when_both_assigned": same_label_if_both_assigned / jointly_assigned if jointly_assigned else None,
            "transition_counts": dict(changed_labels),
        },
        "coordsystem_sidecars_found": coord_sidecars,
        "limitations": [
            "Round-trip consistency measures paired-field numerical agreement, not anatomical correctness of the template-to-template warp.",
            "MNI152Lin is inferred from source-code provenance; the released BIDS tables omit coordsystem.json and row-level source-output identity is unverified.",
            "A standard-template transform is not individual-anatomy registration and cannot correct postoperative shift or contact localization error.",
            "WBEN's exact Harvard-Oxford contact assignment, tie handling, distance rule, and outside-atlas policy remain unspecified; this is an explicit variant, not a faithful WBEN mapping.",
            "The field data are CC BY-NC-SA 4.0; this local audit does not redistribute them. Check obligations before sharing derived outputs or integrating the transform in a public/commercial product.",
            "No signals, event rows, or confirmation participants were accessed; the label count does not establish prediction or model performance.",
        ],
    }
    (out / "audit_easyreg.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out / "SESSION.md").write_text(
        "# Development-only EasyReg point-transform audit\n\n"
        "This audit applies a pinned MNI152Lin-to-MNI152NLin6Asym EasyReg field to released electrode coordinates for sub-01 through sub-03, then samples Harvard–Oxford labels. It reads no event rows or neural signals and no confirmation participants.\n\n"
        "The result is an explicit, reproducible coordinate-map variant. Paired-field round-trip error checks numerical direction/interpolation consistency but does not establish anatomical accuracy, individual localization, or WBEN fidelity. The BIDS coordinate sidecar is absent, and the WBEN contact-assignment rule remains underspecified. See `audit_easyreg.json` and `contact_mapping_easyreg.csv`.\n",
        encoding="utf-8",
    )
    print(json.dumps({k: report[k] for k in (
        "contact_count", "assigned_count", "assigned_fraction",
        "shared_labels_across_development_participants", "transform",
        "comparison_with_withdrawn_identity_lookup",
    )}, indent=2))


if __name__ == "__main__":
    main()
