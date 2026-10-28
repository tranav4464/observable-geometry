# Calibrated Observable Geometry protocol v1

**Protocol status:** frozen design, pending metadata/access audit
**Protocol ID:** COG-2026-10-28-v1
**Primary estimand:** whether a measured scalp field supports a unique source-family attribution under a participant-specific forward model and bounded model uncertainty.

## 1. Data boundary

The primary analysis uses measured recordings from the iES-CCEP/WSGZP dataset:
simultaneous high-density scalp EEG and SEEG, individual MRI, registered scalp
electrodes, intracranial contacts and stimulation triggers. The independent
spatial reference is the stimulated contact pair and the physiological CCEP
response recorded after the direct pulse artifact.

The external test uses HDEEG-IED-SurgOutcome: measured high-density EEG,
individual MRI and surgical-outcome/resection references for endogenous
interictal discharges.

No neural signals will be injected, simulated, denoised from a generated
template, or created by forward projection for the primary analysis. Forward
projection is used only to fit candidate explanations to measured fields.
Algebraic/synthetic cases are a separate unit-test evidence class and cannot
enter calibration, primary metrics or the novelty decision.

## 2. Inclusion and exclusion

Include only participants with all of the following:

* measured scalp EEG and the relevant reference modality;
* participant MRI and registered scalp-electrode coordinates;
* intracranial contact coordinates or surgical reference masks;
* a reproducible channel/reference/filter contract;
* a complete event marker and enough trials for participant-level holdout;
* permitted data-use terms for the planned analysis.

Exclude a participant before outcomes are read if any geometry, timing,
reference, event, or licensing contract cannot be independently reproduced.
Exclude saturated, nonfinite, duplicated or ambiguous events using rules fixed
before the held-out data are accessed.

## 3. Preprocessing contract

Use the dataset's released signal values and metadata. Do not tune filters,
references or windows using source-localization outcomes.

* Reconcile channel order and units before any source computation.
* Apply the documented average/reference projection to measured scalp data and
  the forward model identically.
* Estimate covariance only from a pre-event interval or training data; never
  from the held-out response window.
* For iES-CCEP, exclude the direct stimulation interval `[0, 20] ms` and use
  the post-artifact physiological response window `[20, 500] ms` as the primary
  response. If the frozen metadata audit shows that these windows are not
  represented, the protocol fails rather than being retuned after outcomes.
* For HDEEG interictal events, use the released event alignment and the fixed
  window `[-50, 50] ms` around the annotated discharge peak.

## 4. Source families

All families use participant-specific source coordinates and fixed orientation
from the audited forward model unless a comparator explicitly supports free
orientation. A profiled scalar handles overall amplitude; family scores are
not compared by arbitrary raw coefficient scale.

1. Point: one source vertex.
2. Uniform patch: area-weighted, one-sign connected geodesic patch with radii
   10 mm and 20 mm.
3. Smooth patch: area-weighted Gaussian weights with geodesic widths 5, 10 and
   20 mm, one sign.
4. Signed distributed: constrained L1 fit over a declared support, allowing
   coefficient signs but preserving the support and budget contract.
5. Multi-patch: up to two disjoint connected patches, one profiled coefficient
   per patch; global convexification is forbidden because it erases the
   disjunction being tested.
6. Flexible direct fit: unrestricted constrained fit, reported as a baseline
   and never presented as a new method.

## 5. Forward-model uncertainty set

The primary stress set is fixed before held-out outcomes:

* skull conductivity values: 0.006, 0.009 and 0.012 S/m;
* sensor-location perturbation: up to 3 mm along the audited scalp surface;
* fixed-orientation perturbation: a 15-degree cone around the audited
  orientation;
* covariance shrinkage: 5%, 10% and 20%.

These are declared engineering stress values, not estimates of the true tissue
parameters. Report the nominal result and the worst/best result over the set.

## 6. Certificate output

For each measured event and family `F`, compute the profiled whitened residual

`r_F(y) = min_{theta in U, x in F} || Sigma^(-1/2)(y - G_theta x) ||_2`.

The certificate reports residuals, the best family, the residual gap, the set
of families within the calibrated tolerance, their shared spatial support and
one decision:

* **UNIQUE_ENOUGH**: one family/reference survives and its calibrated risk is
  below the target;
* **AMBIGUOUS**: multiple materially different families survive;
* **UNSUPPORTED**: no declared family fits within the calibrated tolerance.

## 7. Calibration and held-out split

All calibration is participant-level. The primary route uses leave-one-
participant-out or a prespecified 70/15/15 participant split when the dataset
contains enough eligible participants. No trial from a held-out participant,
stimulation site or session may enter threshold fitting, hyperparameter
selection or family definition.

The calibration target is a 90% empirical coverage requirement for the spatial
reference set, with an 80% coverage operating point used for the primary
selective-risk comparison. These are decision targets, not claims of a
distribution-free theorem under non-exchangeable clinical data.

Primary metrics:

* selective localization error at 80% coverage;
* false-unique rate among accepted UNIQUE_ENOUGH events;
* coverage of the reference-supported family set;
* ambiguity rate and unsupported rate;
* participant-bootstrap confidence intervals.

Secondary metrics include residual calibration curves, source-family stability
under the uncertainty set, and the risk-coverage curve.

## 8. Baselines and novelty test

Use identical participant splits and measured fields for:

* direct constrained fitting;
* GBF-only reconstruction;
* MNE, dSPM, eLORETA and LCMV where the data contract permits;
* PSF/CTF or empirical resolution metrics;
* established uniform/smooth patch methods;
* the calibrated certificate.

The single predeclared researcher decision is: **report a unique source,
report an ambiguity set, or abstain**. Novelty is supported only if the
certificate changes this held-out decision correctly, or provides materially
better calibrated selective risk/coverage than every baseline. Different
residual values without a decision or calibration advantage do not support a
novel-method claim.

## 9. Failure and stopping rules

Stop and classify the route as PROMISING BUT UNVERIFIED if the required
individual geometry or independent reference cannot be established. Classify
as VALIDATED SOFTWARE CONTRIBUTION if direct fitting or standard resolution
methods give equivalent decisions. Classify as PIVOT if measured data fail the
endpoint or no defensible decision remains. Never change the primary window,
family definitions, uncertainty set, split or metric after held-out outcomes
are inspected.

## 10. Required evidence

The run must save data-version hashes, metadata hashes, preprocessing settings,
forward-model hashes, participant assignments, access logs, per-event outputs,
calibration fits, baseline outputs, independent replay results and a claim
ledger. The final report must distinguish measured evidence, model hypotheses,
unit tests and unresolved limitations.
