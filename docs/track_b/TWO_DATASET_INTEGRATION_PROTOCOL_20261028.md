# Two-dataset integration protocol

**Protocol:** COG-2026-10-28-v1  
**Primary measured route:** iES-CCEP/WSGZP  
**Previously completed separate benchmark:** ds004752
**Synthetic neural data:** prohibited

**Status:** historical proposal, not locked and not authorization to read signal
values. Its decision labels and window must be reconciled with
`COG_PROTOCOL_AMENDMENT_20261028_v4.md` and `PROTOCOL_LOCK.md`. In particular,
the `unique_enough` label is unavailable until an exhaustive spatial
certificate exists; a finite fit list or unrestricted span screen cannot
justify it.

This v1 is historical and not an integrated validation lock. Its proposed
cross-dataset transfer of WSGZP decision thresholds to ds004752 is withdrawn:
the datasets do not share the same participant-specific forward-model and
spatial estimand contract, so threshold transfer would not validate this
source-family observability result. The current grouped-evaluation draft is
`COG_PROTOCOL_AMENDMENT_20261028_v4.md`.

## Route A: WSGZP controlled source-family test

For each eligible participant, use the **released processed scalp response**
associated with the registered intracranial stimulation pulse. Its
preprocessing and artifact correction are inherited and not independently
reproduced from raw recordings; see
`WSGZP_PREPROCESSING_PROVENANCE_20261028.md`. The 50–300 ms interval remains a
candidate N2 window, not a verified artifact-free interval. The stimulation
contact pair is an
independent known intervention endpoint, not a claim that the scalp field has a
single exact cortical source. Fit the declared point, uniform-patch,
smooth-patch, signed-distributed and multi-patch families under the participant
geometry and covariance contract. Apply the fixed forward-uncertainty grid and
produce a source-family report. Follow the participant-grouped evaluation in
amendment v4: keep all runs and events from a participant in the same outer
fold, and use only outer-training participants to tune global choices. Do not
split trial/event rows from one participant across development and confirmatory
test partitions. The decision must not be called calibrated or certified
unless calibration and spatial-coverage procedures are valid and frozen in the
confirmatory lock.

Do not claim that the pulse-artifact interval has been independently removed;
the released derivative's upstream artifact correction is not established by
the inspected curation code. Participants, stimulation sites and sessions are
split before any held-out decision or calibration is inspected. The known stimulation site is
used only as a controlled endpoint for decision-value analysis; it is not
reported as proof of arbitrary endogenous source recovery.

## Separate benchmark: ds004752 scalp-to-iEEG transport

Retain the already completed ds004752 EEG-to-iEEG transport benchmark as a
separate result. It may contextualize the broader software project, but it is
not external validation of the WSGZP source-family certificate and cannot be
used to claim that a WSGZP source-attribution rule transfers. Do not combine
its outputs or threshold decisions with WSGZP unless a common estimand,
measurement model and evaluation protocol are independently established.

HDEEG-IED-SurgOutcome remains the proposed external endogenous route only if
legitimate access is granted. Without that access, make no surgical-outcome or
clinical claim.

## Decision and claim boundary

The strongest defensible result would be a participant-held-out WSGZP decision
that changes a predeclared researcher choice relative to direct fitting and
established resolution/patch baselines, with valid family coverage and
independent evidence for the decision. If matched baselines give equivalent
decisions, the outcome is a validated software contribution, not a novel
method. WSGZP's stimulation site and sparse SEEG responses do not establish
complete physiological source recovery.
