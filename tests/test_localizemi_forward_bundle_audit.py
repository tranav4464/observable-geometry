import numpy as np
import pytest

from scripts.track_b.audit_localizemi_forward_bundle import inverse_transform_error, parse_annex_key


def test_inverse_transform_error_accepts_matching_translation():
    head_to_surface = np.eye(4)
    head_to_surface[:3, 3] = [0.002, -0.013, -0.0008]
    mri_to_head = np.linalg.inv(head_to_surface)
    assert inverse_transform_error(mri_to_head, head_to_surface) == 0.0


def test_parse_annex_key_reads_size_and_md5():
    size, digest = parse_annex_key("/annex/objects/MD5-s177020482--cc9634d940779b9a11c81afd676ea366\n")
    assert size == 177020482
    assert digest == "cc9634d940779b9a11c81afd676ea366"


@pytest.mark.parametrize("text", ["", "not-a-pointer", "/annex/objects/MD5-s10--bad"])
def test_parse_annex_key_rejects_malformed_pointer(text):
    with pytest.raises(ValueError):
        parse_annex_key(text)


def test_inverse_transform_error_detects_mismatch():
    head_to_surface = np.eye(4)
    mri_to_head = np.eye(4)
    mri_to_head[0, 3] = 0.01
    assert inverse_transform_error(mri_to_head, head_to_surface) == pytest.approx(0.01)


@pytest.mark.parametrize(
    "mri_to_head,head_to_surface",
    [
        (np.eye(3), np.eye(4)),
        (np.full((4, 4), np.nan), np.eye(4)),
        (np.eye(4), np.full((4, 4), np.inf)),
        (np.eye(4), np.zeros((4, 4))),
        (np.eye(4), np.diag([-1.0, 1.0, 1.0, 1.0])),
    ],
)
def test_inverse_transform_error_rejects_invalid_transforms(mri_to_head, head_to_surface):
    with pytest.raises(ValueError):
        inverse_transform_error(mri_to_head, head_to_surface)
