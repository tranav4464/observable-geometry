"""Independently recompute simulator invariants from a saved feasibility run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--report", type=Path, help="Optional new output path for verification report")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    report = json.loads((run_dir / "feasibility_report.json").read_text(encoding="utf-8"))
    arrays_path = run_dir / report["arrays_file"]
    digest = hashlib.sha256(arrays_path.read_bytes()).hexdigest()
    if digest != report["arrays_sha256"]:
        raise SystemExit("array artifact hash mismatch")
    with np.load(arrays_path, allow_pickle=False) as data:
        adj = data["adjacency"]
        transition = data["transition"]
        x = data["latent"]
        lead = data["scalp_operator"]
        select = data["ieeg_operator"]
        scalp = data["scalp"]
        ieeg = data["ieeg"]
        eps_s = data["scalp_noise"]
        eps_i = data["ieeg_noise"]
        indices = data["ieeg_region_indices"]
        active = data["active_region_indices"]
    rho = float(np.max(np.abs(np.linalg.eigvals(transition))))
    snr_s = float(10 * np.log10(np.mean((x @ lead.T) ** 2) / np.mean(eps_s ** 2)))
    snr_i = float(10 * np.log10(np.mean((x @ select.T) ** 2) / np.mean(eps_i ** 2)))
    checks = {
        "hash_matches": digest == report["arrays_sha256"],
        "adjacency_is_binary_zero_diagonal": bool(np.isin(adj, [0, 1]).all() and np.all(np.diag(adj) == 0)),
        "transition_support_matches_graph": bool(np.array_equal(np.abs(transition) > 0, adj.astype(bool))),
        "configured_active_region_graph_matches": bool(
            len(active) == report["config"]["n_active_regions"]
            and int(adj.sum()) == report["config"]["max_indegree"] * len(active)
            and np.all(adj.sum(axis=1)[active] == report["config"]["max_indegree"])
            and np.all(np.delete(adj, active, axis=0) == 0)
            and np.all(np.delete(adj, active, axis=1) == 0)
        ),
        "transition_stable": bool(rho < 1),
        "reported_dimensions_match_arrays": bool(
            list(adj.shape) == report["shapes"]["adjacency"]
            and list(scalp.shape) == report["shapes"]["scalp"]
            and list(ieeg.shape) == report["shapes"]["ieeg"]
        ),
        "iEEG_selection_matches_saved_indices": bool(
            np.all(select.sum(axis=0) <= 1) and int(select.sum()) == len(indices)
            and np.array_equal(np.argmax(select, axis=1), indices)
        ),
        "observations_reconstruct_from_saved_components": bool(
            np.allclose(scalp, x @ lead.T + eps_s)
            and np.allclose(ieeg, x @ select.T + eps_i)
        ),
        "scalp_snr_matches_report": bool(abs(snr_s - report["realized_snr_db"][0]) < 1e-9),
        "ieeg_snr_matches_report": bool(abs(snr_i - report["realized_snr_db"][1]) < 1e-9),
        "no_participant_data_used": report["participant_data_used"] is False,
        "no_confirmatory_outcomes_used": report["confirmatory_outcomes_used"] is False,
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
              "transition_spectral_radius_recomputed": rho,
              "realized_snr_db_recomputed": [snr_s, snr_i],
              "edge_count_recomputed": int(adj.sum()), "arrays_sha256_recomputed": digest}
    print(json.dumps(result, indent=2))
    if args.report:
        report_path = args.report.resolve()
        if report_path.exists():
            raise SystemExit(f"Refusing to overwrite existing verification report: {report_path}")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
