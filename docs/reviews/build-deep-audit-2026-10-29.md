# Observable Geometry build audit

**Audit date:** 29 October 2026  
**Repository state at audit start:** `03d38981ff297f41627a1ab2830bf1a4bb7dce15`  
**Status:** Completed repository and saved-evidence audit. Release decision: **HOLD B8**. This is not an independent rerun of restricted participant inputs or an external scientific review.

## Evidence directly checked

- The repository was clean at the start of the review. No files under `data/`, `outputs/`, `tmp/`, or `reviewer_handoff/` are tracked by Git; no `.fif`, `.edf`, `.bdf`, `.vhdr`, `.set`, `.npz`, `.npy`, or `.zip` files were found among tracked files. This is a tracked-file inventory, not a scan of Git history or every possible binary format.
- The active `distinguish` implementation checks leadfield/covariance dimensions and finiteness, covariance symmetry/support, source coordinates, distance and ranking parameters. It compares normalized noise-whitened forward columns by absolute cosine and records the profiled unit-signal residual. Its output is conditional on the supplied model and does not estimate an active neural source.
- The CLI checks NPZ member names before materializing arrays, logs approved model-array reads, rejects undeclared keys, and publishes output through a staging directory. This is a process-level access guard, not an operating-system security boundary.
- The two-sided audit returns a feasible residual upper bound and a weak-dual lower bound for each declared convex branch. The family-frontier module only combines supplied intervals; it does not verify that those intervals are true.
- The workspace test suite passed **211/211** on the current working tree after the wording fixes. `validate_gate_register.py` passed with **393 evidence paths checked** and B8 still `IN_PROGRESS`. The gate validator confirms path existence and gate-graph rules; it does not independently authenticate the scientific contents of those paths.
- The prior source archive tied to `03d3898` passed **209** tests with **two documented skips**. The prior 7d779cb wheel passed source/provenance checks, isolated installation, and exact 40,980-pair parity on one sealed model. Those wheel checks predate the CLI docstring change made during this audit.
- I inspected the archived linear-Gaussian observable-sensitivity code and its independent Kronecker and finite-difference tests. I also inspected the experimental tail-closed source and tests, including direct S-lemma matrix replay, rank-deficiency, rotation, and finite-prior cases. Saved independent reports `20261029T_relative_frontier_002/independent_check_001.json` and `20261029T_relative_baseline_002/independent_check_001.json` report PASS with verified input hashes and direct replay of 28/25 positive-rank bases and 75 matched-baseline rows, respectively. These are numerical, one-model checks; their float64 bounds are not formal interval proofs.
- The four reviewer-facing Markdown documents checked (`README.md`, TKS handoff, 7d779cb B8 handoff and candidate report) have no broken local links. Their GitHub and external links were not independently fetched in this audit.
- The WSGZP archive-level `LICENSE` and `dataset_description.json` were previously checked and document CC BY-NC-SA 4.0, with hashes in the OSF license audit. That addresses the project-level reuse declaration but does not validate participant registration. The independent geometry recheck records 57 of 6,660 electrodes outside the corresponding MRI field of view and incomplete transform/QC provenance; it explicitly leaves source-analysis geometry unverified. This audit inspected those reports, not the raw electrode/MRI arrays again.

## Findings, ordered by consequence

### 1. B8 remains open (release blocker)

The gate register explicitly reports B8 as `IN_PROGRESS`. Its independent-review field requires an external researcher or reviewer to **perform or witness the clean reproduction**. The two outreach reviews are documentation-level feedback and did not do this. The package remains `0.1.3.dev0`; no final release-version decision is recorded. The current build is a tested research prototype, not a formally closed release.

The B8 reviewer handoff previously invited a high-level review without installation and implied that review alone could close the gate. I corrected it locally to distinguish useful preliminary feedback from the registered reproduction requirement. The TKS handoff was corrected to state that requirement as well.

### 2. Current source-snapshot verifier is stale (reproducibility)

Running `verify_source_snapshot.py` against the current tree failed. The pinned `SOURCE_SNAPSHOT_MANIFEST.json` records 323 files and an older source state. The verifier reported six newer files and modifications to `README.md`, `GATE_REGISTER.json`, `PROJECT_DEFINITION.md`, and `cli.py`. The manifest is historical evidence only. It cannot prove that the current tree matches its snapshot. The commit-bound Git archive and wheel reports are the better evidence for their own named candidates. A new release candidate needs its own versioned source snapshot or exact-commit archive and wheel checks; preserve the old manifest rather than overwriting it.

### 3. Public review cannot reproduce the participant result from GitHub alone (review scope)

The licensed Localize-MI-derived model bundle and machine run outputs are excluded from the public repository. The public reports describe their hashes and checks, but an outside reader cannot independently reproduce the 40,980-pair participant result solely from the public checkout. This limit is documented in the B8 handoff. A reviewer can still inspect the source, run data-free tests, and review claim boundaries; model-level replay needs lawful access to the exact inputs.

### 4. Wording defects found and locally corrected (clarity)

The CLI module description called the command a “GBF diagnostic,” although the active pairwise command compares supplied forward columns separately from the GBF inverse estimator. That description was corrected. `PROJECT_DEFINITION.md` called an older 9a88bad candidate the “current exact-HEAD” candidate; the sentence now reflects the later 7d779cb candidate. The B8 and TKS handoffs now state the exact outside-reproduction requirement. These fixes remain working-tree changes until committed and package-verified; the 7d779cb wheel evidence does not certify this edited tree.

### 5. Optional numerical research is exploratory (claim risk)

The tail-closed relative-frontier output is an attained finite-grid lower bound under a specified finite-mesh model and declared prior. Its independent replay checks saved float64 calculations. It does not establish a globally optimal continuous multiplier, outward-rounded proof, measured neural source recoverability, or method novelty. The repository's own document states these limits. Observable-sensitivity is an archived linear-Gaussian VAR candidate and is not an active source-imaging result.

## Scientific claim boundary

The repository's discovery report explicitly pivots the novel-method and measured source-recovery claims. B4–B7 are `PIVOT`, with documented reasons. The Localize-MI control uses stimulation-pulse artifacts; WSGZP participant-specific scalp-to-MRI registration remains unresolved. Direct constrained fitting has not been beaten on a held-out researcher decision. The current evidence supports a bounded model-auditing software contribution and one-model numerical reproducibility, not physiological source recovery, population generality, clinical use, or a new mathematical method.

## Audit verdict and next gate

**Software and bounded research prototype: PASS for TKS demonstration. Formal release gate B8: HOLD. Scientific source-recovery or novel-method claim: unsupported.** The code, tests, model-only numerical replay, access boundary, and candid negative gates make a credible exploratory tool. The closed 7d779cb candidate has recorded source/wheel checks, but the current audit's local wording fixes are not part of that verified package.

To close B8, freeze the final source commit, rerun source archive, workspace, wheel, clean installation and model-only parity checks on that exact commit, arrange lawful model-only access for an outside reviewer to perform or witness the clean reproduction, record their attributable findings and divergences, and explicitly choose the release version. A public checkout alone cannot reproduce the sealed participant run. Do not mark B8 PASS from the 211 tests, saved replay reports, or outreach feedback alone.

## Audit limits

This review examined the active implementation, major optional numerical modules, tests, gate and release documents, saved machine-readable verification summaries, and tracked-file inventory. It did not independently recompute the restricted one-participant model result from raw inputs, inspect human EEG/SEEG sample arrays, validate WSGZP electrode-to-MRI registration, inspect every historical Git object for restricted data, or establish empirical source-identification accuracy. The saved verifier reports are evidence of recorded replay, not substitutes for an outside clean reproduction.
