# B7 decision-value audit

**Date:** 24 October 2026
**Disposition:** **PIVOT — descriptive diagnostic retained; researcher decision benefit not established.**
**Scope:** Paired, model-derived source metrics for the sealed Track A sub-01, 236-channel forward model. No EEG samples, labels, or participant outcomes were read.

## Question and result

B7 asks whether the B3 per-source best-distant forward-signature similarity offers a different and useful source-reporting decision beyond standard MNE resolution diagnostics. The available data can answer the first part descriptively, but cannot establish the second: there is one participant-specific model, no validated neural-source endpoint, and no independent researcher decision study.

The audit paired all 8,196 B3 source locations with the Track A MNE point-spread summaries. It verified exact vertex-ID order and the sealed input hashes before computing rank associations. Best-distant cosine had Spearman correlations of `0.480` with MNE peak-location error, `0.434` with absolute PSF-weighted distance, `−0.432` with PSF mass within 10 mm, and `−0.393` with the diagonal-to-peak response ratio. These are descriptive relationships among model outputs, not inferential estimates. Cortical vertices are spatially dependent, so the report includes no p-values, confidence intervals, or population interpretation.

Among the top decile of sources by best-distant cosine (cutoff `0.94535`, a data-derived descriptive grouping rather than a decision threshold), median MNE peak-location error was `27.25 mm`, compared with `17.08 mm` for the remaining sources. Median PSF-weighted distance was `48.22 mm` versus `42.11 mm`; median local PSF mass within 10 mm was `0.0191` versus `0.0370`. The two diagnostics therefore share information but are not interchangeable summaries on this model.

## Interpretation and decision

The comparison supports retaining B3 as a distinct, inspectable *pre-inversion* view of nominal forward-pattern similarity alongside the established *post-inversion* MNE resolution summaries. It does not show that the B3 output changes an analyst's source report, improves a decision, predicts actual neural recovery, or adds a novel mathematical method. The B3 cosine remains an established class of leadfield-separability diagnostic; software packaging and transparent pairing are engineering contributions.

The data needed to complete a defensible utility evaluation are absent from this route. Localize-MI's available target is a stimulation pulse artifact, not endogenous neural activity, and the single exposed participant cannot support a decision-utility or population claim. B7 therefore follows its failure route: remove utility claims, retain the bounded diagnostic, and mark B7 **PIVOT**. A future utility study would require a separately reviewed real-data endpoint, a defined reporting decision, and an independent evaluation before accessing outcomes.

## Reproduction and verification

From the repository root, using the Track A environment with NumPy and SciPy installed:

```powershell
.\.venv\Scripts\python.exe scripts\track_b\audit_b7_resolution_overlap.py
.\.venv\Scripts\python.exe scripts\track_b\verify_b7_resolution_overlap.py
```

The first command verifies sealed source hashes, confirms that B3 and MNE cite the same prepared bundle, checks the frozen MNE script and resolution-report hashes, matches the B3 source IDs to the sealed Track A vertex order, and writes the paired table and run manifest to `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/`. It refuses to overwrite an existing run. The second command independently recalculates the Spearman statistics using `scipy.stats.spearmanr`; maximum absolute discrepancy from the primary report was `1.11e-16`. The earlier `20261024_b7_resolution_overlap_audit/` run is retained as a superseded exploratory record; v2 adds the explicit model-input and MNE-script hash cross-checks.

Evidence:

- `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/b7_resolution_overlap_report.json`
- `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/paired_source_metrics.csv`
- `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/run_manifest.json`
- `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/independent_stat_check.json`
- `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/SESSION.md`
- `scripts/track_b/audit_b7_resolution_overlap.py`
- `scripts/track_b/verify_b7_resolution_overlap.py`
