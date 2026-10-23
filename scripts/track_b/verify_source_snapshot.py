"""Verify a committed source-only snapshot and write release provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from build_source_manifest import TARGET, included_files, sha256


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "outputs/track_b/20261024_b8_release_checks/source_snapshot_verification.json"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def verify(report_path: Path) -> dict[str, object]:
    manifest = json.loads(TARGET.read_text(encoding="utf-8"))
    expected = manifest.get("files")
    if not isinstance(expected, dict):
        raise ValueError("source manifest must contain a files object")

    actual_paths = {path.relative_to(ROOT).as_posix(): path for path in included_files()}
    expected_paths = set(expected)
    missing = sorted(expected_paths - set(actual_paths))
    extra = sorted(set(actual_paths) - expected_paths)
    modified = []
    for relative in sorted(expected_paths & set(actual_paths)):
        path = actual_paths[relative]
        record = expected[relative]
        if path.stat().st_size != record.get("size_bytes") or sha256(path) != record.get("sha256"):
            modified.append(relative)
    if missing or extra or modified:
        raise ValueError(json.dumps({"missing": missing, "extra": extra, "modified": modified}))

    worktree = git("status", "--porcelain=v1", "--untracked-files=all")
    if worktree:
        raise ValueError(f"worktree is not clean:\n{worktree}")
    head = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    result: dict[str, object] = {
        "status": "PASS_SOURCE_SNAPSHOT_VERIFIED",
        "commit": head,
        "git_tree": tree,
        "worktree_clean": True,
        "source_file_count": len(expected),
        "manifest_sha256": sha256(TARGET),
        "manifest_path": TARGET.relative_to(ROOT).as_posix(),
        "license": "BSD-3-Clause" if (ROOT / "LICENSE").is_file() else None,
        "excluded_content": ["datasets", "vendor checkouts", "run outputs", "virtual environments", "reviewer handoff files"],
        "report_path": report_path.relative_to(ROOT).as_posix(),
    }
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    resolved = report_path.resolve()
    if not resolved.is_relative_to((ROOT / "outputs").resolve()):
        raise ValueError("release report must be written under the ignored outputs directory")
    print(json.dumps(verify(resolved), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
