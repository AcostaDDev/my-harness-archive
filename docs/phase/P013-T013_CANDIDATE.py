"""Qualify one immutable public export offline, with synthetic installed services only.

All inputs/outputs are explicit. Existing candidate/package/archive paths are read-only.
The candidate remains pristine; builds and tests use an exact disposable copy. Never
publishes, selects a provider, or runs the harness against its development repository.
Run with the repository's locked development Python (uv run --frozen --offline python).
"""
import argparse
import hashlib
from http.cookiejar import CookieJar
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPCookieProcessor, Request, build_opener


ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root):
    """Include directory names/modes and links, not just hashes of regular files."""
    result = {}
    for path in [root, *sorted(root.rglob('*'))]:
        mode = stat.S_IMODE(path.lstat().st_mode)
        key = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[key] = [mode, 'link', os.readlink(path)]
        elif path.is_dir():
            result[key] = [mode, 'directory']
        else:
            result[key] = [mode, 'file', len(path.read_bytes()), digest(path.read_bytes())]
    return result


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_public(candidate):
    """Reuse T012 rules against actual exported bytes, without requiring a .git tree."""
    check = load('public_checks', ROOT / 'docs/phase/P013-T012_CHECK_PUBLIC.py')
    check.ROOT = check.PUBLIC = candidate
    docs = check.public_documents()
    links = check.check_links(docs)
    layout = check.check_layout()
    ids = layout.pop('ids')
    check.check_document_references(docs, ids)
    check.check_private(docs)
    cited = set()
    for folder in ('src', 'frontend/src', 'frontend/tests', 'scripts', 'tests', 'examples'):
        for path in (candidate / folder).rglob('*'):
            if not path.is_file() or '/fixtures/' in path.as_posix():
                continue
            try:
                content = path.read_text()
            except UnicodeDecodeError:
                continue
            for line in content.splitlines():
                if not re.search(r"## D\d|\| D\d|D\d{3}-|'D\d{3}'|\"D\d{3}\"", line):
                    cited.update(re.findall(r'\bD\d{3}\b', line))
    assert not cited - ids - check.SYNTHETIC_IDS, cited - ids
    assert not check.errors, check.errors
    return {'documents': len(docs), 'links': links, 'layout': layout, 'code_decisions': len(cited)}


def start_check(area, env):
    """Start/restart the installed wrapper without Node or provider binaries on PATH."""
    install = area / 'Installed with spaces/installation'
    pointer = json.loads((install / 'current.json').read_text())
    generation = install / 'generations' / pointer['generation']
    data = area / 'Installed with spaces/data'
    clean = dict(env, PATH=str(area / 'runtime-bin'), TMPDIR=str(area / 'tmp'))
    observations = []
    for attempt in range(2):
        with socket.socket() as bound:
            bound.bind(('127.0.0.1', 0))
            port = bound.getsockname()[1]
        base = f'http://127.0.0.1:{port}'
        opener = build_opener(HTTPCookieProcessor(CookieJar()))

        def request(path, body=None):
            req = Request(base + path, json.dumps(body).encode() if body else None,
                          {'Content-Type': 'application/json', 'X-Harness-Local': '1'})
            try:
                with opener.open(req, timeout=2) as response:
                    return response.status, response.read()
            except HTTPError as error:
                return error.code, error.read()

        log_path = area / f'logs/start-{attempt}.log'
        if log_path.exists():
            log_path.rename(log_path.with_name(f'start-{attempt}-previous-{time.time_ns()}.log'))
        with log_path.open('w') as stream:
            process = subprocess.Popen([str(generation / 'distribution/scripts/start'), '--install-dir', str(install),
                                        '--port', str(port)], cwd=area, env=clean, stdout=stream, stderr=stream)
            try:
                for _ in range(300):
                    assert process.poll() is None, log_path.read_text()
                    try:
                        if request('/api/health')[0] == 401:
                            break
                    except (URLError, TimeoutError):
                        pass
                    time.sleep(.1)
                else:
                    raise AssertionError('Installed wrapper did not become ready')
                keys = list((data / 'tmp').glob('harness-session-*/login-key'))
                assert len(keys) == 1
                assert request('/api/session', {'key': keys[0].read_text()})[0] == 200
                status, body = request('/api/managed/configuration')
                configuration = json.loads(body)
                assert status == 200 and configuration['mode'] == 'UNCONFIGURED', configuration
                assert request('/')[0] == 200
                assert json.loads(request('/api/managed/supervisor')[1])['enabled'] is False
                observations.append({'start': attempt + 1, 'configuration': configuration['mode'], 'ui': 200,
                                     'supervisor': False})
            finally:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                    raise AssertionError('Installed wrapper did not stop cleanly')
                assert process.returncode == 143, (process.returncode, log_path.read_text())
    assert (data / 'harness.sqlite3').is_file()
    assert not (area / 'Installed with spaces/configuration/global.toml').exists()
    return observations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--area', type=Path, required=True)
    parser.add_argument('--preserve', type=Path, action='append', default=[])
    parser.add_argument('--resume', action='store_true', help='Reuse successful checkpoints; retain failed logs')
    args = parser.parse_args()
    area, candidate = args.area.resolve(), args.out.resolve()
    if not args.resume:
        assert not area.exists() and not candidate.exists(), 'Choose new destinations'
    assert args.preserve and all(path.is_dir() for path in args.preserve)
    assert not any(area.is_relative_to(p.resolve()) or candidate.is_relative_to(p.resolve()) for p in args.preserve)
    if args.resume:
        before = json.loads((area / 'preserved-before.json').read_text())
        assert set(before) == {str(p.resolve()) for p in args.preserve}
    else:
        area.mkdir(mode=0o700)
        (area / 'logs').mkdir()
        before = {str(p.resolve()): inventory(p.resolve()) for p in args.preserve}
        (area / 'preserved-before.json').write_text(json.dumps(before, indent=2))
    env = {k: v for k, v in os.environ.items() if not k.startswith(('HARNESS_', 'UV_', 'PIP_', 'PYTHON', 'npm_config_', 'NPM_CONFIG_'))
           and k not in ('VIRTUAL_ENV', 'CONDA_PREFIX', 'NODE_OPTIONS')}
    env.update(UV_CACHE_DIR=str(ROOT / '.local/uv-cache'), UV_OFFLINE='1', UV_NO_CONFIG='1',
               UV_PYTHON_DOWNLOADS='never', PYTHONDONTWRITEBYTECODE='1', npm_config_userconfig=os.devnull,
               npm_config_globalconfig=str(area / 'empty.npmrc'))
    (area / 'empty.npmrc').touch()
    checkpoint = area / 'checkpoint.json'
    results = json.loads(checkpoint.read_text()) if args.resume else {}

    def run(name, argv, cwd=area, extra=None):
        if results.get(name, {}).get('exit_code') == 0:
            assert (area / f'logs/{name}.log').is_file()
            return
        log = area / f'logs/{name}.log'
        if log.exists():
            log.rename(log.with_name(f'{name}-failed-{time.time_ns()}.log'))
        started = time.monotonic()
        with log.open('w') as stream:
            result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env | (extra or {}), stdout=stream,
                                    stderr=subprocess.STDOUT)
        results[name] = {'exit_code': result.returncode, 'seconds': round(time.monotonic() - started, 2)}
        checkpoint.write_text(json.dumps(results, indent=2) + '\n')
        print(name, results[name], flush=True)
        assert result.returncode == 0, area / f'logs/{name}.log'

    run('export', [sys.executable, ROOT / 'docs/phase/P013-T013_EXPORT.py',
                   '--revision', args.revision, '--out', candidate, '--private-manifest', area / 'private.tsv',
                   '--public-manifest', area / 'public.sha256'])
    # Also verify a resumed candidate directly against the specified Git revision.
    exporter = load('source_export', ROOT / 'docs/archive/phase-012/P012-T005_public_candidate.py')
    exporter.ROOT = ROOT
    expected = {}
    for path, (mode, content) in exporter.sources(args.revision).items():
        target, _ = exporter.classify(path)
        if target:
            assert target not in expected
            expected[target] = (mode, content)
    assert set(expected) == {str(p.relative_to(candidate)) for p in candidate.rglob('*') if p.is_file()}
    assert not any(p.is_symlink() for p in candidate.rglob('*'))
    for target, (mode, content) in expected.items():
        path = candidate / target
        assert path.read_bytes() == content and stat.S_IMODE(path.stat().st_mode) == (0o755 if mode == '100755' else 0o644)
    pristine = inventory(candidate)
    results['public_docs'] = check_public(candidate)
    work = area / 'verification-copy'
    if not args.resume:
        shutil.copytree(candidate, work)
        assert inventory(work) == pristine
    else:
        for target, (_, content) in expected.items():
            assert (work / target).read_bytes() == content, target
    # npm's synthetic offline TypeScript fixtures expect the chosen copy's cache.
    if not args.resume:
        shutil.copytree(ROOT / '.local/npm-cache/_cacache', work / '.local/npm-cache/_cacache')
    run('sync', ['uv', 'sync', '--frozen', '--offline'], work)
    python = work / '.venv/bin/python'
    run('pytest', [python, '-m', 'pytest', '-q'], work)
    run('unittest', [python, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'], work)
    run('build', [python, work / 'scripts/build_distribution.py', '--out-dir', area / 'package'], work)
    run('node', ['node', '--test', *sorted((work / 'frontend/tests').glob('*.test.mjs'))], work)
    run('frontend-check', ['npm', '--prefix', 'frontend', 'run', 'check'], work)
    db = 'sqlite:///' + str(area / 'alembic.sqlite3')
    run('alembic-upgrade', [python, '-m', 'alembic', 'upgrade', 'head'], work, {'HARNESS_DATABASE_URL': db})
    run('alembic-check', [python, '-m', 'alembic', 'check'], work, {'HARNESS_DATABASE_URL': db})
    # The clone checker additionally compares exact package members against this exported copy.
    run('distribution', [python, work / 'scripts/check_distribution.py', '--dist', area / 'package'], work)
    runtime = area / 'runtime-bin'
    runtime.mkdir(exist_ok=True)
    for name, target in [('python3.14', shutil.which('python3.14')), ('git', shutil.which('git')),
                         ('uv', shutil.which('uv')), ('dirname', shutil.which('dirname'))]:
        assert target, name
        link = runtime / name
        if link.is_symlink():
            assert os.readlink(link) == target
        else:
            link.symlink_to(target)
    (area / 'tmp').mkdir(mode=0o700, exist_ok=True)
    cache = area / 'cache'
    cache.mkdir(exist_ok=True)
    if (cache / 'uv').is_symlink():
        assert (cache / 'uv').resolve() == (ROOT / '.local/uv-cache').resolve()
    else:
        (cache / 'uv').symlink_to(ROOT / '.local/uv-cache', target_is_directory=True)
    operating = area / 'Installed with spaces'
    install_args = [work / 'scripts/install', '--dist', area / 'package', '--python', runtime / 'python3.14',
                    '--uv', runtime / 'uv', '--install-dir', operating / 'installation',
                    '--data-dir', operating / 'data', '--config-dir', operating / 'configuration', '--cache-dir', cache]
    no_node = {'PATH': str(runtime)}
    run('install-no-node', install_args, extra=no_node)
    pointer = (operating / 'installation/current.json').read_bytes()
    run('install-replay-no-node', install_args, extra=no_node)
    assert (operating / 'installation/current.json').read_bytes() == pointer
    results['start_restart_no_node'] = start_check(area, env)
    assert inventory(candidate) == pristine, 'Candidate changed during qualification'
    assert before == {str(p.resolve()): inventory(p.resolve()) for p in args.preserve}, 'Protected input changed'
    results['candidate_unchanged'] = results['protected_inputs_unchanged'] = True
    results['artifacts'] = {str(p.relative_to(area / 'package')): digest(p.read_bytes())
                            for p in sorted((area / 'package').rglob('*')) if p.is_file()}
    results['revision'] = subprocess.check_output(['git', 'rev-parse', args.revision], cwd=ROOT, text=True).strip()
    (area / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print('Qualification complete; raw evidence retained under', area, flush=True)


if __name__ == '__main__':
    main()
