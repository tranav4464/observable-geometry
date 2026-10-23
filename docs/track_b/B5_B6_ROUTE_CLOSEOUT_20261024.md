# B5/B6 route closeout

**Date:** 24 October 2026
**B5 protocol lock:** **PIVOT — not activated.**
**B6 held-out evaluation:** **PIVOT — not run.**

## Decision

B5 and B6 were designed for a confirmatory test of endogenous neural-source distinguishability. The B4 audit found that the available Localize-MI development endpoint is a stimulation pulse artifact, while the tested simple source generators leave structured residuals. The target and source family therefore do not support the proposed physiological inference. The six exposed stimulation sites are development observations, not a held-out neural-source test. No valid confirmatory endpoint or independent ground truth is available in the active route.

Because the target is not supported, a protocol lock would formalize an invalid test rather than repair it. B5 is pivoted without opening any reserved outcomes. B6 is consequently pivoted and no held-out evaluation, model fitting, or additional participant-outcome analysis was performed under this route. These statuses record a deliberate failure-route decision; they do not mean confirmatory validation succeeded.

## Reopening criteria

Do not reopen B5/B6 under the current pulse-artifact endpoint. A future route must first identify a real-data task with an endpoint appropriate to the scientific question, verify its forward model and independent reference, complete a task-level prior-art review, and obtain technical review of the estimand. Only then may a new protocol be locked before any reserved outcome is accessed.

## Evidence

- `docs/track_b/B4_DEVELOPMENT_AUDIT_20261024.md`
- `docs/track_b/B4_CHANNEL_MATCH_RECONCILIATION_20261024.md`
- `docs/track_b/GATE_REGISTER.json`
- B4 run and access-boundary evidence linked from the B4 audit.

## Alternate public-data screen

A metadata-only screen of public alternatives was completed after the original route decision. It found no untouched external cohort for the active GBF estimand. The HDEEG-IED-SurgOutcome release has individual geometry and surgical outcomes, but the GBF paper already analyzed 24 favourable-outcome cases from the same dataset; it remains a possible post-publication held-out-subset evaluation pending exact overlap checks, EBRAINS terms, and independent protocol review. The iES-CCEP data are also already used by GBF and have unresolved OSF license metadata; DRE-LZSH lacks released electrode coordinates and participant MRI. The screen used public metadata and article descriptions only, not signal samples, and does not authorize outcome access or reopen B4–B6. See `docs/track_b/B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md` for the updated criteria, source links, and candidate-specific limits.
