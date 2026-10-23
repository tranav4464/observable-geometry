# Historical independent technical review packet: NeuroFlowNet/WBEN B2

> **Superseded on 23 October 2026.** This packet reviews the withdrawn scalp-EEG-to-iEEG route and must not be used to assess the active GBFs project. The active packet is [`B2_GBF_INDEPENDENT_REVIEW_PACKET.md`](B2_GBF_INDEPENDENT_REVIEW_PACKET.md); the active specification is [`B2_GBF_SPEC.md`](B2_GBF_SPEC.md).

**Review status: same-chat AI PEER REVIEW COMPLETED, HOLD FOR CHANGES; unaffiliated external review remains outstanding.** The [review report](../../outputs/track_b/20261023T_b2_peer_review/REVIEW.md) identified six revision groups. The active specification has since incorporated the core technical revisions for R1–R5, and the prior-art matrix and policy have been reconciled for R6. The original report remains a review of the earlier packet state, not external sign-off or a re-review of the updated specification. B2 remains IN_PROGRESS.

## What the project proposes

The build is a clean-room, source-informed implementation of NeuroFlowNet's conditional normalizing flow. It uses eight fixed scalp channels to predict a conditional distribution over simultaneously recorded iEEG contact waveforms from a verbal working-memory task. The primary challenge holds out one entire set size (4, 6, or 8) within each participant, trains on the other two, and tests whether waveform predictions and raw predictive intervals transfer to the unseen load.

The project does not claim a new flow algorithm, exact reproduction of the paper, unique recovery of latent brain activity, or first-in-field task novelty. The value proposition is a leakage-controlled measured-contact challenge that separates prediction quality and uncertainty from claims of anatomical or neural-source recovery.

## Materials to inspect

1. [`B2_NEUROFLOWNET_SPEC.md`](B2_NEUROFLOWNET_SPEC.md): estimand, data boundaries, preprocessing, fixed models, metrics, and failure rules.
2. [`B2_PRE_REVIEW_AUDIT.md`](B2_PRE_REVIEW_AUDIT.md): author-side status check against all six registered exit criteria; explicitly not an independent review.
3. [`outputs/track_b/20261023T_b2_metric_seed_consistency_audit/SESSION.md`](../../outputs/track_b/20261023T_b2_metric_seed_consistency_audit/SESSION.md): seed derivation, window aggregation, and stochastic-replicate metric aggregation checks.
4. [`B2_PAPER_FIDELITY_MATRIX.md`](B2_PAPER_FIDELITY_MATRIX.md): paper/source equations, discrepancies, and adaptation boundary.
5. [`METHOD_MATRIX.md`](METHOD_MATRIX.md): prior-art distinctions and unresolved overlaps.
6. [`B1_CLOSEOUT.md`](B1_CLOSEOUT.md): real-data feasibility and limits.
7. [`outputs/track_b/20261023T_b2_preprocessing_contract_audit_v2/resampling_audit.json`](../../outputs/track_b/20261023T_b2_preprocessing_contract_audit_v2/resampling_audit.json): corrected SciPy 1.18.1 filter characterization and real-development check.
8. [`outputs/track_b/20261023T_b2_access_exposure_review/SESSION.md`](../../outputs/track_b/20261023T_b2_access_exposure_review/SESSION.md): documented outcome-access boundary and its limitations.
9. [`outputs/track_b/20261023T_b2_protocol_specification_closeout/SESSION.md`](../../outputs/track_b/20261023T_b2_protocol_specification_closeout/SESSION.md): changes made while preparing the review packet.
10. [`outputs/track_b/20261023T_b2_estimand_formalization/SESSION.md`](../../outputs/track_b/20261023T_b2_estimand_formalization/SESSION.md): formal estimand audit and the purely algebraic illustration; it contains no generated neural data or model results.
11. [`outputs/track_b/20261023T_b2_peer_review_remediation/SESSION.md`](../../outputs/track_b/20261023T_b2_peer_review_remediation/SESSION.md): reconciliation of the active specification and reviewer handoff records; documentation only.
12. [`outputs/track_b/20261023T_b2_peer_review_remediation/REVIEW_REASSESSMENT.md`](../../outputs/track_b/20261023T_b2_peer_review_remediation/REVIEW_REASSESSMENT.md): same-chat reassessment of the revised written protocol, not unaffiliated sign-off.
13. [`outputs/track_b/20261023T_b2_peer_review_remediation/reconciliation_checks.json`](../../outputs/track_b/20261023T_b2_peer_review_remediation/reconciliation_checks.json): current local-link, status, and document-hash checks; not scientific or external-review evidence.

## Questions for the reviewer

- Is the target precisely measured, and does the stated claim match the concurrent scalp/iEEG data and within-participant held-load split?
- Does the whole-load outer/inner split prevent trial/window leakage and use only training-load target statistics for prediction and scale restoration?
- Are the input/contact definitions, preprocessing adaptations, model configuration, comparator recipes, seeds, training/stop budgets, scores, uncertainty unit, and technical failure rules sufficiently reproducible?
- Are the participant-level risk contrast and marginal interval-coverage quantities mathematically coherent, and does the stated claim decision follow from them without implying source recovery or zero-shot transfer?
- Does the participant-weighted reliability summary preserve per-load/contact failures and use participant-level uncertainty without allowing participants with more channels or windows to dominate?
- Is the corrected affine inverse mathematically necessary and clearly distinguished from the paper's printed formula? Are other source-informed details honestly labeled as adaptations?
- Does the chosen comparison answer a useful scientific or engineering question, given direct scalp-to-iEEG prediction, prior NeuroFlowNet work, working-memory load research, and virtual-iEEG framing?
- Is any contribution or novelty language still too strong? What should be removed or narrowed?
- Are the documentary data-exposure limits and proposed confirmation boundary adequate, given there is no OS-level file-open audit?
- Should B2 pass, remain open pending specific changes, or fail/pivot? Please list the blocking issues and the smallest defensible remedy.

## Reviewer response template

- Recommendation: PASS / HOLD FOR CHANGES / FAIL OR PIVOT
- Blocking findings:
- Nonblocking improvements:
- Estimand and claim match:
- Leakage and data-access assessment:
- Model/math fidelity assessment:
- Prior-art/contribution assessment:
- Required revisions before B2 passes:

The reviewer should inspect only the records listed above and public primary sources. Confirmation event rows and signal samples for sub-04 through sub-15 must remain unopened until a separate B5 lock. No model fitting is authorized until B2 passes.

## Primary references

- He et al., [NeuroFlowNet v3](https://arxiv.org/html/2603.03354v3).
- Subramanian et al., [Scalp EEG predicts intracranial brain activity in humans](https://pmc.ncbi.nlm.nih.gov/articles/PMC12026988/).
- Pham and Tran, [CAST: cross-subject iEEG reconstruction from scalp recordings](https://arxiv.org/abs/2605.18897).
- Boring et al., [Cognitive load decoding across tasks](https://doi.org/10.1088/1741-2552/abb9bc).
- Dong et al., [EEG-iEEG representational enhancement](https://arxiv.org/abs/2604.14202).
- Yang and Liu, [WBEN: multimodal scalp and intracranial EEG network inference](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html).
- [TF-DiffEEG: High-Fidelity iEEG Reconstruction from Scalp EEG via Dual-Domain Diffusion](https://doi.org/10.1109/ISPCE-ASIA69076.2025.11312313). The publisher abstract establishes a direct reconstruction method; exact cohort, target, split, and held-load overlap remain unverified from the accessible record.
- [Virtual iEEG from Scalp EEG review](https://arxiv.org/abs/2608.26998).
- [NEMAR on004752 dataset](https://github.com/nemarDatasets/on004752).
- Phillips et al., [Characterizing the relationship of non-invasive and invasive neural recordings: An information-theoretic analysis of the scalp and stereo electroencephalography](https://doi.org/10.1109/IEEECONF67917.2025.11443669). The public publisher/author record reviewed so far exposes only the abstract; exact task-level overlap remains unresolved in the method matrix.
