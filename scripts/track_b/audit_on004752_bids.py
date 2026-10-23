"""Audit paired on004752 EDF headers and BIDS sidecars without reading signal samples."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path

import mne


TASK_FIELDS = ("nTrial", "SetSize", "ProbeLetter", "Match", "Correct", "ResponseTime", "Artifact", "duration")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def audit_one(eeg_json: Path) -> dict:
    base = eeg_json.name.removesuffix("_eeg.json")
    eeg_dir = eeg_json.parent
    session_dir = eeg_dir.parent
    ieeg_dir = session_dir / "ieeg"
    paths = {
        "eeg_edf": eeg_dir / f"{base}_eeg.edf",
        "ieeg_json": ieeg_dir / f"{base}_ieeg.json",
        "ieeg_edf": ieeg_dir / f"{base}_ieeg.edf",
        "eeg_channels": eeg_dir / f"{base}_channels.tsv",
        "ieeg_channels": ieeg_dir / f"{base}_channels.tsv",
        "eeg_events": eeg_dir / f"{base}_events.tsv",
        "ieeg_events": ieeg_dir / f"{base}_events.tsv",
    }
    missing = [key for key, path in paths.items() if not path.is_file()]
    if missing:
        return {"subject": session_dir.parent.name, "session": session_dir.name,
                "status": "INCOMPLETE", "missing": missing}

    eeg_meta = json.loads(eeg_json.read_text(encoding="utf-8-sig"))
    ieeg_meta = json.loads(paths["ieeg_json"].read_text(encoding="utf-8-sig"))
    eeg_channels = read_tsv(paths["eeg_channels"])
    ieeg_channels = read_tsv(paths["ieeg_channels"])
    eeg_events = read_tsv(paths["eeg_events"])
    ieeg_events = read_tsv(paths["ieeg_events"])

    # preload=False reads the EDF header and metadata only. No signal samples are loaded.
    eeg_raw = mne.io.read_raw_edf(paths["eeg_edf"], preload=False, verbose="ERROR")
    ieeg_raw = mne.io.read_raw_edf(paths["ieeg_edf"], preload=False, verbose="ERROR")
    try:
        fs_eeg = float(eeg_meta["SamplingFrequency"])
        fs_ieeg = float(ieeg_meta["SamplingFrequency"])
        errors: list[str] = []
        if abs(float(eeg_raw.info["sfreq"]) - fs_eeg) > 1e-9:
            errors.append("EEG sidecar sampling rate differs from EDF header")
        if abs(float(ieeg_raw.info["sfreq"]) - fs_ieeg) > 1e-9:
            errors.append("iEEG sidecar sampling rate differs from EDF header")
        if len(eeg_channels) != len(eeg_raw.ch_names):
            errors.append("EEG channel-table row count differs from EDF channel count")
        if len(ieeg_channels) != len(ieeg_raw.ch_names):
            errors.append("iEEG channel-table row count differs from EDF channel count")
        if len(eeg_events) != len(ieeg_events):
            errors.append("paired modality event-row counts differ")
        paired_fields = all(
            all(eeg_events[i].get(field) == ieeg_events[i].get(field) for field in TASK_FIELDS)
            for i in range(min(len(eeg_events), len(ieeg_events)))
        )
        if not paired_fields:
            errors.append("paired trial/task fields differ between EEG and iEEG events")
        event_bounds_ok = True
        onset_scaling_ok = True
        duration_scaling_ok = True
        onset_differences: list[float] = []
        for rows, fs, n_times, modality in (
            (eeg_events, fs_eeg, eeg_raw.n_times, "EEG"),
            (ieeg_events, fs_ieeg, ieeg_raw.n_times, "iEEG"),
        ):
            for row in rows:
                beg, end = int(row["begSample"]), int(row["endSample"])
                onset, duration = float(row["onset"]), float(row["duration"])
                if beg < 1 or end < beg or end > n_times:
                    event_bounds_ok = False
                    errors.append(f"{modality} event sample bounds outside EDF recording")
                    break
                if abs(onset - beg / fs) > max(1e-9, 0.51 / fs):
                    onset_scaling_ok = False
                expected_duration = (end - beg + 1) / fs
                if abs(duration - expected_duration) > max(1e-9, 0.51 / fs):
                    duration_scaling_ok = False
            if rows and len(rows) and modality == "EEG" and len(rows) == len(ieeg_events):
                onset_differences = [float(a["onset"]) - float(b["onset"])
                                     for a, b in zip(eeg_events, ieeg_events)]
        if not event_bounds_ok:
            pass
        if not onset_scaling_ok:
            errors.append("event onset does not follow the modality sample-index convention")
        if not duration_scaling_ok:
            errors.append("event duration does not match inclusive sample bounds")
        return {
            "subject": session_dir.parent.name,
            "session": session_dir.name,
            "status": "PASS" if not errors else "FAIL",
            "eeg_sfreq_hz": fs_eeg,
            "ieeg_sfreq_hz": fs_ieeg,
            "eeg_channels": len(eeg_raw.ch_names),
            "ieeg_channels": len(ieeg_raw.ch_names),
            "eeg_samples": int(eeg_raw.n_times),
            "ieeg_samples": int(ieeg_raw.n_times),
            "eeg_duration_s": float(eeg_raw.n_times / fs_eeg),
            "ieeg_duration_s": float(ieeg_raw.n_times / fs_ieeg),
            "eeg_trials": len(eeg_events),
            "ieeg_trials": len(ieeg_events),
            "task_fields_match": paired_fields,
            "event_bounds_within_recordings": event_bounds_ok,
            "onset_matches_modality_sample_grid": onset_scaling_ok,
            "duration_matches_inclusive_sample_bounds": duration_scaling_ok,
            "eeg_ieeg_onset_delta_first_s": onset_differences[0] if onset_differences else None,
            "artifact_marked_trials": sum(row.get("Artifact") == "1" for row in eeg_events),
            "signal_samples_loaded": False,
            "errors": errors,
        }
    finally:
        eeg_raw.close()
        ieeg_raw.close()


def audit_header_only(eeg_json: Path) -> dict:
    """Check modality headers/sidecars without opening event-table rows."""
    base = eeg_json.name.removesuffix("_eeg.json")
    eeg_dir = eeg_json.parent
    session_dir = eeg_dir.parent
    ieeg_dir = session_dir / "ieeg"
    paths = {
        "eeg_edf": eeg_dir / f"{base}_eeg.edf",
        "ieeg_json": ieeg_dir / f"{base}_ieeg.json",
        "ieeg_edf": ieeg_dir / f"{base}_ieeg.edf",
        "eeg_channels": eeg_dir / f"{base}_channels.tsv",
        "ieeg_channels": ieeg_dir / f"{base}_channels.tsv",
        "eeg_events_file": eeg_dir / f"{base}_events.tsv",
        "ieeg_events_file": ieeg_dir / f"{base}_events.tsv",
    }
    missing = [key for key, path in paths.items() if not path.is_file()]
    if missing:
        return {"subject": session_dir.parent.name, "session": session_dir.name,
                "status": "INCOMPLETE", "missing": missing,
                "event_rows_read": False, "signal_samples_loaded": False}
    eeg_meta = json.loads(eeg_json.read_text(encoding="utf-8-sig"))
    ieeg_meta = json.loads(paths["ieeg_json"].read_text(encoding="utf-8-sig"))
    eeg_channels = read_tsv(paths["eeg_channels"])
    ieeg_channels = read_tsv(paths["ieeg_channels"])
    def parse_header(path: Path) -> dict:
        # Read only the EDF fixed header and per-channel header, never the data records.
        with path.open("rb") as stream:
            fixed = stream.read(256)
            if len(fixed) != 256:
                raise ValueError("EDF fixed header is truncated")
            def field(start: int, width: int) -> str:
                return fixed[start:start + width].decode("ascii", errors="strict").strip()
            date_text, time_text = field(168, 8), field(176, 8)
            header_bytes = int(field(184, 8))
            record_count = int(field(236, 8))
            record_seconds = float(field(244, 8))
            n_signals = int(field(252, 4))
            if n_signals < 1 or header_bytes < 256 + 256 * n_signals:
                raise ValueError("EDF per-channel header is inconsistent")
            variable = stream.read(header_bytes - 256)
            if len(variable) != header_bytes - 256:
                raise ValueError("EDF per-channel header is truncated")
            widths = (16, 80, 8, 8, 8, 8, 8, 80, 8, 32)
            values = []
            pos = 0
            for width in widths:
                values.append([variable[pos + i * width:pos + (i + 1) * width]
                               .decode("ascii", errors="strict").strip()
                               for i in range(n_signals)])
                pos += width * n_signals
            samples_per_record = [int(value) for value in values[8]]
            channel_rates = [sample_count / record_seconds for sample_count in samples_per_record]
            expected_bytes = header_bytes + record_count * sum(samples_per_record) * 2
            file_bytes = path.stat().st_size
            time_valid = True
            try:
                datetime.strptime(date_text + time_text, "%d.%m.%y%H.%M.%S")
            except ValueError:
                time_valid = False
            return {
                "date": date_text, "time": time_text, "time_valid": time_valid,
                "channels": n_signals, "records": record_count,
                "record_seconds": record_seconds, "channel_rates": channel_rates,
                "samples": record_count * samples_per_record[0],
                "size_matches_header": file_bytes == expected_bytes,
            }

    eeg_header = parse_header(paths["eeg_edf"])
    ieeg_header = parse_header(paths["ieeg_edf"])
    errors: list[str] = []
    warnings: list[str] = []
    fs_eeg = float(eeg_meta["SamplingFrequency"])
    fs_ieeg = float(ieeg_meta["SamplingFrequency"])
    for modality, header, expected_fs, channel_rows in (
        ("EEG", eeg_header, fs_eeg, eeg_channels),
        ("iEEG", ieeg_header, fs_ieeg, ieeg_channels),
    ):
        if len(set(header["channel_rates"])) != 1:
            errors.append(f"{modality} EDF has mixed per-channel sampling rates")
        elif abs(header["channel_rates"][0] - expected_fs) > 1e-9:
            errors.append(f"{modality} sidecar sampling rate differs from EDF header")
        if len(channel_rows) != header["channels"]:
            errors.append(f"{modality} channel-table row count differs from EDF header")
        if not header["size_matches_header"]:
            errors.append(f"{modality} EDF file size differs from declared record structure")
        if not header["time_valid"]:
            warnings.append(f"{modality} EDF start-time field is invalid: {header['date']} {header['time']}")
    return {
        "subject": session_dir.parent.name,
        "session": session_dir.name,
        "status": "PASS" if not errors else "FAIL",
        "eeg_sfreq_hz": fs_eeg,
        "ieeg_sfreq_hz": fs_ieeg,
        "eeg_channels": eeg_header["channels"],
        "ieeg_channels": ieeg_header["channels"],
        "eeg_samples": eeg_header["samples"],
        "ieeg_samples": ieeg_header["samples"],
        "eeg_duration_s": float(eeg_header["samples"] / fs_eeg),
        "ieeg_duration_s": float(ieeg_header["samples"] / fs_ieeg),
        "paired_event_files_present": True,
        "event_rows_read": False,
        "signal_samples_loaded": False,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--subjects", nargs="+", required=True,
                        help="Subjects explicitly designated development-only for this audit")
    parser.add_argument("--headers-only", action="store_true",
                        help="Read EDF headers and BIDS sidecars only; do not read event-table rows")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dataset = args.dataset.resolve()
    rows = []
    for subject in sorted(set(args.subjects)):
        subject_root = dataset / subject
        files = sorted(subject_root.glob("ses-*/eeg/*_eeg.json"))
        if not files:
            rows.append({"subject": subject, "status": "NO_EEG_SIDECARS"})
        audit = audit_header_only if args.headers_only else audit_one
        rows.extend(audit(path) for path in files)
    summary = {
        "dataset": "NEMAR on004752",
        "version": "v1.0.0",
        "role": ("metadata-only headers/sidecars; event rows and signal samples not read"
                 if args.headers_only else "development metadata audit; no confirmatory participants"),
        "subjects": sorted(set(args.subjects)),
        "sessions_checked": len(rows),
        "pass_sessions": sum(row.get("status") == "PASS" for row in rows),
        "fail_or_incomplete_sessions": sum(row.get("status") != "PASS" for row in rows),
        "sessions_with_edf_header_warnings": sum(bool(row.get("warnings")) for row in rows),
        "event_rows_read": False if args.headers_only else None,
        "signal_samples_loaded": False,
        "sessions": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "dataset", "version", "role", "subjects", "sessions_checked", "pass_sessions",
        "fail_or_incomplete_sessions", "signal_samples_loaded")}, indent=2))
    return 0 if summary["fail_or_incomplete_sessions"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
