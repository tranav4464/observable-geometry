"""Read-only adversarial checks of Track A; writes evidence to a separate audit folder.

This reports failures without modifying the scientific implementation or fixtures.
"""
from pathlib import Path
import contextlib
import csv
import importlib.util
import io
import json
import sys
from unittest.mock import patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from observable_geometry.nominal import nearest_distant_signatures, whitened_unit_signatures


def main():
    evidence = {}
    xyz = np.array([[0., 0, 0], [.03, 0, 0], [.06, 0, 0]])
    lead = np.array([[0., 1., 0.], [0., 0., 1.]])
    r = nearest_distant_signatures(lead, np.eye(2), xyz, top_k=1)
    evidence['null_source'] = {
        'expected': 'invalid source excluded from candidates and summaries',
        'valid_source': r['valid_source'].tolist(),
        'null_source_reported_similarity': float(r['absolute_cosine'][0, 0]),
        'reported_sources_with_alternatives': r['summary']['source_count_with_distant_alternative'],
        'status': 'FAIL' if np.isfinite(r['absolute_cosine'][0]).any() else 'PASS'}
    try:
        nearest_distant_signatures(np.array([[1., 0.], [0., 0.]]), np.eye(2), xyz[:2], top_k=1)
        evidence['single_valid_source'] = {'status': 'REVIEW', 'exception': None}
    except Exception as exc:
        evidence['single_valid_source'] = {'status': 'FAIL' if isinstance(exc, IndexError) else 'PASS',
                                           'exception': type(exc).__name__, 'message': str(exc)}
    r = nearest_distant_signatures(np.eye(3), np.eye(3),
                                   np.array([[0., 0, 0], [.001, 0, 0], [.05, 0, 0]]), top_k=2)
    missing = ~np.isfinite(r['absolute_cosine'])
    evidence['missing_candidate_ids'] = {'status': 'FAIL' if (r['candidate_indices'][missing] != -1).any() else 'PASS',
                                         'ids_for_missing_candidates': r['candidate_indices'][missing].tolist()}
    try:
        units, valid, _ = whitened_unit_signatures(np.array([[1., 1.], [0., 100.]]), np.diag([1., 0.]))
        evidence['unsupported_covariance_direction'] = {'status': 'FAIL',
            'description': 'Unsupported nonzero leadfield component silently discarded; two different columns become identical.',
            'resulting_units': units.tolist(), 'valid_flags': valid.tolist()}
    except ValueError:
        evidence['unsupported_covariance_direction'] = {'status': 'PASS'}

    out = ROOT / 'outputs/localize_sub01_run01'
    with np.load(out / 'prepared_bundle.npz', allow_pickle=False) as z:
        lead, cov = z['leadfield'], z['noise_cov']
    with np.load(out / 'nominal_signature_library.npz', allow_pickle=False) as z:
        coords, stored_ids, stored_cos = z['source_coordinates'], z['candidate_indices'], z['absolute_cosine']
    vals, vecs = np.linalg.eigh(cov)
    keep = vals > 1e-10 * vals.max()
    white = (vecs[:, keep].T @ lead) / np.sqrt(vals[keep, None])
    white /= np.linalg.norm(white, axis=0)
    checks = []
    threshold_counts = []
    for i in np.random.default_rng(42).choice(lead.shape[1], 24, replace=False):
        sims = abs(white[:, i] @ white)
        allowed = np.linalg.norm(coords - coords[i], axis=1) >= .020
        allowed[i] = False
        sims[~allowed] = -np.inf
        expected = np.argsort(-sims)[:5]
        checks.append(bool(np.array_equal(expected, stored_ids[i]) and np.allclose(sims[expected], stored_cos[i], atol=1e-6)))
        threshold_counts.append(int((sims >= .95).sum()))
    evidence['stored_library_independent_sample'] = {'status': 'PASS' if all(checks) else 'FAIL',
        'sampled_sources': len(checks), 'max_number_of_ge_095_alternatives_in_sample': max(threshold_counts),
        'stored_alternatives_per_source': 5}
    set_checks = []
    for i in np.argsort(-stored_cos[:, 0])[:3]:
        sims = abs(white[:, i] @ white)
        sims[np.linalg.norm(coords - coords[i], axis=1) < .020] = -np.inf
        set_checks.append({'source_index': int(i), 'alternatives_ge_095': int((sims >= .95).sum()),
                           'stored_alternatives': 5})
    evidence['threshold_set_truncation'] = set_checks
    evidence['basis_penalty_domains'] = {}
    for modes in (20, 300):
        with np.load(out / f'basis_{modes}_per_hemisphere.npz', allow_pickle=False) as z:
            ev = np.r_[z['el'][1:], z['er'][1:]]
            evidence['basis_penalty_domains'][str(modes)] = {
                'positive_penalties': bool(np.all(-1 / np.log(ev) > 0)),
                'min_nonconstant_eigenvalue': float(ev.min()), 'max_eigenvalue': float(ev.max()),
                'cache_fields': z.files}
    metadata_checks = []
    for run in range(1, 12):
        stem = f'sub-01_task-seegstim_run-{run:02d}'
        base = ROOT / 'data/Localize-MI/derivatives/epochs/sub-01/eeg'
        with (base / (stem + '_channels.tsv')).open() as f:
            ch = list(csv.DictReader(f, delimiter='\t'))
        with (base / (stem + '_epochs.tsv')).open() as f:
            events = list(csv.DictReader(f, delimiter='\t'))
        a = np.load(ROOT / 'data/payload/derivatives/epochs/sub-01/eeg' / (stem + '_epochs.npy'), mmap_mode='r')
        metadata_checks.append({'run': run, 'shape': list(a.shape),
            'dimensions_match_metadata': a.shape[:2] == (len(events), len(ch)),
            'sample_rates': sorted({r['sampling_frequency'] for r in ch}),
            'units': sorted({r['units'] for r in ch}), 'zero_times': sorted({r['zero_time'] for r in events}),
            'finite': all(bool(np.isfinite(a[i]).all()) for i in range(len(a)))})
    evidence['actual_metadata_and_finiteness'] = metadata_checks

    spec = importlib.util.spec_from_file_location('audited_validator', ROOT / 'scripts/verify_foundation.py')
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    original_loads = json.loads
    def altered_loads(text, *args, **kwargs):
        data = original_loads(text, *args, **kwargs)
        if isinstance(data, dict) and 'localization_errors' in data:
            data['localization_errors'][0]['GBFs_peak_error_mm'] = float('nan')
        return data
    try:
        with patch.object(validator.json, 'loads', side_effect=altered_loads), contextlib.redirect_stdout(io.StringIO()):
            validator.main()
        evidence['validator_rejects_nonfinite_site_error'] = {'status': 'FAIL',
            'description': 'Validator accepted an in-memory empirical report with NaN in the first site error; no files changed.'}
    except (SystemExit, ValueError):
        evidence['validator_rejects_nonfinite_site_error'] = {'status': 'PASS'}
    audit = ROOT / 'outputs/audit_2026_10_22'
    audit.mkdir(parents=True, exist_ok=True)
    (audit / 'adversarial_checks.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in evidence.items() if k != 'actual_metadata_and_finiteness'}, indent=2))
    print('Actual recording metadata/finite checks:', len(metadata_checks), 'runs')


if __name__ == '__main__':
    main()
