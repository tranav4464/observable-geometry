import pathlib, hashlib, json, zipfile
import numpy as np
import scipy.linalg as la
from scipy.spatial.distance import cdist
root=pathlib.Path(__file__).resolve().parent
repo=root.parents[2]
inputs=repo/'outputs/track_b/20261029T_atomic_cli_real_model_reproduction/model_export'
run=root/'model_replay'
reference=repo/'outputs/track_b/20261030T_commit_release_58570b8/candidate_cli'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
expected={'model_bundle.npz':'e4116465c9af32ddf4bf9e0d3a8e92428c6f1b0bce22a5db257b1c3eaf07a32f','model_metadata.json':'a4d52521ddb760114ba1ce740942bc3bb6232f919de62737d345beb7c48db865'}
for n,h in expected.items():checks['input:'+n]=sha(inputs/n)==h
allowed={'leadfield','noise_covariance','coordinates_m','source_ids'}
with np.load(inputs/'model_bundle.npz',allow_pickle=False) as b:
    assert set(b.files)==allowed
    g=b['leadfield']; c=b['noise_covariance']; xyz=b['coordinates_m']; ids=b['source_ids']
with np.load(run/'scores.npz',allow_pickle=False) as f: scores={k:f[k] for k in f.files}
with np.load(reference/'scores.npz',allow_pickle=False) as ref:
    checks['score_keys']=set(ref.files)==set(scores)
    for k,v in scores.items():checks['reference_array:'+k]=np.array_equal(v,ref[k],equal_nan=True) if v.dtype.kind in 'fc' else np.array_equal(v,ref[k])
checks['csv_exact_reference']=(run/'ranked_pairs.csv').read_bytes()==(reference/'ranked_pairs.csv').read_bytes()
checks['csv_pinned_hash']=sha(run/'ranked_pairs.csv')=='847d248a5155818d234436a6e874ad8d5c2cf30aee1015b00053754e8359bab4'
checks['summary_exact']=json.loads((run/'summary.json').read_text())==json.loads((reference/'summary.json').read_text())
manifest=json.loads((run/'run_manifest.json').read_text())
for name,h in manifest['output_sha256'].items():checks['output_hash:'+name]=sha(run/name)==h
checks['input_manifest']=manifest['input_sha256']=={'bundle':expected['model_bundle.npz'],'metadata':expected['model_metadata.json']}
log=[json.loads(s) for s in (run/'npz_key_access.jsonl').read_text().splitlines()]
checks['access_allowlist']=len(log)==4 and {x['key'] for x in log}==allowed and all(x['decision']=='allow' for x in log)
rows=sum(1 for _ in (run/'ranked_pairs.csv').open())-1
checks['40980_rows']=rows==40980
# Independently recompute with SciPy eigensolver (evd), cdist and stable sorting.
# No project numerical functions or stored scores are used to form predictions.
eig,u=la.eigh((c+c.T)/2,driver='evd')
keep=eig>1e-10*np.max(np.abs(eig))
z=(u[:,keep].T@g)/np.sqrt(eig[keep,None])
norm=np.sqrt(np.einsum('ij,ij->j',z,z)); valid=norm>1e-10*norm.max()
unit=z/norm
n=g.shape[1]; ranking=np.full((n,5),-1,dtype=np.int64); counts=np.zeros(n,dtype=np.int64); values=np.full((n,5),np.nan)
for start in range(0,n,257):
    end=min(start+257,n)
    sim=np.minimum(1,np.abs(unit[:,start:end].T@unit))
    eligible=(cdist(xyz[start:end],xyz)>=0.020)&valid[None,:]&valid[start:end,None]
    eligible[np.arange(end-start),np.arange(start,end)]=False
    counts[start:end]=eligible.sum(axis=1)
    sim[~eligible]=-np.inf
    order=np.argsort(-sim,axis=1,kind='stable')[:,:5]
    ranking[start:end]=order
    values[start:end]=np.take_along_axis(sim,order,axis=1)
checks['independent_ranking_exact']=np.array_equal(ranking,scores['candidate_indices'])
checks['independent_counts_exact']=np.array_equal(counts,scores['candidate_count'])
checks['independent_valid_exact']=np.array_equal(valid,scores['valid_source'])
checks['independent_rank_235']=int(keep.sum())==235
checks['independent_scores']=np.allclose(values,scores['absolute_cosine'],rtol=0,atol=1e-10)
checks['independent_norms']=np.allclose(norm,scores['whitened_norm'],rtol=1e-10,atol=0)
resid=np.sqrt(np.maximum(0,1-values**2))
checks['independent_residuals']=np.allclose(resid,scores['profiled_residual'],rtol=0,atol=1e-9)
report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'ranked_pair_count':rows,'max_independent_score_error':float(np.max(np.abs(values-scores['absolute_cosine']))),'max_independent_residual_error':float(np.max(np.abs(resid-scores['profiled_residual']))),'input_sha256':expected,'output_sha256':{p.name:sha(p) for p in run.iterdir() if p.is_file()},'scope':'Fresh installed-wheel execution and separately implemented full-ranking numerical check; same host and supplied model inputs. No original recording or original forward-model construction replay.'}
(root/'replay_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2)); assert all(checks.values())
