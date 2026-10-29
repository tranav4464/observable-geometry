# Observable Geometry: next-build review actions

**Prepared:** 29 October 2026  
**Purpose:** Turn two external reviews into a practical agenda for the next build session.  
**Status:** Planning document. Reviewer suggestions below are hypotheses to evaluate, not validated findings or committed features.

## Current project position

Observable Geometry is exploratory research software for auditing model-predicted similarity between spatially separated EEG source patterns. Its current pairwise diagnostic is conditional on the supplied leadfield, covariance, channel/reference setup, orientations, and candidate source family. It is not a neural-source recovery method, a calibrated probability of localization, or a demonstrated improvement to researcher decisions. The existing handoff and release-candidate evidence remain the starting point; this plan does not replace or rewrite them.

## What both reviewers agree on

1. **The use case is understandable and potentially worthwhile:** help EEG source-imaging researchers notice distant alternatives before making spatially specific interpretations.
2. **Scientific boundaries are a strength:** preserve the distinction between predicted forward-model ambiguity and measured source-localization error.
3. **The key open issue is decision value:** show whether the diagnostic changes or improves a concrete researcher decision beyond established diagnostics.
4. **Do not overstate novelty:** whitened leadfield similarity is established mathematics; a workflow difference or extra output is not, by itself, a method contribution.
5. **Measured validation needs a defensible endpoint and geometry:** stimulation artifacts and incomplete intracranial coverage must not be presented as complete endogenous source ground truth.

## Reviewer-specific feedback to address

### Review 1

- Make the handoff self-contained about how the pairwise diagnostic relates to GBFs and whether it operates on ordinary source vertices, GBF patches, or general leadfield columns.
- Consider orientation-aware comparisons using subspace principal angles, gain-aware summaries, and ROI/parcel aggregation.
- Consider a montage/covariance sensitivity analysis and a test of whether flagged distant alternatives predict inverse-solver cross-talk beyond Euclidean distance.
- Treat these as candidate extensions. They need prior-art checks, precise definitions, and evidence of added decision value before adoption.

### Review 2

- Clarify that the pairwise diagnostic is distinct from the GBF inverse estimator.
- Compare against direct leadfield similarity and matched PSF/CTF or other established resolution measures.
- Address the practical question: what would a researcher decide differently after seeing the output?
- Prioritize ranking stability, a prespecified decision test, and a valid measured endpoint before adding algorithms.

## Next-build work plan

### 1. Tighten the project explanation

Update the short handoff so a first-time reader can tell:

- what data/model inputs the diagnostic accepts;
- whether candidates are fixed-orientation vertices, free-orientation subspaces, GBF patches, or another declared family;
- what is ranked and what the score does and does not mean;
- how this diagnostic relates to the GBF reproduction/inverse-estimation work;
- one example of a cautious interpretation and one claim the tool cannot support.

**Done when:** the handoff answers those points without needing to inspect other repository documents.

### 2. Define a researcher decision before expanding the method

Choose one practical decision with a clear action, for example whether a prespecified pair of distant ROIs should be reported as spatially distinguishable under the supplied model, or whether the analysis should be flagged for a sensitivity check. Define the inputs, decision rule, and what counts as a changed decision before running comparisons.

**Done when:** the decision can be stated in one sentence, is reproducible from recorded inputs, and does not imply a universal similarity threshold unless that threshold is justified and calibrated.

### 3. Run a matched comparison with existing diagnostics

Compare the current output against, at minimum:

- direct normalized noise-whitened leadfield similarity;
- the current Observable Geometry ranking/report;
- an appropriate PSF/CTF or other inverse-resolution baseline using a declared inverse operator and regularization;
- direct constrained fitting where the decision requires competing source explanations.

Record which outputs are mathematically equivalent, correlated, or provide different information. Use matched candidate sets, covariance, source family, and distance controls. Do not treat a numerical difference as practical superiority.

**Done when:** the comparison table and reproducible inputs show whether the tool changes the prespecified decision, and where it merely repackages an existing measure.

### 4. Check robustness of the current ranking

Test a bounded set of justified perturbations to the model assumptions, such as covariance estimation, sensor/montage selection, and source orientation, only where the available model artifacts support them. Report rank stability and cases where the conclusion changes. Do not call a perturbation range “realistic” without supporting evidence.

**Done when:** the protocol, perturbations, exclusions, and stability summaries are recorded, with clear limits on what one participant/model can establish.

### 5. Decide whether a technical extension earns its place

Evaluate the reviewers' candidate ideas in this order:

1. **Orientation-aware subspace similarity:** define the admissible orientations and compare principal-angle similarity to the fixed-orientation result. Check prior art and whether it changes the chosen decision.
2. **Gain-aware reporting:** report whitened sensitivity/norm alongside normalized similarity; derive any amplitude/SNR interpretation carefully and label assumptions.
3. **ROI/parcel or GBF-patch summaries:** define aggregation (worst case, quantiles, or another prespecified statistic) and verify that aggregation answers a researcher question better than vertex-level output.

Implement only an extension that is mathematically well-defined, has a matched baseline, and changes or clarifies the prespecified decision. Otherwise document why it was not adopted.

### 6. Select a measured-data validation route only after checking its endpoint

Before analysis, confirm data-use permissions, geometry validity, channel/reference compatibility, and whether the measured endpoint can test the claim. Localize-MI stimulation pulses may support a narrowly stated artifact/geometry or montage stress test, but not endogenous neural-source recovery. Any endogenous validation route needs a defensible source reference and independently verified participant geometry. Do not substitute synthetic observations for measured evidence.

**Done when:** a frozen protocol names the dataset, unit of split, endpoint, exclusions, comparator, metric, and claim boundary—or records that no currently available dataset supports the intended validation.

## Deliverables for the next build session

- Revised, self-contained handoff.
- One prespecified researcher decision and a short comparison protocol.
- Reproducible baseline comparison with a clear equivalence/added-value analysis.
- Ranking-stability report under justified assumption changes.
- Decision memo for each proposed extension: adopt, defer, or reject, with rationale.
- If a valid measured endpoint is available, a frozen validation protocol and auditable results; otherwise, a concise blocker statement and the exact evidence needed to proceed.

## Stop/go criteria

**Proceed with an extension** only if it survives prior-art review, is supported by the available model/data assumptions, and either improves a prespecified decision or supplies a defensible new guarantee.

**Keep the contribution at the software/workflow level** if the comparisons show equivalent decisions to established measures or if measured validation is unavailable. This is a valid outcome; do not force a novelty claim.

**Reconsider the project question** if no feasible measured endpoint can test the intended researcher decision, or if the output does not add actionable information beyond the matched baselines.

## Claim language to preserve

Until stronger evidence exists, describe outputs as **model-conditional predicted scalp-pattern similarity/ambiguity**. Do not describe them as proof of true source identity, reliable localization, endogenous source recovery, clinical utility, generalization across participants, or a novel method.
