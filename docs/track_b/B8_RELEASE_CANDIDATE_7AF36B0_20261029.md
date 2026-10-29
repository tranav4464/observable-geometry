# B8 exact-commit release candidate: 7af36b0

**Source commit:** `7af36b0904e0b891c925a9056394c3d36acd43c2`  
**Package:** `observable-geometry 0.1.3.dev0`  
**Gate status:** B8 remains `IN_PROGRESS`; this verifies packaging and one-model numerical parity, not scientific validation.

## Verified evidence

- The exact-commit source archive passed **211/211 workspace tests** and **209 archive tests**, with two documented archive-only skips and no failures. The archive SHA-256 is `cdfd983af53941e18bcaa1d6512ee106704ef0c72fc51837dec08b58a55c4d9f`.
- A wheel built from the extracted archive passed all seven source/version/license provenance checks for the staged source set and 18 package modules.
- A fresh Python 3.12.14 environment installed the wheel with NumPy 2.5.4 and SciPy 1.18.1. All ten installation, provenance, manifest and access-contract checks passed.
- The installed CLI reproduced the established sealed sub-01 model-only result exactly: all **40,980 ranked pairs**, score arrays and summary metrics matched. The input allowlist was limited to `leadfield`, `noise_covariance`, `coordinates_m`, and `source_ids`.

## Release artifacts and reports

- Source archive: `reviewer_handoff/B8_Independent_Review_20261024/observable_geometry_source_7af36b0.zip`
- Wheel: `outputs/track_b/20261029T_commit_release_7af36b0/wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl`
- Wheel SHA-256: `d8225ab414d754d17e335968f3bef886fff277e08eb59ae8d3adfa1e1cd885c1`
- Source archive test run: `outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_7af36b0.json`
- Workspace test run: `outputs/track_b/20261024_b8_release_checks/test_run_7af36b0.json`
- Wheel source verification: `outputs/track_b/20261029T_commit_release_7af36b0/wheel_source_verification.json`
- CLI parity report: `outputs/track_b/20261029T_commit_release_7af36b0/candidate_cli_parity.json`
- Fresh-install verification: `outputs/track_b/20261029T_commit_release_7af36b0/candidate_installation_verification.json`
- Source snapshot verification: `outputs/track_b/20261029T_current_quality_audit/source_snapshot_verification_final.json`

## What this does and does not establish

This is reproducible package behavior for one sealed participant-specific forward model. It does **not** show physiological source recovery, endogenous neural-event validity, calibrated uncertainty, decision benefit, population generalization, or a novel-method advantage. WSGZP MRI-to-electrode registration is still unverified. B8 remains open pending attributable unaffiliated review and a release-version decision; the broader scientific goal additionally needs geometry-supported measured-data validation and comparative evidence of researcher value.
