"""Metadata-only screen of NEMAR catalog entries labeled with EEG and iEEG."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from time import sleep
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs/track_b/20261024_b4_nemar_catalog_screen/catalog_screen.json"
PAGE_SIZE = 200
MAX_PAGES = 20
TIMEOUT_SECONDS = 30


def get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "ObservableGeometry-metadata-audit/1.0"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code >= 500 and attempt < 2:
                sleep(1 + attempt)
                continue
            raise RuntimeError(f"HTTP {exc.code} for metadata URL {url}") from exc
        except (URLError, TimeoutError) as exc:
            if attempt < 2:
                sleep(1 + attempt)
                continue
            raise RuntimeError(f"request failed for metadata URL {url}: {exc}") from exc
    raise RuntimeError(f"metadata request exhausted retries: {url}")


def modality_tokens(value: str | list[str] | None) -> set[str]:
    if isinstance(value, list):
        return {str(item).strip().lower() for item in value if str(item).strip()}
    return {item.strip().lower() for item in (value or "").split(",") if item.strip()}


def listing(url: str) -> list[dict]:
    payload = get_json(f"{url.rstrip('/')}/?format=json")
    children = payload.get("children")
    if not isinstance(children, list):
        raise ValueError(f"NEMAR listing has no children array: {url}")
    return children


def released_subject_modalities(dataset: str, version: str) -> dict[str, list[str]]:
    base = f"https://data.nemar.org/{dataset}/{version}"
    root = listing(base)
    result: dict[str, list[str]] = {}
    subjects = sorted(
        item["name"]
        for item in root
        if item.get("kind") == "dir" and item.get("name", "").startswith("sub-")
    )
    for subject in subjects:
        subject_url = f"{base}/{subject}"
        children = listing(subject_url)
        sessions = sorted(
            item["name"]
            for item in children
            if item.get("kind") == "dir" and item.get("name", "").startswith("ses-")
        )
        modality_names = {
            item["name"] for item in children
            if item.get("kind") == "dir" and item.get("name") in {"eeg", "ieeg", "motion"}
        }
        for session in sessions:
            session_children = listing(f"{subject_url}/{session}")
            modality_names.update(
                item["name"] for item in session_children
                if item.get("kind") == "dir" and item.get("name") in {"eeg", "ieeg", "motion"}
            )
        result[subject] = sorted(modality_names)
    return result


def catalog_records() -> tuple[list[dict], list[dict]]:
    records: list[dict] = []
    for page in range(MAX_PAGES):
        params = urlencode({"modality": "eeg,ieeg", "limit": PAGE_SIZE, "offset": page * PAGE_SIZE})
        payload = get_json(f"https://api.nemar.org/datasets?{params}")
        page_records = payload.get("datasets")
        if not isinstance(page_records, list):
            raise ValueError("NEMAR dataset API response has no datasets array")
        records.extend(page_records)
        if len(page_records) < PAGE_SIZE:
            break
    else:
        raise RuntimeError(f"Catalog exceeded configured page limit ({MAX_PAGES})")

    either = [record for record in records if modality_tokens(record.get("modalities")) & {"eeg", "ieeg"}]
    both = [
        record for record in either
        if {"eeg", "ieeg"}.issubset(modality_tokens(record.get("modalities")))
    ]
    return either, both


def main() -> None:
    try:
        if OUTPUT.exists():
            raise RuntimeError(f"refusing to overwrite existing audit evidence: {OUTPUT}")
        either, both = catalog_records()
        catalog_candidates = []
        for record in sorted(both, key=lambda item: item["dataset_id"]):
            dataset_id = record["dataset_id"]
            version = record.get("latest_version")
            item = {
                "dataset_id": dataset_id,
                "name": record.get("name"),
                "latest_version": version,
                "license": record.get("license"),
                "participants_api": record.get("participants"),
                "modalities": sorted(modality_tokens(record.get("modalities"))),
            }
            if dataset_id in {"nm000434", "on001785"}:
                item["subject_modalities"] = released_subject_modalities(dataset_id, version)
            catalog_candidates.append(item)

        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "schema_version": 1,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "Public catalog metadata and versioned directory listings only; no neural signal or outcome files requested.",
            "query": {
                "endpoint": "https://api.nemar.org/datasets",
                "modality_filter": "eeg,ieeg",
                "page_size": PAGE_SIZE,
                "offsets": list(range(0, len(either), PAGE_SIZE)),
                "returned_records_with_either_exact_modality": len(either),
                "exact_token_rule": "Both comma-separated modality tokens must equal eeg and ieeg; substring matching is not used.",
            },
            "both_modality_records": catalog_candidates,
        }
        OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": "PASS_METADATA_ONLY",
            "either_count": len(either),
            "both_count": len(both),
            "dataset_ids": [item["dataset_id"] for item in catalog_candidates],
            "output": str(OUTPUT),
        }, indent=2))
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(f"NEMAR metadata audit failed: {exc}") from exc


if __name__ == "__main__":
    main()
