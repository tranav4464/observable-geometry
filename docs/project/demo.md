# Running Observable Geometry

## Inspect the interface

Open `index.html` in a browser for the project overview. The small public examples demonstrate software behavior only; they do not analyze EEG recordings or represent a neural-source result.

## Install from a source checkout

Python 3.12 or newer is recommended. From PowerShell:

```powershell
python -m venv .demo-env
.\.demo-env\Scripts\python.exe -m pip install -e .
.\.demo-env\Scripts\observable-geometry.exe --help
```

To install the optional browser interface instead, use `python -m pip install -e ".[web]"` and run `observable-geometry-web`.

## Try the data-free example

```powershell
$demoOutput = Join-Path $PWD ('robust-demo-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
.\.demo-env\Scripts\observable-geometry.exe robust-audit --spec .\examples\robust_audit_toy.json --output $demoOutput
Get-Content (Join-Path $demoOutput 'result.json')
```

This arithmetic fixture tests the command and output format. It is not EEG, simulated neural activity, or scientific validation.

## Run the source-pattern diagnostic

Prepare a model-only NPZ bundle, matching metadata JSON, and a new output path. Then run:

```powershell
.\.demo-env\Scripts\observable-geometry.exe distinguish --bundle "C:\path\to\model_bundle.npz" --metadata "C:\path\to\model_metadata.json" --output .\model-audit --minimum-distance-mm 20 --top-k 5
```

The model bundle contains a sensor-by-source leadfield and covariance; the metadata describes sensor order/reference, source coordinates and model provenance. Recorded EEG sample arrays are not inputs to this diagnostic. Use a new output directory for each run. The tool refuses to overwrite existing results.

Outputs include ranked pairs, score arrays, a summary, a run manifest with hashes and parameters, and an archive-key access record. A high cosine score means similar predicted sensor patterns under the supplied model. It is not a probability that the sources are indistinguishable in a real recording.

## Local browser workflow

See the [browser guide](web-interface.md) to run or inspect a completed output locally. The interface binds to `127.0.0.1` and does not upload files to a hosted service.

## Reproducibility notes

The repository includes software regression tests and recorded model-only evidence. Licensed participant inputs are not distributed here, so an independent reader can run the arithmetic example but cannot reproduce the participant-specific result without lawful access to matching model inputs. The project overview describes exactly what the existing evidence supports and what remains unvalidated.
