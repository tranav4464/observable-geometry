# B1 closeout: real-data and endpoint feasibility

> **Superseded on 23 October 2026. Historical NeuroFlowNet/WBEN route only.** The active build is GBFs reproduction and nominal source-distinguishability under one verified participant-specific head model. Do not use this file as an active task, protocol, or gate contract. See `PROJECT_DEFINITION.md`, `GBF_BUILD_PLAN.md`, and `GATE_REGISTER.json`.

**Decision: PASS for bounded real-data compatibility of the active 200 Hz held-load waveform task.** The earlier 50 Hz result supports the superseded WBEN route and is retained as historical evidence. The active 200 Hz checks establish paired alignment, sample-grid compatibility, and task-window indices on development data only. They do not establish exact NeuroFlowNet reproduction, final preprocessing fidelity, model performance, or a novel method.

## Evidence for each exit criterion

| Requirement | Evidence and result | Limit |
|---|---|---|
| Verify active 200 Hz paired-waveform compatibility | Development-only audit passed corrected event pairing, 8-second sample counts, and finite 2 kHz-to-200 Hz iEEG resampling across 14 sessions; see `20261023T_b1_200hz_candidate_task_audit`. | This establishes technical compatibility only. It is not exact NeuroFlowNet dataset reproduction, final filtering validation, or predictive performance. |
| Pin real dataset, version, license, citation, and manifest | NEMAR on004752 v1.0.0; CC0; pinned manifests and acquisition record in `B1_TASK_AND_DATA_DECISION.md`. | The project uses the released version only. |
| Verify real signal payload | 816 EEG/iEEG files, 10,984,433,222 bytes; independent size/checksum audit passed. | The source recordings must not be redistributed. |
| Reconcile headers, channels, and coverage without exposing reserved outcomes | Header-only audit covers all 68 paired sessions and all 15 participants. Event rows and signal samples for sub-04 through sub-15 remain unopened. | Two sessions have malformed absolute EDF start-time fields and are excluded from the primary analysis by a metadata-only technical rule, leaving at most 66 pairs. The raw files remain unchanged. |
| Establish defensible event-relative alignment | Fourteen development sessions have matching trial order, labels, 8-second sample bounds, and corrected zero-based epoch boundaries. The apparent 4.5 ms discrepancy is caused by calculating onset from one-based `begSample` without subtracting one. | This does not validate arbitrary continuous EDF/NLX synchronization or sub-sample timing. |
| Verify a real paired epoch reaches the historical WBEN grid | One real sub-01/ses-01 trial was read: 19×1,600 EEG and 48×16,000 iEEG samples; polyphase resampling yields 19×400 and 48×400 finite samples at 50 Hz. WBEN Appendix A.4 specifies the same 8-second epochs, input rates, and 50 Hz downsampling. | Historical route evidence only. This is not the active 200 Hz protocol, model training, or a performance result. |
| Define a feasible outcome and reserve confirmatory outcomes | The feasible outcome is prediction of measured held-out iEEG observations/contacts on event-relative trials, with a participant-aware summary. sub-01 through sub-03 are development-only; sub-04 through sub-15 remain reserved until B5. | The exact held-out unit, per-participant fitting allowance, metric, and split are B2/B5 decisions. No external cohort claim is available. |
| Bound the release inventory against the source paper | The pinned release contains 68 paired sessions; the source paper reports 71. The analysis is explicitly limited to pairs available in the pinned release. | The three-session difference is unresolved; this project does not infer why those files are absent. |

## Endpoint boundary

The active task uses the late-maintenance interval `[4,6)` seconds relative to trial onset, represented as two non-overlapping one-second windows on a 200 Hz grid. The primary target is the measured common-reference iEEG waveform at recorded contacts. The dataset does not provide ground truth for unobserved regions or all network edges. Results cannot establish whole-brain recovery, anatomical truth of every estimated connection, causal effects, or performance on an independent external cohort. The earlier 50 Hz event-relative WBEN representation is historical and is not the active model input/output protocol.

The source acquisition paper reports that scalp EEG, ECoG, and LFP were recorded using one Neuralynx ATLAS system. The WBEN paper's real-data section defines 50 8-second events per session, scalp EEG at 200 Hz, iEEG at 2,000 Hz, and common downsampling to 50 Hz. That historical route's released BIDS epoch and event arithmetic were verified. The active waveform candidate instead uses a 200 Hz grid; its limited development compatibility is established by the audit linked above. The author's continuous synchronization script remains useful provenance, but reproducing its original EDF/NLX procedure is not required to analyze these already event-segmented BIDS epochs.

## Remaining data-quality handling

- Exclude sub-06/ses-04 and sub-14/ses-06 from the primary analysis because standard MNE cannot parse their absolute EDF timestamps. This is fixed before any event or signal outcomes are opened; do not modify the source files.
- Interpret the sidecar `HardwareFilters` and acquisition paper as the hardware passband (0.5–1000 Hz); the channel-table `low_cutoff`/`high_cutoff` values appear reversed and must not drive preprocessing.
- Keep sub-04 through sub-15 event values and samples sealed until B5 protocol lock and preflight.
- Use at most 66 paired sessions in the primary analysis under the predeclared strict-parser exclusion.

## Next gate

B2 may now formalize the real-data estimand, training/test units, participant-level uncertainty, preprocessing, contact mapping, matched baselines, metrics, and candidate uncertainty method. B2 must decide whether the candidate method is distinct from prior art and can improve a useful real-data decision. Do not fit confirmatory participants before B5.

## Sources and run evidence

- Dimakopoulos et al., eLife 2022, [acquisition and task methods](https://elifesciences.org/articles/78677), including Neuralynx ATLAS acquisition and event timing.
- Yang and Liu, NeurIPS 2025, [WBEN paper](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html), Appendix A.4 for epoch structure, sample rates, and 50 Hz analysis.
- [Pinned NEMAR on004752 release](https://nemar.org/dataset/on004752) and [dataset repository](https://github.com/nemarDatasets/on004752).
- [`B1_TASK_AND_DATA_DECISION.md`](B1_TASK_AND_DATA_DECISION.md), [`B1_SYNC_SOURCE_AUDIT.md`](B1_SYNC_SOURCE_AUDIT.md), and [`GATE_REGISTER.json`](GATE_REGISTER.json).
- [`alignment feasibility run`](../../outputs/track_b/20261022T182700Z_b1_alignment_verification/alignment_feasibility.json), [`reproducible audit script`](../../outputs/track_b/20261022T182700Z_b1_alignment_verification/audit_alignment.py), and [`session record`](../../outputs/track_b/20261022T182700Z_b1_alignment_verification/SESSION.md).

## 200 Hz active-candidate compatibility check

A later development-only audit checked whether the same event-locked release can also be represented at 200 Hz for a direct scalp-to-iEEG waveform-model candidate. All 14 sub-01–03 paired sessions passed event-row pairing, corrected event-boundary alignment, and real-signal shape/finite checks after resampling iEEG from 2,000 to 200 Hz. The sessions contain 46–50 paired trials, so the audit verifies contiguous trial numbering rather than assuming exactly 50 rows in every session. See [`200 Hz audit result`](../../outputs/track_b/20261023T_b1_200hz_candidate_task_audit/audit.json), [`procedure`](../../outputs/track_b/20261023T_b1_200hz_candidate_task_audit/audit_200hz_alignment.py), and [`session record`](../../outputs/track_b/20261023T_b1_200hz_candidate_task_audit/SESSION.md).

This check is the active-route B1 compatibility evidence, not a supplementary footnote to the old WBEN route. The task-window source audit independently mapped `[4,6)` to the final two seconds of maintenance and verified the corresponding development event indices. Together they establish the limited data and task feasibility required to specify B2; they do not establish full preprocessing, model, performance, novelty, or held-load predictive validity.
