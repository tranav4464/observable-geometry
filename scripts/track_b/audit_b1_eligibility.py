"""Build a metadata-only feasibility screen for matched-current site groups.

Reads validated contract JSON and TSV metadata only. It never opens EEG arrays,
computes signals, or inspects any test-participant outcome.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "outputs" / "track_b" / "data_acquisition" / "contract_sub-02_03_04_05_06_07.json"
META = ROOT / "data" / "Localize-MI" / "derivatives" / "epochs"
OUTPUT = ROOT / "outputs" / "track_b" / "data_acquisition" / "eligibility_sub-02_03_04_05_06_07.json"
CONDITION = re.compile(r"(.+) ([0-9]+(?:\.[0-9]+)?mA)")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite eligibility artifact: {args.output}")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if contract.get("status") != "PASS":
        raise ValueError("The preceding metadata/header contract has not passed")

    participants = []
    for participant in contract["participants"]:
        subject = participant["participant"]
        if participant.get("scope") != "metadata and array headers only; no EEG values or outcomes read":
            raise ValueError(f"Unexpected scope for {subject}")
        groups: dict[str, dict[str, int]] = {}
        good_sets = []
        run_records = []
        for run in participant["runs"]:
            match = CONDITION.fullmatch(run["condition"])
            if match is None:
                raise ValueError(f"Cannot parse contact pair/current: {run['condition']}")
            pair, current = match.groups()
            groups.setdefault(current, {})
            if pair in groups[current]:
                raise ValueError(f"Duplicate contact-pair/current run needs explicit aggregation: {subject} {run['condition']}")
            groups[current][pair] = int(run["trials"])

            stem = Path(run["run_file"]).stem.removesuffix("_epochs")
            channel_path = META / subject / "eeg" / f"{stem}_channels.tsv"
            channel_rows = read_tsv(channel_path)
            good = {row["name"] for row in channel_rows
                    if row.get("status") == "good" and row.get("type") == "EEG"}
            if len(good) != run["good_channels"]:
                raise ValueError(f"Good-channel count mismatch in {channel_path}")
            event_path = META / subject / "eeg" / f"{stem}_epochs.tsv"
            event_rows = read_tsv(event_path)
            if len(event_rows) != run["trials"]:
                raise ValueError(f"Trial count mismatch in {event_path}")
            if {row["trial_type"] for row in event_rows} != {run["condition"]}:
                raise ValueError(f"Condition metadata mismatch in {event_path}")
            good_sets.append(good)
            run_records.append({"run": run["run_file"], "condition": run["condition"],
                                "trials": run["trials"], "good_channels": len(good)})

        common_good = set.intersection(*good_sets) if good_sets else set()
        current_groups = []
        for current, sites in sorted(groups.items(), key=lambda item: float(item[0][:-2])):
            n_sites = len(sites)
            current_groups.append({
                "current": current,
                "site_pairs": [{"contact_pair": pair, "trials": trials}
                               for pair, trials in sorted(sites.items())],
                "n_sites": n_sites,
                "candidate_dependent_pairs": n_sites * (n_sites - 1) // 2,
                "minimum_trials_per_site": min(sites.values()) if sites else 0,
                "maximum_trials_per_site": max(sites.values()) if sites else 0,
            })
        participants.append({
            "participant": subject,
            "scope": "metadata only; no EEG values or outcome scores read",
            "n_runs": len(run_records),
            "common_good_eeg_channels_across_runs": len(common_good),
            "largest_group_size": max((group["n_sites"] for group in current_groups), default=0),
            "same_current_groups": current_groups,
            "runs": run_records,
        })

    # Sensitivity counts only: these thresholds describe design feasibility;
    # they do not constitute a frozen inferential eligibility rule.
    threshold_grid = []
    for minimum_sites in (2, 3, 4):
        for minimum_trials in (10, 20, 30):
            eligible = [p["participant"] for p in participants
                        if any(g["n_sites"] >= minimum_sites and
                               g["minimum_trials_per_site"] >= minimum_trials
                               for g in p["same_current_groups"])]
            threshold_grid.append({"minimum_sites": minimum_sites,
                                   "minimum_trials_per_site": minimum_trials,
                                   "participants_meeting_metadata_threshold": eligible,
                                   "count": len(eligible)})

    report = {
        "status": "PASS_METADATA_ONLY_FEASIBILITY_SCREEN",
        "purpose": "B1 eligibility description; not outcome inspection or confirmatory eligibility freeze",
        "contract_input": str(CONTRACT.relative_to(ROOT)),
        "participant_count": len(participants),
        "no_eeg_values_read": True,
        "no_pair_confusion_or_signal_scores_computed": True,
        "participants": participants,
        "threshold_sensitivity_grid": threshold_grid,
        "limitations": [
            "Matched-current site pairs are dependent because many pairs share a site.",
            "Each condition is represented by one acquisition run in this screen; trial splits do not provide independent run replication.",
            "The threshold grid is descriptive and must not be retrofitted into confirmatory eligibility after outcome access.",
            "Metadata feasibility does not establish signal quality, physical forward-model adequacy, or sufficient statistical power.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "participants": len(participants),
                      "output": str(args.output),
                      "common_good_channel_counts": {p["participant"]: p["common_good_eeg_channels_across_runs"]
                                                      for p in participants}}, indent=2))


if __name__ == "__main__":
    main()
