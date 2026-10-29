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
