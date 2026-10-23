"""Compare the installed-wheel CLI output with the source-environment run."""
from __future__ import annotations

import csv
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import platform
import zipfile

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE_RUN = ROOT / "outputs/track_b/20261024_b8_export_cli_source_env_v1"
CLEAN_RUN = ROOT / "outputs/track_b/20261024_b8_export_cli_clean_env_v2"
OUT = ROOT / "outputs/track_b/20261024_b8_release_checks/clean_install_parity.json"
WHEEL = ROOT / "tmp/b8_dist/observable_geometry-0.1.0-py3-none-any.whl"
BUNDLE = ROOT / "tmp/b8_model_bundle_export_v1/model_bundle.npz"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    with zipfile.ZipFile(WHEEL) as archive:
        wheel_files = archive.namelist()
        metadata_path = next(name for name in wheel_files if name.endswith(".dist-info/METADATA"))
        wheel_metadata = archive.read(metadata_path).decode("utf-8")
    wheel_license_ok = (
        "License-Expression: BSD-3-Clause" in wheel_metadata
        and "License-File: LICENSE" in wheel_metadata
        and any(name.endswith("/LICENSE") for name in wheel_files)
    )
    csv_source = SOURCE_RUN / "ranked_pairs.csv"
    csv_clean = CLEAN_RUN / "ranked_pairs.csv"
    csv_exact = csv_source.read_bytes() == csv_clean.read_bytes()
    source_rows, clean_rows = csv_rows(csv_source), csv_rows(csv_clean)
    exact_scores = True
    with np.load(SOURCE_RUN / "scores.npz", allow_pickle=False) as a, np.load(CLEAN_RUN / "scores.npz", allow_pickle=False) as b:
        if set(a.files) != set(b.files):
            exact_scores = False
        else:
            for key in a.files:
                av, bv = a[key], b[key]
                equal = np.array_equal(av, bv, equal_nan=True) if av.dtype.kind in "fc" else np.array_equal(av, bv)
                if not equal:
                    exact_scores = False
                    break
    source_summary = json.loads((SOURCE_RUN / "summary.json").read_text(encoding="utf-8"))
    clean_summary = json.loads((CLEAN_RUN / "summary.json").read_text(encoding="utf-8"))
    summary_keys = ("source_count", "valid_signature_count", "covariance_rank",
                    "median_best_distant_abs_cosine", "p90_best_distant_abs_cosine",
                    "fraction_best_abs_cosine_ge_0_95", "fraction_best_abs_cosine_ge_0_99")
    summary_exact = all(source_summary[k] == clean_summary[k] for k in summary_keys)
    report = {
        "status": "PASS" if csv_exact and exact_scores and summary_exact and wheel_license_ok and len(source_rows) == len(clean_rows) else "FAIL",
        "check_scope": "installed wheel compared on the sealed real-model-only input bundle; no EEG sample member used",
        "python_version": platform.python_version(),
        "installed_distribution_version": version("observable-geometry"),
        "wheel_declares_bsd_3_clause": wheel_license_ok,
        "wheel_sha256": sha256(WHEEL),
        "model_bundle_sha256": sha256(BUNDLE),
        "source_cli_csv_sha256": sha256(csv_source),
        "clean_env_cli_csv_sha256": sha256(csv_clean),
        "ranked_pair_count": len(clean_rows),
        "ranked_csv_byte_identical": csv_exact,
        "score_npz_arrays_exact": exact_scores,
        "summary_metrics_exact": summary_exact,
        "summary_metrics_compared": list(summary_keys),
        "result": {key: clean_summary[key] for key in summary_keys},
        "limits": [
            "This confirms packaging and numerical reproduction for the selected one-participant model bundle only.",
            "It does not validate endogenous neural-source recovery, decision utility, novelty, or population generalization.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
