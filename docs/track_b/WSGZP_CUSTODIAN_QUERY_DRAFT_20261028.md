# WSGZP custodian query: geometry and cross-modal timing

**Purpose:** resolve the minimum provenance questions needed to decide whether
the released WSGZP derivative supports a participant-specific scalp forward
model and a paired run-condition validation.

**No signal data are requested by this query.** It asks for coordinate
provenance, event-index documentation, and processing provenance only. Do not
send this query without the user's authorization.

## Why we are asking

The WSGZP paper reports that 185 scalp electrodes and fiducials were digitized
and coregistered to each participant's pre-implant MRI. The public BIDS
derivative declares scalp coordinates in `T1w` millimetres. The public
exporter reads `{participant}_egi_dig.hpts` and writes the coordinate table,
but the extracted release does not include those source digitizer files or a
saved digitizer-to-MRI transform. The released EEG/SEEG epoch tables also do
not carry event IDs, trigger times, or sample indices; 319 of 323 paired run
tables have different retained epoch counts between modalities. The analyses currently
support, at most, condition-level averages rather than matched single trials.

## Questions

### A. Scalp sensor geometry

1. Can you provide the original per-participant `{participant}_egi_dig.hpts`
   points, or an authoritative export with channel labels, units, and frame?
2. What coordinate frame, origin, handedness, axis directions, and units do
   those points use? Are the released `electrodes.tsv` values in scanner RAS
   coordinates of the released T1w MRI, or in a digitizer/head frame?
3. What transform or complete registration procedure maps the points into the
   pre-implant MRI? Is a saved transform, landmark residual report, or
   reviewer-approved sensor-on-scalp MRI overlay available?
4. Did AnonyMI or another de-identification step alter the MRI voxels, NIfTI
   affine/header, digitizer points, or transform? Were all changed objects
   transformed consistently?
5. Can you confirm that the values copied into the released BIDS sidecars are
   the final MRI-space positions after registration, and clarify the
   `IntendedFor` filename mismatch (`*_T1.nii` versus released `*_T1w.nii`)?

### B. EEG/SEEG event correspondence

6. Are original trigger/event tables, event IDs, trigger sample indices, or
   unprocessed event logs available to pair each scalp EEG epoch with its
   corresponding SEEG epoch within a stimulation run?
7. If event-level pairing is unavailable, can you confirm that each EEG and
   SEEG derivative file contains epochs from the same stimulation condition
   and acquisition session, despite different rejection counts, so that only
   independent condition averages are scientifically valid to compare?
8. Are the `eeg_badtrials.json` masks ordered against the saved EEG rows, and
   what explains the six runs where mask counts do not match the retained
   epoch count?
9. The metadata-only inventory found the exact same stimulation-condition
   strings in distinct run tables for sub-14 runs 01/02 (`K'7-8 5ma 0.5ms 0.5hz parallel gr_wh`)
   and sub-36 runs 06/07 (`O1-2 3ma 1ms 1hz parallel gr_wh`). Were these
   genuinely independent repeated acquisitions? The public curation repository
   has multiple run-numbering helpers, while the exporter consumes a generated
   `runs_table.csv` not included in that repository. Please provide the
   provenance of this release's run mapping and clarify run order and
   spacing, session relationship, whether any epochs overlap, and whether
   shared preprocessing (including ICA or artifact models) was fitted jointly
   across runs. Are the released EEG/SEEG epochs from corresponding run-level
   repeats, despite the different counts?
   The primary data paper reports 30/40 trials per session and 323/379
   sessions retained after excluding nine sessions with evoked epileptic
   spikes and 47 with fewer than 25 retained trials. However, released
   sub-36/run-06 metadata contain only 13 EEG and 15 iEEG epochs. Can you
   explain the count/selection discrepancy, identify whether this run was in
   the paper's analyzed set, and provide the authoritative trial counts before
   and after rejection for each modality? Please also confirm whether the
   sub-14 pair belongs to that same retained set? The public OSF file index
   currently lists only the multipart derivative archive and
   `eeg_badtrials.json`; no run-map or selection table is present there.

### C. Exported signal processing provenance

10. Which version/commit of `itcfpy.load_scoreg` produced the exported epochs,
   and can its preprocessing implementation or processing logs be shared?
11. What exact filters, artifact removal, rejection rules, reference,
    interpolation, baseline, scaling/normalization, and epoch crop were
    applied to the saved arrays? In particular, do the exported arrays follow
    the paper supplement's `-300 to -50 ms` baseline and SEEG z-scoring, or the
    BIDS metadata's `-300 to 0 ms` mean-subtraction description?
12. Are the continuous raw recordings and their native trigger files available
    under the dataset's existing access and reuse terms? If not, please
    confirm that analyses must be described as inherited-derivative analyses.

## What would resolve the project gates

* For geometry: the original coordinate points plus transform and independent
  replay, **or** an authoritative statement of the coordinate contract plus
  reviewed participant MRI overlays and registration-error/QC evidence.
* For event matching: verified trigger-to-epoch correspondence. If it cannot
  be supplied, scope the study to matched run-condition averages and remove
  single-trial prediction claims.
* For preprocessing: implementation/version or processing logs sufficient to
  establish the saved-array baseline, units, reference, filters, and artifact
  treatment. If unavailable, label the pipeline inherited and limit claims
  accordingly.

Until these points are resolved, keep `PROTOCOL_LOCK.md` unlocked and do not
open WSGZP signal samples for the confirmatory novelty test.

## Evidence and references

* Parmigiani et al. (2022), [dataset paper](https://doi.org/10.1016/j.brs.2022.04.007).
* Official [WSGZP curation repository](https://github.com/iTCf/ccepcoreg),
  including `export_bids.py` and `fx_bids.py`.
* Local metadata and provenance records:
  `WSGZP_METADATA_AUDIT_20261028.md`,
  `WSGZP_PREPROCESSING_PROVENANCE_20261028.md`,
  `WSGZP_COORDINATE_PROVENANCE_REQUEST.md`.
