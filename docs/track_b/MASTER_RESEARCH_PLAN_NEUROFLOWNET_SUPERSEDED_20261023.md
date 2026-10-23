# Observable Geometry: Track B project specification

**Deliverable:** a runnable, reviewable computational-neuroscience ML/software build.
**Current status:** B-1, B0, and B1 are recorded as passed within their documented limits; B2 is in progress; B3–B8 have not passed. The machine-readable [`GATE_REGISTER.json`](GATE_REGISTER.json) is authoritative.
**Data rule:** active scientific analyses use the permitted real recordings only. Do not generate or analyze synthetic datasets or synthetic signal fixtures.
## 1. The project in one paragraph

Observable Geometry will reproduce and challenge an existing model that relates scalp electroencephalography (EEG) to intracranial EEG (iEEG), using paired real recordings. The software will make the path from source data to predictions auditable, compare the reproduced model with fair baselines, and show which conclusions the recordings can and cannot support. A mathematical extension will be developed only if a primary-source review identifies a real gap and an evaluation shows that the extension changes a useful, prespecified research decision. The final product is the working software and its evidence trail, not a paper or an unsupported claim of novelty.

## 2. Scientific question and boundaries

The central question is:

> **Given paired scalp EEG and iEEG recordings from a defined task, which properties of the measured intracranial signal can be predicted from scalp data, and which inferred model properties are actually constrained by the available observations?**

Scalp EEG measures voltage differences at electrodes. Each channel can contain contributions from multiple neural sources and depends on the reference and measurement setup. iEEG measures activity closer to selected brain tissue, but clinical electrodes sample only a small and uneven set of locations. A model may predict a recorded iEEG signal without uniquely identifying the underlying source, network, or activity in tissue that was never measured.

The project therefore distinguishes four kinds of result:

1. **Measurement:** a recorded scalp or intracranial signal, with its sensor, reference, time interval, and preprocessing stated.
2. **Prediction:** an estimate of a held-out measured signal from permitted input data.
3. **Latent model estimate:** an internal state, connection, or parameter inferred by a model rather than directly observed.
4. **Biological interpretation:** a claim about neural sources or mechanisms that requires evidence beyond predictive fit alone.

An improvement in one category does not automatically establish an improvement in another. In particular, this project does not claim to reconstruct the whole brain, read arbitrary thoughts, recover a unique true network from a good fit, establish causal mechanisms, or infer activity from unrecorded tissue.

## 3. What will be built

The project will provide an installable software workflow through which a researcher can inspect the data provenance, run approved preprocessing, fit the reproduced baseline and matched alternatives, inspect predictions next to measured targets, recompute metrics, and see which assumptions materially affect the result.

The build has six parts:

### 3.1 Existing reference model

The active B0 decision selects a clean-room, source-informed implementation of NeuroFlowNet's published conditional-flow method for paired scalp EEG to measured iEEG waveform prediction. It is established prior work, not our invention. Trace the paper into equations, code, configurations, and outputs, and document ambiguities rather than silently choosing an interpretation. Call the implementation a reproduction only if the B3 fidelity checks pass. The earlier WBEN route is archived historical work, not the active model.

### 3.2 Fair comparison models

Implement a small set of task-matched baselines selected only after B2 fixes the task. These may include a simple predictor and a regularized direct mapping. Add another published comparator only when its task, input, target, split, metric, implementation, and reuse conditions are verified. Every comparator receives the same permitted data, split, preprocessing, and a defensible tuning opportunity.

### 3.3 Real-data pipeline

The pipeline will validate source files and metadata, record checksums and provenance, apply only prespecified preprocessing, enforce participant-aware data partitions, save predictions and failures, recompute metrics independently, and retain uncertainty at the participant level. Each run will have a unique identifier and immutable configuration. Original data files will not be modified.

### 3.4 Candidate project contribution

The active candidate is a leakage-safe, within-participant held-load evaluation of whether NeuroFlowNet predicts measured iEEG contact waveforms at an unseen working-memory set size, including an assessment of predictive reliability. This is an empirical challenge/evaluation contribution, not a new flow algorithm or established mathematical method. Its exact overlap with task-level prior art remains unresolved. B2 must determine whether it exposes a useful capability or failure boundary beyond existing held-trial, held-session, and cross-task work. If it is already covered or does not change a meaningful decision, retain only the bounded implementation/benchmark and remove novelty wording. The prior generic identifiability and WBEN-profile proposal is historical and is not the active candidate.

### 3.5 Researcher-facing outputs

Reports and visualizations will distinguish measured signals, predictions, latent estimates, and biological interpretations. They will expose uncertainty, failed fits, exclusions, and the assumptions behind any estimate. An abstain or “insufficient evidence” outcome is appropriate when the data do not support a confident output. A readable graphic is not itself evidence of scientific utility.

### 3.6 Reproducible handoff

The software will include environment and data setup instructions, documented commands, configuration and run manifests, tests of meaningful invariants, saved permitted outputs, a plain-language walkthrough, a technical description of the mathematics, limitations, and a claim-to-evidence table. A clean setup must reproduce the approved outputs without relying on undocumented local state.

## 4. Chosen base and alternatives

### NeuroFlowNet

NeuroFlowNet is the active B0-selected implementation base because its reported output is a conditional distribution over iEEG waveforms given paired scalp EEG, matching a measured contact-waveform endpoint in the available dataset. The inspected author repository has no declared license and is not reused. The project independently implements from the paper and must document unresolved filter, normalization, architecture, and metric details. The source cohort overlaps the selected dataset; this is not an independent-cohort replication. The current B2 specification defines a candidate held-load challenge, not a verified reproduction or novelty claim.

### WBEN

WBEN is established prior work and remains relevant background for joint scalp/iEEG network estimation, but it is not the active Track B model. Its earlier implementation and contact-state proposal are historical only. Do not compare WBEN's regional network scores directly with contact-waveform prediction.

The WBEN paper audit flagged ambiguities in the sparsity-term sign, a metric called “accuracy” whose equation appears to be precision, and prose/table coverage levels. Those are recorded for historical context and do not define the active NeuroFlowNet implementation.

### Track A GBFs

Track A is sealed engineering infrastructure. Its geometric basis functions may be used as a comparator or source-representation component only if B2 establishes a relevant task. Track A results do not validate Track B’s scientific claims.

### REA

REA is a reverse-engineering toolkit, not a neural model or scientific contribution. Use it only if inspection of its actual code shows that it materially helps explain or test the selected baseline. Do not select it just because its name or popularity seems relevant.

### Alternatives

The B0 base decision is recorded in `B0_CLOSEOUT.md` and `METHOD_MATRIX.md`. Reopen it only if new primary-source or data evidence materially invalidates the route. Do not combine unrelated projects to make the build sound larger.

## 5. Data and access rules

The active dataset is NEMAR `on004752`, release v1.0.0, a paired scalp EEG/iEEG working-memory dataset. Its record is CC0. The pinned release contains 68 paired sessions, whereas the source paper reports 71; this discrepancy remains unresolved, so analysis can use only verified files present in the pinned release. Two sessions with malformed absolute EDF timestamps are excluded by the existing metadata-only rule, leaving at most 66 candidate pairs.

Participants `sub-01` through `sub-03` are development-only. Participants `sub-04` through `sub-15` remain sealed until the B5 protocol lock and access preflight pass. If outcomes from the sealed group are accessed earlier, that group becomes development data and cannot later support an independent-confirmation claim.

B1 passed for bounded real-data compatibility on the active 200 Hz waveform route. Paired event alignment, native sample shapes, and real-signal resampling were checked in 14 development sessions using sub-01 through sub-03. The active B2 candidate keeps scalp EEG at 200 Hz and resamples iEEG from 2,000 Hz to 200 Hz before extracting the audited late-maintenance window. This is feasibility evidence only; it does not establish continuous-stream synchronization, sub-sample timing, phase fidelity, causal connectivity, or ground truth for unobserved neural activity. The separate 50 Hz result belongs to the superseded WBEN route.

Active model evaluation uses real recordings only. Do not create or run synthetic signal data or synthetic datasets. Verify code with algebraic identities, independent implementations, and permissible real-data checks. Historical synthetic artifacts are archival and are not project evidence. Respect privacy and license terms; do not redistribute recordings or licensed transform assets.

### Coordinate-space correction

An earlier direct Harvard–Oxford atlas lookup treated two MNI template spaces as identical. That lookup and its reported 374/760 assignment count are withdrawn as anatomical evidence. A candidate template crosswalk has been audited for numerical forward/backward consistency on development electrode metadata, but this does not prove subject-specific anatomical accuracy or reproduce WBEN's exact contact assignment. The transform is a named analysis variant, not anatomical ground truth; the downloaded fields remain local under their CC BY-NC-SA 4.0 terms. The identity of coordinate rows and WBEN's exact conversion, assignment, tie, distance, and outside-label rules remain unresolved. See [`B2_TEMPLATE_SPACE_CROSSWALK.md`](B2_TEMPLATE_SPACE_CROSSWALK.md) and [`B2_SOURCE_COORDINATE_PIPELINE.md`](B2_SOURCE_COORDINATE_PIPELINE.md).

## 6. Stage gates and evidence required

The gates are quality controls, not a schedule. The register records whether evidence exists; prose or code alone does not pass a gate.

| Gate | Purpose | Evidence required to pass |
|---|---|---|
| B-1 | Preserve Track A as a sealed foundation | Recorded engineering checks and release artifacts; no Track A result used as Track B validation. |
| B0 | Select the build base and audit broad prior art | Verified base comparison, licensing/data review, reproduction target, and recorded contribution boundaries. |
| B1 | Verify data feasibility | Source integrity, event alignment, exposure controls, feasible signal representation, and explicit limits. |
| B2 | Freeze the scientific task | One estimand, target map, split, preprocessing, metric, baselines, failure rules, exact prior-art comparison, and keep/reject criterion for the contribution. |
| B3 | Implement NeuroFlowNet clean-room | Equation-to-code trace, CPU reference, permitted real-development run, and independent output/metric check. |
| B4 | Challenge the baseline and candidate | Development-only comparisons, negative controls, sensitivity analysis, failures, and documented keep/reject decision. |
| B5 | Lock confirmation | Immutable protocol, split, configuration/code/data hashes, and access preflight before sealed outcomes are read. |
| B6 | Evaluate on held-out real data | Locked run, independently recomputed metrics, participant-level uncertainty, complete failures and deviations. |
| B7 | Establish researcher value | Prespecified decision value beyond the baseline, or removal of utility claims. |
| B8 | Package the build | Clean setup and reproduction, provenance, license-aware release, limitations, and external technical check. |

The authoritative gate IDs and statuses are in [`GATE_REGISTER.json`](GATE_REGISTER.json). B-1, B0, and B1 are recorded as passed within their stated boundaries; B2 is open; B3–B8 are not passed. These statuses must not be upgraded based on plans or unexecuted code.

## 7. B2: decisions that remain open

B2 has an active candidate specification in `B2_NEUROFLOWNET_SPEC.md`: within each participant, train on two working-memory set sizes and evaluate contact-waveform prediction on the third, while assessing predictive reliability. The target is the measured common-reference contact waveform, not an anatomical source. This is within-participant load transfer, not between-participant generalization or future prediction. B2 remains IN_PROGRESS because the exact task-level prior-art overlap, final technical choices, and independent challenge are unresolved. No model fitting is permitted before B2 passes. The earlier WBEN/Kalman and atlas-mapping proposal is historical only.

The paired-channel audit found different full scalp montage sizes (19 channels for sub-01 and 8 each for sub-02/sub-03), no explicit channel-status flags, and a conflict between channel-table cutoff values and EEG sidecar/BIDS filter definitions. B2 therefore specifies the same eight metadata-verified scalp channels in a fixed order for all retained sessions, with fold-local training-only screening. The effective acquisition filters remain undocumented because development EDF prefilter fields are blank and metadata conflict; the specified common-grid anti-alias filter is an explicit adaptation, not a recovered acquisition filter or exact paper preprocessing.

B2 must record:

- the precise measured inputs and target, units, contacts/channels, time windows, and task labels;
- which observations can be used to fit each evaluation unit and what population the result generalizes to;
- coordinate/contact handling, reference, filtering, anti-aliasing, artifact rules, missing-channel handling, and fit boundaries for preprocessing;
- participant/session/trial split rules, overlap protections, and leakage checks;
- a primary metric, limited secondary metrics, participant-level uncertainty, and matched baselines;
- convergence, exclusions, negative controls, failure thresholds, and independent score recomputation;
- primary-source comparison of the candidate contribution with its closest methods;
- a falsifiable criterion for retaining or rejecting the candidate.

The prior-art review must include scalp-to-iEEG prediction and reconstruction, virtual-iEEG, load-related analyses, information-theoretic EEG/iEEG work, profile and prediction-profile likelihood, dynamic-network identifiability, neural-population EEG identifiability, DCMident, robust system identification, and any closer method found for the final estimand. For each close comparator, record publication status, cohort, task, input, target, split, metrics, code/data access, and claim limits. Resolve the task mismatch flagged in the CAST preprint before treating it as a direct comparator. Generic prediction, mutual-information scoring, model ensembles, graph stability, or uncertainty outputs do not become new merely by applying them to this cohort.

If a task depends on anatomical labels that cannot be verified, either define a defensible non-anatomical endpoint or explicitly treat the crosswalk as a sensitivity variant. Do not turn an uncertain mapping into ground truth.

## 8. Mathematical contribution: accept or reject by evidence

Before implementation as a scientific method, specify the mathematical object completely:

- estimand, variables, dimensions, units, assumptions, and equations;
- operational meaning of support, identifiability, reliability, or stability;
- algorithm and outputs, including behavior when evidence is insufficient;
- limiting cases, failure cases, and a hand-worked analytical example;
- strongest matched baseline and the closest prior method;
- the researcher decision the output could change;
- an explicit result that would falsify the contribution.

Then ask whether it is identifiable from the actual observations, numerically estimable, distinct from prior art, and useful for the selected task. An uncertainty score is not calibrated uncertainty unless calibration is demonstrated. A stable optimizer output is not proof of an identifiable biological network. A better prediction score is not proof of anatomical recovery.

Keep the candidate only if a precise prior-art distinction survives and a fair evaluation shows either a prespecified improvement in a useful decision or a reproducible failure boundary that the current evaluation misses. If it fails, report the negative result and retain only claims supported by the reproduction and challenge.

## 9. Reverse engineering and implementation rules

For the chosen baseline, document the data flow, model architecture, equations, observation operators, preprocessing, objective/loss, parameter updates, initialization, stopping criteria, and outputs. Preserve the original implementation or source snapshot when licensing permits. Keep the independent implementation and candidate extension separate so comparisons are reviewable.

Use CPU float64 as the correctness reference. The existing GPU environment is a capability, not a scientific result. Recheck it before use; run GPU computation only when a permitted real workload benefits, and compare its output with the CPU reference. Do not report a GPU advantage from a runtime smoke test alone.

Write tests for meaningful invariants and scientific failure modes, not tests that merely mirror the implementation. Use analytical identities and independent numerical implementations. Keep configurations, commands, environment, logs, warnings, predictions, metric outputs, exclusions, and hashes for every run. Preserve failed runs and negative results; never overwrite sealed artifacts.

## 10. Evaluation and reporting

All models must receive matched permitted data, preprocessing, split information, and tuning opportunity. Keep all data from a participant together for claims about generalization to people. Treat participants, not repeated trials, windows, or contacts, as the uncertainty unit for population claims.

The report must include the prespecified primary metric, suitable secondary metrics, participant-level uncertainty, all failed fits and exclusions, negative controls, missing channels, protocol deviations, and independent metric recomputation. Compare predictions with measured targets. Do not use held-out outcomes to choose preprocessing, targets, channels, thresholds, model settings, or exclusions.

The final claim-to-evidence table must identify, for every important claim, the exact code path, run, data split, metric or check, and limitation supporting it. Report separately what the build establishes and what it does not establish.

## 11. Stop, narrow, or pivot conditions

Stop or narrow the claim if the released data cannot support the endpoint or split; contact mapping depends on unverified anatomy; source ambiguities prevent fair reproduction; prior art already covers the proposed method; the result depends on unobserved neural ground truth; the candidate fails its criterion; leakage is discovered; or uncertainty is not calibrated as claimed. Preserve the evidence, update the decision log and evidence ledger, and choose a narrower real-data task. Do not rescue a failed claim with synthetic results, post-hoc test changes, or inflated wording.

## 12. Definition of a complete software build

Track B is complete only when:

1. The base project, license, data, and actual inputs are verified.
2. The reference method is reproducible or its exact reproduction limits are documented.
3. The selected task and protocol are frozen before confirmatory outcomes are accessed.
4. Any contribution is implemented separately and distinguished from prior work.
5. Meaningful checks, negative controls, fair comparisons, and required real-data evaluation are completed.
6. Results, failures, uncertainty, limitations, and provenance are saved.
7. The documented main command works in a clean setup and reproduces approved outputs.
8. The gate register, evidence ledger, decision log, method matrix, and review page match the actual evidence.
9. No scientific, novelty, or performance claim exceeds what was demonstrated.

If a scientific contribution fails, a rigorously bounded reproduction or benchmark can still be a useful build. The project must describe it as such.

## 13. Current state and next action

B-1, B0, and B1 are recorded as passed within scope. B2 remains in progress; B3–B8 have not passed. The active route is NeuroFlowNet with a candidate within-participant held-load measured-waveform challenge, not WBEN source/network inference. No algorithmic novelty is accepted. Complete B2 by finishing the focused task-level prior-art comparison, resolving remaining protocol details, and obtaining an independent technical challenge of the specification. If the held-load question is preempted or not decision-relevant, narrow the project to a bounded clean-room implementation/benchmark instead of implying novelty. Only after B2 passes may B3 fitting begin. Do not inspect `sub-04` through `sub-15` outcomes before B5 passes.

## 14. Primary sources and project records

- He et al., [NeuroFlowNet full text](https://arxiv.org/html/2603.03354v3) and [arXiv record](https://arxiv.org/abs/2603.03354), the active implementation base; source-informed adaptation, not yet a verified experimental reproduction.
- Yang and Liu, [WBEN, NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html), historical prior art for the superseded route.
- Dimakopoulos et al., [paired scalp EEG and iEEG working-memory dataset paper, eLife 2022](https://elifesciences.org/articles/78677).
- NEMAR, [dataset `on004752`](https://nemar.org/dataset/on004752).
- [BIDS iEEG specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/intracranial-electroencephalography.html).
- [2026 virtual-iEEG review](https://arxiv.org/abs/2608.26998), a review/preprint used to bound broad novelty claims, not evidence validating our method.
- Raue et al., [structural and practical identifiability using profile likelihood](https://doi.org/10.1093/bioinformatics/btp358).
- Arand et al., [profile-likelihood identifiability analysis for DCM](https://doi.org/10.3389/fnins.2015.00043).
- Hartoyo et al., [parameter identifiability in a neural population model fitted to EEG](https://doi.org/10.1371/journal.pcbi.1006694).
- Boring et al., [cross-task EEG decoding of cognitive load](https://doi.org/10.1088/1741-2552/abb9bc).
- [Pinned dataset localization script](https://github.com/vdimakopoulos/verbal_working_memory/blob/395ae136372be9772cdbeb09bccd677fda01b5d6/Channel%20Localization/Main_4_Region_assignment_200226.m).
- [Pinned source for the audited template transform](https://github.com/LeonDLotter/NiSpace-data/tree/8b3bb0e8ba47a8a2b7c42b801e23b6b7cecf5c26); its license and redistribution limits are documented in the crosswalk audit.

Project records: [`PROJECT_DEFINITION.md`](PROJECT_DEFINITION.md), [`B2_FORMAL_SPEC.md`](B2_FORMAL_SPEC.md), [`METHOD_MATRIX.md`](METHOD_MATRIX.md), [`EVIDENCE_LEDGER.md`](EVIDENCE_LEDGER.md), [`DECISION_LOG.md`](DECISION_LOG.md), and [`GATE_REGISTER.json`](GATE_REGISTER.json).
