# B8 development-candidate wheel provenance and parity

**Date:** 29 October 2026\
**Candidate:** `observable-geometry 0.1.3.dev0`\
**Status:** PASS for byte-level wheel/source provenance and one sealed model-only CLI parity run. This is an unreleased worktree candidate; B8 remains open.

## Why this candidate has a new version

Two preserved wheel artifacts previously carried version `0.1.2` despite
different contents: the 24 October release-check wheel and a later 29 October
worktree wheel. The records are historical and remain unchanged. To avoid
shipping a different build under the same version, the current working-tree
candidate is labeled `0.1.3.dev0` in package metadata and README. It is not a
public release and does not close the clean-commit or external-review gates.

## Source and wheel check

An isolated build stage was assembled from the current `pyproject.toml`,
README, BSD-3-Clause license, and complete `src/observable_geometry` tree. The
wheel was built with:

```powershell
python -m pip wheel --no-deps --wheel-dir <candidate-wheelhouse> <candidate-source-stage>
```

Wheel SHA-256:
`50793f8864d57089ea489bf142d8d377447f0409a66377b09ee57126a4b01c98`

The byte-level verification passed all checks: the source file set matches
the checkout, all 18 Python modules match the source stage and wheel, staged
README/license/project metadata match the checkout, the wheel metadata reports
`0.1.3.dev0`, and the BSD-3-Clause license expression and packaged license
file match. The machine-readable report is
`outputs/track_b/20261029T_release_candidate_013d/wheel_source_verification.json`.

## Discarded build attempts

The first attempt could not run `python -m build` because the build frontend
was not installed. The second used pip without build isolation and failed
because `setuptools.build_meta` was absent from the active environment. A
third attempt produced a wheel, but the source verifier correctly rejected it:
the staging command flattened `observable_geometry` under `src`, so its module
set did not match the actual package layout. That discarded wheel has SHA-256
`f0d12763ad94017058a4340eb0d04715893e8eed2c268ce760622ee907b680c7` and is
preserved with its failing report in
`outputs/track_b/20261029T_release_candidate_013c/`. It was not installed,
used as a result, or included as the candidate. The corrected `013d` stage
uses `src/observable_geometry/` and passes the same verifier.

## Clean-install and output parity

The wheel was installed with declared dependencies in a newly created Python
3.12.14 environment. Installed package version was `0.1.3.dev0`; NumPy was
2.5.4 and SciPy was 1.18.1. The package imported from that environment's
`site-packages`. The installed console command used the already-exported
sealed sub-01 forward-model bundle and metadata, not EEG samples, and produced
the same outputs as the established 0.1.2 clean-wheel reference:

- 40,980 ranked source pairs; CSV SHA-256
  `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`.
- Every stored score array matched exactly; `scores.npz` SHA-256
  `bbc74660d069419ce199c6fd9a86f0f11f7fc52c92f5c93bbcc91ba5684b58c1`.
- Summary metrics matched exactly; median best distant absolute cosine was
  `0.915556984605132`, covariance rank was 235, and 6.0395% of best distant
  similarities were at least 0.95.
- The candidate run manifest records the same model bundle and metadata
  hashes, output hashes, exact allowlisted key access, and no signal-array
  access. Run-manifest SHA-256:
  `ff55849fcd6cc6db7884e6ad465427a1d4ca1038eba0fc8b9b2edcf4f6d13535`.

The source-stage check is
`outputs/track_b/20261029T_release_candidate_013d/wheel_source_verification.json`.
The verifier's default-path replay also passes at
`outputs/track_b/20261029T_release_candidate_013d/wheel_source_verification_rerun.json`.
The clean-install CLI output is under
`outputs/track_b/20261029T_release_candidate_013d/candidate_cli/`; its parity
report is
`outputs/track_b/20261029T_release_candidate_013d/candidate_cli_parity.json`.
The output verifier is `scripts/track_b/verify_b8_atomic_cli_reproduction.py`.
`scripts/track_b/verify_b8_candidate_installation.py` independently checks
that the installed package version and every installed module match this
wheel, then checks the linked parity and model-only access evidence. Its
passing report is
`outputs/track_b/20261029T_release_candidate_013d/candidate_installation_verification.json`.
An additional hardened replay binds the candidate run's implementation hash to
the installed `cli.py`, re-hashes every run output against its manifest, and
requires every parity subcheck to pass. It also passes at
`outputs/track_b/20261029T_release_candidate_013d/candidate_installation_verification_replay_002.json`.

## Reproduction commands

From the repository root, use the checked-in source-stage and wheel paths
below. The output path must be new because the verifier refuses to overwrite
reports.

```powershell
.venv\Scripts\python.exe scripts/track_b/verify_b8_wheel_source.py `
  --stage outputs/track_b/20261029T_release_candidate_013d/source `
  --wheel outputs/track_b/20261029T_release_candidate_013d/wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl `
  --expected-version 0.1.3.dev0 `
  --output outputs/track_b/20261029T_release_candidate_013d/wheel_source_verification_rerun.json

.venv\Scripts\python.exe scripts/track_b/verify_b8_atomic_cli_reproduction.py `
  --candidate outputs/track_b/20261029T_release_candidate_013d/candidate_cli `
  --output outputs/track_b/20261029T_release_candidate_013d/candidate_cli_parity_rerun.json

.venv\Scripts\python.exe scripts/track_b/verify_b8_candidate_installation.py `
  --python outputs/track_b/20261029T_release_candidate_013d/clean_env/Scripts/python.exe `
  --wheel outputs/track_b/20261029T_release_candidate_013d/wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl `
  --parity outputs/track_b/20261029T_release_candidate_013d/candidate_cli_parity.json `
  --output outputs/track_b/20261029T_release_candidate_013d/candidate_installation_verification_replay_003.json
```

## Limits

This verifies wheel contents and reproducible behavior for one participant's
sealed model-only input. It does not verify biological source truth, measured
endogenous neural source recovery, calibrated uncertainty, researcher utility,
novelty, or generalization. The same-model exact match is a packaging and
software regression result. Independent unaffiliated review and a clean,
commit-bound rebuild remain necessary before a release-ready B8 decision.
