"""Matched fixed-subspace comparison for the relative tail-closed objective."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def direct_fixed_subspace_margin(b: np.ndarray, c_values: np.ndarray, e: np.ndarray,
                                 eta: float, basis: np.ndarray,
                                 multipliers: np.ndarray) -> tuple[float, float]:
    """Direct Cholesky evaluation of max_t lambda_min(V'HV,V'B'BV)."""
    signal_gram = b.T @ b
    g = basis.T @ signal_gram @ basis
    chol = np.linalg.cholesky((g + g.T) / 2)
    best = 0.0
    best_t = 0.0
    p_eye = np.eye(b.shape[1])
    for t in multipliers[1:]:
        h = t * (e.T @ ((1.0 / (c_values + t))[:, None] * e)) - t * eta**2 * p_eye
        q = basis.T @ ((h + h.T) / 2) @ basis
        left = np.linalg.solve(chol, q)
        whitened = np.linalg.solve(chol, left.T).T
        value = float(np.linalg.eigvalsh((whitened + whitened.T) / 2)[0])
        if value > best:
            best = value
            best_t = float(t)
    return float(np.sqrt(max(best, 0.0))), best_t


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operator-grams", type=Path, required=True)
    parser.add_argument("--frontier-run", type=Path, required=True)
    parser.add_argument("--reference-result", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.out}")
    result_path = args.frontier_run / "result.json"
    arrays_path = args.frontier_run / "frontier.npz"
    if not result_path.is_file() or not arrays_path.is_file():
        raise SystemExit("frontier run is incomplete")
    with np.load(args.operator_grams, allow_pickle=False) as data:
        b0 = np.asarray(data["retained_operator"], dtype=np.float64)
        c0 = np.asarray(data["full_tail"], dtype=np.float64)
    frontier_result = json.loads(result_path.read_text(encoding="utf-8"))
    reference = json.loads(args.reference_result.read_text(encoding="utf-8"))
    epsilon = float(reference["gram_error_bound"])
    eta = float(frontier_result["eta"])
    grid_size = int(frontier_result["variants"]["error_inflated"]["grid_size"])
    scale = float(frontier_result["variants"]["error_inflated"]["operator_scale"])
    b = b0 / scale
    c = (c0 + c0.T) / (2 * scale**2) + (epsilon / scale**2) * np.eye(c0.shape[0])
    c_values, c_vectors = np.linalg.eigh((c + c.T) / 2)
    e = c_vectors.T @ b
    singular_values = np.linalg.svd(b, compute_uv=False)
    t_max = float(singular_values[0] ** 2 / eta**2)
    multipliers = np.r_[0.0, np.geomspace(t_max * 1e-16, t_max, grid_size)]
    _, _, right_t = np.linalg.svd(b, full_matrices=False)
    p = b.shape[1]
    if p % 2:
        raise SystemExit("bilateral low-mode comparator requires an even coefficient dimension")
    half = p // 2
    order = np.column_stack((np.arange(half), np.arange(half, p))).reshape(-1)
    low_modes = np.eye(p)[:, order]

    rows: list[dict] = []
    with np.load(arrays_path, allow_pickle=False) as saved:
        candidate_margins = np.asarray(frontier_result["variants"]["error_inflated"]["margins"])
        for rank in range(1, p + 1):
            candidate_key = f"robust_basis_{rank}"
            if candidate_key not in saved.files:
                # No positive candidate certificate was produced at this rank.
                if candidate_margins[rank - 1] > 0:
                    raise SystemExit(f"missing candidate basis for positive rank {rank}")
                continue
            bases = {
                "relative_frontier_selected": np.asarray(saved[candidate_key], dtype=np.float64),
                "bilateral_low_modes": low_modes[:, :rank],
                "sensor_svd": right_t.T[:, :rank],
            }
            for family, basis in bases.items():
                score, best_t = direct_fixed_subspace_margin(b, c_values, e, eta, basis, multipliers)
                rows.append({"rank": rank, "family": family,
                             "relative_margin_lower": score,
                             "selected_multiplier_scaled": best_t,
                             "frontier_margin_at_selected_multiplier": (
                                 float(candidate_margins[rank - 1])
                                 if family == "relative_frontier_selected" else None)})

    thresholds = (0.01, 0.02, 0.05, 0.10)
    threshold_ranks = {}
    for threshold in thresholds:
        threshold_ranks[format(threshold, ".6g")] = {}
        for family in ("relative_frontier_selected", "bilateral_low_modes", "sensor_svd"):
            passing = [row["rank"] for row in rows if row["family"] == family
                       and row["relative_margin_lower"] > threshold]
            threshold_ranks[format(threshold, ".6g")][family] = max(passing, default=0)

    args.out.mkdir(parents=True)
    inputs = (args.operator_grams, result_path, arrays_path, args.reference_result)
    root = Path(__file__).resolve().parents[2]
    code_paths = {
        "comparison_runner": Path(__file__).resolve(),
        "independent_verifier": root / "scripts" / "track_b" / "verify_relative_frontier_baselines.py",
    }
    if not all(path.is_file() for path in code_paths.values()):
        raise SystemExit("comparison provenance verifier is missing")
    result = {
        "status": "RETROSPECTIVE_MODEL_ONLY_MATCHED_RELATIVE_MARGIN_COMPARISON",
        "estimand": "max over the same fixed multiplier grid of the minimum relative residual margin on each subspace",
        "eta": eta,
        "gram_error_bound": epsilon,
        "grid_size": grid_size,
        "source_paths": {
            "operator_grams": str(args.operator_grams.resolve()),
            "frontier_result": str(result_path.resolve()),
            "frontier_arrays": str(arrays_path.resolve()),
            "reference_result": str(args.reference_result.resolve()),
        },
        "input_sha256": {str(path.resolve()): sha256(path) for path in inputs},
        "code_sha256": {key: sha256(path) for key, path in code_paths.items()},
        "direct_fitting_equivalence": (
            "For each fixed t, maximizing the minimum generalized Rayleigh quotient over rank-k subspaces "
            "is exactly the top-k generalized-eigenvalue problem. The selected method is this direct fit/design, "
            "not a distinct algorithmic baseline or independent method."
        ),
        "threshold_rank_counts": threshold_ranks,
        "rows": rows,
        "limitations": [
            "One saved participant-specific forward model and declared shifted-FEM tail prior; no EEG/SEEG samples or outcomes read.",
            "Finite-grid numerical lower bounds; not continuous-multiplier global optima or outward-rounded certificates.",
            "The selected basis optimizes this same objective, so superiority to fixed low-mode and sensor-SVD bases is expected and not novelty.",
            "Thresholds are descriptive and post hoc, not calibrated noise or detectability levels.",
            "No physiological source recovery, generalization, or researcher decision benefit is established.",
        ],
    }
    (args.out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "threshold_rank_counts": threshold_ranks}, indent=2))


if __name__ == "__main__":
    main()
