"""Fit the K=1 WBEN reference to a synthetic graph using the sub-01 leadfield.

This is development simulation only. It loads an anatomical forward operator
and saved synthetic arrays, never participant recordings or outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from observable_geometry.track_b.synthetic import SyntheticConfig, generate_synthetic
from observable_geometry.track_b.wben import fit_wben_k1


DEFAULT_OPERATOR_DIR = ROOT / "outputs" / "track_b" / "sub01_geometric_operator_20261022_v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def average_precision(truth: np.ndarray, scores: np.ndarray) -> float:
    mask = ~np.eye(truth.shape[0], dtype=bool)
    labels = truth[mask].astype(bool)
    values = scores[mask]
    positives = int(labels.sum())
    if positives == 0:
        raise ValueError("average precision is undefined without positive edges")
    order = np.argsort(-values, kind="stable")
    ranked = labels[order]
    precision = np.cumsum(ranked) / np.arange(1, len(ranked) + 1)
    return float(precision[ranked].sum() / positives)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operator-dir", type=Path, default=DEFAULT_OPERATOR_DIR)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=20261022)
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--max-em-iterations", type=int, default=200)
    parser.add_argument("--initialization", choices=("zero", "pseudoinverse"), default="zero")
    args = parser.parse_args()
    operator_dir = args.operator_dir.resolve()
    out_dir = args.out_dir.resolve()
    if out_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {out_dir}")
    report_path = operator_dir / "operator_report.json"
    operator_path = operator_dir / "sub01_geometric_leadfield.npz"
    operator_report = json.loads(report_path.read_text(encoding="utf-8"))
    if sha256(operator_path) != operator_report["operator_sha256"]:
        raise SystemExit("operator checksum does not match its report")
    with np.load(operator_path, allow_pickle=False) as stored:
        scalp_operator = stored["scalp_operator"].astype(np.float64)

    scale = 1e-8  # source innovations: 10 nA m, used only for unit scaling
    config = SyntheticConfig(
        n_regions=scalp_operator.shape[1], n_scalp=scalp_operator.shape[0],
        n_active_regions=10, max_indegree=2, n_ieeg_regions=21,
        n_samples=args.samples, target_radius=0.85,
        scalp_snr_db=-5.0, ieeg_snr_db=30.0,
        innovation_scale=scale, seed=args.seed,
    )
    data = generate_synthetic(config, scalp_operator=scalp_operator)
    h = np.vstack([data.scalp_operator, data.ieeg_operator])
    observations = np.column_stack([data.scalp, data.ieeg])
    scalp_noise_var = float(np.mean(np.square(data.scalp_noise)))
    ieeg_noise_var = float(np.mean(np.square(data.ieeg_noise)))
    r = np.diag(np.r_[np.full(data.scalp.shape[1], scalp_noise_var),
                      np.full(data.ieeg.shape[1], ieeg_noise_var)])
    penalty = 0.01 * (args.samples - 1) * scale**2
    init_cov = np.eye(config.n_regions) * scale**2
    variance_floor = scale**2 * 1e-8

    out_dir.mkdir(parents=True, exist_ok=False)
    inputs_path = out_dir / "known_truth_inputs.npz"
    np.savez_compressed(
        inputs_path,
        adjacency=data.adjacency, transition=data.transition, latent=data.latent,
        scalp_operator=data.scalp_operator, ieeg_operator=data.ieeg_operator,
        scalp=data.scalp, ieeg=data.ieeg, scalp_noise=data.scalp_noise,
        ieeg_noise=data.ieeg_noise, observations=observations,
        observation_operator=h, observation_noise_covariance=r,
        active_region_indices=data.active_region_indices,
        ieeg_region_indices=data.ieeg_region_indices,
    )
    input_hash = sha256(inputs_path)
    result: dict = {
        "run_id": out_dir.name,
        "run_role": "development_known_truth_simulation",
        "status": "RUNNING",
        "participant_signal_arrays_used": False,
        "confirmatory_data_used": False,
        "operator_path": str(operator_path.relative_to(ROOT)) if operator_path.is_relative_to(ROOT) else str(operator_path),
        "operator_sha256": operator_report["operator_sha256"],
        "input_arrays": inputs_path.name,
        "input_arrays_sha256": input_hash,
        "config": {**config.__dict__, "penalty": penalty,
                    "penalty_sign": "minus", "initialization": args.initialization,
                    "initial_state_covariance": "innovation_scale^2 I",
                    "initial_process_covariance": "innovation_scale^2 I",
                    "variance_floor": variance_floor,
                    "max_em_iterations": args.max_em_iterations,
                    "tolerance_per_sample": 1e-6},
        "model_notes": [
            "The scalp operator derives from one participant's released anatomical forward solution, aggregated into geometric parcels.",
            "The 69 simulation nodes are not atlas labels.",
            "The iEEG observation is idealized direct selection of latent nodes; no electrode-level iEEG physics is simulated.",
            "Noise covariance is known by construction and fixed in the model; this is an optimistic development condition.",
        ],
    }
    report_file = out_dir / "development_report.json"
    try:
        fit = fit_wben_k1(
            observations, h, r, penalty=penalty, penalty_sign="minus",
            initialization=args.initialization, initial_process_covariance=init_cov,
            initial_state_covariance=init_cov, max_iter=args.max_em_iterations,
            tolerance_per_sample=1e-6, variance_floor=variance_floor,
        )
        estimate = fit.transition
        ap = average_precision(data.adjacency, np.abs(estimate))
        oracle_coef = data.latent[1:].T @ data.latent[:-1] @ np.linalg.pinv(
            data.latent[:-1].T @ data.latent[:-1])
        oracle_ap = average_precision(data.adjacency, np.abs(oracle_coef))
        estimate_path = out_dir / "estimated_transition.npy"
        np.save(estimate_path, estimate, allow_pickle=False)
        result.update({
            "status": "PASS" if fit.converged else "NON_CONVERGED",
            "converged": fit.converged,
            "iterations": fit.iterations,
            "log_likelihood": list(fit.log_likelihood),
            "penalized_objective": list(fit.penalized_objective),
            "estimated_transition": estimate_path.name,
            "estimated_transition_sha256": sha256(estimate_path),
            "edge_recovery": {
                "wben_average_precision": ap,
                "oracle_state_var_average_precision": oracle_ap,
                "no_skill_prevalence": float(data.adjacency.sum() / (config.n_regions * (config.n_regions - 1))),
                "positive_edges": int(data.adjacency.sum()),
                "edge_scores": "absolute fitted transition coefficient; diagonal excluded",
                "primary_unit": "one simulated graph seed; exploratory only",
            },
            "realized_snr_db": list(data.realized_snr_db),
            "transition_spectral_radius_truth": float(np.max(np.abs(np.linalg.eigvals(data.transition)))),
            "transition_spectral_radius_estimate": float(np.max(np.abs(np.linalg.eigvals(estimate)))),
        })
    except Exception as exc:  # preserve failed development attempts as artifacts
        result.update({"status": "FAIL", "error_type": type(exc).__name__, "error": str(exc)})
    report_file.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "report": str(report_file),
                      "arrays_sha256": input_hash,
                      "edge_recovery": result.get("edge_recovery"),
                      "error": result.get("error")}, indent=2))
    return 0 if result["status"] in ("PASS", "NON_CONVERGED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
