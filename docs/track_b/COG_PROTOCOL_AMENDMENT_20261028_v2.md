# COG protocol amendment v2: separate certificate construction from evaluation

**Status:** proposed; not locked; EEG/iEEG sample gate remains closed\
**Supersedes:** the split/evaluation provisions in
`COG_PROTOCOL_AMENDMENT_20261028.md` only\
**Reason:** an internal design audit identified that using the same repetition
half both to filter explanations and to report their prediction success would
make the validation result selected on its evaluation data.

## Required separation

Keep the participant-level leave-one-participant-out outer split. Within each
held-out participant/run, divide retained EEG repetitions deterministically
into at least two disjoint halves before any signal-dependent fitting.

### Half A: construct the candidate certificate

* Fit every prespecified source family to A using only the locked
  participant-specific forward model, covariance contract, family definition
  and uncertainty scenarios.
* Construct the candidate explanation set and compute the proposed spatial
  functional from A only.
* Apply only tolerances and decision thresholds estimated from the outer
  training participants. Freeze the set and the output before reading B's
  signal values.
* The output may be an ambiguity/support report. It must not be described as
  a true-source confidence or whole-cortex truth label.

### Half B: evaluate the frozen predictions

* B is opened only after candidate supports, the ambiguity score, output
  decision and all comparator predictions have been serialized and hashed.
* B evaluates predictive error/calibration for the frozen A-derived
  explanations and matched baselines. It cannot remove explanations, alter
  the reported A-derived ambiguity decision, tune a threshold or change a
  hyperparameter.
* A failure on B is recorded as a failure of the frozen candidate set's
  repeatability/prediction. It is not retroactively used to rewrite the
  certificate and then scored on that same B observation.

If the intended decision definition requires B to accept/reject explanations,
then A/B are development data, not an independent test. Reserve a third
repetition half C (or an independently held-out same-condition run) for final
evaluation. If the retained repetitions cannot support three meaningful
parts, narrow the claim to a two-part repeatability analysis and do not present
the same B-derived decision as independently validated.

Reversing A and B is a useful prespecified cross-fit sensitivity analysis,
but the two directions share a participant and are not independent
replications. Summarize uncertainty at the participant level; do not count
the two directions as separate independent samples.

## Frozen data-processing boundaries

The outer held-out participant remains excluded from calibration, model
selection, source-family budget selection and decision-threshold estimation.
The fit/validation repetition split must be deterministic from metadata and
must not use EEG/iEEG values. No EEG/SEEG rows may be paired by array index:
the released epoch counts differ and the tables contain no shared trial IDs.
If the signal question requires trial-paired multimodal outcomes, it needs
original trigger/rejection logs or a different dataset.

The existing proposal to calibrate response-repeatability tolerances on
training participants can remain, but it must state exactly which data
estimate each parameter and how repetition averaging changes the noise
covariance. The held-out B data cannot calibrate the threshold used to certify
the corresponding A candidate set.

## Metrics and interpretation

Report (1) the A-derived certificate and spatial functional, (2) the
predeclared prediction metric for frozen outputs on B, (3) participant-macro
coverage/error and participant-bootstrap intervals, and (4) matched baseline
results on the same splits. The primary result is repeatability-calibrated
prediction/ambiguity under the tested model family; it does not establish
physiological source correctness. SEEG contacts remain sparse positive
corroboration. The stimulation contact remains an intervention, not a complete
source label for the later distributed response.

Before signal access, the final protocol must still freeze the spatial
functional and its operational threshold, exact source-family coefficients
and supports, the forward-model stress design, covariance construction,
baseline implementations, model-selection rules and the single researcher
decision being evaluated. The two-part split resolves one leakage/selection
concern but does not resolve those other open protocol choices or clear the
geometry/forward-model gate.
