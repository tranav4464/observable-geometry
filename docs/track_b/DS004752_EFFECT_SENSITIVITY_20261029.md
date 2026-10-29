# ds004752 participant-effect sensitivity audit

**Status:** post-hoc, exploratory arithmetic and sensitivity audit. This is not a new confirmatory analysis.

## Question and input

The existing `ds004752` benchmark compared scalp-feature models for predicting intracranial contact-pair signals. Its saved primary participant-level effect is defined as global-baseline NMAE minus cross-spectrum-model NMAE, so positive values favor the cross-spectrum model. The original summary reports 12 participants, a mean effect of 0.022214 normalized-MAE units, and a participant-bootstrap 95% interval of [-0.002948, 0.049584].

This audit reads only the derived `primary_effects.csv` and `summary.json` under the sibling `experiment_v2/real_results` directory. It does not open EEG/iEEG recordings, features, or trial predictions. The CSV and summary hashes are recorded in the machine-readable report. The analysis script is `scripts/track_b/audit_ds004752_participant_effects.py`.

## Sensitivity summaries

Nine of 12 participant effects are positive and three are negative. The exact two-sided sign-flip test for the mean gives p=0.1426; the exact two-sided sign test gives p=0.1460. The leave-one-participant-out mean remains positive, ranging from 0.013144 to 0.030961 normalized-MAE units.

These findings do not provide persuasive participant-level evidence for a reliable advantage: both post-hoc p-values are above conventional thresholds, the bootstrap interval crosses zero, and the mean is sensitive in magnitude to individual participants. The sign-flip calculation assumes sign exchangeability under its null; the sign test ignores effect magnitudes. Neither analysis corrects for all modeling choices or turns the exploratory benchmark into a confirmatory study.

## Independent arithmetic replay

`scripts/track_b/verify_ds004752_effect_sensitivity.py` independently enumerates all 4,096 sign assignments and recomputes the exact sign test and leave-one-out summaries from the derived participant-effect CSV. It also checks the hashes and key aggregate invariants of both source artifacts. A fresh hardened replay is saved as `outputs/track_b/20261029T_ds004752_effect_sensitivity_002/independent_check_003.json` and reports PASS. This verifies the summary arithmetic and input provenance, not the original predictive model, benchmark pipeline, or physiological interpretation.

## Claim boundary

The benchmark predicts an intracranial contact-pair signal from scalp features. It is not a test of GBF source-map recovery, neural generator localization, or a novel source-imaging method. The sensitivity audit does not strengthen those claims and does not change the exploratory status of the benchmark. Its value is to make the uncertainty around the saved participant-level effect more visible and auditable.

## Reproducibility artifacts

- Analysis: `scripts/track_b/audit_ds004752_participant_effects.py`
- Independent replay: `scripts/track_b/verify_ds004752_effect_sensitivity.py`
- Machine-readable result: `outputs/track_b/20261029T_ds004752_effect_sensitivity_002/sensitivity.json`
- Short result: `outputs/track_b/20261029T_ds004752_effect_sensitivity_002/SENSITIVITY.md`
- Independent replay result: `outputs/track_b/20261029T_ds004752_effect_sensitivity_002/independent_check_001.json`
