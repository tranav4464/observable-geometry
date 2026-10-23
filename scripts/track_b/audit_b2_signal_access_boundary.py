"""Metadata-only audit of the B2 verifier's recorded-signal access boundary.

This script reads ZIP member names from the prepared NPZ archive and parses
verifier source as Python syntax. It never decompresses an NPZ member or loads
model/data arrays.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[2]
TRACK_A = ROOT / "outputs" / "tracka_release_20261022_v2"
VERIFIER = ROOT / "scripts" / "track_b" / "recompute_b2_gbf_cpu64.py"
PREPARED = TRACK_A / "prepared_bundle.npz"
EXPECTED_PREPARED_KEYS = {"leadfield", "noise_cov"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def npz_keys_from_directory(path: Path) -> set[str]:
    """Read ZIP central-directory names only; do not read member contents."""
    with zipfile.ZipFile(path) as archive:
        return {
            Path(name).stem
            for name in archive.namelist()
            if name.endswith(".npy") and "/" not in name and "\\" not in name
        }


def prepared_bundle_keys_read_by_verifier(tree: ast.Module) -> set[str]:
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.With, ast.AsyncWith)):
            continue
        for item in node.items:
            context = item.context_expr
            if not isinstance(context, ast.Call):
                continue
            context_text = ast.unparse(context)
            if "prepared_bundle.npz" not in context_text:
                continue
            alias = item.optional_vars
            if not isinstance(alias, ast.Name):
                raise ValueError("prepared bundle is not opened with a simple archive variable")
            found: set[str] = set()
            for child in ast.walk(ast.Module(body=node.body, type_ignores=[])):
                if not isinstance(child, ast.Subscript) or not isinstance(child.value, ast.Name):
                    continue
                if child.value.id != alias.id:
                    continue
                key_node = child.slice
                if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                    raise ValueError("prepared-bundle access uses a nonliteral key")
                found.add(key_node.value)
            keys |= found
    return keys


def audit() -> dict:
    tree = ast.parse(VERIFIER.read_text(encoding="utf-8"), filename=str(VERIFIER))
    read_keys = prepared_bundle_keys_read_by_verifier(tree)
    bundle_keys = npz_keys_from_directory(PREPARED)
    unexpected = read_keys - EXPECTED_PREPARED_KEYS
    missing = EXPECTED_PREPARED_KEYS - bundle_keys
    if unexpected:
        raise ValueError(f"verifier reads unexpected prepared-bundle keys: {sorted(unexpected)}")
    if missing:
        raise ValueError(f"prepared bundle lacks expected model keys: {sorted(missing)}")
    if read_keys != EXPECTED_PREPARED_KEYS:
        raise ValueError(f"verifier prepared-bundle key set is incomplete: {sorted(read_keys)}")
    return {
        "status": "PASS",
        "audit_type": "metadata-only ZIP directory and AST access-boundary check",
        "prepared_bundle_npz_keys_from_headers": sorted(bundle_keys),
        "prepared_bundle_keys_referenced_by_verifier": sorted(read_keys),
        "recorded_eeg_data_key_exists_in_archive": "data" in bundle_keys,
        "recorded_eeg_data_key_referenced_by_verifier": "data" in read_keys,
        "npz_member_payloads_decompressed": False,
        "model_arrays_loaded": False,
        "verifier_sha256": sha256(VERIFIER),
        "prepared_bundle_sha256": sha256(PREPARED),
        "limitation": "Static access-boundary check; it does not execute or independently validate the verifier's numerical result.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new JSON output file outside the sealed Track A release")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output = output.resolve()
    if output == TRACK_A.resolve() or TRACK_A.resolve() in output.parents:
        raise SystemExit("Refusing to write inside the sealed Track A release")
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = audit()
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**result, "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
