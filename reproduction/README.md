# Reproducing Observable Geometry run outputs

This folder makes the selected portable run records available alongside the public source repository. It is a reproducibility aid, not a copy of the local workspace or the dataset.

## Included artifacts

- `run_outputs/portable_run_outputs_20261102.zip` contains 2,118 selected portable CSV, JSON, text, report, and log files.
- `run_outputs/run_output_manifest.csv` maps each archive member to its former Build-relative path, byte length, and SHA-256.
- `run_outputs/portable_run_outputs_20261102.sha256` gives the archive checksum.
- `local_only_array_manifest.csv` records hashes for selected model/result arrays that are deliberately not distributed.

The archive was checked for ZIP integrity. Its text files were checked for local-account paths, credentials, email addresses, and AI-authorship statements. Internal drafts and duplicate review materials were omitted. The archive does not contain EEG/iEEG samples, participant-specific arrays, forward FIF files, BEM/source-model binaries, Python environments, or caches.

## What the main numerical output says

The saved `ranked_pairs.csv` files include repeated runs of a nominal model-only diagnostic. The canonical repeated CSV has 40,980 rows and SHA-256 `847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4`. It lists five distant alternatives for each of 8,196 source locations at a 20 mm minimum separation. In the associated `summary.json`, the median best distant absolute cosine is about 0.916 and the 90th percentile is about 0.945.

These numbers describe similarity between **predicted scalp patterns** under one participant-specific forward model, reference, source orientation, and covariance. They are not localization probabilities, measured neural-source recovery, or population-level evidence. The rows are repeated saved outputs, not 37 independent experiments.

## Rebuild the software checks

Use Python 3.12 or newer. In a fresh checkout of this public repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,research-audit,web,figures]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\observable-geometry.exe --help
```

The repository's arithmetic/demo examples test software behavior only. They are not neural measurements.

## Reacquire data and regenerate the participant-model output

The recorded Localize-MI participant-model result depends on the provider's Localize-MI dataset, including the sub-01 forward solution, selected epoch files, and surfaces. The dataset is available from [GIN Localize-MI](https://gin.g-node.org/ezemikulan/Localize-MI) under its stated **CC BY-NC-SA 4.0** terms. Follow the provider's attribution and noncommercial/share-alike conditions. This repository does not redistribute the data.

The pinned acquisition and preparation route is in `scripts/bootstrap_foundation.ps1`, `scripts/fetch_localize.py`, and `scripts/run_foundation.ps1`. In a clean checkout, install the foundation requirements and run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/foundation.txt
$env:TRACKA_RUN_ID = "tracka_release_20261022_v2"
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_foundation.ps1 -PythonExePath .\.venv\Scripts\python.exe
```

This acquisition route fetches the project-selected sub-01 files and runs the foundation workflow. It requires enough local storage and network access to the provider. The output is participant/model-derived and should remain local unless its redistribution terms are separately confirmed.

After the sealed Track A output is present, export the allowlisted model-only arrays and run the CLI:

```powershell
$modelDir = Join-Path $PWD "tmp\model_export_reproduction"
.\.venv\Scripts\python.exe .\scripts\track_b\export_sealed_model_bundle.py --output $modelDir
$resultDir = Join-Path $PWD "outputs\distinguish_reproduction"
.\.venv\Scripts\observable-geometry.exe distinguish `
  --bundle (Join-Path $modelDir "model_bundle.npz") `
  --metadata (Join-Path $modelDir "model_metadata.json") `
  --output $resultDir `
  --minimum-distance-mm 20 `
  --top-k 5
```

The exporter records the model-array keys it reads and does not read the recorded EEG `data` member. Compare the regenerated `ranked_pairs.csv`, `summary.json`, and manifest with the archived copies. The archived run manifest stores the model and metadata input hashes, source-module hashes, runtime versions, parameters, and output checksums. Matching the dataset name is insufficient for exact reproduction: the generated model and metadata hashes must match too. If they differ, record the discrepancy instead of calling the output an exact reproduction.

## Limits

- Reproducing a model-conditioned result is different from validating endogenous neural-source recovery.
- The Localize-MI pulse-artifact endpoint is not ground truth for spontaneous neural-source localization.
- These outputs do not establish a novel method, calibrated uncertainty, or generalization across participants.
- The WSGZP electrode-to-MRI registration question is separate and remains unresolved by these Localize-MI outputs.
- The dataset's continued availability is controlled by its provider; the scripts document the route, but cannot guarantee future access.