# Observable Geometry: reviewer quick start

Thank you for reviewing Observable Geometry. This is a bounded computational-neuroscience software build for auditing **model-predicted EEG source ambiguity before interpreting an inverse estimate**.

## The two-minute explanation

Different candidate brain sources can produce similar predicted scalp patterns under the same head model, reference, sensor set, and noise covariance. Observable Geometry takes those declared model inputs, excludes nearby candidates, and ranks the most similar distant alternatives. It exports the actual pairs, scores, provenance, hashes, and an access log so the result can be inspected rather than accepted as a black box.

The delivered `distinguish` diagnostic is separate from the reproduced GBF inverse workflow. Its normalized noise-whitened similarity is established mathematics, not a claimed new formula. The current contribution is the auditable software workflow and its bounded model audit. It does not establish neural-source recovery, clinical utility, or a novel inverse method.

## Five-minute review path

1. Read the [TKS submission overview](submission.md).
2. Inspect the [demo guide](demo.md) and [input/output contract](../../README.md#run-the-researcher-facing-diagnostic).
3. Review the [end-to-end acceptance audit](../reviews/user-acceptance-review-2026-10-30.md).
4. Check the [B8 acceptance and limits](../track_b/B8_PASS_20261030.md).
5. Open the repository presentation at [`index.html`](../../index.html).

## Reproduce the public software checks

Python 3.12 or later is required.

```powershell
git clone https://github.com/tranav4464/observable-geometry.git
Set-Location observable-geometry
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[test,research-audit]"
.\.venv\Scripts\python.exe -m pytest -q -ra
.\.venv\Scripts\observable-geometry.exe --help
```

The public source checkout intentionally excludes licensed model arrays, participant recordings, ignored workspace outputs, and the WSGZP dataset. Therefore, two source-only skips are expected: the full-workspace gate-evidence integration and local WSGZP audit. The remaining public tests must pass.

## Questions where feedback would help

1. Is the pre-interpretation model-audit use case clear and worthwhile?
2. Would explicit distant alternatives change how you report or follow up a spatial EEG result beyond existing leadfield-similarity and PSF/CTF summaries?
3. Which next extension has the strongest scientific value: orientation-subspace ambiguity, gain/SNR-aware distinguishability, parcel/patch summaries, or a held-out decision test?
4. What independently verified measured endpoint would you require before trusting a stronger scientific claim?

## Current evidence boundary

- The public software, clean installation, commands, tests, documentation, packaging, and hashes have been exercised end to end.
- The Localize-MI demonstration is conditional on one participant-specific model and an electrical stimulation pulse artifact.
- B4 through B7 are explicit pivots because available evidence did not support physiological recovery or decision-benefit claims.
- B8 passed under the project's disclosed owner-accepted AI reproducibility criterion; external human review remains deferred.
- WSGZP participant-specific source analysis remains blocked pending registration provenance and reviewed geometry QC.

Please treat this as exploratory research software with unusually explicit guardrails, not as a validated clinical or source-recovery system.
