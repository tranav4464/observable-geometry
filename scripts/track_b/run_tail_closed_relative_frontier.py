"""Run the optional per-field relative tail-closed frontier on model Grams only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from observable_geometry.track_b.tail_closed import tail_closed_relative_margin_frontier


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize(frontier, thresholds: tuple[float, ...]) -> dict:
    margins = frontier.normalized_lower_margin
    return {
        "effective_rank": frontier.effective_rank,
        "operator_scale": frontier.operator_scale,
        "grid_size": frontier.multiplier_grid_size,
        "margins": margins.tolist(),
        "selected_multiplier_scaled": frontier.selected_multiplier_scaled.tolist(),
        "threshold_rank_counts": {
            format(value, ".6g"): int(np.count_nonzero(margins > value))
            for value in thresholds
        },
        "claim_boundary": frontier.claim_boundary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operator-grams", type=Path, required=True)
    parser.add_argument("--reference-result", type=Path, required=True,
                        help="Existing tail-closed result.json, used only for its declared Gram-error bound.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--grid-size", type=int, default=2049)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit(f"refusing to overwrite existing output: {args.out}")
    if not args.operator_grams.is_file() or not args.reference_result.is_file():
        raise SystemExit("input artifact is missing")

    with np.load(args.operator_grams, allow_pickle=False) as data:
        b = np.asarray(data["retained_operator"], dtype=np.float64)
        c = np.asarray(data["full_tail"], dtype=np.float64)
    reference = json.loads(args.reference_result.read_text(encoding="utf-8"))
    epsilon = float(reference["gram_error_bound"])
    root = Path(__file__).resolve().parents[2]
    source_files = {
        "tail_closed_module": root / "src" / "observable_geometry" / "track_b" / "tail_closed.py",
        "runner": Path(__file__).resolve(),
        "independent_verifier": root / "scripts" / "track_b" / "verify_tail_closed_relative_frontier.py",
    }
    if not all(path.is_file() for path in source_files.values()):
        raise SystemExit("one or more implementation files needed for provenance are missing")
    nominal = tail_closed_relative_margin_frontier(b, c, grid_size=args.grid_size)
    robust = tail_closed_relative_margin_frontier(
        b, c, gram_error_bound=epsilon, grid_size=args.grid_size
    )
    thresholds = (0.01, 0.02, 0.05, 0.10)

    args.out.mkdir(parents=True)
    arrays: dict[str, np.ndarray] = {}
    for name, frontier in (("nominal", nominal), ("robust", robust)):
        arrays[f"{name}_margins"] = frontier.normalized_lower_margin
        arrays[f"{name}_multipliers_scaled"] = frontier.selected_multiplier_scaled
        for rank, basis in enumerate(frontier.selected_basis_by_rank, start=1):
            if basis is not None:
                arrays[f"{name}_basis_{rank}"] = basis
    np.savez_compressed(args.out / "frontier.npz", **arrays)

    result = {
        "status": "MODEL_ONLY_RELATIVE_FRONTIER_COMPUTED",
        "method": "finite logarithmic grid over generalized eigenvalues relative to B.T @ B",
        "estimand": "maximum feasible relative residual margin delta for rank-k retained subspaces, under ||z|| <= eta*||c||",
        "eta": 1.0,
        "gram_error_bound": epsilon,
        "inputs": {
            "operator_grams": str(args.operator_grams.resolve()),
            "operator_grams_sha256": sha256(args.operator_grams),
            "reference_result": str(args.reference_result.resolve()),
            "reference_result_sha256": sha256(args.reference_result),
        },
        "code_sha256": {key: sha256(path) for key, path in source_files.items()},
        "variants": {
            "nominal": summarize(nominal, thresholds),
            "error_inflated": summarize(robust, thresholds),
        },
        "thresholds": list(thresholds),
        "limitations": [
            "Uses only saved finite-mesh forward-model Gram artifacts; no EEG or SEEG samples or outcomes were read.",
            "Finite-grid values are numerical lower-bound candidates, not continuous-multiplier optima or outward-rounded formal certificates.",
            "The relative margin is conditional on the declared source coefficient norm, tail Gram, and one-sided Gram-error inflation.",
            "This is an established generalized-eigenvalue normalization of the existing S-lemma bound, not a novel method claim.",
            "Threshold rank counts are descriptive and not calibrated detectability or researcher utility.",
            "No physiological source recovery, source-prior validation, participant generality, or neural-data result is established.",
        ],
    }
    (args.out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "output": str(args.out.resolve()),
        "robust_threshold_rank_counts": robust_summary if (robust_summary := result["variants"]["error_inflated"]["threshold_rank_counts"]) else {},
    }, indent=2))


if __name__ == "__main__":
    main()
