"""Controlled-stimulation source-family validation on Localize-MI.

This is a real-data, participant-specific forward-model benchmark.  The
measured endpoint is the scalp electrical stimulation pulse artifact, and the
intracranial contact-pair midpoint is only an approximate spatial reference.
It is deliberately not a claim about endogenous neural-source recovery.

The script compares fixed-orientation point, equal-weight local-patch,
signed local-patch, and global ridge families.  Each family is scored by a
profiled whitened residual.  The 1 mA/5 mA repeated-site pairs provide a
small held-current check: the scalar amplitude is fitted on one current and
evaluated on the other.  No source-family choice is tuned using the held-out
current.
"""
from __future__ import annotations

import csv, hashlib, json
from pathlib import Path

import h5py
import mne
import numpy as np
from scipy.linalg import solve
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "data" / "Localize-MI"
PAYLOAD = ROOT / "data" / "payload"
OUT = ROOT / "outputs" / "track_b" / "localize_family_validation"
SUBJECT = "sub-01"
ALL_RUNS = list(range(1, 12))
CURRENT_PAIRS = {"K13-14": (1, 2), "N2-3": (3, 4), "S1-2": (6, 7),
                 "S3-4": (8, 9), "S5-6": (10, 11)}
WINDOW = (-0.002, 0.002)
PATCH_RADII_MM = (10.0, 20.0)


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def whiten(cov: np.ndarray):
    vals, vecs = np.linalg.eigh((cov + cov.T) / 2)
    keep = vals > 1e-10 * vals.max()
    return vecs[:, keep].T / np.sqrt(vals[keep])[:, None], int(keep.sum())


def profiled_residual(y: np.ndarray, x: np.ndarray) -> float:
    """Relative residual after fitting one unconstrained scalar amplitude."""
    den = float(np.dot(x, x))
    if den <= 0 or not np.isfinite(den):
        return float("nan")
    a = float(np.dot(x, y) / den)
    return float(np.linalg.norm(y - a * x) / max(np.linalg.norm(y), 1e-30))


def ridge_residual(y: np.ndarray, X: np.ndarray, ridge: float) -> float:
    """Relative residual for a fixed, auditable ridge coefficient."""
    # Use the sensor-space dual system for the global bank.  Forming an
    # 8,000-by-8,000 source Gram matrix is unnecessary and can dominate the
    # audit; the identity X(X'X+lambda I)^-1X' = XX'(XX'+lambda I)^-1
    # gives the same fitted sensor vector in float64 up to solver tolerance.
    gram = X @ X.T
    scale = max(float(np.trace(gram) / max(gram.shape[0], 1)), 1e-30)
    alpha = solve(gram + ridge * scale * np.eye(gram.shape[0]), y,
                  assume_a="pos", check_finite=False)
    return float(np.linalg.norm(y - gram @ alpha) / max(np.linalg.norm(y), 1e-30))


def ridge_direction(y: np.ndarray, X: np.ndarray, ridge: float) -> np.ndarray:
    """Return the fitted sensor vector using the same dual ridge rule."""
    gram = X @ X.T
    scale = max(float(np.trace(gram) / max(gram.shape[0], 1)), 1e-30)
    alpha = solve(gram + ridge * scale * np.eye(gram.shape[0]), y,
                  assume_a="pos", check_finite=False)
    return gram @ alpha


def contact_pair(label: str, xyz: dict[str, np.ndarray]):
    site = label.split()[0]
    first, num = site.split("-")
    prefix = "".join(c for c in first if not c.isdigit())
    second = prefix + num
    if first not in xyz or second not in xyz:
        raise ValueError(f"Missing contact coordinates for {label}")
    return first, second


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    metadata = {}
    common_good = None
    clock = None
    for run in ALL_RUNS:
        stem = f"{SUBJECT}_task-seegstim_run-{run:02d}"
        ep = PAYLOAD / "derivatives" / "epochs" / SUBJECT / "eeg" / f"{stem}_epochs.npy"
        chp = META / "derivatives" / "epochs" / SUBJECT / "eeg" / f"{stem}_channels.tsv"
        evp = META / "derivatives" / "epochs" / SUBJECT / "eeg" / f"{stem}_epochs.tsv"
        ch, ev = rows(chp), rows(evp)
        if not ep.is_file() or not ch or not ev:
            raise FileNotFoundError(stem)
        eeg = [r for r in ch if r["type"].upper() == "EEG"]
        if any(r["units"] != "V" for r in eeg):
            raise ValueError(f"{stem}: EEG units are not volts")
        c = (float(eeg[0]["sampling_frequency"]), float(ev[0]["zero_time"]),
             float(ev[0]["duration"]))
        if any(float(r["sampling_frequency"]) != c[0] for r in eeg):
            raise ValueError(f"{stem}: inconsistent sampling frequency")
        if clock is None:
            clock = c
        elif not np.allclose(c, clock, rtol=0, atol=1e-12):
            raise ValueError(f"{stem}: time grid differs")
        names = [r["name"] for r in ch if r["status"] == "good"]
        common_good = set(names) if common_good is None else common_good.intersection(names)
        metadata[run] = (ep, ch, ev)

    order = [r["name"] for r in metadata[1][1] if r["name"] in common_good]
    fwd_path = PAYLOAD / "derivatives" / "sourcemodelling" / SUBJECT / "fwd" / f"{SUBJECT}_fwd.fif"
    fwd = mne.read_forward_solution(fwd_path, verbose="ERROR")
    fwd = mne.pick_channels_forward(fwd, include=order, ordered=True, copy=True, verbose="ERROR")
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True, use_cps=True, verbose="ERROR")
    if fwd["sol"]["row_names"] != order:
        raise ValueError("forward model channel order mismatch")
    lead_raw = np.asarray(fwd["sol"]["data"], dtype=np.float64)
    source_head = np.vstack([s["rr"][s["vertno"]] for s in fwd["src"]])
    source_ids = np.r_[fwd["src"][0]["vertno"], fwd["src"][1]["vertno"]]
    xfm = META / "derivatives" / "sourcemodelling" / SUBJECT / "xfm" / f"{SUBJECT}_from-head_to-surface.h5"
    with h5py.File(xfm, "r") as h5:
        head_to_surface = np.asarray(h5["trans"][()], dtype=float)
    source_surface = mne.transforms.apply_trans(head_to_surface, source_head)
    contacts_path = META / "derivatives" / "epochs" / SUBJECT / "ieeg" / f"{SUBJECT}_task-seegstim_space-surface_electrodes.tsv"
    xyz = {r["name"]: np.array([float(r[a]) for a in ("x", "y", "z")]) for r in rows(contacts_path)}

    # Pooled pre-pulse covariance from the five 1 mA runs, without using the
    # artifact window or any family score.
    total = 0
    sx = np.zeros(len(order)); sxx = np.zeros((len(order), len(order)))
    run_evoked = {}
    labels = {}
    sfreq, zero, duration = clock
    for run, (ep, ch, ev) in metadata.items():
        arr = np.asarray(np.load(ep, mmap_mode="r"), dtype=np.float64)
        if arr.ndim != 3 or arr.shape[0] != len(ev) or arr.shape[1] != len(ch):
            raise ValueError(f"{run}: array/metadata shape mismatch")
        idx = [next(i for i, r in enumerate(ch) if r["name"] == name) for name in order]
        selected = arr[:, idx, :]
        times = -zero + np.arange(arr.shape[-1]) / sfreq
        base = (times >= -.20) & (times <= -.05)
        win = (times >= WINDOW[0]) & (times <= WINDOW[1])
        if run in {1, 3, 5, 6, 8, 10}:
            b = selected[:, :, base].transpose(1, 0, 2).reshape(len(order), -1)
            total += b.shape[1]; sx += b.sum(1); sxx += b @ b.T
        label_set = sorted({r["trial_type"] for r in ev})
        if len(label_set) != 1:
            raise ValueError(f"{run}: multiple labels")
        evoked = selected.mean(axis=0)
        sample = int(np.argmax(np.linalg.norm(evoked[:, win], axis=0)))
        run_evoked[run] = (evoked[:, win][:, sample], label_set[0], int(selected.shape[0]))
        labels[run] = label_set[0]

    cov = (sxx - np.outer(sx, sx) / total) / (total - 1)
    ref = np.eye(len(order)) - np.ones((len(order), len(order))) / len(order)
    lead = ref @ lead_raw
    cov = ref @ cov @ ref.T
    cov = .9 * cov + .1 * np.trace(cov) / (len(order) - 1) * ref
    W, rank = whiten(cov)
    Xall = W @ lead
    tree = cKDTree(source_surface)

    # Candidate family residuals for each measured condition.
    family_rows = []
    for run, (topo, label, ntrials) in run_evoked.items():
        c1, c2 = contact_pair(label, xyz)
        target = (xyz[c1] + xyz[c2]) / 2
        _, ti = tree.query(target)
        y = W @ (ref @ topo)
        point = Xall[:, ti]
        row = {"run": run, "label": label, "n_trials": ntrials,
               "target_vertex_id": int(source_ids[ti]),
               "target_grid_distance_mm": float(np.linalg.norm(source_surface[ti] - target) * 1000),
               "point_residual": profiled_residual(y, point)}
        for radius in PATCH_RADII_MM:
            mask = np.linalg.norm(source_surface - source_surface[ti], axis=1) <= radius / 1000
            equal = Xall[:, mask].mean(axis=1)
            row[f"uniform_patch_{int(radius)}mm_residual"] = profiled_residual(y, equal)
            row[f"signed_patch_{int(radius)}mm_residual"] = ridge_residual(y, Xall[:, mask], 1e-6)
            row[f"patch_{int(radius)}mm_vertices"] = int(mask.sum())
        row["global_ridge_residual"] = ridge_residual(y, Xall, 1e-6)
        family_rows.append(row)

    # Hold-current check: fit the scalar amplitude on 1 mA and evaluate the
    # same family direction on 5 mA for each repeated stimulation pair.
    held_rows = []
    by_label = {label: {r: run_evoked[r] for r in runs if r in run_evoked}
                for label, runs in CURRENT_PAIRS.items()}
    for label, pair in CURRENT_PAIRS.items():
        if not all(r in by_label[label] for r in pair):
            continue
        for train, test in (pair, pair[::-1]):
            train_y = W @ (ref @ by_label[label][train][0])
            test_y = W @ (ref @ by_label[label][test][0])
            c1, c2 = contact_pair(label + " 1mA", xyz)
            target = (xyz[c1] + xyz[c2]) / 2; _, ti = tree.query(target)
            cols = {"point": Xall[:, ti]}
            for radius in PATCH_RADII_MM:
                mask = np.linalg.norm(source_surface - source_surface[ti], axis=1) <= radius / 1000
                cols[f"uniform_patch_{int(radius)}mm"] = Xall[:, mask].mean(axis=1)
                # Ridge direction is fit on train and then held unchanged.
                X = Xall[:, mask]; gram = X.T @ X; scale = max(float(np.trace(gram)/max(len(mask),1)), 1e-30)
                beta = solve(gram + 1e-6*scale*np.eye(X.shape[1]), X.T @ train_y, assume_a="pos")
                cols[f"signed_patch_{int(radius)}mm"] = X @ beta
            cols["global_ridge"] = ridge_direction(train_y, Xall, 1e-6)
            for fam, direction in cols.items():
                held_rows.append({"label": label, "train_run": train, "test_run": test,
                                  "family": fam, "test_profiled_residual": profiled_residual(test_y, direction)})

    result = {"status": "completed controlled-stimulation family-fit validation",
              "endpoint": "measured scalp electrical stimulation pulse artifact",
              "participant": SUBJECT, "runs": ALL_RUNS, "common_good_channels": len(order),
              "source_vertices": int(len(source_surface)), "noise_rank": rank,
              "patch_radii_mm": list(PATCH_RADII_MM), "family_rows": family_rows,
              "held_current_rows": held_rows,
              "provenance": {"forward_sha256": sha256(fwd_path), "transform_sha256": sha256(xfm),
                             "epoch_sha256": {str(r): sha256(metadata[r][0]) for r in ALL_RUNS}},
              "limitations": [
                  "One participant and five repeated stimulation sites; no population inference.",
                  "The endpoint is an electrical pulse artifact, not spontaneous or endogenous neural activity.",
                  "The contact midpoint is an approximate reference and fixed cortical-normal orientation may not equal artifact-current orientation.",
                  "Patch radii and ridge regularization are predeclared engineering families, not fitted physiology.",
                  "A family fit to this endpoint does not establish GBF superiority or a novel source-localization method."]}
    (OUT / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (OUT / "family_rows.csv").open("w", newline="", encoding="utf-8") as f:
        keys = list(family_rows[0]); w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(family_rows)
    with (OUT / "held_current_rows.csv").open("w", newline="", encoding="utf-8") as f:
        keys = list(held_rows[0]); w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(held_rows)
    print(json.dumps({"status": result["status"], "family_rows": len(family_rows),
                      "held_rows": len(held_rows), "output": str(OUT / "result.json")}, indent=2))


if __name__ == "__main__":
    main()
