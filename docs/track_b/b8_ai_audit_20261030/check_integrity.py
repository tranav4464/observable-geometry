import base64, csv, hashlib, io, json, pathlib, sys, zipfile, importlib.metadata as md
root=pathlib.Path(__file__).resolve().parent
packet=root/'packet'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
manifest=json.loads((packet/'EVIDENCE_MANIFEST.json').read_text())
for name,record in manifest['files'].items():
    p=packet/name
    checks['manifest:'+name]=sha(p)==record['sha256'] and p.stat().st_size==record['size_bytes']
with zipfile.ZipFile(root/'pinned_source.zip') as git, zipfile.ZipFile(packet/'source/observable_geometry_source_58570b8.zip') as src:
    names={n for n in git.namelist() if not n.endswith('/')}
    checks['source_archive_matches_git_tree']=names=={n for n in src.namelist() if not n.endswith('/')} and all(git.read(n)==src.read(n) for n in names)
wheel=packet/'wheel/observable_geometry-0.1.3.dev0-py3-none-any.whl'
with zipfile.ZipFile(wheel) as z:
    checks['wheel_crc']=z.testzip() is None
    record=next(n for n in z.namelist() if n.endswith('.dist-info/RECORD'))
    for name,digest,size in csv.reader(io.StringIO(z.read(record).decode())):
        if digest:
            encoded=base64.urlsafe_b64encode(hashlib.sha256(z.read(name)).digest()).decode().rstrip('=')
            checks['wheel_record:'+name]=digest=='sha256='+encoded and int(size)==len(z.read(name))
    import observable_geometry
    installed=pathlib.Path(observable_geometry.__file__).parent
    for name in z.namelist():
        if name.startswith('observable_geometry/') and name.endswith('.py'):
            checks['source_wheel_installed:'+name]=z.read(name)==(root/'source/src'/name).read_bytes()==(installed.parent/name).read_bytes()
checks['isolated_prefix']=sys.prefix!=sys.base_prefix and str(installed).startswith(str(root/'env'))
checks['no_system_site_packages']='include-system-site-packages = false' in (root/'env/pyvenv.cfg').read_text()
report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'python':sys.version,'executable':sys.executable,'package_path':str(installed),'versions':{n:md.version(n) for n in ['observable-geometry','numpy','scipy','pytest','mne','nibabel','h5py']},'wheel_sha256':sha(wheel)}
(root/'integrity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert all(checks.values())
