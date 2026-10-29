# COG protocol amendment v4: grouped participant evaluation

**Status:** proposed correction; metadata/preprocessing audit only\
**Supersedes:** v3 interleaved within-run A/B/C row assignment for primary
confirmatory evaluation\
**Signal gate:** closed; this amendment does not authorize sample access

## Why v3 is not the confirmatory split

The v3 draft deterministically interleaves epoch-table rows within each run
into A/B/C. This prevents literal row reuse by the downstream code, but it is
still an event-level split. It cannot establish participant/session-level
generalization, and the paper supplement shows that trial rejection and other
preprocessing occurred before the released epochs were exported. ICA fitting
scope is not specified. The released derivative therefore cannot support an
end-to-end raw-to-output holdout based on these row partitions.

The v3 manifest and its verification remain useful as metadata-coverage and
assignment diagnostics only. They are not the confirmatory split and must not
be cited as evidence of independent held-out performance.

A replacement metadata-only leave-one-participant-out inventory has been built
and independently replayed:
`outputs/track_b/20261028_wsgzp_participant_split/participant_grouped_manifest_v1.json`
and `verification_v1.json`. It covers 36 participants, 323 EEG run tables and
10,088 metadata rows, with all runs assigned to their participant's outer
fold. No BIDS session entity appears in the EEG epoch paths; run labels encode
stimulation conditions and are not assumed to be independent sessions. The
verification proves metadata grouping and file-hash agreement only, not
forward-model validity or analysis readiness.

## Confirmatory split unit

Keep every recording, stimulation pair, run, and event from one participant in
one outer fold. Do not divide epoch/event rows from a participant between
training, calibration, threshold selection, and confirmatory test sets.
Use nested participant-grouped evaluation:

1. **Outer fold:** hold out one participant (or a prespecified participant
   group) in full. No response values, SEEG outcomes, event identifiers or
   derived summaries from that participant may tune model choices, thresholds,
   family constraints, calibration, or stopping rules.
2. **Inner development:** use only outer-training participants for selecting
   all global method parameters, calibration maps, and decision thresholds.
   Use grouped inner folds by participant, not by epoch.
3. **Held-out participant evaluation:** run the frozen algorithm on the
   participant's released processed scalp responses. Participant-specific
   anatomy/forward model and any prespecified unsupervised baseline covariance
   may be supplied as test-time inputs only if their construction is frozen,
   outcome-blind, and recorded. No held-out response or SEEG label may alter
   global thresholds or model selection.
4. **Aggregation:** report participant-macro metrics and uncertainty with the
   participant as the independent resampling unit. Runs and events are nested
   observations, not independent participants.

The primary endpoint is therefore cross-participant performance of a frozen
analysis procedure, conditional on the released processed derivative and on
valid participant-specific geometry. The protocol must state explicitly that
this does not validate raw preprocessing or remove possible within-participant
transductive preprocessing inherited from the dataset. The supplement/exporter
baseline and scale discrepancy, and the unrecorded ICA fitting pool, must be
reported in the analysis lock.

## Repetition and response handling

For each held-out stimulation condition, average only the released trials
assigned to that condition using the frozen procedure. Do not create train and
test sets by splitting repeated event rows. EEG and SEEG rows must not be
paired unless a documented shared event key and equal acquisition timing
establish the pairing. Use SEEG only as sparse positive corroboration of
responsive contacts; it is not a whole-cortex negative map or complete ground
truth for the distributed CCEP generator.

The fixed scalp interval 50–300 ms may be used only as a prespecified
released-derivative response window after the baseline and preprocessing
contracts are documented. It is not certified artifact-free. The Supplement
1 versus BIDS exporter baseline discrepancy, and the undocumented ICA fitting
pool, must be reported as inherited limitations. Any analysis that depends on
the precise released-array baseline or scale must resolve that discrepancy
before signal access.

## Decision and claim limits

This split can test whether frozen analysis choices generalize to unseen
participants under the same data-release conventions. It cannot by itself
prove endogenous source recovery, complete source truth, clinical utility, or
novelty. A novel-method claim still requires a prospectively specified
decision-value advantage over matched direct constrained fitting, GBF,
resolution/patch baselines, with valid source-family and forward-uncertainty
coverage. If those baselines make equivalent held-out decisions, report a
validated software contribution or pivot.

## Required freeze before sample access

Freeze and hash the exact dataset release and license, group-fold assignments,
channel and reference contract, baseline/scaling decision, permitted
test-time participant-specific inputs, forward-model construction and
uncertainty set, source-family definitions, covariance procedure, response
window, primary spatial functional, comparator implementations, decision
threshold/calibration procedure, controls, and stopping rules. The outer
held-out predictions and decision rule must be serialized before evaluation
metrics or held-out SEEG outcomes are opened.
