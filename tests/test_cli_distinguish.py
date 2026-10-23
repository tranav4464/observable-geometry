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
    access = [json.loads(line) for line in (output / "npz_key_access.jsonl").read_text().splitlines()]
    assert len(access) == 1
    assert access[0]["archive"] == "forbidden.npz"
    assert access[0]["key"] == "data"
    assert access[0]["decision"] == "deny"
