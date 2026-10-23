# HDEEG-IED-SurgOutcome reopening assessment

**Assessment date:** 24 October 2026  
**Review stage:** metadata and published-method feasibility only  
**Signal access:** none  
**Decision:** candidate for a separately reviewed secondary evaluation; not yet feasible as the frozen B2 evaluation

## What this dataset contains

The 2025 data descriptor reports 44 patients, 257-channel averaged interictal epileptiform discharges, participant-specific preprocessed structural MRI, individual electrode coordinates in the corresponding T1 space, postsurgical imaging, and 12-month seizure outcomes. An older UNIGE dataset landing-page summary says 45 patients, so the release manifest and version-specific participant table must be checked before fixing any analysis denominator. The 2026 GBF paper separately reports evaluating 24 favourable-outcome participants from this same release, so the dataset is not untouched with respect to GBF source localization.

Sources: Vorderwülbecke et al. (2025), [Scientific Data](https://doi.org/10.1038/s41597-025-05740-z), especially its Data Records and limitations; the [UNIGE dataset page](https://www.unige.ch/medecine/neucli/groupes-de-recherche/serge-vulliemoz/open-science/interictal-discharges-validated-surgical-outcome-eeg-source-localisation); Wang et al. (2026), [GBF paper](https://arxiv.org/html/2604.25592), especially Section 2.6 and Methods 4.7. The article reports 24 favourable-outcome cases and an endpoint based on distance to the resection mask; this is published overlap, not independent confirmation.

## Candidate question

> Among patients whose averaged interictal EEG source estimate is compared with the resected tissue, does the frozen B2 nominal source-ambiguity score identify cases in which the scalp pattern admits strong, spatially distant alternatives, and does that score add predictive information about clinical source/resection concordance beyond source depth, signal amplitude, sensor coverage, and established resolution diagnostics?

This is a possible use of the existing B2 score, not a new mathematical method. The analysis would have to be specified at the participant level. Time points, vertices, and alternative sources cannot be treated as independent participants. An observed association would be a post-publication secondary result, not independent replication of GBF or proof of source truth.

## Feasibility blockers

1. **Prior-analysis overlap:** GBF already analyzed 24 favourable-outcome cases from this release. The exact participant identifiers in that analysis must be mapped to the dataset's `patXX` identifiers before defining any held-out cases. A different partition may not be selected after looking at outcomes.
2. **Data-use terms:** EBRAINS requires registration and acceptance of dataset-specific terms. The project has not accepted those terms or accessed the data. The data-specific license and any conditions on derived results must be inspected before acquisition.
3. **Noise model:** the release contains averaged discharges, not the original single-trial EEG. The descriptor also documents heterogeneous filtering and sampling rates. A covariance estimated from time points in one averaged epoch is not automatically an estimate of trial-level sensor noise: temporal autocorrelation, averaging, filtering, and differing numbers of events matter. The dataset paper notes that single-discharge counts are missing for four cases. A valid covariance contract compatible with B2 must be established before the frozen score is applied; substituting identity covariance or the Track A participant covariance would change the estimand.
4. **Reference interpretation:** resection and 12-month seizure outcome provide a clinically meaningful but indirect reference. Resection extent does not equal the complete epileptogenic zone, and persistent seizures can result from incomplete treatment or network disease. The outcome cannot be described as direct intracranial ground truth.
5. **Effective sample size:** the maximum cohort is 44 patients and the GBF paper has already used 24 favourable cases. Any genuinely unoverlapped portion is smaller. The sample may support descriptive or pilot estimates but may be too small to establish incremental clinical prediction with useful precision. Power and uncertainty must be assessed at the participant level before activation.
6. **Method overlap:** the broad localization task, surgical-resection reference, and GBF baseline have already been studied. The only candidate contribution is a narrowly defined, externally challenged evaluation of whether B2's ambiguity output adds predictive value beyond established diagnostics. The normalized leadfield-cosine score itself is established prior art and must not be called novel.

## Gate decision and required evidence

Keep B4, B5, and B6 at their recorded **PIVOT** status for now. Do not access signal files or participant outcomes. A reopening proposal can be submitted for independent review only after all of the following are documented:

- EBRAINS dataset terms and reuse permissions are verified from the actual dataset record;
- participant overlap with the 2026 GBF analysis is resolved from a documented crosswalk, with the held-out set fixed without inspecting its outcomes;
- a participant-level endpoint and comparator set are frozen, including the exact definition of source/resection concordance;
- the B2 covariance/noise contract can be met without changing its estimand, or a separately named and reviewed adaptation is approved;
- feasibility and statistical precision are assessed for the actual number of eligible held-out patients;
- an unaffiliated reviewer approves the protocol before outcomes are accessed.

If the covariance contract or the independent participant set cannot be established, close this candidate and retain the transparent GBFs reproduction/software release. Do not present this dataset as validation of arbitrary source recovery, whole-brain reconstruction, or a novel ambiguity metric.
