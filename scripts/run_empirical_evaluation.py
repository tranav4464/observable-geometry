"""Descriptive, same-participant Localize-MI pulse-artifact localization check.

This is a development evaluation, not held-out validation. It uses the six
sub-01 1 mA contact pairs for the primary site-similarity comparison and all
11 runs for a secondary current-sensitivity table.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import html
import json
import os
from pathlib import Path
from types import SimpleNamespace

import h5py
import mne
import numpy as np
from scipy.stats import spearmanr, pearsonr
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parents[1]
from tracka_paths import OUT
from geometry_basis_cache import load_or_compute
META = ROOT / "data/Localize-MI"
PAYLOAD = ROOT / "data/payload"
SUBJECT = "sub-01"
PRIMARY_RUNS = [1, 3, 5, 6, 8, 10]
ALL_RUNS = list(range(1, 12))
WINDOW_S = (-0.002, 0.002)
N_MODES_PER_HEMISPHERE = 300


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_paths(run: int) -> tuple[Path, Path, Path]:
    stem = f"{SUBJECT}_task-seegstim_run-{run:02d}"
    meta = META / "derivatives/epochs" / SUBJECT / "eeg"
    payload = PAYLOAD / "derivatives/epochs" / SUBJECT / "eeg"
    return (payload / f"{stem}_epochs.npy", meta / f"{stem}_channels.tsv",
            meta / f"{stem}_epochs.tsv")


def contacts_for_label(label: str, contact_xyz: dict[str, np.ndarray]) -> tuple[str, str]:
    # Dataset labels are e.g. K13-14 or X'1-2; the second contact repeats the shaft prefix.
    site = label.split()[0]
    first, second_number = site.split("-")
    prefix = "".join(c for c in first if not c.isdigit())
    second = prefix + second_number
    if first not in contact_xyz or second not in contact_xyz:
        raise ValueError(f"Could not resolve stimulating contacts {first}, {second} from {label!r}")
    return first, second


def whiten_matrix(covariance: np.ndarray) -> tuple[np.ndarray, int]:
    values, vectors = np.linalg.eigh((covariance + covariance.T) / 2)
    keep = values > 1e-10 * values.max()
    return vectors[:, keep].T / np.sqrt(values[keep])[:, None], int(keep.sum())


def abs_cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float("nan")
    return float(abs(np.dot(a, b) / (na * nb)))


def main() -> None:
    # Load metadata first and require the complete predeclared development subset.
    metadata_by_run = {}
    common_good = None
    run_clock = None
    for run in ALL_RUNS:
        epoch_path, channels_path, events_path = run_paths(run)
        if not epoch_path.is_file():
            raise SystemExit(f"Missing sub-01 run-{run:02d} payload; run scripts/fetch_localize.py")
        ch = rows(channels_path)
        ev = rows(events_path)
        if not ch or not ev:
            raise SystemExit(f"run-{run:02d} has empty channel or epoch metadata")
        all_names = [r["name"] for r in ch]
        if len(set(all_names)) != len(all_names):
            raise SystemExit(f"run-{run:02d} contains duplicate channel names")
        eeg_rows = [r for r in ch if r["type"].upper() == "EEG"]
        if not eeg_rows or any(r["units"] != "V" for r in eeg_rows):
            raise SystemExit(f"run-{run:02d} EEG channels must be explicitly stored in volts")
        sfreqs = {float(r["sampling_frequency"]) for r in eeg_rows}
        if len(sfreqs) != 1:
            raise SystemExit(f"run-{run:02d} has inconsistent EEG sampling frequencies")
        zeros = {float(r["zero_time"]) for r in ev}
        durations = {float(r["duration"]) for r in ev}
        labels = {r["trial_type"] for r in ev}
        if len(zeros) != 1 or len(durations) != 1 or len(labels) != 1:
            raise SystemExit(f"run-{run:02d} requires one event label and a consistent epoch time grid")
        clock = (sfreqs.pop(), zeros.pop(), durations.pop())
        if run_clock is None:
            run_clock = clock
        elif not np.allclose(clock, run_clock, rtol=0, atol=1e-12):
            raise SystemExit(f"run-{run:02d} time metadata differ from the frozen common-grid contract")
        names = [r["name"] for r in ch if r["status"] == "good"]
        common_good = set(names) if common_good is None else common_good.intersection(names)
        metadata_by_run[run] = (epoch_path, ch, ev)
    channel_order = [r["name"] for r in metadata_by_run[1][1] if r["name"] in common_good]
    if len(channel_order) < 100:
        raise SystemExit("Fewer than 100 channels are common to all development runs")

    fwd_path = PAYLOAD / "derivatives/sourcemodelling" / SUBJECT / "fwd" / f"{SUBJECT}_fwd.fif"
    fwd = mne.read_forward_solution(fwd_path, verbose="ERROR")
    fwd = mne.pick_channels_forward(fwd, include=channel_order, ordered=True, copy=True, verbose="ERROR")
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True, use_cps=True, verbose="ERROR")
    if fwd["sol"]["row_names"] != channel_order:
        raise SystemExit("Forward channels do not exactly match the common good-channel order")
    lead_raw = fwd["sol"]["data"]
    n_left = len(fwd["src"][0]["vertno"])
    source_vertices = np.r_[fwd["src"][0]["vertno"], fwd["src"][1]["vertno"]]
    src_head = np.vstack([s["rr"][s["vertno"]] for s in fwd["src"]])
    transform_file = META / "derivatives/sourcemodelling" / SUBJECT / "xfm" / f"{SUBJECT}_from-head_to-surface.h5"
    with h5py.File(transform_file, "r") as h5:
        head_to_surface = np.asarray(h5["trans"][()], dtype=float)
    fixed_normals_surface = np.asarray(fwd["source_nn"], dtype=float) @ head_to_surface[:3, :3].T
    fixed_normals_surface /= np.linalg.norm(fixed_normals_surface, axis=1, keepdims=True)
    src_surface = mne.transforms.apply_trans(head_to_surface, src_head)
    contacts_path = META / "derivatives/epochs" / SUBJECT / "ieeg" / f"{SUBJECT}_task-seegstim_space-surface_electrodes.tsv"
    contact_xyz = {r["name"]: np.array([float(r[a]) for a in ("x", "y", "z")])
                   for r in rows(contacts_path)}
    source_tree = __import__("scipy.spatial", fromlist=["cKDTree"]).cKDTree(src_surface)

    # Estimate a single reference-consistent noise model from baseline samples of
    # the six predeclared 1 mA site runs. Accumulate cross-products to bound memory.
    total = 0
    sum_x = np.zeros(len(channel_order))
    sum_xx = np.zeros((len(channel_order), len(channel_order)))
    run_data = {}
    sfreq, zero_time, duration = run_clock
    grid_samples = None
    for run in ALL_RUNS:
        epoch_path, ch, event_rows = metadata_by_run[run]
        epoch_array = np.load(epoch_path, mmap_mode="r")
        if epoch_array.ndim != 3 or epoch_array.shape[0] != len(event_rows) or epoch_array.shape[1] != len(ch):
            raise SystemExit(f"run-{run:02d} epoch array dimensions disagree with metadata")
        if grid_samples is None:
            grid_samples = int(epoch_array.shape[-1])
        elif int(epoch_array.shape[-1]) != grid_samples:
            raise SystemExit(f"run-{run:02d} sample count differs from the frozen common time grid")
        times = -zero_time + np.arange(epoch_array.shape[-1]) / sfreq
        if abs((times[-1] - times[0]) - (duration - 1 / sfreq)) > 1 / sfreq + 1e-12:
            raise SystemExit(f"run-{run:02d} epoch length disagrees with duration metadata")
        if not np.any((times >= -0.20) & (times <= -0.05)) or not np.any((times >= 0) & (times <= 0.01)):
            raise SystemExit(f"run-{run:02d} does not cover the frozen baseline and artifact windows")
        idx = [next(i for i, r in enumerate(ch) if r["name"] == name) for name in channel_order]
        selected = np.asarray(epoch_array[:, idx, :], dtype=np.float64)
        if not np.isfinite(selected).all():
            raise SystemExit(f"run-{run:02d} contains nonfinite selected EEG samples")
        baseline_mask = (times >= -0.20) & (times <= -0.05)
        run_window_mask = (times >= WINDOW_S[0]) & (times <= WINDOW_S[1])
        if run in PRIMARY_RUNS:
            base = selected[:, :, baseline_mask].transpose(1, 0, 2).reshape(len(channel_order), -1)
            total += base.shape[1]
            sum_x += base.sum(axis=1)
            sum_xx += base @ base.T
        evoked = selected.mean(axis=0)
        labels = sorted({r["trial_type"] for r in event_rows})
        if len(labels) != 1:
            raise SystemExit(f"run-{run:02d} has multiple event labels and needs a stratified adapter")
        c1, c2 = contacts_for_label(labels[0], contact_xyz)
        target_midpoint = (contact_xyz[c1] + contact_xyz[c2]) / 2
        target_dist, target_index = source_tree.query(target_midpoint)
        contact_axis = contact_xyz[c2] - contact_xyz[c1]
        contact_axis /= np.linalg.norm(contact_axis)
        orientation_cosine = float(abs(np.dot(fixed_normals_surface[target_index], contact_axis)))
        orientation_angle = float(np.degrees(np.arccos(np.clip(orientation_cosine, -1, 1))))
        # Use the single sample with greatest global field power in the frozen
        # window; unlike a signed mean, this does not cancel opposite phases.
        window_samples = evoked[:, run_window_mask]
        peak = int(np.argmax(np.linalg.norm(window_samples, axis=0)))
        window_topography = window_samples[:, peak]
        run_data[run] = {"evoked": evoked, "label": labels[0], "n_trials": int(selected.shape[0]),
                         "contacts": [c1, c2], "target_midpoint_surface_m": target_midpoint.tolist(),
                         "target_vertex_index": int(target_index), "target_vertex_id": int(source_vertices[target_index]),
                         "target_hemisphere": "L" if target_index < n_left else "R",
                         "midpoint_to_cortical_grid_mm": float(target_dist * 1000),
                         "fixed_cortical_normal_vs_contact_axis_angle_degrees": orientation_angle,
                         "observed_topography": window_topography,
                         "observed_topography_peak_gfp_time_s": float(times[run_window_mask][peak]),
                         "epochs_sha256": sha256(epoch_path)}
    baseline_cov = (sum_xx - np.outer(sum_x, sum_x) / total) / (total - 1)
    # Apply average reference to all compared objects, then shrink in the
    # reference-supported subspace (rank 1 fewer than channels).
    ref = np.eye(len(channel_order)) - np.ones((len(channel_order), len(channel_order))) / len(channel_order)
    lead = ref @ lead_raw
    baseline_cov = ref @ baseline_cov @ ref.T
    baseline_cov = 0.9 * baseline_cov + 0.1 * np.trace(baseline_cov) / (len(channel_order) - 1) * ref
    whitener, noise_rank = whiten_matrix(baseline_cov)

    # Build the same GBFs 300-mode-per-hemisphere source family used by the paper demo.
    vendor_file = ROOT / "vendor/GBFs/utils/seeg_with_eeg.py"
    tree_ast = ast.parse(vendor_file.read_text(encoding="utf-8"))
    wanted = {"get_tria_from_src", "calc_eig_from_src", "process_evoked"}
    defs = [n for n in tree_ast.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    if {n.name for n in defs} != wanted:
        raise SystemExit("Pinned GBFs implementation functions changed")
    ns = {"np": np, "mne": mne, "lapy": __import__("lapy"), "os": os}
    exec(compile(ast.Module(body=defs, type_ignores=[]), str(vendor_file), "exec"), ns)
    basis_cache = OUT / "basis_300_per_hemisphere.npz"
    print("Loading or computing identity-checked pinned GBFs 300-mode basis", flush=True)
    (el, er, pl, pr), basis_identity = load_or_compute(
        basis_cache, fwd_path, vendor_file, fwd["src"], N_MODES_PER_HEMISPHERE,
        ns["calc_eig_from_src"])

    # Apply inverse estimates at each run under fixed settings, then score the
    # peak absolute response in the prespecified artifact window.
    for run in ALL_RUNS:
        item = run_data[run]
        evoked = item["evoked"]
        x = ref @ evoked
        gbfs_evoked = SimpleNamespace(data=x, nave=item["n_trials"])
        gbfs_source, _ = ns["process_evoked"](gbfs_evoked, whitener, 1.2, el, er, pl, pr,
                                                 fwd["src"], lead)
        g_peak_index = int(np.argmax(np.max(np.abs(gbfs_source[:, run_window_mask]), axis=1)))

        info = mne.create_info(channel_order, sfreq, ch_types="eeg")
        mne_evoked = mne.EvokedArray(x, info, tmin=-0.25, verbose="ERROR")
        mne_evoked.nave = item["n_trials"]
        mne_evoked.set_eeg_reference(ref_channels="average", projection=True, verbose="ERROR")
        cov = mne.Covariance(baseline_cov, channel_order, [], mne_evoked.info["projs"],
                             nfree=max(total - 1, 1), method="empirical", verbose="ERROR")
        inv = mne.minimum_norm.make_inverse_operator(mne_evoked.info, fwd, cov,
                                                      loose=0.0, depth=None, fixed=True,
                                                      rank="info", verbose="ERROR")
        stc = mne.minimum_norm.apply_inverse(mne_evoked, inv, lambda2=1.0 / 9.0,
                                              method="MNE", pick_ori=None, verbose="ERROR")
        m_peak_index = int(np.argmax(np.max(np.abs(stc.data[:, run_window_mask]), axis=1)))
        target = np.asarray(item["target_midpoint_surface_m"])
        g_dist = float(np.linalg.norm(src_surface[g_peak_index] - target) * 1000)
        m_dist = float(np.linalg.norm(src_surface[m_peak_index] - target) * 1000)
        item["gbfs_peak_index"] = g_peak_index
        item["mne_peak_index"] = m_peak_index
        item["gbfs_peak_source_vertex_id"] = int(source_vertices[g_peak_index])
        item["mne_peak_source_vertex_id"] = int(source_vertices[m_peak_index])
        item["gbfs_peak_hemisphere"] = "L" if g_peak_index < n_left else "R"
        item["mne_peak_hemisphere"] = "L" if m_peak_index < n_left else "R"
        item["gbfs_peak_error_mm"] = g_dist
        item["mne_peak_error_mm"] = m_dist
        item["gbfs_peak_source_amplitude_abs"] = float(np.max(np.abs(gbfs_source[:, run_window_mask])))
        item["mne_peak_source_amplitude_abs"] = float(np.max(np.abs(stc.data[:, run_window_mask])))

    primary = [run_data[r] for r in PRIMARY_RUNS]
    predicted = []
    observed = []
    for item in primary:
        idx = item["target_vertex_index"]
        predicted.append(whitener @ lead[:, idx])
        observed.append(whitener @ (ref @ item["observed_topography"]))
    predicted_similarity, observed_similarity = [], []
    pair_rows = []
    for i in range(len(primary)):
        for j in range(i + 1, len(primary)):
            p = abs_cosine(predicted[i], predicted[j])
            o = abs_cosine(observed[i], observed[j])
            predicted_similarity.append(p)
            observed_similarity.append(o)
            pair_rows.append({"site_a": primary[i]["label"], "site_b": primary[j]["label"],
                              "predicted_signature_similarity": p,
                              "observed_artifact_similarity": o})
    pearson = float(pearsonr(predicted_similarity, observed_similarity).statistic)
    spearman = float(spearmanr(predicted_similarity, observed_similarity).statistic)

    # Same-pair 1-vs-5 mA topographic similarity is a sensitivity check, not a
    # localization metric; the pairs are repeated within a single participant.
    by_site_current = {}
    for run, item in run_data.items():
        site = "-".join(item["contacts"])
        intensity = item["label"].split()[-1]
        by_site_current.setdefault(site, {})[intensity] = item
    intensity_pairs = []
    for site, current_map in sorted(by_site_current.items()):
        if "1mA" in current_map and "5mA" in current_map:
            a = whitener @ (ref @ current_map["1mA"]["observed_topography"])
            b = whitener @ (ref @ current_map["5mA"]["observed_topography"])
            intensity_pairs.append({"site": site, "observed_1mA_vs_5mA_similarity": abs_cosine(a, b)})

    primary_errors = [{"condition": run_data[r]["label"], "trials": run_data[r]["n_trials"],
                       "midpoint_to_cortical_grid_mm": run_data[r]["midpoint_to_cortical_grid_mm"],
                       "fixed_normal_vs_contact_axis_angle_degrees": run_data[r]["fixed_cortical_normal_vs_contact_axis_angle_degrees"],
                       "GBFs_peak_error_mm": run_data[r]["gbfs_peak_error_mm"],
                       "GBFs_peak_hemisphere": run_data[r]["gbfs_peak_hemisphere"],
                       "MNE_peak_error_mm": run_data[r]["mne_peak_error_mm"],
                       "MNE_peak_hemisphere": run_data[r]["mne_peak_hemisphere"]}
                      for r in PRIMARY_RUNS]
    report = {
        "status": "completed descriptive development evaluation; not held-out validation",
        "task": "localize the known intracranial pulse-artifact stimulation site from averaged scalp EEG",
        "participant": SUBJECT,
        "primary_sites": len(PRIMARY_RUNS), "primary_runs": PRIMARY_RUNS,
        "primary_intensity": "1 mA", "secondary_runs": ALL_RUNS,
        "secondary_intensity_pairs": intensity_pairs,
        "observation_window_s": list(WINDOW_S), "n_trials_primary": {str(r): run_data[r]["n_trials"] for r in PRIMARY_RUNS},
        "common_good_channels": channel_order, "n_common_good_channels": len(channel_order),
        "reference": "same common-channel average reference for observations, forward and pooled baseline covariance",
        "orientation_model": "fixed cortical-normal leadfield; contact-pair axis angle is only a geometry diagnostic and is not assumed to equal stimulation-current orientation",
        "epoch_grid": {"sampling_frequency_hz": sfreq, "zero_time_s": zero_time,
                       "duration_s": duration, "samples": int(epoch_array.shape[-1])},
        "pooled_baseline_noise_rank": noise_rank,
        "GBFs": {"modes_per_hemisphere": N_MODES_PER_HEMISPHERE, "lambda": 1.2,
                 "settings": "pinned upstream recorded-data transformation; no tuning on target errors",
                 "basis_cache_identity": basis_identity},
        "MNE": {"method": "fixed-orientation minimum norm", "lambda2": 1.0 / 9.0,
                "depth_weighting": None, "settings": "fixed comparator; single-trial baseline covariance is scaled by each Evoked nave; no tuning on target errors"},
        "localization_errors": primary_errors,
        "orientation_diagnostic": {
            "angles_degrees": [run_data[r]["fixed_cortical_normal_vs_contact_axis_angle_degrees"] for r in PRIMARY_RUNS],
            "range_degrees": [float(min(run_data[r]["fixed_cortical_normal_vs_contact_axis_angle_degrees"] for r in PRIMARY_RUNS)),
                              float(max(run_data[r]["fixed_cortical_normal_vs_contact_axis_angle_degrees"] for r in PRIMARY_RUNS))],
            "interpretation": "The stimulation-contact axis is only a geometry proxy. Its angle to the fixed cortical normal does not identify the physical artifact-current orientation.",
        },
        "summary_error_mm": {
            "GBFs_median": float(np.median([run_data[r]["gbfs_peak_error_mm"] for r in PRIMARY_RUNS])),
            "GBFs_mean": float(np.mean([run_data[r]["gbfs_peak_error_mm"] for r in PRIMARY_RUNS])),
            "MNE_median": float(np.median([run_data[r]["mne_peak_error_mm"] for r in PRIMARY_RUNS])),
            "MNE_mean": float(np.mean([run_data[r]["mne_peak_error_mm"] for r in PRIMARY_RUNS]))},
        "predicted_vs_observed_pair_similarity": {
            "n_dependent_pairs": len(pair_rows), "sites": len(PRIMARY_RUNS),
            "pearson_r": pearson, "spearman_rho": spearman,
            "interpretation": "descriptive only; pairwise comparisons share sites and are not independent; no p-value or generalization claim"},
        "pair_similarity_rows": pair_rows,
        "per_run": {str(r): {k: v for k, v in run_data[r].items()
                              if k not in {"evoked", "observed_topography"}} for r in ALL_RUNS},
        "failure_catalogue": [
            "All runs belong to one participant, so no participant-level generalization or held-out estimate is available.",
            "The contact-pair midpoint is a benchmark reference for the measured stimulation artifact; the cortical mesh projection is approximate.",
            "The fixed cortical-normal source orientation is a forward-model assumption; the contact-pair axis is only a diagnostic proxy for artifact orientation.",
            "Peak-localization error depends on the fixed −2 to +2 ms window and fixed inverse settings; this run is not a parameter sweep.",
            "Pulse artifacts are not physiological source maps; performance cannot be transferred to spontaneous or distributed neural activity.",
            "The pairwise similarity sample has only six sites and dependent pairs; its correlation is an exploratory description.",
            "No calibrated recoverability, forward-model uncertainty or RSG method is evaluated in Track A."],
        "provenance": {"dataset_snapshot": "d7a123d3067213281f106b343c71f28c30e4dd60",
                       "GBFs_commit": "99fc7c6e8afbd2e3e68a700c5f1fa1483b90f49e",
                       "metadata_commit": "d7a123d3067213281f106b343c71f28c30e4dd60",
                       "forward_sha256": sha256(fwd_path), "head_to_surface_sha256": sha256(transform_file),
                       "primary_epoch_sha256": {str(r): run_data[r]["epochs_sha256"] for r in PRIMARY_RUNS}},
        "limitations": ["Development-only descriptive evaluation. No participant is held out.",
                        "These estimates concern the stimulation pulse artifact only.",
                        "No RSG novelty or superiority claim is supported."]}
    out_path = OUT / "empirical_evaluation_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    with (OUT / "predicted_observed_similarity.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pair_rows[0]))
        w.writeheader(); w.writerows(pair_rows)
    error_rows_html = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in row.values()) + "</tr>"
        for row in primary_errors
    )
    similarity_rows_html = "".join(
        f"<tr><td>{html.escape(row['site_a'])}</td><td>{html.escape(row['site_b'])}</td>"
        f"<td>{row['predicted_signature_similarity']:.3f}</td>"
        f"<td>{row['observed_artifact_similarity']:.3f}</td></tr>"
        for row in pair_rows
    )
    intensity_rows_html = "".join(
        f"<tr><td>{html.escape(row['site'])}</td><td>{row['observed_1mA_vs_5mA_similarity']:.3f}</td></tr>"
        for row in intensity_pairs
    )
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Track A empirical evaluation</title><style>body{{font:16px/1.55 system-ui,Segoe UI,Arial,sans-serif;max-width:1050px;margin:32px auto;padding:0 20px;color:#182238}}h1,h2{{line-height:1.2}}.notice{{background:#fff5df;border:1px solid #e7c56f;padding:14px;border-radius:8px}}table{{border-collapse:collapse;width:100%;margin:12px 0 28px}}th,td{{border-bottom:1px solid #dbe2ed;text-align:left;padding:8px}}th{{background:#f4f7fb}}small,.muted{{color:#58667c}}code{{background:#f2f4f8;padding:2px 5px}}</style>
<body><h1>Track A: pulse-artifact localization check</h1>
<p class="notice"><b>Development-only result.</b> Six stimulation sites from one participant; the contact-pair midpoint is the benchmark reference for the short stimulation artifact. This does not validate localization of spontaneous neural activity or the post-stimulus physiological response. Settings were fixed in advance and were not tuned against these target errors.</p>
<p>We ran the pinned upstream GBFs estimator with 300 modes per hemisphere and a fixed-orientation MNE minimum-norm comparator on 224 channels shared across the selected runs. The response window was −2 to +2 ms. Each condition used the dataset's repeated trials; the site-level sample remains six, not the number of trials.</p>
<h2>Peak localization distance</h2><p>The fixed source model uses cortical-normal dipoles. Across the six primary sites, the contact-pair axis forms angles of {report["orientation_diagnostic"]["range_degrees"][0]:.1f}° to {report["orientation_diagnostic"]["range_degrees"][1]:.1f}° with the nearest modeled normal. The contact axis is only a geometry proxy, not a measurement of the artifact-current orientation, so these are model-conditional errors.</p><p>Across the six 1 mA sites, median distance from the reconstructed peak to the stimulation midpoint was <b>{report['summary_error_mm']['GBFs_median']:.1f} mm for GBFs</b> and <b>{report['summary_error_mm']['MNE_median']:.1f} mm for MNE</b>. Means were {report['summary_error_mm']['GBFs_mean']:.1f} mm and {report['summary_error_mm']['MNE_mean']:.1f} mm. These are descriptive estimates from one participant, not a method-ranking claim.</p>
<table><thead><tr><th>Stimulation site</th><th>Trials</th><th>Midpoint to cortical mesh</th><th>GBFs peak error</th><th>GBFs hemisphere</th><th>MNE peak error</th><th>MNE hemisphere</th></tr></thead><tbody>{error_rows_html}</tbody></table>
<h2>Predicted and observed scalp-pattern similarity</h2><p>For six 1 mA sites, nominal lead-field similarity and observed artifact-topography similarity had Pearson <i>r</i>={pearson:.3f} and Spearman <i>ρ</i>={spearman:.3f} across 15 dependent pairs. Pairs share the same six sites, so these coefficients are exploratory and no p-value is reported.</p>
<table><thead><tr><th>Site A</th><th>Site B</th><th>Predicted similarity</th><th>Observed artifact similarity</th></tr></thead><tbody>{similarity_rows_html}</tbody></table>
<h2>Same site at 1 mA and 5 mA</h2><p>These repeated-site comparisons illustrate current sensitivity; they are not independent sites or accuracy estimates.</p>
<table><thead><tr><th>Site</th><th>Observed similarity across currents</th></tr></thead><tbody>{intensity_rows_html}</tbody></table>
<h2>Limits</h2><ul>{''.join(f'<li>{html.escape(item)}</li>' for item in report['failure_catalogue'])}</ul>
<p class="muted">Machine-readable data and provenance: <code>empirical_evaluation_report.json</code>. Pairwise data: <code>predicted_observed_similarity.csv</code>. Dataset license: CC-BY-NC-SA 4.0.</p></body></html>"""
    html_path = OUT / "empirical_evaluation_report.html"
    html_path.write_text(page, encoding="utf-8")
    print(json.dumps({"status": report["status"], "sites": len(PRIMARY_RUNS),
                      "primary_peak_error_mm": report["summary_error_mm"],
                      "predicted_vs_observed_similarity": report["predicted_vs_observed_pair_similarity"],
                      "outputs": [str(out_path), str(html_path)]}, indent=2))


if __name__ == "__main__":
    main()
