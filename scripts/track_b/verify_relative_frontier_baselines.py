"""Independent direct-solve replay of matched relative-margin baseline rows."""
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


def direct_margin_squared(b: np.ndarray, c: np.ndarray, eta: float,
                          basis: np.ndarray, t: float) -> float:
    h = t * (b.T @ np.linalg.solve(c + t * np.eye(c.shape[0]), b))
    h -= t * eta**2 * np.eye(b.shape[1])
    g = b.T @ b
    qv = basis.T @ ((h + h.T) / 2) @ basis
    gv = basis.T @ g @ basis
    chol = np.linalg.cholesky((gv + gv.T) / 2)
    left = np.linalg.solve(chol, qv)
    whitened = np.linalg.solve(chol, left.T).T
    return float(np.linalg.eigvalsh((whitened + whitened.T) / 2)[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit(f"refusing to overwrite existing verifier output: {args.out}")
    result_path = args.run / "result.json"
    if not result_path.is_file():
        raise SystemExit("comparison result.json is missing")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    expected_inputs = result["input_sha256"]
    for filename, expected in expected_inputs.items():
        path = Path(filename)
        if not path.is_file() or sha256(path) != expected:
            raise SystemExit(f"input hash mismatch: {path}")
    root = Path(__file__).resolve().parents[2]
    code_paths = {
        "comparison_runner": root / "scripts" / "track_b" / "compare_relative_frontier_baselines.py",
        "independent_verifier": Path(__file__).resolve(),
    }
    expected_code = result.get("code_sha256", {})
    if set(expected_code) != set(code_paths) or any(
        not path.is_file() or sha256(path) != expected_code[key]
        for key, path in code_paths.items()
    ):
        raise SystemExit("code hash mismatch")

    grams = Path(result["source_paths"]["operator_grams"])
    frontier_json = Path(result["source_paths"]["frontier_result"])
    frontier_npz = Path(result["source_paths"]["frontier_arrays"])
    reference_json = Path(result["source_paths"]["reference_result"])
    with np.load(grams, allow_pickle=False) as data:
        b0 = np.asarray(data["retained_operator"], dtype=np.float64)
        c0 = np.asarray(data["full_tail"], dtype=np.float64)
    frontier = json.loads(frontier_json.read_text(encoding="utf-8"))
    reference = json.loads(reference_json.read_text(encoding="utf-8"))
    epsilon = float(reference["gram_error_bound"])
    eta = float(result["eta"])
    variant = frontier["variants"]["error_inflated"]
    scale = float(variant["operator_scale"])
    b = b0 / scale
    c = (c0 + c0.T) / (2 * scale**2) + (epsilon / scale**2) * np.eye(c0.shape[0])
    p = b.shape[1]
    _, _, right_t = np.linalg.svd(b, full_matrices=False)
    order = np.column_stack((np.arange(p // 2), np.arange(p // 2, p))).reshape(-1)
    low = np.eye(p)[:, order]
    rows = result["rows"]
    if len(rows) != 75:
        raise SystemExit(f"expected 75 matched rows, found {len(rows)}")
    unique = {(int(row["rank"]), row["family"]) for row in rows}
    if len(unique) != len(rows):
        raise SystemExit("duplicate rank/family row")
    worst_excess = 0.0
    largest_margin_difference = 0.0
    replayed = 0
    for row in rows:
        rank = int(row["rank"])
        family = row["family"]
        if not 1 <= rank <= 25 or family not in {
            "relative_frontier_selected", "bilateral_low_modes", "sensor_svd"
        }:
            raise SystemExit("unexpected rank or family")
        with np.load(frontier_npz, allow_pickle=False) as saved:
            if family == "relative_frontier_selected":
                basis = np.asarray(saved[f"robust_basis_{rank}"], dtype=np.float64)
            elif family == "bilateral_low_modes":
                basis = low[:, :rank]
            else:
                basis = right_t.T[:, :rank]
        t = float(row["selected_multiplier_scaled"])
        margin = float(row["relative_margin_lower"])
        if not np.isfinite(margin) or margin < 0:
            raise SystemExit("invalid saved margin or multiplier")
        if margin == 0 and t == 0:
            replayed += 1
            continue
        if t <= 0:
            raise SystemExit("positive margin requires a positive multiplier")
        actual_squared = direct_margin_squared(b, c, eta, basis, t)
        reported_squared = margin**2
        excess = reported_squared - actual_squared
        tolerance = 5e-8 * max(1.0, reported_squared, abs(actual_squared))
        worst_excess = max(worst_excess, excess)
        margin_difference = abs(np.sqrt(max(actual_squared, 0.0)) - margin)
        largest_margin_difference = max(largest_margin_difference, margin_difference)
        if excess > tolerance or margin_difference > 5e-7:
            raise SystemExit(f"direct replay mismatch at rank {rank}, family {family}")
        if family == "relative_frontier_selected":
            frontier_margin = float(variant["margins"][rank - 1])
            if margin + 5e-7 < frontier_margin:
                raise SystemExit(f"selected subspace fails its frontier lower bound at rank {rank}")
        replayed += 1

    threshold_ranks = result["threshold_rank_counts"]
    for threshold, families in threshold_ranks.items():
        value = float(threshold)
        for family, reported_rank in families.items():
            passing = [int(row["rank"]) for row in rows if row["family"] == family
                       and float(row["relative_margin_lower"]) > value]
            if max(passing, default=0) != int(reported_rank):
                raise SystemExit(f"threshold summary mismatch at {threshold}/{family}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "PASS_MATCHED_BASELINE_DIRECT_REPLAY_MODEL_ONLY",
        "input_hashes_verified": True,
        "code_hashes_verified": True,
        "rows_replayed": replayed,
        "worst_reported_squared_margin_minus_replay": worst_excess,
        "maximum_margin_difference": largest_margin_difference,
        "claim_boundary": "Replay verifies attained margins for saved finite-grid subspaces under one model only; it does not validate physiological sources, global optimality over continuous t, superiority of an optimized method, or novelty.",
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
