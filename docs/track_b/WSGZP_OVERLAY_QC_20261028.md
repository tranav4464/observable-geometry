# WSGZP metadata-only MRI/electrode overlay QC

**Date:** 28 October 2026\
**Status:** diagnostic screen only; no participant cleared for source fitting\
**Signal samples read:** no

## Why this packet exists

The BIDS release declares scalp electrodes in `T1w` millimetres, but its source
digitizer points and digitizer-to-MRI transform are absent. The purpose here
is to make the declared interpretation inspectable against the released MRI,
not to estimate a replacement transform. Coordinates are displayed as
scanner-RAS world millimetres through the NIfTI affine, exactly as assumed in
the coordinate audits. They are never moved, refit, clipped, or corrected.

## Rendered participants

The first row in each image contains actual axial, coronal and sagittal MRI
slices. Each slice is positioned at the median scalp-sensor coordinate along
its through-plane axis; EEG and SEEG points are shown only when within a
2.5-mm slab. The second row contains max-intensity projections with all sensor
coordinates. Projections collapse depth, so a point that appears over MRI
tissue in that row may be in front of or behind the tissue. They are useful for
orientation and gross pattern review, not pointwise registration proof.

* [sub-01 MRI/electrode overlay](../../outputs/track_b/20261028_wsgzp_overlay_qc/sub-01_geometry_overlay.png)
* [sub-32 MRI/electrode overlay](../../outputs/track_b/20261028_wsgzp_overlay_qc/sub-32_geometry_overlay.png)
* [overlay manifest and input/output hashes](../../outputs/track_b/20261028_wsgzp_overlay_qc/overlay_manifest.json)

## Visual observations

### sub-01

The scalp coordinates form a broadly head-shaped array in the axial projection.
NAS is anterior and LPA/RPA are on opposite lateral sides under the assumed
RAS interpretation. The true-slice panels show only five, five and two scalp
sensors in their respective 2.5-mm slabs, so they cannot establish alignment
of the complete array to the outer scalp boundary. The MIP also projects the
SEEG shafts and scalp net through the head. No gross left/right reversal is
obvious in these views, but this is not a transform check or clearance for a
forward model.

### sub-32

The 29 sensors already identified outside the MRI field of view lie beyond
the superior edge in the coronal and sagittal projections. The axial slice at
the median sensor superior coordinate (voxel 215) contains no visible MRI
anatomy, while the projected sensor cloud still looks approximately
head-shaped. The MRI has positive-valued voxels only through superior plane
212, followed by 43 fully blank planes through the image boundary at 255; 98
of 185 scalp sensors lie above that last positive-intensity plane. This makes
superior MRI truncation a concrete possibility, but it does not establish that
the released coordinates are correct or explain all sensor-to-tissue
distances. A coordinate-frame/transform mismatch remains possible. The
projection illustrates why a head-shaped 2-D shadow cannot resolve this. Keep
`sub-32` excluded until the original transform or authoritative curator QC
resolves it.

## Geometry counts and provenance

* `sub-01`: 185/185 scalp sensors and 179/179 SEEG contacts fall inside the
  NIfTI voxel-cell bounds; all three fiducials are inside.
* `sub-32`: 156/185 scalp sensors fall inside; 29 are outside on the superior
  side. Its last positive-valued MRI plane is 212, with 43 blank superior
  planes to the image boundary; 98/185 sensors lie superior to plane 212. All
  143 listed SEEG contacts and all three fiducials fall inside.
* Both images and their source coordinate files are SHA-256 recorded in the
  JSON manifest. The source MRI and metadata are read-only inputs.

Being inside the NIfTI field of view does not prove that a scalp point is
located on the scalp. SEEG inclusion is only a same-image geometry control.
The visual review is internal and cannot substitute for an independent
reviewer or the missing source transform. Accordingly, the overall status is
`VISUAL_DIAGNOSTIC_ONLY_REVIEW_REQUIRED` for both participants.

## Reproduction

```powershell
.venv\Scripts\python.exe scripts\track_b\render_wsgzp_geometry_overlay.py `
  --dataset-root "..\wsgzp datset\extracted\ccepcoreg" `
  --output-dir outputs\track_b\20261028_wsgzp_overlay_qc `
  --subjects sub-01 sub-32
```

The renderer reads only T1w MRI voxels, electrode TSVs and coordinate
sidecars. It does not access EEG/SEEG sample arrays. It is a visual QC helper,
not a segmentation, coregistration solver, forward model, or neural-data
analysis.

## Cohort-wide extension

On 28 October 2026, the same unchanged renderer was run for all 36 released
participants. The resulting overlays and machine-readable manifest are in
`outputs/track_b/20261028_wsgzp_overlay_qc_all/`. The manifest records the
input and image hashes for every participant, reports `signal_samples_read`
as false, and keeps every participant at
`VISUAL_DIAGNOSTIC_ONLY_REVIEW_REQUIRED`; the cohort render does not clear
anyone for forward modeling.

The cohort-wide affine/FOV screen reproduces the earlier count: 57 of 6,660
scalp sensors fall outside their MRI voxel-cell bounds across eight
participants (`sub-05`, `sub-07`, `sub-10`, `sub-16`, `sub-21`, `sub-29`,
`sub-32`, `sub-33`). `sub-32` remains the strongest anomaly, with 29 sensors
outside the image FOV and 98 above the last positive MRI plane. This is
consistent with MRI truncation but does not rule out a coordinate-frame error.
The other 28 participants having all sensors inside the image bounds is only
a triage result, not a geometry pass: FOV containment cannot verify the
digitizer-to-MRI transform or placement on the scalp. The images are supplied
for curator/reviewer inspection, not presented as independent validation.

Manifest SHA-256:
`4AAB6B6F33D4621928ABC50CC4F66D2D6038D87C8CB841559D1B4A8405642125`.
The all-participant renderer command is:

```powershell
observable_geometry\.venv\Scripts\python.exe `
  observable_geometry\scripts\track_b\render_wsgzp_geometry_overlay.py `
  --dataset-root "wsgzp datset\extracted\ccepcoreg" `
  --output-dir observable_geometry\outputs\track_b\20261028_wsgzp_overlay_qc_all `
  --subjects sub-01 sub-02 sub-03 sub-04 sub-05 sub-06 sub-07 sub-08 sub-09 `
    sub-10 sub-11 sub-12 sub-13 sub-14 sub-15 sub-16 sub-17 sub-18 sub-19 `
    sub-20 sub-21 sub-22 sub-23 sub-24 sub-25 sub-26 sub-27 sub-28 sub-29 `
    sub-30 sub-31 sub-32 sub-33 sub-34 sub-35 sub-36
```

## Gate consequence

The overlays improve reviewability but do not resolve the absent
digitizer-to-MRI provenance. Do not build source models or open neural sample
arrays on the basis of these images alone. The exact curator request and its
acceptance checks remain in `WSGZP_COORDINATE_PROVENANCE_REQUEST.md`.
