# COG protocol amendment: WSGZP metadata and endpoint contract

**Supersedes:** only the WSGZP-specific assumptions in `COG_PROTOCOL_v1.md`\
**Status:** proposed amendment, not yet locked; signal gate remains closed\
**Why:** metadata audit found absent trial IDs, unequal retained modality epochs,
and an unverified participant-specific WSGZP forward-model pipeline.

## Primary estimand

For a measured WSGZP scalp CCEP response, assess whether prespecified source
families fitted to one set of retained scalp repetitions can predict the
independent repetitions within a tolerance calibrated on training
participants, and whether the candidate explanations agree spatially under a
registered finite forward-model stress ensemble.

This is **repeatability-calibrated model-conditional observability**. It does
not estimate the probability that a candidate is the true neural generator,
and it does not validate complete source recovery.

## Signal and trial contract

* Use only the released baseline-corrected epochs. Raw continuous sources,
  triggers and rejection logs are absent, so filtering, ICA and rejection are
  inherited and cannot be reproduced here.
* Primary scalp response is the channel-by-time matrix in `[20, 500] ms` after
  stimulation. The released epochs span `[-300, 700] ms`, so this interval is
  present. Treat `[0, 20] ms` as artifact-excluded. Do not tune this window
  against localization results.
* Primary within-run split: alternating retained EEG rows into fit and
  validation halves; repeat with halves reversed. The contiguous first-half /
  second-half split is sensitivity analysis only. No row correspondence with
  SEEG is assumed.
* Each run has one stimulation-condition description, but the EEG and SEEG
  epoch tables do not contain unique event IDs or onset indices, and their
  retained counts differ in 319/323 run pairs. Compare only run-condition
  averages across modalities. Never zip trial arrays by row.
* Use leave-one-participant-out outer evaluation. All runs from the held-out
  participant stay out of calibration and model-selection. Within a held-out
  run, fit on one EEG half and evaluate on the other; reverse halves as the
  prespecified repeatability check. Estimate any covariance and thresholds
  only from allowed fit-side data and training participants.
* SEEG is secondary sampled-contact corroboration. A positive response at a
  sampled contact is evidence at that contact; an unresponsive or unrecorded
  location is not a whole-cortex negative label. The stimulation pair is an
  intervention site, not ground truth for later CCEP generators.

## Calibration and decision semantics

Calibrate the held-out prediction tolerance from independent-half repeat
disagreement in training participants only. Report participant-macro results
and participant-bootstrap intervals. This calibration concerns response
repeatability, **not source correctness or nominal coverage of the true source**.

For each prespecified family, retain fits that pass the held-out predictive
repeatability threshold. This is a predictive screen, not calibration of
source correctness. Family labels cannot be treated as competing truth labels:
the families overlap and some are nested. Preserve every predictive-admissible
fit and report the full spatial spread across them.

The previous 20 mm `UNIQUE_ENOUGH` rule is withdrawn. It was an operational
cutoff without validated source-truth calibration or a matched researcher
decision. Until a spatial tolerance or anatomical-parcel decision is justified
and frozen before signal access, report continuous support diameter and
centroid spread, plus sensitivity at 10/20/40 mm. The output is:

* `NO_TESTED_FIT`: no tested family predicts the held-out measured response
  within the training-calibrated tolerance;
* `SPATIALLY_STABLE_WITHIN_TESTED_SET`: reserved until its spatial functional,
  tolerance and matched researcher decision are justified and frozen;
* `SPATIALLY_DISCORDANT_WITHIN_TESTED_SET`: reserved until the same decision
  rule is justified and frozen.

No status based on the tested model set is a posterior probability, family
truth label, or physiological source certificate. A finite perturbation grid
is a stress ensemble, not a continuous guarantee between grid points. Report
best-case/existential compatibility and all-scenario stability separately;
`min_{theta in U}` alone establishes only that at least one tested model fits.

## Source families and comparisons

Retain the v1 point, one-sign area-weighted uniform patches (10/20 mm),
one-sign smooth patches (5/10/20 mm), signed distributed fits, up-to-two
connected patches with one coefficient sign per patch, and flexible direct
constrained fitting. Report family nesting and do not rank a “true” family by
residual alone. Compare identical held-out fields and participant splits with
direct fitting, corrected GBF, MNE/dSPM/eLORETA/LCMV where supported,
PSF/CTF or empirical fidelity, and established patch methods.

The listed stress ranges are not yet a fully enumerated perturbation set:
exact sensor-displacement directions, orientation sampling, cross-product
design and random seeds remain to be frozen. They cannot support a reproducible
uncertainty certificate yet. Any finite grid will be called a stress ensemble,
not a continuous bound. Report existential compatibility separately from
stability across every tested model.

Use prestimulus baseline and time-shifted split/condition controls. Keep
Localize-MI pulse artifacts as a control endpoint and ds004752 as a separate
scalp-to-iEEG transport benchmark; neither substitutes for WSGZP CCEP
validation.

## Forward-model gate

Before opening WSGZP EEG/iEEG sample values for this analysis:

1. resolve the T1w-to-head coordinate contract and inspect an MRI/electrode
   overlay for every proposed participant;
2. create participant-specific scalp/skull/brain surfaces, source spaces and
   forward solutions from that participant's MRI;
3. verify channel order, reference projection, source orientation, covariance
   rank and numerical replay;
4. freeze each model hash and the finite uncertainty scenarios.

The coordinate-only proximity triage subsequently flagged `sub-32` as a
priority unresolved anomaly (median 43.0 mm and 90th percentile 62.7 mm from
thresholded MRI tissue under the declared T1w coordinates). Do not include
`sub-32` in initial forward modeling until its source transform or a reviewed
overlay resolves the discrepancy. Follow-up tests found the discrepancy
unchanged when using every MRI voxel and intensity thresholds 0.1–10, so the
tested cutoff and sampling choices do not explain it. A separate exact affine
screen found 57/6,660 sensors outside MRI FOV in 8/36 participants; all 29
`sub-32` outliers lie beyond one superior FOV boundary, which is compatible
with MRI cropping and is not by itself a registration failure. These checks
prioritize review but do not determine whether the cause is a coordinate
transform, incomplete/masked MRI scalp, or another geometry issue. Do not
silently clip or refit coordinates. No participant is cleared without the
overlay review above.

The earlier coordinate-only audit's `PASS_INTERNAL_GEOMETRY_ONLY` label is
withdrawn. The original data paper reports scalp electrodes and fiducials were
digitized and coregistered with the pre-implant MRI, supporting the sidecar's
`T1w` declaration. The BIDS exporter copies the `.hpts` values without showing
the exact transform, and the source `.hpts` files are absent. MNE notes that
`.hpts` points are usually in head coordinates, but that generic convention
does not disprove the paper's documented MRI coregistration. A reviewed
electrode-to-MRI overlay is still required. The release provides no surfaces
or forward solutions. Until the overlay, participant model and numerical
checks pass, no WSGZP signal array may be opened for source-family fitting.
The threshold-sensitivity and FOV evidence is recorded in
`WSGZP_COREG_AUDIT_20261028.md`, with machine-readable results kept outside Git
beside the large dataset.

## Novelty decision

Novelty requires a predeclared held-out researcher-decision advantage over the
matched baselines. A smaller residual, narrower candidate set, or different
label is insufficient. Because the WSGZP stimulation location is not the
ground truth for post-artifact CCEP generators, report any measured SEEG
agreement as sparse positive corroboration only. If available measurements
cannot test source correctness, the final outcome cannot be `NOVEL METHOD
SUPPORTED`; select `PROMISING BUT UNVERIFIED`, `VALIDATED SOFTWARE
CONTRIBUTION`, or `PIVOT` from the evidence.

## Frozen provenance

The metadata-only WSGZP audit and coordinate-only transform audit are recorded
in `WSGZP_METADATA_AUDIT_20261028.md` and
`WSGZP_COREG_AUDIT_20261028.md`. Neither reads EEG/iEEG sample values. This
amendment does not modify v1 or any sealed Track A artifact.
