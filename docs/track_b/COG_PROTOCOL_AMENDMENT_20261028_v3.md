# COG protocol amendment v3: three-partition held-out evaluation

**Status:** historical proposal, superseded for confirmatory splitting by v4; not a signal-analysis lock\
**Supersedes:** split and evaluation provisions in amendments v1/v2 only\
**Signal gate:** remains closed

## Why three partitions

The WSGZP metadata contain 323 EEG run tables and 10,088 retained-epoch rows.
Each run has one stimulation condition, with 9–57 EEG rows (median 29). A
deterministic three-way interleaved partition is feasible by counts: every A,
B and C partition has at least three rows in every run. The metadata-only
draft manifest records the exact row assignments and source TSV hashes at
`outputs/track_b/20261028_wsgzp_split/metadata_split_draft_v1.json`.

Three partitions are required because B may be needed to filter or refine
candidate explanations. The data used to make that decision must not also
score its performance.

## Participant and repetition split

* Outer evaluation uses leave-one-participant-out. Every run from the held-out
  participant is excluded from calibration, hyperparameter selection and
  source-model selection.
* Within each run's EEG `epochs.tsv`, assign its zero-based row index modulo 3:
  `0 -> A`, `1 -> B`, `2 -> C`. This is interleaved table order, not pairing
  with any SEEG event row. The exact deterministic assignments and SHA-256 of
  each source table are in the draft manifest.
* A loader must later verify, after signal access is authorized, that each
  epoch-array row count matches the metadata table. It must preserve this
  row-index map and never zip EEG and SEEG rows. The released EEG/SEEG epoch
  counts differ and shared trial IDs are absent.
* Partitions are **disjoint**, not assumed statistically independent. The
  final analysis must assess run/time dependence and report the endpoint as
  within-run held-out repetition prediction unless stronger independence is
  justified. Participant-level uncertainty must not count A/B/C partitions
  as independent participants.

## Roles of A, B and C

### A: fit and propose

Use A only for the primary covariance estimate, candidate fitting, model
parameter estimation and initial source-family explanations. The covariance
must use only A-side baseline samples (or a separately specified baseline
estimator fitted on training participants), with averaging handled explicitly.

### B: finalize the decision

Use B only to apply predeclared candidate-acceptance/refinement rules to the
A-derived candidates and produce the source-family report, spatial functional
and researcher-facing decision. Any threshold estimated for the held-out
participant must come from the outer training participants. Before C is
opened, serialize and hash all retained candidate predictions, outputs,
baseline outputs, code/configuration and decision.

### C: final evaluation

C is not used to fit, select, reject, recalibrate or revise candidates. Score
the frozen outputs and matched baseline predictions on C. Report participant-
macro prediction metrics, participant-bootstrap intervals, coverage and
selective-risk summaries where their interpretation is valid. If C causes a
change to the method, threshold, candidate set or decision rule, that C
partition is no longer independent confirmation; use a new held-out run or
dataset for confirmation.

## What the output can claim

One fitted map per family, or a finite set of optimizer-returned examples, is a
**tested-explanation report** only. It cannot support a universal statement
that all admissible sources in a family share a location. A **spatial
certificate** requires valid optimization extrema or exclusion bounds that
cover every admissible explanation within every declared family and every
claimed forward-uncertainty case. If exhaustive coverage is not established,
report the tested set, its search limits and unexamined possibilities, and do
not use “certificate” as if it were exhaustive.

The A/B/C endpoint concerns predictive repeatability and model-conditional
spatial ambiguity. It does not establish the true neural generator,
whole-cortex activity, calibrated source correctness or full physiological
recovery. SEEG remains sparse positive corroboration; the stimulated contact
is not a complete source label for a later distributed CCEP response.

## Pre-signal freeze still required

Before opening EEG/SEEG samples, the team must freeze and hash: dataset release
and license; channel and reference contract; preprocessing limits; coordinate
provenance and participant forward models; primary time window and temporal
source model; family constraints and complete-search status; forward
uncertainty scenarios; spatial functional and threshold; calibration and
covariance procedures; matched baselines; one researcher decision; stopping
rules; and code/configuration. The metadata split manifest is a draft
contribution to this freeze, not authorization to analyze signals.

## Primary-data controls and limitations

The original continuous recordings and trigger/rejection logs are absent, so
filtering, ICA and artifact rejection remain inherited rather than independently
reproduced. The paper supplement documents the study-level scalp sequence
(artifact removal, 0.5–45 Hz filtering, epoching, interpolation, average
rereferencing, baseline correction and ICA), but the released exporter delegates
to an external loader and does not link those exact operations to the saved
arrays. ICA fitting scope across the proposed A/B/C partitions is unknown. No trial-level
EEG-SEEG pairing is permitted without shared event identifiers. The run-level
SEEG response may be used only as separately averaged sparse-contact
corroboration, never as a whole-cortex negative map. Localize-MI remains an
artifact control, and ds004752 remains a separate EEG-to-iEEG transport
benchmark; neither replaces the WSGZP primary endpoint.

The official WSGZP curation exporter was additionally inspected at pinned
commit `8721fc04328c00b131659915dfbfa569bd342b54`. It calls an external
`itcfpy.load_scoreg`, crops the returned epoch object and saves the arrays,
while writing filtering/reference/baseline metadata. The supplement now gives
publication-level steps, but neither it nor the exporter ties every operation
and fitting scope to the exact released arrays or discloses all parameters for
stimulation-artifact correction. Preprocessing may have used all retained
trials before the proposed row split. The 50–300 ms interval remains a fixed
candidate response window, and A/B/C is not an end-to-end untouched
preprocessing holdout. If analysis proceeds on the distributed derivative,
describe the target as the
**released processed scalp response**, report artifact and preprocessing
sensitivity controls, and avoid claiming independently verified post-artifact
source recovery. See
`WSGZP_PREPROCESSING_PROVENANCE_20261028.md`.
