# Adversarial amendment: separate compatibility from follow-up prioritization

**Date:** 29 October 2026\
**Status:** Design correction only; protocol remains unlocked and signal access remains unauthorized.\
**Applies to:** `NOVELTY_TARGET_SELECTION_20261029.md` and future COG protocol drafts.

## Why this amendment is needed

The proposed fixed-area contact-capture test bundles two different outputs:
whether the scalp field permits materially different source explanations, and
whether a region chosen from those explanations is useful for planning a
follow-up measurement. Sparse SEEG-positive contacts can inform the second
question, but cannot establish whole-cortex truth or whether a `UNIQUE_ENOUGH`,
`AMBIGUOUS`, or `UNSUPPORTED` label is biologically correct. The earlier
selection note also proposed a minimum-over-compatible-explanations parcel
score. That score is zero for any parcel avoided by one admissible explanation;
it is not yet shown to yield a usable ranking. Withdraw it as the primary
ranking rule unless a pre-outcome analysis proves it nondegenerate on eligible
cases under the already declared families, or a separately justified
replacement is frozen before any outcomes are examined.

This is an adversarial design correction, not evidence that the proposed
analysis succeeds.

## Two outputs, two validation questions

### A. Conditional compatibility audit

For a measured scalp response `y`, a frozen source-family set, forward model,
uncertainty set, covariance and tolerance define a feasible set `K(y)`. Report
whether it is empty, the declared spatial-functional range, materially distinct
feasible witnesses, numerical gaps, and sensitivity to each declared family
and forward uncertainty.

Direct constrained optimization of this exact same set and functional is the
answer-equivalence oracle. Matching its results checks implementation; it is
not evidence that one method is more useful. This audit does not validate the
source family as physiology and does not infer a unique true generator.

### B. Follow-up prioritization

If a separate rule turns the audit into a region for subsequent sampling, call
that output a **prioritization map**, not the complete compatible source set.
Its evaluation may use the fraction of eligible, sampled SEEG-responsive
contacts inside a predeclared cortical area budget. This is positive-contact
capture on sampled locations only. It is not source sensitivity, specificity,
whole-cortex coverage, or a truth label for ambiguity.

Keep every eligible held-out participant-condition in the denominator.
Abstentions must be counted as zero captured positives and also reported as a
separate rate. Compare methods at the same area and abstention budgets. Report
participant-macro paired differences and participant-level uncertainty; events,
contacts and runs are not independent participants.

## Required adversarial controls before any outcome analysis

1. Use nested participant-grouped selection. Do not tune the area budget,
   family constraints, tolerance, abstention rule or comparator settings on
   held-out responses or SEEG labels.
2. Use condition-level averages unless the dataset supplies verified shared
   event identifiers and acquisition correspondence. Matching exported
   condition labels alone does not establish independent repeat runs or
   trial-paired EEG/SEEG.
3. Match all methods on the usable scalp inputs, reference, forward model,
   uncertainty, eligible cortical area, abstention allowance and tuning budget.
   Include direct constrained fitting as the equivalence oracle; compare the
   prioritization decision against GBF, established inverse/patch/resolution
   methods and simple map ensembles where a fair implementation is possible.
4. Examine sensitivity to implant coverage, shaft, region, depth, stimulation
   distance and geometry. Use spatial nulls and condition/pre-stimulus controls
   that preserve the relevant sampling structure.
5. Predeclare the minimum practically meaningful participant-level gain and
   its uncertainty procedure. The rule passes an empirical utility test only
   if the held-out gain exceeds that margin and survives the listed controls.
   A different map or a lower residual alone is not a pass.

Even a positive result would support only improved prioritization of sampled
responsive contacts on the processed cohort. It would not establish complete
source recovery, biological uniqueness, clinical benefit, or an algorithmic
novelty claim. A method-novelty claim separately needs a distinct guarantee or
replayable computational advantage over direct fitting of the identical
mathematical object.

## Current decision and blockers

Do not access or fit WSGZP EEG/SEEG samples under this candidate yet. The
participant-specific scalp-to-MRI provenance and reviewed overlays remain
unresolved; released-derivative preprocessing and scale semantics are not
fully reproducible; candidate repeated-run independence is unverified; the
minimum-area score can degenerate; and no numerical protocol or independent
pre-signal approval is locked. These are validity conditions, not parameters
to infer after looking at outcomes.

If those conditions cannot be resolved, retain the bounded GBF and
source-family software contribution. The measured Localize-MI artifact and
ds004752 scalp-to-iEEG prediction benchmark remain separate evidence classes;
neither should be relabelled as validation of endogenous spatial source
recovery. WSGZP has already been analyzed by GBF and XDL-ESI, so it is not an
independent cohort for those broad claims. A new analysis on this release would
need to beat the exact closest baselines on a prespecified decision, not merely
reproduce a different map or extend the dataset's existing source-extent
results.

## Evidence informing this correction

- `NOVELTY_TARGET_SELECTION_20261029.md` (candidate score and its explicit
  degeneracy check).
- `COG_PRE_SIGNAL_REVIEW_20261028.md` and
  `COG_PROTOCOL_AMENDMENT_20261028_v4.md` (signal-access and design gates).
- `WSGZP_PREPROCESSING_PROVENANCE_20261028.md` and
  `WSGZP_REPEAT_RUN_FEASIBILITY_20261028.md` (inherited preprocessing and
  unverified acquisition semantics).
- `DISCOVERY_OUTCOME_REPORT_20261029.md` (current scientific claim boundary).
- `B4_DEVELOPMENT_AUDIT_20261024.md` and
  `B5_B6_ROUTE_CLOSEOUT_20261024.md` (artifact endpoint and prior pivot).
