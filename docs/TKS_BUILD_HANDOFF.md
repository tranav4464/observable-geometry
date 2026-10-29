# Observable Geometry: TKS build handoff

**Build:** Observable Geometry 0.1.3.dev0 (unreleased development candidate)  
**Scope:** GBF reproduction workflow and a nominal, participant-model-conditional EEG source-pattern diagnostic.

## The problem and the tool

EEG source imaging estimates brain activity from voltages recorded at the scalp. Different candidate source locations can produce similar predicted scalp patterns under a particular head model. Observable Geometry makes that model-based similarity inspectable: given a forward model, sensor covariance, source coordinates, and metadata, it ranks spatially separated source pairs by their normalized, noise-whitened similarity.

The intended use is a **pre-interpretation model audit**. A researcher can ask whether the supplied forward model predicts clearly different scalp patterns for two candidate locations before treating a source estimate as spatially specific. The answer is conditional on the supplied model, channel order, reference, covariance, source orientations, and candidate source family.

## A short demonstration

In the full research workspace, run the sealed Localize-MI model-only example:

```powershell
python scripts\track_b\export_sealed_model_bundle.py --output .\tmp\model_bundle_demo
observable-geometry distinguish `
  --bundle .\tmp\model_bundle_demo\model_bundle.npz `
  --metadata .\tmp\model_bundle_demo\model_metadata.json `
  --output .\outputs\track_b\tks-demo-run `
  --minimum-distance-mm 20 `
  --top-k 5
```

The command reports highly similar candidate pairs separated by at least 20 mm, their similarity scores, model/input/code provenance, and an access log. The current sealed example contains 40,980 ranked pairs from one participant-specific model. It is a **model-only demonstration**: the predicted signatures are not measured neural events, and the output is not a source-recovery score or a probability of correct localization. The model bundle is Localize-MI-derived and must remain local under that dataset's license.

For a new model, the install and input contracts are in the repository [README](../README.md). Do not use the command with an unverified forward model, inconsistent channel order/reference, or an undocumented covariance and interpret the result as empirical evidence.

## Evidence and current gate state

- B0–B3 passed at their declared, bounded scopes.
- B4–B7 were explicitly pivoted or stopped after the proposed endpoints failed to support the intended neural-source or analyst-decision claims. These are documented outcomes, not hidden completed validations.
- The exact-commit 9a88bad candidate passed 211 workspace tests, 209 source-archive tests with two documented skips, package provenance checks, fresh-environment installation, and exact one-model CLI output replay. The source archive and wheel hashes are recorded in the [B8 candidate report](track_b/B8_RELEASE_CANDIDATE_9A88BAD_20261029.md).
- The release candidate is not yet a final release. B8 remains open pending unaffiliated external review and a release-version decision; see the [review handoff](track_b/B8_REVIEW_HANDOFF_9A88BAD_20261029.md).

## What this build does not establish

It does not establish endogenous neural-source recovery, calibrated localization uncertainty, improved researcher decisions, population generalization, clinical utility, or a novel mathematical method. The normalized whitened similarity and underlying constrained-fitting ideas have substantial prior art. Current evidence does not show a distinct advantage over direct constrained fitting or established resolution methods.

The ds004752 real-recording benchmark is a separate exploratory scalp-to-intracranial prediction result, not validation of source-map recovery; its average advantage was small and uncertain. Localize-MI results concern a stimulation pulse artifact, not endogenous neural activity. WSGZP's participant-specific scalp-electrode-to-MRI registration remains unverified, so WSGZP source analysis is deferred until that geometry is validated.

## What remains before calling the TKS software build released

1. Obtain unaffiliated external review of the current hash-identified B8 packet.
2. Resolve any review blockers, if present, and rerun release checks against the final source commit.
3. Choose and record the release version, then publish the code and documentation without redistributing restricted participant data.
4. Present the tool with the bounded use case and limitations above; keep WSGZP geometry validation as a later extension.

This is a software-build completion path, not a claim that the scientific research questions or a journal-ready novelty claim are complete.
