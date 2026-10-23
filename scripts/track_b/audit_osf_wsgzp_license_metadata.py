"""Audit public OSF license metadata and file names without downloading data."""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
API = "https://api.osf.io/v2"
NODE = "wsgzp"
DEFAULT_OUTPUT = ROOT / "outputs/track_b/20261024_b4_osf_license_audit/osf_license_metadata.json"


def get_json(url: str) -> dict:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "api.osf.io":
        raise ValueError("metadata audit follows OSF API URLs only")
    request = Request(url, headers={"User-Agent": "ObservableGeometry-metadata-audit/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def audit(fetch=get_json) -> dict:
    node_doc = fetch(f"{API}/nodes/{NODE}/")
    node = node_doc["data"]
    license_ref = node.get("relationships", {}).get("license", {}).get("data")
    license_record = None
    if license_ref and license_ref.get("id"):
        license_doc = fetch(f"{API}/licenses/{license_ref['id']}/")
        attrs = license_doc["data"]["attributes"]
        license_record = {key: attrs.get(key) for key in ("name", "text", "url")}

    pending = deque([f"{API}/nodes/{NODE}/files/osfstorage/"])
    files: list[dict[str, str]] = []
    visited: set[str] = set()
    while pending:
        url = pending.popleft()
        if url in visited:
            continue
        visited.add(url)
        page = fetch(url)
        for item in page.get("data", []):
            attrs = item.get("attributes", {})
            name = attrs.get("name", "")
            path = attrs.get("materialized_path", "")
            kind = attrs.get("kind", "")
            files.append({"name": name, "path": path, "kind": kind})
            if kind == "folder":
                children = (
                    item.get("relationships", {})
                    .get("files", {})
                    .get("links", {})
                    .get("related", {})
                    .get("href")
                )
                if children:
                    pending.append(children)
        next_url = page.get("links", {}).get("next")
        if next_url:
            pending.append(next_url)

    files.sort(key=lambda item: (item["path"].casefold(), item["name"].casefold()))
    named_license = [item for item in files if item["name"].casefold() == "license.txt"]
    return {
        "audit": "OSF public metadata only; no file download or content access",
        "node": NODE,
        "node_title": node.get("attributes", {}).get("title"),
        "public": node.get("attributes", {}).get("public"),
        "license": license_record,
        "license_file_listed": bool(named_license),
        "license_file_paths": [item["path"] for item in named_license],
        "visible_file_count": sum(item["kind"] == "file" for item in files),
        "visible_storage_inventory": files,
        "access_boundary": "Only OSF JSON API metadata endpoints were requested; links.download was not requested.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    if not output.is_relative_to((ROOT / "outputs").resolve()):
        raise ValueError("audit output must be written under the ignored outputs directory")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite prior metadata audit: {output}")
    result = audit()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS_METADATA_AUDIT",
        "output": output.relative_to(ROOT).as_posix(),
        "license": result["license"],
        "license_file_listed": result["license_file_listed"],
        "visible_file_count": result["visible_file_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
