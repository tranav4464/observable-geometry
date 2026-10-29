# Owner-run, externally witnessed B8 model-only replay for candidate 58570b8.
# This script never opens EEG/iEEG recording samples and does not copy inputs.
$ErrorActionPreference = 'Stop'

$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$commit = '58570b8738080efd6c94b7e44eb5d89f83343be9'
$bundle = Join-Path $root 'outputs\track_b\20261029T_atomic_cli_real_model_reproduction\model_export\model_bundle.npz'
$metadata = Join-Path $root 'outputs\track_b\20261029T_atomic_cli_real_model_reproduction\model_export\model_metadata.json'
$wheel = Join-Path $root 'outputs\track_b\20261030T_commit_release_58570b8\wheelhouse\observable_geometry-0.1.3.dev0-py3-none-any.whl'
$cleanPython = Join-Path $root 'outputs\track_b\20261030T_commit_release_58570b8\clean_env\Scripts\python.exe'
$cleanCli = Join-Path $root 'outputs\track_b\20261030T_commit_release_58570b8\clean_env\Scripts\observable-geometry.exe'
$auditPython = Join-Path $root '.venv\Scripts\python.exe'
$parityScript = Join-Path $root 'scripts\track_b\verify_b8_atomic_cli_reproduction.py'
$installScript = Join-Path $root 'scripts\track_b\verify_b8_candidate_installation.py'

function Assert-Sha256([string] $Path, [string] $Expected) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing required file: $Path" }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $Expected) { throw "SHA-256 mismatch for $Path`: $actual" }
    Write-Host "SHA-256 PASS $Path $actual"
    return $actual
}

Push-Location $root
try {
    $actualCommit = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $actualCommit -ne $commit) {
        throw "Checkout is not the reviewed candidate $commit; found $actualCommit"
    }
    $dirty = @(git status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0 -or $dirty.Count -ne 0) { throw 'The source checkout is not clean.' }

    $bundleHash = Assert-Sha256 $bundle 'e4116465c9af32ddf4bf9e0d3a8e92428c6f1b0bce22a5db257b1c3eaf07a32f'
    $metadataHash = Assert-Sha256 $metadata 'a4d52521ddb760114ba1ce740942bc3bb6232f919de62737d345beb7c48db865'
    $wheelHash = Assert-Sha256 $wheel '3d38d857afd015630ae55283a24512132e6c444077fc97f971b98d410eb43c56'

    $parent = Join-Path $root 'outputs\track_b\b8_witness'
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    $run = Join-Path $parent ("witness_{0}_{1}" -f (Get-Date -Format 'yyyyMMdd_HHmmss'), (Get-Random -Minimum 1000 -Maximum 9999))
    if (Test-Path -LiteralPath $run) { throw "Output already exists: $run" }
    New-Item -ItemType Directory -Path $run | Out-Null
    $candidate = Join-Path $run 'candidate_cli'
    $parity = Join-Path $run 'parity.json'
    $installation = Join-Path $run 'installed_wheel_verification.json'

    & $cleanCli distinguish --bundle $bundle --metadata $metadata --output $candidate --minimum-distance-mm 20 --top-k 5
    if ($LASTEXITCODE -ne 0) { throw "Candidate CLI failed: $LASTEXITCODE" }

    & $auditPython $parityScript --candidate $candidate --output $parity
    if ($LASTEXITCODE -ne 0) { throw "Model-only parity verifier failed: $LASTEXITCODE" }

    & $auditPython $installScript --python $cleanPython --wheel $wheel --parity $parity --output $installation
    if ($LASTEXITCODE -ne 0) { throw "Installed-wheel verifier failed: $LASTEXITCODE" }

    $parityRecord = Get-Content -LiteralPath $parity -Raw | ConvertFrom-Json
    $installRecord = Get-Content -LiteralPath $installation -Raw | ConvertFrom-Json
    if ($parityRecord.status -ne 'PASS' -or $installRecord.status -ne 'PASS' -or $parityRecord.ranked_pair_count -ne 40980) {
        throw 'Saved verifier records did not report the expected PASS and pair count.'
    }
    $csvHash = Assert-Sha256 (Join-Path $candidate 'ranked_pairs.csv') '847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4'

    $summary = [ordered]@{
        status = 'OWNER_RUN_PASS_AWAITING_EXTERNAL_WITNESS_RECORD'
        candidate_commit = $commit
        run_directory = $run
        model_bundle_sha256 = $bundleHash
        model_metadata_sha256 = $metadataHash
        wheel_sha256 = $wheelHash
        ranked_pairs_sha256 = $csvHash
        ranked_pair_count = 40980
        parity_report_sha256 = (Get-FileHash -LiteralPath $parity -Algorithm SHA256).Hash.ToLowerInvariant()
        installation_report_sha256 = (Get-FileHash -LiteralPath $installation -Algorithm SHA256).Hash.ToLowerInvariant()
        limitation = 'This is an owner-run model-only computation. An external reviewer must personally witness or reproduce it and record their own conclusion.'
    }
    $summaryPath = Join-Path $run 'witness_run_summary.json'
    $summary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $summaryPath -Encoding utf8
    Write-Output "WITNESS RUN PASS. Share the new run directory and summary with the external reviewer: $run"
}
finally {
    Pop-Location
}
