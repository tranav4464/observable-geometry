# B8 commit-bound candidate build and parity

**Run date:** 29 October 2026  
**Source commit:** `db98529f4590bb7d9ce4ff6f31b977b29b56ac3a`  
**Package:** `observable-geometry 0.1.3.dev0`  
**B8 status:** Candidate verification passes; B8 remains open pending an unaffiliated external reproduction/review and a release-version decision.

## Build provenance

The wheel was built from a Git archive of the source commit, not from an
uncommitted package tree. The candidate is
`outputs/track_b/20261029T_commit_release_db98529/wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl`
with SHA-256
`bb3c21a9955896bae5c8314a447559e1d685b42bd28f45eb5ddba2ce8cdddcb4`.
The source verifier passed all checks: 18/18 Python modules match the wheel,
the wheel matches the commit archive, the package version is correct, and the
BSD-3-Clause metadata and license file match. It normalizes CRLF to Git's
canonical LF before comparing source-stage files because Git archive extraction
on this Windows environment materializes CRLF. It still checks the wheel
members against the actual staged bytes.

Machine-readable verification:
`outputs/track_b/20261029T_commit_release_db98529/wheel_source_verification.json`.

## Fresh installation and replay

The candidate was installed with declared dependencies into a fresh Python
3.12 environment (NumPy 2.5.4, SciPy 1.18.1). The installed console command
ran against the sealed sub-01 forward-model bundle and metadata, using only
the allowlisted model keys. It produced 40,980 ranked source pairs, byte-for-
byte identical CSV output, exact score arrays, and exact summary values against
the established clean-wheel reference. The installed-wheel verifier passed all
10 checks, including installed-module equality, CLI implementation provenance,
output-manifest hashes, and confirmation that no EEG signal-array key was
accessed.

Reports:

- `outputs/track_b/20261029T_commit_release_db98529/candidate_cli_parity.json`
- `outputs/track_b/20261029T_commit_release_db98529/candidate_installation_verification.json`
- `outputs/track_b/20261029T_commit_release_db98529/candidate_cli/run_manifest.json`

The commit-bound release runner for the same source commit passed 175/175
workspace tests and 173 source-archive tests, with two documented skips and no
failures. The gate-register validator passed and checked 267 evidence paths.
See `outputs/track_b/20261024_b8_release_checks/test_run_db98529.json` and
`outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_db98529.json`.

## Reproduction commands

From the repository root:

```powershell
.venv\Scripts\python.exe scripts\track_b\verify_b8_wheel_source.py `
  --stage outputs/track_b/20261029T_commit_release_db98529/source `
  --wheel outputs/track_b/20261029T_commit_release_db98529/wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl `
  --expected-version 0.1.3.dev0 `
  --output outputs/track_b/20261029T_commit_release_db98529/wheel_source_verification_replay_001.json

.venv\Scripts\python.exe scripts\track_b\verify_b8_atomic_cli_reproduction.py `
  --candidate outputs/track_b/20261029T_commit_release_db98529/candidate_cli `
  --model-export outputs/track_b/20261029T_atomic_cli_real_model_reproduction/model_export `
  --clean-install-check outputs/track_b/20261024_b8_release_checks/clean_install_parity.json `
  --output outputs/track_b/20261029T_commit_release_db98529/candidate_cli_parity_replay_001.json
```

The original fresh-environment installation command and installed-wheel
verification report are retained in the run directory; the environment is
available at `outputs/track_b/20261029T_commit_release_db98529/clean_env/`.

## Interpretation and limits

This is a reproducible package build and one-model software parity result. It
does not establish that a scalp source map is physiologically correct, that
the diagnostic improves a researcher decision, that the model generalizes
across people, or that the method is novel. B4–B7 remain pivoted; measured
endogenous source recovery and a novel-method advantage remain unproven. B8
also remains open until an unaffiliated reviewer independently reproduces or
reviews the commit-bound artifacts and the project chooses a release version.
