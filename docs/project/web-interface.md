# Local browser interface

The optional browser interface runs the `distinguish` diagnostic on your computer and helps inspect its outputs. It uses the same calculation and input checks as the command-line tool.

## Install and open

From a source checkout, using Python 3.12 or newer:

```powershell
python -m venv .web-env
.\.web-env\Scripts\python.exe -m pip install -e ".[web]"
.\.web-env\Scripts\observable-geometry-web.exe
```

Open `http://127.0.0.1:8501` if the browser does not open automatically. Stop the server with Ctrl+C. It binds to the local computer only.

## Try the arithmetic fixture

Choose **Run a model**. Set the bundle to `examples/browser_algebra_demo.npz` and metadata to `examples/browser_algebra_demo_metadata.json`. Choose a new output folder and run the diagnostic. This tiny hand-written matrix is only for learning the interface; it contains no recording, participant geometry or physiological result.

## Inspect a completed run

Provide the path to a completed output directory containing `ranked_pairs.csv`, `summary.json`, `scores.npz`, `npz_key_access.jsonl`, and `run_manifest.json`. The interface checks each output against the SHA-256 hashes in the manifest before displaying it. This detects accidental file changes; it does not independently validate the scientific model.

## Run a model

Provide absolute paths to a verified model-only NPZ bundle, its matching metadata JSON, and a new output directory. Set the minimum distance and number of alternatives, then run. The interface uses the same strict array-key checks and no-overwrite behavior as the CLI.

## Read the results

Review the score distribution, select a source to see ranked alternatives, inspect the distance-versus-score plot, and download the ranked CSV. The provenance panel displays input hashes and run parameters; the full manifest and key-access log remain in the output directory.

The public repository does not include the licensed participant model used for the recorded 40,980-row example. Scores are conditional on the supplied forward model and covariance. They are not probabilities of correct localization or evidence that a neural event was recovered. The browser interface is a local workflow, not a separate validation of the underlying method.
