"""Audit exploratory sub-01 associations using sealed Track A outputs only.

This script does not open recordings or fit models. It joins the six already
reported 1 mA stimulation sites to the independently versioned B3 float64
distinguishability output and the sealed MNE resolution summary. All resulting
associations are descriptive and post hoc; the sites are from one participant.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "outputs" / "tracka_release_20261022_v2"
B3 = ROOT / "outputs" / "track_b" / "20261024_b3_gbf_tool_v1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def corr(x: list[float], y: list[float]) -> dict[str, float | int]:
    if len(x) != len(y) or len(x) < 3:
        raise ValueError("descriptive association requires at least three paired sites")
    return {
        "n_sites": len(x),
        "pearson_r": float(pearsonr(x, y).statistic),
        "spearman_rho": float(spearmanr(x, y).statistic),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT / "outputs" / "track_b")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", args.run_id):
        raise SystemExit("--run-id must be a safe 1-80 character identifier")
    out = (args.output_root / args.run_id).resolve()
    if not out.is_dir():
        raise SystemExit(f"Run directory must already exist and contain its session record: {out}")
    names = ["b4_site_associations.json", "b4_site_associations.csv", "b4_site_associations_manifest.json"]
    if any((out / name).exists() for name in names):
        raise SystemExit("Refusing to overwrite a B4 audit artifact")

    track_manifest = json.loads((TRACK_A / "run_manifest.json").read_text(encoding="utf-8"))
    expected = track_manifest["artifact_files_sha256"]
    inputs = {
        "track_a_report": TRACK_A / "empirical_evaluation_report.json",
        "track_a_resolution": TRACK_A / "mne_resolution_summary.npz",
        "track_a_signatures": TRACK_A / "nominal_signature_library.npz",
        "b3_float64": B3 / "distinguishability_float64.npz",
    }
    rels = {
        "track_a_report": "outputs/tracka_release_20261022_v2/empirical_evaluation_report.json",
        "track_a_resolution": "outputs/tracka_release_20261022_v2/mne_resolution_summary.npz",
        "track_a_signatures": "outputs/tracka_release_20261022_v2/nominal_signature_library.npz",
    }
    hashes = {name: sha256(path) for name, path in inputs.items()}
    for name, rel in rels.items():
        if hashes[name] != expected[rel]:
            raise RuntimeError(f"sealed Track A checksum mismatch: {rel}")
    b3_manifest = json.loads((B3 / "run_manifest.json").read_text(encoding="utf-8"))
    b3_expected = b3_manifest["output_sha256"]["distinguishability_float64.npz"]
    if hashes["b3_float64"] != b3_expected:
        raise RuntimeError("B3 float64 output checksum mismatch")

    report = json.loads(inputs["track_a_report"].read_text(encoding="utf-8"))
    with np.load(inputs["track_a_signatures"], allow_pickle=False) as z:
        track_a_rho = z["absolute_cosine"]
    with np.load(inputs["track_a_resolution"], allow_pickle=False) as z:
        psf_peak_error = z["peak_location_error_mm"]
        psf_spread = z["absolute_psf_weighted_distance_mm"]
        psf_mass10 = z["psf_l1_mass_within_10mm"]
        psf_diag = z["diagonal_to_peak_response_ratio"]
    with np.load(inputs["b3_float64"], allow_pickle=False) as z:
        b3_indices = z["candidate_indices"]
        b3_rho = z["absolute_cosine"]

    primary = [int(run) for run in report["primary_runs"]]
    if len(primary) != 6 or report["participant"] != "sub-01":
        raise RuntimeError("unexpected Track A development cohort or primary-site count")
    rows: list[dict[str, object]] = []
    for run in primary:
        site = report["per_run"][str(run)]
        i = int(site["target_vertex_index"])
        if i < 0 or i >= len(psf_peak_error) or not np.isfinite(b3_rho[i, 0]):
            raise RuntimeError(f"invalid target source record for run {run}")
        if int(b3_indices[i, 0]) < 0:
            raise RuntimeError(f"B3 has no valid distant alternative for run {run}")
        rho64 = float(b3_rho[i, 0])
        if abs(rho64 - float(track_a_rho[i, 0])) > 1e-7:
            raise RuntimeError(f"B3/Track A score parity failed at target index {i}")
        rows.append({
            "run": run,
            "site": site["label"],
            "target_vertex_index": i,
            "top_alternative_index": int(b3_indices[i, 0]),
            "top_alternative_abs_cosine_float64": rho64,
            "gbfs_artifact_localization_error_mm": float(site["gbfs_peak_error_mm"]),
            "mne_artifact_localization_error_mm": float(site["mne_peak_error_mm"]),
            "mne_psf_peak_location_error_mm": float(psf_peak_error[i]),
            "mne_psf_absolute_weighted_spread_mm": float(psf_spread[i]),
            "mne_psf_mass_within_10mm": float(psf_mass10[i]),
            "mne_psf_diagonal_to_peak_ratio": float(psf_diag[i]),
        })

    def col(key: str) -> list[float]:
        return [float(row[key]) for row in rows]

    observed_pair_rows = report["pair_similarity_rows"]
    pair_pred = [float(r["predicted_signature_similarity"]) for r in observed_pair_rows]
    pair_obs = [float(r["observed_artifact_similarity"]) for r in observed_pair_rows]
    associations = {
        "b2_best_distant_similarity_vs_gbfs_artifact_error": corr(
            col("top_alternative_abs_cosine_float64"), col("gbfs_artifact_localization_error_mm")),
        "b2_best_distant_similarity_vs_mne_artifact_error": corr(
            col("top_alternative_abs_cosine_float64"), col("mne_artifact_localization_error_mm")),
        "mne_psf_peak_offset_vs_mne_artifact_error": corr(
            col("mne_psf_peak_location_error_mm"), col("mne_artifact_localization_error_mm")),
        "mne_psf_weighted_spread_vs_mne_artifact_error": corr(
            col("mne_psf_absolute_weighted_spread_mm"), col("mne_artifact_localization_error_mm")),
        "mne_psf_mass10mm_vs_mne_artifact_error": corr(
            col("mne_psf_mass_within_10mm"), col("mne_artifact_localization_error_mm")),
        "forward_similarity_vs_observed_artifact_similarity": corr(pair_pred, pair_obs),
    }
    result = {
        "status": "completed exploratory retrospective audit; not confirmatory validation",
        "run_id": args.run_id,
        "task": "one-participant Localize-MI bipolar stimulation pulse artifact",
        "participant": "sub-01",
        "n_sites": len(rows),
        "n_dependent_site_pairs": len(observed_pair_rows),
        "independent_participant_count": 1,
        "associations": associations,
        "site_rows": rows,
        "interpretation": [
            "All associations are descriptive and post hoc; no p-values or population inference are reported.",
            "The stimulation pulse artifact is not an endogenous physiological source signal.",
            "The 15 site pairs reuse the same six sites and are not independent observations.",
            "The source-pattern score is nominal and model-conditional; it is not calibrated localization uncertainty.",
            "These results cannot establish incremental decision value or a novel method.",
        ],
        "data_access": {
            "recording_samples_opened_by_this_script": False,
            "model_scores_read_from": "sealed Track A and versioned B3 outputs",
            "held_out_participant_outcomes_opened": False,
        },
    }
    with (out / names[1]).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out / names[0]).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "run_id": args.run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python scripts/track_b/audit_b4_site_level_associations.py --run-id <run_id>",
        "input_sha256": hashes,
        "track_a_manifest_sha256": sha256(TRACK_A / "run_manifest.json"),
        "b3_manifest_sha256": sha256(B3 / "run_manifest.json"),
        "script_sha256": sha256(Path(__file__)),
        "output_sha256": {n: sha256(out / n) for n in names[:2]},
        "scope": "derived-output consistency and exploratory site-level association only; no raw recording access",
        "claim_boundary": "single participant, stimulation artifact, post hoc, descriptive",
    }
    (out / names[2]).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output_dir": str(out), "associations": associations}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
