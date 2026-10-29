"""CLI contract checks using algebraic software fixtures, not neural signals."""
import json

import numpy as np

from observable_geometry.cli import main


def _metadata(path, sensor_names):
    path.write_text(json.dumps({
        "dataset": "algebraic CLI contract fixture",
        "participant": "not_applicable",
        "forward_model": "fixed test matrix",
        "reference": "identity",
        "coordinate_frame": "arbitrary test frame",
        "source_orientation": "fixed columns",
        "noise_covariance": "identity",
        "sensor_names": sensor_names,
    }), encoding="utf-8")


def test_distinguish_cli_writes_auditable_outputs(tmp_path, capsys):
    bundle = tmp_path / "model.npz"
    metadata = tmp_path / "metadata.json"
    output = tmp_path / "result"
    leadfield = np.array([[1., 0., 1.], [0., 1., 1.]])
    coordinates = np.array([[0., 0., 0.], [0.1, 0., 0.], [0., 0.1, 0.]])
    np.savez(bundle, leadfield=leadfield, noise_covariance=np.eye(2), coordinates_m=coordinates,
             source_ids=np.array([101, 202, 303], dtype=np.int64))
    _metadata(metadata, ["S1", "S2"])

    code = main(["distinguish", "--bundle", str(bundle), "--metadata", str(metadata),
                 "--output", str(output), "--minimum-distance-mm", "20", "--top-k", "2"])

    assert code == 0
    assert "COMPLETED_NOMINAL_MODEL_DIAGNOSTIC" in capsys.readouterr().out
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "run_manifest.json").read_text(encoding="utf-8"))
    assert summary["source_count"] == 3
    assert summary["covariance_rank"] == 2
    assert manifest["recorded_signal_array_accessed"] is False
    provenance = manifest["implementation_provenance"]
    assert "track_b/distinguishability.py" in provenance["package_source_sha256"]
    assert provenance["runtime"]["numpy"] == np.__version__
    allowed = [json.loads(line) for line in (output / "npz_key_access.jsonl").read_text().splitlines()]
    assert {row["key"] for row in allowed} == {"leadfield", "noise_covariance", "coordinates_m", "source_ids"}
    assert all(row["decision"] == "allow" for row in allowed)
    assert (output / "ranked_pairs.csv").is_file()
    assert (output / "scores.npz").is_file()


def test_distinguish_cli_rejects_unlisted_signal_member_without_loading_it(tmp_path, capsys):
    bundle = tmp_path / "forbidden.npz"
    metadata = tmp_path / "metadata.json"
    output = tmp_path / "rejected"
    np.savez(bundle, leadfield=np.eye(2), noise_covariance=np.eye(2),
             coordinates_m=np.array([[0., 0., 0.], [0.1, 0., 0.]]),
             data=np.array([object()], dtype=object))
    _metadata(metadata, ["S1", "S2"])

    code = main(["distinguish", "--bundle", str(bundle), "--metadata", str(metadata),
                 "--output", str(output)])

    assert code == 2
    assert "undeclared array member(s): data" in capsys.readouterr().err
    assert not output.exists()


def test_distinguish_cli_does_not_publish_partial_output_when_metadata_is_invalid(tmp_path, capsys):
    bundle = tmp_path / "model.npz"
    metadata = tmp_path / "metadata.json"
    output = tmp_path / "result"
    np.savez(bundle, leadfield=np.eye(2), noise_covariance=np.eye(2),
             coordinates_m=np.array([[0., 0., 0.], [0.1, 0., 0.]]))
    metadata.write_text("{}", encoding="utf-8")

    code = main(["distinguish", "--bundle", str(bundle), "--metadata", str(metadata),
                 "--output", str(output)])

    assert code == 2
    assert "metadata is missing nonempty field(s)" in capsys.readouterr().err
    assert not output.exists()


def test_cli_refuses_existing_output_without_changing_it(tmp_path, capsys):
    bundle = tmp_path / "model.npz"
    metadata = tmp_path / "metadata.json"
    output = tmp_path / "result"
    output.mkdir()
    sentinel = output / "keep.txt"
    sentinel.write_text("existing", encoding="utf-8")
    np.savez(bundle, leadfield=np.eye(2), noise_covariance=np.eye(2),
             coordinates_m=np.array([[0., 0., 0.], [0.1, 0., 0.]]))
    _metadata(metadata, ["S1", "S2"])

    code = main(["distinguish", "--bundle", str(bundle), "--metadata", str(metadata),
                 "--output", str(output)])

    assert code == 2
    assert "refusing to overwrite existing output path" in capsys.readouterr().err
    assert sentinel.read_text(encoding="utf-8") == "existing"


def test_cli_does_not_report_success_if_atomic_publish_fails(tmp_path, capsys, monkeypatch):
    bundle = tmp_path / "model.npz"
    metadata = tmp_path / "metadata.json"
    output = tmp_path / "result"
    np.savez(bundle, leadfield=np.array([[1., 0.], [0., 1.]]),
             noise_covariance=np.eye(2),
             coordinates_m=np.array([[0., 0., 0.], [0.1, 0., 0.]]))
    _metadata(metadata, ["S1", "S2"])

    def fail_publish(_source, _destination):
        raise OSError("simulated atomic publish failure")

    monkeypatch.setattr("observable_geometry.cli.os.rename", fail_publish)
    code = main(["distinguish", "--bundle", str(bundle), "--metadata", str(metadata),
                 "--output", str(output)])

    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    assert "simulated atomic publish failure" in captured.err
    assert not output.exists()
