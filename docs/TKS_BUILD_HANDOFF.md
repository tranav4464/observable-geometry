# Observable Geometry: TKS build handoff

**Build:** Observable Geometry 0.1.3.dev1 (owner-accepted TKS snapshot at commit 3c99ca1; no stable package publication implied)
**Scope:** A traceable GBF reproduction workflow plus a separate, nominal, participant-model-conditional EEG source-pattern diagnostic.

## The problem and the tool

EEG source imaging estimates brain activity from voltages recorded at the scalp. Different candidate source locations can produce similar predicted scalp patterns under a particular head model. Observable Geometry makes that model-based similarity inspectable: given a forward model, sensor covariance, source coordinates, and metadata, it ranks spatially separated source pairs by their normalized, noise-whitened similarity.

The intended use is a **pre-interpretation model audit**. A researcher can ask whether the supplied forward model predicts clearly different scalp patterns for two candidate locations before treating a source estimate as spatially specific. The answer is conditional on the supplied model, channel order, reference, covariance, source orientations, and candidate source family.

The pairwise `distinguish` diagnostic is **separate from the GBF inverse estimator**. It accepts a sensor-by-candidate-pattern leadfield and compares its columns; it does not construct GBF patches or estimate active sources. In the sealed Localize-MI demonstration, columns represent fixed-orientation cortical source vertices. A caller may supply another declared source-pattern family, but must document how those columns were constructed. The diagnostic reports pair rankings and scores, not an inverse solution or a calibrated decision threshold.

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
- B8 passed on 30 October 2026 under owner-accepted AI reproducibility: fresh installation, 213 workspace tests and 211 archive tests with two expected skips, exact 40,980-pair replay and independent numerical calculation. External human review is deferred under a documented acceptance amendment. See [B8 decision](track_b/B8_PASS_20261030.md).

## What this build does not establish

It does not establish endogenous neural-source recovery, calibrated localization uncertainty, improved researcher decisions, population generalization, clinical utility, or a novel mathematical method. The normalized whitened similarity and underlying constrained-fitting ideas have substantial prior art. Current evidence does not show a distinct advantage over direct constrained fitting or established resolution methods.

The ds004752 real-recording benchmark is a separate exploratory scalp-to-intracranial prediction result, not validation of source-map recovery; its average advantage was small and uncertain. Localize-MI results concern a stimulation pulse artifact, not endogenous neural activity. WSGZP's participant-specific scalp-electrode-to-MRI registration remains unverified, so WSGZP source analysis is deferred until that geometry is validated.

## Outreach feedback and next build

Two reviewers found the exploratory pre-interpretation use case clear and worth considering. They emphasized that the next scientific step is to show what decision the output changes beyond direct leadfield similarity and established PSF/CTF or other resolution diagnostics. One reviewer also suggested clarifying the relationship between the diagnostic and GBFs; the distinction is stated above. Suggested orientation-aware, gain-aware, and parcel-level extensions remain candidates, not implemented or validated improvements. The detailed next-build agenda is in [NEXT_BUILD_REVIEW_ACTIONS.md](NEXT_BUILD_REVIEW_ACTIONS.md).

These comments are useful outreach feedback, but they are not a formal B8 pass or an independent clean reproduction of the release candidate. B8 was subsequently accepted on the separately executed AI audit under the documented amendment; these outreach comments themselves do not establish reproduction.

## Accepted TKS snapshot and next work

The accepted snapshot is `3c99ca1`, version `0.1.3.dev1`. [B8 PASS](track_b/B8_PASS_20261030.md) records the owner's amended software acceptance criteria. External human reproduction, WSGZP geometry verification and scientific extension remain next-build work. A stable-version rebuild or public package release would require its own artifact checks; neither is implied by this snapshot acceptance.

Current maintenance verification: [remediation re-review](TKS_REMEDIATION_REVIEW_20261030.md). The original B8 acceptance artifact remains preserved; this update repairs provenance and packaging without changing numerical scores.
