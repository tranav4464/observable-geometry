# Observable Geometry B8: independent reproduction handoff

**Candidate commit:** `8a19221595b6a56a816ca2e4aec44784ab049402`  
**Package:** `observable-geometry 0.1.3.dev0` (development candidate)  
**B8 status:** IN_PROGRESS. This packet is evidence for review, not a reviewer verdict.

## What the tool does

Given a declared EEG forward model and noise covariance, `distinguish` ranks spatially separated candidate source patterns whose *predicted* scalp fields are similar. It does not infer active neural sources. The pairwise diagnostic is separate from the GBF inverse estimator.

## Evidence already recorded

- Workspace: 211 passed, 0 skipped, 0 failed.
- Extracted commit archive: 209 passed, 2 documented environment/evidence skips, 0 failed.
- Source/wheel: 18 modules, license and version checks pass.
- Fresh Python 3.12 environment: installed wheel modules match the wheel and installed CLI implementation matches the run manifest.
- One-model CLI: all 40,980 ranked pairs, score arrays and summary metrics match the earlier clean-wheel reference exactly. The bundle/export logs declare only approved model-array keys; no EEG/iEEG sample arrays were read by this workflow.

See `EVIDENCE_MANIFEST.json` for hashes, and `evidence/` for machine-readable results. These records are supplied evidence, not checks personally performed by a reviewer.

## The required outside check

B8 requires an external researcher or reviewer to **perform or witness a clean reproduction** of this exact candidate. A documentation skim is useful preliminary feedback but cannot close the gate. The reviewer should:

1. Verify this packet's hashes and inspect the source archive and wheel. The source can also be viewed at https://github.com/tranav4464/observable-geometry/tree/8a19221595b6a56a816ca2e4aec44784ab049402.
2. Create a fresh Python **3.12 or newer** environment (the owner used 3.12.14), install the included wheel and all test/research dependencies, then run the archive tests. For example: `python -m pip install <included-wheel>` followed by `python -m pip install "pytest>=8" "h5py>=3.10" "mne>=1.7" "nibabel>=5.2"`; extract the source ZIP, set `PYTHONPATH` to its `src` folder, and run `python -m pytest -q` there. Record exact versions, commands, pass/skip/fail counts, and any divergence. The package declares `requires-python >=3.12`; a different supported Python version is a reported environment difference, not automatically a gate failure. Two skips are expected when local evidence outputs and WSGZP data are absent. Without `nibabel`, three WSGZP test modules can fail during collection, so a 201-test subset is not the full archive run.
3. For the primary 40,980-pair artifact, obtain lawful access to the exact **model-only** Localize-MI-derived bundle and metadata from the project owner, or witness the owner running the clean installation on that bundle. Check input hashes in `evidence/model_only_parity.json`, run `observable-geometry distinguish --bundle <bundle> --metadata <metadata> --output <new-output-dir> --minimum-distance-mm 20 --top-k 5`, and compare the resulting CSV, score arrays, summary and access log with the pinned parity evidence. Do not inspect or redistribute human recording samples. If the reviewer cannot access or witness this run, record the scope limit and leave B8 open.
4. Return a short attributable record: name, affiliation, expertise, conflicts or prior involvement, date, checks personally performed or witnessed, checks accepted from supplied reports, findings, and `PASS`, `HOLD FOR CHANGES`, or `FAIL/PIVOT`.

The model-only bundle is excluded from this public handoff under the dataset terms. Contact the owner for a lawful private review path. No source-recovery, clinical, population, decision-benefit or novel-method claim follows from successful software reproduction.

## Release decision

Version `0.1.3.dev0` is the verified development candidate. A stable release version and B8 PASS remain deferred until the outside check is recorded and any findings are addressed.

**Offline environment:** If package downloads fail, attach a compatible dependency wheelhouse or use a machine with package access. Dependencies borrowed through `PYTHONPATH` from another environment do not establish a fully isolated installation.

## New owner-run clean-environment evidence (v3)

The v1/v2 `evidence/source_archive_tests.json` describes tests run from the build environment. It has **not** been replaced. New files under `evidence/fresh_environment/` separately document a newly created Python 3.12 virtual environment, installation of the candidate wheel plus test/research dependencies, `pip check`, and a full extracted-archive test run: 209 passed, two expected skips. This is **owner-executed evidence**, not an outside reproduction. Review `clean_env_full_002_verification.json` and its listed file hashes before relying on it.

The `offline_wheels/` folder includes `nibabel-5.4.2-py3-none-any.whl` to resolve the missing-`nibabel` collection error reported by one offline AI audit. On a Python >=3.12 environment with its other declared dependencies already installed, use `python -m pip install --no-index --no-deps offline_wheels/nibabel-5.4.2-py3-none-any.whl`. This single wheel is not a complete offline dependency bundle; a fully isolated installation still needs all package dependencies from a trusted index or complete wheelhouse.
