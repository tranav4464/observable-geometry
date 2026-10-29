# DeESI equation and code audit

**Audit date:** 28 October 2026
**Scope:** full author-hosted paper, publisher/indexed record and pinned author code; no EEG samples accessed
**Repository:** [tongpf/Debiased_EEGMEG_source_imaging](https://github.com/tongpf/Debiased_EEGMEG_source_imaging)
**Observed `main` revision:** `4abb42725a028ada9c214226931c29b08d1faf86` (`git ls-remote`, 28 October 2026)

The three inspected repository files were cloned at that revision. SHA-256:

| File | SHA-256 |
|---|---|
| `README.md` | `ECE8B1C57B636F754E593270C8F1B0B64FBAEB21A281C130406BEC8A0120F1F5` |
| `ADMM_GroupLASSO.py` | `8844BEFFCDA708191D2735C63D7C133C8AC2C515BC163261A3A891A55E2739B5` |
| `simulation_study.py` | `5F4D8A835225AA760C3C2C5D79D2FE82FD594AD42E88684C41174658A7087693` |

## Primary sources inspected

* Tong et al., *Debiased Estimation and Inference for Spatial-Temporal EEG/MEG Source Imaging*, IEEE Transactions on Medical Imaging 44(3), 1480–1493 (2025), [DOI 10.1109/TMI.2024.3506596](https://doi.org/10.1109/TMI.2024.3506596), [PubMed record and abstract](https://pubmed.ncbi.nlm.nih.gov/40030292/).
* Mikulan et al., *Simultaneous human intracerebral stimulation and HD-EEG, ground-truth for source localization methods*, Scientific Data 7, 127 (2020), [paper](https://doi.org/10.1038/s41597-020-0467-x), [dataset description](https://pmc.ncbi.nlm.nih.gov/articles/PMC7189230/).
* Full 14-page author-hosted version, [PDF](https://www.songxichen.com/Uploads/Files/Publication/Debiased_Estimation_and_Inference_for_SpatialTemporal_EEG_MEG_Source_Imaging.pdf). This complete copy was inspected on 28 October 2026 after two separate local download attempts had produced truncated files.
* Author repository README and `ADMM_GroupLASSO.py`, [repository](https://github.com/tongpf/Debiased_EEGMEG_source_imaging), [implementation at the inspected revision](https://github.com/tongpf/Debiased_EEGMEG_source_imaging/blob/4abb42725a028ada9c214226931c29b08d1faf86/ADMM_GroupLASSO.py).

## What is already implemented

The paper proposes a sparse spatiotemporal inverse estimator. Its abstract describes a group-Lasso extension using Frobenius and L1 penalties to encourage sparsity over source groups while retaining temporal/orientation structure. It derives a variance for debiased estimates, enabling standardized estimation and hypothesis testing, and reports comparisons with eleven ESI methods plus an open EEG dataset with known stimulation locations.

The inspected public implementation operates on a leadfield `G`, sensor-by-time matrix `Y`, source coefficients `X`, and orientation grouping `O`. Its ADMM routine estimates a group-sparse support. The bias-correction routine then partitions selected and unselected source groups, fits a structured nuisance contribution from unselected groups, residualizes the selected lead fields, and applies a projected least-squares correction. The source implements the covariance-like quantity for corrected coefficients from the pseudoinverse/projection terms. It has an explicit rank check; if the projected selected design is rank-deficient, the correction is not performed. See `ADMM_GroupLASSO.py`, especially `gl_ADMM_dual_bias_correction` and `_gl_ADMM_dual_bias_correction`.

The variable named `significance_list` is annotated `# the p-value`, but the inspected code fills it with norms of the correction effect matrix multiplied by the debiased estimates; no p-value tail transformation or hypothesis decision appears in the inspected repository. It should not be interpreted as a p-value, calibrated probability, or family-wise source-compatibility certificate. This finding is limited to the public code at the pinned revision; the paper separately defines the test statistic below.

## Full-paper equation and endpoint review

The complete paper resolves the previous full-text gap. Its stated model is `Y = GX + E` (Eq. 1), with a given patient-specific gain matrix and IID Gaussian measurement errors independent of `G` (lines 173–191). Its core estimator is a scaled rotated group Lasso (Eqs. 11–12): a Frobenius loss with a sum of weighted group-Frobenius source penalties, jointly estimating noise scale. This yields source sparsity while retaining temporal/orientation structure.

The paper's debiasing target is materially different from Observable Geometry's candidate-family compatibility question. After selecting active groups `A`, it fits nuisance contributions from unselected leadfield groups (Eqs. 13–16), residualizes the selected leadfields, and obtains a post-selection least-squares correction (Eq. 15), provided a rank condition holds. It derives an asymptotic covariance under a strong group-sparsity condition (Eq. 17) and a chi-square-type test under Gaussian errors and a full-rank condition (Eq. 18). This is source-amplitude inference conditional on a selected support, not a robust identified set over competing physiological families and an explicit forward-operator uncertainty set. However, it means broad claims to “uncertainty-aware,” “statistically tested,” or “more interpretable” source estimates are already occupied and cannot distinguish the build.

The real-data endpoint is especially relevant prior art. The paper analyzes the seven-participant Localize-MI dataset with simultaneous 256-channel hdEEG and SEEG, anonymous MRI, known electrical stimulation contacts, and BEM forward models. Mikulan et al. describe 61 sessions across those seven participants. DeESI uses epochs from -250 to 50 ms, averages good trials, and reconstructs from a -2 to +2 ms interval (33 temporal observations at 8 kHz); the endpoint is dipole localization distance to the known stimulation site and source-signal reconstruction. It reports mean DLD of 11.2 mm (fixed orientation) and 11.5 mm (free orientation), comparing 12 methods, and discusses forward-model conductivity sensitivity. This is direct prior art for known-stimulation localization on **Localize-MI**, our designated pulse-artifact control. It is not evidence that DeESI analyzed the separate 36-participant WSGZP/iES-CCEP resource.

That result is not equivalent to the planned late post-artifact CCEP question: the paper's principal reconstruction window is tightly centered on stimulation onset, while our prospective target concerns later physiological responses in WSGZP and must treat the stimulation contact as an intervention site rather than ground truth for the later distributed response. The datasets are distinct: Localize-MI is the seven-subject pulse-localization dataset; WSGZP/iES-CCEP is the separate 36-participant stimulation-parameter/CCEP resource. This distinction creates a legitimate *different estimand to test*, but does not make the method novel. A matched comparison must verify dataset/version and event units, channels, forward-model provenance and preprocessing; it must include the published Localize-MI comparator for the control analysis where reproducible. Do not present DeESI's Localize-MI result as a WSGZP result or as independent validation on WSGZP.

The authors also report standard PSF/CTF resolution analysis (Eq. 19 onward), which rules out presenting point-spread/cross-talk diagnostics alone as a new contribution. Their methods rely on a known forward matrix and Gaussian IID errors, and the paper itself notes sensitivity to conductivity and MRI anonymization. An explicit robust operator-uncertainty guarantee could be a mathematical extension only if it is not reducible to existing robust inverse-estimation methods and changes a prespecified measured-data decision.

## Reproducibility and comparator implications

The repository README calls the code example code and routes reproduction to `simulation_study.py`; that script creates an MNE `fsaverage` forward solution and synthesizes source time courses and sensor noise. It contains no corresponding real-data analysis script or dataset. The full paper supplies the real-data protocol, but a matched DeESI analysis is not turnkey from the repository. The complete author-hosted paper has now been inspected directly, so equation-level paper review is no longer open. The two truncated local copies remain unusable and were not used as evidence.

DeESI weakens any generic novelty claim about sparse multi-source estimation, bias correction, uncertainty estimates, variance-based hypothesis tests, or validation against known stimulation locations. The present project is not distinguished merely by returning several candidate source maps. Its proposed object is a family-wise compatibility/ambiguity report under explicit forward-model uncertainty. That is a task difference, not yet a novel method: SESAMEEG, finite-union recovery, set-membership methods, robust inverse methods, and close CCEP source-extent studies remain comparators. A defensible contribution would require either a theorem not reducible to those methods or a predeclared measured-data decision advantage beyond them.

## Next required checks

1. Record the confirmed identity: DeESI's seven-subject analysis uses Localize-MI, not WSGZP/iES-CCEP. Preserve this distinction in the dataset map and reports.
2. Extract the full preprocessing and comparator details, identify any supplementary protocol, and determine whether an implementation-faithful DeESI comparator can be run on the project's Localize-MI control route under its locked data-access rules.
3. Pin and archive the author repository revision before any local benchmark; do not cite mutable `main` as a reproducible code version.
4. Add DeESI as a matched comparator only where its objective and assumptions can be made comparable; distinguish an inapplicable baseline from a poor-performing baseline.

**Assessment:** DeESI is very close prior art for Localize-MI pulse-localization: it validates against known stimulation locations in seven hdEEG/SEEG participants with MRI, compares a broad method set, and includes debiased amplitudes, inferential statistics, and PSF/CTF diagnostics. It does not establish a robust source-family identified set under explicit forward-operator uncertainty for later physiological CCEPs in WSGZP. That is a different target and dataset, not a novelty result; its decision value remains unproven.
