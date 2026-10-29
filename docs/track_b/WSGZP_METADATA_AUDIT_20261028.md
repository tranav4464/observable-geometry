# WSGZP metadata-only audit and analysis gate

**Original audit:** `WSGZP-METADATA-2026-10-28-v1`\
**Metadata-contract recheck:** `WSGZP-METADATA-2026-10-29-v2`\
**Run date:** 29 October 2026\
**Status:** `REVIEW`\
**Signal samples read:** no

## What was inspected

The audit script reads BIDS JSON/TSV files, hashes MRI and geometry files, and
reads NumPy headers only. It does not materialize EEG/iEEG samples. The complete
machine-readable output is `outputs/track_b/20261028_wsgzp_metadata_audit/audit.json`;
the runnable audit is `scripts/track_b/audit_wsgzp_extracted_metadata.py`.

The extracted release contains 36 participants, 323 run pairs with matching
scalp EEG and SEEG stimulation descriptions, individual `T1w` MRIs, 185 scalp
electrode coordinates per participant, and native-MRI plus MNI SEEG contact
tables. Coordinates are declared in millimetres for scalp EEG and metres for
SEEG. The archive's `LICENSE` identifies CC BY-NC-SA 4.0. The six multipart
download files have byte counts and SHA-256 values recorded as matching in
`wsgzp datset/data/WSGZP_DOWNLOAD_MANIFEST.json`. Keep the recordings and MRI
files outside Git. The manifest SHA-256 is
`746a29a365fb17830e9077dcca5d553762e2e9f8df03f229b6b56a6824e391e7`.

The derivatives contain 10,088 retained EEG epochs and 11,070 retained SEEG
epochs across the 323 paired runs. The released channel metadata reports EEG
average reference, 0.5–45 Hz filtering and 1,000 Hz sampling; SEEG is bipolar
referenced, 0.5–300 Hz and 1,000 Hz. Values are in volts. Epoch metadata states
mean baseline correction over -300 to 0 ms, with each one-second epoch aligned
at 300 ms. The derivative description reports manual bad-channel/epoch
rejection, third-order Butterworth filtering, and EEG ICA for blink removal.
These steps are inherited; the original continuous sources named by the
derivative `Sources` fields are absent from this extracted release.
The official curation helper writes the same single `trial_type` description
for all epochs in a run and exports no event identifier or trigger timestamp.

An audit of the official curation code pinned to commit
`8721fc04328c00b131659915dfbfa569bd342b54` shows that the BIDS exporter calls
an external `itcfpy.load_scoreg`, crops the returned epoch object and saves it,
while writing cutoff/reference/baseline fields as metadata. The exporter does
not show how those operations were performed. Because the external loader may
apply preprocessing internally, this audit cannot establish whether any
specific transformation was absent. The upstream loader implementation and
raw preprocessing inputs were not available in the inspected repository.
See `WSGZP_PREPROCESSING_PROVENANCE_20261028.md`.

## Findings that change the protocol

1. **No trial-level EEG/SEEG pairing is available.** 319 of 323 paired runs
   have different retained epoch counts. No epoch table has a unique event ID,
   onset or sample index. The runs do share the same stimulation condition.
   Therefore analyses may pair only run-level condition averages. Do not zip
   EEG and SEEG arrays by row or claim matched single-trial observations.
2. **Sub-33 has 50 good SEEG channel/run entries without exact native
   coordinates.** Ten bipolar labels (`V1-2`, `V2-3`, `V3-4`, and `V6-7` through
   `V12-13`) are absent from its native coordinate table in five runs. Exclude
   those channels from spatial comparisons unless the custodian supplies a
   documented alias or coordinate source; do not infer their positions.
3. **Scalp coordinate sidecars have an unresolved MRI association for all 36
   participants.** Each populated `IntendedFor` points to `sub-XX_T1.nii`, while the
   actual file is `sub-XX_T1w.nii`. The coordinates are declared in `T1w`
   space, but that label alone does not specify the EEG coordinate convention
   (axes and origin) or establish the transform provenance. Under the dataset's
   declared BIDS 1.6.0 version, the EEG coordinate appendix lists `CapTrak`
   and standard template identifiers, and separately describes `individual`
   for participant-specific anatomical space. The sidecar's `T1w` declaration
   does not document which supported convention is intended or identify the
   transform. A custom frame can instead be described with `Other` and its
   required coordinate-system description. This is a metadata/provenance
   ambiguity, not evidence that the coordinates are anatomically wrong.
   Preserve the source files and record a local, explicit path-resolution rule
   if the forward-model toolchain requires it. The
   official `fx_bids.py` helper labels these scalp coordinates as
   `coord_frame='head'` when loading, despite the T1w/mm declaration. Do not
   reuse that loader unchanged: convert units and apply a checked T1w-to-head
   transform before passing sensors to an MNE forward model.
4. **The derivative `dataset_description.json` is invalid strict JSON** because
   of trailing commas. The audit parser removes only trailing commas in
   memory, records the warning, and does not edit the dataset.
5. **No participant-specific forward model is supplied.** The release has
   MRIs and electrode/contact coordinates, but no cortical surfaces, BEM
   surfaces, source spaces, or forward solutions. MNE and nibabel are available
   in the project environment; FreeSurfer segmentation executables are not
   present on `PATH`. MRI and sensor-coordinate presence alone does not close
   the forward-model gate.

The 29 October contract recheck found the same `T1w` coordinate declaration
and nonexistent `IntendedFor` target in all 36 scalp EEG sidecars. The
coordinate label is not an allowed EEG coordinate-system keyword under BIDS
1.6.0; a metadata-only validator fixture confirmed both the EEG and anatomical
landmark fields are rejected. This establishes metadata nonconformance, not
that the numeric locations are anatomically wrong. It remains metadata-only
and did not read EEG/SEEG samples. The BIDS 1.6.0
requirements are documented in the official [EEG specification](https://bids-specification.readthedocs.io/en/v1.6.0/04-modality-specific-files/03-electroencephalography.html)
and [coordinate-systems appendix](https://bids-specification.readthedocs.io/en/v1.6.0/99-appendices/08-coordinate-systems.html).
The updated machine-readable report is generated locally at
`outputs/track_b/20261029_wsgzp_metadata_contract_audit/audit.json` (outputs
are excluded from Git); the script and regression tests are tracked.

### Coordinate-only follow-up

The initial `WSGZP_COREG_AUDIT_20261028.md` transform result is superseded. The
original Parmigiani et al. data paper reports scalp electrodes and fiducials
were digitized with SofTaxicOptic and coregistered with each participant's
pre-implant MRI, supporting the sidecar's `T1w` declaration. The exporter reads
`{participant}_egi_dig.hpts` and copies its values into BIDS without showing
the exact transform; the source `.hpts` files are absent. MNE says `.hpts`
locations are usually head-frame, but this generic convention does not
disprove the paper's MRI-coregistration method. The previous fiducial-axis
check was imposed by the transform built from those same fiducials, and
containment in the MRI voxel bounding box is not independent overlay evidence.
The v3 audit status is `REVIEW_REQUIRED_VISUAL_COREGISTRATION`; no participant
forward model or signal fitting may proceed until a reviewed MRI/electrode
overlay and model checks pass.

A separate coarse T1w-intensity proximity screen (not a segmentation or
registration test) identified `sub-32` for priority review: its 185 electrode
coordinates have median nearest-thresholded-tissue distance 43.0 mm and
90th-percentile distance 62.7 mm under the declared T1w frame. The NAS is
17.7 mm from thresholded tissue while LPA/RPA are 1.2/1.1 mm away. Treat this
as an unresolved anomaly, not proof that the coordinates are wrong. Exclude
`sub-32` from initial modeling until the original coordinate transform or a
reviewed MRI overlay explains it. All other subjects still require visual
overlays; coarse proximity alone does not clear them. See
`WSGZP_COREG_AUDIT_20261028.md` and the machine-readable output outside Git.

## Scientific interpretation limits

The stimulation pair is an intervention location, not a complete ground-truth
map of all neural generators of the later CCEP. SEEG provides sparse measured
responses, not proof that unrecorded locations are inactive. The derivatives
do not permit exact event-level matching across modalities. Any primary
analysis must state these limits and describe its output as model-conditional
ambiguity or measured response concordance, not validated whole-cortex source
recovery.

The 2026 GBF article already evaluates intracranial stimulation and names this
dataset; its stimulation-site validation includes 18 sessions from two
participants. Reusing WSGZP is not independent cohort validation. In addition,
Phee et al. (2026; article date 8 September 2026, print issue December) report
subject-specific MRI-informed EEG source localization with confidence
intervals and recorded intracranial-stimulation evaluation. Generic calibrated
source-localization confidence is therefore a direct priority threat. The
article's exact calibration equations still require inspection before any
novelty statement.

## Gate decision

**Metadata gate:** passed for confirming that the measured recordings, MRI,
and geometry are present and identifying their contracts.\
**Signal-analysis gate:** not passed. Before opening samples, the project must
resolve participant-specific forward construction, the sub-33 coordinate
exclusion, the run-average estimand, the response/reference definition, and the
calibration target. The family certificate must report the spatial claim
shared by all plausible explanations; residual ranking cannot identify a
unique family when the families overlap or nest. Also distinguish existential
fit over an uncertainty ensemble from a claim that holds uniformly over the
entire uncertainty set.

### Follow-up: EEG epoch-index feasibility (metadata/header only)

The separate `wsgzp datset/additional_info/eeg_badtrials.json` file contains
323 binary masks, one for each paired run. A new read-only audit compared the
number of zeros in each mask with the exported EEG epoch TSV row count and
the first dimension of the corresponding `.npy` **header** (the array payload
was not read). All 323 NPY first dimensions match their TSV row counts; for
317 runs, the zero count also matches both. Six runs do not:

| Participant | Run | Mask length | Zero count | Exported epochs |
|---|---:|---:|---:|---:|
| sub-06 | 04 | 18 | 17 | 16 |
| sub-13 | 02 | 40 | 37 | 33 |
| sub-19 | 03 | 40 | 38 | 31 |
| sub-19 | 05 | 40 | 37 | 36 |
| sub-19 | 06 | 40 | 37 | 34 |
| sub-26 | 03 | 30 | 28 | 27 |

The 317 count matches make a candidate original-row index map possible **only
if** zero means retained, the mask refers to the same input epochs, order is
preserved, and no additional rejection occurred. Those semantics and order
are not documented by the inspected exporter, so the map is not accepted as
event identity or proof of independent trials. The mask contains no onset
times; it cannot validate non-overlap, preprocessing independence, or EEG to
SEEG trial pairing. The six mismatches require case-specific reconciliation
before any row-level use. Therefore this result modestly improves the
prospects for a conditional EEG-only derivative repeatability analysis, but
does not clear its independence gate or authorize signal access.

Reproduce with `scripts/track_b/audit_wsgzp_trial_index_feasibility.py`; its
machine-readable output is
`outputs/track_b/20261028_wsgzp_trial_index_feasibility/trial_index_audit.json`
(SHA-256 `2f612037b30f24882c31d69de824bc7a1509eebc5830b293d268864e498cc81d`).
The script reads TSVs, the JSON mask and NPY headers only; it explicitly marks
mask semantics, row-order preservation, event timing and temporal
non-overlap as unverified.

## Reproduction

From the `observable_geometry` directory:

```powershell
.venv\Scripts\python.exe scripts\track_b\audit_wsgzp_extracted_metadata.py `
  --dataset-root "..\wsgzp datset\extracted\ccepcoreg" `
  --output outputs\track_b\20261028_wsgzp_metadata_audit\audit.json
```

The audit is intentionally read-only with respect to the extracted dataset.


### Candidate repeated stimulation-condition runs (metadata only)

A separate scan of the extracted derivative's 323 paired EEG/SEEG epoch
metadata tables found two pairs of distinct run tables with an identical
participant and exact `trial_type` string: sub-14 runs 01/02 and sub-36 runs
06/07. The respective EEG/SEEG epoch counts are 37/40 versus 36/40 and 13/15
versus 25/30. This identifies candidate same-condition run repeats, not
independent replication. The tables have no shared event identifiers or
onsets, EEG and SEEG rows cannot be paired, and the release does not establish
run spacing, acquisition independence, epoch overlap, or whether preprocessing
was fitted jointly. The paper's minimum-trial rule also makes sub-36/run-06
ineligible for a paper-matched repeat test unless its count and session
membership are reconciled. Sub-14 runs 01/02 pass the simple count screen but
remain one unverified participant pair. At most, they could motivate a
descriptive within-participant run comparison if independence is confirmed;
they do not support confirmatory repeatability, source truth, or a novelty
claim. Only TSV metadata were read; signal samples were not opened. See
`WSGZP_REPEAT_RUN_FEASIBILITY_20261028.md` and the machine-readable inventory
under `outputs/track_b/20261028_wsgzp_repeat_run_audit/`.

The primary dataset paper reports that its analyzed 323/379 stimulation
sessions excluded 47 sessions with fewer than 25 retained trials and nine
sessions with evoked epileptic spikes. This raises a specific unresolved
cross-check: sub-36/run-06 in the released derivative has 13 EEG and 15 iEEG
epoch rows. Its membership in the paper's retained set and the meaning of the
released counts are unknown. Do not treat sub-36 runs 06/07 as a paper-matched
repeat pair unless this is reconciled; sub-14 runs 01/02 exceed 25 rows in
both modalities but still lack acquisition and preprocessing independence
evidence. See the focused feasibility audit and the custodian query draft.
The paper source is Parmigiani et al. (2022),
[doi:10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007).
