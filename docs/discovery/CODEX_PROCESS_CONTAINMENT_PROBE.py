"""D063: standalone macOS filesystem experiment; fake auth only, not product code."""
import errno, hashlib, json, os, pathlib, pwd, subprocess, sys, tempfile

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def child(root):
    root = pathlib.Path(root)
    auth = root/'home/.codex/auth.json'
    assert json.loads(auth.read_text()) == {'token': 'FAKE-NOT-A-CREDENTIAL'}
    assert os.environ['USER'] == pwd.getpwuid(os.getuid()).pw_name
    results = {'read_fake_auth': True}
    for name, op in {
        'config_write': lambda: (root/'home/.codex/config.toml').write_text('changed'),
        'auth_refresh_write': lambda: auth.write_text('changed'),
        'auth_unlink': lambda: auth.unlink(),
        'auth_chmod': lambda: auth.chmod(0o666),
        'global_create': lambda: (root/'home/new').write_text('changed'),
        'outside_temp': lambda: (root/'outside/new').write_text('changed'),
        'symlink_escape': lambda: (root/'allowed/link').write_text('changed'),
        'atomic_replace': lambda: (root/'allowed/replacement').replace(auth),
    }.items():
        try:
            op()
        except OSError as e:
            assert e.errno in (errno.EPERM, errno.EACCES), (name, e)
            results[name] = 'denied'
        else:
            raise AssertionError(name + ' escaped')
    (root/'allowed/temp').write_text('temporary')
    (root/'checkout/edit').write_text('edit')
    results['allowed_writes'] = True
    cp = subprocess.run([sys.executable, '-B', '-c', "from pathlib import Path; import sys\ntry: Path(sys.argv[1]).write_text('child')\nexcept PermissionError: sys.exit(23)\nsys.exit(99)", str(auth)], capture_output=True)
    assert cp.returncode == 23
    results['descendant_denied'] = True
    # Fail explicitly on a required refresh write; no retry or alternate store.
    print(json.dumps(results))
    return 23

if len(sys.argv)>1:
    sys.exit(child(sys.argv[1]))
pathlib.Path('/private/tmp/h63-containment').mkdir(exist_ok=True)
root=pathlib.Path(tempfile.mkdtemp(prefix='synthetic-',dir='/private/tmp/h63-containment'))
for name in ['home/.codex','allowed','checkout','outside']:
    (root/name).mkdir(parents=True)
auth=root/'home/.codex/auth.json'; auth.write_text('{"token":"FAKE-NOT-A-CREDENTIAL"}')
config=root/'home/.codex/config.toml'; config.write_text('# synthetic\n')
(root/'allowed/link').symlink_to(auth)
(root/'allowed/replacement').write_text('replacement')
before={str(p.relative_to(root)):{'hash':digest(p),'mode':p.stat().st_mode,'mtime':p.stat().st_mtime_ns} for p in [auth,config]}
profile='(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(root/'allowed'))+') (subpath '+json.dumps(str(root/'checkout'))+'))\n'
profile_path=root/'probe.sb'; profile_path.write_text(profile)
env={'HOME':str(root/'home'),'USER':pwd.getpwuid(os.getuid()).pw_name,'PATH':'/usr/bin:/bin','TMPDIR':str(root/'allowed'),'LANG':'C','PYTHONDONTWRITEBYTECODE':'1'}
cp=subprocess.run(['/usr/bin/sandbox-exec','-f',str(profile_path),sys.executable,'-B',str(pathlib.Path(__file__).resolve()),str(root)],env=env,cwd=root/'checkout',capture_output=True,text=True,timeout=20)
result={'root':str(root),'launches':1,'returncode':cp.returncode,'stdout':cp.stdout.strip(),'stderr':cp.stderr.strip(),'originals_unchanged':all(digest(root/p)==v['hash'] and (root/p).stat().st_mode==v['mode'] and (root/p).stat().st_mtime_ns==v['mtime'] for p,v in before.items()),'profile':profile,'python':sys.executable}
(root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if cp.returncode !=23 or not result['originals_unchanged']:
    sys.exit(1)
