# Track B build-base decision: GBFs source-distinguishability tool

**Active route as of 23 October 2026:** GBFs reproduction and a nominal source-distinguishability software tool under one verified participant-specific head model. This replaces the NeuroFlowNet/on004752 route for active work. The previous decision is preserved in `BUILD_BASE_DECISION_NEUROFLOWNET_SUPERSEDED_20261023.md`; its research and data audits remain historical evidence.

## Selected base

- **Existing scientific method:** Geometric-Informed Basis Functions for EEG/MEG source imaging, using the vendored upstream checkout and the Track A adaptation.
- **Existing real-data case:** Localize-MI sub-01 with the participant-specific forward solution and recorded scalp EEG. The sealed Track A run remains immutable and all its data-derived decisions are development-only.
- **Target tool:** report nominal sensor-pattern distinguishability for specified source hypotheses, under a declared source family, head model, electrode montage/reference, and noise covariance. Preserve pairwise ambiguity rather than forcing a potentially non-transitive relation into clusters.
- **Claim boundary:** this measures distinguishability implied by the selected forward model. It is not a calibrated recovery probability or independent physiological-localization validation.

## Why this route matches the stated build goal

Track A already reverse-engineered the upstream GBFs path, checked parity on the selected real inputs, and produced nominal source-signature and MNE resolution artifacts. This is direct continuity with the user's intended build. It is also a more coherent base than combining an EEG/iEEG waveform model with a separate source-localization question.

## Candidate comparison

| Candidate | Scientific relevance | Runnable/reproducible here | Real-data fit | Ability to test the stated tool | Fit with longer-term BCI motivation | Defensible contribution space and claim risk | Decision |
|---|---|---|---|---|---|---|---|
| **GBFs** | Directly models EEG/MEG source imaging with individualized cortical geometry. | Upstream code is vendored under BSD-3-Clause, pinned, traced, and parity-checked on selected Localize-MI inputs. Track A has a sealed, runnable real-data case; full paper-benchmark reproduction remains unverified. | Strong: the participant-specific forward solution and stimulation-artifact task support a bounded real demonstration. | Directly testable against the measured stimulation-site reference and matched resolution diagnostics, with strict pulse-artifact limits. | Relevant upstream capability for future BCI/source-imaging work, while bounded to source-pattern interpretation. | A reusable workflow and empirical characterization are feasible; the nominal pair score and broad separability idea are established. No new method is accepted. | **Selected.** Matches the project goal and has an existing real-data foundation. |
| **WBEN** | Estimates electrophysiological networks by integrating simultaneous scalp EEG and iEEG with a state-space/EM model. | Public paper; reproduction requires a different regional target map and paired EEG/iEEG data contract. | Does not directly test source-pattern distinguishability; it asks a different network-inference question. | Could test joint network inference if we changed the endpoint, but combining it here would conflate estimands. | Relevant to future multimodal BCI research, but not required for the present source-imaging goal. | High claim risk if interpreted as validated whole-brain network recovery under sparse iEEG coverage and model assumptions. | **Not selected.** Relevant prior art, different output. |
| **REA** | Agent-assisted reverse engineering of binaries, applications, and runtime behavior; it is not a neural source-imaging method. | Public MIT-licensed CLI/MCP tool; native workflows may depend on external analyzers. GBFs source is already available, so those workflows are unnecessary for this code audit. | No neural dataset, forward model, or neuroscience estimand. | Could inspect an indispensable opaque executable, but does not test the selected scientific question. | May help with software inspection later; no direct BCI capability. | Low risk if limited to software observations; irrelevant as the scientific base. | **Not selected as the scientific base.** Direct source inspection is sufficient. |

This is a scope decision, not a claim that GBFs is universally the best EEG source-imaging method. The comparison follows the explicit current TKS objective and available real case. Primary descriptions: [GBFs repository](https://github.com/ncclab-sustech/GBFs), [WBEN NeurIPS 2025 paper](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html), and [REA repository](https://github.com/morluto/rea).

## Prior-art and novelty status

Source-resolution functions, ambiguity, leadfield similarity, pairwise separability, and forward-model uncertainty all have established prior art. The existing Track A whitened-cosine score is a standard nominal similarity calculation, not a new mathematical method. The software may still be a useful, rigorous build, but a new-method claim requires a specific additional operation, matched baselines, and evidence that it changes a prespecified researcher decision. `B0_EQUATION_AUDIT.md` remains the relevant collision audit and currently rules out broad novelty claims.

## Route status and required gates

B0 is closed as a **bounded base-selection/prior-art decision**: select GBFs, deliver the reproduction and nominal tool, and make no new-method claim. The nominal score is an established geometry/separability diagnostic; no standalone mathematical novelty is asserted. The GBFs license, pinned source, equation/code lineage, same-input parity scope, and prior-art boundary are documented. B1 passes for one verified Localize-MI sub-01 development case, bounded to the stimulation-pulse artifact and its participant-specific forward model.

B2 passed on 24 October 2026 after the supplied reviewer explicitly approved the registered v11 CPU64 parity recomputation and the run passed. The frozen specification is `B2-GBF-2026-10-23-v10` (SHA-256 `1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062`). The reviewer transcribed a malformed v11 verifier hash; the local verifier hash was independently computed and preserved in the B2 closeout. B3 also passes as a bounded software implementation and model-only demonstration; see `B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md`. B4 onward remain unpassed and require their own evidence and reviews. Track A remains sealed.

The active route has no novel-method claim. No model fitting, synthetic neural data, new signal analysis, or confirmatory outcome access occurred in the B2 specification review. Any future novel-method claim requires a distinct operation, matched baselines, and evidence that it changes a prespecified researcher decision. The final project still requires the outside project review specified by B8 before it can be described as externally checked.

## Alternatives

| Candidate | Current disposition |
|---|---|
| GBFs | Selected base. Reproduction and tool scope grounded in Track A artifacts. |
| NeuroFlowNet | Superseded prior route; retained documents are historical. |
| WBEN | Relevant prior art, different output (regional network inference); not combined with this source-imaging build. |
| REA | Generic software reverse-engineering toolkit, not a neural method; unnecessary for the already inspectable GBFs source. |
