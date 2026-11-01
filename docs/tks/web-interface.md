# Observable Geometry: local browser interface

This optional interface helps a researcher run the existing `distinguish` diagnostic and read its outputs. It does not change the similarity calculation or turn the score into a source-recovery result.

## Install and open

From a clone of the repository, using Python 3.12 or newer:

```powershell
python -m venv .web-env
.\.web-env\Scripts\python.exe -m pip install -e ".[web]"
.\.web-env\Scripts\observable-geometry-web.exe
```

Open `http://127.0.0.1:8501` if your browser does not open automatically. Stop the server with Ctrl+C. It binds to this computer only. The optional `Web Interface` folder in the TKS handoff contains a versioned wheel if you prefer to install that instead of a source checkout; install it along with `streamlit` and `pandas`.

## Use it

- **Inspect an existing run:** enter the absolute path to a completed `distinguish` output directory containing `ranked_pairs.csv` and `summary.json`. This works without participant model inputs if you already have a completed run.
- **Run a model:** enter absolute paths to a verified model-only NPZ bundle, matching metadata JSON and a new output directory. Set the minimum straight-line distance and number of alternatives. The interface invokes the same diagnostic as `observable-geometry distinguish` and preserves its strict array-key checks and no-overwrite behavior.
- **Read results:** review the distribution of each source's best eligible score, choose one source to see its ranked alternatives, inspect the distance-versus-score plot, and download the CSV. The provenance panel shows input hashes and run parameters; the full manifest and key-access log remain in the output directory.

The included public package does not contain the licensed Localize-MI participant model used for the recorded 40,980-row example. Scores are conditional on the supplied forward model and covariance; they are not a probability of correct localization. The original 0.1.3.dev1 TKS ZIP is the accepted bounded CLI snapshot. Version 0.1.3.dev2 is this additional local browser iteration and has not received a separate external review.
