"""Run workspace and source-archive tests, recording commit-bound B8 evidence."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE_DIR = ROOT / "outputs/track_b/20261024_b8_release_checks"
ARCHIVE_REPORT_DIR = ROOT / "outputs/track_b/20261024_b8_source_archive_tests"
HANDOFF_DIR = ROOT / "reviewer_handoff/B8_Independent_Review_20261024"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def test_counts(junit_path: Path) -> dict[str, int]:
    root = ET.parse(junit_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    total = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failed = sum(
        int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
        for suite in suites
    )
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)
    return {"passed": total - failed - skipped, "skipped": skipped,
            "failed": failed, "total": total}


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[int, str]:
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def write_new(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite prior B8 evidence: {path}")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise SystemExit(f"refusing to test a dirty source snapshot:\n{status}")

    commit = git("rev-parse", "HEAD")
    short = commit[:7]
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    HANDOFF_DIR.mkdir(parents=True, exist_ok=True)

    workspace_xml = RELEASE_DIR / f"junit_{short}.xml"
    workspace_log = RELEASE_DIR / f"pytest_{short}.log"
    workspace_report = RELEASE_DIR / f"test_run_{short}.json"
    archive = HANDOFF_DIR / f"observable_geometry_source_{short}.zip"
    archive_xml = HANDOFF_DIR / f"junit_{short}.xml"
    archive_log = HANDOFF_DIR / f"pytest_{short}.log"
    archive_report = ARCHIVE_REPORT_DIR / f"source_archive_test_run_{short}.json"
    evidence_paths = (workspace_xml, workspace_log, workspace_report, archive, archive_xml,
                      archive_log, archive_report)
    existing = [str(path.relative_to(ROOT)) for path in evidence_paths if path.exists()]
    if existing:
        raise SystemExit(f"refusing to overwrite prior B8 evidence: {existing}")

    workspace_exit, workspace_output = run(
        [sys.executable, "-m", "pytest", "-q", f"--junitxml={workspace_xml}"], ROOT
    )
    workspace_log.write_text(workspace_output, encoding="utf-8")
    workspace_results = test_counts(workspace_xml)
    workspace_status = "PASS" if workspace_exit == 0 and workspace_results["failed"] == 0 else "FAIL"
    write_new(workspace_report, {
        "status": workspace_status,
        "source_commit": commit,
        "command": f"{Path(sys.executable).name} -m pytest -q --junitxml={workspace_xml.relative_to(ROOT).as_posix()}",
        "python_version": sys.version.split()[0],
        "exit_code": workspace_exit,
        "result": workspace_results,
        "outputs_sha256": {"pytest_log": digest(workspace_log), "junit_xml": digest(workspace_xml)},
        "scope": "Full-workspace software correctness tests; no participant outcomes accessed by this test invocation.",
    })
    if workspace_status != "PASS":
        raise SystemExit(f"workspace test failure; see {workspace_log}")

    subprocess.run(["git", "archive", "--format=zip", f"--output={archive}", "HEAD"], cwd=ROOT, check=True)
    archive_hash = digest(archive)
    with tempfile.TemporaryDirectory(prefix=f"og_b8_{short}_") as temp_name:
        extracted = Path(temp_name) / "source"
        extracted.mkdir()
        with zipfile.ZipFile(archive) as source_zip:
            for member in source_zip.infolist():
                member_path = Path(member.filename)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise ValueError(f"unsafe member in git source archive: {member.filename}")
            source_zip.extractall(extracted)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(extracted / "src") + os.pathsep + env.get("PYTHONPATH", "")
        import_check = subprocess.run(
            [sys.executable, "-c", "import observable_geometry; print(observable_geometry.__file__)"],
            cwd=extracted, env=env, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if not Path(import_check).resolve().is_relative_to((extracted / "src").resolve()):
            raise SystemExit(f"archive tests would import outside extracted source: {import_check}")
        temp_xml = Path(temp_name) / "junit.xml"
        archive_exit, archive_output = run(
            [sys.executable, "-m", "pytest", "-q", f"--junitxml={temp_xml}"], extracted, env
        )
        if not temp_xml.is_file():
            archive_log.write_text(archive_output, encoding="utf-8")
            raise SystemExit(f"source-archive pytest did not produce JUnit output; see {archive_log}")
        archive_results = test_counts(temp_xml)
        archive_xml.write_bytes(temp_xml.read_bytes())
        archive_log.write_text(archive_output, encoding="utf-8")

    archive_status = (
        "PASS_SOURCE_ARCHIVE_TESTS_WITH_DOCUMENTED_SKIP"
        if archive_exit == 0 and archive_results["failed"] == 0 and archive_results["skipped"] > 0
        else "PASS_SOURCE_ARCHIVE_TESTS"
        if archive_exit == 0 and archive_results["failed"] == 0
        else "FAIL"
    )
    write_new(archive_report, {
        "status": archive_status,
        "source_commit": commit,
        "source_archive": archive.relative_to(ROOT).as_posix(),
        "source_archive_sha256": archive_hash,
        "source_import_verified": True,
        "imported_module": import_check,
        "test_command": f"{Path(sys.executable).name} -m pytest -q --junitxml=junit_{short}.xml",
        "test_environment": f"Extracted Git archive; executed with Python {sys.version.split()[0]} from the build environment; dependencies were not reinstalled into a fresh environment.",
        "exit_code": archive_exit,
        "result": archive_results,
        "junit_sha256": digest(archive_xml),
        "pytest_log_sha256": digest(archive_log),
        "interpretation": "Source tests only. Evidence-path integration checks may skip because the archive excludes local run outputs; the full-workspace strict gate validation is run separately.",
    })
    if archive_exit != 0 or archive_results["failed"]:
        raise SystemExit(f"source archive test failure; see {archive_log}")

    print(json.dumps({
        "status": "PASS_B8_COMMIT_BOUND_TESTS",
        "source_commit": commit,
        "workspace_report": workspace_report.relative_to(ROOT).as_posix(),
        "workspace_results": workspace_results,
        "source_archive_report": archive_report.relative_to(ROOT).as_posix(),
        "source_archive_results": archive_results,
        "source_archive_sha256": archive_hash,
    }, indent=2))


if __name__ == "__main__":
    main()
