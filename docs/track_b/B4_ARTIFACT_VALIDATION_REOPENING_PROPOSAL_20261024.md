# B4 artifact-bounded validation reopening proposal

**Status:** proposal for independent technical review; no signal outcomes from sub-02–07 have been opened.
**Relationship to the existing B4 decision:** the original physiological-source validation route remains **PIVOT**. This proposal asks whether a narrower, separately labelled stimulation-artifact benchmark can test one part of the software's stated sensor-geometry claim.

## Why consider this route

The current B4 failure is still valid for endogenous neural-source claims. The Localize-MI signal is an electrical stimulation pulse artifact, and the tested cortical source generator did not explain it adequately. That failure prevents interpreting the artifact result as evidence of physiological source recovery.

The dataset was nevertheless designed as a controlled benchmark for forward and inverse EEG methods: a known intracranial contact pair is electrically stimulated while scalp EEG is recorded. The original dataset paper explicitly chose the pulse artifact because the stimulated location is known more precisely than the generator of a spontaneous brain rhythm. Later work has already compared inverse methods and acquisition configurations on Localize-MI, including an eight-method, seven-participant study of electrode-loss effects. That prior work rules out a generic claim that the dataset or source-localization benchmark is new. See the [dataset paper](https://doi.org/10.1038/s41597-020-0467-x) and [Qin et al. 2026](https://doi.org/10.1109/TNSRE.2026.3688271).

The candidate question was: **does the GBF tool's nominal pairwise similarity rank which known stimulation sites yield empirically harder-to-distinguish scalp pulse-artifact patterns, and does that ranking add information beyond distance and standard MNE point-spread diagnostics?** The metadata audit below shows that this dataset cannot support the planned held-out participant-level test with adequate independent run replication and enough eligible comparisons. The question remains untested; it is not a project result or a novelty claim.

## Metadata-only feasibility evidence

The audit scripts read channel and epoch TSV metadata, electrode coordinate files, forward-model geometry and a saved geometry report. They did not load EEG/iEEG arrays or inspect waveform values.

| Participant | Runs | Epoch metadata rows | Stimulation contact pairs | Good EEG channels common across runs | Forward sources | Max sensor-coordinate mismatch (mm) | Max contact-midpoint to nearest cortical vertex (mm) | ≥20 mm source-proxy pairs also shared at ≥2 intensities |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| sub-01 | 11 | 389 | 6 | 224 | 8,196 | 0.0081 | 2.72 | 7 |
| sub-02 | 6 | 277 | 3 | 190 | 8,196 | 0.0082 | 2.17 | 1 |
| sub-03 | 7 | 245 | 5 | 195 | 8,196 | 0.0081 | 2.99 | 1 |
| sub-04 | 9 | 378 | 7 | 212 | 8,196 | 0.0081 | 3.91 | 0 |
| sub-05 | 14 | 560 | 8 | 156 | 8,196 | 0.0081 | 3.12 | 12 |
| sub-06 | 7 | 281 | 4 | 169 | 8,196 | 0.0087 | 3.14 | 2 |
| sub-07 | 7 | 263 | 4 | 140 | 8,196 | 0.0081 | 2.37 | 3 |
| **Total / range** | **61** | **2,393** | **37** | **140–224** | — | **0.0087 max** | **3.91 max** | **26 (19 held-out)** |

The 37 is the sum of distinct contact pairs within participant, not 37 independent observations. Across participants there are only seven independent clusters. Each participant's scalp channel set is reduced to the intersection of channels marked good across that participant's runs; the intersection ranges from 140 to 224 channels. This may limit pair-level precision, especially for sub-07 and sub-05. Geometry metadata show close alignment for the supplied sensor and stimulation coordinates, but do not establish physiological validity or signal quality.

The last column applies both the B2 `≥20 mm` Euclidean source-proxy separation rule and the requirement that both candidate stimulation sites have runs at at least two shared intensities. Each site–intensity condition appears in only one run. Therefore a run-held-out test must train at one intensity and test at another, rather than split trials from the same run. The six untouched participants yield only 19 such comparisons, distributed 1, 1, 0, 12, 2, and 3. Only sub-05 has enough comparisons to support even a modest within-participant rank analysis. This is a material feasibility failure for the proposed six-participant confirmatory rank and top-quartile decision test.

Reproduce the metadata audit from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\track_b\audit_geometry.py --subjects 01 02 03 04 05 06 07
.\.venv\Scripts\python.exe scripts\track_b\audit_b4_multisubject_metadata.py
```

The reports are `outputs/track_b/data_acquisition/geometry_sub-01_02_03_04_05_06_07.json` and `outputs/track_b/data_acquisition/b4_multisubject_metadata_feasibility.json`. The feasibility report hashes every channel/epoch TSV and the geometry report; the geometry report hashes each participant's forward file, transforms, coordinate metadata, and epoch TSVs used to derive the nearest-source proxy coordinates.

## Candidate estimand and feasibility decision

The intended unit of inference would be a participant, not a source pair. For each participant, stimulation-site pairs would be mapped to the nearest fixed-orientation cortical source proxies under the existing geometry audit. Pairwise B2 cosine scores would use the participant-specific forward model, common-good channels, average-reference projection, noise covariance, and 20 mm exclusion rule. No held-out signals were opened and no empirical score was calculated for this proposal.

The initial idea of held-out-trial balanced accuracy using within-run folds is **rejected as a confirmatory design**. Every site–intensity condition occurs in a single run, so a split within that run cannot separate site-specific signal structure from run-specific acquisition effects. The only run-held-out option is cross-intensity transfer: train at one intensity and test at another, then reverse the direction. This leaves only 19 geometry-eligible site-pair comparisons across the six untouched participants, distributed 1, 1, 0, 12, 2, and 3. That is too sparse and uneven for the proposed participant-level rank, stable uncertainty summaries, or top-quartile decision analysis. No classifier fitting on sub-02–07 is recommended under this proposal.

The proposed outcome would have been the held-out confusion between two recorded pulse-artifact conditions, compared against B2 cosine, Euclidean distance, and a matched MNE point-spread/cross-talk measure. Any such result would concern repeatability and discrimination of this electrical probe under these recording conditions only. It could not validate endogenous neural-source recovery. The planned participant-level summary and manual-caution decision are abandoned for this dataset because the eligible comparisons fail the feasibility screen.

## Prior-art and novelty boundary

The mathematical cosine remains established leadfield-separability prior art. Forward-model uncertainty, source-resolution matrices and empirical stimulation-site localization are also established. The proposed potential contribution is the held-out, participant-level **test of whether a fixed nominal source-pair ranking predicts measured pulse-artifact discriminability beyond standard geometric and inverse-resolution comparators**, packaged with auditable channel/reference/covariance contracts. A fresh search of the exact pairwise prediction question and an independent reviewer must establish that this is a useful gap before calling it novel. Even if successful, the result supports only the controlled artifact endpoint in this dataset.

The recent Qin, Tong & Sun study (2026, [DOI](https://doi.org/10.1109/TNSRE.2026.3688271)) already uses Localize-MI's seven participants and compares eight inverse methods under electrode-loss conditions. It evaluates localization error and spatial dispersion rather than the B2 pairwise score, but is close enough that an artifact benchmark must explicitly compare its intended decision with that work. The present data structure makes the proposed cross-intensity test too sparse to establish incremental value.

Unnwongse et al. (2026, [DOI](https://doi.org/10.1016/j.eplepsyres.2026.107764)) provide adjacent prior art: they estimate region-specific error vectors from stimulation-evoked scalp localization and apply the correction to interictal epileptiform discharges. The abstract does not identify the Localize-MI cohort, so no cohort overlap is assumed. It does show that stimulation-derived empirical localization correction is already an active method, further narrowing any novelty claim for an artifact-based extension.

The proposal is **not feasible as a confirmatory six-participant test on the present dataset**. The metadata-only audit computes the nearest-source-proxy distances and applies the B2 20 mm threshold; it also exposes the one-run-per-site–intensity confound and sparse cross-intensity comparison counts. The empirical method cannot be rescued by choosing a classifier or threshold after seeing outcomes. A future reopening would require a different permitted real dataset or task with repeated independent runs per site/condition, enough source pairs per participant, appropriate physical source references, and a new prior-art review. Any new candidate protocol must be reviewed before signal access.

## Gate disposition

This proposal does not change the original B4, B5 or B6 statuses. B4's physiological-source route remains pivoted. The current artifact-only extension is also **held from outcome access and not recommended for confirmatory execution** because the run structure and eligible comparison counts fail its planned evaluation. B5/B6 remain pivoted. Reopening requires a different valid real-data endpoint and an independently reviewed, adequately powered protocol; the supplied human B2 readiness decision does not authorize this work.

## Independent reviewer questions

1. Does the one-run-per-site–intensity structure invalidate within-run trial cross-validation for the proposed site-discrimination question?
2. Are the 19 held-out cross-intensity comparisons across six participants too sparse and uneven for participant-level inference and a researcher-facing decision?
3. Does the 2026 Localize-MI eight-method study leave a distinct, useful empirical question for the B2 score, or is the overlap too close given this dataset's limits?
4. Should this artifact-only route be closed as infeasible and B4–B6 remain pivoted pending a new dataset, rather than opening any sub-02–07 signal outcomes?

Please state what you personally inspected and whether you independently checked these metadata counts. This is a request for technical feasibility review only; it grants no permission to access additional EEG/iEEG sample arrays or run an outcome analysis.
