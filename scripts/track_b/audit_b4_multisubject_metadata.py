"""Inventory Localize-MI stimulation metadata without opening EEG samples.

This is a feasibility audit only. It reads BIDS channel and epoch TSV files
plus a saved participant-geometry report; it never loads an EEG array.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from statistics import median
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data/Localize-MI/derivatives/epochs"
DEFAULT_GEOMETRY = ROOT / "outputs/track_b/data_acquisition/geometry_sub-01_02_03_04_05_06_07.json"
DEFAULT_OUT = ROOT / "outputs/track_b/data_acquisition/b4_multisubject_metadata_feasibility.json"
SUBJECTS = tuple(f"sub-{i:02d}" for i in range(1, 8))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def path_key(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def audit(data_root: Path, geometry_path: Path) -> dict[str, Any]:
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    geom_by_subject = {item["participant"]: item for item in geometry["participants"]}
    if set(geom_by_subject) != set(SUBJECTS):
        raise ValueError("geometry report does not contain exactly sub-01 through sub-07")

    participants: dict[str, Any] = {}
    input_hashes: dict[str, str] = {path_key(geometry_path): sha256(geometry_path)}
    total_runs = total_rows = total_pairs = total_conditions = repeated_conditions = 0
    for subject in SUBJECTS:
        eeg_root = data_root / subject / "eeg"
        channel_files = sorted(eeg_root.glob(f"{subject}_task-seegstim_run-*_channels.tsv"))
        epoch_files = sorted(eeg_root.glob(f"{subject}_task-seegstim_run-*_epochs.tsv"))
        by_run_channels: dict[str, set[str]] = {}
        by_run_counts: dict[str, int] = {}
        for path in channel_files:
            match = re.search(r"run-(\d+)", path.name)
            if match is None:
                raise ValueError(f"cannot parse run id from {path}")
            run = match.group(1)
            input_hashes[path_key(path)] = sha256(path)
            rows = read_tsv(path)
            eeg = [row for row in rows if row.get("type", "").upper() == "EEG"]
            if not eeg:
                raise ValueError(f"no EEG channel rows in {path}")
            by_run_channels[run] = {row["name"] for row in eeg if row.get("status", "").lower() == "good"}
            by_run_counts[run] = len(by_run_channels[run])

        site_runs: dict[str, list[str]] = {}
        site_conditions: dict[str, dict[str, dict[str, int]]] = {}
        run_trials: dict[str, int] = {}
        intensity_values: set[str] = set()
        for path in epoch_files:
            match = re.search(r"run-(\d+)", path.name)
            if match is None:
                raise ValueError(f"cannot parse run id from {path}")
            run = match.group(1)
            input_hashes[path_key(path)] = sha256(path)
            rows = read_tsv(path)
            labels = {row.get("trial_type", "").strip() for row in rows}
            labels.discard("")
            if len(labels) != 1:
                raise ValueError(f"expected one stimulation condition in {path}, found {len(labels)}")
            label = next(iter(labels))
            site_label, intensity = label.rsplit(" ", 1)
            site_runs.setdefault(site_label, []).append(run)
            site_conditions.setdefault(site_label, {}).setdefault(intensity, {})[run] = len(rows)
            intensity_values.add(intensity)
            run_trials[run] = len(rows)

        if set(by_run_channels) != set(run_trials):
            raise ValueError(f"channel and epoch run ids differ for {subject}")
        geometry_sites = {tuple(pair["contacts"]) for pair in geom_by_subject[subject]["contact_pairs"]}
        observed_sites: set[tuple[str, str]] = set()
        for label in site_runs:
            first, second_number = label.split("-", 1)
            prefix = "".join(character for character in first if not character.isdigit())
            observed_sites.add((first, prefix + second_number))
        if observed_sites != geometry_sites:
            raise ValueError(f"epoch and coordinate contact-pair sets differ for {subject}")

        geometry_pairs = geom_by_subject[subject]["source_proxy_pairwise_separation"]["pairs"]
        eligible_geometry_pairs = {
            frozenset((tuple(item["contacts_a"]), tuple(item["contacts_b"])))
            for item in geometry_pairs if item["eligible_at_20mm"]
        }
        multi_intensity_pairs = {
            frozenset((_contacts_for_site_label(left), _contacts_for_site_label(right)))
            for left, right in _multi_intensity_site_label_pairs(site_conditions)
        }

        common_good = set.intersection(*by_run_channels.values())
        union_good = set.union(*by_run_channels.values())
        geom = geom_by_subject[subject]
        rows_n = sum(run_trials.values())
        participant = {
            "run_count": len(run_trials),
            "epoch_metadata_row_count": rows_n,
            "unique_stimulation_contact_pairs": len(site_runs),
            "site_intensity_condition_count": sum(len(items) for items in site_conditions.values()),
            "site_intensity_conditions_with_multiple_runs": sum(
                1 for items in site_conditions.values() for runs in items.values() if len(runs) > 1
            ),
            "stimulation_intensities": sorted(intensity_values),
            "site_condition_run_counts": {
                site: {
                    intensity: {
                        "run_count": len(runs),
                        "trial_metadata_rows_by_run": dict(sorted(runs.items())),
                        "total_trial_metadata_rows": sum(runs.values()),
                    }
                    for intensity, runs in sorted(conditions.items())
                }
                for site, conditions in sorted(site_conditions.items())
            },
            "site_pair_same_intensity_opportunities": _same_intensity_pair_summary(site_conditions),
            "cross_intensity_geometry_eligible_site_pair_count": len(
                eligible_geometry_pairs & multi_intensity_pairs
            ),
            "cross_intensity_geometry_eligible_site_pairs": [
                [list(site) for site in sorted(pair)]
                for pair in sorted(eligible_geometry_pairs & multi_intensity_pairs, key=lambda p: sorted(p))
            ],
            "good_eeg_channel_count_by_run": by_run_counts,
            "good_eeg_channels_common_to_all_runs": len(common_good),
            "good_eeg_channels_union_across_runs": len(union_good),
            "forward_source_count": geom["n_forward_sources"],
            "contact_pair_coordinate_count": geom["n_contact_pairs"],
            "maximum_sensor_coordinate_mismatch_mm": geom["sensor_position_error_mm"]["max"],
            "nearest_cortical_vertex_offset_max_mm": geom["midpoint_offset_mm"]["max"],
            "geometry_source_proxy_pairwise_separation": geom["source_proxy_pairwise_separation"],
            "site_runs": {site: sorted(runs) for site, runs in sorted(site_runs.items())},
        }
        participants[subject] = participant
        total_runs += participant["run_count"]
        total_rows += rows_n
        total_pairs += len(site_runs)
        total_conditions += participant["site_intensity_condition_count"]
        repeated_conditions += participant["site_intensity_conditions_with_multiple_runs"]

    return {
        "status": "PASS_METADATA_FEASIBILITY_ONLY",
        "audit_type": "Localize-MI multi-participant pre-outcome metadata feasibility",
        "data_access": {
            "EEG_or_iEEG_sample_arrays_opened": False,
            "signal_values_read": False,
            "participant_signal_outcomes_read": False,
            "files_read": "BIDS channel TSVs, epoch condition TSVs, and saved geometry audit JSON only",
        },
        "aggregate": {
            "participants": len(participants),
            "recording_runs": total_runs,
            "epoch_metadata_rows": total_rows,
            "unique_contact_pairs": total_pairs,
            "site_intensity_conditions": total_conditions,
            "site_intensity_conditions_with_multiple_runs": repeated_conditions,
            "participant_cluster_count": len(participants),
            "median_common_good_eeg_channels": median(
                item["good_eeg_channels_common_to_all_runs"] for item in participants.values()
            ),
        },
        "participants_detail": participants,
        "input_sha256": dict(sorted(input_hashes.items())),
        "interpretation_limits": [
            "Metadata availability does not establish signal quality or empirical prediction performance.",
            "Stimulation artifacts are known-location electrical probes, not endogenous neural source ground truth.",
            "The audit does not authorize opening signal arrays or running a confirmatory analysis.",
            "Seven participants are a small independent-cluster count; pair rows must not be treated as independent subjects.",
        ],
    }


def _same_intensity_pair_summary(
    site_conditions: dict[str, dict[str, dict[str, int]]],
) -> dict[str, Any]:
    """Count candidate site comparisons sharing intensity, without reading signals."""
    sites = sorted(site_conditions)
    comparisons: list[dict[str, Any]] = []
    for left_index, left in enumerate(sites):
        for right in sites[left_index + 1 :]:
            shared = sorted(set(site_conditions[left]) & set(site_conditions[right]))
            for intensity in shared:
                left_runs = site_conditions[left][intensity]
                right_runs = site_conditions[right][intensity]
                comparisons.append(
                    {
                        "site_a": left,
                        "site_b": right,
                        "intensity": intensity,
                        "site_a_runs": len(left_runs),
                        "site_b_runs": len(right_runs),
                        "site_a_min_trials_per_run": min(left_runs.values()),
                        "site_b_min_trials_per_run": min(right_runs.values()),
                        "site_a_total_trials": sum(left_runs.values()),
                        "site_b_total_trials": sum(right_runs.values()),
                    }
                )
    return {
        "same_intensity_site_pair_condition_count": len(comparisons),
        "site_pairs_with_two_or_more_shared_intensities": len(_multi_intensity_site_label_pairs(site_conditions)),
        "source_site_pairs_with_shared_multiple_intensities": [
            {
                "site_a": left,
                "site_b": right,
                "shared_intensities": sorted(set(site_conditions[left]) & set(site_conditions[right])),
            }
            for left, right in _multi_intensity_site_label_pairs(site_conditions)
        ],
        "comparisons": comparisons,
        "interpretation": (
            "Counts describe metadata opportunities only. They do not authorize signal access, "
            "establish independent run replication, or validate a classifier protocol."
        ),
    }


def _multi_intensity_site_label_pairs(
    site_conditions: dict[str, dict[str, dict[str, int]]],
) -> list[tuple[str, str]]:
    sites = sorted(site_conditions)
    return [
        (left, right)
        for left_index, left in enumerate(sites)
        for right in sites[left_index + 1 :]
        if len(set(site_conditions[left]) & set(site_conditions[right])) >= 2
    ]


def _contacts_for_site_label(site_label: str) -> tuple[str, str]:
    first, second_number = site_label.split("-", 1)
    prefix = "".join(character for character in first if not character.isdigit())
    return tuple(sorted((first, prefix + second_number)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--geometry-report", type=Path, default=DEFAULT_GEOMETRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = audit(args.data_root.resolve(), args.geometry_report.resolve())
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "aggregate": report["aggregate"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
