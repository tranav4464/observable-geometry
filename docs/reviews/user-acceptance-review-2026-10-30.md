# End-to-end user acceptance review

**Date:** 30 October 2026  
**Scope:** current Observable Geometry working tree after repository reorganization  
**Verdict:** PASS for the bounded TKS research-software build, with the scientific limits already declared by the project

## User journeys executed

1. Built a wheel from a clean extracted source tree and installed it in a new Python 3.12 environment.
2. Confirmed `pip check` and all three public CLI help routes.
3. Ran `distinguish` with declared model arrays, metadata, string source IDs, generated integer IDs, and missing candidate slots.
4. Ran `robust-audit` with the packaged arithmetic example.
5. Ran `family-frontier` with a valid conditional-family comparison.
6. Confirmed clear failures for an existing output path, a forbidden `data` array, a missing input, negative distance, zero `top_k`, and zero block size.
7. Independently replayed output hashes, CSV row counts, array shapes, and the recorded-signal access declaration.
8. Ran the documented Localize-MI model-only live demo: 8,196 sources, covariance rank 235, and 40,980 ranked rows reproduced the recorded summary.
9. Built and verified the portable submission bundle. Every manifest hash and ZIP member passed; the user-facing bundle documents had zero broken local links.
10. Ran the current full workspace suite: 214 passed, zero failed.
11. Ran a source-only archive suite: 212 passed and exactly two documented skips occurred for unavailable workspace evidence and WSGZP data.
12. Ran the complete Track A workflow under a fresh run ID. The recorded-data integration, geometry contract, GBF parity, MNE baseline, resolution analysis, sensitivity analysis, 8,196-source signature library, six-site/11-run descriptive evaluation, report generation, sealing, and second verification all passed.
13. Re-verified the accepted `tracka_release_20261022_v2` release, including scientific input hashes, artifact hashes, source snapshot, dataset commit, 236 channels, 8,196 vertices, 11 empirical runs, and 912 threshold-set edges.
14. Validated all 411 gate-register evidence paths and scanned current workspace documentation: zero broken local links.

## Technical findings and remediation

### 1. Stale wheel-build cache

A direct wheel build from the long-lived worktree initially included three deleted historical modules from the ignored `build/` cache. The source/wheel correspondence check correctly rejected that wheel. The stale cache was moved out of the build location, the clean-source requirement was made explicit, and a subsequent root build contained no historical modules.

### 2. Review renderer could overwrite the curated review

`scripts/render_review.py` previously targeted the curated project review. It now writes `foundation_review.html` inside the selected Track A run directory. A hash check confirmed that executing the renderer leaves `docs/project-review.html` unchanged.

### 3. Gate-badge updater required absent optional elements

The updater required both row and header badge IDs even though the current review contains only row badges. Header badges are now optional, row badges remain mandatory, and the updater executes successfully.

### 4. Submission bundle omitted an HTML document

The documentation copier omitted `.html`, leaving the documentation hub's project-review link unresolved. HTML documentation is now included. The rebuilt bundle contains the project review and has zero broken links across its user-facing pages.

### 5. Sealed verification depended on mutable Git internals

The original Track A seal included `.git/config` and other mutable clone metadata as if they were scientific inputs. Future seals exclude `.git` internals. Verification checks every scientific input file and separately verifies the pinned Localize-MI commit. The accepted v2 release passes under this policy.

### 6. Active documentation cited an older pre-hardening snapshot

Current Track A documentation now identifies `tracka_release_20261022_v2` as the accepted release. The older snapshot remains historical and is not presented as the current verification target.

## Current limitations, not software failures

- The tool is a model-conditional ambiguity audit, not physiological source recovery.
- B4 through B7 remain explicit pivots; no novel-method, clinical, population-generalization, or improved-decision claim is established.
- WSGZP participant-specific registration remains unsuitable for source analysis without the missing registration provenance and QC.
- Licensed recordings, model arrays, ignored run outputs, and the larger adjacent research workspace are intentionally excluded from the portable bundle. Historical evidence links to those materials require the full workspace.
- This review validates the current working tree. A final public release should be built only after committing the accepted changes, then pin that commit and the resulting artifact hashes.

## Final result

No unresolved defect was found in the installable package, public CLI routes, current gate register, accepted Track A release, fresh Track A execution, or portable user-facing bundle. The build is ready for bounded TKS demonstration after the current changes are committed and a final commit-pinned submission bundle is generated.
