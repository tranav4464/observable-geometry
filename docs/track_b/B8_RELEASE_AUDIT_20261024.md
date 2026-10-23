# B8 release preparation audit

**Date:** 24 October 2026
**Status:** **IN_PROGRESS** — local software release checks, clean-wheel reproduction, and committed source-snapshot verification pass; unaffiliated outside review or independent reproduction remains open.

## What is complete

The public-facing `observable-geometry` entry point runs the active nominal GBF source-pattern diagnostic. It accepts an explicit leadfield/covariance/coordinate bundle and provenance JSON, refuses overwrite, rejects unlisted NPZ arrays before materializing them, and writes ranked pairs, float64 scores, a summary, hashes, and an access log. Superseded WBEN and synthetic-signal modules have been moved to `archive/historical_wben/`; they are excluded from the installed package and default test path.

The sealed-model adapter `scripts/track_b/export_sealed_model_bundle.py` verifies the Track A manifest hashes and reads only `leadfield`, `noise_cov`, `source_coordinates`, and `vertex_ids`. Its key-level log contains no EEG `data` access. The export is data-derived and kept in ignored local `tmp/`; neither Localize-MI recordings nor the derivative bundle are part of the source package.

The CLI was installed from a cleanly staged 0.1.2 wheel (built outside the stale repository build directory) in a fresh Python 3.12.14 virtual environment with NumPy 2.5.4. The wheel declares BSD-3-Clause and includes its license text. The fresh environment reproduced the source-environment output exactly on the same sealed model-only bundle:

- 8,196 source columns and 236 sensors, with covariance support rank 235.
- 40,980 ranked pairs; source/candidate indices, IDs, rankings, cosine scores and profiled residuals matched exactly.
- The ranked-pair CSV was byte-identical across environments (SHA-256 `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`).
- The rebuilt wheel declares `License-Expression: BSD-3-Clause`, includes `License-File: LICENSE`, and the separate verifier checks that the license file is present in the wheel.
- The deliverable wheel is `outputs/track_b/20261024_b8_release_checks/release_artifacts/observable_geometry-0.1.2-py3-none-any.whl`; SHA-256 `dc8b241e0320c901d98cf65dc626c8d1131c2f2b6caae6a4bb51b916cce02100`. The earlier 0.1.1 wheel was found to contain stale archived modules from the repository build directory; its failed check and wheel are preserved under `failed_artifacts/` and `clean_install_parity_stale_build_failure_01.json`.
- Summary values matched exactly: median best distant cosine `0.915556984605132`, 90th percentile `0.9453457802989496`, and fraction at or above `0.95` of `0.06039531478770132`.
- The normal test command, `python -m pytest -q`, passes all 79 full-workspace tests. The two legacy simulator/WBEN test modules are archived outside `tests/`, so this result requires no exclusion flags.
- The clean-wheel verifier confirms that `synthetic.py`, `physical_synthetic.py`, and `wben.py` are absent from the installed package.
- The gate-register validator passes with B0–B3 at PASS, B4–B7 at PIVOT, and B8 at IN_PROGRESS as listed in the register.
- The source-only snapshot contains 182 hashed files and is committed. The clean-tree verifier records the current commit, tree, and manifest SHA-256 in `outputs/track_b/20261024_b8_release_checks/source_snapshot_verification.json`.

The B8 handoff build is reproducible with `scripts/track_b/build_b8_reviewer_handoff.py` from a clean, committed source snapshot. The current extracted source-only Git archive passes 78 tests with one evidence-path integration check skipped because local evidence outputs are excluded. Two earlier failed archive runs are preserved as `source_archive_failure_01.json` and `source_archive_failure_02.json`. The strict evidence validator remains unchanged and runs separately in the full repository. The skip means omitted evidence paths were not verified by the archive; it is not a gate pass. Exact archive hash and test output are recorded in `outputs/track_b/20261024_b8_source_archive_tests/`.

Full output and run evidence are under `outputs/track_b/20261024_b8_release_checks/`, `outputs/track_b/20261024_b8_export_cli_source_env_v1/`, and `outputs/track_b/20261024_b8_export_cli_clean_env_v4/`. The v1–v3 clean-environment runs are retained as earlier checks; v4 verifies the final 0.1.2 wheel. Temporary staging, wheels, and data-derived model bundles are under ignored `tmp/`.

One first version of the B8 comparison verifier failed on a Unicode source-ID array because it used a floating-array NaN comparison option. That verifier failure is preserved in `outputs/track_b/20261024_b8_release_checks/clean_install_parity_failure_01.json`; the verifier was corrected and the independent package comparison passed. A later package audit found and corrected stale build contents in wheel 0.1.1. No model computation changed.

The B7 audit now pairs all 8,196 B3 source scores with the sealed MNE PSF summaries from the same 236-channel forward model. Spearman associations range from `−0.393` to `0.480`; the top-decile comparison is descriptive only. An independent SciPy recomputation of the five rank correlations agrees to maximum absolute error `1.11e-16`. This establishes a paired model-output comparison, not a researcher utility result. B7 follows its pivot route and no utility claim is retained. B5/B6 likewise have explicit pivot closeout records; no held-out outcomes were opened.

The updated prior-art and dataset screen records Wang et al. 2026 as the direct GBF source and notes its localization analysis of 318 sessions from 35 participants on the public iES-CCEP route. The same paper also evaluates GBF on 24 favourable-outcome participants from HDEEG-IED-SurgOutcome. The 2025 data descriptor reports 44 patients, while an older UNIGE landing-page summary says 45; the versioned release manifest and participant table must settle the denominator before any protocol is frozen. The dataset includes individual MRI, electrode coordinates, averaged interictal discharges, resection imaging, and 12-month outcomes. It is a possible post-publication secondary evaluation, not an untouched external cohort; EBRAINS registration and dataset-specific terms must be checked before access, and any remaining held-out cases must be identified without outcome inspection. A separate 2023 simultaneous scalp/SEEG stimulation study with individual FEM models offers a future collaboration route, but its data are available only from the authors upon reasonable request. No author has been contacted. The iES-CCEP OSF metadata reviewed do not give an explicit dataset license. No outcome analysis is authorized until the candidate, terms, exact overlap, and a reviewed protocol are resolved. These findings narrow the scientific claims; they do not change the bounded software-release evidence above.

## What remains before B8 can pass

1. **Outside review or reproduction:** no unaffiliated external reviewer has inspected the final package or independently reproduced the clean run. The supplied B2 review concerns only the registered B2 computation and does not satisfy B8.
2. **B2 review record limitation:** supplied review versions contain different affiliation declarations and a malformed digest transcription. The registered computation passes, but the supplied external identity cannot be represented as independently authenticated based on this workspace alone.
3. **Public distribution:** this is a committed local software release; no public repository URL or DOI is claimed. The wheel and data-derived model bundle are kept in ignored local build/output directories. Datasets, vendored GBFs, and data-derived outputs remain outside the source release under their separate terms.

## Claim boundary

This audit establishes packaging and exact numerical reproduction of the declared nominal diagnostic on one real participant-specific model. It does not validate endogenous neural-source localization, calibrated recoverability, population generalization, superiority over established methods, or researcher decision utility. B4–B7 are pivoted; no B5/B6 held-out analysis was run.

## Review packet

Use `B8_EXTERNAL_REVIEW_PACKET_20261024.md` for the remaining independent package and scientific-scope check. Do not describe the build as a new scientific discovery or novel mathematical framework unless later evidence independently supports that claim.
