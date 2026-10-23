"""Export only allowlisted forward-model arrays for the generic B3/B8 CLI.

This adapter reads the sealed Track A manifest and model-only NPZ members.
It never indexes the recorded EEG ``data`` member.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "outputs/tracka_release_20261022_v2"
SPECS = {
    "prepared_bundle.npz": {
        "allowed": ("leadfield", "noise_cov"),
        "expected": "outputs/tracka_release_20261022_v2/prepared_bundle.npz",
    },
    "nominal_signature_library.npz": {
        "allowed": ("source_coordinates", "vertex_ids"),
        "expected": "outputs/tracka_release_20261022_v2/nominal_signature_library.npz",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def log_access(path: Path, archive: Path, key: str, decision: str) -> None:
    row = {"time_utc": datetime.now(timezone.utc).isoformat(),
           "archive": archive.name, "key": key, "decision": decision}
    fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, (json.dumps(row, sort_keys=True) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)


def read_key(path: Path, key: str, allowed: tuple[str, ...], log: Path) -> np.ndarray:
    decision = "allow" if key in allowed else "deny"
    log_access(log, path, key, decision)
    if decision != "allow":
        raise PermissionError(f"denied NPZ key {key!r} in {path.name}")
    with np.load(path, allow_pickle=False) as archive:
        return np.asarray(archive[key])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="new directory for the local model-only bundle; never overwritten")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing directory: {output}")
    output.mkdir(parents=True, exist_ok=False)
    access_log = output / "source_npz_key_access.jsonl"
    release_manifest_path = TRACK_A / "run_manifest.json"
    release_manifest = json.loads(release_manifest_path.read_text(encoding="utf-8"))
    input_hashes = {"run_manifest.json": sha256(release_manifest_path)}
    for name, spec in SPECS.items():
        path = TRACK_A / name
        actual = sha256(path)
        expected = release_manifest["artifact_files_sha256"][spec["expected"]]
        if actual != expected:
            raise RuntimeError(f"sealed artifact hash mismatch: {spec['expected']}")
        input_hashes[name] = actual

    prepared_path = TRACK_A / "prepared_bundle.npz"
    signature_path = TRACK_A / "nominal_signature_library.npz"
    leadfield = read_key(prepared_path, "leadfield", SPECS[prepared_path.name]["allowed"], access_log)
    covariance = read_key(prepared_path, "noise_cov", SPECS[prepared_path.name]["allowed"], access_log)
    coordinates = read_key(signature_path, "source_coordinates", SPECS[signature_path.name]["allowed"], access_log)
    vertex_ids = read_key(signature_path, "vertex_ids", SPECS[signature_path.name]["allowed"], access_log)

    prepared_meta = json.loads((TRACK_A / "prepared_bundle.json").read_text(encoding="utf-8"))
    metadata = {
        "dataset": prepared_meta["dataset"],
        "participant": "sub-01",
        "forward_model": prepared_meta["forward_provenance"],
        "reference": prepared_meta["reference"],
        "coordinate_frame": f"MNE source coordinate frame code {prepared_meta['coordinate_frame']}",
        "source_orientation": "fixed cortical-normal source columns from the sealed forward model",
        "noise_covariance": f"baseline window {prepared_meta['noise_window']} s; sealed noise_cov array",
        "sensor_names": prepared_meta["channel_names"],
    }
    if leadfield.shape != (len(metadata["sensor_names"]), len(vertex_ids)):
        raise ValueError("sealed leadfield dimensions do not match sensor names and vertex IDs")
    if covariance.shape != (leadfield.shape[0], leadfield.shape[0]):
        raise ValueError("sealed covariance dimensions do not match leadfield sensors")
    if coordinates.shape != (leadfield.shape[1], 3):
        raise ValueError("sealed source coordinates do not match leadfield columns")
    bundle_path = output / "model_bundle.npz"
    np.savez_compressed(bundle_path, leadfield=leadfield, noise_covariance=covariance,
                        coordinates_m=coordinates, source_ids=vertex_ids)
    metadata_path = output / "model_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    implementation = Path(__file__).resolve()
    manifest = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "MODEL_ONLY_EXPORT",
        "track_a_run_id": release_manifest.get("run_id"),
        "track_a_manifest_sha256": sha256(release_manifest_path),
        "input_sha256": input_hashes,
        "implementation_sha256": sha256(implementation),
        "output_sha256": {name: sha256(output / name) for name in
                          ("model_bundle.npz", "model_metadata.json", "source_npz_key_access.jsonl")},
        "source_keys_read": {
            "prepared_bundle.npz": ["leadfield", "noise_cov"],
            "nominal_signature_library.npz": ["source_coordinates", "vertex_ids"],
        },
        "recorded_EEG_data_key_accessed": False,
        "dimensions": {"sensors": int(leadfield.shape[0]), "sources": int(leadfield.shape[1]),
                       "covariance_rank_expected": int(np.linalg.matrix_rank(covariance))},
        "license_boundary": "Localize-MI is CC-BY-NC-SA 4.0; this local derivative is not included in a public source distribution and must not be redistributed without assessing the applicable terms.",
    }
    (output / "export_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "output": str(output),
                      "sensors": leadfield.shape[0], "sources": leadfield.shape[1],
                      "recorded_EEG_data_key_accessed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
