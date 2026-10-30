param([string]$PythonExePath)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot
try {
    $Venv = Join-Path $ProjectRoot '.venv'
    $Python = Join-Path $Venv 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $Python)) {
        if ($PythonExePath) {
            $BasePython = (Resolve-Path -LiteralPath $PythonExePath).Path
        } elseif (Get-Command py -ErrorAction SilentlyContinue) {
            $BasePython = 'py'
        } elseif (Get-Command python3.12 -ErrorAction SilentlyContinue) {
            $BasePython = (Get-Command python3.12).Source
        } else { throw 'Python 3.12 was not found. Pass -PythonExePath to a Python 3.12 executable.' }
        if ($BasePython -eq 'py') { & py -3.12 -m venv .venv }
        else { & $BasePython -m venv .venv }
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python 3.12 virtual environment.' }
    }
    & $Python -m pip install --disable-pip-version-check -r requirements/foundation.txt
    if ($LASTEXITCODE -ne 0) { throw 'Pinned Python environment installation failed.' }

    $Metadata = Join-Path $ProjectRoot 'data\Localize-MI'
    $MetadataCommit = 'd7a123d3067213281f106b343c71f28c30e4dd60'
    if (-not (Test-Path -LiteralPath (Join-Path $Metadata '.git'))) {
        if (Test-Path -LiteralPath $Metadata) { throw "Metadata folder exists without Git history: $Metadata" }
        New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot 'data') | Out-Null
        git clone https://gin.g-node.org/ezemikulan/Localize-MI.git $Metadata
        if ($LASTEXITCODE -ne 0) { throw 'Could not clone the pinned Localize-MI metadata repository.' }
    }
    $ActualMetadata = (& git -C $Metadata rev-parse HEAD).Trim()
    if ($ActualMetadata -ne $MetadataCommit) {
        git -C $Metadata checkout --detach $MetadataCommit
        if ($LASTEXITCODE -ne 0) { throw 'Could not check out the pinned Localize-MI metadata snapshot.' }
    }

    $GBFs = Join-Path $ProjectRoot 'vendor\GBFs'
    $GBFsCommit = '99fc7c6e8afbd2e3e68a700c5f1fa1483b90f49e'
    if (-not (Test-Path -LiteralPath (Join-Path $GBFs '.git'))) {
        if (Test-Path -LiteralPath $GBFs) { throw "GBFs folder exists without Git history: $GBFs" }
        New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot 'vendor') | Out-Null
        git clone https://github.com/ncclab-sustech/GBFs.git $GBFs
        if ($LASTEXITCODE -ne 0) { throw 'Could not clone the pinned GBFs repository.' }
    }
    $ActualGBFs = (& git -C $GBFs rev-parse HEAD).Trim()
    if ($ActualGBFs -ne $GBFsCommit) {
        git -C $GBFs checkout --detach $GBFsCommit
        if ($LASTEXITCODE -ne 0) { throw 'Could not check out the pinned GBFs commit.' }
    }

    $env:PYTHONPATH = Join-Path $ProjectRoot 'src'
    & $Python scripts\fetch_localize.py
    if ($LASTEXITCODE -ne 0) { throw 'Localize-MI payload retrieval or checksum verification failed.' }
    & (Join-Path $ProjectRoot 'scripts\run_foundation.ps1') -PythonExePath $Python
}
finally { Pop-Location }
