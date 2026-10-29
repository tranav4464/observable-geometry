# B8 release recheck: refreshed source snapshot

**Source commit tested:** `d38ff42611c843dc650d5bf8982902176ac41ea4`  
**Run date:** 29 October 2026  
**Outcome:** Software provenance and model-only parity pass. B8 remains open.

## Checks

- The source-only manifest covers 298 files and verifies against the clean
  commit. Report:
  `outputs/track_b/20261024_b8_release_checks/source_snapshot_verification_d38ff42.json`.
- The commit-bound workspace suite passed **175/175** tests. The extracted
  Git archive passed **173 tests**, recorded two documented skips, and had no
  failures. The skipped tests require local repository evidence outputs or
  the WSGZP dataset. Reports:
  `outputs/track_b/20261024_b8_release_checks/test_run_d38ff42.json` and
  `outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_d38ff42.json`.
- The `0.1.3.dev0` wheel was built from the commit archive. Its SHA-256 is
  `cffa86f58bb8d96be7136e882f9c962520cb2677a81f359da43fd71caa3ac6cb`.
  All 18 package modules, version metadata, and BSD-3-Clause license checks
  passed in `outputs/track_b/20261029T_commit_release_d38ff42/wheel_source_verification.json`.
- A fresh Python 3.12 environment installed the wheel with NumPy 2.5.4 and
  SciPy 1.18.1. Its CLI reproduced the established sealed sub-01 model-only
  result exactly: 40,980 ranked pairs, identical CSV bytes, score arrays, and
  summary values. The installation verifier passed all 10 checks, including
  output hashes and the allowlist showing no EEG sample access. Reports are in
  `outputs/track_b/20261029T_commit_release_d38ff42/candidate_cli_parity.json`
  and `candidate_installation_verification.json`.
- The full-workspace gate validator passed and checked 274 registered
  evidence paths. B-1 and B0–B3 remain PASS, B4–B7 remain PIVOT, and B8
  remains IN_PROGRESS.

## Interpretation

This closes a software release recheck for commit `d38ff42`. It verifies the
package and reproduces one model-only computation. It does not validate
endogenous neural source recovery, establish researcher decision benefit,
prove a novel method, or demonstrate cross-participant scientific
generalization. An unaffiliated external reproduction/review and a release
version decision are still required for B8 closure.

## Newer exact-commit candidate: 1e83192

The documentation/register commit `1e831920cb8b6d8f97078bdb66229e5598d4657e`
was also checked directly. Its committed source manifest verified cleanly
(299 files; manifest SHA-256
`da5311b51cf50c810261914b29c0e38d5d8349b521826961a19c7e10c80a6575`).
The commit-bound release runner passed 175/175 workspace tests and 173 source
archive tests, with two named skips and no failures.

A wheel built from that commit's Git archive passed all 7 source, package,
version, and license checks across 18 modules. Its SHA-256 is
`e81af2356c3856d0d71bd287d69482919b614bdbf722cbcfa660ccc2c425227f`. A fresh
Python 3.12 environment installed it and reproduced the sealed sub-01
model-only CLI output exactly: all 40,980 ranked pairs and score arrays
matched the established reference, and the output/access manifests passed
verification. No EEG signal-array key was accessed. Machine-readable results
are under `outputs/track_b/20261029T_commit_release_1e83192/`; commit-bound
test reports are `outputs/track_b/20261024_b8_release_checks/test_run_1e83192.json`
and `outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_1e83192.json`.

This closes the software verification for this source commit, not B8 itself.
The package remains a one-model nominal diagnostic. Physiological source
recovery, comparative researcher benefit, method novelty, independent
external reproduction, and a final release-version decision remain open or
unsupported.
