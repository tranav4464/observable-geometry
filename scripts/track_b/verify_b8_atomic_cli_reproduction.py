"""Verify a working-tree CLI run against the prior clean-wheel model-only run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFERENCE = ROOT / "outputs/track_b/20261024_b8_export_cli_clean_env_v4"
DEFAULT_CANDIDATE = ROOT / "outputs/track_b/20261029T_atomic_cli_real_model_reproduction/source_cli"
DEFAULT_EXPORT = ROOT / "outputs/track_b/20261029T_atomic_cli_real_model_reproduction/model_export"
DEFAULT_CLEAN_CHECK = ROOT / "outputs/track_b/20261024_b8_release_checks/clean_install_parity.json"
SUMMARY_KEYS = (
    "source_count", "valid_signature_count", "covariance_rank",
    "median_best_distant_abs_cosine", "p90_best_distant_abs_cosine",
    "fraction_best_abs_cosine_ge_0_95", "fraction_best_abs_cosine_ge_0_99",
)
EXPECTED_CLI_KEYS = {"leadfield", "noise_covariance", "coordinates_m", "source_ids"}
EXPECTED_SOURCE_KEYS = {
    "prepared_bundle.npz": {"leadfield", "noise_cov"},
    "nominal_signature_library.npz": {"source_coordinates", "vertex_ids"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_npz(reference: Path, candidate: Path) -> bool:
    with np.load(reference, allow_pickle=False) as ref, np.load(candidate, allow_pickle=False) as cand:
        if set(ref.files) != set(cand.files):
            return False
        for key in ref.files:
            left, right = ref[key], cand[key]
            equal = (np.array_equal(left, right, equal_nan=True)
                     if left.dtype.kind in "fc" else np.array_equal(left, right))
            if not equal:
                return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--model-export", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--clean-install-check", type=Path, default=DEFAULT_CLEAN_CHECK)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    reference, candidate = args.reference.resolve(), args.candidate.resolve()
    model_export, clean_check_path = args.model_export.resolve(), args.clean_install_check.resolve()
    report_path = (args.output or (candidate / "reproduction_check.json")).resolve()
    required = [
        reference / "ranked_pairs.csv", reference / "scores.npz", reference / "summary.json",
        candidate / "ranked_pairs.csv", candidate / "scores.npz", candidate / "summary.json",
        candidate / "run_manifest.json", candidate / "npz_key_access.jsonl",
        model_export / "model_bundle.npz", model_export / "model_metadata.json",
        model_export / "export_manifest.json", model_export / "source_npz_key_access.jsonl",
        clean_check_path,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing verification input(s): " + ", ".join(missing))
    if report_path.exists() or report_path.is_symlink():
        raise FileExistsError(f"refusing to overwrite verification report: {report_path}")

    old_csv, new_csv = reference / "ranked_pairs.csv", candidate / "ranked_pairs.csv"
    csv_exact = old_csv.read_bytes() == new_csv.read_bytes()
    score_arrays_exact = exact_npz(reference / "scores.npz", candidate / "scores.npz")
    old_summary = json.loads((reference / "summary.json").read_text(encoding="utf-8"))
    new_summary = json.loads((candidate / "summary.json").read_text(encoding="utf-8"))
    summary_exact = all(old_summary.get(key) == new_summary.get(key) for key in SUMMARY_KEYS)

    run_manifest = json.loads((candidate / "run_manifest.json").read_text(encoding="utf-8"))
    export_manifest = json.loads((model_export / "export_manifest.json").read_text(encoding="utf-8"))
    clean_check = json.loads(clean_check_path.read_text(encoding="utf-8"))
    output_hashes = run_manifest.get("output_sha256", {})
    output_hashes_match = all(
        output_hashes.get(name) == sha256(candidate / name)
        for name in ("scores.npz", "ranked_pairs.csv", "summary.json", "npz_key_access.jsonl")
    )
    input_hashes_match = (
        run_manifest.get("input_sha256", {}).get("bundle") == sha256(model_export / "model_bundle.npz")
        and run_manifest.get("input_sha256", {}).get("metadata") == sha256(model_export / "model_metadata.json")
    )
    cli_reads = [json.loads(line) for line in (candidate / "npz_key_access.jsonl").read_text().splitlines()]
    cli_allowlist_ok = (
        {row.get("key") for row in cli_reads} == EXPECTED_CLI_KEYS
        and all(row.get("decision") == "allow" for row in cli_reads)
    )
    source_reads = [json.loads(line) for line in (model_export / "source_npz_key_access.jsonl").read_text().splitlines()]
    source_allowlist_ok = (
        {(row.get("archive"), row.get("key")) for row in source_reads}
        == {(archive, key) for archive, keys in EXPECTED_SOURCE_KEYS.items() for key in keys}
        and all(row.get("decision") == "allow" for row in source_reads)
        and export_manifest.get("source_keys_read") == {k: sorted(v) for k, v in EXPECTED_SOURCE_KEYS.items()}
        and export_manifest.get("recorded_EEG_data_key_accessed") is False
    )
    clean_reference_chain = (
        clean_check.get("status") == "PASS"
        and clean_check.get("clean_env_cli_csv_sha256") == sha256(old_csv)
        and clean_check.get("score_npz_arrays_exact") is True
        and clean_check.get("summary_metrics_exact") is True
    )

    checks = {
        "ranked_pairs_byte_identical_to_clean_wheel_reference": csv_exact,
        "all_score_arrays_exact_to_clean_wheel_reference": score_arrays_exact,
        "summary_metrics_exact_to_clean_wheel_reference": summary_exact,
        "current_output_hashes_match_manifest": output_hashes_match,
        "current_input_hashes_match_exported_model": input_hashes_match,
        "cli_read_only_allowlist_exact": cli_allowlist_ok,
        "sealed_export_allowlist_and_no_eeg_data_access": source_allowlist_ok,
        "reference_is_linked_to_prior_clean_install_pass": clean_reference_chain,
    }
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_scope": "Candidate CLI run versus the prior verified 0.1.2 clean-wheel output on the sealed sub-01 model-only bundle.",
        "candidate_output_directory": str(candidate),
        "checks": checks,
        "ranked_pair_count": sum(1 for _ in new_csv.open(encoding="utf-8")) - 1,
        "ranked_pairs_sha256": {"reference": sha256(old_csv), "candidate": sha256(new_csv)},
        "summary_values": {key: new_summary.get(key) for key in SUMMARY_KEYS},
        "reference_clean_install_check_sha256": sha256(clean_check_path),
        "candidate_run_manifest_sha256": sha256(candidate / "run_manifest.json"),
        "model_export_manifest_sha256": sha256(model_export / "export_manifest.json"),
        "limits": [
            "One participant and one sealed forward model only.",
            "This is software numerical parity, not physiological source recovery, decision utility, novelty, or population generalization.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
