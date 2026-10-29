# WSGZP EEG-to-MRI coordinate compatibility screen

**Date:** 29 October 2026
**Status:** Descriptive metadata/MRI audit; participant geometry gate remains open
**Dataset:** WSGZP / ccepcoreg BIDS release, BIDS 1.6.0
**Scope:** 36 participants; electrode tables, coordinate sidecars, T1w MRI headers/voxels, and root participant metadata only. No EEG/SEEG recordings or epoch arrays were opened.

## Question and method

This is a limited field-of-view and image-occupancy diagnostic under one mapping hypothesis: the released electrode and anatomical-landmark XYZ values, declared in millimetres in `T1w` coordinates, are treated as world coordinates under each MRI's NIfTI qform. It maps the points through the qform inverse, counts points outside the voxel-cell field of view (bounds `[-0.5, shape-0.5)`), and measures rounded-voxel distance to MRI voxels with intensity greater than zero. The latter is only a crude occupancy measure; it is not a scalp segmentation or a registration-error estimate. The audit also checks the expected left/right and anterior landmark ordering. Because external scalp electrodes can lie outside a cropped MRI's acquired volume, an out-of-volume count by itself cannot show that the shared world frame is wrong.

The released sidecars state `T1w` and `mm`, but omit an `EEGCoordinateSystemDescription`. BIDS defines a coordinate frame through its origin, axis directions, and units; its EEG coordinate keywords are restricted, so the sidecar's `T1w` label under the declared BIDS 1.6.0 version requires curator clarification. This metadata ambiguity is not evidence that the numeric coordinates are anatomically wrong. See the [BIDS 1.6.0 coordinate-system appendix](https://bids-specification.readthedocs.io/en/v1.6.0/99-appendices/08-coordinate-systems.html).

The audit deliberately does not fit a transform, correct coordinates, or treat a plausible overlay as registration validation. It requires the stated T1w/mm sidecar fields, a 3D MRI, an explicit qform, and millimetre MRI units. Each participant's source-file hashes and qform/sform codes are retained in the machine-readable evidence. The full run output is `outputs/track_b/20261029_wsgzp_eeg_mri_coordinate_consistency_005/audit.json` (SHA-256 `8fe700c360afa63f26e1b32432b995d71cb99abc195fc76e96583e9612917dc7`; audit script SHA-256 `b86763fac53885d165dfa3114f9692e9534a9bedc132301e922fed5ea19e3444`). The compact participant-level extract is stored alongside this report as `WSGZP_COORDINATE_COMPATIBILITY_SCREEN_20261029.json` (SHA-256 `0d54e4c95c8838372bc4084b48595f31a0c2168c5ba426c56073dd108858363c`) and links to the full JSON by hash.

## Results

- 36/36 participant entries were processed; every MRI reported qform code 1, sform code 0, and spatial units of millimetres.
- Under the direct-qform hypothesis, at least one electrode lay outside the voxel-cell field of view for 8 participants. There were 57 outside-volume electrode points total. The largest counts were sub-32 (29), sub-29 (11), and sub-33 (8). All standard LPA/NAS/RPA fiducials were inside the image volume, and all passed the two simple orientation-order checks. These counts identify where image-overlay QC is especially important; they do not prove a coordinate-frame error because the MRI may not include the external scalp at those locations.
- Across participants, the median of each participant's median electrode-to-nonzero-voxel distance was 10.07 mm (range 1.41 to 38.26 mm). The median participant-level 90th percentile was 15.00 mm (maximum 58.36 mm). These values depend on the crude intensity threshold and rounded voxel lookup and must not be interpreted as sensor-to-scalp error.
- Sub-32 is a conspicuous field-of-view/occupancy triage case under this mapping hypothesis: 29/185 electrode coordinates were outside the MRI volume, and its median in-volume occupancy distance was 38.26 mm. The outside-volume count alone does not justify excluding it. The separate earlier tissue-proximity and overlay audits already flag it for priority review; it should remain outside initial forward modeling until a reviewed scalp overlay or curator evidence resolves that independent concern.

## Interpretation

This screen does **not establish whether** the direct-coordinate-to-qform hypothesis is right or wrong. Points outside the voxel bounds may still be valid coordinates in the MRI's world frame when the scalp lies beyond the acquired image field. The occupancy distances are not scalp-surface distances. The study-level papers describe digitization/coregistration, but the participant-level linkage from original digitizer points and transforms to the released coordinates and MRI has not been demonstrated here. The frame question therefore remains unresolved rather than falsified by this screen.

This screen does not clear the WSGZP forward-model gate and does not authorize EEG/SEEG source analysis. Before using a participant, obtain or verify the coordinate-frame contract and transformation provenance, then inspect sensor and fiducial overlays on the corresponding MRI with documented registration QC. Sub-32 remains unresolved under the earlier tissue-proximity/overlay audits; keep it out of initial forward modeling until those concerns are independently resolved. The current out-of-FOV count alone does not make it ineligible. Do not invent a coordinate uncertainty radius from the occupancy distances.

## Reproduction

Run `scripts/track_b/audit_wsgzp_eeg_mri_coordinate_consistency.py` against the extracted BIDS root, writing both outputs outside that dataset. The script records the code and input hashes and refuses to overwrite either output. For example:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_eeg_mri_coordinate_consistency.py `
  --dataset-root "C:\path\to\ccepcoreg" `
  --output outputs\track_b\RUN_ID\audit.json `
  --summary-output outputs\track_b\RUN_ID\summary.json
```

The compact JSON is generated directly from the full result and links to it by SHA-256; it retains participant-level source-file hashes, qform/sform codes, in-volume counts, distance quantiles, and fiducial checks. Input-contract, affine, boundary, and compacting behavior are covered in `tests/test_wsgzp_metadata_audit.py`; the final focused run passed 12 tests. No signal data are needed for this audit.

On 29 October 2026, the complete repository suite passed **186 tests** after this audit was added. The gate-register validator also passed with **325 evidence paths checked**. These checks validate software behavior and registered evidence paths; they do not validate the WSGZP coordinate transform.

## Decision

**Coordinate gate: OPEN.** This metadata/MRI-only screen is a useful diagnostic for field-of-view and image-overlay triage. It neither validates nor falsifies the participant coordinate frame. It is not registration QC, physiological validation, a novelty result, or evidence of neural-source recovery.
