# Rebuild the TKS submission from a clean checkout

The builder requires explicit artifact paths and hashes. It does not read ignored research outputs, model arrays or recordings. Python 3.12+ and Git are required; wheel building requires pip and setuptools (package-index access or cached build dependencies). Build from the freshly extracted source directory shown below, not from a long-lived worktree with a stale `build/` cache. The builder rejects a wheel whose Python modules differ from the source archive.

In PowerShell, clone the repository, select the intended code revision, then run from the repository root:

```powershell
$codeCommit = (git rev-parse HEAD).Trim()
New-Item -ItemType Directory -Path build-artifacts -ErrorAction Stop
# Git's ZIP comment records the source commit; the builder checks it.
git archive --format=zip --output=build-artifacts/source.zip $codeCommit
Expand-Archive build-artifacts/source.zip build-artifacts/source
python -m pip wheel --no-deps --wheel-dir build-artifacts/wheels ./build-artifacts/source
$wheel = (Get-ChildItem build-artifacts/wheels/observable_geometry-*.whl).FullName
$sourceHash = (Get-FileHash build-artifacts/source.zip -Algorithm SHA256).Hash
$wheelHash = (Get-FileHash $wheel -Algorithm SHA256).Hash
python scripts/build_tks_submission.py --source build-artifacts/source.zip --wheel $wheel --source-sha256 $sourceHash --wheel-sha256 $wheelHash --code-commit $codeCommit --output build-artifacts/submission
```

Use a new output path for another run. The builder refuses overwrites. It checks the ZIP's commit comment, both supplied hashes, version agreement, and exact Python-module correspondence between source and wheel. It then verifies every packaged file against its manifest. This establishes internal artifact consistency; computing hashes yourself is not a substitute for comparing with the accepted release record.

The builder uses documentation from the checkout you run it in. The source ZIP and wheel describe the numerical software revision; current outer documentation can describe a later acceptance. Retain both identities when publishing a documentation refresh. `--update-page` also writes the repository's index.html; omit it to keep packaging isolated.

Reproducing the numerical participant result additionally requires lawful access to the declared model inputs. The packaging process does not acquire those inputs.
