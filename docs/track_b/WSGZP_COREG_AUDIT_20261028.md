# WSGZP scalp-coordinate transform audit

> **Re-review correction (28 October 2026):** the initial
> `PASS_INTERNAL_GEOMETRY_ONLY` status is withdrawn. The original data paper
> says scalp electrodes and fiducials were digitized with SofTaxicOptic and
> coregistered with each participant's pre-implant MRI. That supports the
> declared MRI registration. However, the released `.hpts` source and exact
> transform are absent; the exporter copies `.hpts` values into BIDS as `T1w`
> without showing a transform. MNE notes `.hpts` points are usually head-frame,
> although that generic convention does not disprove this study's documented
> MRI coregistration. The v3 script therefore reports
> `REVIEW_REQUIRED_VISUAL_COREGISTRATION`: a fiducial-derived transform is not
> independent validation, and a reviewed electrode-to-MRI overlay is still
> required before building a participant forward model or fitting signals.

**Date:** 28 October 2026\
**Audit ID (historical):** `WSGZP-T1W-HEAD-COREG-2026-10-28-v1`
**Scope:** metadata, MRI headers and coordinate geometry only; no EEG/iEEG samples read.

## Result

All 36 participants have 185 scalp-electrode coordinates and NAS/LPA/RPA
fiducials declared in `T1w` millimetres. Under the explicit interpretation that
these values share the MRI's scanner-RAS world frame, MNE's fiducial transform
maps every participant's fiducials onto the expected head axes. The maximum
zero-axis residual across participants is `3.65e-14 mm`; all fiducials map
inside the corresponding NIfTI volume. The transformed electrode radii span
71.0–172.4 mm across the cohort.

The official curation helper `fx_bids.py` writes the scalp electrode and
fiducial coordinates from the same digitization file, labels them `T1w`, and
sets millimetre units. Its loader then passes these coordinates directly to
MNE as `coord_frame='head'`. That loader behavior skips the required coordinate
transform, so this project does not reuse it for forward modeling. The source
sidecars' `IntendedFor` names `*_T1.nii`, while the actual images are
`*_T1w.nii`; the audit resolves the local MRI by participant and records the
original file hashes without modifying the dataset.

## What this establishes and what it does not

The original Parmigiani et al. data paper reports that scalp electrode and
fiducial positions were digitized with SofTaxicOptic and coregistered with the
pre-implant MRI. This makes the sidecar's `T1w` declaration plausible. The
released BIDS exporter copies the `.hpts` coordinates and labels them `T1w`,
but the source `.hpts` and exact transform are not included. MNE's generic
`.hpts` documentation says positions are usually in head coordinates; this
does not establish that this dataset's exported values are wrong, but it means
the exact transform cannot be reconstructed from the release. The previous
fiducial-axis calculation was imposed by constructing the transform from
those same fiducials, and NIfTI-bound containment is not independent
coregistration evidence. The old `PASS_INTERNAL_GEOMETRY_ONLY` label is
withdrawn. The replacement status is
`REVIEW_REQUIRED_VISUAL_COREGISTRATION`.

All 36 EEG sidecars omit `EEGCoordinateSystemDescription`; thus the release
does not spell out the coordinate origin and axis directions alongside its
`T1w`/`mm` label. The BIDS coordinate-system specification defines a coordinate
frame by its origin, axis interpretation and units, and distinguishes scanner
coordinates from file-format and head coordinates. Our affine/FOV screens
explicitly assume the listed `T1w` values are NIfTI scanner-RAS world
millimetres; that is a reproducible computational assumption, not a transform
independently demonstrated by the release. It must be confirmed by the
curators or a reviewed overlay before using these points in a forward model.

### Released-file provenance check

The full extracted WSGZP tree was searched for digitizer/registration artifacts
(`.hpts`, `.elp`, `.sfp`, `.pos`, `.mrk`, and filenames containing `egi_dig`,
`digitiz`, `fiducial`, `coreg`, or `transform`); none were present. The public
OSF storage API lists the `data` folder as the five multipart BIDS archive
segments plus `ccepcoreg-bids.zip`, and `additional_info/eeg_badtrials.json`.
The upstream curation script separately reads
`{subj_name}_egi_dig.hpts` from `dir_dig`, then passes that file to the EEG
coordinate-system and electrode-table writers. It does not expose the source
digitizer file or a transform in the public repository. Therefore, the
declared T1w coordinates cannot currently be independently traced back to the
original digitization using released artifacts.

The remaining provenance request is specific: obtain the original per-subject
digitizer point files (or an authoritative export), the coordinate-frame and
unit definition, the transformation from digitizer/head coordinates into the
anonymized T1w MRI frame, and a statement of whether an anonymization transform
was applied to the MRI and coordinates together. If available, a reviewed
sensor-to-MRI overlay or registration QC report should accompany it. Without
these, rigidly fitting the standard HydroCel net to an MRI surface would be a
new estimated registration, not verification of the released coordinates, and
must not be presented as ground truth. The complete request and acceptance
checks are in
[`WSGZP_COORDINATE_PROVENANCE_REQUEST.md`](WSGZP_COORDINATE_PROVENANCE_REQUEST.md).

## Coarse MRI tissue-proximity triage

A separate coordinate-only screen mapped each declared T1w scalp-electrode
coordinate through the NIfTI affine and measured distance to the nearest
sampled voxel with intensity greater than 10. Voxels were sampled every two
steps, so distances are approximate. This is not scalp segmentation and does
not establish registration. A same-MRI native-space SEEG contact set was
checked as a positive control for the MRI coordinate interpretation. The run
covered all 36 participants, 6,660 scalp electrodes and 6,754 SEEG contacts
with no metadata failures; all 36 NIfTI headers declared millimetres. No
EEG/iEEG samples were read.

Participant median distances ranged from 2.0 to 43.0 mm. `sub-32` was a clear
triage outlier: median 43.0 mm, 90th percentile 62.7 mm and maximum 66.4 mm
across its 185 electrodes. Its NAS was 17.7 mm from the thresholded tissue
voxels, while LPA/RPA were 1.2/1.1 mm away. Meanwhile, native-MRI SEEG contact
medians were 1.0–1.1 mm across participants (with a small number of outlying
contacts), supporting the NIfTI-world interpretation for the SEEG table but
not validating the scalp table. The pattern could reflect an unresolved
scalp-coordinate frame/transform issue, missing or masked scalp tissue in the
MRI, or an artifact of this coarse intensity screen. AnonyMI is documented as
editing image voxels without changing the file header, so this result is not
evidence of a known global anonymization transform. It is not proof of bad
registration, but
`sub-32` must not enter the first forward-model analysis until its MRI overlay
and source coordinate provenance are reviewed. Other participants also still
require overlays; their smaller distances are not a pass. Machine-readable
screen output is outside Git at
`outputs/track_b/20261028_wsgzp_coreg_audit/proximity_v2.json`.

### NIfTI field-of-view coverage check

A separate exact affine-coordinate check mapped every declared scalp sensor
into the corresponding T1w voxel grid and counted points outside the image
field of view (voxel-cell bounds `[-0.5, shape-0.5]`). Eight participants had
any out-of-FOV sensors, for 57/6,660 sensors total. `sub-32` had 29/185
(15.7%), with the most distant point 20.3 mm beyond the image bounds;
`sub-29` had 11/185 (5.9%), `sub-33` 8/185 (4.3%), and `sub-21` 4/185
(2.2%). Four other participants had 1–2 points only, within 1.84 mm. The other
28 participants had all listed sensors inside the MRI FOV. The affine voxel
axes were verified orthogonal before computing the closest point to the FOV
parallelepiped. All 29 sub-32 outliers lie beyond the same superior image
boundary, which is consistent with a cropped MRI and cautions against reading
the count as registration failure. No neural signal arrays were read.

This means some sensor positions cannot be directly checked against that
participant's MRI image content. It does **not** alone show that they are
misregistered: the MRI may simply crop part of the external scalp, where
electrodes sit. Combined with the thresholded-tissue anomaly, it prioritizes
review of `sub-32`, `sub-29`, `sub-33`, and `sub-21`; it does not clear the
remaining participants for forward modeling. Full per-electrode coordinates,
voxel positions and input hashes are recorded in
`outputs/track_b/20261028_wsgzp_coreg_audit/electrode_fov_v1.json`. The audit
script SHA-256 is
`865D54C4340A2DCB7E7D9BC478B64E7A16FDC4A745C26F2080D215EA2B35AFE9` and the
output SHA-256 is
`35D7FA2423EEF3FA94F62AB5F7D735A5A24FCD2785F0EF06873481E016B65482`.
Reproduce with:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_electrode_fov.py `
  --dataset-root "..\wsgzp datset\extracted\ccepcoreg" `
  --output outputs\track_b\20261028_wsgzp_coreg_audit\electrode_fov_v1.json
```

### Threshold-sensitivity follow-up

To check whether the `sub-32` finding was driven by the arbitrary global
intensity cutoff, the same coarse screen was repeated at thresholds 10, 25,
50, 100 and 200, with the same 2-voxel sampling step, for `sub-32` and the
comparison participant `sub-01`. At thresholds 10–50, `sub-32` scalp-electrode
median distance stayed between 43.0 and 43.7 mm (90th percentile 62.7–63.4 mm),
while its native-MRI SEEG median stayed at 1.0 mm. For `sub-01`, the scalp
median stayed 10.8–11.1 mm and the SEEG median stayed 1.1 mm. At thresholds
100 and 200, distances rose for both modalities, showing that the screen
becomes uninformative as the mask shrinks. The low-to-moderate-threshold
stability makes a simple cutoff artifact less likely, but it still cannot
distinguish a scalp-coordinate transform problem from missing/altered scalp
voxels or another MRI-to-electrode mismatch. It is not registration evidence
and does not clear any participant for source fitting.

A stricter follow-up used every voxel (`step=1`) and thresholds 0.1, 1, 5 and
10 for the same two participants. `sub-32` remained at 43.02 mm median and
62.43 mm p90 at every threshold; `sub-01` remained at 10.47 mm median and
12.96 mm p90. The SEEG medians were 0.49 mm for both participants throughout.
This rules out the tested cutoff and sampling choices as explanations for the
large `sub-32` distance. It still cannot establish why scalp coordinates and
MRI tissue differ, because this global-intensity measure is not anatomical
scalp segmentation. Machine-readable result:
`outputs/track_b/20261028_wsgzp_coreg_audit/threshold_sensitivity_low_v1.json`
(SHA-256
`465CE5D5FB71069A2566C5AECF36BC3E8B92C5998601B7805063842EC9F84BC7`).
Re-run with:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_proximity_sensitivity.py `
  --dataset-root "..\wsgzp datset\extracted\ccepcoreg" `
  --subjects sub-01 sub-32 --thresholds 0.1 1 5 10 --step 1 `
  --output outputs\track_b\20261028_wsgzp_coreg_audit\threshold_sensitivity_low_v1.json
```

Reproducible output is
`outputs/track_b/20261028_wsgzp_coreg_audit/threshold_sensitivity_v1.json`.
SHA-256: script
`C5826D8429CCD42BC72B38764EB2E74954B3592FD5014427EE5715CF0F1DB93A`;
result
`050F001CA19F62EF361DE7593E2E493128DA19117C22E3CEF3608E4B013EAB12`.
Re-run with:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_proximity_sensitivity.py `
  --dataset-root "..\wsgzp datset\extracted\ccepcoreg" `
  --output outputs\track_b\20261028_wsgzp_coreg_audit\threshold_sensitivity_v1.json
```

## HydroCel net-shape check

To distinguish a malformed channel layout from a pose-to-MRI mismatch, a
second screen compared all 185 labeled scalp-electrode pairwise distances
against the corresponding positions in MNE's built-in GSN-HydroCel-256
template, allowing one isotropic scale factor. All 36 participants were
audited (6,660 electrodes; no missing template labels or failures; no signal
samples read). Across participants, pairwise-distance correlation ranged
0.9854–0.9966 and scaled-distance RMSE 3.76–8.47 mm. `sub-32` was within those
cohort ranges (correlation 0.9934; RMSE 5.75 mm). Its 185-point net is
therefore internally consistent with the standard layout under this
shape-only check, even though the MRI-proximity screen flags a large
pose/frame discrepancy. Because pairwise geometry is invariant to rigid
translation and rotation, this does not resolve the registration or validate
any sensor-to-MRI transform. It narrows the unresolved question to sensor-net
pose/coordinate provenance versus the MRI or coarse tissue screen; it does
not prove which is responsible. Output is outside Git at
`outputs/track_b/20261028_wsgzp_coreg_audit/net_shape_v1.json`.

Run with:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_net_geometry.py `
  --dataset-root "..\wsgzp datset\extracted\ccepcoreg" `
  --output outputs\track_b\20261028_wsgzp_coreg_audit\net_shape_v1.json
```

Run with:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_electrode_mri_proximity.py `
  --dataset-root "..\wsgzp datset\extracted\ccepcoreg" `
  --output outputs\track_b\20261028_wsgzp_coreg_audit\proximity_v2.json
```

No scalp/skull/brain surfaces, source space, covariance or participant-specific
forward solution has been generated for WSGZP.

MNE documents that its watershed BEM construction uses FreeSurfer's
`mri_watershed`; FreeSurfer is not available in the current Windows
environment, and WSL is not installed. The arithmetic audit makes the
declared-coordinate interpretation reproducible but does **not** resolve the
digitizer-to-MRI transform ambiguity or close the forward-model gate. A
metadata-only visual overlays are now available for all 36 participants in
`outputs/track_b/20261028_wsgzp_overlay_qc_all/`; the cohort-level summary is
in `WSGZP_OVERLAY_QC_20261028.md`. These remain diagnostic and do not
establish registration. All participants remain uncleared for source fitting
until the source transform or authoritative registration QC is supplied and
reviewed.

## Reproduction

```powershell
& 'observable_geometry/.venv/Scripts/python.exe' `
  'observable_geometry/scripts/track_b/audit_wsgzp_coregistration.py' `
  --dataset-root 'wsgzp datset/extracted/ccepcoreg' `
  --output 'observable_geometry/outputs/track_b/20261028_wsgzp_coreg_audit/audit_v3.json'
```

The output JSON is kept outside Git with the large dataset. The first script
reads MRI headers and coordinate metadata; the separate proximity screen
also reads T1w intensity voxels but no neural samples. Tests verify transform
arithmetic, reject incomplete fiducials, prevent the construction-only check
from being treated as frame validation, validate the proximity calculator,
and reject missing or empty dataset paths.

## Provenance and primary sources

* The official dataset helper, `iTCf/ccepcoreg/fx_bids.py`, creates the
  `T1w` coordinates from its digitization input and shows the loader behavior:
  <https://github.com/iTCf/ccepcoreg/blob/main/fx_bids.py>
* The official exporter reads `{participant}_egi_dig.hpts` and writes its
  coordinates and fiducials to BIDS without a documented transform:
  <https://github.com/iTCf/ccepcoreg/blob/main/export_bids.py>
* MNE documents `.hpts` digitizer positions as usually being in head
  coordinates: <https://mne.tools/stable/generated/mne.channels.read_dig_hpts.html>
* BIDS explains that a coordinate system requires a defined origin, axes and
  units, and distinguishes scanner, file-format and head frames:
  <https://bids-specification.readthedocs.io/en/relax-bep032/appendices/coordinate-systems.html>
* Parmigiani et al. report that scalp-electrode positions and fiducials were
  digitized and coregistered with the pre-implant MRI:
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC7189230/>
* Mikulan et al. describe AnonyMI's geometry-preserving image masking and
  state that the method edits image data without changing the file header:
  <https://doi.org/10.1002/hbm.25639>
* Official WSGZP BIDS export code shows the EEG `.hpts` coordinates are copied
  directly into tables declared as T1w, without a transform in the exporter:
  <https://github.com/iTCf/ccepcoreg/blob/main/fx_bids.py>
* The public WSGZP OSF storage listing contains the BIDS archive segments and
  `eeg_badtrials.json`; it does not list the source digitizer inputs:
  <https://osf.io/wsgzp/overview>
* MNE documents the built-in standard montage interface used for the
  translation/rotation-invariant net-shape comparison:
  <https://mne.tools/stable/generated/mne.channels.make_standard_montage.html>
* BIDS defines coordinate-system metadata as the specification for interpreting
  electrode coordinates: <https://bids-specification.readthedocs.io/en/latest/>
* MNE's watershed BEM API documents its FreeSurfer dependency:
  <https://mne.tools/stable/generated/mne.bem.make_watershed_bem.html>
* MNE notes FreeSurfer does not natively run on Windows:
  <https://mne.tools/mne-bids-pipeline/1.9/getting_started/freesurfer.html>
