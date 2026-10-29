"""Render metadata-only WSGZP MRI/electrode overlays for coordinate QC.

The script displays the released T1w MRI max-intensity projections with the
released scalp electrodes and fiducials mapped through the NIfTI affine. It
does not fit or alter coordinates and never opens EEG/iEEG sample arrays.
The sidecar's T1w-mm coordinates are explicitly treated as scanner-RAS mm;
this visualization can reveal gross inconsistencies but cannot independently
prove that the declared transform is correct.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv_xyz(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    names = [r["name"] for r in rows]
    xyz = np.asarray([[float(r[k]) for k in ("x", "y", "z")] for r in rows], dtype=np.float64)
    if not names or not np.isfinite(xyz).all():
        raise ValueError(f"Invalid electrode table: {path}")
    return names, xyz


def voxel_points(world_xyz_mm: np.ndarray, affine: np.ndarray) -> np.ndarray:
    return nib.affines.apply_affine(np.linalg.inv(affine), world_xyz_mm)


def render_subject(root: Path, subject: str, output: Path) -> dict:
    prefix = f"{subject}_task-ccepcoreg"
    mri = root / subject / "anat" / f"{subject}_T1w.nii"
    eeg = root / "derivatives" / "epochs" / subject / "eeg"
    electrodes = eeg / f"{prefix}_electrodes.tsv"
    coordsystem = eeg / f"{prefix}_coordsystem.json"
    ieeg = root / "derivatives" / "epochs" / subject / "ieeg"
    ieeg_electrodes = ieeg / f"{prefix}_space-T1w_electrodes.tsv"
    ieeg_coordsystem = ieeg / f"{prefix}_space-T1w_coordsystem.json"
    for p in (mri, electrodes, coordsystem, ieeg_electrodes, ieeg_coordsystem):
        if not p.is_file():
            raise FileNotFoundError(p)

    cs = json.loads(coordsystem.read_text(encoding="utf-8"))
    if cs.get("EEGCoordinateSystem") != "T1w" or cs.get("EEGCoordinateUnits") != "mm":
        raise ValueError(f"Unexpected coordinate contract for {subject}")
    names, xyz = read_tsv_xyz(electrodes)
    landmarks = cs.get("AnatomicalLandmarkCoordinates", {})
    landmark_names = [n for n in ("NAS", "LPA", "RPA") if n in landmarks]
    landmark_xyz = np.asarray([landmarks[n] for n in landmark_names], dtype=np.float64)
    if landmark_xyz.shape != (len(landmark_names), 3) or not np.isfinite(landmark_xyz).all():
        raise ValueError(f"Invalid anatomical landmark table for {subject}")

    image = nib.as_closest_canonical(nib.load(str(mri)))
    data = np.asarray(image.dataobj, dtype=np.float32)
    if data.ndim != 3 or not np.isfinite(image.affine).all():
        raise ValueError(f"Expected a finite 3-D MRI and affine for {subject}")
    affine = np.asarray(image.affine, dtype=np.float64)
    sizes = np.asarray(image.header.get_zooms()[:3], dtype=np.float64)
    if np.any(sizes <= 0):
        raise ValueError(f"Invalid voxel sizes for {subject}")
    direction = affine[:3, :3] / sizes[np.newaxis, :]
    axis_alignment_error = float(np.max(np.abs(direction - np.eye(3))))
    if axis_alignment_error > 1e-4:
        raise ValueError(
            f"{subject} MRI is oblique/sheared relative to canonical RAS axes "
            f"(max direction-cosine error {axis_alignment_error:.3g}); resample explicitly before rendering"
        )
    eijk = voxel_points(xyz, affine)
    lijk = voxel_points(landmark_xyz, affine)
    ieeg_cs = json.loads(ieeg_coordsystem.read_text(encoding="utf-8"))
    if (ieeg_cs.get("iEEGCoordinateSystem") != "Other"
            or ieeg_cs.get("iEEGCoordinateUnits") != "m"
            or "Native MRI" not in ieeg_cs.get("iEEGCoordinateSystemDescription", "")):
        raise ValueError(f"Unexpected native-MRI SEEG coordinate contract for {subject}")
    ieeg_names, ieeg_xyz_m = read_tsv_xyz(ieeg_electrodes)
    ieeg_xyz_mm = ieeg_xyz_m * 1000.0
    ieegijk = voxel_points(ieeg_xyz_mm, affine)
    dims = np.asarray(data.shape, dtype=np.float64)
    e_inside = np.all((eijk >= -0.5) & (eijk <= dims - 0.5), axis=1)
    l_inside = np.all((lijk >= -0.5) & (lijk <= dims - 0.5), axis=1)
    ieeg_inside = np.all((ieegijk >= -0.5) & (ieegijk <= dims - 0.5), axis=1)
    positive_superior_planes = np.flatnonzero(np.any(data > 0, axis=(0, 1)))
    if not len(positive_superior_planes):
        raise ValueError(f"MRI has no positive-valued voxels for {subject}")
    last_positive_superior_plane = int(positive_superior_planes[-1])
    eeg_above_last_positive_plane = eijk[:, 2] > last_positive_superior_plane

    # Top row: actual orthogonal MRI slices through median scalp-sensor
    # coordinates; only points within +/-2.5 mm of the slice are drawn.
    # Bottom row: whole-volume MIPs show the full spatial cloud but collapse
    # depth, so they are explicitly labelled as projections.
    view_specs = [
        ("Axial", 2, np.median(eijk[:, 2]), (0, 1), ("R", "A"), lambda q: data[:, :, q].T,
         np.max(data, axis=2).T),
        ("Coronal", 1, np.median(eijk[:, 1]), (0, 2), ("R", "S"), lambda q: data[:, q, :].T,
         np.max(data, axis=1).T),
        ("Sagittal", 0, np.median(eijk[:, 0]), (1, 2), ("A", "S"), lambda q: data[q, :, :].T,
         np.max(data, axis=0).T),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    slice_metadata = []
    for col, (title, fixed, center, (h, v), labels, slicer, mip) in enumerate(view_specs):
        idx = int(np.clip(np.rint(center), 0, dims[fixed] - 1))
        extent = (-0.5 * sizes[h], (dims[h] - 0.5) * sizes[h],
                  -0.5 * sizes[v], (dims[v] - 0.5) * sizes[v])
        ax = axes[0, col]
        ax.imshow(slicer(idx), cmap="gray", origin="lower", extent=extent, aspect="equal")
        ax.plot([extent[0], extent[1], extent[1], extent[0], extent[0]],
                [extent[2], extent[2], extent[3], extent[3], extent[2]],
                color="cyan", linewidth=0.8, linestyle="--", label="MRI FOV")
        eeg_slab = np.abs(eijk[:, fixed] - idx) * sizes[fixed] <= 2.5
        eeg_plane_fov = ((eijk[:, h] >= -0.5) & (eijk[:, h] <= dims[h] - 0.5)
                         & (eijk[:, v] >= -0.5) & (eijk[:, v] <= dims[v] - 0.5))
        e_keep = eeg_slab & eeg_plane_fov
        eh, ev = eijk[:, h] * sizes[h], eijk[:, v] * sizes[v]
        ax.scatter(eh[e_keep], ev[e_keep], s=24, c="#ff4d4d", edgecolors="white",
                   linewidths=0.45, label="Scalp sensors within +/-2.5 mm slab", zorder=3)
        e_out = eeg_slab & ~eeg_plane_fov
        if np.any(e_out):
            ax.scatter(eh[e_out], ev[e_out], s=28, marker="x", c="#ffb000",
                       linewidths=1.2, label="Slab sensors outside MRI FOV", zorder=4)
        seeg_slab = np.abs(ieegijk[:, fixed] - idx) * sizes[fixed] <= 2.5
        seeg_plane_fov = ((ieegijk[:, h] >= -0.5) & (ieegijk[:, h] <= dims[h] - 0.5)
                          & (ieegijk[:, v] >= -0.5) & (ieegijk[:, v] <= dims[v] - 0.5))
        s_keep = seeg_slab & seeg_plane_fov
        sh, sv = ieegijk[:, h] * sizes[h], ieegijk[:, v] * sizes[v]
        ax.scatter(sh[s_keep], sv[s_keep], s=12, c="#6dc7ff", alpha=0.8,
                   linewidths=0, label="SEEG contacts within slab", zorder=2)
        l_keep = np.abs(lijk[:, fixed] - idx) * sizes[fixed] <= 2.5
        if np.any(l_keep):
            lh, lv = lijk[:, h] * sizes[h], lijk[:, v] * sizes[v]
            ax.scatter(lh[l_keep], lv[l_keep], s=58, marker="+", c="#44ddff",
                       linewidths=1.5, label="Fiducials within slab", zorder=5)
            for name, x, y, keep in zip(landmark_names, lh, lv, l_keep):
                if keep:
                    ax.annotate(name, (x, y), xytext=(3, 3), textcoords="offset points",
                                fontsize=7, color="#44ddff")
        ax.set_title(f"{title} slice at voxel {idx}; EEG in slab={int(eeg_slab.sum())}")
        ax.set_xlabel(f"{labels[0]} axis (mm; canonical voxel coordinates)")
        ax.set_ylabel(f"{labels[1]} axis (mm; canonical voxel coordinates)")
        slice_voxel = (dims - 1) / 2.0
        slice_voxel[fixed] = idx
        slice_center_world_mm = nib.affines.apply_affine(affine, slice_voxel)
        slice_metadata.append({
            "view": title,
            "through_plane_axis_index": int(fixed),
            "through_plane_axis_code": list(nib.aff2axcodes(affine))[fixed],
            "slice_index_zero_based": idx,
            "slice_voxel_center_world_xyz_mm": slice_center_world_mm.tolist(),
            "slab_half_width_mm": 2.5,
            "scalp_sensor_count_in_slab": int(eeg_slab.sum()),
            "seeg_contact_count_in_slab": int(seeg_slab.sum()),
            "fiducial_count_in_slab": int(l_keep.sum()),
        })

        ax = axes[1, col]
        ax.imshow(mip, cmap="gray", origin="lower", extent=extent, aspect="equal")
        ax.plot([extent[0], extent[1], extent[1], extent[0], extent[0]],
                [extent[2], extent[2], extent[3], extent[3], extent[2]],
                color="cyan", linewidth=0.8, linestyle="--", label="MRI FOV")
        projected_inside = eeg_plane_fov
        collapsed_only_out = projected_inside & ~e_inside
        e_full_fov = e_inside
        ax.scatter(eh[e_full_fov], ev[e_full_fov], s=14, c="#ff4d4d", edgecolors="white",
                   linewidths=0.3, label="Scalp sensors within 3-D MRI FOV", zorder=3)
        if np.any(collapsed_only_out):
            ax.scatter(eh[collapsed_only_out], ev[collapsed_only_out], s=30,
                       facecolors="none", edgecolors="#ffb000", linewidths=1.2,
                       label="Outside FOV on collapsed axis", zorder=4)
        if np.any(~projected_inside):
            ax.scatter(eh[~projected_inside], ev[~projected_inside], s=26, marker="x",
                       c="#ffb000", linewidths=1.2, label="Outside projected MRI bounds", zorder=4)
        ieeg_projected_inside = ((ieegijk[:, h] >= -0.5) & (ieegijk[:, h] <= dims[h] - 0.5)
                                 & (ieegijk[:, v] >= -0.5) & (ieegijk[:, v] <= dims[v] - 0.5))
        ax.scatter(sh[ieeg_inside], sv[ieeg_inside], s=6, c="#6dc7ff", alpha=0.6,
                   linewidths=0, label="SEEG contacts within 3-D MRI FOV", zorder=2)
        if np.any(~ieeg_inside & ieeg_projected_inside):
            ax.scatter(sh[~ieeg_inside & ieeg_projected_inside], sv[~ieeg_inside & ieeg_projected_inside],
                       s=16, marker="^", facecolors="none", edgecolors="#6dc7ff", linewidths=0.8,
                       label="SEEG outside FOV on collapsed axis", zorder=2)
        lh, lv = lijk[:, h] * sizes[h], lijk[:, v] * sizes[v]
        ax.scatter(lh, lv, s=48, marker="+", c="#44ddff", linewidths=1.5,
                   label="NAS/LPA/RPA", zorder=5)
        for name, x, y in zip(landmark_names, lh, lv):
            ax.annotate(name, (x, y), xytext=(3, 3), textcoords="offset points",
                        fontsize=7, color="#44ddff")
        ax.set_title(f"{title} MIP (all coordinates projected)")
        ax.set_xlabel(f"{labels[0]} axis (mm; canonical voxel coordinates)")
        ax.set_ylabel(f"{labels[1]} axis (mm; canonical voxel coordinates)")
        xall = np.r_[extent[:2], eh, sh, lh]
        yall = np.r_[extent[2:], ev, sv, lv]
        dx, dy = max(float(np.ptp(xall)), 1.0) * 0.04, max(float(np.ptp(yall)), 1.0) * 0.04
        ax.set_xlim(float(np.min(xall) - dx), float(np.max(xall) + dx))
        ax.set_ylim(float(np.min(yall) - dy), float(np.max(yall) + dy))
    handles, labels_legend = [], []
    for ax in axes.flat:
        for handle, label in zip(*ax.get_legend_handles_labels()):
            if label not in labels_legend:
                handles.append(handle)
                labels_legend.append(label)
    fig.subplots_adjust(bottom=0.15, top=0.88, wspace=0.32, hspace=0.32)
    fig.legend(handles, labels_legend, loc="lower center", bbox_to_anchor=(0.5, 0.02),
               ncol=3, frameon=False, fontsize=8)
    fig.suptitle(
        f"{subject}: released T1w MRI and scalp geometry\n"
        "Metadata-only diagnostic; T1w coordinates interpreted as scanner-RAS mm; no refit",
        fontsize=11,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return {
        "subject": subject,
        "status": "VISUAL_DIAGNOSTIC_ONLY_REVIEW_REQUIRED",
        "signal_samples_read": False,
        "coordinate_interpretation": "sidecar T1w mm treated as NIfTI scanner-RAS world mm; unverified assumption",
        "n_scalp_electrodes": len(names),
        "scalp_electrodes_inside_nifti_fov": int(e_inside.sum()),
        "scalp_electrodes_outside_nifti_fov": int((~e_inside).sum()),
        "last_superior_voxel_plane_with_any_positive_mri_intensity": last_positive_superior_plane,
        "number_of_completely_blank_superior_planes_to_nifti_edge": int(dims[2] - 1 - last_positive_superior_plane),
        "scalp_electrodes_superior_to_last_positive_mri_plane": int(eeg_above_last_positive_plane.sum()),
        "n_seeg_contacts": len(ieeg_names),
        "seeg_contacts_inside_nifti_fov": int(ieeg_inside.sum()),
        "seeg_contacts_outside_nifti_fov": int((~ieeg_inside).sum()),
        "n_landmarks": len(landmark_names),
        "landmarks_inside_nifti_fov": int(l_inside.sum()),
        "canonical_axis_codes": list(nib.aff2axcodes(affine)),
        "mri_voxel_sizes_mm": sizes.tolist(),
        "max_canonical_axis_alignment_error": axis_alignment_error,
        "slice_specs": slice_metadata,
        "input_sha256": {"mri": sha256(mri), "eeg_electrodes_tsv": sha256(electrodes),
                         "eeg_coordsystem_json": sha256(coordsystem),
                         "ieeg_electrodes_tsv": sha256(ieeg_electrodes),
                         "ieeg_coordsystem_json": sha256(ieeg_coordsystem)},
        "overlay_png": str(output),
        "overlay_png_sha256": sha256(output),
        "limitations": [
            "Top-row slices show only contacts within a +/-2.5-mm physical slab; absence from a slice is not an exclusion.",
            "Bottom-row maximum-intensity projections collapse one spatial axis; projected points can overlap MRI tissue even when physically outside it.",
            "A maximum-intensity projection is for gross visual QC, not a scalp/skull segmentation.",
            "The last positive MRI voxel plane is an image-content boundary, not an anatomical scalp segmentation.",
            "A plausible overlay cannot independently recover or validate the absent digitizer-to-MRI transform.",
            "Coordinates are not moved, refitted, clipped or corrected.",
            "This is not a forward model and does not authorize source fitting.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--subjects", nargs="+", required=True)
    args = parser.parse_args()
    root = args.dataset_root.resolve()
    output_dir = args.output_dir.resolve()
    records = []
    for subject in args.subjects:
        records.append(render_subject(root, subject, output_dir / f"{subject}_geometry_overlay.png"))
    report = {
        "audit_id": "WSGZP-MRI-ELECTRODE-OVERLAY-2026-10-28-v1",
        "status": "VISUAL_DIAGNOSTIC_ONLY_REVIEW_REQUIRED",
        "signal_samples_read": False,
        "subject_count": len(records),
        "renderer_script": str(Path(__file__).resolve()),
        "renderer_script_sha256": sha256(Path(__file__).resolve()),
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "nibabel": nib.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "slab_half_width_mm": 2.5,
        "subjects": records,
    }
    manifest = output_dir / "overlay_manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "subjects": records}, indent=2))


if __name__ == "__main__":
    main()
