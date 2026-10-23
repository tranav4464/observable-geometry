"""Content-addressed, integrity-checked GBFs geometry-basis cache."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _src_hash(src) -> str:
    digest = hashlib.sha256()
    for hemi in src:
        digest.update(np.ascontiguousarray(hemi["vertno"]).view(np.uint8))
        digest.update(np.ascontiguousarray(hemi["rr"][hemi["vertno"]]).view(np.uint8))
    return digest.hexdigest()


def _valid_basis(result, n_modes: int, left_vertices: int, right_vertices: int,
                 constant_mode_tolerance: float = 1e-12) -> bool:
    el, er, pl, pr = result
    if (el.shape != (n_modes,) or er.shape != (n_modes,) or
            pl.shape != (left_vertices, n_modes) or pr.shape != (right_vertices, n_modes) or
            not all(np.isfinite(a).all() for a in result)):
        return False
    # Each connected cortical Laplacian has one constant mode at eigenvalue 0.
    # The pinned inverse explicitly replaces that first value with the next one.
    for eigenvalues in (el, er):
        if abs(float(eigenvalues[0])) > constant_mode_tolerance:
            return False
        if np.any(eigenvalues[1:] <= 0) or np.any(eigenvalues >= 1):
            return False
    return True


def load_or_compute(cache_path: Path, fwd_path: Path, vendor_path: Path, src,
                    n_modes: int, compute, *, cut: bool = True):
    """Load only an exact matching cache; otherwise compute and bind metadata."""
    identity = {
        "schema": 1,
        "forward_sha256": sha256_file(fwd_path),
        "vendor_sha256": sha256_file(vendor_path),
        "source_geometry_sha256": _src_hash(src),
        "n_modes_per_hemisphere": int(n_modes),
        "cut": bool(cut),
        "units": "MNE source-space coordinates in metres",
        "vertex_order": "left hemisphere source vertno order followed by right hemisphere source vertno order",
    }
    if cache_path.exists():
        with np.load(cache_path, allow_pickle=False) as bundle:
            if "metadata_json" not in bundle:
                raise ValueError(f"Unverified geometry cache has no identity metadata: {cache_path}")
            metadata = json.loads(str(bundle["metadata_json"].item()))
            if metadata != identity:
                raise ValueError(f"Geometry cache identity mismatch: {cache_path}; remove it or use a new run id")
            result = tuple(bundle[key].copy() for key in ("el", "er", "pl", "pr"))
    else:
        result = tuple(compute(src, n_modes, cut=cut, save=False))
        np.savez_compressed(cache_path, el=result[0], er=result[1], pl=result[2], pr=result[3],
                            metadata_json=np.asarray(json.dumps(identity, sort_keys=True)))
    el, er, pl, pr = result
    expected_left, expected_right = len(src[0]["vertno"]), len(src[1]["vertno"])
    if not _valid_basis(result, n_modes, expected_left, expected_right):
        raise ValueError("GBFs cache has invalid dimensions, values, or inverse-log penalty eigenvalues")
    return result, identity
