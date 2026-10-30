from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "track_b"))
from audit_wsgzp_coregistration import make_t1w_to_head, resolve_subjects
from mne.transforms import apply_trans


def test_fiducials_map_to_expected_head_axes():
    fid = {
        "NAS": [0.0, 85.0, -12.0],
        "LPA": [-65.0, -3.0, -30.0],
        "RPA": [63.0, -6.0, -22.0],
    }
    trans = make_t1w_to_head(fid)
    head = apply_trans(
        trans, np.asarray([fid[k] for k in ("NAS", "LPA", "RPA")]) / 1000.0
    )
    assert head[0, 1] > 0
    assert head[1, 0] < 0 < head[2, 0]
    assert np.max(np.abs([head[0, 0], head[0, 2], head[1, 1], head[1, 2],
                          head[2, 1], head[2, 2]])) < 1e-12


def test_missing_fiducial_is_rejected():
    with pytest.raises(ValueError, match="Missing fiducials"):
        make_t1w_to_head({"NAS": [0, 1, 2], "LPA": [-1, 0, 0]})


def test_missing_or_empty_dataset_root_cannot_return_empty_success(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        resolve_subjects(tmp_path / "missing")
    with pytest.raises(ValueError, match=r"No sub-\* participant"):
        resolve_subjects(tmp_path)


def test_requested_subject_must_exist(tmp_path):
    (tmp_path / "sub-01").mkdir()
    with pytest.raises(ValueError, match="participant directories are missing"):
        resolve_subjects(tmp_path, ["sub-02"])


def test_fiducial_transform_is_not_treated_as_frame_validation():
    from audit_wsgzp_coregistration import audit_subject

    build_root = Path(__file__).resolve().parents[2]
    source = build_root / "Datasets" / "WSGZP" / "extracted" / "ccepcoreg"
    if not source.exists():
        source = build_root / "wsgzp datset" / "extracted" / "ccepcoreg"
    if not source.exists():
        pytest.skip("Local WSGZP dataset is not available")
    report = audit_subject(source, "sub-01")
    assert report["status"] == "REVIEW_REQUIRED_VISUAL_OVERLAY"
    assert report["nifti_spatial_units"] == "mm"
    assert report["fiducial_transform_check"] == "CONSTRUCTION_CHECK_ONLY_NOT_INDEPENDENT_VALIDATION"
