# Observable Geometry B8 — external software and scope review

**Review requested:** independent technical review of the bounded GBFs software build and its release claims.
**Project status:** B0–B3 pass at bounded scopes; B4 pivoted away from empirical neural-source validation; B5/B6 not activated; B8 remains open until this review is completed.

**Current-state supplement, 29 October 2026:** this packet has been reconciled
with the later worktree. The WSGZP archive has been downloaded and extracted;
its packaged `LICENSE` and `dataset_description.json` declare CC BY-NC-SA
4.0. The live OSF listing still shows an `Other` metadata license and no
separate digitizer/registration files. The new inventory report records that
distinction. No WSGZP neural sample analysis is part of that license or
inventory check. The historical 0.1.2 wheel records include two different
wheel hashes built at different points in the worktree history. A distinct
0.1.3.dev0 development wheel now matches the current package source and
reproduces the sealed model-only output; it remains an unreleased worktree
candidate. The 167-test worktree result is also not commit-bound. An outside
review requires a clean committed source snapshot and a rebuilt final wheel.

**Commit-bound update, 29 October 2026:** commit
`9bfd375b20b1d2f1318904551f5a341977b68982` passes the full workspace suite
(173 passed, 0 skipped) and the extracted source-archive suite (171 passed,
2 documented skips, 0 failed). The skips are limited to the full-workspace
evidence-path integration test, whose outputs are intentionally excluded from
the source archive, and the WSGZP audit that requires the local dataset. The
release runner now accepts only a subset of these named skips with matching
reasons; unknown or duplicated skips fail. This closes the stale-skip-count
ambiguity, but does not close B8: a commit-bound wheel rebuild and unaffiliated
external reproduction/review are still required. The machine-readable runs
are `outputs/track_b/20261024_b8_release_checks/test_run_9bfd375.json` and
`outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run_9bfd375.json`.

**Commit-bound candidate update, 29 October 2026:** the subsequent commit
`db98529f4590bb7d9ce4ff6f31b977b29b56ac3a` passes 175/175 workspace tests
and 173 source-archive tests with two documented skips. A `0.1.3.dev0` wheel
built from its Git archive passes byte-level module/version/license checks,
fresh isolated installation, and exact sealed sub-01 CLI output parity for
40,980 ranked pairs. The wheel SHA-256 is
`bb3c21a9955896bae5c8314a447559e1d685b42bd28f45eb5ddba2ce8cdddcb4`.
Full commands, reports, and limits are in
[`B8_COMMIT_BOUND_CANDIDATE_20261029.md`](B8_COMMIT_BOUND_CANDIDATE_20261029.md).
This is release verification only. B8 remains open pending unaffiliated
external review/reproduction; the results do not validate neural source
recovery or novelty.

## Materials

- `README.md` and `docs/ARCHITECTURE.md` for setup and interfaces.
- `docs/track_b/PROJECT_DEFINITION.md` and `docs/track_b/GBF_BUILD_PLAN.md` for scope and claim boundaries.
- `docs/track_b/B0_GBF_EXTENSION_SCREEN.md` for prior art and novelty limits.
- Suzuki, Wada & Sugiura's CANDLE preprint and the project page ([paper](https://arxiv.org/abs/2610.07824), [full text](https://arxiv.org/html/2610.07824), [project page](https://candle-esi.pages.dev/)) are newly identified close prior art. Please assess whether its null-space learning method, GBF comparison, and Parmigiani stimulation evaluation materially change the project's claim boundary; do not treat its preprint results as independent replication or assume exact participant overlap without checking.
- `docs/track_b/B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md` for the updated metadata-only screen of alternatives, including iES-CCEP, DRE-LZSH, HDEEG-IED-SurgOutcome, and Barborica et al.'s simultaneous scalp–SEEG seizure-onset dataset. Please check that close prior art is identified, that previously analyzed data are not called independent replication, and that access terms and endpoint limitations are handled explicitly.
- `docs/track_b/B4_OSF_WSGZP_LICENSE_AUDIT_20261024.md` and `docs/track_b/WSGZP_PUBLIC_GEOMETRY_INVENTORY_RECHECK_20261029.md` for the current license/provenance distinction. The live OSF API still exposes the `Other` record pointing to `license.txt`, which is not separately listed; the downloaded BIDS archive itself contains a root `LICENSE` and `dataset_description.json` declaring CC BY-NC-SA 4.0. The fresh recursive OSF metadata inventory lists only the archive parts and `eeg_badtrials.json`, with no separate digitizer or registration/QC file. The EBRAINS data files remain unaccessed. The inventory checked metadata only and did not inspect neural recordings.
- `docs/track_b/B4_HDEEG_REOPENING_ASSESSMENT_20261024.md` and `docs/track_b/B4_HDEEG_PUBLISHED_OVERLAP_ADDENDUM_20261024.md` for the focused HDEEG assessment and published cohort-count reconciliation. The 20-person remainder is only a same-cohort candidate by count, not an independent external sample; identities, quality eligibility, terms, covariance, and endpoint feasibility remain unresolved.
- `docs/track_b/B2_GBF_SPEC.md` and `docs/track_b/B2_GATE_CLOSEOUT_20261024.md` for the fixed score, numerical check, and reviewer-record limitation.
- `docs/track_b/B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md` for upstream trace and the sealed model-only comparison.
- `docs/track_b/B3_MONTAGE_SENSITIVITY_20261024.md` and `outputs/track_b/20261024_b3_montage_sensitivity/` for the deterministic 236-to-224 channel/reference sensitivity check. Please assess whether the covariance projection is consistent with the declared reference, whether the ranking-stability summaries are correctly bounded, and whether this evidence is kept separate from empirical source validation.
- `scripts/track_b/verify_b3_montage_sensitivity_reproduction.py` and `outputs/track_b/20261024_b3_montage_sensitivity_reproduction_01/` for a repeat run and machine-checked comparison against the first result. It compares the semantic report, input hashes, and access logs; it is a same-model repeatability check, not an independent sample.
- `docs/track_b/B4_DEVELOPMENT_AUDIT_20261024.md` and `docs/track_b/B4_CHANNEL_MATCH_RECONCILIATION_20261024.md` for the empirical endpoint, pivot, and preserved invalid join.
- `docs/track_b/B4_ARTIFACT_VALIDATION_REOPENING_PROPOSAL_20261024.md` and `outputs/track_b/data_acquisition/b4_multisubject_metadata_feasibility.json` for a metadata-only assessment of a possible artifact-benchmark reopening. The audit found a single run per site–intensity condition and sparse cross-intensity comparisons; no held-out signal outcomes were opened and the proposal is not approved for confirmatory execution.
- `docs/track_b/B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md` for the metadata-only screen of public paired EEG/SEEG alternatives and the reasons none currently reopens the active GBF evaluation. No neural-signal samples were opened for that screen.
- `docs/track_b/B4_NEMAR_NM000456_PAIRING_AUDIT_20261024.md` for a version-pinned read-only check showing that the recently released `nm000456` record's combined modality label refers to disjoint participant groups, not paired EEG/iEEG recordings.
- `docs/track_b/B4_NEMAR_CATALOG_SCREEN_20261024.md` for a catalog-wide, metadata-only NEMAR search and version-pinned checks of all four records returned with both exact EEG and iEEG modality labels, including the newly indexed SenseFOG (`nm000434`) and perceptual-consciousness (`on001785`) candidates.
- `scripts/track_b/audit_nemar_eeg_ieeg_catalog.py` and `outputs/track_b/20261024_b4_nemar_catalog_screen/catalog_screen.json` for the query implementation and captured catalog/participant-directory metadata. The script refuses to overwrite its evidence file.
- `docs/track_b/B5_B6_ROUTE_CLOSEOUT_20261024.md` for the decision not to lock a confirmatory protocol or access held-out outcomes under the pulse-artifact endpoint.
- `docs/track_b/B7_DECISION_VALUE_AUDIT_20261024.md` and `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/` for the paired same-model diagnostic comparison and independent rank-statistic recheck. The earlier v1 exploratory run is retained and marked superseded.
- `scripts/track_b/export_sealed_model_bundle.py`, `src/observable_geometry/cli.py`, and `src/observable_geometry/track_b/distinguishability.py` for code review.
- `scripts/track_b/run_b8_release_tests.py` and `scripts/track_b/build_b8_reviewer_handoff.py` for commit-bound workspace/archive tests and the clean-commit, hash-verified handoff build procedure. The archive-test runner explicitly verifies that imports resolve inside the extracted snapshot.
- `outputs/track_b/20261024_b8_release_checks/clean_install_parity.json` for the final wheel-based reproduction, license-metadata check, and confirmation that archived simulator modules are absent; the final clean-environment outputs are under `outputs/track_b/20261024_b8_export_cli_clean_env_v4/`.
- `outputs/track_b/20261024_b8_source_archive_tests/` for extracted source-only handoff checks, including preserved failed attempts and commit-bound reports. Earlier 88/87-test counts are historical. The latest report for commit `9bfd375` records 173 workspace passes and 171 archive passes with exactly two documented skips; the handoff builder binds reports to the exact packaged commit and source-archive hash.
- `outputs/track_b/20261024_b8_release_checks/release_artifacts/observable_geometry-0.1.2-py3-none-any.whl` for the distributable BSD-3-Clause wheel (SHA-256 `dc8b241e0320c901d98cf65dc626c8d1131c2f2b6caae6a4bb51b916cce02100`). The superseded 0.1.1 stale-build failure is preserved separately and is not the release candidate.
- `docs/track_b/PROJECT_DEFINITION.md` for the current build target and claim boundary, including the distinction between a software reproduction, a nominal model-based diagnostic, and empirical validation.
- `docs/track_b/DISCOVERY_OUTCOME_REPORT_20261029.md`, `docs/track_b/TAIL_CLOSED_NOVELTY_FALSIFICATION_20261029.md`, and `docs/track_b/TAIL_CLOSED_RELATIVE_FRONTIER_20261029.md` for the latest candidate-method falsification, matched-subspace comparisons, and explicit no-novelty boundary. The relative-margin selector optimizes its declared fixed-grid objective, but no distinct algorithmic or decision advantage is established.
- `docs/track_b/DS004752_EFFECT_SENSITIVITY_20261029.md` for the measured scalp-to-iEEG benchmark sensitivity result. Its small mean advantage has an interval crossing zero and is not source-map recovery.
- `docs/track_b/WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md` and `docs/track_b/WSGZP_PUBLIC_GEOMETRY_INVENTORY_RECHECK_20261029.md` for the remaining participant-specific coordinate-provenance gate.
- `outputs/track_b/20261029T_goal_resume_validation_003/SESSION.md` for the latest 167-test and 253-path gate-register run. This is evidence from an uncommitted working tree, not from the historical clean source archive.
- `LICENSE`, `CITATION.cff`, and `docs/track_b/SOURCE_SNAPSHOT_MANIFEST.json` for source terms and source-only provenance. The separate verification report is generated under the ignored release-check output folder after the source snapshot is committed.

## Checks requested

1. Inspect whether the CLI rejects undeclared arrays before reading them, validates its input dimensions and metadata, refuses overwrites, and records the needed provenance.
2. Check that the implementation in `distinguishability.py` matches the B2 equations and does not silently treat unsupported covariance components as observed information.
3. Verify the clean-wheel results independently, either by rerunning on the permitted model-only bundle or by auditing the input and output hashes and the exact pairwise parity report.
4. Check that the README, project definition, and reports clearly distinguish nominal forward-model similarity from measured localization, source truth, calibrated probability, and population performance.
5. Review the B4 pivot and confirm that the 236-channel/224-channel joined analysis is excluded from scientific inference.
6. Check that B5/B6 are recorded as pivoted without held-out outcome access, and that B7 reports only descriptive model-output associations rather than analyst utility.
7. Identify any release-blocking defects and state whether the package is ready for a limited software release. Do not certify scientific novelty or physiological validation from the supplied evidence.
8. Check whether the proposed iES-CCEP or HDEEG-IED-SurgOutcome secondary evaluations could provide a sufficiently distinct, useful test beyond Wang et al. 2026, and whether Barborica et al.'s seizure-onset dataset merits a separate template-model reproduction route. Assess the participant-overlap, endpoint, comparators, geometry adequacy, data terms, and protocol review required before access. These are candidates only; no new outcomes or signals have been opened for them.

## Required reviewer record

Please provide reviewer name, affiliation, relevant expertise, conflicts or prior involvement, materials personally inspected, independent computations or checks performed, findings, recommendation (`PASS`, `HOLD FOR CHANGES`, or `FAIL/PIVOT`), and date. Clearly distinguish checks personally reproduced from checks accepted from the supplied records. Do not claim that EEG samples were untouched unless your own access path supports that statement.

## Known release limits to retain

- The repository source code is BSD-3-Clause licensed; this does not cover the separately vendored GBFs checkout or datasets.
- The Localize-MI dataset and data-derived bundles are not included in the source distribution.
- The B2 verifier hash printed in the supplied review was malformed; the locally computed code hash is documented in the B2 closeout.
- Workspace review records contain a conflict about reviewer identity/affiliation; the supplied identity is not independently authenticated. Preserve this limitation and do not edit historical source records.
- No held-out participant analysis, independent cohort validation, neural physiological source test, decision-utility study, or novel-method evidence is complete.
- The public iES-CCEP archive is not an untouched cohort for broad GBF localization: Wang et al. 2026 report 318 sessions from 35 participants on this data route. The OSF API's `Other` license record refers to a `license.txt` not separately listed in storage metadata, but the downloaded/extracted BIDS package contains a root license declaring CC BY-NC-SA 4.0. The data remain outside Git. The current source-imaging protocol is still unlocked, and no WSGZP neural samples have been used for this candidate evaluation; license resolution does not clear geometry, preprocessing, endpoint, or prior-art gates.
- The iES-CCEP data are also indexed in EBRAINS. The unauthenticated Knowledge Graph instance request returned HTTP 401, and the public page response exposed only the application shell; dataset-specific reuse terms were not established through that route either. The EBRAINS dataset files were not accessed.
- The October 2026 CANDLE preprint (under review) reports 291 stimulation runs from 32 patients on the Parmigiani et al. dataset family and includes GBF as a baseline. Exact subject/run overlap with the Wang et al. GBF analysis is unresolved. CANDLE therefore raises the prior-art bar and cannot be represented as an independent cohort or validation of our B2 score. Its inspected project page did not expose a code link; supplementary code/checkpoint availability and license remain unverified.
- The HDEEG-IED-SurgOutcome dataset has individual MRI, EEG averages, electrode coordinates, resection imaging, and clinical outcomes. The data descriptor reports 44 participants, including 30 favourable and 14 unfavourable outcomes; the GBF paper reports a 24-person favourable subset after quality exclusions. A 20-person remainder follows by count, but it is not an external cohort, the six favourable cases may have failed quality control, and the 14 unfavourable cases do not provide straightforward resection-based source truth. Averaged heterogeneous EEG also leaves B2 covariance compatibility unresolved. No dataset access or outcome analysis is authorized by the metadata screen.
- Barborica et al.'s simultaneous scalp–SEEG seizure-onset analysis is close prior art. The paper reports use of an MNI-template head model because scalp electrode coordinates were unavailable. EBRAINS indexes a versioned `v1` dataset record, but the exact file inventory and dataset-specific reuse terms were not verified; the paper's dataset site did not load during the metadata-only screen. It does not satisfy the participant-specific model contract for B2.
- A user-supplied B2 review text recommends approval of the registered B2 computation only. It does not review B8. The supplied verifier digest is malformed, and the reviewer affiliation differs across supplied versions, so workspace evidence does not authenticate the named reviewer. Do not treat this text alone as unaffiliated external B8 review.
- The 0.1.3.dev0 development wheel with SHA-256 `50793f8864d57089ea489bf142d8d377447f0409a66377b09ee57126a4b01c98` matches the current package modules and reproduces the sealed model-only output in a fresh environment. It was built from a modified, uncommitted worktree and is not a public release. The earlier two 0.1.2 wheel hashes are preserved as historical records and must not be conflated. The 167-test result likewise covers a modified worktree; an updated commit-bound source archive, final wheel/version decision, and unaffiliated outside review remain required for B8 closure. See `docs/track_b/B8_DEVELOPMENT_CANDIDATE_PARITY_20261029.md`.

## 29 October 2026 release-candidate update

The refreshed commit-bound candidate is documented in
[`B8_RELEASE_RECHECK_20261029.md`](B8_RELEASE_RECHECK_20261029.md). Commit
`d38ff42611c843dc650d5bf8982902176ac41ea4` passed 175/175 workspace tests
and 173 source-archive tests, with two documented skips and zero failures.
Its source-verified `0.1.3.dev0` wheel installed in a fresh Python 3.12
environment and reproduced the sealed one-participant model-only result
exactly. The check does not establish physiological validity or method
novelty.

**External reviewer action still needed:** independently obtain the exact
commit and wheel identified in the recheck report, follow its reproduction
commands, record the environment and any deviations, inspect claim boundaries,
and provide a signed or otherwise attributable review. Do not treat prior
project-associated review text as this independent B8 review.

## Latest exact-commit package evidence

The newer package verification is bound to source commit
`1e831920cb8b6d8f97078bdb66229e5598d4657e`, superseding d38ff42 for the
reviewer's candidate. See [`B8_RELEASE_RECHECK_20261029.md`](B8_RELEASE_RECHECK_20261029.md)
and its listed reports. The current candidate wheel SHA-256 is
`e81af2356c3856d0d71bd287d69482919b614bdbf722cbcfa660ccc2c425227f`. The
external reviewer should reproduce this exact commit/wheel pair or report why
that is not possible. The required review record and claim limits above still
apply.
