# Fresh public clone check, 1 November 2026

Scope: independent user-path check of the public repository at commit `248fafc` on this machine. The public clone used lawfully held local model-only inputs for a separate participant replay; those inputs are not distributed.

## Environment and commands

- Cloned `https://github.com/tranav4464/observable-geometry.git` into a new directory under `Neurotech/Build/Verification Runs/fresh_public_20261101/repo`.
- Created a new virtual environment using Windows CPython 3.12.16.
- Installed the checkout with `python -m pip install -e ".[test,research-audit]"`.
- Ran `python -m pytest -q -ra` from the clone: **212 passed, two skipped, zero failed** in 10.60 seconds. The skips concern local gate evidence and the unavailable WSGZP dataset.
- Launched the installed `observable-geometry.exe --help` and ran `robust-audit` using the public `examples/robust_audit_toy.json`. The command produced `result.json` with `interval_decision=certified_target_only` and explicitly labelled its bounds as supplied, not independently replayed.
- Ran the installed `distinguish` command on the locally held model-only bundle with `--minimum-distance-mm 20 --top-k 5`. The fresh output had 8,196 sources, covariance rank 235, median best cosine 0.915556984605132 and fraction at or above 0.95 of 0.06039531478770132.
- Compared SHA-256 hashes with the earlier `outputs/track_b/tks_remediation_20261030/model_replay/` output. The ranked CSV (`847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`), scores NPZ (`bbc74660d069419ce199c6fd9a86f0f11f7fc52c92f5c93bbcc91ba5684b58c1`) and summary JSON (`6e33d22df83170fe0c64b6fff94e363b86741f24521b4ffa1523864853034155`) matched byte for byte. The new access log contained only the four permitted model keys. Bundle SHA-256: `e4116465c9af32ddf4bf9e0d3a8e92428c6f1b0bce22a5db257b1c3eaf07a32f`; metadata SHA-256: `a4d52521ddb760114ba1ce740942bc3bb6232f919de62737d345beb7c48db865`.

The first trial installed only the base package plus pytest. Test collection failed for missing `h5py`, `mne` and `nibabel`. The README's full test command requires the documented `research-audit` extra; installation with that extra resolved the collection errors. This is an environment-contract check, not a code failure.

## Newly added adversarial check

Added a joint sensor-permutation test to `tests/test_track_b_distinguishability.py`. It changes the order of leadfield rows and both covariance axes together, then checks exact rankings and float64 scores/norms to tight numerical tolerances. Eight focused tests passed. This verifies a previously uncovered numerical invariant; it does not establish that an arbitrary supplied covariance really matches the sensor order, which remains a provenance obligation for the user.

## Documentation defect repaired

`docs/tks/demo.md` still pointed to the old `TKS/observable_geometry` path and model export files that are absent after workspace reorganization. It now gives a portable public arithmetic demonstration and states plainly that licensed model inputs are required for independent reproduction of the 40,980-row participant result. The public command was executed successfully; the modified guide still needs a post-change clean-clone check after publication.

## Open completion items

- Run the complete audit again after the documentation and new test are committed and published.
- Complete the article, claim-to-evidence audit, citation check and editorial review.
- A reviewer without the licensed model-only input bundle cannot reproduce the participant result from the public clone alone. This same-host replay is independent of the earlier run directory, but it is not external human reproduction or physiological validation.
