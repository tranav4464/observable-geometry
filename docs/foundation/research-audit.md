# Research and novelty audit

Prepared 21 October and updated 22 October 2026. This is a targeted audit, not an exhaustive systematic review. Code findings below refer to actual local files.

## Evidence map

| Source | What it establishes for this project | Consequence |
|---|---|---|
| [GBFs official code](https://github.com/ncclab-sustech/GBFs) | Public geometry-based inverse implementation and demo routes | Reproduce the pinned implementation before extending it |
| [GBFs earlier paper](https://arxiv.org/abs/2401.17939) | Geometric priors were already proposed for EEG/MEG inverse estimation | Geometric basis use is upstream work, not our invention |
| [Localize-MI paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC7189230/) | Known intracranial stimulation sites and scalp recordings | Physical localization test; not full physiological ground truth |
| [Localize-MI source](https://github.com/iTCf/mikulan_et_al_2020) | Public preparation and demonstration scripts | Adapt time/reference/coordinate handling explicitly |
| [Localize-MI data](https://gin.g-node.org/ezemikulan/Localize-MI) | Cloned metadata supplies prepared forwards, surfaces and epoch pointers | Files require actual annex payload retrieval and verification |
| [SESAMEEG](https://www.frontiersin.org/articles/10.3389/fnhum.2024.1359753/pdf?isPublishedV2=False) | Existing probabilistic source localization and uncertainty tooling | Uncertainty reporting alone is not novel; full implementation comparison pending |
| [Spatial fidelity study](https://pmc.ncbi.nlm.nih.gov/articles/PMC7793168/) | Existing evaluation of spatial fidelity of M/EEG estimates | Compare resolution analysis and spatial errors; do not rename existing diagnostics |
| [Objective linear resolution analysis](https://doi.org/10.1016/j.neuroimage.2022.119177) | Resolution matrices, point-spread and cross-talk functions already quantify inverse spatial behavior | RSG must not repackage inverse resolution metrics as a new certificate |
| [Adaptive cortical parcellations](https://pmc.ncbi.nlm.nih.gov/articles/PMC5864515/) | Cross-talk-based split/merge and region-growing methods already maximize parcel sensitivity and distinguishability | “Merge indistinguishable regions” is direct prior art; RSG needs a measurement-level, calibrated, model-robust distinction |
| [Bayesian uncertainty in skull conductivity](https://arxiv.org/abs/2002.00066) | Prior method incorporates conductivity uncertainty into source estimation | Model-error correction is an essential competing approach |
| [Global conductivity sensitivity, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10963400/) | Tissue conductivity changes affect forward and inverse results, with skull conductivity especially influential in the reported study | Ensemble ranges need physical provenance and spatially varying sensitivity checks |
| [Robust eLORETA](https://arxiv.org/abs/2405.05790) | A robust source method has already been proposed for geometry, conductivity, source-resolution and electrode-position errors | Robustness to a forward ensemble is not itself novel |
| [Sequential Bayesian sensor placement](https://www.eurasip.org/Proceedings/Eusipco/Eusipco2020/pdfs/0000241.pdf) | Bayesian measurement design is an established research direction | Generic variance reduction is a baseline; relevance to EEG implementation needs full-text comparison |
| [REA](https://github.com/morluto/rea) | Agent tooling for software/binary/runtime investigation | Engineering support; no direct neural-recoverability theorem or model interpretation guarantee |

Access note: PMC direct pages returned a browser challenge during this pass; earlier indexed text supplied the source summaries. The current report does not claim a fresh full-text review of these papers. The arXiv conductivity abstract and official repositories were directly inspected. The GBFs code audit and Localize-MI metadata/license checks are local, reproducible observations.

## Proposed novelty and its falsifiers

**Additional close prior art found during planning:** [Subspace electrode selection under uncertain conductivity (2012)](https://iopscience.iop.org/article/10.1088/0031-9155/57/7/1963/pdf) directly addresses electrode selection and conductivity uncertainty in EEG dipole localization. [Structural eigenmodes for EEG source localization (2026)](https://advanced.onlinelibrary.wiley.com/doi/10.1002/advs.202516802) covers another structural-mode source approach. [Temporally constraining geometric source estimates (2026 preprint)](https://arxiv.org/abs/2609.00809) addresses temporal restrictions and cross-mode coupling. [Sensor placement for noisy source separation](https://www.sciencedirect.com/science/article/abs/pii/S0165168424002792) considers spatially correlated noise and an EEG application. These records were identified from publisher/author abstracts; full method-level comparison remains open. They materially weaken any broad claim that combining geometry, uncertainty and electrode selection is new.

Until these comparisons are completed, the proposed extension is a research direction rather than a finalized invention. The current worst-case variance-reduction helper is baseline infrastructure, not evidence that this prior art has been surpassed.

Candidate: **Recoverable Source Geometry**, a GBFs-compatible, measurement-level and statistically calibrated recoverability object over a plausible forward-model family. It should predict held-out empirical confusion between source conditions and constrain downstream spatial reporting.

The claim fails if a published method already implements the same object under equivalent conditions, if calibration fails on held-out participants, if the benefit disappears against adaptive-parcellation or robust Bayesian baselines, or if the method requires hidden true locations. A convenient package may still be useful, but should then be presented as engineering/reproduction rather than a new framework.

Before freezing the algorithm, read and compare the closest four works in full. Record objective function, prior, nuisance model, calibration mechanism, decision rule, assumptions, datasets and public implementation. The minimal novelty table must contain an exact mathematical difference, a predicted benefit and a falsifying experiment for each claimed innovation. A difference in terminology is insufficient.

## Corrections to the earlier proposal

- Localize-MI's actual repository license is **CC-BY-NC-SA 4.0**, confirmed in its LICENSE and dataset_description.json. The article's open-access license does not determine the dataset license. Downloading for this research is supported; redistribution and commercial reuse require attention to the actual terms.
- GBFs' repository does not bundle the benchmark payload in Git. Its releases API lists a 405,702,052-byte `data.7z` archive containing meta-analysis maps. Those maps alone do not supply every anatomy/noise input needed by the demo.
- A large posterior variance can reflect uncertainty; small variance can still accompany model error. Neither is automatically a hallucination detector.
- Changing from monopolar to bipolar iEEG changes the target. A difference in R-squared is not a uniquely identified reference-leakage fraction.
- Correlation and normalized MAE improvement are different metrics and cannot be compared as the same numerical scale.
- A null scalp-to-iEEG result does not prove all competing methods used artifacts.
- Ordinary sequential residual fitting does not guarantee orthogonality on held-out data or identify causal physical contributions.
- Sparse-sensor rank limits apply to the specified observation/source model. They do not establish universal anatomical resolution or thought-decoding limits.
- Adding an electrode can change reference and correlated noise. The design algorithm must account for both.

## Research claims permitted today

We have cloned and inspected existing code, identified implementation and data-contract issues, and parked standard inverse-problem building blocks. We have not established RSG novelty, calibrated recoverability, a superior reconstruction method or a physiological mapping breakthrough. Those remain research questions.
