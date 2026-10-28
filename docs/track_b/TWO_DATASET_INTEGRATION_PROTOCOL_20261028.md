# Two-dataset integration protocol

**Protocol:** COG-2026-10-28-v1  
**Primary measured route:** iES-CCEP/WSGZP  
**Independent measured route:** ds004752  
**Synthetic neural data:** prohibited

## Route A: WSGZP controlled source-family test

For each eligible participant, use the measured scalp response after the
registered intracranial stimulation pulse. The stimulation contact pair is an
independent known intervention endpoint, not a claim that the scalp field has a
single exact cortical source. Fit the declared point, uniform-patch,
smooth-patch, signed-distributed and multi-patch families under the participant
geometry and covariance contract. Apply the fixed forward-uncertainty grid and
produce the conservative `unique_enough`, `ambiguous` or `unsupported`
decision.

The pulse-artifact interval is excluded before the CCEP response window is
constructed. Participants, stimulation sites and sessions are split before any
held-out decision or calibration is inspected. The known stimulation site is
used only as a controlled endpoint for decision-value analysis; it is not
reported as proof of arbitrary endogenous source recovery.

## Route B: ds004752 independent transport test

Use participant-level held-out scalp EEG and simultaneously recorded iEEG from
the CC0 ds004752 release. The outcome is measured scalp-to-iEEG transport or
contact-level observability, not surgical localization. The ds004752 release
does not supply the same participant-specific MRI/forward-model contract as
WSGZP, so it cannot be silently pooled into the WSGZP source-family certificate.

The certificate thresholds, family definitions and uncertainty grid are fit or
locked on the WSGZP development partition only. ds004752 evaluates whether the
resulting ambiguity/abstention rule transfers to a different measured cohort.
No participant, event or contact from ds004752 may be used to tune the WSGZP
threshold, select a family, or choose a favourable window.

## Decision and claim boundary

The strongest defensible result would be a held-out measured decision that is
calibrated on WSGZP, transfers to ds004752, and changes a predeclared researcher
choice relative to direct fitting and established resolution baselines. If the
rule does not transfer or gives equivalent decisions, the outcome is a
validated software contribution, not a novel method. Neither route alone
establishes complete physiological source recovery.
