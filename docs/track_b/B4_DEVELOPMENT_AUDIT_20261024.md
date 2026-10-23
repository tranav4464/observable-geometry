# B4 development audit and route decision

**Date:** 24 October 2026
**Gate:** B4 — development and adversarial validation
**Decision:** **PIVOT** the empirical-validation branch; retain the bounded GBFs reproduction and inspectable software build.
**Scope:** Localize-MI sub-01, previously exposed development data only. This is not held-out validation.

## Decision

The permitted sub-01 rerun is reproducible and provides a matched, descriptive comparison of two inverse methods on the measured stimulation-pulse artifact. It does not validate the B2/B3 nominal distinguishability output as a predictor of neural source recovery. The physical endpoint is an electrical stimulation artifact, while the B2 source family consists of fixed-orientation cortical sources. Existing development audits also show that a simple point-source cortical generator leaves a large, reproducible residual. The route therefore cannot support a claim about endogenous neural-source identifiability or a new source-localization method.

The B4 falsification condition is met for the broader empirical claim: the real endpoint does not support the proposed neural interpretation, and the current evidence does not show that the distinguishability output changes a source-reporting decision beyond standard diagnostics. Retain B0–B3 as a bounded implementation/reproduction contribution. Do not begin B5/B6 held-out model evaluation under this source-localization estimand. A separate, defensible endpoint and protocol would require a new gate decision and independent review.

## What was checked

The fresh run `outputs/20261023T192900Z_b4_matched_224_reproduction` reran the existing Track A empirical script on sub-01 only. It used the 224 channels shared across the selected sub-01 runs, a common-average reference, a pooled baseline covariance with 10% shrinkage, fixed cortical-normal forward orientations, and the fixed −2 to +2 ms pulse-artifact window. No sub-02–07 signal outcomes were opened. No synthetic signals or datasets were used.

The 15-row `predicted_observed_similarity.csv` is byte-for-byte identical to the sealed Track A CSV (SHA-256 `d3808dfb22318df1fc8fab6a06c4e20c8a059622dca93465029da2619396f50b`). The report contains six already-exposed stimulation sites and 15 dependent pairs. Predicted lead-field similarity and observed artifact-topography similarity have Pearson `r = 0.3452` and Spearman `rho = 0.3429`. These are descriptive associations only: all pairs reuse the same six sites, there is one participant, and the observed patterns are stimulation artifacts.

In the same 224-channel run, GBFs and fixed-orientation MNE peak-localization errors were calculated against the stimulation-contact midpoint. Median errors were 19.76 mm for GBFs and 28.30 mm for MNE. These numbers are a same-case, model-conditional artifact comparison, not a population estimate or evidence that GBFs is superior. The contact midpoint is an approximate reference, and the fixed cortical-normal orientation is not established as the artifact-current orientation.

## Adversarial findings and limits

1. **Endpoint mismatch:** Localize-MI measures scalp potentials during intracranial electrical stimulation. The short pulse artifact is not an endogenous neural response. Matching an artifact topography to a cortical lead field cannot establish physiological source recovery.
2. **Source-generator inadequacy:** The B1 development audit reports median held-out whitened R² of 0.162–0.173 for the fixed cortical-normal dipole. Even a fitted free-orientation dipole reaches only 0.615–0.651, and the layered source-sink model retains a median train/test residual cosine of 0.999. The residual is systematic. These checks do not identify its cause, but they reject treating the present simple generator as validated artifact physics.
3. **Different quantities:** The B2 score measures nominal similarity between two forward signatures. The MNE comparator in this rerun reports inverse peak distance to a stimulation-contact midpoint. Those quantities answer different questions. The matched peak-distance comparison is valid for the narrow artifact task; it is not a matched test of the B2 score against an MNE resolution-matrix or PSF/CTF measure.
4. **Channel-contract discrepancy:** The sealed B2/B3 model-only artifacts use 236 channels; the empirical artifact analysis uses the common 224-channel set. The fresh Track A script recomputed its own predicted pair scores under the 224-channel contract, but the earlier B4 association table joined 236-channel B2/B3 scores and MNE PSF summaries to 224-channel empirical errors. That earlier join is invalid and is retained only as a failed exploratory artifact. See `B4_CHANNEL_MATCH_RECONCILIATION_20261024.md`.
5. **No independent sample:** The six sites and all sub-01 runs were already exposed in Track A. The pair count is not an independent sample size. No p-values, confidence intervals, calibration claims, or generalization claims are justified.
6. **Protocol-record correction:** The B4 session note said “20 ms” for the artifact window. The executed code and report use −2 to +2 ms, a 4 ms interval. This is logged as a documentation error and corrected here; the rerun remains a development-only reproduction, not a preregistered confirmatory analysis.
7. **No demonstrated decision value or novelty:** The run does not establish a researcher decision that changes beyond established resolution/separability diagnostics. Pairwise lead-field similarity, resolution metrics, and forward-model uncertainty have substantial prior art. No novel-method claim survives this evidence.

## Result table

| Check | Result | Interpretation |
|---|---|---|
| Reproduced six-site pairwise CSV | Exact byte parity; 15 pairs | Reproducible under the existing 224-channel Track A script |
| Predicted vs observed similarity | Pearson `r = 0.3452`; Spearman `rho = 0.3429` | Weak-to-moderate descriptive association; dependent pairs, one participant, artifact endpoint |
| GBFs peak distance | Median 19.76 mm; mean 19.96 mm | Artifact-specific, model-conditional estimate |
| MNE peak distance | Median 28.30 mm; mean 27.16 mm | Same 224-channel artifact task; not a direct comparator for B2 similarity |
| Endogenous neural source validity | Not tested | No inference permitted |
| New method / decision benefit | Not demonstrated | Do not claim novelty or utility |
| B4 disposition | PIVOT | Narrow project to verified reproduction and inspectable software; no held-out source-localization run |

## Gate and next-step consequence

B4 is recorded as **PIVOT**, following its specified failure route: narrow the claim and preserve the failed empirical-validation branch. B5 and B6 remain **NOT_STARTED**. Their participant-held-out design is not activated because there is no currently supported source-physiology endpoint for this GBFs task. Any future proposal to use another endpoint must first undergo prior-art review, data/ground-truth feasibility audit, a frozen protocol, and independent review before outcome access.

The project can still be completed as a high-quality software build: reproduce the pinned GBFs behavior, make its inputs and assumptions inspectable, expose the nominal source-signature diagnostic with appropriate limits, ship a reproducible one-command demonstration, and obtain an external software/scientific review. This is a valuable engineering contribution, but the present evidence does not justify calling it a scientific discovery or a novel mathematical framework.

## Evidence

- Fresh rerun: `outputs/20261023T192900Z_b4_matched_224_reproduction/empirical_evaluation_report.json`
- Fresh pair table: `outputs/20261023T192900Z_b4_matched_224_reproduction/predicted_observed_similarity.csv`
- Session record: `outputs/20261023T192900Z_b4_matched_224_reproduction/SESSION.md`
- Earlier invalid channel join and its manifest: `outputs/track_b/20261023T192200Z_b4_dev_protocol_feasibility/b4_site_associations.csv` and `b4_site_associations_manifest.json`
- Original failed attempt, preserved: `outputs/track_b/20261023T192200Z_b4_dev_protocol_feasibility/b4_audit_failure_01.json`
- Source-generator adequacy failures: `docs/track_b/B1_BEM_DEVELOPMENT.md`
- Prior-art boundary: `docs/track_b/B0_GBF_EXTENSION_SCREEN.md`
