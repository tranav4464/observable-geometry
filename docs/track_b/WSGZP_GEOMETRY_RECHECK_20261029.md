# WSGZP geometry recheck: released points versus participant MRIs

**Date:** 29 October 2026  
**Scope:** Geometry only. No EEG/iEEG recordings or epoch arrays were opened.

## Finding

The extracted WSGZP package is available locally at `TKS/wsgzp datset/extracted/ccepcoreg`, outside the repository's `observable_geometry/data` tree. It contains a T1w MRI for each of 36 participants, a scalp electrode TSV with 185 coordinate rows per participant under `derivatives/epochs/sub-XX/eeg`, and an EEG coordinate sidecar containing LPA, NAS, and RPA landmarks. The sidecars declare the scalp coordinates and landmarks in T1w millimetres.

This corrects the earlier implication that no released participant geometry was available. The public release does contain enough geometry to run consistency screens. It still does **not** contain the original digitizer `.hpts` files or saved digitizer-to-MRI transform in the extracted package, and the local inventory has no such files. The OSF public file-list audit also lists only the split BIDS archive files under `/data/` and `eeg_badtrials.json` under `/additional_info/`; it exposes no separate transform or digitizer file. That audit inspected public filenames/metadata only. Therefore the original registration cannot be replayed from the published package alone. The local OSF inventory record is `outputs/track_b/20261029_wsgzp_osf_file_index.json` (SHA-256 `8de27898fc69d65da8c9c3cfaceace3d2fd0fbefe5bf71e31fb2c3733834f3be`).

## Rechecks performed

Three existing read-only audits were run against the extracted package:

1. `audit_wsgzp_eeg_mri_coordinate_consistency.py` checked all 36 EEG coordinate tables and T1w MRIs under the explicit hypothesis that the declared XYZ millimetres are in each MRI's NIfTI qform world frame. All 36 participants completed. All three fiducials per participant were within the NIfTI field of view, and the simple LPA/RPA x-order and NAS-anterior-to-ear y-order checks passed for all 36. The electrode field-of-view audit below found 57 of 6,660 electrode points outside the image across 8 participants; the two screens agree on the affected counts.
2. `audit_wsgzp_electrode_fov.py` found 57 of 6,660 released electrode points outside the MRI voxel field of view, across 8 participants: sub-05 (2), sub-07 (1), sub-10 (1), sub-16 (1), sub-21 (4), sub-29 (11), sub-32 (29), and sub-33 (8). Most excursions are small, but sub-32 requires special handling because its MRI is cropped and 29 points are out of bounds.
3. `audit_wsgzp_electrode_mri_proximity.py` compared point coordinates with voxels above a coarse MRI intensity threshold (10, sampled every second voxel). The median across participants of the per-participant median distance was 10.48 mm (range 1.96 to 43.04 mm); the SEEG contact positive-control median was 1.00 mm (range 0.96 to 1.07 mm). This is a triage signal only: the intensity threshold and downsampling do not form a scalp segmentation, so these distances must not be interpreted as registration errors or pass/fail values.

The coarse proximity screen was also rerun at intensity thresholds 1 and 40, keeping the same MRI sampling step of 2. Across the 36 participants, the median of participant-level median distances was 10.41 mm (range 1.74–43.04 mm) at threshold 1, 10.48 mm (1.96–43.04 mm) at threshold 10, and 10.83 mm (2.92–43.67 mm) at threshold 40. `sub-32` was the only participant above 20 mm at all three thresholds; `sub-25` remained lowest. This shows the coarse outlier ranking is not sensitive to these three intensity cutoffs. It does **not** validate the ranking anatomically: all three runs use the same non-scalp tissue thresholding method and qform assumption. The JSON output SHA-256 values are `D6F522C5E9C179A60D85377FEE91FF0384473EF40918B92C0278C7668A08E314` (threshold 1), `E6B3B9D4EB8080B6155FC0B82553B3E9870CC82CE02916A34F1F12A0B3D37F80` (threshold 10), and `BAEC8DE7F4A938E3D9A0B1D9975A3F8BFECC1BE0AA19B4114DF573A3ADF51F65` (threshold 40). The full per-electrode report is local, ignored run evidence.

The screens support a plausible coordinate orientation and identify participants/points that need inspection. They do not prove that electrodes sit on the correct participant's scalp. In particular, a coordinate can be inside an MRI's field of view while being anatomically misplaced; likewise, fiducial axis order is only a weak sanity check.

## Verification status

**Status: PARTIAL GEOMETRY CONSISTENCY, REGISTRATION NOT VERIFIED.**

The release metadata also remain ambiguous for strict interpretation: scalp sidecars use `EEGCoordinateSystem: T1w` without an axis/origin description, and their `IntendedFor` field names `sub-XX_T1.nii` while the released MRI is `sub-XX_T1w.nii`. These metadata defects do not prove the numeric points are wrong, but they leave the coordinate contract and MRI association insufficiently documented. BIDS expects the coordinate system description to specify axes and origin; see the [BIDS v1.6 EEG specification](https://bids-specification.readthedocs.io/en/v1.6.0/04-modality-specific-files/03-electroencephalography.html). MNE documents MRI/head coregistration, digitizer-to-skin distance checks, and an [interactive coregistration GUI](https://mne.tools/stable/generated/mne.gui.coregistration.html).

Do not approve participant-specific forward modeling on these screens alone. The strongest verification requires either the original digitizer points plus the exact transform and registration QC, or a new, independently reviewed surface-overlay validation with a suitable MRI scalp segmentation and a prespecified tolerance grounded in the acquisition system's accuracy. If a transform is reconstructed from the three released fiducials, those same three points cannot serve as independent validation. Use held-out head-shape points or other independently localized landmarks to test it. If only surface overlays can be obtained, report that as independent plausibility review rather than transform provenance.

## Reproduction

From the repository root in PowerShell, use the extracted dataset path and a fresh output directory (the audit scripts refuse to overwrite outputs):

```powershell
$dataset = "C:\Users\TRANAV\OneDrive\Desktop\TKS\wsgzp datset\extracted\ccepcoreg"
$out = "outputs\track_b\wsgzp_geometry_recheck"
.\.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_eeg_mri_coordinate_consistency.py `
  --dataset-root $dataset --output "$out\coordinate_consistency_full.json" `
  --summary-output "$out\coordinate_consistency_summary.json"
.\.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_electrode_fov.py `
  --dataset-root $dataset --output "$out\fov_screen.json"
.\.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_electrode_mri_proximity.py `
  --dataset-root $dataset --output "$out\proximity_screen.json"
.\.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_electrode_mri_proximity.py `
  --dataset-root $dataset --threshold 1 --output "$out\proximity_threshold1.json"
.\.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_electrode_mri_proximity.py `
  --dataset-root $dataset --threshold 40 --output "$out\proximity_threshold40.json"
```

The executed evidence is in the ignored local directory `outputs/track_b/20261029_wsgzp_geometry_recheck/`. The compact coordinate report SHA-256 is `34c7ecd9dd437775a9677ed6a57edfbe8c3c095ce577968027edcab2ac90a512`. The full report records per-participant MRI, electrode TSV, and sidecar hashes; it contains coordinates and should remain in the local audit outputs rather than being published unnecessarily. The full audit explicitly records that signal samples were not accessed.

## Next geometry gate

For each candidate participant, verify the image/coordinate convention, overlay all scalp sensors and fiducials on axial/coronal/sagittal views and a 3D scalp surface, report sensor-to-surface residuals and outliers, and have a second reviewer inspect the overlay. Resolve sub-32's crop or exclude that participant before forward modeling. Obtain the source `.hpts`, exact transform and registration QC from the data curator if possible. Freeze acceptance criteria before reviewing candidate overlays. Only after that gate passes should a participant-specific head model or source-localization evaluation use the geometry.

The 29 October local feasibility check found that the current Windows environment lacks the documented FreeSurfer/MNE watershed and SimNIBS `charm` tools, with about 3.43 GB free on its only available volume. See [the tooling feasibility note](WSGZP_SCALP_SURFACE_TOOLING_FEASIBILITY_20261029.md). This explains why no scalp segmentation or new overlay validation was produced in this environment; it does not change the coordinate-validity conclusion above.




