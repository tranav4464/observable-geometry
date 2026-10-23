"""Development-case integration on recorded Localize-MI EEG, not validation.

Uses upstream GBFs functions extracted by AST to avoid unrelated demo imports.
The vendor files are unchanged. Executes participant geometric modes and the
original recorded-data inverse path; also runs the independent Gaussian core.
No source-location accuracy is asserted by this onboarding script.
"""
from pathlib import Path
import ast
import csv
import hashlib
import json
import os
import sys
import time
from types import SimpleNamespace
import numpy as np
import scipy.linalg
import mne
import lapy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from tracka_paths import OUT
from geometry_basis_cache import load_or_compute
from observable_geometry.core import average_reference, fit_linear_geometry


def main():
    start = time.perf_counter()
    out = OUT
    meta = ROOT/'data/Localize-MI'
    payload = ROOT/'data/payload'
    epbase = 'derivatives/epochs/sub-01/eeg/sub-01_task-seegstim_run-01'
    with (meta/(epbase+'_channels.tsv')).open() as stream:
        channels = list(csv.DictReader(stream, delimiter='\t'))
    with (meta/(epbase+'_epochs.tsv')).open() as stream:
        events = list(csv.DictReader(stream, delimiter='\t'))
    sfreqs = {float(row['sampling_frequency']) for row in channels}
    if len(sfreqs) != 1:
        raise ValueError('Sampling rate disagreement')
    sfreq = sfreqs.pop()
    zero_times = {float(row['zero_time']) for row in events}
    if len(zero_times) != 1:
        raise ValueError('Event time disagreement')
    tmin = -zero_times.pop()
    epochs = np.load(payload/(epbase+'_epochs.npy'), mmap_mode='r')
    if len(events) != epochs.shape[0] or len(channels) != epochs.shape[1]:
        raise ValueError('Metadata/recording dimensions disagree')
    times = tmin + np.arange(epochs.shape[2])/sfreq
    fwd = mne.read_forward_solution(payload/'derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif', verbose=False)
    good = [row['name'] for row in channels if row['status']=='good']
    fwd = mne.pick_channels_forward(fwd, include=good, ordered=True, copy=True, verbose=False)
    fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True, use_cps=True, verbose=False)
    ordered = fwd['sol']['row_names']
    ids = [next(i for i,row in enumerate(channels) if row['name']==name) for name in ordered]
    selected = np.asarray(epochs[:, ids, :])
    baseline = (times >= -.20) & (times <= -.05)
    # Development covariance: pooled pre-pulse samples with transparent 10% shrinkage.
    baseline_data = selected[:, :, baseline].transpose(1, 0, 2).reshape(len(ids), -1)
    empirical = np.cov(baseline_data)
    noise = .9*empirical + .1*np.trace(empirical)/len(ids)*np.eye(len(ids))
    baseline_degrees_of_freedom = int(baseline_data.shape[1] - 1)
    evoked = selected.mean(axis=0)
    x, lead, noise = average_reference(evoked, fwd['sol']['data'], noise)
    values, vectors = np.linalg.eigh(noise)
    keep = values > 1e-10*values.max()
    whitener = vectors[:, keep].T / np.sqrt(values[keep])[:, None]

    vendor = ROOT/'vendor/GBFs/utils/seeg_with_eeg.py'
    source = vendor.read_text(encoding='utf-8')
    wanted = {'get_tria_from_src', 'calc_eig_from_src', 'process_evoked'}
    definitions = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    if {n.name for n in definitions} != wanted:
        raise ValueError('Upstream functions changed')
    ns = {'np': np, 'mne': mne, 'lapy': lapy, 'os': os}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(vendor), 'exec'), ns)
    cache = out/'basis_20_per_hemisphere.npz'
    print('Loading or computing identity-checked 20-mode GBFs basis', flush=True)
    (el, er, pl, pr), basis_identity = load_or_compute(
        cache, payload/'derivatives/sourcemodelling/sub-01/fwd/sub-01_fwd.fif',
        vendor, fwd['src'], 20, ns['calc_eig_from_src'])
    phi = scipy.linalg.block_diag(pl, pr)
    ev = SimpleNamespace(data=x, nave=selected.shape[0])
    # Unmodified upstream real-data function; its scaling is reported separately.
    upstream_source, theta = ns['process_evoked'](ev, whitener, 1.2, el, er, pl, pr, fwd['src'], lead)
    if not np.isfinite(upstream_source).all():
        raise ValueError('Nonfinite upstream estimate')

    # Fixed-frame evoked covariance; this is an integration baseline, not calibrated.
    evoked_cov = noise/selected.shape[0]
    a = np.sqrt(selected.shape[0])*whitener @ lead @ phi
    singular = np.linalg.svd(a, compute_uv=False)
    scale = float(1/np.median(singular[singular>0])**2)
    prior = np.eye(phi.shape[1])*scale
    fit = fit_linear_geometry(x, lead, phi, evoked_cov, prior)
    np.savez_compressed(out/'recorded_estimates.npz', times=times,
        upstream_gbfs_source=upstream_source, conditional_source=fit.source_mean,
        conditional_amplitude_sd=fit.source_std, information_fractions=fit.information_fractions,
        coefficient_resolution=fit.coefficient_resolution,
        source_coordinates=np.vstack([s['rr'][s['vertno']] for s in fwd['src']]),
        geometric_eigenvalues=np.r_[el,er])
    np.savez_compressed(out/'prepared_bundle.npz', data=x, leadfield=lead, basis=phi,
                        noise_cov=evoked_cov, noise_cov_single_trial=noise, prior_cov=prior)
    metadata = {'dataset':'Localize-MI d7a123d3067213281f106b343c71f28c30e4dd60',
        'data_kind':'recorded', 'reference':'average over selected good channels, same projection on L and C',
        'channel_names':ordered, 'source_units':'forward-defined fixed dipole units; upstream output separately scaled',
        'forward_provenance':'subject-01 supplied forward, fixed cortical orientation via MNE',
        'noise_window':[-.20,-.05], 'averaging_count':selected.shape[0],
        'baseline_degrees_of_freedom':baseline_degrees_of_freedom,
        'covariance_convention':'single-trial baseline covariance is stored separately; noise_cov is scaled by nave for the conditional estimate',
        'coordinate_frame':int(fwd['src'][0]['coord_frame']),
        'prior_selection':'median nonzero singular-value scale, development convenience only'}
    (out/'prepared_bundle.json').write_text(json.dumps(metadata,indent=2), encoding='utf-8')
    report = {'status':'recorded-data development integration; NOT accuracy validation or paper reproduction',
        'subject':'sub-01','run':'run-01','trials':selected.shape[0], 'good_channels':len(ids),
        'sampling_rate_hz':sfreq,'epoch_start_s':float(times[0]),'epoch_end_s':float(times[-1]),
        'sources':phi.shape[0],'modes':phi.shape[1],'noise_rank':fit.noise_rank,
        'forward_rank':fit.forward_rank,'runtime_seconds':time.perf_counter()-start,
        'upstream_file_sha256':hashlib.sha256(vendor.read_bytes()).hexdigest(),
        'metadata':metadata,'basis_cache_identity':basis_identity,
        'limitations':['One development case only; no held-out metrics',
          '20 modes per hemisphere rather than upstream demo 300',
          'Original source transform on Localize-MI, not GBFs paper dataset replication',
          'Shrinkage and prior scaling are onboarding choices, not tuned or calibrated',
          'Contact proximity is descriptive; the bipolar stimulation pair is not exact cortical ground truth',
          'Conditional amplitude SD is not a location confidence region',
          'Evoked noise division assumes independent trials; assess covariance for inference']}
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__ == '__main__':
    main()
