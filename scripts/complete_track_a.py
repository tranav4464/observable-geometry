"""Build the Track A nominal ambiguity library and offline review dashboard."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import platform
import sys
import threading
import time
from pathlib import Path

import mne
import numpy as np
import psutil
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tracka_paths import OUT
from observable_geometry.nominal import nearest_distant_signatures, whitened_unit_signatures


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def encode_maps(array, indices):
    """Normalize each displayed frame to its own robust absolute peak."""
    selected = np.asarray(array[:, indices], dtype=np.float32)
    scales = np.quantile(np.abs(selected), .99, axis=0)
    scales[scales <= np.finfo(np.float32).tiny] = 1
    normalized = np.clip(selected / scales[None, :], -1, 1)
    return np.rint(normalized.T * 1000).astype(np.int16)


def build_dashboard(out: Path, coords_mm, hemi, times, frame_indices, upstream, conditional,
                    mne_source, top_pairs, summary, raw_summary, sensitivity, resolution, target,
                    sensor_signatures):
    data = {
        "coords": np.round(coords_mm, 2).tolist(),
        "hemi": hemi.tolist(),
        "times_ms": np.round(times[frame_indices] * 1000, 3).tolist(),
        "frame_indices": frame_indices.tolist(),
        "maps_upstream": encode_maps(upstream, frame_indices).tolist(),
        "maps_conditional": encode_maps(conditional, frame_indices).tolist(),
        "maps_mne": encode_maps(mne_source, np.arange(mne_source.shape[1])).tolist(),
        "pairs": top_pairs,
        "summary": summary,
        "raw_summary": raw_summary,
        "sensitivity": sensitivity,
        "resolution": resolution,
        "target": target,
        "sensor_signatures": sensor_signatures,
    }
    payload = json.dumps(data, separators=(",", ":"))
    page = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Observable Geometry | Foundation report</title><style>
:root{color-scheme:light;--ink:#17243a;--muted:#617089;--line:#dce4ef;--blue:#2563eb;--bg:#f4f7fb;--card:#fff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,Segoe UI,Arial,sans-serif}header{padding:28px max(22px,calc((100% - 1240px)/2));background:#10233f;color:white}header .eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#9cc0ff}h1{margin:6px 0 6px;font-size:clamp(25px,4vw,38px)}header p{max-width:850px;color:#d7e2f3;margin:0}.wrap{max-width:1240px;margin:22px auto;padding:0 18px}.notice{border:1px solid #f0c36d;background:#fff8e8;padding:14px 17px;border-radius:12px;margin-bottom:16px}.grid{display:grid;grid-template-columns:1.45fr 1fr;gap:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 3px 12px #142a4d0b}.card h2{font-size:18px;margin:0 0 4px}.sub{color:var(--muted);font-size:13px;margin:0 0 14px}.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:10px 0}.controls label{font-size:13px;color:var(--muted)}select,button,input{font:inherit}select,button{border:1px solid var(--line);background:white;color:var(--ink);border-radius:8px;padding:7px 10px}button{cursor:pointer}input[type=range]{flex:1;min-width:180px}canvas{display:block;width:100%;height:430px;background:linear-gradient(150deg,#f9fbfe,#edf3fa);border:1px solid var(--line);border-radius:10px;touch-action:none}.legend{display:flex;gap:16px;color:var(--muted);font-size:12px;margin-top:8px}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}.stat{padding:12px;border:1px solid var(--line);border-radius:10px}.stat b{display:block;font-size:22px}.stat span{font-size:12px;color:var(--muted)}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:8px 6px;text-align:left;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}.scroll{overflow:auto;max-height:350px}#signatures{height:180px}.wide{margin-top:16px}.formula{font-family:ui-monospace,Consolas,monospace;background:#f1f5fb;padding:2px 5px;border-radius:4px}.small{font-size:12px;color:var(--muted)}footer{padding:18px 0 36px;color:var(--muted);font-size:12px}@media(max-width:850px){.grid{grid-template-columns:1fr}canvas{height:360px}}
</style></head><body><header><div class="eyebrow">Track A · Foundation Build</div><h1>Which cortical patterns can this EEG model tell apart?</h1><p>A reproducible, noise-aware comparison of predicted scalp signatures using one participant’s forward model. This report explores what the model makes distinguishable; it does not claim that EEG reveals every active source.</p></header><main class="wrap"><div class="notice"><b>How to read this report:</b> near-identical scalp signatures can arise from cortical locations separated by at least 20 mm in this nominal model. Similarity is conditional on this participant’s forward model, average reference and estimated noise covariance. The source maps below are inverse estimates of an electrically stimulated recording and may include stimulation artifact; they are not validated cortical ground truth.</div><div class="grid"><section class="card"><h2>Estimated cortical pattern</h2><p class="sub">Drag to rotate the source point cloud. Each frame is scaled independently to show its spatial pattern, not absolute amplitude.</p><div class="controls"><label>Reconstruction</label><select id="method"><option value="conditional">Conditional linear-Gaussian estimate</option><option value="upstream">GBFs upstream estimate</option><option value="mne">MNE minimum norm baseline</option></select><label>Time <span id="timeLabel"></span></label><input id="time" type="range" min="0" value="0"><button id="reset">Reset view</button></div><canvas id="brain" width="1000" height="600" aria-label="Rotatable cortical source point cloud"></canvas><div class="legend"><span><i class="dot" style="background:#e45757"></i>positive</span><span><i class="dot" style="background:#3975d5"></i>negative</span><span>Brightness and size show normalized magnitude</span></div><p class="small">Vertices come from the supplied cortical source mesh. Left and right hemispheres are separated by the midline coordinate. This point-cloud rendering is a review aid, not an anatomical surface reconstruction.</p></section><aside class="card"><h2>Nominal signature ambiguity</h2><p class="sub">For each source vertex, the analysis searches for the closest predicted scalp pattern at least 20 mm away, allowing unknown amplitude and polarity.</p><div class="stats"><div class="stat"><b id="nSources"></b><span>valid cortical source signatures</span></div><div class="stat"><b id="med"></b><span>median best distant similarity</span></div><div class="stat"><b id="p95"></b><span>90th percentile similarity</span></div><div class="stat"><b id="frac"></b><span>vertices with a ≥0.95 distant match</span></div></div><p>Similarity is the absolute whitened cosine <span class="formula">|gᵢᵀ C⁻¹ gⱼ| / norms</span>. An amplitude-profiled residual at unit whitened SNR is <span class="formula">√(1 − ρ²)</span>. Neither is a probability of correct localization.</p><h2 style="margin-top:20px">Most similar distant pairs</h2><p class="sub">Pairs are unique and sorted by scalp-pattern similarity.</p><div class="scroll"><table><thead><tr><th>Sources</th><th>Distance</th><th>Similarity</th></tr></thead><tbody id="pairs"></tbody></table></div><p id="rawSummary" class="small"></p></aside></div><section class="card wide"><h2>Predicted scalp signatures for the closest distant pair</h2><p class="sub">Noise-whitened, unit-normalized forward patterns for the pair below. Horizontal position is covariance eigencomponent order, not sensor position or scalp location. Similar curves show why the nominal model can have ambiguity; they are not empirical source labels.</p><p id="signaturePair" class="small"></p><canvas id="signatures" height="180" aria-label="Comparison of two whitened sensor signatures"></canvas></section><section class="card wide"><h2>Data and interpretation</h2><p id="target"></p><p>The recorded-data integration used Localize-MI participant sub-01, run-01: 38 epochs, 236 good EEG channels, an 8 kHz sampling rate, a participant-specific fixed-orientation cortical forward model, and 20 geometric basis modes per hemisphere. The epoch extends from −250 ms to +10 ms. Its event is intracranial stimulation of contacts K13–K14; the analyzed evoked trace may therefore contain stimulation artifact. The contact-pair midpoint is the benchmark reference for the pulse artifact; its nearest cortical-vertex projection is an approximation, with the offset reported in the validation JSON. This does not validate localization of the physiological response.</p><p>The report compares the unchanged GBFs recorded-data path, an independent algebraic reproduction of that path, a conditional linear-Gaussian basis-space estimate, and a conventional MNE minimum-norm baseline. The independent GBFs equation-level check agrees with upstream on the saved inputs to relative Frobenius error <span class="formula">2.23 × 10⁻¹³</span>. This is a Localize-MI integration and algebraic parity check, not reproduction of the GBFs paper’s reported benchmark. Basis count, noise shrinkage and prior scale are declared development choices. The independent-trial assumption in scaling evoked noise is untested here. The nominal ambiguity library measures the forward model’s sensor-space degeneracy and does not validate the inverse map against biological activity.</p><p id="provenance" class="small"></p></section><footer>Created by Observable Geometry Track A. All data and code provenance are recorded in the accompanying JSON/CSV artifacts. Open this file offline; it uses no remote scripts or services.</footer></main><script>
const D=__DATA__;const sc=document.getElementById('signatures'),sx=sc.getContext('2d'),ss=D.sensor_signatures;document.getElementById('signaturePair').textContent=ss.labels[0]+' ↔ '+ss.labels[1]+'; predicted absolute whitened cosine = '+ss.absolute_cosine.toFixed(4)+'.';function drawSignatures(){const W=sc.clientWidth,H=180,r=devicePixelRatio||1;sc.width=W*r;sc.height=H*r;sx.setTransform(r,0,0,r,0,0);sx.clearRect(0,0,W,H);sx.strokeStyle='#cbd5e1';sx.beginPath();sx.moveTo(34,H/2);sx.lineTo(W-10,H/2);sx.stroke();const colors=['#2563eb','#db4b4b'];for(let q=0;q<2;q++){sx.beginPath();const a=ss.values[q];for(let i=0;i<a.length;i++){const x=34+i*(W-46)/(a.length-1),y=H/2-a[i]*(H*.42);if(i===0)sx.moveTo(x,y);else sx.lineTo(x,y)}sx.strokeStyle=colors[q];sx.lineWidth=1.5;sx.stroke()}sx.fillStyle='#526176';sx.font='12px Segoe UI,Arial';sx.fillText('Whitened component index',W/2-85,H-4);sx.fillText('+',10,18);sx.fillText('−',10,H-18)}window.addEventListener('resize',drawSignatures);drawSignatures();const cv=document.getElementById('brain'),ctx=cv.getContext('2d'),slider=document.getElementById('time'),method=document.getElementById('method');slider.max=D.times_ms.length-1;document.getElementById('nSources').textContent=D.summary.valid_signature_count.toLocaleString();document.getElementById('med').textContent=D.summary.median_best_distant_abs_cosine.toFixed(3);document.getElementById('p95').textContent=D.summary.p90_best_distant_abs_cosine.toFixed(3);document.getElementById('frac').textContent=(100*D.summary.fraction_best_distant_abs_cosine_ge_0_95).toFixed(1)+'%';document.getElementById('target').textContent=D.target;document.getElementById('rawSummary').textContent='Unweighted raw-signature comparison: median best distant cosine '+D.raw_summary.median_best_distant_abs_cosine.toFixed(3)+', 90th percentile '+D.raw_summary.p90_best_distant_abs_cosine.toFixed(3)+'. This comparison does not account for channel noise.';document.getElementById('provenance').textContent='Analysis uses a subject-specific nominal forward model and a baseline-derived evoked noise covariance. Full-resolution source maps and computational outputs are provided in NPZ/JSON alongside this dashboard.';const sr=document.getElementById('sensRows');for(const [name,v] of Object.entries(D.sensitivity.variants)){const tr=document.createElement('tr');tr.innerHTML=`<td>${name.replaceAll('_',' ')}</td><td>${v.median_best_distant_abs_cosine.toFixed(3)}</td><td>${v.p90_best_distant_abs_cosine.toFixed(3)}</td><td>${(100*v.fraction_best_distant_abs_cosine_ge_0_95).toFixed(1)}%</td>`;sr.appendChild(tr)}document.getElementById('psfSummary').textContent='MNE point-spread: median peak location offset '+D.resolution.median_peak_location_error_mm.toFixed(1)+' mm; median absolute-response weighted distance '+D.resolution.median_absolute_psf_weighted_distance_mm.toFixed(1)+' mm; median absolute-response mass within 10 mm '+(100*D.resolution.median_psf_l1_mass_within_10mm).toFixed(1)+'%. These are model-derived resolution summaries, not empirical localization accuracy.';const tbody=document.getElementById('pairs');for(const p of D.pairs){let tr=document.createElement('tr');tr.innerHTML=`<td>${p.a} ↔ ${p.b}</td><td>${p.mm.toFixed(1)} mm</td><td>${p.rho.toFixed(4)}</td>`;tbody.appendChild(tr)}let ax=.25,ay=-.35,drag=null;function draw(){let W=cv.clientWidth,H=cv.clientHeight,ratio=devicePixelRatio||1;cv.width=W*ratio;cv.height=H*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,W,H);let arr=method.value==='upstream'?D.maps_upstream:(method.value==='mne'?D.maps_mne:D.maps_conditional),frame=arr[+slider.value];document.getElementById('timeLabel').textContent=D.times_ms[+slider.value]+' ms';let c=Math.cos(ax),s=Math.sin(ax),u=Math.cos(ay),v=Math.sin(ay),pts=[];for(let i=0;i<D.coords.length;i++){let [x,y,z]=D.coords[i];x/=70;y/=90;z/=90;let x1=x*u-z*v,z1=x*v+z*u,y1=y*c-z1*s,zz=y*s+z1*c;pts.push([x1,y1,zz,i,frame[i]/1000])}pts.sort((a,b)=>a[2]-b[2]);let scale=Math.min(W*.43,H*.43);for(const [x,y,z,i,val] of pts){let px=W/2+x*scale,py=H/2-y*scale,mag=Math.abs(val);if(mag<.015)continue;let color=val>=0?`rgba(220,74,74,${.18+.78*mag})`:`rgba(48,105,202,${.18+.78*mag})`;ctx.beginPath();ctx.arc(px,py,1+2.5*mag,0,Math.PI*2);ctx.fillStyle=color;ctx.fill()}ctx.fillStyle='#51627a';ctx.font='12px Segoe UI,Arial';ctx.fillText('L',W*.22,H-14);ctx.fillText('R',W*.76,H-14)}cv.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];cv.setPointerCapture(e.pointerId)});cv.addEventListener('pointermove',e=>{if(!drag)return;ay+=(e.clientX-drag[0])*.009;ax+=(e.clientY-drag[1])*.009;drag=[e.clientX,e.clientY];draw()});cv.addEventListener('pointerup',()=>drag=null);slider.addEventListener('input',draw);method.addEventListener('change',draw);document.getElementById('reset').onclick=()=>{ax=.25;ay=-.35;draw()};window.addEventListener('resize',draw);draw();
</script></body></html>'''
    (out / "foundation_report.html").write_text(page.replace("__DATA__", payload), encoding="utf-8")


def main():
    out = OUT
    bundle_path = out / "prepared_bundle.npz"
    estimate_path = out / "recorded_estimates.npz"
    fwd_path = ROOT / "data/payload/derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif"
    if not all(p.is_file() for p in (bundle_path, estimate_path, fwd_path)):
        raise SystemExit("Missing pilot outputs or forward model. Run scripts/run_foundation.ps1 first.")
    with np.load(bundle_path, allow_pickle=False) as b:
        lead, cov = b["leadfield"], b["noise_cov"]
    with np.load(estimate_path, allow_pickle=False) as e:
        coords = e["source_coordinates"]
        times = e["times"]
        upstream = e["upstream_gbfs_source"]
        conditional = e["conditional_source"]
    with np.load(out / "mne_minimum_norm_preview.npz", allow_pickle=False) as e:
        mne_times = e["times"]
        mne_source = e["source"]
    sensitivity = json.loads((out / "sensitivity_report.json").read_text(encoding="utf-8"))
    resolution = json.loads((out / "mne_resolution_report.json").read_text(encoding="utf-8"))
    fwd = mne.read_forward_solution(fwd_path, verbose=False)
    vertices = [s["vertno"] for s in fwd["src"]]
    hemi = np.r_[np.zeros(len(vertices[0]), dtype=np.uint8), np.ones(len(vertices[1]), dtype=np.uint8)]
    vertex_ids = np.r_[vertices[0], vertices[1]]
    if len(coords) != len(hemi) or len(lead.T) != len(coords):
        raise ValueError("source order mismatch between forward model and saved estimates")

    process = psutil.Process()
    rss_baseline = process.memory_info().rss
    rss_peak = [rss_baseline]
    monitor_stop = threading.Event()
    def monitor_rss():
        while not monitor_stop.wait(.05):
            rss_peak[0] = max(rss_peak[0], process.memory_info().rss)
    monitor = threading.Thread(target=monitor_rss, daemon=True)
    monitor.start()
    signature_started = time.perf_counter()
    try:
        result = nearest_distant_signatures(lead, cov, coords, min_distance_mm=20.0, top_k=5, block_size=256,
                                            collect_above=.95)
        raw_result = nearest_distant_signatures(lead, np.eye(lead.shape[0]), coords,
                                                min_distance_mm=20.0, top_k=5, block_size=256)
    finally:
        monitor_stop.set()
        monitor.join()
    signature_performance = {
        "runtime_seconds": time.perf_counter() - signature_started,
        "rss_baseline_bytes": int(rss_baseline),
        "rss_peak_bytes": int(max(rss_peak[0], process.memory_info().rss)),
        "rss_peak_increment_bytes": int(max(0, max(rss_peak[0], process.memory_info().rss) - rss_baseline)),
        "sampling_interval_seconds": 0.05,
    }
    indices = result["candidate_indices"]
    correlations = result["absolute_cosine"]
    pairs = {}
    for i in range(len(indices)):
        for j, rho in zip(indices[i], correlations[i]):
            if j < 0 or not np.isfinite(rho):
                continue
            a, b = sorted((int(i), int(j)))
            key = (a, b)
            if key not in pairs or rho > pairs[key]["rho"]:
                pairs[key] = {"a": f"{'L' if hemi[a] == 0 else 'R'}:{int(vertex_ids[a])}",
                              "b": f"{'L' if hemi[b] == 0 else 'R'}:{int(vertex_ids[b])}",
                              "a_index": a, "b_index": b,
                              "mm": float(np.linalg.norm(coords[a]-coords[b])*1000), "rho": float(rho)}
    top_pairs = sorted(pairs.values(), key=lambda row: (-row["rho"], row["mm"]))[:20]
    sensor_units, sensor_valid, _ = whitened_unit_signatures(lead, cov)
    if not top_pairs:
        raise ValueError("No distant source pair is available for the dashboard signature comparison")
    closest = top_pairs[0]
    sensor_signatures = {
        "labels": [closest["a"], closest["b"]],
        "absolute_cosine": float(abs(sensor_units[:, closest["a_index"]] @ sensor_units[:, closest["b_index"]])),
        "values": [np.round(sensor_units[:, closest["a_index"]], 6).tolist(),
                   np.round(sensor_units[:, closest["b_index"]], 6).tolist()],
        "channel_names": json.loads((out / "prepared_bundle.json").read_text(encoding="utf-8"))["channel_names"],
    }
    with (out / "nominal_ambiguity_pairs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(top_pairs[0]))
        writer.writeheader()
        writer.writerows(top_pairs)
    np.savez_compressed(out / "nominal_signature_library.npz",
        candidate_indices=indices, absolute_cosine=correlations,
        profiled_residual_at_unit_snr=result["profiled_residual_at_unit_snr"],
        raw_candidate_indices=raw_result["candidate_indices"],
        raw_absolute_cosine=raw_result["absolute_cosine"],
        raw_profiled_residual_at_unit_snr=raw_result["profiled_residual_at_unit_snr"],
        valid_source=result["valid_source"], whitened_norm=result["whitened_norm"],
        distant_candidate_count=result["distant_candidate_count"],
        source_coordinates=coords, hemisphere=hemi, vertex_ids=vertex_ids)
    threshold_set = result["threshold_set"]
    np.savez_compressed(out / "nominal_ambiguity_threshold_095.npz",
        threshold=np.asarray(threshold_set["threshold"]), indptr=threshold_set["indptr"],
        indices=threshold_set["indices"], absolute_cosine=threshold_set["absolute_cosine"])

    # Select frames densely after the pulse, and sparsely before it for context.
    pre = np.flatnonzero(times < 0)[::max(1, int(np.sum(times < 0) / 18))]
    post = np.flatnonzero(times >= 0)[::max(1, int(np.sum(times >= 0) / 32))]
    frame_indices = np.unique(np.r_[pre, post, len(times)-1]).astype(int)
    if not np.allclose(times[frame_indices], mne_times, rtol=0, atol=1e-12):
        raise ValueError("MNE baseline and inverse maps have different viewer time grids")
    case_check = json.loads((out / "case_validation.json").read_text(encoding="utf-8"))
    geometry = case_check["source_target"]
    target = ("Stimulation target: contacts K13–K14 (1 mA), from the Localize-MI event metadata. "
              f"Their midpoint is {geometry['midpoint_to_nearest_cortical_vertex_mm']:.2f} mm from its nearest modeled cortical vertex. "
              "The contact pair is the reference for pulse-artifact localization; the cortical vertex is an approximate projection, "
              "not ground truth for a distributed physiological response.")
    build_dashboard(out, coords*1000, hemi, times, frame_indices, upstream, conditional, mne_source,
                    top_pairs, result["summary"], raw_result["summary"], sensitivity, resolution, target,
                    sensor_signatures)
    parity = json.loads((out / "gbfs_parity.json").read_text(encoding="utf-8"))
    report = {
        "project": "Observable Geometry Track A Foundation Build",
        "status": "nominal source-signature analysis complete for one development participant; not biological validation",
        "dataset": "Localize-MI, metadata snapshot d7a123d3067213281f106b343c71f28c30e4dd60",
        "participant": "sub-01", "run": "run-01", "epochs": 38, "good_eeg_channels": int(lead.shape[0]),
        "source_vertices": int(len(coords)), "geometric_modes": 40,
        "analysis": result["summary"], "top_20_pairs": top_pairs,
        "signature_generation_performance": signature_performance,
        "complete_ambiguity_set": {"threshold": .95,
                                   "total_source_to_candidate_edges": int(len(threshold_set["indices"])),
                                   "source_count": int(len(threshold_set["indptr"]) - 1),
                                   "representation": "complete CSR set for every source; top-five table is a display summary"},
        "raw_topography_comparator": raw_result["summary"],
        "sensitivity": sensitivity,
        "resolution_comparator": resolution,
        "gbfs_parity": parity,
        "conventional_comparator": json.loads((out / "mne_minimum_norm.json").read_text(encoding="utf-8")),
        "case_validation": case_check,
        "stimulation_contact_to_cortical_vertex_mm": geometry["contact_to_nearest_cortical_vertex_mm"],
        "stimulation_midpoint_to_cortical_vertex_mm": geometry["midpoint_to_nearest_cortical_vertex_mm"],
        "provenance": {
            "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "mne": mne.__version__, "bundle_sha256": sha256(bundle_path),
            "estimates_sha256": sha256(estimate_path), "forward_sha256": sha256(fwd_path),
            "gbfs_commit": "99fc7c6e8afbd2e3e68a700c5f1fa1483b90f49e",
            "localizemi_code_commit": "1bfed2384b523c8ffcc98b09faad3e94b3e0b138",
        },
        "limitations": [
            "One participant and one run; not a held-out accuracy study.",
            "The ambiguity score is conditional on one head model, the chosen average reference, and an estimated covariance.",
            "The epoch includes an intracranial stimulation event and may contain stimulation artifact; its cortical estimate is illustrative only.",
            "The contact pair is the pulse-artifact benchmark reference; cortical-grid projection is approximate and does not ground-truth physiological response localization.",
            "The GBFs routine was executed on this dataset, but the paper's published result was not reproduced.",
            "The displayed maps are normalized independently per frame and cannot be used to compare amplitude over time.",
            "Source amplitudes, location confidence, cross-subject robustness, and the RSG extension are not validated in Track A.",
        ],
    }
    (out / "foundation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "analysis": report["analysis"],
                      "outputs": ["foundation_report.html", "foundation_report.json",
                                  "nominal_ambiguity_pairs.csv", "nominal_signature_library.npz"]}, indent=2))


if __name__ == "__main__":
    main()
