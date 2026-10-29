"""Verify installed-wheel provenance and parity evidence for a B8 candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN = ROOT / "outputs/track_b/20261029T_release_candidate_013d"
DEFAULT_WHEEL = DEFAULT_RUN / "wheelhouse/observable_geometry-0.1.3.dev0-py3-none-any.whl"
DEFAULT_PARITY = DEFAULT_RUN / "candidate_cli_parity.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True, help="Python executable in the clean install environment")
    parser.add_argument("--wheel", type=Path, default=DEFAULT_WHEEL)
    parser.add_argument("--parity", type=Path, default=DEFAULT_PARITY)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    python, wheel, parity_path, output = (p.resolve() for p in (args.python, args.wheel, args.parity, args.output))
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"refusing to overwrite report: {output}")
    if not python.is_file() or not wheel.is_file() or not parity_path.is_file():
        raise FileNotFoundError("Python executable, wheel, or parity report is missing")

    probe = """import importlib.metadata as m, json, pathlib, sys
import numpy, scipy
d=m.distribution('observable-geometry')
print(json.dumps({'version':m.version('observable-geometry'),'prefix':sys.prefix,
 'base_prefix':sys.base_prefix,'python':sys.version,'package_file':str(d.locate_file('observable_geometry/cli.py')),
 'numpy':numpy.__version__,'scipy':scipy.__version__}))"""
    installed = json.loads(subprocess.check_output([str(python), "-c", probe], text=True))
    isolated = Path(installed["prefix"]).resolve() != Path(installed["base_prefix"]).resolve()
    package_file = Path(installed["package_file"]).resolve()
    try:
        package_root = package_file.parents[1]
        package_inside_environment = package_root.is_relative_to(Path(installed["prefix"]).resolve())
    except (IndexError, ValueError):
        package_inside_environment = False

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("wheel must contain exactly one METADATA file")
        metadata = archive.read(metadata_names[0]).decode("utf-8")
        wheel_version = next(
            (line.partition(": ")[2] for line in metadata.splitlines() if line.startswith("Version: ")),
            None,
        )
        module_names = sorted(name for name in names if name.startswith("observable_geometry/") and name.endswith(".py"))
        module_checks = []
        for name in module_names:
            installed_file = package_root.joinpath(*name.split("/"))
            installed_hash = hashlib.sha256(installed_file.read_bytes()).hexdigest() if installed_file.is_file() else None
            wheel_hash = hashlib.sha256(archive.read(name)).hexdigest()
            module_checks.append({"module": name, "wheel_sha256": wheel_hash,
                                  "installed_sha256": installed_hash, "matches": wheel_hash == installed_hash})

    parity = json.loads(parity_path.read_text(encoding="utf-8"))
    run_dir = Path(parity.get("candidate_output_directory", "")).resolve()
    run_manifest_path = run_dir / "run_manifest.json"
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8")) if run_manifest_path.is_file() else {}
    expected_run_outputs = ("scores.npz", "ranked_pairs.csv", "summary.json", "npz_key_access.jsonl")
    recorded_output_hashes = run_manifest.get("output_sha256", {})
    run_outputs_match = bool(run_manifest_path.is_file()) and all(
        (run_dir / name).is_file()
        and recorded_output_hashes.get(name) == sha256(run_dir / name)
        for name in expected_run_outputs
    )
    parity_checks = parity.get("checks", {})
    checks = {
        "fresh_isolated_environment": isolated,
        "package_imported_from_environment": package_inside_environment,
        "installed_version_matches_wheel": installed["version"] == wheel_version,
        "all_installed_modules_match_wheel": bool(module_checks) and all(row["matches"] for row in module_checks),
        "installed_cli_matches_run_implementation_hash": (
            run_manifest.get("implementation_sha256") == sha256(package_file)
        ),
        "candidate_run_outputs_match_manifest": run_outputs_match,
        "candidate_cli_parity_passed": parity.get("status") == "PASS" and bool(parity_checks)
            and all(value is True for value in parity_checks.values()),
        "parity_report_targets_candidate_run": str(run_dir) == str(Path(parity.get("candidate_output_directory", "")).resolve()),
        "run_manifest_declares_no_signal_access": run_manifest.get("recorded_signal_array_accessed") is False,
        "run_manifest_contains_expected_model_only_keys": set(run_manifest.get("allowed_bundle_keys", [])) == {
            "coordinates_m", "leadfield", "noise_covariance", "source_ids"},
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "Installed wheel module/version provenance and linked one-model CLI parity; not scientific validation.",
        "python_executable": str(python),
        "environment": installed,
        "wheel": str(wheel),
        "wheel_sha256": sha256(wheel),
        "wheel_version": wheel_version,
        "parity_report": str(parity_path),
        "parity_report_sha256": sha256(parity_path),
        "run_manifest": str(run_manifest_path),
        "run_manifest_sha256": sha256(run_manifest_path) if run_manifest_path.is_file() else None,
        "checks": checks,
        "wheel_modules_checked": module_checks,
        "limits": [
            "A passing result establishes package provenance and reproducibility for the linked sealed model-only run.",
            "It does not establish physiological source recovery, method novelty, calibrated uncertainty, or researcher utility.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": checks,
                      "wheel_sha256": report["wheel_sha256"], "wheel_version": wheel_version}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
