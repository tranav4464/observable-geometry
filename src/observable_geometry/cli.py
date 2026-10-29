"""Command-line interface for model-conditional EEG forward-pattern diagnostics."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import csv
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

import numpy as np

from .track_b.distinguishability import compute_distinguishability, summarize
from .track_b.robust_attribution import EndpointChallenge, RobustAuditInput, audit_robust_attribution
from .track_b.family_frontier import DistanceInterval, FamilyComparison, compare_families
from .track_b import family_frontier as family_frontier_module


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


@contextmanager
def fresh_output_directory(destination: Path):
    """Write a run privately, then publish the complete directory atomically."""
    destination = destination.resolve()
    if os.path.lexists(destination):
        raise ValueError(f"refusing to overwrite existing output path: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.tmp-", dir=destination.parent))
    try:
        yield stage
        if os.path.lexists(destination):
            raise ValueError(f"refusing to overwrite existing output path: {destination}")
        os.rename(stage, destination)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


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
    final_output = args.output.resolve()
    with fresh_output_directory(final_output) as output:
        completion = _write_distinguish_run(args, bundle, metadata_path, output, final_output)
    print(json.dumps(completion, indent=2))
    return 0


def _write_distinguish_run(
    args: argparse.Namespace,
    bundle: Path,
    metadata_path: Path,
    output: Path,
    final_output: Path,
) -> dict:
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
    return {"status": summary["status"], "output": str(final_output), "summary": {k: summary[k] for k in (
        "source_count", "valid_signature_count", "covariance_rank", "median_best_distant_abs_cosine",
        "p90_best_distant_abs_cosine", "fraction_best_abs_cosine_ge_0_95")}}


def run_robust_audit(args: argparse.Namespace) -> int:
    """Compare a nominal target-only claim with interval and in-set evidence."""
    spec_path=args.spec.resolve()
    output=args.output.resolve()
    raw=json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(raw,dict) or not isinstance(raw.get("endpoints"),list):
        raise ValueError("robust audit spec needs a JSON object with endpoints")
    allowed={"parameter_interval","tolerance","anchor_target_residual_upper",
             "anchor_alternative_residual_lower","anchor_alternative_residual_upper",
             "target_amplitude_abs_upper","alternative_l1_budget",
             "target_column_radius","alternative_column_radius_upper","endpoints"}
    if set(raw)!=allowed:
        raise ValueError("robust audit spec keys do not match the declared schema")
    endpoints=tuple(EndpointChallenge(**item) for item in raw["endpoints"])
    spec=RobustAuditInput(**{k:v for k,v in raw.items() if k!="endpoints"},endpoints=endpoints)
    result=audit_robust_attribution(spec)
    with fresh_output_directory(output) as stage:
        report={"status":"COMPLETED_CONDITIONAL_ROBUST_AUDIT",
                "result":asdict(result),"input":asdict(spec),
                "input_evidence_status":"supplied_bounds_not_replayed_by_this_command",
                "claim_boundary":"Conditional on supplied in-set scenarios, residual certificates and column radii. This is a standard sufficient bound and counterexample audit, not a new inverse method or physiological source identity.",
                "input_sha256":sha256(spec_path),"implementation_sha256":sha256(Path(__file__).resolve())}
        (stage/"result.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"anchor_decision":result.anchor_decision,
                      "interval_decision":result.interval_decision,
                      "input_evidence_status":report["input_evidence_status"],
                      "output":str(output)},indent=2))
    return 0


def run_family_frontier(args: argparse.Namespace) -> int:
    """Report source-family decision reversals from supplied distance bounds."""
    spec_path = args.spec.resolve()
    output = args.output.resolve()
    raw = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"tolerance", "cases"} or not isinstance(raw["cases"], list):
        raise ValueError("family-frontier spec needs exactly tolerance and cases")
    if not raw["cases"]:
        raise ValueError("family-frontier spec needs at least one case")

    def parse_family(item: dict) -> FamilyComparison:
        if not isinstance(item, dict) or set(item) != {"name", "distance", "evidence"}:
            raise ValueError("family needs exactly name, distance and evidence")
        distance = item["distance"]
        if not isinstance(distance, dict) or set(distance) != {"lower", "upper"}:
            raise ValueError("distance needs exactly lower and upper")
        return FamilyComparison(item["name"], DistanceInterval(**distance), item["evidence"])

    reports = []
    seen = set()
    for case in raw["cases"]:
        if not isinstance(case, dict) or set(case) != {"id", "reference", "alternatives"}:
            raise ValueError("case needs exactly id, reference and alternatives")
        if not isinstance(case["id"], str) or not case["id"].strip() or case["id"] in seen:
            raise ValueError("case IDs must be distinct nonempty strings")
        seen.add(case["id"])
        if not isinstance(case["alternatives"], list):
            raise ValueError("alternatives must be a list")
        comparison = compare_families(
            parse_family(case["reference"]),
            tuple(parse_family(family) for family in case["alternatives"]),
            raw["tolerance"],
        )
        reports.append({"id": case["id"], **comparison})
    report = {
        "status": "COMPLETED_CONDITIONAL_FAMILY_FRONTIER",
        "input_sha256": sha256(spec_path),
        "implementation_sha256": sha256(Path(__file__).resolve()),
        "family_frontier_module_sha256": sha256(Path(family_frontier_module.__file__).resolve()),
        "input_evidence_status": "supplied_distance_bounds_not_replayed_by_this_command",
        "cases": reports,
    }
    with fresh_output_directory(output) as stage:
        (stage / "result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "cases": len(reports), "output": str(output)}, indent=2))
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
    robust=subparsers.add_parser("robust-audit",help="classify an attribution claim across a declared forward-model set")
    robust.add_argument("--spec",required=True,type=Path,help="JSON with residual bounds, column radii and in-set scenarios")
    robust.add_argument("--output",required=True,type=Path,help="new output directory; existing paths are rejected")
    robust.set_defaults(handler=run_robust_audit)
    frontier=subparsers.add_parser("family-frontier",help="show tolerance windows where an alternative source family refutes a reference exclusion")
    frontier.add_argument("--spec",required=True,type=Path,help="JSON with supplied distance bounds for each family")
    frontier.add_argument("--output",required=True,type=Path,help="new output directory; existing paths are rejected")
    frontier.set_defaults(handler=run_family_frontier)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, TypeError, OSError, json.JSONDecodeError, PermissionError) as exc:
        print(f"observable-geometry: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
