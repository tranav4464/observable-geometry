# B0 audit: multimodal scalp–intracranial network inference

**Updated 22 October 2026.** This is an equation and experiment audit of Yang and Liu, *Inference of Whole Brain Electrophysiological Networks Through Multimodal Integration of Simultaneous Scalp and Intracranial EEG*, NeurIPS 2025. The paper is direct prior art for joint scalp EEG/iEEG latent-network estimation and uses NEMAR on004752. It is a candidate reproduction-and-challenge target, not a novelty claim for Track B.

**Current-use note:** the initial synthetic-benchmark suggestions below are historical audit proposals and are superseded by the user's real-recordings-only constraint and decision D024. Do not generate or run synthetic neural data. B0's current status and selected route are defined by `B0_CLOSEOUT.md` and `GATE_REGISTER.json`; this source audit does not reopen B0.

## What the paper estimates

The latent regional activity is a VAR process,

`x_t = Σ_(k=1..K) Φ_k x_(t-k) + n_t`,

with two observation equations:

`y_t = L x_t + w_t` for scalp EEG, and `z_t = C x_t + e_t` for iEEG.

Here `L` is an EEG lead field, `C` selects the latent regions treated as directly observed by iEEG, `Φ_k` encodes lagged regional interactions, and `Q`, `P`, and `S` are state, EEG-observation, and iEEG-observation noise covariances. Their EM procedure alternates fixed-interval Kalman smoothing of latent states with a sparse VAR parameter update using FASTA. This is a linear-Gaussian state-space model with a row-wise L1 sparsity preference on the network matrix. The core objects, joint estimation, and multimodal application are already published.

## Published evidence and scope

The synthetic experiments create known source networks, generate scalp observations through a realistic-model lead field, and treat a chosen fraction of latent regions as directly observed by simulated iEEG. They vary iEEG coverage, scalp SNR, and network complexity, then score recovered directed edges. The real-data analysis uses 15 epilepsy patients performing verbal working memory, maps source estimates and intracranial contacts to 69 Harvard–Oxford regions, and compares estimated networks across encoding and maintenance phases.

This supports a proof-of-concept that adding partially observed intracranial signals can improve network-edge recovery in the paper’s simulations, and an exploratory phase-related network analysis in that cohort. It does not establish that every unrecorded region or edge is uniquely identified from the real data, that inferred directed edges are causal effects, or that the estimated networks reconstruct all neural activity. The real recording analysis is observational; VAR directionality is model-based temporal prediction under its assumptions, not an intervention.

## Equation and implementation checks to reproduce

1. **The stated sparsity-penalty sign is inconsistent.** Equation (4) maximizes log likelihood minus `λ Σ_i ||Φ_(i,:)||_1`, the usual sparsity-penalized objective. Equation (12) and Algorithm 1 instead print maximization of `Q + λ Σ_i ||Φ_(i,:)||_1`. With a positive λ, the latter rewards larger coefficients rather than sparsity. This may be a typographical error or an implementation discrepancy. No source code was public in the paper’s checklist, so the intended implementation cannot be inferred from the publication alone. Reproduction must implement the minus-sign objective, test the plus-sign literal separately, and report the difference rather than silently choosing one.
2. **The synthetic edge metric called “Acc” is precision, not conventional accuracy.** Appendix A.3 defines `Sen = N_correct / N_total` and `Acc = N_correct / (N_correct + N_wrong)`, where `N_wrong` is false positives. The second expression is positive predictive value/precision. Reproduce the published numbers under the authors’ formula, then additionally report precision, recall, specificity, false-positive rate, balanced accuracy, and edge prevalence so comparisons are interpretable.
3. **The experiment description and table disagree on coverage.** Section 3.1 says coverage ranges from 0% to 50% in 10-point steps; Table 1 includes 60%. Recover the actual levels from code if it becomes available; until then, reproduce both the prose-defined and table-defined designs or mark the 60% condition unresolved.
4. **The real-data noise model needs an explicit sensitivity analysis.** The paper says that without empty-room recordings it models EEG noise as Gaussian with standard deviation 1 and iEEG noise as Gaussian with standard deviation 0.1. These are prescribed values, not estimates from each recording's baseline noise. Because these determine the relative weight of the modalities in the fused observation, sweep plausible covariance scales and correlations, and compare with estimates obtainable from pre-event or baseline segments if the raw data support them.
5. **The observation geometry is an idealization.** The real analysis uses an `fsaverage` template, maps sources to atlas regions, averages iEEG channels assigned to a region, and uses a binary region-selection matrix `C`. This does not model individual anatomy, electrode-specific sensitivity, within-region variation, or uncertainty in the contact-to-atlas assignment. Treat the published real-data result as conditional on this representation; test perturbations and alternative mappings before interpreting individual edges.
6. **The reported method has known ghost-edge risk.** Appendix A.11 acknowledges leakage and false-positive connections under underdetermined source reconstruction. The challenge must measure false edges, edge uncertainty, and calibration as a function of coverage location and forward/noise mismatch, not just aggregate sensitivity or a visually plausible network.

## Reproduction target and challenge design

The initial synthetic-benchmark proposal in this audit is not part of the active build. The current task uses eligible real recordings only. Reconstruct the Kalman smoother/EM/FASTA equations with a CPU reference, check algebraic identities and independent implementations without fabricated neural data, and use the GPU only after the real-data CPU path is correct and a measured workload justifies it. The NeurIPS paper reports an A6000 with 48 GB; that published hardware result does not establish that this project needs GPU acceleration.

The active challenge may examine real-data variation in held-out contacts/regions, observation assumptions, and participant/session shifts only when the B2 task supports those comparisons. Do not generate graph truth or synthetic observations. On on004752, a held-out iEEG evaluation validates predictions at the withheld measured targets only; it cannot validate the full latent network as ground truth. Split by participant for population-generalization claims and by session within participant only for narrower repeatability claims.

A possible extension to investigate is a **coverage-conditioned edge support report**: label which estimated edges are directly anchored by observed iEEG, which rely on scalp plus model dynamics, and which are too unstable under plausible observation/forward perturbations to report. A useful success criterion would be improved held-out edge or withheld-contact prediction calibration at matched graph sparsity, without hiding failures through threshold tuning. This is only a candidate. Coverage-aware inference, uncertainty reporting, and robustness each have substantial prior art; B0 must still identify a precise difference and verify it against closest methods before calling it a new framework.

## Additional prior art found in the current B0 pass

Two primary sources make the support-score hypothesis less distinctive than it first appeared:

- Machado et al. (AAAI 2023) explicitly recover graph dependencies in linear stochastic network dynamics when only a subset of nodes is observed. Their method builds pairwise features from observed time series, proves a linear-separability property for the proposed features, and trains classifiers including CNNs. This is not the same measurement setting as WBEN: it does not model a scalp lead field fused with sparse, anatomically mapped iEEG contacts. However, it rules out presenting generic hidden-node graph recovery or adding an ML classifier for partial observations as our contribution. The official [AAAI paper page](https://ojs.aaai.org/index.php/AAAI/article/view/26085) describes the task and claims.
- The linked [official implementation repository](https://github.com/ASanctvs/Structure-Identification) was cloned read-only for inspection. Its notebooks implement an Erdős–Rényi network generator, a linear diffusion-like transition matrix, observed-node lag-covariance features, Granger/R1/R1-R3 estimates, Gaussian-mixture thresholding, and SVM/CNN pair classifiers. The inspected comparison notebooks use an undirected graph configuration and select a 20-node observed subset; the training notebook creates pair examples from a 100-node, p=0.5 graph and randomly splits pair examples. That split is not a held-out-graph generalization test. The repository has no README and no license file in the inspected checkout, so its code and model artifacts are not copied into this project. The paper, not the repository, remains the source for the method definition. Its pair-classification task is a useful conceptual comparator but is not a like-for-like baseline for directed WBEN VAR recovery.
- Berry and Sauer (SIAM JADS, 2025) study reconstruction of unobserved network-node time series from noisy partial observations and define an observation-error magnification factor to compare target/observer configurations. This overlaps a broad claim that coverage determines inference reliability or that sensor configurations can be ranked by error sensitivity. Their task assumes known dynamics and concerns state reconstruction, so direct score comparisons need an aligned problem; still, a WBEN application alone does not establish methodological novelty. See the [official SIAM article page](https://epubs.siam.org/doi/full/10.1137/24M1655780).

**Updated implication:** the simple score `S_e = weighted fraction of perturbation fits that retain edge e` is not approved as an innovation. It is a familiar stability construction applied to a model and data setting with significant prior art in partial observation, graph inference, and observability. Retain it only as a baseline or diagnostic unless a derivation identifies a specific quantity that existing work does not provide and a matched real-data experiment shows it improves a defined decision. The current deliverable is a faithful, tested WBEN reproduction plus a real-data challenge with claims bounded to measured targets. A new method remains conditional on B2–B4 evidence. The Machado repository is a conceptual method comparator; adapting its pair classifier to directed, multimodal WBEN would require a new, fully specified real-data experiment and cannot be described as directly reproducing the published classifier.

The primary-source screen and read-only implementation inspection establish a close task-level overlap, but not a like-for-like WBEN baseline or a complete equation-level comparison. This audit section was written before the B0 closeout and is historical. The current B0 route is closed as WBEN reproduction/challenge with no new estimator claim; later direct scalp-to-iEEG prior art is being screened under B2.

## Dataset-specific blockers

Our pinned on004752 metadata audit confirms 15 participants and 68 paired sessions, but it also found variability in reported sampling rates, a scalp/iEEG onset-grid offset, and BIDS `channels.tsv` cutoff fields that appear swapped relative to the acquisition sidecars. The paper describes 200-Hz scalp and 2,000-Hz iEEG recordings followed by downsampling to 50 Hz. Before a raw-data reproduction, reconcile the exact session versions, anti-alias filtering, resampling, synchronization, event definitions, channel reference, and the reported hardware-filter metadata against the original protocol/code. Do not assume the paper’s canonical sampling rates cover every distributed session.

The paper’s own checklist states that code was not publicly available at publication and says it would be released after acceptance. No released implementation has been verified in this audit. The official paper, its equations, appendix, and NEMAR metadata were inspected; no EEG/iEEG signal arrays were processed for this audit.

## Gate decision

- **Novelty:** the broad joint scalp+iEEG network method is already published. A generic multimodal state-space model or “whole-brain” inference claim is ruled out as a Track B novelty claim.
- **Replication value:** high enough for a carefully scoped, fully tested reproduction, especially given the printed penalty-sign inconsistency, metric naming, noise assumptions, and documented ghost-edge limitation.
- **Potential extension:** only a testable failure/robustness result or a narrowly specified coverage-conditioned decision rule that beats strong matched baselines. No invention claim is approved yet.
- **GPU:** the isolated Track B runtime now passes a CPU/CUDA double-precision solve parity check on the RTX 4050 (`3.4e-14` maximum absolute error); details and pins are in `GPU_ENVIRONMENT.md`. This is only an environment check. Use CPU as the numerical reference and benchmark the actual reproduction before claiming a GPU benefit. The sealed Track A environment remains unchanged.

## Sources

- [Official NeurIPS 2025 paper page](https://papers.nips.cc/paper_files/paper/2025/hash/82a6afb1f666daaeec8da4d775452bc7-Abstract-Conference.html)
- [Official NeurIPS 2025 full paper PDF](https://papers.nips.cc/paper_files/paper/2025/file/82a6afb1f666daaeec8da4d775452bc7-Paper-Conference.pdf)
- [NEMAR on004752 repository](https://github.com/nemarDatasets/on004752)
- [OpenNeuro ds004752 v1.0.1](https://doi.org/10.18112/openneuro.ds004752.v1.0.1)
- [Boran et al. 2019, hippocampal firing and scalp EEG during working memory](https://pubmed.ncbi.nlm.nih.gov/30944858/)
- [Dimakopoulos et al. 2022, hippocampal LFP information flow during verbal working memory](https://pmc.ncbi.nlm.nih.gov/articles/PMC9374435/)
