# WSGZP scalp-coordinate provenance needed before source analysis

## Why this is needed

The WSGZP paper reports that scalp-electrode positions and anatomical fiducials
were digitized with SofTaxicOptic and coregistered with each participant's
pre-implant 3D T1 MRI. The released BIDS sidecars likewise label the scalp
coordinates and fiducials as T1w millimetres. The study-level registration
workflow is therefore documented; this request is not asking whether
coregistration occurred. The remaining gap is that the extracted release does
not contain the original digitizer inputs, an explicit coordinate-frame
definition or transform record, or participant-level registration QC. The
curation code reads `{participant}_egi_dig.hpts` and writes coordinates from
that file into BIDS, so clarification is needed about whether those values
were already in the MRI frame or were transformed before export. This affects
whether the released positions can be independently interpreted and checked
before constructing a participant-specific scalp forward model.

## Requested items

For each participant intended for analysis, please provide or confirm:

1. Whether the released `electrodes.tsv` and `coordsystem.json` values are
   already the final coordinates in the participant's pre-implant T1w MRI
   frame, as the paper's methods and BIDS declaration imply, or whether a
   further transform is required.
2. The coordinate frame, handedness, axis directions, origin, and units of
   the original digitizer points and of the released BIDS coordinates.
3. If available, the original scalp digitizer points used to create the
   released table, or an authoritative export with labels and units, plus the
   transform or registration procedure/output that maps them to T1w space.
   The curation code refers to source files named
   `{participant}_egi_dig.hpts`.
4. Whether AnonyMI or another anonymization step changed MRI voxel contents,
   the NIfTI affine/header, the digitizer points, or the transform; state
   whether all affected objects were transformed consistently.
5. Available participant-level registration quality-control evidence, such as
   a reviewed sensor/fiducial overlay on the individual T1w MRI, landmark
   residuals, or registration error summary.
6. Confirmation that `AnatomicalLandmarkCoordinates` and electrode labels
   correspond to the same final coordinate frame and that the reported
   registration/QC applies to the released files and MRI version.

No EEG or iEEG recordings, event outcomes, or clinical data are requested for
this geometry question.

## Acceptance checks after receipt

* Verify participant identifiers, labels, units, finite values, and source-file
  hashes.
* If source digitizer points and a transform are supplied, recompute the
  transformation independently and compare every transformed channel and
  fiducial with the released BIDS coordinates using a prespecified tolerance.
  If the released BIDS points are already in T1w coordinates, verify that
  coordinate contract and compare the authoritative QC with the supplied MRI.
* Overlay transformed points and fiducials on the individual MRI and record
  reviewer-visible QC; report exclusions or mismatches without silently
  correcting coordinates.
* Build a participant-specific forward model only after these checks pass.

If the source points/transform cannot be shared, acceptable alternatives are
an authoritative signed statement of the exact transform and coordinate
contract plus per-participant reviewed MRI overlays and registration-error
summaries. A new fit of a standard HydroCel template to the MRI is not a
substitute for verifying the released registration.

## Suggested author request

The linked 2020 Localize-MI dataset paper lists Andrea Pigorini as its
corresponding author (`andrea.pigorini@unimi.it`). This is a reasonable first
contact for the shared cohort and geometry workflow, but it does not establish
that he personally holds the WSGZP export records. If he is not the right
contact, ask to be redirected to the WSGZP data curator or the person who
created the participant-level BIDS geometry. The public curation repository
and the 2022 dataset paper should be included in the request for context.

Suggested message (do not send without the project owner's authorization):

> **Subject:** WSGZP scalp electrode coordinate provenance and QC
>
> Dear Dr. Pigorini and the dataset team,
>
> I am auditing the scalp-electrode geometry in the public WSGZP/iES-CCEP BIDS
> release for a computational source-imaging project. The BIDS sidecars label
> the electrode and fiducial positions as millimetres in T1w space, and the
> paper describes digitization and coregistration to each participant's
> pre-implant MRI. Could you confirm whether the released coordinates are
> already in the coordinate frame of the released T1w MRI, and clarify the
> frame, axes, handedness, and units of the source `.hpts` files used by the
> exporter?
>
> If available, could you point me to the original digitizer points, the
> participant-specific transform or registration record, and reviewed
> electrode/fiducial-over-MRI QC or registration-error summaries? I am
> particularly interested in resolving the flagged geometry for `sub-32`.
> If these materials are held by another curator, I would be grateful for the
> correct contact. I am requesting geometry provenance and QC only, not
> additional recordings or clinical information.
>
> Thank you for your time.

Reference for the listed corresponding-author contact: Mikulan et al. (2020),
[Scientific Data, DOI 10.1038/s41597-020-0467-x](https://doi.org/10.1038/s41597-020-0467-x).
The BIDS export implementation is in the pinned
[`iTCf/ccepcoreg` repository](https://github.com/iTCf/ccepcoreg); the 2022
dataset paper is [Parmigiani et al., DOI 10.1016/j.brs.2022.04.007](https://doi.org/10.1016/j.brs.2022.04.007).

## Independent reconstruction fallback

If the original transform cannot be recovered, the project may evaluate a
**new, explicitly labelled independent registration**. It must not be described
as recovering the original transform or validating the provenance of the
released points. This fallback is eligible only when the participant MRI
contains enough scalp/head surface to assess the full sensor array. For each
participant:

1. Have two reviewers independently mark MRI-visible anatomical landmarks
   that correspond to the released NAS/LPA/RPA points. Record the MRI voxel
   locations, inter-rater differences, and conversion through the exact NIfTI
   affine into world coordinates.
2. Estimate a rigid transform from the released landmark coordinates into
   MRI world space. Do not use the electrode cloud to fit the transform.
   Record handedness, units, determinant, and the transform hash. If only the
   three NAS/LPA/RPA points are used to estimate a six-degree-of-freedom rigid
   transform, their fit residual is not an independent validation measure.
3. Independently inspect the transformed full sensor array against a
   participant-specific scalp/head surface. Record nearest-surface residuals,
   coverage, outliers, and blinded reviewer decisions. If additional digitized
   head-shape points or MRI-visible landmarks are available, hold some out of
   fitting and report their transform residuals. Define any acceptable
   tolerance before viewing participant outcomes; the source dataset provides
   no registration-error threshold, so do not invent one after inspecting
   results.
4. Require acceptable predeclared landmark agreement and independent visual
   QC before building a forward model. A large mismatch or insufficient MRI
   coverage means that participant remains ineligible.

This route creates a new registration with its own uncertainty. It may support
a separately named exploratory model if it passes independent QC, but it does
not resolve whether the historical BIDS coordinates were originally exported
in the same frame. A cropped image such as sub-32's, which omits part of the
superior head surface, cannot independently validate the complete cap under
this fallback; obtain a full-coverage MRI or leave that participant out.
