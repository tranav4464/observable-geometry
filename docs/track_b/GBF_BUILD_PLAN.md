# GBFs source-distinguishability build plan

## Objective

Deliver a runnable software build that reproduces the relevant GBFs behavior, explains its implementation, and measures nominal distinguishability between source hypotheses using one verified real participant-specific forward model. Any further mathematical contribution must be distinct from existing EEG/MEG resolution and ambiguity methods and must change a useful decision. The project uses real data only.

## Work stages

### B0: Base and prior art

Reconfirm upstream GBFs version/license, equation-to-code lineage, Track A parity scope, and the direct literature on resolution matrices, source ambiguity, leadfield similarity, source separability, and forward-model uncertainty. Select the GBFs route explicitly. No broad novelty claim.

### B1: Real case and forward model

Use the pinned Localize-MI release and sub-01 case already retained in Track A. Verify manifests and licenses; trace scalp montage, units, reference projection, noise covariance, source coordinates, orientation, individual anatomy, forward-solution provenance, and stimulation contact pair to primary dataset records. State that the pulse artifact validates only that task. No synthetic dataset or synthetic signal work.

### B2: Formal tool specification

Define input/output types, units, assumptions, mathematical score, pairwise decision or display, thresholds if any, and the research decision it supports. Compare nominal whitened similarity with the MNE resolution matrix, point-spread/cross-talk summaries, and published source-separability methods. Include limiting cases, invariants, failure handling, and falsification criteria using equations and code checks, not synthetic signal experiments. Independent challenge required before passing.

### B3: Reproduction and tool implementation

Preserve Track A as sealed. In a new versioned module, expose the GBFs method and source-distinguishability calculation through a documented API/CLI. Trace every operation to upstream code or mark it as a project adaptation. Keep CPU float64 as reference; test with the existing real case after B2 passes.

### B4: Real-data development checks

Run only prespecified checks on development real recordings. Recompute scores independently, compare with matched resolution baselines, inspect sensitivity to documented analysis assumptions, and report failures. Do not use a synthetic neural dataset or claim generalization from one participant.

### B5/B6: Confirmatory evaluation route, pivoted

The B4 audit found no valid endogenous neural-source endpoint in the permitted Localize-MI case. B5 protocol lock and B6 held-out evaluation are therefore **PIVOTED**, not passed. No reserved outcomes were opened. Reopen only after identifying a real-data task with a suitable independent reference, verifying the forward-model contract, completing a focused prior-art review, and reviewing a locked protocol before outcome access. The route closeout is `B5_B6_ROUTE_CLOSEOUT_20261024.md`.

### B7: Practical value, pivoted

The paired same-model comparison found moderate associations between the B3 score and MNE PSF summaries, but did not test whether analysts change or improve a source-reporting decision. B7 is therefore **PIVOTED** under its failure route. Retain the score as an inspectable descriptive diagnostic and make no utility claim. See `B7_DECISION_VALUE_AUDIT_20261024.md`.

### B8: Package

Provide clean setup, one command for the real-data demonstration, tests, pinned provenance, saved outputs and manifest, technical/plain-language walkthrough, limitations, claim-to-evidence table, and outside technical review. Keep publication of an academic paper secondary to the software build.

## Current state and next action

Track A already supplies the sealed GBFs implementation-parity result, reverse-engineering record, nominal source-signature library, ambiguity pairs, offline report, and MNE resolution comparison. The clarified three-part goal is therefore substantially present in Track A; see `outputs/track_b/20261023T_b0_gbf_route_reconciliation/FOUNDATION_SCOPE_CHECK.md`. The NeuroFlowNet route is historical. B0 is passed as a bounded GBFs reproduction/software route with no novel-method claim. B1 passes for the one-participant pulse-artifact development case.


The B2 specification is frozen as `B2-GBF-2026-10-23-v10`, SHA-256 `1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062`. The hardened independent v11 verifier is separately versioned at SHA-256 `0927f600bc4843319f96c2f8cdb0e64753861e926d665e55417a76855d17f57e`. The registered v11 CPU64 parity run passed exact ranking, validity, and count checks; score, residual replay, and whitened-norm comparisons met their fixed tolerances. Near-tie margins are recorded. The supplied review text contains a malformed v11 hash string, and the workspace contains conflicting reviewer-identity declarations; both limitations remain visible in the review records. B2 is recorded **PASS** for the frozen specification and registered computation; see `B2_GATE_CLOSEOUT_20261024.md`. B3 is **PASS** for the reusable CPU-float64 nominal distinguishability API/CLI and one sealed model-only demonstration; its method trace, test evidence, and limitations are recorded in `B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md`. The cosine score is not claimed as new mathematics.

B4's fresh 224-channel rerun reproduced the sealed pairwise table byte-for-byte, but the permitted Localize-MI evidence remains a one-participant stimulation-pulse artifact task, not validation of endogenous neural-source distinguishability. B1 source-generator checks also show large structured residuals under the tested point-source families. The earlier join between 236-channel B2/B3 artifacts and 224-channel empirical results is invalid and preserved. B4 is therefore **PIVOT** under its failure route: retain the bounded reproduction/software build and do not open held-out Localize-MI outcomes or claim neural recovery. B5/B6 are explicitly **PIVOTED** without protocol lock or held-out analysis. See `B4_DEVELOPMENT_AUDIT_20261024.md`, `B4_CHANNEL_MATCH_RECONCILIATION_20261024.md`, and `B5_B6_ROUTE_CLOSEOUT_20261024.md`.

B7 compared all 8,196 B3 source-pair scores with paired MNE point-spread summaries under the same 236-channel model. The rank associations are moderate (`|rho| = 0.39–0.48`), and the top decile of forward-signature similarity has worse median MNE resolution summaries than the remaining sources. This is a distinct descriptive view in this model, not evidence of analyst decision benefit, a new method, or physiological source recovery. B7 is therefore **PIVOT** under its failure route: retain the diagnostic and exclude utility claims. See `B7_DECISION_VALUE_AUDIT_20261024.md`.

The installed CLI and clean-wheel model-only reproduction pass. B8 remains in progress pending unaffiliated external review and a clean committed source snapshot with its verification report. The source license and citation metadata are now present. Conflicting B2 reviewer-identity records remain disclosed, so the supplied reviewer identity is not represented as authenticated. See `B8_RELEASE_AUDIT_20261024.md`.
