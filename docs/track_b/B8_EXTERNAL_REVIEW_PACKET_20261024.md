# Observable Geometry B8 — external software and scope review

**Review requested:** independent technical review of the bounded GBFs software build and its release claims.
**Project status:** B0–B3 pass at bounded scopes; B4 pivoted away from empirical neural-source validation; B5/B6 not activated; B8 remains open until this review is completed.

## Materials

- `README.md` and `docs/ARCHITECTURE.md` for setup and interfaces.
- `docs/track_b/PROJECT_DEFINITION.md` and `docs/track_b/GBF_BUILD_PLAN.md` for scope and claim boundaries.
- `docs/track_b/B0_GBF_EXTENSION_SCREEN.md` for prior art and novelty limits.
- `docs/track_b/B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md` for the updated metadata-only screen of alternatives, including iES-CCEP, DRE-LZSH, HDEEG-IED-SurgOutcome, and Barborica et al.'s simultaneous scalp–SEEG seizure-onset dataset. Please check that close prior art is identified, that previously analyzed data are not called independent replication, and that access terms and endpoint limitations are handled explicitly.
- `docs/track_b/B4_HDEEG_REOPENING_ASSESSMENT_20261024.md` and `docs/track_b/B4_HDEEG_PUBLISHED_OVERLAP_ADDENDUM_20261024.md` for the focused HDEEG assessment and published cohort-count reconciliation. The 20-person remainder is only a same-cohort candidate by count, not an independent external sample; identities, quality eligibility, terms, covariance, and endpoint feasibility remain unresolved.
- `docs/track_b/B2_GBF_SPEC.md` and `docs/track_b/B2_GATE_CLOSEOUT_20261024.md` for the fixed score, numerical check, and reviewer-record limitation.
- `docs/track_b/B3_IMPLEMENTATION_AND_CLOSEOUT_20261024.md` for upstream trace and the sealed model-only comparison.
- `docs/track_b/B3_MONTAGE_SENSITIVITY_20261024.md` and `outputs/track_b/20261024_b3_montage_sensitivity/` for the deterministic 236-to-224 channel/reference sensitivity check. Please assess whether the covariance projection is consistent with the declared reference, whether the ranking-stability summaries are correctly bounded, and whether this evidence is kept separate from empirical source validation.
- `scripts/track_b/verify_b3_montage_sensitivity_reproduction.py` and `outputs/track_b/20261024_b3_montage_sensitivity_reproduction_01/` for a repeat run and machine-checked comparison against the first result. It compares the semantic report, input hashes, and access logs; it is a same-model repeatability check, not an independent sample.
- `docs/track_b/B4_DEVELOPMENT_AUDIT_20261024.md` and `docs/track_b/B4_CHANNEL_MATCH_RECONCILIATION_20261024.md` for the empirical endpoint, pivot, and preserved invalid join.
- `docs/track_b/B4_ARTIFACT_VALIDATION_REOPENING_PROPOSAL_20261024.md` and `outputs/track_b/data_acquisition/b4_multisubject_metadata_feasibility.json` for a metadata-only assessment of a possible artifact-benchmark reopening. The audit found a single run per site–intensity condition and sparse cross-intensity comparisons; no held-out signal outcomes were opened and the proposal is not approved for confirmatory execution.
- `docs/track_b/B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md` for the metadata-only screen of public paired EEG/SEEG alternatives and the reasons none currently reopens the active GBF evaluation. No neural-signal samples were opened for that screen.
- `docs/track_b/B5_B6_ROUTE_CLOSEOUT_20261024.md` for the decision not to lock a confirmatory protocol or access held-out outcomes under the pulse-artifact endpoint.
- `docs/track_b/B7_DECISION_VALUE_AUDIT_20261024.md` and `outputs/track_b/20261024_b7_resolution_overlap_audit_v2/` for the paired same-model diagnostic comparison and independent rank-statistic recheck. The earlier v1 exploratory run is retained and marked superseded.
- `scripts/track_b/export_sealed_model_bundle.py`, `src/observable_geometry/cli.py`, and `src/observable_geometry/track_b/distinguishability.py` for code review.
- `scripts/track_b/run_b8_release_tests.py` and `scripts/track_b/build_b8_reviewer_handoff.py` for commit-bound workspace/archive tests and the clean-commit, hash-verified handoff build procedure. The archive-test runner explicitly verifies that imports resolve inside the extracted snapshot.
- `outputs/track_b/20261024_b8_release_checks/clean_install_parity.json` for the final wheel-based reproduction, license-metadata check, and confirmation that archived simulator modules are absent; the final clean-environment outputs are under `outputs/track_b/20261024_b8_export_cli_clean_env_v4/`.
- `outputs/track_b/20261024_b8_source_archive_tests/` for the extracted source-only handoff check, including preserved failed attempts and the current commit-bound run report. The current archive passes 83 tests and skips only the strict evidence-path integration test because run evidence is intentionally excluded from the source archive. The complete workspace passes all 84 tests and the strict validator checks all registered evidence paths.
- `outputs/track_b/20261024_b8_release_checks/release_artifacts/observable_geometry-0.1.2-py3-none-any.whl` for the distributable BSD-3-Clause wheel (SHA-256 `dc8b241e0320c901d98cf65dc626c8d1131c2f2b6caae6a4bb51b916cce02100`). The superseded 0.1.1 stale-build failure is preserved separately and is not the release candidate.
- `docs/track_b/PROJECT_DEFINITION.md` for the current build target and claim boundary, including the distinction between a software reproduction, a nominal model-based diagnostic, and empirical validation.
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
- The public iES-CCEP archive is not an untouched cohort for broad GBF localization: Wang et al. 2026 report 318 sessions from 35 participants on this data route. OSF metadata queried for the screen contain no explicit license. No use of its signal data is authorized in this project until terms are clarified and a distinct protocol receives review.
- The HDEEG-IED-SurgOutcome dataset has individual MRI, EEG averages, electrode coordinates, resection imaging, and clinical outcomes. The data descriptor reports 44 participants, including 30 favourable and 14 unfavourable outcomes; the GBF paper reports a 24-person favourable subset after quality exclusions. A 20-person remainder follows by count, but it is not an external cohort, the six favourable cases may have failed quality control, and the 14 unfavourable cases do not provide straightforward resection-based source truth. Averaged heterogeneous EEG also leaves B2 covariance compatibility unresolved. No dataset access or outcome analysis is authorized by the metadata screen.
- Barborica et al.'s simultaneous scalp–SEEG seizure-onset analysis is close prior art. The paper reports use of an MNI-template head model because scalp electrode coordinates were unavailable. EBRAINS indexes a versioned `v1` dataset record, but the exact file inventory and dataset-specific reuse terms were not verified; the paper's dataset site did not load during the metadata-only screen. It does not satisfy the participant-specific model contract for B2.
- A user-supplied B2 review text recommends approval of the registered B2 computation only. It does not review B8. The supplied verifier digest is malformed, and the reviewer affiliation differs across supplied versions, so workspace evidence does not authenticate the named reviewer. Do not treat this text alone as unaffiliated external B8 review.
