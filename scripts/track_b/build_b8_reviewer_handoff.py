"""Build a hash-verified, source-only B8 reviewer handoff from a clean commit."""
from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HANDOFF_ROOT = ROOT / "reviewer_handoff"
RELEASE_DATE = "20261024"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise SystemExit(f"refusing to package a dirty worktree:\n{status}")

    commit = git("rev-parse", "HEAD")
    short = commit[:7]
    snapshot_report = ROOT / "outputs/track_b/20261024_b8_release_checks/source_snapshot_verification.json"
    test_report = ROOT / "outputs/track_b/20261024_b8_release_checks/test_run.json"
    archive_test_report = ROOT / "outputs/track_b/20261024_b8_source_archive_tests/source_archive_test_run.json"
    clean_parity = ROOT / "outputs/track_b/20261024_b8_release_checks/clean_install_parity.json"
    wheel = ROOT / "outputs/track_b/20261024_b8_release_checks/release_artifacts/observable_geometry-0.1.2-py3-none-any.whl"
    for path in (snapshot_report, test_report, archive_test_report, clean_parity, wheel):
        if not path.is_file():
            raise SystemExit(f"required B8 evidence is missing: {path.relative_to(ROOT)}")

    snapshot = json.loads(snapshot_report.read_text(encoding="utf-8"))
    workspace_tests = json.loads(test_report.read_text(encoding="utf-8"))
    archive_tests = json.loads(archive_test_report.read_text(encoding="utf-8"))
    if snapshot.get("commit") != commit or snapshot.get("worktree_clean") is not True:
        raise SystemExit("source snapshot verification does not match the current clean commit")
    if workspace_tests.get("status") != "PASS" or workspace_tests.get("result", {}).get("failed") != 0:
        raise SystemExit("latest full-workspace test report is not passing")
    if archive_tests.get("source_commit") != commit or archive_tests.get("exit_code") != 0:
        raise SystemExit("source-archive test report does not match the current commit")
    if archive_tests.get("status") != "PASS_SOURCE_ARCHIVE_TESTS_WITH_DOCUMENTED_SKIP":
        raise SystemExit("source-archive test report has an unexpected status")
    parity = json.loads(clean_parity.read_text(encoding="utf-8"))
    if parity.get("status") != "PASS" or parity.get("wheel_sha256") != sha256_bytes(wheel.read_bytes()):
        raise SystemExit("clean-install parity report does not match the packaged wheel")

    dated_dir = HANDOFF_ROOT / f"B8_Independent_Review_{RELEASE_DATE}"
    dated_dir.mkdir(parents=True, exist_ok=True)
    source_archive = dated_dir / f"observable_geometry_source_{short}.zip"
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={source_archive}", "HEAD"],
        cwd=ROOT,
        check=True,
    )
    archive_digest = sha256_bytes(source_archive.read_bytes())
    if archive_tests.get("source_archive_sha256") != archive_digest:
        raise SystemExit("source-archive test report hash does not match the built archive")
    with zipfile.ZipFile(source_archive) as source_zip:
        forbidden_prefixes = ("data/", "datasets/", "outputs/", "tmp/", "vendor/", "reviewer_handoff/")
        forbidden = [name for name in source_zip.namelist() if name.startswith(forbidden_prefixes)]
        if forbidden:
            raise SystemExit(f"source archive contains excluded content: {forbidden[:5]}")

    inputs = {
        "B2_GATE_CLOSEOUT_20261024.md": ROOT / "docs/track_b/B2_GATE_CLOSEOUT_20261024.md",
        "B0_GBF_EXTENSION_SCREEN.md": ROOT / "docs/track_b/B0_GBF_EXTENSION_SCREEN.md",
        "B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md": ROOT / "docs/track_b/B4_ALTERNATE_PUBLIC_DATASET_SCREEN_20261024.md",
        "B4_HDEEG_REOPENING_ASSESSMENT_20261024.md": ROOT / "docs/track_b/B4_HDEEG_REOPENING_ASSESSMENT_20261024.md",
        "B8_EXTERNAL_REVIEW_PACKET_20261024.md": ROOT / "docs/track_b/B8_EXTERNAL_REVIEW_PACKET_20261024.md",
        "B8_RELEASE_AUDIT_20261024.md": ROOT / "docs/track_b/B8_RELEASE_AUDIT_20261024.md",
        "PROJECT_DEFINITION.md": ROOT / "docs/track_b/PROJECT_DEFINITION.md",
        "clean_install_parity.json": clean_parity,
        "source_snapshot_verification.json": snapshot_report,
        "test_run_workspace.json": test_report,
        "test_run_source_archive.json": archive_test_report,
        "observable_geometry-0.1.2-py3-none-any.whl": wheel,
        source_archive.name: source_archive,
    }
    for name, path in inputs.items():
        if not path.is_file():
            raise SystemExit(f"required handoff file is missing: {path.relative_to(ROOT)}")

    readme = f"""# Observable Geometry — independent B8 review handoff

Prepared for independent software and scientific-scope review. Source commit: `{commit}` (24 October 2026). The source archive contains software, tests, and documentation, while excluding datasets, the separately pinned GBFs checkout, local run outputs, and virtual environments. A BSD-3-Clause wheel is included.

## Scope and limits

The project reproduces a declared nominal GBF source-pattern diagnostic under one verified participant-specific forward model. It reports model-conditional similarity between candidate scalp patterns. It does not establish physiological source recovery, calibrated localization probabilities, population generalization, analyst decision benefit, or a novel cosine-based method. B4–B7 are pivoted; B8 remains open pending independent outside review or reproduction.

The updated prior-art and dataset screen records that Wang et al. 2026 already reports GBF localization results for 318 sessions from 35 participants on the public iES-CCEP data route and on 24 favourable-outcome patients from the HDEEG-IED-SurgOutcome release. The HDEEG landing page and 2025 data descriptor differ in their stated cohort count (45 versus 44); the release manifest must be checked before any denominator is frozen. The iES-CCEP OSF metadata reviewed show no explicit dataset license. HDEEG-IED-SurgOutcome offers participant MRI, EEG averages, electrode coordinates, resection masks, and clinical outcomes, but any unused participants remain a possible post-publication secondary subset, not an untouched external cohort; EBRAINS terms, overlap, covariance contract, and a reviewed protocol must be resolved before access. A separate 2023 simultaneous scalp/SEEG stimulation study reports individual FEM models but makes its data available only upon reasonable request. No author has been contacted and no new signal or outcome analysis is authorized by the metadata screen.

## Materials

The package includes the source archive, BSD-3-Clause wheel, B0 prior-art screen, B2 closeout, current dataset screen and focused HDEEG reopening assessment, B8 review packet and release audit, project definition, clean-install parity record, source-snapshot verification, and current full-workspace and source-archive test reports. The source-archive report records any skipped evidence-path test, because local run outputs are excluded from that archive.

## Data boundary

This handoff contains no EEG/SEEG recordings or data-derived forward-model bundle. The Localize-MI data-derived bundle remains local under its separate terms. The clean-wheel parity report documents a model-only run in the project workspace, so this handoff alone cannot independently reproduce participant-specific numeric results. Model-level reproduction requires lawful access to the exact permitted model inputs and provenance.

Please state your name, affiliation, expertise, conflicts or prior involvement, materials personally inspected, independent checks performed, and a recommendation of `PASS`, `HOLD FOR CHANGES`, or `FAIL/PIVOT`. Distinguish your reproduced checks from supplied results. Do not infer permission to access or redistribute human recordings.
"""
    manifest = {
        "schema_version": 1,
        "project_commit": commit,
        "scope": "B8 review handoff only; no datasets, human signal samples, or data-derived model bundle included.",
        "files": {
            name: {
                "size_bytes": path.stat().st_size,
                "sha256": sha256_bytes(path.read_bytes()),
            }
            for name, path in inputs.items()
        },
    }
    output = HANDOFF_ROOT / f"Observable_Geometry_B8_Independent_Review_{RELEASE_DATE}.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr("README_FOR_REVIEWER.md", readme)
        for name, path in inputs.items():
            archive.write(path, name)
        archive.writestr("HANDOFF_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    with zipfile.ZipFile(output) as archive:
        stored_manifest = json.loads(archive.read("HANDOFF_MANIFEST.json"))
        for name, record in stored_manifest["files"].items():
            content = archive.read(name)
            if len(content) != record["size_bytes"] or sha256_bytes(content) != record["sha256"]:
                raise SystemExit(f"handoff integrity check failed: {name}")
    print(json.dumps({
        "status": "PASS_B8_HANDOFF_BUILT",
        "project_commit": commit,
        "output": output.relative_to(ROOT).as_posix(),
        "size_bytes": output.stat().st_size,
        "sha256": sha256_bytes(output.read_bytes()),
        "source_archive": source_archive.relative_to(ROOT).as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
