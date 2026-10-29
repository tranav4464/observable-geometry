# Historical 0.1.2 wheel clean-environment parity check

**Date:** 29 October 2026\
**Status:** PASS for the bounded clean-install and output-parity checks below. B8 remains open. Superseded as the current worktree wheel by the separately versioned 0.1.3.dev0 candidate documented in [the development-candidate parity record](B8_DEVELOPMENT_CANDIDATE_PARITY_20261029.md).

## What was checked

At the time of this historical check, the `0.1.2` package was built from an isolated copy of the then-current
package source into a wheel. It was installed in a newly created Python 3.12
virtual environment with dependencies resolved from package metadata, then
invoked using that environment's console script. Runtime metadata confirms
that the package module was imported from the isolated environment and that
NumPy 2.5.4 and SciPy 1.18.1 were installed there. The candidate run used
only the sealed sub-01 model bundle and was compared with the prior verified
`0.1.2` clean-wheel reference.

The fresh-environment candidate reproduced the reference exactly: all 40,980
ranked pairs, saved score arrays, summary values, manifest hashes and
model-only access records passed the parity checker. The reports are
[`clean_environment_parity.json`](../../outputs/track_b/20261029T_atomic_cli_real_model_reproduction/fresh_clean_env_cli/clean_environment_parity.json)
and [`clean_environment_installation.json`](../../outputs/track_b/20261029T_atomic_cli_real_model_reproduction/fresh_clean_env_cli/clean_environment_installation.json).

A separate byte-level check confirmed that all 18 Python modules in the wheel
match both the isolated build stage and current checkout, and that the staged
README, license and project metadata match the current checkout. The checker
and result are `scripts/track_b/verify_b8_wheel_source.py` and
`outputs/track_b/20261029T_atomic_cli_real_model_reproduction/wheel_source_verification.json`.

Wheel SHA-256:
`e145c5d9f6e5a32408b0065bf838436dd97ed17757cdd4d6799ada110a63a582`

## Limits

This is a fresh virtual-environment package-install check and an exact
one-model output-parity check. The wheel reflects a modified, uncommitted
worktree and retains version `0.1.2`; it is not a new public release or an
outside reproduction. It does not establish physiological source recovery,
decision utility, or novelty. B8 remains open pending unaffiliated outside
review/reproduction and final release review.
