# B0 closeout: select and bound the build target

> **Historical closeout superseded on 2026-10-23.** B0 is currently `IN_PROGRESS`, not passed. The earlier WBEN selection was paired with a separate contact-waveform task, which has a different output and estimand. That two-part proposal is withdrawn as the primary build. See the current state in `BUILD_BASE_DECISION.md` and the B0 decision log. The audits below remain valid historical evidence, but they do not justify the current route.

## Decision

Proceed with an independent implementation of Yang and Liu's WBEN model as the **existing software baseline**, followed by a real-data challenge on the paired on004752 recordings. Do not call WBEN our method and do not claim a new estimator at this stage. Track B's active experiments use real recordings only. Historical synthetic files in the workspace are excluded from current work and evidence.

This decision selects a practical build target; it does not establish that WBEN can be reproduced exactly, that its network estimates are anatomically true, or that a novel extension exists. The proposed contribution remains open until B2 completes an exact prior-art comparison and defines a measurable real-data decision.

## Evidence reviewed

- Yang and Liu's [official NeurIPS 2025 paper](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html), [full PDF](https://papers.nips.cc/paper_files/paper/2025/file/82a6afb1f666daaeec8da4d775452bc7-Paper-Conference.pdf), and [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13345474/) describe the model, equations, inference, real-data cohort, and limitations.
- The paper's checklist did not provide a public code link at submission, and the audit did not find a verifiable official implementation. Implement independently from the paper unless a fresh search verifies subsequent author code.
- The equation audit records consequential ambiguities: the L1 sparsity penalty has conflicting signs across the paper, the `Acc` label does not match its printed precision equation, and coverage descriptions conflict between prose and table. The paper also acknowledges ghost-edge risk. Preserve these choices explicitly; do not silently select whichever interpretation scores best.
- Partial-observation graph recovery and observation-error amplification are established topics. Machado et al. (AAAI 2023) study graph recovery from partial node observations; Berry and Sauer (SIAM JADS 2025) quantify reconstruction error amplification. Their targets are not automatically like-for-like WBEN baselines, but they rule out generic partial-observation recovery or stability as novelty claims.
- B2's direct-prior screen now includes scalp-to-iEEG spectral prediction, within-participant waveform generation, calibrated cross-participant waveform reconstruction, event localization plus waveform reconstruction, working-memory load analyses, CAST, and the virtual-iEEG review. A scalp-only Kalman inference mode has been derived algebraically for held-out-iEEG prediction, but is not implemented or empirically evaluated. The target map and task protocol remain unresolved. See `outputs/track_b/20261022T195500Z_b2_direct_prior_and_task_alignment_audit/SESSION.md` and `outputs/track_b/20261022T200010Z_b2_wben_scalp_only_inference_derivation/SESSION.md`.
- REA is a general software reverse-engineering toolkit, not an EEG model or neural dataset. GBFs is a source-imaging comparator and Track A infrastructure. Neither replaces WBEN as the selected Track B reproduction target.

## Exit review

| B0 criterion | Finding |
|---|---|
| Select an actual, relevant software target | WBEN is selected as an existing joint scalp EEG/iEEG model with published equations and a real paired dataset application. |
| Identify implementation status and ambiguities | No verifiable official implementation was found in the prior audit; paper-level ambiguities are documented and must remain explicit. Recheck for any later official release before implementation. |
| Compare neighboring methods | The method matrix covers partial-observation graph inference, observation error, source imaging, uncertainty, direct scalp-to-iEEG prediction/reconstruction, and working-memory load analyses. B2 must resolve the exact task/model interface and any retained contribution before implementation. |
| Choose without assuming novelty | The project is a baseline reproduction and real-data challenge. No extension or breakthrough claim has been accepted. |
| Enforce the current data policy | Active experiments use real recordings only. The paper's published synthetic results are prior work, not a license to create synthetic active experiments in this project. |

## Limits and handoff

The on004752 cohort was already analyzed in the WBEN paper. A reanalysis of that cohort is not independent-cohort replication. Its sparse iEEG does not reveal unrecorded regions or establish ground truth for every network edge. Results must be bounded to the released recordings, event-relative task, allowed contacts, and locked evaluation.

B1 has passed only for the event-relative 8-second task represented at a shared 50 Hz grid. B2 is the next gate. It must specify an exact measured outcome, allowed inputs, holdout unit, split, processing, metrics, matched baselines, leakage controls, and claim scope. It must complete the direct prior-art comparison and reject any proposed extension that is only a renamed standard score. No confirmation participant outcomes may be accessed before B5 protocol lock.

## Primary references

- Yang and Liu, [NeurIPS 2025 WBEN paper](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html).
- Machado et al., [AAAI 2023 partial-observation graph recovery](https://ojs.aaai.org/index.php/AAAI/article/view/26085).
- Berry and Sauer, [SIAM Journal on Applied Dynamical Systems 2025](https://epubs.siam.org/doi/full/10.1137/24M1655780).
- See [`METHOD_MATRIX.md`](METHOD_MATRIX.md), [`B0_EQUATION_AUDIT.md`](B0_EQUATION_AUDIT.md), [`B1_CLOSEOUT.md`](B1_CLOSEOUT.md), and [`B2_FORMAL_SPEC.md`](B2_FORMAL_SPEC.md) for the auditable project record.
