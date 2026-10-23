"""Audit B2 model provenance using only metadata and permitted model arrays.

This script never opens the recorded EEG ``data`` member. Its NPZ accesses are
wrapped by the same runtime key allowlist used by the v11 recomputation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

import h5py
import mne
import numpy as np
from mne.io.constants import FIFF


ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "outputs" / "tracka_release_20261022_v2"
SPEC_PATH = ROOT / "docs" / "track_b" / "B2_GBF_SPEC.md"
VERIFIER_PATH = ROOT / "scripts" / "track_b" / "recompute_b2_gbf_cpu64_v11.py"
CORE_PATH = ROOT / "src" / "observable_geometry" / "core.py"
NOMINAL_PATH = ROOT / "src" / "observable_geometry" / "nominal.py"
PILOT_PATH = ROOT / "scripts" / "pilot_localize.py"
COMPLETE_PATH = ROOT / "scripts" / "complete_track_a.py"
FORWARD_PATH = ROOT / "data" / "payload" / "derivatives" / "sourcemodelling" / "sub-01" / "fwd" / "sub-01_fwd.fif"
TRANSFORM_PATH = ROOT / "data" / "Localize-MI" / "derivatives" / "sourcemodelling" / "sub-01" / "xfm" / "sub-01_from-head_to-surface.h5"
CHANNELS_PATH = ROOT / "data" / "Localize-MI" / "derivatives" / "epochs" / "sub-01" / "eeg" / "sub-01_task-seegstim_run-01_channels.tsv"
ELECTRODES_PATH = ROOT / "data" / "Localize-MI" / "derivatives" / "epochs" / "sub-01" / "eeg" / "sub-01_task-seegstim_electrodes.tsv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_runtime_guard():
    spec = importlib.util.spec_from_file_location("b2_v11_provenance", VERIFIER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def build_report(output: Path) -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_b2_provenance_audit"
    access_log = output / "npz_key_access.jsonl"
    guard = load_runtime_guard()

    with (TRACK_A / "run_manifest.json").open(encoding="utf-8") as f:
        manifest = json.load(f)
    with (TRACK_A / "prepared_bundle.json").open(encoding="utf-8") as f:
        bundle_meta = json.load(f)
    with (TRACK_A / "case_validation.json").open(encoding="utf-8") as f:
        case = json.load(f)

    required_artifacts = {
        "prepared_bundle": TRACK_A / "prepared_bundle.npz",
        "nominal_signature_library": TRACK_A / "nominal_signature_library.npz",
        "case_validation": TRACK_A / "case_validation.json",
        "prepared_bundle_metadata": TRACK_A / "prepared_bundle.json",
        "run_manifest": TRACK_A / "run_manifest.json",
    }
    artifact_hashes = {name: sha256(path) for name, path in required_artifacts.items()}
    manifest_artifacts = manifest["artifact_files_sha256"]
    for name in ("prepared_bundle", "nominal_signature_library", "case_validation", "prepared_bundle_metadata"):
        rel = f"outputs/tracka_release_20261022_v2/{required_artifacts[name].name}"
        if manifest_artifacts.get(rel) != artifact_hashes[name]:
            raise AssertionError(f"run manifest artifact hash mismatch: {rel}")

    with guard.guarded_npz(TRACK_A / "prepared_bundle.npz", guard.PREPARED_ALLOWED_KEYS, access_log, run_id) as z:
        leadfield = np.asarray(z["leadfield"], dtype=np.float64)
        covariance = np.asarray(z["noise_cov"], dtype=np.float64)
    with guard.guarded_npz(TRACK_A / "nominal_signature_library.npz", guard.SIGNATURE_ALLOWED_KEYS, access_log, run_id) as z:
        coordinates = np.asarray(z["source_coordinates"], dtype=np.float64)
        vertex_ids = np.asarray(z["vertex_ids"], dtype=np.int64)

    if leadfield.shape != (236, 8196) or covariance.shape != (236, 236):
        raise AssertionError(f"unexpected model dimensions: leadfield={leadfield.shape}, covariance={covariance.shape}")
    if coordinates.shape != (8196, 3) or vertex_ids.shape != (8196,):
        raise AssertionError("source coordinate/vertex metadata dimensions do not match the frozen case")

    channels = tsv_rows(CHANNELS_PATH)
    good_channels = [row["name"] for row in channels if row["status"] == "good"]
    fwd = mne.read_forward_solution(FORWARD_PATH, verbose="ERROR")
    fwd = mne.pick_channels_forward(fwd, include=good_channels, ordered=True, copy=True, verbose="ERROR")
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True, use_cps=True, copy=True, verbose="ERROR")
    forward_names = list(fwd["sol"]["row_names"])
    prepared_names = list(bundle_meta["channel_names"])
    if forward_names != prepared_names:
        raise AssertionError("converted forward channel order does not exactly match the prepared bundle")
    if int(fwd["source_ori"]) != int(FIFF.FIFFV_MNE_FIXED_ORI):
        raise AssertionError(f"converted forward orientation is not fixed: source_ori={fwd['source_ori']}")
    if len(fwd["src"]) != 2 or sum(len(s["vertno"]) for s in fwd["src"]) != leadfield.shape[1]:
        raise AssertionError("forward source-space vertices do not align with saved leadfield columns")

    source_coords = np.vstack([s["rr"][s["vertno"]] for s in fwd["src"]])
    coordinate_error = np.linalg.norm(coordinates - source_coords, axis=1)
    if float(coordinate_error.max(initial=0.0)) > 1e-12:
        raise AssertionError("saved comparison coordinates do not match forward source order")
    vertex_ids_forward = np.concatenate([s["vertno"] for s in fwd["src"]]).astype(np.int64)
    if not np.array_equal(vertex_ids, vertex_ids_forward):
        raise AssertionError("saved vertex IDs do not match converted forward source order")

    if set(good_channels) != set(prepared_names) or len(good_channels) != len(prepared_names):
        raise AssertionError("prepared channel set does not match the run's metadata-marked good EEG channels")
    if len(set(prepared_names)) != len(prepared_names):
        raise AssertionError("duplicate channel names in prepared channel order")

    electrode_rows = {row["name"]: row for row in tsv_rows(ELECTRODES_PATH)}
    sensor_xyz = np.vstack([[float(electrode_rows[name][axis]) for axis in ("x", "y", "z")] for name in prepared_names])
    forward_xyz = np.vstack([np.asarray(channel["loc"][:3], dtype=float) for channel in fwd["info"]["chs"]])
    sensor_position_errors_mm = np.linalg.norm(sensor_xyz - forward_xyz, axis=1) * 1000
    if float(sensor_position_errors_mm.max(initial=0.0)) > 0.1:
        raise AssertionError("forward and metadata electrode positions differ by more than 0.1 mm")

    # Check the declared common-average reference projector on both saved model arrays.
    n_channels = leadfield.shape[0]
    projector = np.eye(n_channels) - np.ones((n_channels, n_channels)) / n_channels
    projected_leadfield = projector @ fwd["sol"]["data"]
    forward_to_bundle_relerr = float(np.linalg.norm(leadfield - projected_leadfield) / max(np.linalg.norm(projected_leadfield), np.finfo(float).tiny))
    if forward_to_bundle_relerr > 1e-10:
        raise AssertionError(f"saved leadfield is not the common-average-projected converted forward (relative error {forward_to_bundle_relerr:g})")
    leadfield_projection_relerr = float(np.linalg.norm(leadfield - projector @ leadfield) / max(np.linalg.norm(leadfield), np.finfo(float).tiny))
    covariance_projection_relerr = float(np.linalg.norm(covariance - projector @ covariance @ projector.T) / max(np.linalg.norm(covariance), np.finfo(float).tiny))
    if leadfield_projection_relerr > 1e-10 or covariance_projection_relerr > 1e-10:
        raise AssertionError("saved leadfield or covariance does not satisfy the common-average reference projection")

    eigenvalues = np.linalg.eigvalsh((covariance + covariance.T) * 0.5)
    covariance_scale = max(float(np.max(np.abs(eigenvalues))), np.finfo(np.float64).tiny)
    rank_threshold = 1e-10 * covariance_scale
    covariance_rank = int(np.count_nonzero(eigenvalues > rank_threshold))
    if float(eigenvalues.min()) < -1e-10 * covariance_scale:
        raise AssertionError("noise covariance is not positive semidefinite at the frozen tolerance")
    if covariance_rank != n_channels - 1:
        raise AssertionError(f"expected average-reference covariance rank {n_channels - 1}; measured {covariance_rank}")

    with h5py.File(TRANSFORM_PATH, "r") as h5:
        transform = np.asarray(h5["trans"][()], dtype=np.float64)
    if transform.shape != (4, 4) or not np.allclose(transform[3], [0, 0, 0, 1], atol=1e-12):
        raise AssertionError("head-to-surface transform is not a valid homogeneous affine matrix")
    if bundle_meta.get("coordinate_frame") != int(fwd["src"][0]["coord_frame"]):
        raise AssertionError("prepared bundle coordinate-frame metadata does not match forward source space")

    input_hashes = {
        "forward": sha256(FORWARD_PATH),
        "head_to_surface_transform": sha256(TRANSFORM_PATH),
        "run_channels_tsv": sha256(CHANNELS_PATH),
        "electrodes_tsv": sha256(ELECTRODES_PATH),
    }
    if case["hashes_sha256"].get("forward") != input_hashes["forward"]:
        raise AssertionError("case validation forward hash differs from current forward file")
    if case["hashes_sha256"].get("head_to_surface") != input_hashes["head_to_surface_transform"]:
        raise AssertionError("case validation transform hash differs from current transform file")
    for relative, actual in [
        ("data/payload/derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif", input_hashes["forward"]),
        ("data/Localize-MI/derivatives/sourcemodelling/sub-01/xfm/sub-01_from-head_to-surface.h5", input_hashes["head_to_surface_transform"]),
        ("data/Localize-MI/derivatives/epochs/sub-01/eeg/sub-01_task-seegstim_run-01_channels.tsv", input_hashes["run_channels_tsv"]),
        ("data/Localize-MI/derivatives/epochs/sub-01/eeg/sub-01_task-seegstim_electrodes.tsv", input_hashes["electrodes_tsv"]),
    ]:
        if manifest.get("input_files_sha256", {}).get(relative) != actual:
            raise AssertionError(f"run manifest input hash mismatch: {relative}")

    core_text = CORE_PATH.read_text(encoding="utf-8")
    import ast
    core_tree = ast.parse(core_text, filename=str(CORE_PATH))
    psd_node = next(n for n in core_tree.body if isinstance(n, ast.FunctionDef) and n.name == "_psd_eigh")
    psd_source = ast.get_source_segment(core_text, psd_node)
    assert psd_source is not None
    psd_hash = hashlib.sha256(psd_source.encode("utf-8")).hexdigest()

    access_events = [json.loads(line) for line in access_log.read_text(encoding="utf-8").splitlines()]
    denied = [event for event in access_events if event["decision"] != "allow"]
    if denied:
        raise AssertionError(f"unexpected denied accesses during provenance audit: {denied}")
    if any(event["key"] == "data" for event in access_events):
        raise AssertionError("recorded EEG data key was attempted during provenance audit")

    return {
        "status": "PASS",
        "audit_type": "B2 head-model, channel, reference, covariance, orientation, and artifact provenance; model arrays only",
        "specification": {"path": str(SPEC_PATH.relative_to(ROOT)), "sha256": sha256(SPEC_PATH), "spec_id": "B2-GBF-2026-10-23-v10"},
        "verifier": {"path": str(VERIFIER_PATH.relative_to(ROOT)), "sha256": sha256(VERIFIER_PATH), "revision": "v11"},
        "implementation": {
            "mne_version": mne.__version__,
            "conversion": {"surf_ori": True, "force_fixed": True, "use_cps": True, "source_ori_value": int(fwd["source_ori"]), "mne_fixed_orientation_constant": int(FIFF.FIFFV_MNE_FIXED_ORI)},
            "conversion_code_path": str(PILOT_PATH.relative_to(ROOT)),
            "conversion_code_sha256": sha256(PILOT_PATH),
            "postprocessing_code_path": str(COMPLETE_PATH.relative_to(ROOT)),
            "postprocessing_code_sha256": sha256(COMPLETE_PATH),
            "production_core_path": str(CORE_PATH.relative_to(ROOT)),
            "production_core_sha256": sha256(CORE_PATH),
            "nominal_implementation_path": str(NOMINAL_PATH.relative_to(ROOT)),
            "nominal_implementation_sha256": sha256(NOMINAL_PATH),
            "_psd_eigh_source_sha256": psd_hash,
            "_psd_eigh_source": psd_source,
            "v11_verifier_sha256": sha256(VERIFIER_PATH),
        },
        "input_artifact_sha256": input_hashes,
        "sealed_artifact_sha256": artifact_hashes,
        "channel_order": {
            "channel_count": len(prepared_names),
            "prepared_order_equals_converted_forward_order": True,
            "prepared_set_equals_good_channel_metadata": True,
            "max_electrode_position_error_mm": float(sensor_position_errors_mm.max(initial=0.0)),
            "median_electrode_position_error_mm": float(np.median(sensor_position_errors_mm)),
            "channel_names": prepared_names,
        },
        "source_geometry": {
            "source_count": int(leadfield.shape[1]),
            "coordinate_frame_code": int(fwd["src"][0]["coord_frame"]),
            "coordinate_units": "metres (MNE forward source coordinates)",
            "max_saved_vs_forward_coordinate_error_m": float(coordinate_error.max(initial=0.0)),
            "vertex_ids_exact_match": True,
            "head_to_surface_transform_shape": list(transform.shape),
            "head_to_surface_transform_sha256": input_hashes["head_to_surface_transform"],
        },
        "reference_and_covariance": {
            "reference": bundle_meta["reference"],
            "projector": "R = I - 11^T / n_channels",
            "projector_symmetric_idempotent": bool(np.allclose(projector, projector.T) and np.allclose(projector @ projector, projector)),
            "leadfield_equals_projected_converted_forward_relative_frobenius_error": forward_to_bundle_relerr,
            "leadfield_reference_projection_relative_error": leadfield_projection_relerr,
            "covariance_reference_projection_relative_error": covariance_projection_relerr,
            "covariance_shape": list(covariance.shape),
            "covariance_symmetry_relative_error": float(np.linalg.norm(covariance - covariance.T) / max(np.linalg.norm(covariance), np.finfo(float).tiny)),
            "covariance_eigenvalue_min": float(eigenvalues.min()),
            "covariance_eigenvalue_max": float(eigenvalues.max()),
            "covariance_rank_threshold": rank_threshold,
            "covariance_supported_rank": covariance_rank,
            "covariance_rank_matches_average_reference": covariance_rank == n_channels - 1,
            "covariance_convention": bundle_meta["covariance_convention"],
            "noise_window_s": bundle_meta["noise_window"],
            "averaging_count": bundle_meta["averaging_count"],
        },
        "runtime_access_guard": {
            "status": "PASS",
            "allowed_keys": {"prepared_bundle.npz": sorted(guard.PREPARED_ALLOWED_KEYS), "nominal_signature_library.npz": sorted(guard.SIGNATURE_ALLOWED_KEYS)},
            "access_events": access_events,
            "access_log_sha256": sha256(access_log),
            "data_key_attempted": False,
            "enforcement": "NPZ key access is checked before NumPy member materialization; each attempt is appended and fsynced",
            "limitation": "Process-level Python guard and append-only audit file, not an OS sandbox or tamper-proof log",
        },
        "signal_data_access": {
            "prepared_bundle_data_key_accessed": False,
            "recorded_trial_or_eeg_sample_read_by_this_audit": False,
            "note": "Only leadfield, noise_cov, source coordinates, and vertex IDs were read from NPZ archives; all other provenance inputs were metadata/forward model files.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new output directory outside the sealed Track A release")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    if output == TRACK_A.resolve() or TRACK_A.resolve() in output.parents:
        raise SystemExit("Refusing to write inside the sealed Track A release")
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to write into a non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    report = build_report(output)
    report["output_dir"] = str(output)
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    path = output / "provenance_audit.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(path), "sha256": sha256(path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
