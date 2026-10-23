# B2 formal specification: active route

> **Superseded on 23 October 2026. Historical NeuroFlowNet/WBEN route only.** The active build is GBFs reproduction and nominal source-distinguishability under one verified participant-specific head model. Do not use this file as an active task, protocol, or gate contract. See `PROJECT_DEFINITION.md`, `GBF_BUILD_PLAN.md`, and `GATE_REGISTER.json`.

**Gate status: IN_PROGRESS.** The active GBFs specification is [`B2_GBF_SPEC.md`](B2_GBF_SPEC.md), with its review checklist in [`B2_GBF_INDEPENDENT_REVIEW_PACKET.md`](B2_GBF_INDEPENDENT_REVIEW_PACKET.md). This file and the NeuroFlowNet/WBEN specifications are historical route records only; they do not define the active model, target, data, metrics, or authorization boundary.

## Active project contract

- **Baseline:** clean-room, source-informed implementation of NeuroFlowNet's conditional normalizing flow. The upstream repository was inspected read-only at a pinned commit; it has no declared license and is not reused.
- **Measured task:** use simultaneous scalp EEG as input to generate a conditional distribution over measured, common-reference iEEG contact waveforms in the late maintenance interval of the verbal working-memory task.
- **Evaluation question:** within a participant, how well does the model predict waveforms from a set size entirely absent during training, and do predictive intervals retain reliability under that load shift?
- **Contribution boundary:** a leakage-safe, test-time-valid real-data challenge and reliability assessment. It is not presently a novel algorithm or a claim of uniquely recovering brain sources.
- **Data discipline:** development work is restricted to real recordings from sub-01 through sub-03. Confirmation events and signal samples for sub-04 through sub-15 remain sealed until a separately versioned B5 protocol lock and access preflight. No synthetic neural data are generated or scored.
- **Implementation boundary:** the primary paper prints an incorrect affine inverse relative to its own forward equation. The clean-room code must use the algebraically verified inverse and label the correction; all other undocumented behavior is explicit adaptation. Paper-source differences and known preprocessing limitations are tabulated in [`B2_PAPER_FIDELITY_MATRIX.md`](B2_PAPER_FIDELITY_MATRIX.md).
- **Current evidence:** the dataset lineage, paired event timing, common-grid resampling adaptation, development-only fold feasibility, documentary access boundary, metric contract, and paper/source comparison are recorded under `outputs/track_b/` and linked from the active spec.

## B2 exit condition

B2 may pass only after the active specification, prior-art boundary, data-exposure record, and implementation contract receive an independent technical challenge and all findings are resolved or explicitly accepted as limitations. This document is not protocol lock, evidence of model performance, or permission to fit a model. B3 cannot begin until the gate validator records B2 as passed. B5 must lock the confirmation analysis before confirmation outcomes are opened.

## Current unresolved limits

1. Exact acquisition filtering and the NeuroFlowNet paper's numeric anti-alias filter cannot be recovered from audited records. The chosen common-grid filter is an explicit adaptation.
2. The paper's Eq. 1 and Eq. 4/Algorithm 2 are algebraically inconsistent. The independent method will use the correct inverse and cannot claim exact reproduction.
3. The inspected paper/repository details do not fully specify all architecture/data pipeline choices; those choices must stay visible in code/config and results.
4. The held-load contact-waveform task's exact overlap with all literature is not established. No priority or novelty claim is accepted.
5. The separate external/independent reviewer challenge has not been completed. Do not substitute this authoring pass for that review.

See [`B2_NEUROFLOWNET_SPEC.md`](B2_NEUROFLOWNET_SPEC.md), [`B2_PAPER_FIDELITY_MATRIX.md`](B2_PAPER_FIDELITY_MATRIX.md), [`METHOD_MATRIX.md`](METHOD_MATRIX.md), [`EVIDENCE_LEDGER.md`](EVIDENCE_LEDGER.md), and [`GATE_REGISTER.json`](GATE_REGISTER.json) for the current detailed contract and evidence paths.
