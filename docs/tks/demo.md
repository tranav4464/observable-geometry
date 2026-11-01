# Demonstrating Observable Geometry

## Inspect without installing

Open `index.html` in the repository, or `START_HERE.html` in the submission bundle. The displayed numbers are recorded results from the verified model-only run, not a live analysis of a visitor's EEG.

## Install the tested wheel

Extract the submission ZIP. Python 3.12+ is required. In PowerShell from that extracted folder:

```powershell
python -m venv .demo-env
.\.demo-env\Scripts\python.exe -m pip install .\package\observable_geometry-0.1.3.dev1-py3-none-any.whl numpy==2.5.4 scipy==1.18.1
.\.demo-env\Scripts\observable-geometry.exe --help
```

Python package installation requires package-index access or a complete dependency wheelhouse. The bundle does not include one. The exact full audit environment is listed in `evidence/requirements_resolved.txt`.

## Run with your own verified model

```powershell
.\.demo-env\Scripts\observable-geometry.exe distinguish --bundle "C:\path\to\model_bundle.npz" --metadata "C:\path\to\model_metadata.json" --output .\demo-results --minimum-distance-mm 20 --top-k 5
```

Replace the two input paths. Choose a new output folder each time. The diagnostic refuses to overwrite an existing result. See the input schema in the source archive's README or the public repository. No participant recording arrays should be put into the bundle.

## Run a public data-free example

From a clone of the public repository, create a Python 3.12+ environment and run the separate `robust-audit` workflow:

```powershell
python -m venv .demo-env
.\.demo-env\Scripts\python.exe -m pip install -e .
$demoOutput = Join-Path $PWD ('robust-demo-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
.\.demo-env\Scripts\observable-geometry.exe robust-audit --spec .\examples\robust_audit_toy.json --output $demoOutput
Get-Content (Join-Path $demoOutput 'result.json')
```

This is an arithmetic example, not a source-imaging result. The main `distinguish` diagnostic requires a compatible model bundle and metadata as described above. The licensed sub-01 inputs used for the 8,196-source, 40,980-row result are not distributed in the public repository or submission ZIP. A reviewer without those inputs can inspect its recorded replay evidence but cannot independently regenerate that participant result from the public package alone.

## Two-minute walkthrough

1. Explain the problem: different sources can produce similar scalp patterns under a model.
2. Show the four allowed model arrays and the metadata contract.
3. Run `distinguish` with a verified model, or show the recorded model-only audit and run the public arithmetic example.
4. Show a query source and its ranked distant alternatives in the CSV. Explain that cosine is pattern similarity, not probability.
5. Show the hashes and access log, then the audit result.
6. Close with the use case and limitation: inspect model ambiguity before interpreting a source estimate; physiological validation and decision advantage remain future work.

## Verify the source and bundle

The packaged source commit is recorded in the bundle README and SHA-256 manifest. The accepted numerical snapshot was commit `3c99ca1`; later package archives can include documentation and tests added after acceptance without changing the diagnostic implementation. Current acceptance is described in the outer submission documents. After extracting the source, install pytest, h5py, MNE and nibabel in a virtual environment, set PYTHONPATH to its `src` folder and run `python -m pytest -q -ra`. The two archive skips are expected; a downloaded source archive does not include the private workspace evidence or WSGZP dataset.

## Rebuild the submission

See [the clean-checkout build instructions](building-submission.md). All artifact paths and output destinations are explicit.
