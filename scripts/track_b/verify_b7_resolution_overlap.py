"""Independently check B7 descriptive rank correlations with SciPy."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "outputs/track_b/20261024_b7_resolution_overlap_audit_v2"
REPORT = RUN / "b7_resolution_overlap_report.json"
TABLE = RUN / "paired_source_metrics.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    with TABLE.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    expected_n = int(report["source_count"])
    if len(rows) != expected_n or len({row["source_index"] for row in rows}) != expected_n:
        raise ValueError("paired table row count or source-index uniqueness check failed")
    metrics = sorted(report["spearman_correlations"])
    x = np.asarray([float(row["best_distant_abs_cosine"]) for row in rows])
    observed = {}
    for name in metrics:
        y = np.asarray([float(row[name]) for row in rows])
        observed[name] = float(spearmanr(x, y).statistic)
    discrepancies = {
        name: abs(observed[name] - float(report["spearman_correlations"][name]))
        for name in metrics
    }
    if any(value > 1e-12 for value in discrepancies.values()):
        raise ValueError(f"independent SciPy rank check exceeded tolerance: {discrepancies}")
    verification = {
        "status": "PASS_INDEPENDENT_RANK_STATISTIC_RECHECK",
        "source_count": expected_n,
        "implementation": "scipy.stats.spearmanr",
        "maximum_absolute_discrepancy": max(discrepancies.values(), default=0.0),
        "recomputed_spearman": observed,
        "report_spearman": report["spearman_correlations"],
        "input_sha256": {p.name: sha256(p) for p in (REPORT, TABLE)},
        "limitations": [
            "This rechecks descriptive calculations only; it does not add independent observations.",
            "No p-values or confidence intervals are interpreted because source vertices are spatially dependent.",
            "It does not establish researcher decision utility or physiological source validity.",
        ],
    }
    target = RUN / "independent_stat_check.json"
    target.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": verification["status"], "maximum_absolute_discrepancy": verification["maximum_absolute_discrepancy"]}, indent=2))


if __name__ == "__main__":
    main()
