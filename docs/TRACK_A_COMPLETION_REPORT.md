# Track A Foundation Build: verification and closeout

> **Status: accepted as a verified engineering and exploratory foundation for Track B research.** The acceptance is bounded to the declared one-participant Localize-MI pulse-artifact benchmark. It does not establish physiological source recovery, population performance, a calibrated recoverability measure, or novelty of Recoverable Source Geometry.

**Verified:** 22 October 2026
**Run:** `tracka_verified_20261022_final`
**Evidence:** `outputs/tracka_verified_20261022_final/run_manifest.json` and the offline report in the same folder.

## What Track A establishes

Track A now has a reproducible, version-pinned software foundation that integrates the pinned GBFs implementation with Localize-MI, compares it with a fixed MNE minimum-norm baseline, and measures nominal source-signature similarity across the complete 8,196-vertex cortical grid. The pipeline validates the data contracts, checks an independent GBFs algebraic implementation against the upstream routine on matching inputs, evaluates the declared benchmark, produces offline reports, and seals inputs, source files, and outputs in a run manifest.

The benchmark target is the midpoint of the known intracranial stimulation contacts for the measured electrical pulse artifact. It is not the distributed physiological response after the pulse, spontaneous activity, or a general neural source. All eleven runs and six primary sites come from participant sub-01 and remain development data.

## A0–A7 closeout

| Gate | Status | Verified evidence and boundary |
|---|---|---|
| A0: design freeze | Pass for the declared proxy task | Target, −2 to +2 ms window, source family, nuisance handling, fixed comparisons, and development-only split are frozen in `FOUNDATION_DECISIONS.md` and `FOUNDATION_PROTOCOL.md`. Fixed cortical-normal orientation is retained as a model assumption, not validated as the physical direction of the stimulation artifact. |
| A1: environment and provenance | Pass | Python 3.12.14 virtual environment; 34 exact package pins; a separate empty-venv install and dependency check passed; hashed requirements, input payloads, source snapshot, artifacts, and sealed run manifest. |
| A2: physical data adapter | Pass for supplied data contracts | All eleven runs are checked for channels, units, event metadata, time grids, dimensions, trial counts, finiteness, and common channel order. Sensor positions and transforms are validated. Orientation compatibility remains a scientific limitation. |
| A3: reverse engineering and parity | Pass for stated integration scope | Pinned upstream GBFs path is retained and an independent algebraic parity check gives relative Frobenius error `2.23e-13` on identical inputs. This is not a reproduction of the GBFs paper benchmark. |
| A4: signature library | Pass | Deterministic results cover 8,196 source vertices. Invalid queries, unsupported covariance directions, absent candidates, and threshold-set behavior have regression coverage. Performance is measured and included in the report. |
| A5: ambiguity and resolution | Pass as nominal diagnostics | Complete sparse source-centered sets at the 0.95 cosine threshold, sensitivity variants, and MNE point-spread L1-mass metric are saved. They are conditional on this participant's model and covariance, not calibrated uncertainty. |
| A6: reproduction and interface | Pass | The one-command runner checks environment, tests, data, caches, analyses, reports, validator, and sealing. The cold run regenerated both 20- and 300-mode geometry caches. The offline report includes sensor-signature comparison. |
| A7: evaluation and handoff | Pass for Track A foundation freeze | Six-site descriptive evaluation, failure/limitation record, frozen protocol, reproducible API, research-gap rationale, and Track B handoff are recorded. Track B must still finish method-level novelty review and independent held-out scientific evaluation. |

## Verified development results

The six primary 1 mA sites use fixed GBFs (300 modes per hemisphere, Lambda 1.2) and fixed-orientation MNE minimum norm (lambda² = 1/9). Median peak distance to the contact-pair midpoint was 19.76 mm for GBFs and 28.30 mm for MNE. These are descriptive errors from one participant; they do not show that GBFs is superior.

Across fifteen dependent site pairs, predicted and observed pulse-artifact scalp-pattern similarity had Pearson `r = 0.345` and Spearman `rho = 0.343`. The pairs share sites, so they are not independent observations. No p-value or population/generalization claim is made. The empirical MNE covariance convention was corrected to pass single-trial baseline covariance and the actual `nave`, applying average scaling once.

For the separate run-01 nominal signature diagnostic, all 8,196 vertices have valid signatures and at least one alternative at least 20 mm away. The median best distant noise-whitened absolute cosine is 0.916, the 90th percentile is 0.945, and 6.04% of vertices have a distant alternative at or above 0.95. The full 0.95 threshold relation contains 912 directed source-to-alternative edges. Under the fixed MNE resolution diagnostic, median peak offset is 17.96 mm and median point-spread L1 mass within 10 mm is 3.41%. These are model-conditional diagnostics, not biological accuracy or calibrated recoverability.

## Audit findings and remediation

The original audit reproduced five adversarial software failures and several missing deliverables. They were addressed as follows:

- Signature handling now masks invalid source rows and columns, returns explicit `-1`/NaN padding, rejects unsupported covariance-null components, and raises a clear error when no distant candidate exists.
- The validator now rejects non-finite or inconsistent row-level results, recomputes summaries and signature outputs from saved inputs, checks cache identities and complete threshold relations, and detects modified artifacts after sealing.
- Geometry caches are bound to the forward model, upstream code, source geometry/order, mode count, and configuration. A fresh run regenerated 20- and 300-mode caches.
- The resolution statistic is named L1 mass, matching its absolute-amplitude computation. The observed artifact topography uses the predeclared-window sample with maximum GFP rather than a signed average that could cancel waveform phases.
- All eleven run metadata and data arrays are checked before evaluation. The MNE covariance/nave scaling is explicit and applied once.
- The report now includes the sensor-signature comparison, performance measurement, orientation caveat, and complete 0.95 ambiguity export. The clean pinned environment includes the report renderer dependency.
- Run outputs are uniquely named and immutable after sealing. The verified run has 20 passing tests, a 34-package pinned environment, a cold-cache end-to-end execution, and two consecutive validator PASS results.

The detailed historical findings and their closure mapping remain in [the audit record](TRACK_A_AUDIT_2026_10_22.md). The original findings are preserved as the state observed before remediation; the closeout section records what changed and what remains open.

## Remaining scientific limits and failures

Track A is verified as software and a narrowly scoped development benchmark. The following points are still open and must be treated as limits, rather than hidden by the completion status:

- **Orientation compatibility:** a geometric comparison found 44.4°–87.6° between the contact-pair axes and nearest fixed cortical normals at the six sites. A contact-pair axis is only a geometric proxy for artifact current, so the angles neither prove nor disprove the model. The fixed-normal cortical inverse is not established as a physically faithful model of the pulse artifact. Track B needs a task-appropriate orientation/forward model or must retain this proxy boundary.
- **Ground truth scope:** contact midpoint is a reference for the electrical pulse artifact; it is not ground truth for a physiological source map.
- **Sample size and dependence:** one participant, six sites, and fifteen dependent pairs cannot establish generalization, statistical significance, calibration, or population reliability.
- **Forward uncertainty:** the nominal analysis uses one supplied participant-specific forward model. Sensitivity variants are not a justified probability distribution over head models.
- **Novelty:** existing resolution-matrix, robust inverse, and adaptive-parcellation approaches overlap with the proposed question. Track A identifies a plausible research gap in empirical calibration and prediction of task-specific source confusion under defensible model variation, but does not prove that gap is novel.
- **Source-control history:** this workspace is not a Git repository, so it has no commit history or tag. The sealed source ZIP and SHA-256 manifest identify the exact verified snapshot, but do not replace collaborative version history.
- **Visual QA:** HTML content, report assets, and static integrity were checked. Automated browser interaction and cross-browser visual certification were not performed.

## Track B entry condition

Track B may begin with equation-level prior-art comparison, task validity, dataset feasibility, and a preregistered falsifiable hypothesis. It should test whether model-predicted source ambiguity predicts held-out empirical confusion beyond resolution-matrix, adaptive-parcellation, and robust-inverse baselines. Novelty and a new-method claim remain gated on that evidence. If calibration or baseline advantage fails, report the negative result and do not claim a new framework.

## Reproduction

From PowerShell in the project directory, bootstrap the pinned environment and dependencies with:

```powershell
.\scripts\bootstrap_foundation.ps1
```

Then run the full Track A build with:

```powershell
.\scripts\run_foundation.ps1
```

To inspect the verified result, open `outputs/tracka_verified_20261022_final/foundation_report.html`. The sealed manifest records the environment, input hashes, source snapshot, artifact hashes, run ID, and verification results.

As a separate setup check, a new temporary Python 3.12 virtual environment was created from the base interpreter, all 34 exact packages were installed from `requirements-foundation.txt`, `pip check` reported no broken requirements, and all 20 tests passed. This verifies dependency installation and unit tests independently from the cold-cache analysis run.
