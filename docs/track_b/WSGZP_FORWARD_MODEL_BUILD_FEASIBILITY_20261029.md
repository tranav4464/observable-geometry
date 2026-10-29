# WSGZP participant-specific EEG forward-model feasibility

**Date:** 29 October 2026

**Status:** implementation route identified; model build not started

**Neural samples accessed:** no

## Decision

SimNIBS CHARM is a viable candidate for participant-specific FEM head meshes
and EEG leadfields on this Windows machine. Do not install or run it yet. The
electrode-to-MRI registration is not independently verified, and the system
has only about 4 GB free. Installing the documented 3 GB application would
leave too little room for a subject mesh, leadfield, intermediates, and saved
replay evidence.

## Evidence and constraints

* SimNIBS 4.6 CHARM can create an individual head mesh from T1w alone, although
  its documentation says skull segmentation is more reliable with T2w. It
  supports Windows and documents an installation footprint of about 3 GB.
  Sources: [CHARM documentation](https://simnibs.github.io/simnibs/build/html/documentation/command_line/charm.html),
  [head-meshing tutorial](https://simnibs.github.io/simnibs/build/html/tutorial/head_meshing.html),
  [installation](https://simnibs.github.io/simnibs/build/html/installation/installation.html).
* SimNIBS EEG leadfield construction requires a subject MRI plus an EEG montage
  registered to that MRI. The documentation says montage coordinates should
  come from digitization or a template warped to the participant, and then be
  checked on the head model. The current WSGZP release declares T1w
  coordinates, but its source digitizer files and digitizer-to-MRI transform
  are absent; current overlays are diagnostic and do not clear participants.
  Source: [EEG leadfield tutorial](https://simnibs.github.io/simnibs/build/html/tutorial/advanced/eeg_leadfields.html).
* The repository environment has MNE 1.13.2 and nibabel 5.4.2. SimNIBS'
  documented direct MNE export is currently compatible only with MNE <=1.5.
  A candidate integration route is to retain SimNIBS' HDF5 leadfield output
  and write a separately tested reader, or create a separate compatible
  interchange environment. Neither route has been implemented or validated.
* The WSGZP coordinate-provenance request is already drafted in
  `WSGZP_COORDINATE_PROVENANCE_REQUEST.md`. It requests original
  `{participant}_egi_dig.hpts` points, coordinate-frame metadata, the saved
  MRI-registration transform and QC, plus confirmation that released
  electrode tables contain final MRI-space positions.

## Gate before any leadfield

For at least one development participant, obtain the digitizer points and
transform or equivalent authoritative provenance. Independently verify every
transformed electrode and fiducial against the released BIDS coordinates and
review the overlay. If that evidence is unavailable, do not call a warped
template participant-specific ground truth; either retain the work as a
software-only demonstrator or obtain an explicitly approved new protocol for
bounded template-warp uncertainty.

After geometry passes and adequate disk space is available, build one
participant's CHARM model, inspect segmentation, generate the EEG leadfield,
verify channel order/reference/source coordinates and archive input/output
hashes. Only then can the source-family protocol be finalized against an actual
participant model. This is a forward-model readiness gate, not novelty
evidence.
