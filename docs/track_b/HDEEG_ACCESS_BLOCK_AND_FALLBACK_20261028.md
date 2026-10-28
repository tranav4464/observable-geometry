# HDEEG access block and measured-data fallback

**Decision date:** 28 October 2026  
**Status:** HDEEG route unavailable for this institution

The institution cannot obtain HDEEG-IED-SurgOutcome because the distributing
organization has not validated its institutional access. We therefore do not
use that dataset, do not bypass its access controls, and do not describe the
project as having surgical-outcome external validation.

## What remains available

1. **ds004752 full measured release:** 15 participants with simultaneous scalp
   EEG and intracranial EEG, available under CC0. It is now downloaded and
   integrity-audited at
   `observable_geometry/data/raw_20261028/ds004752_v1.0.0_full/`.
2. **Localize-MI controlled endpoint:** the existing measured pulse-artifact
   and participant-specific forward-model validation remains available for a
   known stimulation-site control. It is not endogenous source ground truth.
3. **Existing real-data transport benchmark:** the completed scalp-to-iEEG
   benchmark remains a measured transport result, not a source-localization
   proof.

## Claim boundary after the pivot

The fallback can test whether the certificate's ambiguity/abstention output is
stable on held-out measured scalp fields and whether it corresponds to measured
iEEG observability under the available sensor/contact geometry. It cannot test
resection-mask concordance, clinical outcome prediction, or full physiological
source recovery without an individual head model and an independent anatomical
reference.

The final report must state this limitation explicitly. If the fallback gives
no decision advantage over direct fitting and established resolution metrics,
the correct outcome is **VALIDATED SOFTWARE CONTRIBUTION**, not a novel-method
claim. HDEEG can be reopened later only through an authorized institutional
route.
