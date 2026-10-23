# Observable Geometry

Observable Geometry 0.1.2 is a computational-neuroscience software build around **Geometric-Informed Basis Functions (GBFs)** and a nominal EEG source-pattern comparison. The software asks what a declared forward model predicts at the sensors for pairs of candidate sources. It does not infer every active neural source, assign calibrated probabilities, or establish physiological source recovery.

The active contribution is a traceable GBFs implementation/reproduction workflow and an inspectable researcher-facing diagnostic. The normalized, noise-whitened source-pattern similarity is established prior art; this project does not claim that score as a new mathematical method. Track A's Localize-MI pulse-artifact evaluation is limited to one participant and an electrical stimulation artifact. It does not validate endogenous neural-source localization.

## Current project state

- **B0–B3:** passed at bounded scopes. This includes prior-art screening, one verified real model, the frozen nominal score, a CPU float64 implementation, tests, and a sealed model-only demonstration.
- **B4:** pivoted. A fresh 224-channel sub-01 rerun reproduces the existing pairwise CSV exactly, but the measured pulse artifact and tested source models do not support a neural-source validation claim. The previous 236/224-channel comparison is documented as invalid.
- **B5/B6:** pivoted without protocol lock or held-out evaluation because the available endpoint cannot validate endogenous neural-source distinguishability. No reserved outcomes were opened.
- **B7:** pivoted after a same-model, paired comparison found moderate association between the B3 score and MNE PSF summaries but no evidence of analyst decision benefit. Retain as a descriptive diagnostic only.
- **B8:** the BSD-3-Clause CLI package and clean model-only reproduction pass. The source-only manifest is committed and verified. An unaffiliated external review remains open; the B2 review is retained with its identity/authentication limitation.

See [the project definition](docs/track_b/PROJECT_DEFINITION.md), [the build plan](docs/track_b/GBF_BUILD_PLAN.md), the [B4 audit](docs/track_b/B4_DEVELOPMENT_AUDIT_20261024.md), the [B5/B6 route closeout](docs/track_b/B5_B6_ROUTE_CLOSEOUT_20261024.md), the [B7 decision-value audit](docs/track_b/B7_DECISION_VALUE_AUDIT_20261024.md), and the [gate register](docs/track_b/GATE_REGISTER.json).

## Install

Python 3.12 or later is required. From the project directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Run the focused correctness tests:

```powershell
python -m pytest -q
```

The full research workspace also contains local dataset files, ignored build outputs, and the pinned upstream GBFs checkout. Those files are not included in a clean source installation. The Localize-MI data have a non-commercial share-alike license and must not be redistributed with this package. Superseded WBEN and synthetic-signal code is retained only under `archive/historical_wben/`; it is excluded from the installed package and normal test suite. Follow each dataset's current terms and citation instructions before acquiring or using it.

## Run the researcher-facing diagnostic

Prepare an NPZ bundle with exactly these arrays:

- `leadfield`: finite `n_sensors × n_sources` forward matrix.
- `noise_covariance`: finite `n_sensors × n_sensors` covariance using the same sensor order and reference.
- `coordinates_m`: finite `n_sources × 3` source coordinates in metres.
- Optional `source_ids`: one integer or string ID per source column.

The command rejects undeclared arrays, including a `data` member, before materializing them. It records the allowed keys it reads. This process-level guard prevents accidental access through this CLI; it is not a security sandbox.

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

Run the analysis into a new output directory. Existing output paths are never overwritten.

```powershell
observable-geometry distinguish `
  --bundle .\model_bundle.npz `
  --metadata .\model_metadata.json `
  --output .\results\run-001 `
  --minimum-distance-mm 20 `
  --top-k 5
```

The output contains ranked source pairs, float64 scores, a JSON summary, input and code hashes, and an NPZ access log. Similarity is conditional on the supplied forward model, sensor reference, source family, and covariance. It is not a probability that a source will be localized correctly.

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

The equation, assumptions, prior art, data provenance, failures, and claim limits are documented in `docs/track_b/`. Historical NeuroFlowNet/WBEN experiments are archived and are not part of the active target. Active experimental work uses real recordings only; software correctness checks may use algebraic fixtures, but no synthetic neural dataset or signal is used as empirical evidence.

Track A remains sealed. Do not overwrite its outputs. Project source code is BSD-3-Clause licensed. This covers this repository's source only; it does not relicense the separately vendored GBFs checkout or any dataset. The Localize-MI data have a non-commercial share-alike license and are excluded from the package and source snapshot. External scientific/software review is not complete; treat the build as a research prototype until that review is completed.
