# B8 current release candidate: 3cfa693

**Source commit:** `3cfa693c2be6ab5866df9ae68613236fda937d0e`  
**Package:** `observable-geometry 0.1.3.dev0`  
**Status:** Current-commit package and software checks pass; B8 remains open pending independent outside review and a release-version decision.

## Build and provenance

The source archive was produced from the exact commit and tested with the guarded B8 release runner. The wheel was then built from the extracted commit archive using the declared setuptools build backend, not from the editable checkout. The source verifier passed all seven checks: the staged source file set matches, the 18 wheel modules match staged sources, the staged metadata (`README.md`, `LICENSE`, and `pyproject.toml`) matches the commit, and version/license metadata are correct.

- Source archive: `reviewer_handoff/B8_Independent_Review_20261024/observable_geometry_source_3cfa693.zip`
- Source archive SHA-256: `308b2b4e87603eadf3d58a33700f15305e160d52fab3fcac5bcb149c455c81ad`
- Wheel: `outputs/track_b/20261029T_commit_release_3cfa693/wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl`
- Wheel SHA-256: `e150582fdde3efd51c79d123dbac868431b44b3cd48528e201c0d612ae2f6f3e`
- Wheel-source verification: `outputs/track_b/20261029T_commit_release_3cfa693/wheel_source_verification.json`

## Fresh-install parity

The wheel was installed into a fresh Python 3.12.14 environment with NumPy 2.5.4 and SciPy 1.18.1. Its installed CLI ran against the sealed sub-01 model-only bundle and exactly reproduced the established clean-wheel reference: all **40,980 ranked pairs**, score arrays, and summary metrics matched. All 10 installed-package, CLI-provenance, output-manifest, and model-only access checks passed.

- Candidate CLI run: `outputs/track_b/20261029T_commit_release_3cfa693/candidate_cli/`
- Parity report: `outputs/track_b/20261029T_commit_release_3cfa693/candidate_cli_parity.json`
- Installation verification: `outputs/track_b/20261029T_commit_release_3cfa693/candidate_installation_verification.json`
- The access guard recorded only `leadfield`, `noise_covariance`, `coordinates_m`, and `source_ids`; it did not read the EEG signal array.

## Commit-bound tests and gate state

The B8 release runner on this commit passed **211/211 workspace tests** and **209 source-archive tests**, with two documented archive-only skips and no failures. The exact archive and test reports are `outputs/track_b/20261024_b8_release_checks/test_run_3cfa693.json` and `outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_3cfa693.json`. The read-only gate validator passed with 341 evidence paths; B-1/B0/B1/B2/B3 are PASS, B4–B7 are PIVOT, and B8 remains IN_PROGRESS.

The current source snapshot passed its 315-file verifier at this commit. The package does not include datasets or participant-derived model arrays.

## Interpretation and limits

This establishes exact software/package parity for one participant-specific forward model. It does **not** establish endogenous neural-source recovery, physiological validity, calibrated uncertainty, analyst decision benefit, population generalization, or a novel method. The source-pattern similarity remains established prior art. WSGZP registration remains unverified, so it does not support a participant-specific source-recovery claim.

An unaffiliated reviewer can test the source archive and wheel without the local dataset; independently replaying the model-specific numeric result requires separate authorized access to the sealed model-only bundle. B8 remains open until that review/reproduction and the release-version decision are completed.
