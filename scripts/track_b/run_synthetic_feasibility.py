"""Run a labeled Track B synthetic feasibility check; never overwrites output."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from observable_geometry.track_b.synthetic import SyntheticConfig, generate_synthetic


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, help="New, unused output directory")
    parser.add_argument("--seed", type=int, default=20261022)
    args = parser.parse_args()
    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {out_dir}")

    config = SyntheticConfig(seed=args.seed)
    result = generate_synthetic(config)
    spectral_radius = float(np.max(np.abs(np.linalg.eigvals(result.transition))))
    if not np.isfinite(spectral_radius) or spectral_radius >= 1:
        raise SystemExit("Generated transition matrix is not stable")
    if not np.allclose(result.realized_snr_db,
                       (config.scalp_snr_db, config.ieeg_snr_db), atol=1e-10):
        raise SystemExit("Realized observation SNR does not match the config")

    out_dir.mkdir(parents=True, exist_ok=False)
    arrays_path = out_dir / "synthetic_feasibility.npz"
    np.savez_compressed(
        arrays_path,
        adjacency=result.adjacency,
        transition=result.transition,
        latent=result.latent,
        scalp_operator=result.scalp_operator,
        ieeg_operator=result.ieeg_operator,
        scalp=result.scalp,
        ieeg=result.ieeg,
        scalp_noise=result.scalp_noise,
        ieeg_noise=result.ieeg_noise,
        active_region_indices=result.active_region_indices,
        ieeg_region_indices=result.ieeg_region_indices,
    )
    digest = hashlib.sha256(arrays_path.read_bytes()).hexdigest()
    report = {
        "run_role": "development_feasibility_only",
        "generator_scope": "explicit first-order VAR simulator with abstract random linear scalp mixing; not a physical lead field or exact author-generator reproduction",
        "config": asdict(config),
        "shapes": {
            "adjacency": list(result.adjacency.shape),
            "transition": list(result.transition.shape),
            "latent": list(result.latent.shape),
            "scalp_operator": list(result.scalp_operator.shape),
            "ieeg_operator": list(result.ieeg_operator.shape),
            "scalp": list(result.scalp.shape),
            "ieeg": list(result.ieeg.shape),
        },
        "edge_count": int(result.adjacency.sum()),
        "directed_edge_convention": "adjacency[target, source]; x[t] = transition @ x[t-1] + innovation[t]",
        "active_region_count": int(len(result.active_region_indices)),
        "active_region_indices": result.active_region_indices.tolist(),
        "ieeg_coverage_fraction": config.n_ieeg_regions / config.n_regions,
        "transition_spectral_radius": spectral_radius,
        "requested_snr_db": [config.scalp_snr_db, config.ieeg_snr_db],
        "realized_snr_db": list(result.realized_snr_db),
        "arrays_file": arrays_path.name,
        "arrays_sha256": digest,
        "participant_data_used": False,
        "confirmatory_outcomes_used": False,
    }
    report_path = out_dir / "feasibility_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
