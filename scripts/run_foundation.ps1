param([string]$PythonExePath, [switch]$ResumeRun)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = if ($PythonExePath) { (Resolve-Path -LiteralPath $PythonExePath).Path } else { Join-Path $ProjectRoot '.venv\Scripts\python.exe' }
if (-not (Test-Path -LiteralPath $Python)) {
    throw "Foundation environment missing. Create it with: py -3.12 -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements/foundation.txt"
}
if (-not $env:TRACKA_RUN_ID) {
    $env:TRACKA_RUN_ID = 'tracka_' + (Get-Date -Format 'yyyyMMdd_HHmmss')
}
if ($env:TRACKA_RUN_ID -notmatch '^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$') { throw 'TRACKA_RUN_ID is not a safe run identifier.' }
$RunDirectory = Join-Path (Join-Path $ProjectRoot 'outputs') $env:TRACKA_RUN_ID
if ((Test-Path -LiteralPath $RunDirectory) -and -not $ResumeRun) { throw "Run directory already exists and is immutable: $RunDirectory. Choose a new TRACKA_RUN_ID or pass -ResumeRun for an unsealed failed run." }
if ((Test-Path -LiteralPath $RunDirectory) -and (Test-Path -LiteralPath (Join-Path $RunDirectory 'run_manifest.json'))) { throw "Sealed run directories cannot be resumed or overwritten: $RunDirectory" }
$Forward = Join-Path $ProjectRoot 'data\payload\derivatives\sourcemodelling\sub-01\fwd\sub-01_fwd.fif'
foreach ($RunNumber in 1..11) {
    $Run = '{0:D2}' -f $RunNumber
    $Epochs = Join-Path $ProjectRoot "data\payload\derivatives\epochs\sub-01\eeg\sub-01_task-seegstim_run-$($Run)_epochs.npy"
    if (-not (Test-Path -LiteralPath $Epochs)) { throw "Required Localize-MI development payload is missing: $Epochs. Run scripts/fetch_localize.py." }
}
foreach ($File in @($Forward)) {
    if (-not (Test-Path -LiteralPath $File)) { throw "Required Localize-MI payload is missing: $File. See docs/foundation/foundation-protocol.md for the data-fetch procedure." }
}
$env:PYTHONPATH = Join-Path $ProjectRoot 'src'
Push-Location $ProjectRoot
try {
    & $Python scripts\verify_environment.py
    if ($LASTEXITCODE -ne 0) { throw 'Pinned environment verification failed.' }
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Mathematical tests failed.' }
    & $Python scripts\pilot_localize.py
    if ($LASTEXITCODE -ne 0) { throw 'Recorded-data GBFs integration failed.' }
    & $Python scripts\validate_case.py
    if ($LASTEXITCODE -ne 0) { throw 'Physical data and coordinate contract validation failed.' }
    & $Python scripts\verify_gbfs_parity.py
    if ($LASTEXITCODE -ne 0) { throw 'Independent GBFs algebraic parity check failed.' }
    & $Python scripts\run_mne_baseline.py
    if ($LASTEXITCODE -ne 0) { throw 'MNE minimum-norm comparator failed.' }
    & $Python scripts\run_resolution_baseline.py
    if ($LASTEXITCODE -ne 0) { throw 'MNE resolution-matrix comparison failed.' }
    & $Python scripts\run_sensitivity.py
    if ($LASTEXITCODE -ne 0) { throw 'Reference/covariance sensitivity analysis failed.' }
    & $Python scripts\complete_track_a.py
    if ($LASTEXITCODE -ne 0) { throw 'Nominal signature analysis or report generation failed.' }
    & $Python scripts\run_empirical_evaluation.py
    if ($LASTEXITCODE -ne 0) { throw 'Development-set pulse-artifact evaluation failed.' }
    & $Python scripts\render_review.py
    if ($LASTEXITCODE -ne 0) { throw 'Planning review page generation failed.' }
    & $Python scripts\verify_foundation.py --seal
    if ($LASTEXITCODE -ne 0) { throw 'Foundation artifact validation or release sealing failed.' }
    & $Python scripts\verify_foundation.py
    if ($LASTEXITCODE -ne 0) { throw 'Foundation artifact validation failed.' }
}
finally { Pop-Location }
