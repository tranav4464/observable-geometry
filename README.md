# Observable Geometry

**Observable Geometry is open-source research software for inspecting when candidate brain sources have similar predicted EEG patterns under a supplied forward model.** It helps researchers examine a model's spatial ambiguity before interpreting a source estimate.

## What it does

Given a sensor-by-source leadfield, a matching noise covariance, source coordinates and model metadata, the diagnostic:

1. whitens the predicted scalp patterns using the covariance's supported subspace;
2. normalizes pattern magnitude and compares candidates with an absolute cosine score;
3. excludes pairs closer than a user-chosen distance; and
4. saves the highest-similarity alternatives with input/output hashes and an access log.

The command-line tool and optional local browser interface use the same calculation. The browser can display score distributions, a selected source's ranked alternatives, and a distance-versus-score plot.

## Scientific scope

This is an **exploratory, model-conditional diagnostic**. The similarity calculation is established mathematics, not a new method claim. A high score means two modeled sources predict similar sensor patterns under the supplied inputs. It is not a probability, proof that either source was active, or evidence of accurate recovery from a measured neural event.

The public example is a small arithmetic fixture for learning the interface. Licensed participant inputs are not included. The project has not established endogenous neural-source recovery, improved researcher decisions, or generalization across participants. See [the method and limitations](docs/foundation/mathematics.md) and [the project overview](docs/project/project-overview.md).

## Install

Python 3.12 or newer is required.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\observable-geometry.exe --help
```

For the local browser interface:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[web]"
.\.venv\Scripts\observable-geometry-web.exe
```

Open `http://127.0.0.1:8501`. The browser interface runs on your computer; it does not upload model files to a hosted service.

## Try the public example

The arithmetic example demonstrates the interface and output format. It is not EEG data or a neuroscience result.

```powershell
$demoOutput = Join-Path $PWD ('demo-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
.\.venv\Scripts\observable-geometry.exe robust-audit --spec .\examples\robust_audit_toy.json --output $demoOutput
Get-Content (Join-Path $demoOutput 'result.json')
```

To run `distinguish` on a research model, provide a compatible model-only NPZ, matching metadata JSON, and a new output directory. See [the user guide](docs/project/demo.md) for the input contract and an example command. Never put recorded EEG samples into the model bundle.

## Output

A `distinguish` run writes ranked candidate pairs, score arrays, a summary, a run manifest containing hashes and parameters, and a record of which NPZ keys were accessed. Results are not overwritten; use a new output directory for each run.

## Project documents

- [Project overview and claim limits](docs/project/project-overview.md)
- [Installation and demonstration guide](docs/project/demo.md)
- [Local browser guide](docs/project/web-interface.md)
- [Architecture](docs/foundation/architecture.md)
- [Mathematical definition](docs/foundation/mathematics.md)
- [Validation scope](docs/foundation/validation.md)
- [Recorded results and limitations](docs/project/results-and-limits.md)
- [Article: When Two Brain Locations Look Alike to EEG](docs/project/article-1-observable-geometry.md)
- [Article: A Brain Map Can Look Right. How Would We Know It Is?](docs/project/article-2-source-validation.md)
- [Documentation index](docs/README.md)

## License and data

Project source is licensed under BSD 3-Clause. This does not relicense upstream GBFs code or any dataset. Obtain data directly from their providers, follow their license and access conditions, and prepare participant-specific model inputs locally.
