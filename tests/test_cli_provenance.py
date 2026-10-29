from observable_geometry.cli import implementation_provenance


def test_numerical_module_change_changes_provenance_without_cli_change(tmp_path):
    (tmp_path / "cli.py").write_text("# unchanged CLI\n")
    module = tmp_path / "track_b" / "distinguishability.py"
    module.parent.mkdir()
    module.write_text("# numerical implementation A\n")
    before = implementation_provenance(tmp_path)
    module.write_text("# numerical implementation B\n")
    after = implementation_provenance(tmp_path)
    assert before["package_source_sha256"]["cli.py"] == after["package_source_sha256"]["cli.py"]
    assert before["package_source_fingerprint_sha256"] != after["package_source_fingerprint_sha256"]
    assert before["package_source_sha256"]["track_b/distinguishability.py"] != after["package_source_sha256"]["track_b/distinguishability.py"]


def test_provenance_is_stable_and_records_runtime():
    first = implementation_provenance()
    assert first == implementation_provenance()
    assert "track_b/distinguishability.py" in first["package_source_sha256"]
    assert set(first["runtime"]) == {"python", "numpy", "scipy"}
    assert all(first["runtime"].values())
