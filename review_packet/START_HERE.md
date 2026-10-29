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
2. Create a fresh Python 3.12 environment, install the included wheel and `pytest`, and run the archive tests. Record environment, commands, pass/skip/fail counts, and any divergence. Two skips are expected when local evidence outputs and WSGZP data are absent.
3. For the primary 40,980-pair artifact, obtain lawful access to the exact **model-only** Localize-MI-derived bundle and metadata from the project owner, or witness the owner running the clean installation on that bundle. Check input hashes in `evidence/model_only_parity.json`, run `observable-geometry distinguish --bundle <bundle> --metadata <metadata> --output <new-output-dir> --minimum-distance-mm 20 --top-k 5`, and compare the resulting CSV, score arrays, summary and access log with the pinned parity evidence. Do not inspect or redistribute human recording samples. If the reviewer cannot access or witness this run, record the scope limit and leave B8 open.
4. Return a short attributable record: name, affiliation, expertise, conflicts or prior involvement, date, checks personally performed or witnessed, checks accepted from supplied reports, findings, and `PASS`, `HOLD FOR CHANGES`, or `FAIL/PIVOT`.

The model-only bundle is excluded from this public handoff under the dataset terms. Contact the owner for a lawful private review path. No source-recovery, clinical, population, decision-benefit or novel-method claim follows from successful software reproduction.

## Release decision

Version `0.1.3.dev0` is the verified development candidate. A stable release version and B8 PASS remain deferred until the outside check is recorded and any findings are addressed.
