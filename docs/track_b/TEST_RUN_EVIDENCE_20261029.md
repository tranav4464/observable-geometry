# Track B software test run evidence

**Run date:** 29 October 2026

**Repository revision:** `af0d86942fdbbd346231ac07bf43078e80713c83`

**Environment:** repository `.venv`, Python 3.12.14, pytest 9.1.1

**Command:** `python -m pytest -q`

**Result:** 150 passed in 11.83 seconds

The command was run from the repository root using
`.venv/Scripts/python.exe`. The default system Python did not provide pytest;
the repository environment did.

## Independent same-day rerun

A separate rerun from the modified working tree also passed **150 tests in
6.49 seconds**. Its exact Python/pytest versions, repository HEAD, working-tree
scope, and hashes of the revised linear-span screen and focused test file are
recorded in
[`outputs/track_b/20261029T_reproducibility_full_suite_rerun/SESSION.md`](../../outputs/track_b/20261029T_reproducibility_full_suite_rerun/SESSION.md).
The rerun includes uncommitted changes, so it must not be described as a test
of the clean HEAD revision.

## Covariance-screen hardening rerun

After adding validation for the covariance eigenvalue cutoff and regression
cases for rank-deficient, indefinite, asymmetric, and zero-rank covariance,
the focused API tests passed **13/13** and the full suite passed **158/158**.
The commands, environment, working-tree scope, and code/test hashes are in
[`outputs/track_b/20261029T_covariance_screen_hardening/SESSION.md`](../../outputs/track_b/20261029T_covariance_screen_hardening/SESSION.md).
This is also an uncommitted working-tree run, not a clean-release test.

## Atomic CLI publication regression

The CLI now stages each output bundle in a temporary sibling directory and
publishes it only when all files are complete. Rejected input leaves no
partial final output directory, and an existing output is left unchanged.
Focused CLI tests passed **5/5** and the full suite passed **161/161** after
this change. Full run details and source/test hashes are recorded in
[`outputs/track_b/20261029T_atomic_cli_publication/SESSION.md`](../../outputs/track_b/20261029T_atomic_cli_publication/SESSION.md).

## What this establishes

The current test suite passes for the software and test fixtures it covers,
including algebraic numerical cases, metadata/audit behavior, access-boundary
checks, and Track A/Track B unit contracts. The suite is reproducible from the
repository environment and is recorded separately from scientific evidence.

## Fresh continuation audit

After the subsequent source-family and WSGZP metadata audit additions, the
current modified working tree passed **165/165 tests**. The gate-register
validator also passed and checked **248 evidence paths** without modifying
the register. This run is not a clean-HEAD test: the repository had 80
modified or untracked paths. The exact stdout/stderr, Python and pytest
versions, repository HEAD, worktree inventory, and tracked-diff hash are
recorded in
[`outputs/track_b/20261029T_goal_resume_validation_001/SESSION.md`](../../outputs/track_b/20261029T_goal_resume_validation_001/SESSION.md).

This fresh check updates the current software test count only. It does not
change the scientific gate statuses or validate any neural-source claim.

## Public WSGZP inventory audit regression and latest full-suite run

A read-only OSF JSON:API inventory script was added to check whether the
public WSGZP storage tree exposes separate source-digitizer or registration
files. Its filename classifier is covered by two tests, including a negative
case preventing the `ccepcoreg` archive name from being mistaken for a
coregistration file. The live inventory found zero separate geometry
candidates; details and response hashes are in
[`WSGZP_PUBLIC_GEOMETRY_INVENTORY_RECHECK_20261029.md`](WSGZP_PUBLIC_GEOMETRY_INVENTORY_RECHECK_20261029.md).

After this addition and registering the new geometry-inventory evidence,
the latest full working-tree suite passed **167/167** and the gate-register
validator passed with **253 paths** checked. Exact evidence for the run is at
[`outputs/track_b/20261029T_goal_resume_validation_003/SESSION.md`](../../outputs/track_b/20261029T_goal_resume_validation_003/SESSION.md).
This is a modified-tree software check and does not alter the B4–B8 scientific
gate statuses.

## Sealed model-only CLI parity after output-safety change

A fresh working-tree CLI run on the sealed sub-01 model bundle reproduced the
prior verified clean-wheel output exactly: the 40,980-row ranked-pair CSV was
byte-identical, every saved score array and all seven summary metrics matched,
and both manifests' hashes and allowlists passed. The saved verifier and result
are `scripts/track_b/verify_b8_atomic_cli_reproduction.py` and
`outputs/track_b/20261029T_atomic_cli_real_model_reproduction/source_cli/reproduction_check.json`.
This is one-model software parity only, not empirical source recovery or
scientific validation.

## Historical 0.1.2 virtual-environment wheel parity

The historical 0.1.2 wheel was installed with its declared dependencies into a
new Python 3.12 virtual environment, then the installed console command was
run against the same sealed model-only bundle. Runtime metadata confirms the
CLI imported from that environment (NumPy 2.5.4, SciPy 1.18.1). The fresh
environment produced byte-identical ranked-pair CSV, exact score arrays and
exact summary values against the prior clean-wheel reference; the replay also
checked input/output hashes and the model-only access allowlist. See
[`B8_CURRENT_WHEEL_PARITY_20261029.md`](B8_CURRENT_WHEEL_PARITY_20261029.md)
and the registered reports in
`outputs/track_b/20261029T_atomic_cli_real_model_reproduction/fresh_clean_env_cli/`.
This establishes package behavior on one model, not scientific validity,
source recovery, novelty, or an outside reproduction.

## Distinct 0.1.3.dev0 development-candidate wheel

To remove the same-version/different-content ambiguity between the two
historical 0.1.2 wheels, a distinct `0.1.3.dev0` candidate was built from an
isolated copy of the current package sources. The source-stage verifier passed
all checks: 18/18 Python modules matched the checkout and wheel, project
metadata matched, and the BSD-3-Clause license file and expression matched.
The candidate wheel SHA-256 is
`50793f8864d57089ea489bf142d8d377447f0409a66377b09ee57126a4b01c98`.

The wheel was installed into a newly created Python 3.12 environment with its
declared NumPy and SciPy dependencies. Its console command reproduced the
40,980-pair sealed sub-01 model-only output exactly: CSV bytes, every saved
score array, all compared summary metrics, input/output hashes and allowlisted
model-key access matched the established reference. The source-family
diagnostic remains conditional on one supplied forward model; this is package
reproducibility, not physiological validation or novelty. Detailed commands,
environment metadata and output hashes are in
[`B8_DEVELOPMENT_CANDIDATE_PARITY_20261029.md`](B8_DEVELOPMENT_CANDIDATE_PARITY_20261029.md).

The later final candidate audit reran the full suite with **167/167 passing**
and the read-only gate validator with **264 evidence paths**. Its session
record is
[`outputs/track_b/20261029T_release_candidate_013d/FINAL_VALIDATION_SESSION.md`](../../outputs/track_b/20261029T_release_candidate_013d/FINAL_VALIDATION_SESSION.md).
The worktree is dirty, so this evidence is explicitly not commit-bound.

## Commit-bound release-runner hardening

Commit `9bfd375b20b1d2f1318904551f5a341977b68982` includes tests that ensure
the source-archive release runner accepts only specifically documented
environmental skips, including valid subsets, and rejects unexpected skips or
reasons. The full committed workspace passed **173/173 tests**. A Git archive
of the same commit passed **171 tests, skipped 2 documented cases, and had no
failures**. The skipped checks require repository evidence outputs omitted
from the source archive and the local WSGZP dataset, respectively. The
machine-readable reports are
[`workspace run`](../../outputs/track_b/20261024_b8_release_checks/test_run_9bfd375.json)
and
[`source archive run`](../../outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_9bfd375.json).
This validates the release runner and source snapshot, not scientific claims
or a clean-built wheel.

## What this does not establish

This is not a measured EEG/SEEG validation, a participant-specific forward
model validation, a test of calibration coverage, or evidence of method
novelty. Algebraic fixtures are software tests only. The WSGZP signal-access
gate remains closed; no result in this test report is a neural-data outcome.

## Refreshed commit-bound release check on d38ff42

The refreshed source snapshot and package candidate were checked from commit
`d38ff42611c843dc650d5bf8982902176ac41ea4`. The workspace suite passed
175/175; the extracted source archive passed 173 tests with two documented
skips and zero failures. A fresh Python 3.12 installation of the commit-built
`0.1.3.dev0` wheel reproduced the sealed sub-01 model-only CLI result exactly
(40,980 ranked source pairs). This verifies software provenance and parity,
not source truth, neural recovery, researcher decision benefit, or novelty.
Full report: [`B8_RELEASE_RECHECK_20261029.md`](B8_RELEASE_RECHECK_20261029.md).
