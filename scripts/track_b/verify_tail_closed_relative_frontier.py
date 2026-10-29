"""Independent direct-matrix replay for a relative tail-closed frontier run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def generalized_minimum(q: np.ndarray, g: np.ndarray) -> float:
    """Compute the smallest eigenvalue of (q, g) by an independent Cholesky replay."""
    chol = np.linalg.cholesky((g + g.T) / 2)
    left = np.linalg.solve(chol, q)
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
    arrays_path = args.run / "frontier.npz"
    if not result_path.is_file() or not arrays_path.is_file():
        raise SystemExit("run result.json/frontier.npz is missing")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    source = Path(result["inputs"]["operator_grams"])
    reference = Path(result["inputs"]["reference_result"])
    expected_source_hash = result["inputs"]["operator_grams_sha256"]
    expected_reference_hash = result["inputs"]["reference_result_sha256"]
    hashes_ok = sha256(source) == expected_source_hash and sha256(reference) == expected_reference_hash
    if not hashes_ok:
        raise SystemExit("input hash mismatch; refusing to replay")
    root = Path(__file__).resolve().parents[2]
    current_code = {
        "tail_closed_module": root / "src" / "observable_geometry" / "track_b" / "tail_closed.py",
        "runner": root / "scripts" / "track_b" / "run_tail_closed_relative_frontier.py",
        "independent_verifier": Path(__file__).resolve(),
    }
    expected_code = result.get("code_sha256", {})
    if set(expected_code) != set(current_code) or any(
        not path.is_file() or sha256(path) != expected_code[key]
        for key, path in current_code.items()
    ):
        raise SystemExit("implementation hash mismatch; refusing to replay")

    with np.load(source, allow_pickle=False) as data:
        b0 = np.asarray(data["retained_operator"], dtype=np.float64)
        c0 = np.asarray(data["full_tail"], dtype=np.float64)
    epsilon = float(result["gram_error_bound"])
    eta = float(result["eta"])
    checks = []
    with np.load(arrays_path, allow_pickle=False) as saved:
        for variant, error in (("nominal", 0.0), ("robust", epsilon)):
            summary_key = "nominal" if variant == "nominal" else "error_inflated"
            summary = result["variants"][summary_key]
            scale = float(summary["operator_scale"])
            b = b0 / scale
            c = (c0 + c0.T) / (2 * scale**2) + (error / scale**2) * np.eye(c0.shape[0])
            margins = np.asarray(summary["margins"], dtype=np.float64)
            multipliers = np.asarray(summary["selected_multiplier_scaled"], dtype=np.float64)
            saved_margins = np.asarray(saved[f"{variant}_margins"], dtype=np.float64)
            saved_multipliers = np.asarray(saved[f"{variant}_multipliers_scaled"], dtype=np.float64)
            if margins.shape != (b.shape[1],) or multipliers.shape != margins.shape:
                raise SystemExit(f"{variant}: unexpected frontier dimensions")
            if not np.array_equal(margins, saved_margins) or not np.array_equal(multipliers, saved_multipliers):
                raise SystemExit(f"{variant}: JSON/NPZ summaries disagree")
            gram = b.T @ b
            replayed = 0
            worst_deficit = 0.0
            max_margin_error = 0.0
            for index, margin in enumerate(margins):
                rank = index + 1
                basis_key = f"{variant}_basis_{rank}"
                if margin <= 0:
                    if basis_key in saved.files:
                        raise SystemExit(f"{variant} rank {rank}: unexpected zero-margin basis")
                    continue
                if basis_key not in saved.files:
                    raise SystemExit(f"{variant} rank {rank}: missing selected basis")
                basis = np.asarray(saved[basis_key], dtype=np.float64)
                if basis.shape != (b.shape[1], rank) or not np.isfinite(basis).all():
                    raise SystemExit(f"{variant} rank {rank}: invalid basis")
                if not np.allclose(basis.T @ basis, np.eye(rank), rtol=1e-9, atol=1e-10):
                    raise SystemExit(f"{variant} rank {rank}: basis is not orthonormal")
                t = float(multipliers[index])
                h = t * (b.T @ np.linalg.solve(c + t*np.eye(c.shape[0]), b)) - t*eta**2*np.eye(b.shape[1])
                actual = generalized_minimum(basis.T @ h @ basis, basis.T @ gram @ basis)
                deficit = margin**2 - actual
                worst_deficit = max(worst_deficit, deficit)
                max_margin_error = max(max_margin_error, abs(np.sqrt(max(actual, 0.0)) - margin))
                tolerance = 2e-8 * max(1.0, margin**2)
                if deficit > tolerance:
                    raise SystemExit(f"{variant} rank {rank}: reported margin exceeds direct replay")
                replayed += 1
            if np.any(np.diff(margins) > 2e-10):
                raise SystemExit(f"{variant}: rank frontier is not nonincreasing")
            checks.append({
                "variant": variant,
                "positive_rank_bases_replayed": replayed,
                "worst_reported_squared_margin_minus_replay": worst_deficit,
                "maximum_margin_difference": max_margin_error,
            })
        if np.any(np.asarray(result["variants"]["error_inflated"]["margins"])
                  > np.asarray(result["variants"]["nominal"]["margins"]) + 2e-10):
            raise SystemExit("Gram-error inflation increased the frontier")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "PASS_DIRECT_MATRIX_REPLAY_MODEL_ONLY",
        "run": str(args.run.resolve()),
        "input_hashes_verified": True,
        "checks": checks,
        "claim_boundary": "Independent replay verifies finite-grid numerical certificates on saved model operators only; not neural source recovery, formal outward-rounded proof, or novelty.",
    }
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
