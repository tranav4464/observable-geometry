from scripts.track_b.audit_wsgzp_public_geometry_inventory import is_geometry_candidate


def test_geometry_inventory_identifies_registration_artifacts():
    assert is_geometry_candidate("sub-01_egi_dig.hpts")
    assert is_geometry_candidate("sub-01_scanner_transform.mat")
    assert is_geometry_candidate("sub-01_head_coregistration.fif")


def test_geometry_inventory_does_not_match_project_name_inside_archive_name():
    assert not is_geometry_candidate("ccepcoreg-bids.z01")
    assert not is_geometry_candidate("ccepcoreg-bids.zip")
