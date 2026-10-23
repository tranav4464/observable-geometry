"""Run the versioned B3 nominal source-pattern tool on sealed model arrays only.

The command never materializes the recorded EEG ``data`` member. It validates
the sealed Track A manifest, computes float64 pair scores, checks agreement
with the frozen Track A diagnostic, and writes a new immutable output folder.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from observable_geometry.track_b.distinguishability import (  # noqa: E402
    compute_distinguishability,
    summarize,
)

TRACK_A = ROOT / "outputs" / "tracka_release_20261022_v2"
PREPARED_KEYS = frozenset({"leadfield", "noise_cov"})
SIGNATURE_KEYS = frozenset({
    "source_coordinates", "vertex_ids", "candidate_indices", "absolute_cosine",
    "profiled_residual_at_unit_snr", "valid_source", "whitened_norm",
    "distant_candidate_count",
})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class AllowlistedNPZ:
    """An explicit key allowlist with append-only access-attempt logging."""

    def __init__(self, path: Path, allowed: frozenset[str], log_path: Path, run_id: str):
        self.path, self.allowed = path, allowed
        self.log_path, self.run_id = log_path, run_id
        self.archive = None

    def __enter__(self):
        self.archive = np.load(self.path, allow_pickle=False)
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self.archive is not None:
            self.archive.close()
            self.archive = None

    def __getitem__(self, key: str):
        allowed = isinstance(key, str) and key in self.allowed
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "archive": self.path.name,
            "key": key if isinstance(key, str) else repr(key),
            "decision": "allow" if allowed else "deny",
        }
        flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
        fd = os.open(self.log_path, flags, 0o600)
        try:
            os.write(fd, (json.dumps(row, sort_keys=True) + "\n").encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
        if not allowed:
            raise PermissionError(f"B3 runtime allowlist denied key {key!r} in {self.path.name}")
        if self.archive is None:
            raise RuntimeError("NPZ archive is not open")
        return self.archive[key]


def load_sealed_inputs(log_path: Path, run_id: str):
    manifest_path = TRACK_A / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = {
        "prepared_bundle": TRACK_A / "prepared_bundle.npz",
        "signature_library": TRACK_A / "nominal_signature_library.npz",
    }
    rels = {
        "prepared_bundle": "outputs/tracka_release_20261022_v2/prepared_bundle.npz",
        "signature_library": "outputs/tracka_release_20261022_v2/nominal_signature_library.npz",
    }
    input_hashes = {}
    for label, path in files.items():
        actual = sha256(path)
        expected = manifest["artifact_files_sha256"][rels[label]]
        if actual != expected:
            raise RuntimeError(f"sealed Track A hash mismatch for {rels[label]}")
        input_hashes[rels[label]] = actual
    with AllowlistedNPZ(files["prepared_bundle"], PREPARED_KEYS, log_path, run_id) as archive:
        leadfield = np.asarray(archive["leadfield"], dtype=np.float64)
        covariance = np.asarray(archive["noise_cov"], dtype=np.float64)
    with AllowlistedNPZ(files["signature_library"], SIGNATURE_KEYS, log_path, run_id) as archive:
        coords = np.asarray(archive["source_coordinates"], dtype=np.float64)
        vertex_ids = np.asarray(archive["vertex_ids"], dtype=np.int64)
        ref_indices = np.asarray(archive["candidate_indices"])
        ref_scores = np.asarray(archive["absolute_cosine"])
        ref_valid = np.asarray(archive["valid_source"])
        ref_norms = np.asarray(archive["whitened_norm"])
        ref_counts = np.asarray(archive["distant_candidate_count"])
    if leadfield.shape[1] != len(vertex_ids) or coords.shape != (len(vertex_ids), 3):
        raise ValueError("sealed source coordinate/vertex arrays do not align with the leadfield")
    return manifest, input_hashes, leadfield, covariance, coords, vertex_ids, (
        ref_indices, ref_scores, ref_valid, ref_norms, ref_counts
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="new safe run identifier; existing outputs are never overwritten")
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "track_b")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", args.run_id):
        raise SystemExit("--run-id must be 1-80 safe ASCII letters, digits, dot, underscore, or hyphen")
    out = (args.output_root / args.run_id).resolve()
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing run directory: {out}")
    if TRACK_A.resolve() == out or TRACK_A.resolve() in out.parents:
        raise SystemExit("Refusing to write inside sealed Track A")
    out.mkdir(parents=True)
    try:
        access_log = out / "npz_key_access.jsonl"
        manifest, input_hashes, leadfield, covariance, coords, vertex_ids, reference = load_sealed_inputs(access_log, args.run_id)
        result = compute_distinguishability(
            leadfield, covariance, coords, minimum_distance_mm=20.0, top_k=5, block_size=128
        )
        ref_indices, ref_scores, ref_valid, ref_norms, ref_counts = reference
        if not np.array_equal(result.candidate_indices, ref_indices):
            raise AssertionError("B3 top-five candidate indices differ from sealed Track A")
        if not np.array_equal(result.valid_source, ref_valid):
            raise AssertionError("B3 valid-source mask differs from sealed Track A")
        if not np.array_equal(result.candidate_count, ref_counts):
            raise AssertionError("B3 eligible-candidate counts differ from sealed Track A")
        occupied = result.candidate_indices >= 0
        score_delta = np.abs(result.absolute_cosine[occupied] - ref_scores[occupied])
        if float(score_delta.max(initial=0.0)) > 1e-7:
            raise AssertionError("B3 float64 score differs from sealed Track A by more than 1e-7")
        if not np.allclose(result.whitened_norm, ref_norms, rtol=1e-8, atol=1e-15):
            raise AssertionError("B3 whitened norms differ from sealed Track A contract")

        np.savez_compressed(
            out / "distinguishability_float64.npz",
            source_indices=result.source_indices,
            source_vertex_ids=vertex_ids,
            candidate_indices=result.candidate_indices,
            candidate_vertex_ids=np.where(result.candidate_indices >= 0, vertex_ids[np.maximum(result.candidate_indices, 0)], -1),
            absolute_cosine=result.absolute_cosine,
            profiled_residual=result.profiled_residual,
            valid_source=result.valid_source,
            whitened_norm=result.whitened_norm,
            candidate_count=result.candidate_count,
        )
        summary = summarize(result, 20.0)
        summary.update({
            "status": "PASS",
            "run_id": args.run_id,
            "route": "B3 nominal source-pattern distinguishability",
            "track_a_reference_run": manifest["run_id"],
            "track_a_release_status": manifest["status"],
            "parity": {
                "top_five_indices_exact": True,
                "valid_mask_exact": True,
                "eligible_counts_exact": True,
                "max_abs_float64_vs_track_a_float32_score": float(score_delta.max(initial=0.0)),
                "score_tolerance": 1e-7,
                "whitened_norms_allclose": True,
                "norm_rtol": 1e-8,
                "norm_atol": 1e-15,
            },
            "source_index_note": "Candidate index is the column index in the sealed fixed-orientation leadfield; vertex ID is provided separately.",
            "claim_boundary": "Model-predicted signatures under one fixed participant-specific forward model and covariance. Not a probability, empirical recovery accuracy, physiological source validation, or generalization result.",
        })
        report_path = out / "result_summary.json"
        report_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        with (out / "top_pairs.csv").open("w", newline="", encoding="utf-8") as stream:
            import csv
            writer = csv.writer(stream)
            writer.writerow(["query_index", "query_vertex_id", "rank", "candidate_index", "candidate_vertex_id", "distance_mm", "absolute_cosine_float64", "profiled_residual_float64"])
            for i in range(len(vertex_ids)):
                for rank, j in enumerate(result.candidate_indices[i]):
                    if j < 0:
                        continue
                    distance_mm = float(np.linalg.norm(coords[i] - coords[j]) * 1000.0)
                    writer.writerow([i, int(vertex_ids[i]), rank + 1, int(j), int(vertex_ids[j]), f"{distance_mm:.9f}", f"{result.absolute_cosine[i, rank]:.17g}", f"{result.profiled_residual[i, rank]:.17g}"])
        output_files = ["distinguishability_float64.npz", "result_summary.json", "top_pairs.csv", "npz_key_access.jsonl"]
        output_hashes = {name: sha256(out / name) for name in output_files}
        tool_path = ROOT / "src" / "observable_geometry" / "track_b" / "distinguishability.py"
        cli_path = Path(__file__).resolve()
        run_manifest = {
            "schema_version": 1,
            "run_id": args.run_id,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "command": "python scripts/track_b/run_b3_distinguishability.py --run-id <run_id>",
            "algorithm": "B2-GBF-v10 nominal whitened absolute-cosine diagnostic; separate from GBFs inverse",
            "numeric_precision": "float64 CPU reference",
            "parameters": {"minimum_distance_mm": 20.0, "top_k": 5, "block_size": 128, "eigenvalue_rtol": 1e-10, "support_rtol": 1e-7},
            "specification": {"id": "B2-GBF-2026-10-23-v10", "sha256": "1024c4c80ca31d1375cc13a078bc52ab5b5c58136f8c0ece7debb96f0c3e1062"},
            "track_a_manifest_sha256": sha256(TRACK_A / "run_manifest.json"),
            "input_sha256": input_hashes,
            "implementation_sha256": {"api": sha256(tool_path), "cli": sha256(cli_path)},
            "output_sha256": output_hashes,
            "input_boundary": {"allowed_prepared_bundle_keys": sorted(PREPARED_KEYS), "allowed_signature_library_keys": sorted(SIGNATURE_KEYS), "recorded_eeg_data_key_accessed": False, "access_log": "npz_key_access.jsonl"},
            "result": {"ranking_exact_match": True, "validity_exact_match": True, "counts_exact_match": True, "score_max_abs_difference": float(score_delta.max(initial=0.0)), "norms_allclose": True},
            "limitations": ["Recomputes a nominal geometric diagnostic under one sealed model.", "Does not run a new EEG analysis or establish physiological localization accuracy.", "GBFs inverse behavior and its upstream parity evidence remain in the sealed Track A lineage; this calculation compares vertex-level leadfield columns directly and is not a GBFs estimator output."],
        }
        (out / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "output": str(out), "summary": summary}, indent=2))
        return 0
    except Exception as exc:
        failure = {"status": "FAILED", "run_id": args.run_id, "error_type": type(exc).__name__, "error": str(exc), "created_utc": datetime.now(timezone.utc).isoformat()}
        (out / "failure.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
