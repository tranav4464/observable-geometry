# HDEEG published-overlap and remainder feasibility addendum

**Date:** 24 October 2026  
**Scope:** Published cohort counts and methods only; no EBRAINS registration, signal-array access, participant-level outcome inspection, or reanalysis.  
**Gate effect:** Clarifies B4 feasibility; does not reopen B4 or authorize B5/B6.

## Verified published facts

The HDEEG data descriptor reports a final release of 44 participants, including 30 with favourable 12-month seizure outcomes and 14 with unfavourable outcomes. It also states that one participant with an unfavourable outcome (#39) is retained in the release despite being removed from that descriptor's analysis because EEG source imaging was performed after an earlier surgery. The release includes averaged interictal EEG, participant-specific preprocessed MRI, electrode coordinates, postsurgical imaging, and clinical information. Only averaged, heterogeneously filtered EEG is available; the original raw EEG and single-discharge trial counts for four participants are unavailable. The dataset has no simultaneous intracranial EEG ground truth.

The GBF preprint reports its resection analysis on 24 favourable-outcome patients after excluding cases that failed EEG or resection-mask quality control. It does not report a complete public participant-ID crosswalk for those 24 in the main text.

Therefore, **20 of the 44 released participants were outside the reported GBF resection-analysis sample by count**: 14 with unfavourable outcome and six favourable-outcome participants not included in the reported 24-person analysis. This arithmetic does not establish that all 20 are usable, outcome-independent, or suitable for a confirmatory evaluation. In particular, the six favourable cases may have been excluded by the GBF quality-control criteria. The 14 unfavourable cases were outside the published GBF analysis by design, but resection location alone is a weaker source reference when surgery did not yield seizure freedom.

The 20-person remainder is from the same clinical cohort and data release. It is **not an external cohort** and must not be described as independent external validation. The cohort has also supported earlier source-localization studies, as documented by the data descriptor. At most, the remainder could be considered for a separately reviewed, participant-held-out secondary analysis of a carefully bounded endpoint after identity, quality, and data-use checks.

## Feasibility consequence

The published counts correct an overbroad statement in the original HDEEG reopening assessment that any unoverlapped portion must simply be smaller than the already analyzed set. A potential complement of 20 exists by cohort counts, but the scientifically usable sample is unresolved and could be substantially smaller. The main constraints remain:

1. **No exact overlap crosswalk in the inspected main text.** The participant IDs in the 24-person GBF analysis must be mapped to the release before defining a complement. That mapping must not be inferred by examining outcomes or source results.
2. **Quality exclusions may explain the six omitted favourable cases.** They cannot be assumed eligible without an outcome-blind QC audit.
3. **The 14 unfavourable cases cannot be treated as straightforward source-localization ground truth.** A source lying outside resected tissue in a patient with persistent seizures does not prove the source estimate was wrong; the epileptogenic network may be broader or the surgery incomplete.
4. **The frozen B2 covariance contract is not automatically met.** The release supplies averaged epochs rather than repeated single discharges. Constructing a channel covariance from time samples of one filtered average would be a new assumption and must not be silently substituted for the development covariance. A separately reviewed dataset-specific covariance adaptation may preserve the mathematical estimand only if it is explicitly specified and validated before held-out outcomes are accessed.
5. **The effective sample is too uncertain for incremental-prediction claims.** Even the nominal 20-person complement is small for a multi-covariate claim that ambiguity adds value beyond depth, amplitude, coverage, and standard resolution measures. Participant-level precision and a simpler estimand must be assessed before considering any run.

The correct gate decision remains **B4/B5/B6 PIVOT**. The update supports keeping HDEEG on a narrowly scoped candidate list; it does not establish a viable confirmatory route, a novel method, or any empirical result. Do not access participant signal arrays or held-out outcomes under the present authorization boundary.

## Primary sources

- Vorderwülbecke et al. (2025), *High-Density EEG Source Localisation of averaged interictal epileptic Discharges validated by surgical Outcome*, [Scientific Data](https://doi.org/10.1038/s41597-025-05740-z), especially Methods, Data Records, Usage Notes, and limitations. The article states that the release has 44 participants (30 favourable, 14 unfavourable), includes one retained case removed from the descriptor's analysis, provides averaged EEG only, and requires EBRAINS registration and acceptance of data-use terms.
- Wang et al. (2026), *A geometry aware framework enhances noninvasive mapping of whole human brain dynamics*, [arXiv:2604.25592](https://arxiv.org/abs/2604.25592), especially Results §2.6 and Methods §4.7. The paper reports GBF resection analysis on 24 favourable-outcome participants after EEG or resection-mask quality exclusions.

