"""Verify that a wheel contains the reviewed package source snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATE_DIR = ROOT / "outputs/track_b/20261029T_release_candidate_013d"
DEFAULT_STAGE = DEFAULT_CANDIDATE_DIR / "source"
DEFAULT_WHEEL = DEFAULT_CANDIDATE_DIR / "wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl"
DEFAULT_OUTPUT = DEFAULT_CANDIDATE_DIR / "wheel_source_verification_rerun.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--wheel", type=Path, default=DEFAULT_WHEEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--expected-version",
        default=tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"],
        help="Expected PEP 440 project version (defaults to pyproject.toml).",
    )
    args = parser.parse_args()
    stage, wheel, output = (p.resolve() for p in (args.stage, args.wheel, args.output))
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"refusing to overwrite report: {output}")
    if not stage.is_dir() or not wheel.is_file():
        raise FileNotFoundError("wheel source stage or wheel is missing")

    staged_sources = sorted((stage / "src/observable_geometry").rglob("*.py"))
    current_sources = sorted((ROOT / "src/observable_geometry").rglob("*.py"))
    staged_rel = {p.relative_to(stage / "src").as_posix(): p for p in staged_sources}
    current_rel = {p.relative_to(ROOT / "src").as_posix(): p for p in current_sources}
    same_file_set = set(staged_rel) == set(current_rel)
    source_rows = []
    with zipfile.ZipFile(wheel) as archive:
        wheel_files = set(archive.namelist())
        for rel in sorted(set(staged_rel) | set(current_rel)):
            staged = staged_rel.get(rel)
            current = current_rel.get(rel)
            member = rel
            stage_hash = sha256_file(staged) if staged else None
            current_hash = sha256_file(current) if current else None
            wheel_hash = sha256_bytes(archive.read(member)) if member in wheel_files else None
            source_rows.append({
                "path": rel,
                "stage_sha256": stage_hash,
                "current_source_sha256": current_hash,
                "wheel_member_sha256": wheel_hash,
                "stage_matches_current": stage_hash == current_hash and staged is not None and current is not None,
                "wheel_matches_stage": stage_hash == wheel_hash and staged is not None and wheel_hash is not None,
            })

        root_rows = {}
        for rel in ("README.md", "LICENSE", "pyproject.toml"):
            stage_path, current_path = stage / rel, ROOT / rel
            root_rows[rel] = {
                "stage_sha256": sha256_file(stage_path) if stage_path.is_file() else None,
                "current_sha256": sha256_file(current_path) if current_path.is_file() else None,
                "stage_matches_current": stage_path.is_file() and current_path.is_file() and sha256_file(stage_path) == sha256_file(current_path),
            }
        metadata_names = [n for n in wheel_files if n.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("expected exactly one wheel METADATA member")
        metadata = archive.read(metadata_names[0]).decode("utf-8")
        license_members = [n for n in wheel_files if n.endswith(".dist-info/licenses/LICENSE")]
        version = next((line.split(": ", 1)[1] for line in metadata.splitlines() if line.startswith("Version: ")), None)
        license_expression_ok = "License-Expression: BSD-3-Clause" in metadata
        staged_license_hash = sha256_file(stage / "LICENSE")
        wheel_license_hash = sha256_bytes(archive.read(license_members[0])) if len(license_members) == 1 else None

    checks = {
        "source_file_sets_match": same_file_set,
        "all_staged_sources_match_current_checkout": all(r["stage_matches_current"] for r in source_rows),
        "all_wheel_modules_match_staged_sources": all(r["wheel_matches_stage"] for r in source_rows),
        "README_LICENSE_pyproject_match_current_checkout": all(v["stage_matches_current"] for v in root_rows.values()),
        "wheel_version_matches_expected": version == args.expected_version,
        "wheel_license_is_BSD_3_Clause": license_expression_ok,
        "wheel_license_file_matches_stage": staged_license_hash == wheel_license_hash,
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "Byte-level source-stage, current-checkout, and wheel-member provenance check; no neural samples accessed.",
        "wheel": str(wheel),
        "wheel_sha256": sha256_file(wheel),
        "wheel_version": version,
        "expected_version": args.expected_version,
        "checks": checks,
        "source_file_count": len(source_rows),
        "source_files": source_rows,
        "root_files": root_rows,
        "limits": [
            "Proves the wheel packages the checked current source files; does not establish scientific correctness or physiological validity.",
            f"The wheel is built from a worktree snapshot at version {args.expected_version}; this is not a public release approval.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": checks,
                      "source_file_count": len(source_rows), "wheel_sha256": report["wheel_sha256"]}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
