"""D064 standalone macOS qualification. Only fresh synthetic data; no provider CLI.

Run with Python 3.14 on macOS. Results remain in a fresh /private/tmp directory.
An unavailable sandbox is a failure, never an invitation to run the target bare.
This is a laboratory probe, deliberately NOT an importable product launcher.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import pwd
import select
import signal
import socket
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time

SELF = Path(__file__).resolve()
LAUNCHER = '/usr/bin/sandbox-exec'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(paths):
    return {str(p): {'sha256': sha(p), 'mode': p.stat().st_mode,
                     'mtime_ns': p.stat().st_mtime_ns} for p in paths}


def overlap(a, b):
    return a == b or a in b.parents or b in a.parents


def roots(checkout, temporary, protected):
    """Conservative synthetic admission; not a race-free filesystem boundary."""
    result = []
    for raw in (checkout, temporary):
        p = Path(raw)
        if not p.is_absolute() or '..' in p.parts or any(ord(c) < 32 for c in str(p)):
            raise ValueError('invalid_path')
        canonical = p.resolve(strict=True)
        if canonical != p or not p.is_dir():
            raise ValueError('noncanonical_directory')
        if any(overlap(p, q.resolve(strict=True)) for q in protected + result):
            raise ValueError('overlapping_root')
        # Reject existing aliases/special objects before allowing a subtree.
        for item in p.rglob('*'):
            st = item.lstat()
            if stat.S_ISLNK(st.st_mode) or (stat.S_ISREG(st.st_mode) and st.st_nlink != 1):
                raise ValueError('alias')
            if not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):
                raise ValueError('special_file')
        result.append(p)
    return result


def profile(checkout, temporary, writer=True, extra=''):
    allowed = [temporary] + ([checkout] if writer else [])
    filters = ' '.join('(subpath ' + json.dumps(str(p)) + ')' for p in allowed)
    return '(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n' + \
        '(allow file-write* ' + filters + ')\n' + extra


def attempt(op):
    try:
        op()
        return 'allowed'
    except OSError as exc:
        if exc.errno in (errno.EACCES, errno.EPERM):
            return 'denied'
        return 'errno:' + str(exc.errno)


def worker(case, root, args):
    r = Path(root)
    home, tmp, checkout = r/'home', r/'tmp space "quote"', r/'checkout'
    auth = home/'.codex/auth.json'
    config = home/'.codex/config.toml'
    out = {}
    if case == 'filesystem':
        out['fake_auth_read'] = json.loads(auth.read_text()) == {'token': 'FAKE-NOT-A-CREDENTIAL'}
        out['user_matches_uid'] = os.environ['USER'] == pwd.getpwuid(os.getuid()).pw_name
        operations = {
            'config_write': lambda: config.write_text('changed'),
            'refresh_save': lambda: auth.write_text('changed'),
            'unlink': lambda: auth.unlink(),
            'chmod': lambda: auth.chmod(0o666),
            'utime': lambda: os.utime(auth, (1, 1)),
            'home_temp': lambda: (home/'.codex/config.tmp').write_text('tmp'),
            'cache': lambda: (home/'cache').mkdir(),
            'lock': lambda: os.close(os.open(home/'lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)),
            'state_write': lambda: (r/'state/new').write_text('x'),
            'artifact_write': lambda: (r/'artifacts/new').write_text('x'),
            'prefix_sibling': lambda: (r/'checkout-other/new').write_text('x'),
            'dotdot': lambda: (tmp/'../outside/new').write_text('x'),
            'symlink_escape': lambda: (tmp/'escape').write_text('x'),
            'atomic_replace': lambda: (tmp/'replacement').replace(config),
            'hardlink_create': lambda: os.link(auth, tmp/'new-hardlink'),
            'fifo_outside': lambda: os.mkfifo(r/'outside/fifo'),
            'checkout_write': lambda: (checkout/'edit').write_text('edit'),
            'tmp_write': lambda: (tmp/'temporary').write_text('tmp'),
        }
        out.update({name: attempt(op) for name, op in operations.items()})
        try:
            with sqlite3.connect(home/'state.sqlite') as db:
                db.execute('create table data (value)')
        except sqlite3.OperationalError:
            out['sqlite_home'] = 'denied'
        else:
            out['sqlite_home'] = 'allowed'
        with sqlite3.connect(tmp/'state.sqlite') as db:
            out['sqlite_wal'] = db.execute('pragma journal_mode=wal').fetchone()[0]
            db.execute('create table data (value)')
            db.execute('insert into data values (1)')
        (tmp/'config.tmp').write_text('synthetic')
        (tmp/'config.tmp').replace(tmp/'config.toml')
        fd = os.open(tmp/'lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        out['auxiliary_tmp'] = True
        cp = subprocess.run([sys.executable, '-B', str(SELF), 'worker', 'descendant', str(r)],
                            capture_output=True, text=True, timeout=5)
        out['descendant'] = {'exit': cp.returncode, 'result': json.loads(cp.stdout)}
    elif case == 'descendant':
        out['auth_write'] = attempt(lambda: auth.write_text('child'))
    elif case.startswith('auth_'):
        try:
            auth.read_text()
        except FileNotFoundError:
            out['diagnostic'] = 'auth_absent'
        except PermissionError:
            out['diagnostic'] = 'auth_unreadable'
        else:
            out['diagnostic'] = 'refresh_persistence_' + attempt(lambda: auth.write_text('fake-refresh'))
        out['fake_refresh_attempts'] = int(case == 'auth_refresh')
        out['fallbacks'] = 0
        print(json.dumps(out))
        return 23
    elif case == 'nested':
        cp = subprocess.run([LAUNCHER, '-f', str(r/'inner.sb'), sys.executable, '-B',
                             str(SELF), 'worker', 'inner', str(r)],
                            capture_output=True, text=True, timeout=5)
        out = {'exit': cp.returncode, 'stdout': cp.stdout.strip(), 'stderr': cp.stderr.strip()}
    elif case == 'inner':
        out = {'checkout': attempt(lambda: (checkout/'nested').write_text('x')),
               'tmp': attempt(lambda: (tmp/'nested').write_text('x')),
               'outside': attempt(lambda: (r/'outside/nested').write_text('x')),
               'home': attempt(lambda: config.write_text('x'))}
    elif case == 'fd':
        out['inherited_file'] = attempt(lambda: os.write(int(args[0]), b'changed'))
    elif case == 'hardlink':
        out['preexisting_hardlink'] = attempt(lambda: (tmp/'hardlink').write_text('changed'))
    elif case == 'ipc':
        out['inherited_pipe_request'] = attempt(lambda: os.write(int(args[0]), b'W'))
    elif case == 'socket':
        with socket.socket(socket.AF_UNIX) as client:
            out['unix_connect'] = attempt(lambda: client.connect(str(r/'service.sock')))
            if out['unix_connect'] == 'allowed':
                client.sendall(b'W')
    elif case == 'marker':
        (tmp/'target-started').write_text('started')
        out['terminal'] = 'complete'
    elif case == 'no_terminal':
        return 0
    elif case == 'signal':
        os.kill(os.getpid(), signal.SIGTERM)
    elif case == 'hang':
        # Cooperative child reaped by its parent on group TERM; KILL tested separately.
        child = subprocess.Popen([sys.executable, '-B', '-c', 'import time; time.sleep(30)'])
        def stop(*_):
            child.wait(timeout=3)
            sys.exit(0)
        signal.signal(signal.SIGTERM, stop)
        print(json.dumps({'ready': True, 'child_pid': child.pid}), flush=True)
        time.sleep(30)
    elif case == 'ignore_term':
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        print(json.dumps({'ready': True}), flush=True)
        time.sleep(30)
    else:
        raise ValueError(case)
    print(json.dumps(out))
    return 0


class Probe:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix='h64-synthetic-', dir='/private/tmp')).resolve()
        self.results = []
        self.env = None

    def setup(self, name):
        r = self.root/name
        for sub in ('home/.codex', 'tmp space "quote"', 'checkout', 'outside', 'state', 'artifacts', 'checkout-other'):
            (r/sub).mkdir(parents=True)
        (r/'home/.codex/auth.json').write_text('{"token":"FAKE-NOT-A-CREDENTIAL"}')
        (r/'home/.codex/config.toml').write_text('# synthetic\n')
        self.env = {'HOME': str(r/'home'), 'USER': pwd.getpwuid(os.getuid()).pw_name,
                    'PATH': '/usr/bin:/bin', 'TMPDIR': str(r/'tmp space "quote"'),
                    'LANG': 'C', 'PYTHONDONTWRITEBYTECODE': '1'}
        return r

    def run(self, r, case, *, writer=True, extra='', fds=(), args=(), launcher=LAUNCHER, raw_profile=None):
        p = r/'outer.sb'
        p.write_text(raw_profile if raw_profile is not None else profile(r/'checkout', r/'tmp space "quote"', writer, extra))
        cmd = [launcher, '-f', str(p), sys.executable, '-B', str(SELF), 'worker', case, str(r), *map(str, args)]
        originals = [r/'home/.codex/config.toml']
        if (r/'home/.codex/auth.json').exists():
            originals.append(r/'home/.codex/auth.json')
        before = snapshot(originals)
        try:
            cp = subprocess.run(cmd, env=self.env, cwd=r/'checkout', capture_output=True,
                                text=True, timeout=10, pass_fds=fds, start_new_session=True)
            result = {'case': r.name, 'launches': 1, 'exit': cp.returncode,
                      'stdout': cp.stdout.strip(), 'stderr': cp.stderr.strip()}
        except FileNotFoundError:
            result = {'case': r.name, 'launches': 0, 'diagnostic': 'launcher_missing'}
        except PermissionError:
            result = {'case': r.name, 'launches': 0, 'diagnostic': 'launcher_not_executable'}
        result['originals_unchanged'] = before == snapshot(originals)
        result['profile_sha256'] = sha(p)
        assert result['originals_unchanged'], result
        self.results.append(result)
        return result

    def execute(self):
        r = self.setup('root-validation')
        c, t = r/'checkout', r/'tmp space "quote"'
        protected = [r/'home', r/'state', r/'artifacts']
        assert roots(c, t, protected) == [c, t]
        invalid = [r, r/'home', r/'home/.codex', r/'state', r/'artifacts', Path('/'),
                   Path('/private/tmp'), c/'..', Path('relative'), t, r/'absent', Path(str(c) + '\n'), t/'nested']
        (t/'nested').mkdir()
        (r/'alias').symlink_to(c)
        invalid.append(r/'alias')
        rejected = 0
        for path in invalid:
            try:
                roots(path, t, protected)
            except (ValueError, FileNotFoundError):
                rejected += 1
            else:
                raise AssertionError(path)
        for kind in ('symlink', 'hardlink', 'fifo'):
            item = c/kind
            if kind == 'symlink':
                item.symlink_to(r/'home/.codex/auth.json')
            elif kind == 'hardlink':
                os.link(r/'home/.codex/auth.json', item)
            else:
                os.mkfifo(item)
            try:
                roots(c, t, protected)
            except ValueError:
                rejected += 1
            else:
                raise AssertionError(kind)
            item.unlink()
        self.results.append({'case': 'root-validation', 'rejected': rejected, 'accepted': 1})
        for writer in (False, True):
            r = self.setup('writer' if writer else 'reader')
            t = r/'tmp space "quote"'
            (t/'escape').symlink_to(r/'home/.codex/auth.json')
            (t/'replacement').write_text('x')
            result = self.run(r, 'filesystem', writer=writer)
            if result.get('exit') != 0:
                raise RuntimeError('sandbox qualification failed before filesystem results: ' + str(result))
            data = json.loads(result['stdout'])
            for key in ('config_write', 'refresh_save', 'unlink', 'chmod', 'utime', 'home_temp',
                        'cache', 'lock', 'state_write', 'artifact_write', 'prefix_sibling', 'dotdot',
                        'symlink_escape', 'atomic_replace', 'hardlink_create', 'fifo_outside', 'sqlite_home'):
                assert data[key] == 'denied', (key, data[key])
            assert data['checkout_write'] == ('allowed' if writer else 'denied')
            assert data['tmp_write'] == 'allowed' and data['sqlite_wal'] == 'wal'
            assert data['fake_auth_read'] and data['user_matches_uid'] and data['auxiliary_tmp']
            assert data['descendant'] == {'exit': 0, 'result': {'auth_write': 'denied'}}
        for mode in ('absent', 'unreadable', 'refresh'):
            r = self.setup('auth_' + mode)
            extra = ''
            if mode == 'absent':
                (r/'home/.codex/auth.json').unlink()  # Fixture setup, not an auth repair.
            elif mode == 'unreadable':
                extra = '(deny file-read-data (literal ' + json.dumps(str(r/'home/.codex/auth.json')) + '))\n'
            result = self.run(r, 'auth_' + mode, extra=extra)
            assert result['exit'] == 23
            assert json.loads(result['stdout'])['diagnostic'] == {
                'absent': 'auth_absent', 'unreadable': 'auth_unreadable',
                'refresh': 'refresh_persistence_denied'}[mode]
        for writer in (False, True):
            r = self.setup('nested-writer' if writer else 'nested-reader')
            (r/'inner.sb').write_text(profile(r/'checkout', r/'tmp space "quote"', writer))
            result = self.run(r, 'nested')
            assert result['exit'] == 0
            inner = json.loads(result['stdout'])
            if inner['exit'] == 0:
                assert json.loads(inner['stdout']) == {'checkout': 'allowed' if writer else 'denied',
                    'tmp': 'allowed', 'outside': 'denied', 'home': 'denied'}
            else:
                assert not inner['stdout']  # Unsupported nesting never launches bare.
        for case in ('fd', 'fd-closed', 'hardlink', 'ipc'):
            r = self.setup(case)
            target = r/'outside/sacrificial'
            target.write_text('original')
            if case in ('fd', 'fd-closed'):
                fd = os.open(target, os.O_WRONLY)
                try:
                    result = self.run(r, 'fd', fds=(fd,) if case == 'fd' else (), args=(fd,))
                    if case == 'fd-closed':
                        assert json.loads(result['stdout'])['inherited_file'] == 'errno:9'
                finally:
                    os.close(fd)
            elif case == 'hardlink':
                os.link(target, r/'tmp space "quote"/hardlink')
                result = self.run(r, case)
            else:
                rd, wr = os.pipe()
                helper = subprocess.Popen([sys.executable, '-B', '-c',
                    'import os,sys; from pathlib import Path; '
                    'data=os.read(int(sys.argv[1]),1); '
                    'Path(sys.argv[2]).write_text("delegated") if data==b"W" else None',
                    str(rd), str(target)], pass_fds=(rd,), env=self.env)
                os.close(rd)
                try:
                    result = self.run(r, case, fds=(wr,), args=(wr,))
                finally:
                    os.close(wr)
                    helper.wait(timeout=5)
            result['sacrificial_changed'] = target.read_text() != 'original'
            if case == 'fd-closed':
                assert not result['sacrificial_changed']
            assert result['exit'] == 0
        r = self.setup('unix-service')
        with socket.socket(socket.AF_UNIX) as server:
            server.bind(str(r/'service.sock'))
            server.listen(1)
            result = self.run(r, 'socket')
            result['service_received'] = False
            if select.select([server], [], [], 0.2)[0]:
                connection, _ = server.accept()
                with connection:
                    connection.settimeout(1)
                    if connection.recv(1) == b'W':
                        (r/'outside/delegated').write_text('synthetic service')
                        result['service_received'] = True
        invalid_launcher = self.root/'not-executable'
        invalid_launcher.write_text('synthetic non-executable launcher')
        invalid_launcher.chmod(0o600)
        for name, options in (('launcher-missing', {'launcher': str(self.root/'missing')}),
                              ('launcher-invalid', {'launcher': str(invalid_launcher)}),
                              ('profile-invalid', {'raw_profile': '(not-valid-profile'})):
            r = self.setup(name)
            result = self.run(r, 'marker', **options)
            assert not (r/'tmp space "quote"/target-started').exists()
            assert result.get('exit', 1) != 0
        r = self.setup('profile-missing')
        cp = subprocess.run([LAUNCHER, '-f', str(r/'absent.sb'), sys.executable, '-B',
                             str(SELF), 'worker', 'marker', str(r)], env=self.env,
                            capture_output=True, text=True, timeout=5)
        assert cp.returncode != 0 and not (r/'tmp space "quote"/target-started').exists()
        self.results.append({'case': r.name, 'launches': 1, 'exit': cp.returncode,
                             'stderr': cp.stderr.strip(), 'target_started': False})
        for case in ('no_terminal', 'signal'):
            r = self.setup(case)
            result = self.run(r, case)
            assert result['stdout'] == ''
            assert result['exit'] == (0 if case == 'no_terminal' else -signal.SIGTERM)
            result['complete'] = False
        self.gates()

    def gates(self):
        gate = SELF.parents[2]/'src/harness_local/adapters/process_gate.py'
        for mode in ('go', 'eof', 'identity-failure', 'invalid', 'cancel-before-go', 'timeout', 'cancel', 'kill'):
            r = self.setup('gate-' + mode)
            p = r/'outer.sb'
            p.write_text(profile(r/'checkout', r/'tmp space "quote"'))
            originals = [r/'home/.codex/auth.json', r/'home/.codex/config.toml']
            before = snapshot(originals)
            rd, wr = os.pipe()
            case = 'ignore_term' if mode == 'kill' else ('hang' if mode in ('timeout', 'cancel') else 'marker')
            cp = subprocess.Popen([sys.executable, '-B', str(gate), str(rd), LAUNCHER, '-f', str(p),
                                   sys.executable, '-B', str(SELF), 'worker', case, str(r)],
                                  pass_fds=(rd,), env=self.env, start_new_session=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            os.close(rd)
            try:
                assert os.getpgid(cp.pid) == cp.pid
                record = {'pid': cp.pid, 'pgid': cp.pid, 'gate_sha256': sha(gate),
                          'identity_confirmed': mode != 'identity-failure'}
                if mode != 'identity-failure':
                    with (r/'identity.json').open('w') as f:
                        json.dump(record, f)
                        f.flush()
                        os.fsync(f.fileno())
                assert not (r/'tmp space "quote"/target-started').exists()
                if mode == 'cancel-before-go':
                    os.killpg(cp.pid, signal.SIGTERM)
                elif mode == 'invalid':
                    os.write(wr, b'X')
                elif mode not in ('eof', 'identity-failure'):
                    os.write(wr, b'G')
                os.close(wr)
                wr = None
                ready = None
                if mode in ('timeout', 'cancel', 'kill'):
                    assert select.select([cp.stdout], [], [], 5)[0], 'missing ready'
                    ready = json.loads(cp.stdout.readline())
                    assert ready['ready']
                    if mode == 'timeout':
                        try:
                            cp.wait(timeout=0.1)
                        except subprocess.TimeoutExpired:
                            pass
                        else:
                            raise AssertionError('timeout not reached')
                    os.killpg(cp.pid, signal.SIGTERM)
                    if mode == 'kill':
                        try:
                            cp.wait(timeout=0.1)
                        except subprocess.TimeoutExpired:
                            os.killpg(cp.pid, signal.SIGKILL)
                stdout, stderr = cp.communicate(timeout=5)
                try:
                    os.killpg(cp.pid, 0)
                except ProcessLookupError:
                    dead = True
                else:
                    dead = False
                assert dead, 'group still alive'
                assert before == snapshot(originals)
                started = (r/'tmp space "quote"/target-started').exists()
                assert started == (mode == 'go')
                if mode in ('eof', 'identity-failure', 'invalid'):
                    assert cp.returncode == 125
                elif mode == 'go':
                    assert cp.returncode == 0 and json.loads(stdout)['terminal'] == 'complete'
                self.results.append({'case': r.name, **record, 'launches': 1,
                    'exit': cp.returncode, 'target_marker': started, 'group_dead': dead,
                    'ready': ready, 'stderr': stderr.strip(), 'originals_unchanged': True,
                    'complete': mode == 'go', 'stop_reason': mode if mode != 'go' else None})
            finally:
                if wr is not None:
                    os.close(wr)
                if cp.poll() is None:
                    os.killpg(cp.pid, signal.SIGKILL)
                    cp.wait(timeout=5)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        return worker(sys.argv[2], sys.argv[3], sys.argv[4:])
    probe = Probe()
    result = {'decision': 'D064', 'platform': platform.platform(), 'python': sys.version,
              'root': str(probe.root), 'probe_sha256': sha(SELF),
              'provider_invocations': 0, 'real_cli_processes': 0, 'product_integration': False}
    try:
        probe.execute()
        result['qualification_completed'] = True
    except Exception as exc:
        result['qualification_completed'] = False
        result['failure'] = str(exc)
    result['results'] = probe.results
    output = probe.root/'result.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'result': str(output), 'completed': result['qualification_completed'],
                      'cases': len(probe.results), 'failure': result.get('failure')}))
    return 0 if result['qualification_completed'] else 1


if __name__ == '__main__':
    sys.exit(main())
