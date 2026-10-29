# Prior-art code audit: Phee et al. conformal EEG source imaging

**Audit date:** 2026-10-28\
**Purpose:** determine how closely the released MRI-informed conformal source
localizer overlaps Observable Geometry's proposed calibrated ambiguity report.\
**Scope:** read-only inspection of the official public repository at commit
`ded88a361ad349cb5e93a07171a11772f791a0e5`. No project data or EEG/SEEG
samples were accessed.

## Files inspected

| File | SHA-256 |
|---|---|
| `main.py` | `1b1250e83a6782b279f038358c9aefe371c8ba86fc21ababd1624174cba16705` |
| `deeplearning_code_files/datautils.py` | `3653c192d82e949a2df1157e0004edc1397e5cc8f4fd6abddfc3486103e054ec` |

Official source: [Phee et al. EEG source-localization repository](https://github.com/pheeeeee/eeg_source_localization).
The paper is [Phee et al. (2026), DOI 10.1016/j.cmpb.2026.109637](https://doi.org/10.1016/j.cmpb.2026.109637).

## What the implementation does

In `main.py`, the configured output is `center_ras` and the source task is
`singledipole` (lines 97, 101–117). The model predicts a single source center
from EEG, MRI, or their fusion, depending on the selected task. The code first
fits and evaluates the model, then estimates a scalar 95% prediction-loss
threshold from a separate conformal dataset.

The data loader uses indices 0–1999 for the main dataset and, when
`conformal=True`, offsets the indices to 2000–2199 (`datautils.py` line 137).
`main.py` constructs 200 conformal observations per MRI for both the training
MRI IDs and the held-out MRI IDs (lines 319–355). With the default IDs, 10
MRI IDs are used for model fitting and 3 are held out. The 200 calibration
scores from each of those 3 held-out MRI IDs are pooled into one quantile;
the calibration set is therefore a **target-cohort-specific pooled
calibration distribution**, not a separate coverage guarantee for each MRI.
The same held-out MRI IDs supply test examples, using the disjoint indexed
files 0–1999. This is not zero-shot calibration on a new anatomy without
calibration data for that target cohort. The code establishes different file
indices; the inspected lines alone do not establish independent random seeds
or independence of the underlying generated source configurations.

The conformal score is the model's scalar `LOSSFT` value for the predicted
single-dipole center (`main.py` lines 361–404). The code computes an empirical
upper quantile and prints it as a “Radius of 95% CI”; the inspected repository
does not itself turn that threshold into a spatial set or export per-example
prediction regions. It does not construct a union of feasible distributed
source families, a spatial identified set across source parameterizations,
or a certificate robust over a continuous participant-specific forward-model
uncertainty set. The implementation's calibration validity still depends on
exchangeability of calibration and target examples and on details of the
underlying simulated-data generation; those assumptions require review of
the generator and full paper. The primary train/validation/test split is
created with `random_split` without an explicit generator in the inspected
code (lines 138–162), so that split is not reproducibly fixed by this script.

## Equation/estimand comparison

Phee et al.'s reported object is a calibrated error region around a **point
localization** under a selected single-dipole task and a trained
MRI/EEG-informed predictor. Observable Geometry proposes a **set of spatial
explanations** spanning different prespecified source families and forward
models that meet a measured-response compatibility threshold. These are
related uncertainty outputs, but they answer different questions:

* Phee: how far can the predicted single source center be from its target
  under the calibration distribution?
* Observable Geometry: which distinct source fields/families remain able to
  explain a measured scalp response under the declared model and uncertainty
  set?

Therefore, “calibration for EEG source localization is new” is falsified.
The family-wise feasible-set construction is not established as new either;
it must still be compared to direct constrained fitting, resolution/fidelity
methods, robust inverse methods, and union-of-convex-set functional recovery.
Phee is a close comparator for prediction-set calibration, but not evidence
that the proposed source-family object is novel or useful.

## Required consequences for our novelty test

1. If Observable Geometry reports a calibrated location/ambiguity region,
   compare its coverage, size, and selective risk against a matched
   calibration baseline. Give every method the same participant-specific
   calibration information and keep calibration participants/examples
   separate from evaluation.
2. Report whether calibration is based on measured examples or on
   forward-generated examples. Do not describe simulated calibration as
   measured-neural validation.
3. Do not call another prediction interval “source-family observability”
   unless it explicitly ranges over the declared source families and
   participant-specific forward uncertainty.
4. Do not claim a false-source-attribution reduction without an independent
   source reference. WSGZP late CCEP and sparse responsive SEEG contacts do
   not provide complete source truth.
5. A new method still requires a mathematical step or guarantee absent from
   the closest methods **and** a held-out measured-data decision benefit.
   If direct constrained fitting plus matched calibration yields the same
   decisions, novelty is not supported.

## Conclusion

This code audit narrows, but does not remove, the prior-art overlap. The
nearest comparison is a **subject-specific conformal point-localization
region** trained/calibrated from simulated EEG, including a separate
calibration subset for MRI IDs held out from model fitting. Our possible
distinction is the across-family, forward-uncertainty-aware feasible set and
its decision output. That distinction is only a candidate: its exact
mathematical novelty, validity, and measured-data decision value remain
unproven.
