# Observable Geometry

Observable Geometry 0.1.3.dev0 is an unreleased development candidate for a computational-neuroscience software build around **Geometric-Informed Basis Functions (GBFs)** and a nominal EEG source-pattern comparison. The software asks what a declared forward model predicts at the sensors for pairs of candidate sources. It does not infer every active neural source, assign calibrated probabilities, or establish physiological source recovery.

The active contribution is a traceable GBFs implementation/reproduction workflow and an inspectable researcher-facing diagnostic. The normalized, noise-whitened source-pattern similarity is established prior art; this project does not claim that score as a new mathematical method. Track A's Localize-MI pulse-artifact evaluation is limited to one participant and an electrical stimulation artifact. It does not validate endogenous neural-source localization.

## Current project state

- **B0–B3:** passed at bounded scopes. This includes prior-art screening, one verified real model, the frozen nominal score, a CPU float64 implementation, tests, and a sealed model-only demonstration.
- **B4:** pivoted. A fresh 224-channel sub-01 rerun reproduces the existing pairwise CSV exactly, but the measured pulse artifact and tested source models do not support a neural-source validation claim. The previous 236/224-channel comparison is documented as invalid.
- **B5/B6:** pivoted without protocol lock or held-out evaluation because the available endpoint cannot validate endogenous neural-source distinguishability. No reserved outcomes were opened.
- **B7:** pivoted after a same-model, paired comparison found moderate association between the B3 score and MNE PSF summaries but no evidence of analyst decision benefit. Retain as a descriptive diagnostic only.
- **B8:** the BSD-3-Clause CLI package, source/wheel provenance check, isolated `0.1.3.dev0` install, and exact one-model output parity pass for current commit `3cfa693`. The commit also passes 211 workspace tests and 209 source-archive tests, with two documented archive-only skips, plus source-snapshot verification. See the [exact-commit B8 candidate report](docs/track_b/B8_RELEASE_CANDIDATE_3CFA693_20261029.md) and [review handoff record](docs/track_b/B8_REVIEW_HANDOFF_3CFA693_20261029.md). This remains an unreleased development candidate; unaffiliated outside review and the release decision are still open. The supplied B2 review is retained with its identity/authentication limitation.

### WSGZP geometry status

The WSGZP release supplies individual scalp-electrode coordinates and fiducials labeled `T1w`/millimetres. The dataset paper reports digitization and MRI coregistration, but the public export code copies values from `*_egi_dig.hpts` into BIDS without showing the upstream transform. The source digitizer files and participant registration QC are not present in the downloaded package. A 36-participant metadata/MRI screen found 57 electrodes outside the MRI field of view across eight participants; this is a triage result, not proof of a coordinate error or a geometry pass. Do not use WSGZP for participant-specific source analysis until the coordinate-frame provenance is confirmed and electrode-to-scalp geometry receives reviewed QC. See the [coordinate screen](docs/track_b/WSGZP_COORDINATE_COMPATIBILITY_SCREEN_20261029.md), [upstream pipeline audit](docs/track_b/WSGZP_UPSTREAM_COORDINATE_PIPELINE_AUDIT_20261029.md), and [geometry acceptance request](docs/track_b/WSGZP_COORDINATE_PROVENANCE_REQUEST.md).

### Localize-MI model-only extension

Seven Localize-MI participant forward FIFs are available locally and pass file-hash, leadfield-structure, channel-order, and internal transform-consistency checks. Together with the earlier all-participant metadata geometry audit, the maximum discrepancy between released scalp-electrode positions and forward sensor positions is 0.00866 mm; this establishes cross-file consistency, not endogenous source recovery. The data remain local under their CC BY-NC-SA 4.0 terms. See the [bundle audit](docs/track_b/LOCALIZEMI_FORWARD_BUNDLE_AUDIT_20261029.md), [participant geometry evidence](docs/track_b/B1_LOCAL_DATA_AUDIT.md), and [replayable audit script](scripts/track_b/audit_localizemi_forward_bundle.py).

See [the project definition](docs/track_b/PROJECT_DEFINITION.md), [the build plan](docs/track_b/GBF_BUILD_PLAN.md), the [B4 audit](docs/track_b/B4_DEVELOPMENT_AUDIT_20261024.md), the [B5/B6 route closeout](docs/track_b/B5_B6_ROUTE_CLOSEOUT_20261024.md), the [B7 decision-value audit](docs/track_b/B7_DECISION_VALUE_AUDIT_20261024.md), and the [gate register](docs/track_b/GATE_REGISTER.json).

## Install

Python 3.12 or later is required. From the project directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test,research-audit]"
```

Run the full workspace correctness and audit tests:

```powershell
python -m pytest -q
```

The `research-audit` extra supplies the HDF5, MRI and MNE dependencies used by repository audit tests; these are not required to install or use the researcher-facing CLI. In a full research workspace, the gate-register integration test also checks that every cited evidence path exists. A source-only archive intentionally omits those local run outputs, so that integration test is skipped there; run `python scripts/track_b/validate_gate_register.py` only from the complete workspace to validate the evidence paths.

The full research workspace also contains local dataset files, ignored build outputs, and the pinned upstream GBFs checkout. Those files are not included in a clean source installation. The Localize-MI data have a non-commercial share-alike license and must not be redistributed with this package. Superseded WBEN and synthetic-signal code is retained only under `archive/historical_wben/`; it is excluded from the installed package and normal test suite. Follow each dataset's current terms and citation instructions before acquiring or using it.

## Run the researcher-facing diagnostic

Prepare an NPZ bundle with exactly these arrays:

- `leadfield`: finite `n_sensors × n_sources` forward matrix.
- `noise_covariance`: finite `n_sensors × n_sensors` covariance using the same sensor order and reference.
- `coordinates_m`: finite `n_sources × 3` source coordinates in metres.
- Optional `source_ids`: one integer or string ID per source column.

The command rejects undeclared arrays, including a `data` member, before materializing them. A successful run records the allowed keys it reads; a rejected run reports the denied key on stderr and does not publish an output folder. This process-level guard prevents accidental access through this CLI; it is not a security sandbox.

Provide a JSON file describing the model. It must include nonempty strings for `dataset`, `participant`, `forward_model`, `reference`, `coordinate_frame`, `source_orientation`, and `noise_covariance`, plus a `sensor_names` array with one unique name per leadfield row. For example:

```json
{
  "dataset": "your dataset and version",
  "participant": "subject identifier",
  "forward_model": "forward solution and provenance",
  "reference": "electrode reference",
  "coordinate_frame": "coordinate frame",
  "source_orientation": "fixed or free orientation convention",
  "noise_covariance": "estimation window and method",
  "sensor_names": ["sensor-1", "sensor-2"]
}
```

Run the analysis into a new output directory. Existing output paths are never overwritten. Each command writes into a temporary sibling directory and publishes the finished result only after every output file is complete; a failed run removes its temporary directory so it cannot be mistaken for a completed result or block a retry.

```powershell
observable-geometry distinguish `
  --bundle .\model_bundle.npz `
  --metadata .\model_metadata.json `
  --output .\results\run-001 `
  --minimum-distance-mm 20 `
  --top-k 5
```

The output contains ranked source pairs, float64 scores, a JSON summary, input and code hashes, and an NPZ access log. Similarity is conditional on the supplied forward model, sensor reference, source family, and covariance. It is not a probability that a source will be localized correctly.

## Compare source-family claims across tolerances

The `family-frontier` command takes previously computed distance intervals for a reference source family and one or more alternatives. It reports whether each family fits, is excluded, or remains unresolved at a supplied tolerance. It also reports the half-open tolerance interval where a valid lower bound excludes the reference while a feasible alternative upper bound fits. This makes a source-family assumption change visible without choosing a single tolerance after seeing the result.

```powershell
observable-geometry family-frontier `
  --spec .\family_distances.json `
  --output .\results\family-frontier-001
```

The input has `tolerance` and a nonempty `cases` array. Each case has a unique `id`, one `reference` family and an `alternatives` array. Each family has a unique `name`, `evidence` label and `distance` with nonnegative `lower` and `upper` bounds. An exact numerical minimum can be supplied as equal bounds only when its numerical and modeling limitations are understood. A feasible witness without an exclusion certificate should use `lower: 0` and its replayed residual as `upper`.

This command **does not recompute or authenticate** supplied distances. It records the input hash and labels this limit in its output. A reversal is conditional on the source families, model and valid bounds; it is not measured source recovery or a composite-classifier error rate. A five-participant, 20-case worked input built from independently replayed research results is documented in [the family-frontier report](../research/gbf_omitted_activity_20261024/SECONDARY_FAMILY_FRONTIER_RESULTS_20261028.md) in the full workspace.

## Audit a target-only claim across a declared model set

The separate `robust-audit` command accepts a JSON specification with a fixed-field tolerance, anchor target and alternative residual certificates, a source amplitude limit, an alternative L1 budget, certified per-column forward radii, and one or more independently checked scenarios inside the declared uncertainty set. It returns **certified target only**, **refuted by an in-set scenario**, or **unresolved**. A single in-set target-fit failure refutes the universal claim; a loose radius never becomes a false certificate.

```powershell
observable-geometry robust-audit `
  --spec .\examples\robust_audit_toy.json `
  --output .\results\robust-audit-001
```

The source checkout's `examples/robust_audit_toy.json` is an **arithmetic illustration**, not simulated neural evidence. Its supplied bounds satisfy a positive certificate; the separate sub-01 research example demonstrates an in-set counterexample and the failure of a loose continuous bound. A wheel-only installation needs a user-supplied JSON spec in the same schema.

The input JSON must have exactly these fields: `parameter_interval`, `tolerance`, `anchor_target_residual_upper`, `anchor_alternative_residual_lower`, `anchor_alternative_residual_upper`, `target_amplitude_abs_upper`, `alternative_l1_budget`, `target_column_radius`, `alternative_column_radius_upper`, and `endpoints`. `parameter_interval` is a two-number range for the varied forward parameter. Each endpoint has a unique `name`, an in-range `parameter_value`, a separately established `target_residual_lower`, and optionally an `alternative_residual_upper`. The observed field, source units, sensor reference, whitening and source-family definitions must agree across all scenarios. The CLI checks numeric membership and decision arithmetic; it cannot authenticate those scientific assumptions or manufacture valid residual/radius certificates from arbitrary numbers.

Every CLI result includes `input_evidence_status=supplied_bounds_not_replayed_by_this_command`. The two included sub-01 research inputs have a separate hash and conservative-scalar replay in `research/gbf_omitted_activity_20261024/ROBUST_AUDIT_INPUT_REPLAY_RESULTS_20261028.md`. That replay is case-specific; it does not confer verification on other user-supplied specs.

The included sub-01 research example is documented in `research/gbf_omitted_activity_20261024/ROBUST_AUDIT_DECISION_RESULTS_20261027.md` in the full workspace. Its conductivity range and tolerance are illustrative. The three-way logic is standard triangle-inequality reasoning plus an in-set counterexample, not a novel source inverse or physiological validation.

## Reproduce the sealed Localize-MI model-only demonstration

In the full research workspace, with the sealed Track A artifacts present, first export only the allowed model arrays. The adapter validates the sealed artifact hashes, records each NPZ key read, and never indexes the recorded EEG `data` member:

```powershell
python scripts\track_b\export_sealed_model_bundle.py --output .\tmp\model_bundle_run1
observable-geometry distinguish `
  --bundle .\tmp\model_bundle_run1\model_bundle.npz `
  --metadata .\tmp\model_bundle_run1\model_metadata.json `
  --output .\outputs\track_b\your-new-run-id `
  --minimum-distance-mm 20 `
  --top-k 5
```

The original B3 reference command remains available as `python scripts\track_b\run_b3_distinguishability.py --run-id your-new-run-id`. Both commands refuse overwrites and do not read the EEG sample array. The exported model bundle is Localize-MI-derived and must stay local unless its license terms have been assessed. The Track A report and B4 rerun are development evidence for one participant and the pulse artifact only.

## Interpretation and research boundaries

The experimental [two-sided fixed-field audit API](docs/track_b/TWO_SIDED_AUDIT_API.md)
compares a favored source family and a finite union of constrained alternatives
against the same pre-whitened field. It returns feasible witnesses, weak-dual
lower bounds, and an explicit abstention state when neither family fits. This
is standard constrained-fitting mathematics implemented as inspectable
research software. The current conductivity example uses a synthetic field;
it does not establish physiological source attribution.

The equation, assumptions, prior art, data provenance, failures, and claim limits are documented in `docs/track_b/`. Historical NeuroFlowNet/WBEN experiments are archived and are not part of the active target. Active experimental work uses real recordings only; software correctness checks may use algebraic fixtures, but no synthetic neural dataset or signal is used as empirical evidence.

An optional [relative tail-closed frontier](docs/track_b/TAIL_CLOSED_RELATIVE_FRONTIER_20261029.md) evaluates the model-conditional separation margin relative to each retained field's gain, using a generalized eigenvalue form of the existing S-lemma bound. It is a finite-grid, model-only diagnostic, not a novel method or neural-source result. The full workspace includes a runner and a separate direct-matrix verifier under `scripts/track_b/`.

Track A remains sealed. Do not overwrite its outputs. Project source code is BSD-3-Clause licensed. This covers this repository's source only; it does not relicense the separately vendored GBFs checkout or any dataset. The Localize-MI data have a non-commercial share-alike license and are excluded from the package and source snapshot. External scientific/software review is not complete; treat the build as a research prototype until that review is completed.

The current B8 independent-review bundle is [available in the local handoff folder](reviewer_handoff/B8_Independent_Review_20261029_3cfa693.zip); its contents, integrity result, and claim limits are recorded in [the handoff report](docs/track_b/B8_REVIEW_HANDOFF_3CFA693_20261029.md).
