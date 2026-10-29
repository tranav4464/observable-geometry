# Observable Geometry B8: executed AI reproducibility audit

Date: 30 October 2026 (Asia/Calcutta). Reviewer: OpenAI GPT-6 Astra, executing through Codex in Tranav's existing project chat. Candidate: `58570b8738080efd6c94b7e44eb5d89f83343be9`. Package: `0.1.3.dev0`.

**Recommendation: PASS for the tested AI software/model-output reproducibility scope.**

This is a newly executed audit, including the participant-model run. It is not an unaffiliated external human review. I inherited the project conversation, used the owner's machine and owner-supplied model files, and have no institutional affiliation or human signature. Computational independence here means fresh execution and a separately written numerical checker; it does not mean organizational independence. B8's external-review requirement is not fulfilled by calling this report independent, and the gate register has not been changed.

## Personally executed

| Check | Result |
|---|---|
| v4 ZIP CRC and manifest | PASS; all 11 manifest-listed artifacts verified |
| Source archive versus Git candidate tree | PASS; exact file inventory and bytes |
| Wheel RECORD, committed modules, installed modules | PASS; all 18 Python modules agree |
| Fresh venv installation | PASS; system site packages disabled; dependencies newly installed into the venv, using pip's cached distributions where available |
| Dependency consistency | PASS; pip check found no broken requirements |
| Full extracted source test suite | 209 passed, 2 expected skips; no manual MNE preimport |
| Two skipped cases with local workspace evidence | 2 passed separately; this supplement depends on local evidence/data and is not a portable archive-only test |
| Fresh installed-wheel participant-model CLI | PASS; 8,196 sources, rank 235, 40,980 ranked rows |
| Reference comparison | Exact CSV bytes, all nine score arrays and full summary agree |
| Independent all-source numerical calculation | All candidate rankings, eligible counts and validity flags match |
| Input/output hashes and runtime access log | PASS; four approved model keys only |

Environment: Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1, pytest 9.2.0, MNE 1.13.2, nibabel 5.4.2, h5py 3.16.0. The resolved dependency list and installation logs are saved alongside this report. Fresh venv does not mean a new OS or different host.

The two archive skips were the repository gate-evidence validator and the local WSGZP geometry-status test. The latter only asserts that geometry remains marked as requiring review; its passing result does not validate WSGZP registration. The supplemental test reads local geometry/MRI metadata, not recorded EEG samples.

## Participant-model replay

The supplied model-only Localize-MI derivative was available locally under the user's authorized audit access. Its export manifest records CC BY-NC-SA 4.0 provenance. I used it locally without redistribution; this report does not independently adjudicate licensing or revalidate original participant consent. The NPZ inventory contains exactly leadfield, noise_covariance, coordinates_m and source_ids. No EEG/iEEG recording sample arrays were opened for this replay.

The installed CLI was invoked from outside the source tree with PYTHONPATH removed. Installed module bytes were checked against the wheel and committed source. The result was compared directly with the existing candidate reference files; their recorded PASS labels were not used as proof of the new execution.

A new checker, `replay_check.py`, independently recomputed all source rankings using SciPy's `eigh(driver='evd')`, a different block size (257), `cdist`, and stable sorting. It imports no project numerical function. Rankings and candidate counts matched exactly. Maximum cosine difference: 2.1094237467877974e-15; maximum profiled-residual difference: 4.2188474935755949e-15. Criteria were absolute score tolerance 1e-10, residual tolerance 1e-9, norm relative tolerance 1e-10, and exact integer/mask agreement, set in the checker before execution. This is a second implementation of the same established calculation, not a new scientific method.

Reproduced summary: median best distant absolute cosine 0.915556984605132; 90th percentile 0.9453457802989496; fraction at least 0.95 is 0.06039531478770132; fraction at least 0.99 is zero. These describe one modeled source family and covariance.

## Hashes

| Artifact | SHA-256 |
|---|---|
| v4 review ZIP | `9b9c6414569e6e21dd2bc4f68225e5a67f5bfa1ef797299ad9d5922777d72a11` |
| Reviewed wheel | `3d38d857afd015630ae55283a24512132e6c444077fc97f971b98d410eb43c56` |
| Packet source ZIP | `9ec5daca87af0fa9a27838d20ce3c412d50f912d89cdf8d31768583965067b02` |
| Model bundle | `e4116465c9af32ddf4bf9e0d3a8e92428c6f1b0bce22a5db257b1c3eaf07a32f` |
| Model metadata | `a4d52521ddb760114ba1ce740942bc3bb6232f919de62737d345beb7c48db865` |
| Reproduced ranked CSV | `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4` |
| Reproduced scores NPZ | `bbc74660d069419ce199c6fd9a86f0f11f7fc52c92f5c93bbcc91ba5684b58c1` |
| Reproduced summary | `6e33d22df83170fe0c64b6fff94e363b86741f24521b4ffa1523864853034155` |

Runtime access logs and run manifests contain fresh timestamps and paths, so their bytes need not match earlier executions. Their own recorded output hashes were checked against the new files. Access logging is application-level evidence, not an OS sandbox or proof about historical executions.

## Differences and failed audit attempts

No product numerical discrepancy or test failure occurred in the successful executions. The first pip attempt used an incorrect path to a wheel that had not yet been extracted; it failed before installation. The retry used the extracted v4 packet and succeeded. The first independent checker attempted NaN-aware equality on string source IDs and raised TypeError. I corrected only the audit checker to use dtype-appropriate equality. The initial log and successful retry log are both retained. No candidate source was modified.

## Inspected rather than independently established

I inspected START_HERE, the numerical implementation, access handling, export metadata and supplied reference evidence. I did not recreate the original forward model/covariance from raw recordings, reverify MRI-to-electrode registration, redo all historical Track A/B scientific experiments, or independently download/reconstruct the licensed derivative. The original export's historical no-signal-use record remains documentary evidence. Model-output reproducibility does not establish physiological recovery, novelty, researcher decision benefit or cross-participant generalization.

## B8 disposition

The previously missing model-output execution has now been performed by this AI auditor and independently recalculated within the same host. That supports PASS for this requested AI reproducibility scope. B8 as an external-review gate remains open unless its owner transparently changes the acceptance criterion or obtains the required external review. This report cannot establish the stronger claim of unaffiliated reproduction on another machine or end-to-end recreation without owner-provided model state. No release criterion was weakened during this audit.

## Commands and retained evidence

```powershell
# Run from the repository; $audit is outputs/track_b/astra_b8_audit_20261030 (absolute).
git archive --format=zip --output="$audit/pinned_source.zip" 58570b8738080efd6c94b7e44eb5d89f83343be9
Expand-Archive "$audit/pinned_source.zip" "$audit/source"
.venv/Scripts/python.exe -m venv "$audit/env"
# Extract the v4 ZIP to $audit/packet first.
& "$audit/env/Scripts/python.exe" -m pip install --disable-pip-version-check "$audit/packet/wheel/observable_geometry-0.1.3.dev0-py3-none-any.whl" pytest h5py mne nibabel
& "$audit/env/Scripts/python.exe" "$audit/check_integrity.py"
& "$audit/env/Scripts/python.exe" -m pip check
& "$audit/env/Scripts/python.exe" -m pip freeze
$env:PYTHONPATH="$audit/source/src"
Set-Location "$audit/source"
& "$audit/env/Scripts/python.exe" -m pytest -q -ra --junitxml="$audit/tests.xml"
Remove-Item Env:PYTHONPATH
Set-Location $audit
# $model = repository/outputs/track_b/20261029T_atomic_cli_real_model_reproduction/model_export
& "$audit/env/Scripts/observable-geometry.exe" distinguish --bundle "$model/model_bundle.npz" --metadata "$model/model_metadata.json" --output "$audit/model_replay" --minimum-distance-mm 20 --top-k 5
& "$audit/env/Scripts/python.exe" "$audit/replay_check.py"
# Supplemental tests: from the original clean pinned checkout, PYTHONPATH=<repository>/src
& "$audit/env/Scripts/python.exe" -m pytest -q -ra tests/test_track_b_gates.py::GateRegisterTests::test_current_gate_register_has_complete_evidence_and_valid_order tests/test_wsgzp_coregistration_audit.py::test_fiducial_transform_is_not_treated_as_frame_validation --junitxml="$audit/workspace_supplement.xml"
```

Evidence directory: `C:\Users\TRANAV\OneDrive\Desktop\TKS\observable_geometry\outputs\track_b\astra_b8_audit_20261030`. `integrity.json`, `replay_verification.json`, JUnit XML, logs, resolved dependencies, audit scripts and SHA-256 manifest provide machine-readable evidence. Original candidate/release inputs were left intact. New review material should not be represented as part of the pinned source commit.
