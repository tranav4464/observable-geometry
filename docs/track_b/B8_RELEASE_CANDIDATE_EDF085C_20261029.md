# B8 exact-commit wheel and reviewer bundle: edf085c

**Source commit:** `edf085c07b08d3681657f164a0a9e3bb6a5ecf03`
**Package:** `observable-geometry 0.1.3.dev0`
**Status:** Software/package checks pass; B8 remains open.

## Checks performed

The wheel was built from a Git archive of the exact commit, then compared
against the source stage and commit. The verifier passed all seven checks:
all 18 Python modules match, `README.md`, `LICENSE`, and `pyproject.toml` match,
the package version is correct, and BSD-3-Clause metadata and license file are
present and consistent.

Wheel SHA-256:
`eae1bf92e97dfb7e1ae3e2239ea4f5dfc43b6aa92127274e0904d42d72162dc5`.

The wheel was installed into a new isolated Python 3.12.14 environment with
NumPy 2.5.4 and SciPy 1.18.1. Using the sealed sub-01 model-only bundle, its
CLI reproduced all **40,980** ranked pairs, score arrays, and summary metrics
exactly against the established reference. All ten installed-package,
implementation-hash, manifest, and access-boundary checks passed. The
allowlisted arrays were `leadfield`, `noise_covariance`, `coordinates_m`, and
`source_ids`; no EEG signal array was read.

The same source commit passed 181/181 workspace tests and 179 source-archive
tests with two documented skips and no failures. The 303-file source-manifest
verification passed. Machine-readable records are under
`outputs/track_b/20261029T_commit_release_edf085c/` and the commit-bound test
reports use the `edf085c` suffix.

## Reviewer handoff

The current v2 source archive, wheel, verification records, access log, and
updated scope documents are packaged in
`reviewer_handoff/B8_Independent_Review_20261029_edf085c_v2.zip`.
The archive passed CRC and per-file SHA-256 verification; its SHA-256 is
`977a4ede5fdeabc1bec4d9f8a95edbe02102c10052a106f457ca56c277b1964d`. The
earlier v1 bundle is superseded. The current bundle contains no EEG/SEEG
samples or data-derived forward-model arrays. A
reviewer needs authorized access to the sealed model bundle to independently
replay the participant-specific numeric run.

## Interpretation

This is exact package and software parity for one participant-specific model.
It does **not** establish endogenous neural-source recovery, calibrated
uncertainty, researcher decision benefit, population generalization, or a
novel method. WSGZP's coordinate/registration provenance, preprocessing
semantics, and event-level pairing remain unresolved. B4–B7 remain pivoted;
B8 remains open pending an attributable independent review/reproduction and a
release-version decision.
