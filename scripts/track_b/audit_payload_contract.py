"""Audit Localize-MI participant file contracts without reading EEG sample values.

This gate checks acquisition integrity, headers, channel order and event metadata.
It deliberately does not compute evoked responses, pair confusion or source scores.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

import mne
import numpy as np

from fetch_localize import META, PAYLOAD, ROOT, digest_file, expected_files, parse_pointer


def table(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def audit_subject(subject: str) -> dict:
    paths = expected_files(subject, "both")
    verified = []
    for relative in paths:
        target = PAYLOAD / relative
        size, md5 = parse_pointer(relative)
        if not target.is_file() or target.stat().st_size != size or digest_file(target) != md5:
            raise ValueError(f"Missing or invalid payload: {relative}")
        verified.append({"path": relative.as_posix(), "bytes": size, "dataset_md5": md5})

    forward_path = PAYLOAD / paths[0]
    forward = mne.read_forward_solution(forward_path, verbose="ERROR")
    channel_names = list(forward["info"]["ch_names"])
    if len(channel_names) != forward["nchan"] or len(set(channel_names)) != len(channel_names):
        raise ValueError(f"Forward channel identity problem for sub-{subject}")

    run_rows = []
    for relative in paths[1:]:
        prefix = (META / relative).with_name(relative.stem.removesuffix("_epochs"))
        events = table(Path(str(prefix) + "_epochs.tsv"))
        channels = table(Path(str(prefix) + "_channels.tsv"))
        sidecar = json.loads(Path(str(prefix) + "_epochs.json").read_text(encoding="utf-8"))
        array = np.load(PAYLOAD / relative, mmap_mode="r", allow_pickle=False)
        if array.ndim != 3 or array.dtype != np.float64:
            raise ValueError(f"Unexpected EEG array header: {relative}: {array.shape}, {array.dtype}")
        if len(events) != array.shape[0] or len(channels) != array.shape[1]:
            raise ValueError(f"Epoch/channel metadata count disagrees with array: {relative}")
        if [row["name"] for row in channels] != channel_names:
            raise ValueError(f"Channel order differs from forward: {relative}")
        if {row["units"] for row in channels} != {"V"} or {
            float(row["sampling_frequency"]) for row in channels
        } != {8000.0}:
            raise ValueError(f"EEG voltage or sampling-rate contract differs: {relative}")
        if not sidecar.get("BaselineCorrection"):
            raise ValueError(f"Baseline correction metadata missing: {relative}")
        zero_times = {float(row["zero_time"]) for row in events}
        trial_types = Counter(row["trial_type"] for row in events)
        if zero_times != {0.25} or len(trial_types) != 1:
            raise ValueError(f"Unexpected event timing or mixed stimulation condition: {relative}")
        run_rows.append({"run_file": relative.name, "trials": array.shape[0],
                         "channels": array.shape[1], "samples": array.shape[2],
                         "dtype": str(array.dtype), "condition": next(iter(trial_types)),
                         "good_channels": sum(row["status"] == "good" for row in channels)})
        del array

    return {"participant": f"sub-{subject}", "scope": "metadata and array headers only; no EEG values or outcomes read",
            "forward": {"channels": forward["nchan"], "sources": forward["nsource"],
                        "orientation": str(forward["source_ori"]),
                        "leadfield_shape": list(forward["sol"]["data"].shape)},
            "runs": run_rows, "total_trials": sum(row["trials"] for row in run_rows),
            "payloads": verified}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", nargs="+", choices=[f"{i:02d}" for i in range(1, 8)], required=True)
    args = parser.parse_args()
    reports = [audit_subject(subject) for subject in args.subjects]
    report = {"status": "PASS", "kind": "B1 metadata/header contract only; no outcome inspection",
              "participants": reports}
    out = ROOT / "outputs" / "track_b" / "data_acquisition"
    out.mkdir(parents=True, exist_ok=True)
    name = "contract_sub-" + "_".join(args.subjects) + ".json"
    (out / name).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "participants": [r["participant"] for r in reports],
                      "runs": sum(len(r["runs"]) for r in reports),
                      "trials": sum(r["total_trials"] for r in reports),
                      "report": str(out / name)}, indent=2))


if __name__ == "__main__":
    main()
