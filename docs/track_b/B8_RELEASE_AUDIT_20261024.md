# B8 release preparation audit

**Date:** 24 October 2026
**Status:** **IN_PROGRESS** — clean package reproduction and source licensing pass; source-manifest verification and local version-control provenance are being finalized; unaffiliated outside review remains open.

## What is complete

The public-facing `observable-geometry` entry point now runs the active nominal GBF source-pattern diagnostic. It accepts an explicit leadfield/covariance/coordinate bundle and provenance JSON, refuses overwrite, rejects unlisted NPZ arrays before materializing them, and writes ranked pairs, float64 scores, a summary, hashes, and an access log. The older conditional linear-Gaussian prototype remains available as a library module but is not the active CLI.

The sealed-model adapter `scripts/track_b/export_sealed_model_bundle.py` verifies the Track A manifest hashes and reads only `leadfield`, `noise_cov`, `source_coordinates`, and `vertex_ids`. Its key-level log contains no EEG `data` access. The export is data-derived and kept in ignored local `tmp/`; neither Localize-MI recordings nor the derivative bundle are part of the source package.

The CLI was installed from a rebuilt wheel in a fresh Python 3.12.14 virtual environment with NumPy 2.5.4. The wheel declares BSD-3-Clause and includes its license text. The fresh environment reproduced the source-environment output exactly on the same sealed model-only bundle:

- 8,196 source columns and 236 sensors, with covariance support rank 235.
- 40,980 ranked pairs; source/candidate indices, IDs, rankings, cosine scores and profiled residuals matched exactly.
- The ranked-pair CSV was byte-identical across environments (SHA-256 `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`).
- The rebuilt wheel declares `License-Expression: BSD-3-Clause`, includes `License-File: LICENSE`, and the separate verifier checks that the license file is present in the wheel.
- Summary values matched exactly: median best distant cosine `0.915556984605132`, 90th percentile `0.9453457802989496`, and fraction at or above `0.95` of `0.06039531478770132`.
- The applicable repository tests pass 76/76. The two historical WBEN test modules were excluded because they generate simulated signal sequences; the active project does not use synthetic neural signals as evidence.
- The gate-register validator passes with B0–B3 at PASS, B4–B7 at PIVOT, and B8 at IN_PROGRESS as listed in the register.

Full output and run evidence are under `outputs/track_b/20261024_b8_release_checks/`, `outputs/track_b/20261024_b8_export_cli_source_env_v1/`, and `outputs/track_b/20261024_b8_export_cli_clean_env_v2/`. The earlier clean-env run is retained under `...clean_env_v1/`; v2 is the final rebuilt-wheel check. Temporary wheel and data-derived model bundles are under ignored `tmp/`.

One first version of the B8 comparison verifier failed on a Unicode source-ID array because it used a floating-array NaN comparison option. That verifier failure is preserved in `outputs/track_b/20261024_b8_release_checks/clean_install_parity_failure_01.json`; the verifier was corrected and the independent package comparison passed. No model computation changed.

The B7 audit now pairs all 8,196 B3 source scores with the sealed MNE PSF summaries from the same 236-channel forward model. Spearman associations range from `−0.393` to `0.480`; the top-decile comparison is descriptive only. An independent SciPy recomputation of the five rank correlations agrees to maximum absolute error `1.11e-16`. This establishes a paired model-output comparison, not a researcher utility result. B7 follows its pivot route and no utility claim is retained. B5/B6 likewise have explicit pivot closeout records; no held-out outcomes were opened.

## What remains before B8 can pass

1. **Outside review or reproduction:** no unaffiliated external reviewer has inspected the final package or independently reproduced the clean run. The B2 review concerns only the registered B2 computation and does not satisfy B8. The review packet now includes the B4–B7 empirical/utility route decisions.
2. **B2 review record limitation:** the workspace contains conflicting reviewer-identity declarations and a malformed digest transcription. The registered computation passes, but the supplied external identity cannot be represented as independently authenticated based on this workspace alone.
3. **Release provenance:** a source-only hash manifest and a verifier that requires a clean committed tree are part of the build. The manifest excludes datasets, vendored checkouts, environments, reviewer handoff files, and run outputs. The verifier writes its report under the ignored B8 release-check output folder. Data, vendored GBFs, and data-derived model/output bundles remain outside the source release under their separate terms.
4. **Citation metadata:** `CITATION.cff` records the software citation. No DOI or public repository URL is claimed.

## Claim boundary

This audit establishes packaging and exact numerical reproduction of the declared nominal diagnostic on one real participant-specific model. It does not validate endogenous neural-source localization, calibrated recoverability, population generalization, superiority over established methods, or researcher decision utility. B4–B7 are pivoted; no B5/B6 held-out analysis was run.

## Review packet

Use `B8_EXTERNAL_REVIEW_PACKET_20261024.md` for the remaining independent package and scientific-scope check. Do not describe the build as a new scientific discovery or novel mathematical framework unless later evidence independently supports that claim.
