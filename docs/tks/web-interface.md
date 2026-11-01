# Observable Geometry: local browser interface

This optional interface helps a researcher run the existing `distinguish` diagnostic and read its outputs. It does not change the similarity calculation or turn the score into a source-recovery result.

## Install and open

From a clone of the repository, using Python 3.12 or newer:

```powershell
python -m venv .web-env
.\.web-env\Scripts\python.exe -m pip install -e ".[web]"
.\.web-env\Scripts\observable-geometry-web.exe
```

Open `http://127.0.0.1:8501` if your browser does not open automatically. Stop the server with Ctrl+C. It binds to this computer only. The optional `Web Interface` folder in the TKS handoff contains a versioned wheel if you prefer that to a source checkout. From that folder, install it with `python -m pip install .\observable_geometry-0.1.3.dev2-py3-none-any.whl streamlit pandas`, then run `observable-geometry-web`.

On a machine where Streamlit has never been started, Streamlit may first ask for an optional email address in the terminal. Press Enter to leave it blank; the local server then starts. This is Streamlit's initial setup, not a prompt from Observable Geometry.

## Use it

### Try the public arithmetic demo first

Choose **Run a model**. Set the bundle to the absolute path of `examples/browser_algebra_demo.npz` and metadata to `examples/browser_algebra_demo_metadata.json` in the repository, or use the copies beside this guide in the TKS handoff. Choose a new output folder and click **Run diagnostic**. Then select a source to see its alternatives. This four-source matrix is handwritten arithmetic for learning the interface. It contains no EEG recording, participant geometry or physiological source result.


- **Inspect an existing run:** enter the absolute path to a completed `distinguish` output directory containing `ranked_pairs.csv`, `summary.json`, `scores.npz`, `npz_key_access.jsonl`, and `run_manifest.json`. The interface checks each file against the manifest's SHA-256 hash before display. This detects accidental or unrecorded file changes, but a self-authored manifest is not independent proof of scientific validity. Inspection works without participant model inputs if you already have a completed run.
- **Run a model:** enter absolute paths to a verified model-only NPZ bundle, matching metadata JSON and a new output directory. Set the minimum straight-line distance and number of alternatives. The interface invokes the same diagnostic as `observable-geometry distinguish` and preserves its strict array-key checks and no-overwrite behavior.
- **Read results:** review the distribution of each source's best eligible score, choose one source to see its ranked alternatives, inspect the distance-versus-score plot, and download the CSV. The provenance panel shows input hashes and run parameters; the full manifest and key-access log remain in the output directory.

The included public package does not contain the licensed Localize-MI participant model used for the recorded 40,980-row example. Scores are conditional on the supplied forward model and covariance; they are not a probability of correct localization. The original 0.1.3.dev1 TKS ZIP is the accepted bounded CLI snapshot. Version 0.1.3.dev2 is this additional local browser iteration and has not received a separate external review.
