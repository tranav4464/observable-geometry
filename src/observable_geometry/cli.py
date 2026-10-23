"""Command-line interface for Observable Geometry's GBF diagnostic."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

from .track_b.distinguishability import compute_distinguishability, summarize


ALLOWED_BUNDLE_KEYS = frozenset({"leadfield", "noise_covariance", "coordinates_m", "source_ids"})
REQUIRED_METADATA = (
    "dataset", "participant", "forward_model", "reference",
    "coordinate_frame", "source_orientation", "noise_covariance",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def log_access(path: Path, bundle: Path, key: str, decision: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "archive": bundle.name,
        "key": key,
        "decision": decision,
    }
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, (json.dumps(row, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)


def read_bundle(bundle: Path, access_log: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Read only the declared forward-model arrays; never materialize signal arrays."""
    if not bundle.is_file():
        raise ValueError(f"input bundle does not exist: {bundle}")
    with np.load(bundle, allow_pickle=False) as archive:
        keys = set(archive.files)
        missing = {"leadfield", "noise_covariance", "coordinates_m"} - keys
        if missing:
            raise ValueError(f"bundle is missing required key(s): {', '.join(sorted(missing))}")
        forbidden = keys - ALLOWED_BUNDLE_KEYS
        if forbidden:
            for key in sorted(forbidden):
                log_access(access_log, bundle, key, "deny")
            raise ValueError(
                "bundle contains undeclared array member(s): " + ", ".join(sorted(forbidden))
            )
        arrays = {}
        for key in ("leadfield", "noise_covariance", "coordinates_m"):
            log_access(access_log, bundle, key, "allow")
            arrays[key] = np.asarray(archive[key])
        if "source_ids" in keys:
            log_access(access_log, bundle, "source_ids", "allow")
            ids = np.asarray(archive["source_ids"])
        else:
            ids = np.arange(arrays["leadfield"].shape[1], dtype=np.int64)
    if ids.ndim != 1 or len(ids) != arrays["leadfield"].shape[1]:
        raise ValueError("source_ids must be a one-dimensional array with one ID per leadfield column")
    if ids.dtype.kind not in "iuUS":
        raise ValueError("source_ids must use a non-object integer or string dtype")
    return arrays["leadfield"], arrays["noise_covariance"], arrays["coordinates_m"], ids


def read_metadata(path: Path, sensor_count: int) -> dict:
    if not path.is_file():
        raise ValueError(f"metadata JSON does not exist: {path}")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a JSON object")
    missing = [key for key in REQUIRED_METADATA if not isinstance(metadata.get(key), str) or not metadata[key].strip()]
    if missing:
        raise ValueError("metadata is missing nonempty field(s): " + ", ".join(missing))
    sensors = metadata.get("sensor_names")
    if not isinstance(sensors, list) or len(sensors) != sensor_count or any(not isinstance(x, str) or not x for x in sensors):
        raise ValueError("metadata.sensor_names must list one nonempty name per leadfield row")
    if len(set(sensors)) != len(sensors):
        raise ValueError("metadata.sensor_names contains duplicates")
    return metadata


def run_distinguish(args: argparse.Namespace) -> int:
    bundle = args.bundle.resolve()
    metadata_path = args.metadata.resolve()
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite existing output path: {output}")
    output.mkdir(parents=True, exist_ok=False)
    access_log = output / "npz_key_access.jsonl"
    leadfield, covariance, coordinates, source_ids = read_bundle(bundle, access_log)
    metadata = read_metadata(metadata_path, leadfield.shape[0])
    result = compute_distinguishability(
        leadfield,
        covariance,
        coordinates,
        minimum_distance_mm=args.minimum_distance_mm,
        top_k=args.top_k,
        block_size=args.block_size,
    )
    scores_path = output / "scores.npz"
    np.savez_compressed(
        scores_path,
        source_indices=result.source_indices,
        source_ids=source_ids,
        candidate_indices=result.candidate_indices,
        candidate_ids=np.where(result.candidate_indices >= 0, source_ids[np.maximum(result.candidate_indices, 0)], ""),
        absolute_cosine=result.absolute_cosine,
        profiled_residual=result.profiled_residual,
        valid_source=result.valid_source,
        whitened_norm=result.whitened_norm,
        candidate_count=result.candidate_count,
    )
    pairs_path = output / "ranked_pairs.csv"
    with pairs_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("source_index", "source_id", "rank", "candidate_index", "candidate_id",
                         "distance_mm", "absolute_cosine", "profiled_residual_unit_snr"))
        for source_index, candidates in enumerate(result.candidate_indices):
            for rank, candidate_index in enumerate(candidates, start=1):
                if candidate_index < 0:
                    continue
                distance_mm = float(np.linalg.norm(coordinates[source_index] - coordinates[candidate_index]) * 1000.0)
                writer.writerow((source_index, str(source_ids[source_index]), rank, int(candidate_index),
                                 str(source_ids[candidate_index]), f"{distance_mm:.9f}",
                                 f"{result.absolute_cosine[source_index, rank - 1]:.17g}",
                                 f"{result.profiled_residual[source_index, rank - 1]:.17g}"))
    summary = summarize(result, args.minimum_distance_mm)
    summary.update({
        "status": "COMPLETED_NOMINAL_MODEL_DIAGNOSTIC",
        "claim_boundary": "Model-predicted sensor-pattern similarity under the declared inputs; not calibrated localization probability, neural source recovery, or population generalization.",
        "metadata": metadata,
        "parameters": {"minimum_distance_mm": args.minimum_distance_mm, "top_k": args.top_k,
                       "block_size": args.block_size, "numeric_precision": "float64"},
        "inputs": {"bundle_sha256": sha256(bundle), "metadata_sha256": sha256(metadata_path)},
    })
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    implementation = Path(__file__).resolve()
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": "observable-geometry distinguish",
        "implementation_sha256": sha256(implementation),
        "input_sha256": {"bundle": sha256(bundle), "metadata": sha256(metadata_path)},
        "output_sha256": {name: sha256(output / name) for name in ("scores.npz", "ranked_pairs.csv", "summary.json", "npz_key_access.jsonl")},
        "allowed_bundle_keys": sorted(ALLOWED_BUNDLE_KEYS),
        "recorded_signal_array_accessed": False,
        "limits": [
            "Numerical output is conditional on the declared forward model, sensor reference, source family, and covariance.",
            "The statistic is an established nominal similarity diagnostic; the package does not claim a novel mathematical method.",
            "The process-level key guard helps prevent accidental array access; it is not an operating-system sandbox.",
        ],
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "output": str(output), "summary": {k: summary[k] for k in (
        "source_count", "valid_signature_count", "covariance_rank", "median_best_distant_abs_cosine",
        "p90_best_distant_abs_cosine", "fraction_best_abs_cosine_ge_0_95")}}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    distinguish = subparsers.add_parser("distinguish", help="rank nominal source-pattern lookalikes")
    distinguish.add_argument("--bundle", required=True, type=Path,
                             help="NPZ with leadfield, noise_covariance, coordinates_m, optional source_ids")
    distinguish.add_argument("--metadata", required=True, type=Path, help="JSON describing model and sensor provenance")
    distinguish.add_argument("--output", required=True, type=Path, help="new output directory; existing paths are rejected")
    distinguish.add_argument("--minimum-distance-mm", type=float, default=20.0)
    distinguish.add_argument("--top-k", type=int, default=5)
    distinguish.add_argument("--block-size", type=int, default=128)
    distinguish.set_defaults(handler=run_distinguish)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError, json.JSONDecodeError, PermissionError) as exc:
        print(f"observable-geometry: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
