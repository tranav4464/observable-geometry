# Demonstrating Observable Geometry

## Inspect without installing

Open `TKS_BUILD.html` in the repository, or `START_HERE.html` in the submission bundle. The displayed numbers are recorded results from the verified model-only run, not a live analysis of a visitor's EEG.

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

## Tranav's local live demo

On the existing full workspace, use this previously verified wheel environment and model export. This convenience command is specific to this machine; it is not a portable data-download procedure.

```powershell
Set-Location 'C:\Users\TRANAV\OneDrive\Desktop\TKS\observable_geometry'
$demoOutput = Join-Path $PWD ('outputs/track_b/tks_demo_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
& .\outputs\track_b\astra_b8_audit_20261030\env\Scripts\observable-geometry.exe distinguish --bundle .\outputs\track_b\20261029T_atomic_cli_real_model_reproduction\model_export\model_bundle.npz --metadata .\outputs\track_b\20261029T_atomic_cli_real_model_reproduction\model_export\model_metadata.json --output $demoOutput --minimum-distance-mm 20 --top-k 5
Get-Content (Join-Path $demoOutput 'summary.json')
Import-Csv (Join-Path $demoOutput 'ranked_pairs.csv') | Select-Object -First 5
```

Expected model size: 8,196 sources, covariance rank 235, 40,980 ranked rows. Changing model inputs or options changes the result. Preserve the original sealed files.

## Two-minute walkthrough

1. Explain the problem: different sources can produce similar scalp patterns under a model.
2. Show the four allowed model arrays and the metadata contract.
3. Run `distinguish`, or open the already executed audit output if time is short.
4. Show a query source and its ranked distant alternatives in the CSV. Explain that cosine is pattern similarity, not probability.
5. Show the hashes and access log, then the audit result.
6. Close with the use case and limitation: inspect model ambiguity before interpreting a source estimate; physiological validation and decision advantage remain future work.

## Verify the source and bundle

The source archive is pinned to commit `58570b8`; its older status documents reflect that commit's history. Current acceptance is in the outer submission documents. The manifest lists SHA-256 hashes for all packaged files. After extracting the source, install pytest, h5py, MNE and nibabel in a virtual environment, set PYTHONPATH to its `src` folder and run `python -m pytest -q -ra`. The two archive skips are expected; a downloaded source archive does not include the private workspace evidence or WSGZP dataset.

## Rebuild the submission

See [the clean-checkout build instructions](BUILDING_TKS_SUBMISSION.md). All artifact paths and output destinations are explicit.
