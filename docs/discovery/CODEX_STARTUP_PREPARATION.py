"""D067 preparation only. No entry point runs Codex or any provider CLI.

Reads the public pinned native image for its digest, plans two commands without
running them, and exercises a controller only with this script as a Python fake.
Retains fresh synthetic fixtures/evidence. Unavailable sandbox fails closed.
"""
import errno
import hashlib
import json
import mmap
import os
from pathlib import Path
import platform
import pwd
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import time
import tomllib

SELF = Path(__file__).resolve()
PYTHON = Path(sys.executable).resolve()
LAUNCHER = '/usr/bin/sandbox-exec'
CODEX = Path('$HOME/.nvm/versions/node/v24.15.0/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex')
CODEX_SHA = '74c6a6d263f40d65f99c27a815275f5b4ed0bcc2baecc396b4cf3255498bdfc0'
LIMIT = 16 * 1024


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, diagnostic):
    if not condition:
        raise RuntimeError(diagnostic)


def originals(root):
    return {str(path.relative_to(root)): {'sha256': digest(path),
            'mode': path.stat().st_mode, 'mtime_ns': path.stat().st_mtime_ns}
            for path in (root/'home/.codex/auth.json', root/'outside/auth-canary',
                         root/'outside/config-canary')}


def operation(call):
    try:
        call()
        return 'allowed'
    except OSError as exc:
        return 'denied' if exc.errno in (errno.EPERM, errno.EACCES) else 'errno:' + str(exc.errno)


def profile(root, *, future=False):
    # No HOME/real state, broad /tmp, all-file reads, network or Mach allowances.
    public = [Path('/System/Library'), Path('/usr/lib'),
              Path('/System/Volumes/Preboot/Cryptexes/OS/usr/lib'),
              Path(sys.base_prefix).resolve()]
    allowed = [root/'home', root/'checkout', root/'temporary']
    filters = ' '.join('(subpath ' + json.dumps(str(path)) + ')' for path in public + allowed)
    executables = [PYTHON] + ([CODEX] if future else [])
    return ('(version 1)\n(deny default)\n'
            '(allow process-fork)\n(allow sysctl-read)\n'
            '(allow process-exec ' + ' '.join('(literal ' + json.dumps(str(p)) + ')' for p in executables) + ')\n'
            '(allow file-map-executable ' + ' '.join('(subpath ' + json.dumps(str(p)) + ')' for p in public)
            + ' ' + ' '.join('(literal ' + json.dumps(str(p)) + ')' for p in executables) + ')\n'
            '(allow file-read* ' + filters + ' (literal "/dev/null") '
            '(literal ' + json.dumps(str(root/'worker.py')) + ') '
            '(literal ' + json.dumps(str(PYTHON)) + ') '
            + ('(literal ' + json.dumps(str(CODEX)) + ') ' if future else '') + ')\n'
            '(allow file-write* ' + ' '.join('(subpath ' + json.dumps(str(p)) + ')' for p in allowed) + ')\n')


def planned_argv(root, trusted):
    argv = [str(CODEX), 'exec', '--strict-config', '--ignore-user-config', '--ignore-rules',
            '--ephemeral', '--json', '--model', 'gpt-6-luna', '--sandbox', 'workspace-write',
            '--color', 'never']
    overrides = ['approval_policy="never"', 'model_reasoning_effort="low"',
                 'model_provider="openai"', 'web_search="disabled"', 'features.memories=false',
                 'memories.generate_memories=false', 'memories.use_memories=false',
                 'history.persistence="none"', 'sandbox_workspace_write.network_access=false',
                 'sandbox_workspace_write.writable_roots=' + json.dumps([str(root/'checkout')]),
                 'sandbox_workspace_write.exclude_slash_tmp=true']
    if trusted:
        overrides.append('projects.' + json.dumps(str(root/'checkout')) + '.trust_level="trusted"')
    for value in overrides:
        argv.extend(['-c', value])
    return argv + ['--cd', str(root/'checkout'), '-']


def worker(mode, root, argument):
    if mode == 'filesystem':
        result = {'fake_auth_read': (root/'home/.codex/auth.json').read_text() == '{"api_key":"FAKE-NOT-A-CREDENTIAL"}',
                  'outside_read': operation(lambda: (root/'outside/auth-canary').read_bytes()),
                  'outside_write': operation(lambda: (root/'outside/config-canary').write_text('changed')),
                  'artifact_read': operation(lambda: (root/'artifacts/private').read_bytes()),
                  'tmp_write': operation(lambda: (root/'temporary/tmp').write_text('synthetic'))}
        with socket.socket(socket.AF_UNIX) as client:
            result['own_socket_connect'] = operation(lambda: client.connect(str(root/'outside/service.sock')))
        print(json.dumps(result), flush=True)
    elif mode in ('persist', 'override-persists', 'no-persist', 'auth-before-thread'):
        if mode == 'auth-before-thread':
            print(json.dumps({'type': 'synthetic.auth_error'}), flush=True)
            return 23
        print(json.dumps({'type': 'synthetic.thread.started'}), flush=True)
        if mode != 'no-persist':
            (root/'home/.codex/config.toml').write_text('# synthetic trust persisted\n')
        print(json.dumps({'type': 'synthetic.auth_error'}), flush=True)
        return 23
    elif mode == 'fd':
        print(json.dumps({'inherited_fd': operation(lambda: os.write(int(argument), b'changed'))}), flush=True)
    elif mode == 'forged-marker':
        print(json.dumps({'type': 'synthetic.error', 'detail': 'synthetic.thread.started'}), flush=True)
        return 23
    elif mode == 'flood':
        os.write(1, b'x' * (LIMIT * 4))
        time.sleep(2)
    elif mode == 'timeout':
        time.sleep(30)
    elif mode == 'signal':
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        return 125
    return 0


class Preparation:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix='h67-synthetic-', dir='/private/tmp')).resolve()
        self.results = []

    def setup(self, name):
        root = self.root/name
        for folder in ('home/.codex', 'checkout/.git/objects/info', 'checkout/.git/objects/pack',
                       'checkout/.git/refs/heads', 'temporary', 'outside', 'artifacts'):
            (root/folder).mkdir(parents=True, mode=0o700)
        # Minimal fresh Git metadata, no Git subprocess/user configuration or copied run.
        (root/'checkout/.git/HEAD').write_text('ref: refs/heads/diagnostic\n')
        (root/'checkout/.git/config').write_text('[core]\nrepositoryformatversion = 0\nbare = false\n')
        for name, value in [('home/.codex/auth.json', '{"api_key":"FAKE-NOT-A-CREDENTIAL"}'),
                            ('home/.codex/config.toml', '# synthetic original\n'),
                            ('outside/auth-canary', 'FAKE-PRIVATE-CANARY'),
                            ('outside/config-canary', '# protected fictitious config\n'),
                            ('artifacts/private', 'PRIVATE-SYNTHETIC-ARTIFACT')]:
            (root/name).write_text(value)
            (root/name).chmod(0o600)
        (root/'worker.py').write_bytes(SELF.read_bytes())
        (root/'outer.sb').write_text(profile(root))
        return root

    def environment(self, root):
        return {'HOME': str(root/'home'), 'CODEX_HOME': str(root/'home/.codex'),
                'USER': pwd.getpwuid(os.getuid()).pw_name, 'PATH': '/usr/bin:/bin',
                'TMPDIR': str(root/'temporary'), 'LANG': 'C', 'PYTHONDONTWRITEBYTECODE': '1'}

    def run(self, name, mode, *, launcher=LAUNCHER, bad_profile=False, synthetic_controller=False):
        require(launcher in (LAUNCHER, str(self.root/'missing')), 'unsupported preparation launcher')
        root = self.setup(name)
        if bad_profile:
            (root/'outer.sb').write_text('(invalid-profile')
        before = originals(root)
        config_before = digest(root/'home/.codex/config.toml')
        fd = os.open(root/'outside/config-canary', os.O_WRONLY) if mode == 'fd' else None
        target = [str(PYTHON), '-B', str(root/'worker.py'), '--synthetic-worker', mode,
                  str(root), str(fd if fd is not None else -1)]
        # Separate controller unit experiments on a hardcoded trusted Python fake.
        # This is NOT a fallback for the denied boundary target, or a real launcher.
        command = ([launcher] + target[1:] if launcher != LAUNCHER else target) if synthetic_controller else [
            launcher, '-f', str(root/'outer.sb'), *target]
        process = None
        streams = {'stdout': bytearray(), 'stderr': bytearray()}
        status = 'exited'
        started = time.monotonic()
        try:
            process = subprocess.Popen(command, cwd=root/'checkout', env=self.environment(root),
                close_fds=True, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            deadline = time.monotonic() + (0.2 if mode == 'timeout' else 5)
            with selectors.DefaultSelector() as selector:
                for label in streams:
                    pipe = getattr(process, label)
                    os.set_blocking(pipe.fileno(), False)
                    selector.register(pipe, selectors.EVENT_READ, label)
                while selector.get_map() or process.poll() is None:
                    if time.monotonic() >= deadline:
                        status = 'timeout'
                        break
                    for key, _ in selector.select(0.05):
                        chunk = os.read(key.fd, 8192)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        remaining = LIMIT - len(streams[key.data])
                        streams[key.data].extend(chunk[:remaining])
                        if len(chunk) > remaining:
                            status = 'output_limit'
                            break
                    if status == 'output_limit':
                        break
            if status != 'exited':
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=1)
        except FileNotFoundError:
            status = 'launcher_missing'
        finally:
            if fd is not None:
                os.close(fd)
            if process is not None:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=1)
                for pipe in (process.stdout, process.stderr):
                    pipe.close()
        text = streams['stdout'].decode('utf-8', errors='replace')
        config_changed = config_before != digest(root/'home/.codex/config.toml')
        phase = False
        for line in text.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict) and event.get('type') == 'synthetic.thread.started':
                phase = True
        meaning = ('synthetic_persistence_observed' if config_changed else
                   'synthetic_no_change_after_marker' if phase else 'inconclusive_before_marker')
        group_dead = None
        if process is not None:
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                group_dead = True
            else:
                group_dead = False
        record = {'case': name, 'status': status, 'launches': int(process is not None),
                  'backend': 'controller-synthetic' if synthetic_controller else 'OS-boundary-candidate',
                  'exit': process.returncode if process else None, 'classification': meaning,
                  'synthetic_marker': phase, 'config_changed': config_changed,
                  'config_sha256_before': config_before,
                  'config_sha256_after': digest(root/'home/.codex/config.toml'),
                  'originals_before': before, 'originals_after': originals(root),
                  'protected_originals_unchanged': before == originals(root),
                  'group_dead': group_dead, 'capture_complete': status == 'exited',
                  'elapsed_seconds': round(time.monotonic() - started, 3),
                  'profile_sha256': digest(root/'outer.sb'), 'streams': {}}
        for label, content in streams.items():
            path = root/'artifacts'/(label + '.bin')
            with path.open('xb') as output:
                os.fchmod(output.fileno(), 0o600)
                output.write(content)
            record['streams'][label] = {'size': len(content), 'sha256': digest(path)}
        # Synthetic-only output is safe to retain. No executable switch accepts real output.
        record['stdout'] = text if mode != 'flood' else '<bounded synthetic flood>'
        record['stderr'] = streams['stderr'].decode('utf-8', errors='replace')
        self.results.append(record)
        return record

    def boundary(self):
        r = self.run('direct-boundary', 'filesystem')
        if r['exit'] == 0:
            data = json.loads(r['stdout'])
            require(data == {'fake_auth_read': True, 'outside_read': 'denied', 'outside_write': 'denied',
                             'artifact_read': 'denied', 'tmp_write': 'allowed', 'own_socket_connect': 'denied'},
                    'direct boundary does not satisfy controls')
            return True
        require(not r['stdout'], 'unexpected partial boundary execution')
        return False

    def controller(self):
        for mode in ('persist', 'override-persists', 'no-persist', 'auth-before-thread'):
            r = self.run('controller-' + mode, mode, synthetic_controller=True)
            require(r['exit'] == 23, 'fake auth exit missing')
            require(r['config_changed'] == (mode in ('persist', 'override-persists')), 'config observation mismatch')
            require(r['synthetic_marker'] == (mode != 'auth-before-thread'), 'marker observation mismatch')
        r = self.run('controller-forged-marker', 'forged-marker', synthetic_controller=True)
        require(r['exit'] == 23 and not r['synthetic_marker'] and not r['config_changed'],
                'marker text mistaken for a structured event')
        r = self.run('controller-fd-closed', 'fd', synthetic_controller=True)
        require(json.loads(r['stdout'])['inherited_fd'] == 'errno:9', 'inherited descriptor not closed')
        for mode in ('signal', 'timeout', 'flood'):
            r = self.run('controller-' + mode, mode, synthetic_controller=True)
            require(r['status'] == {'signal': 'exited', 'timeout': 'timeout', 'flood': 'output_limit'}[mode],
                    'bounded stop mismatch')
        r = self.run('invalid-profile', 'persist', bad_profile=True)
        require(r['exit'] != 0 and not r['synthetic_marker'], 'invalid profile target started')
        r = self.run('controller-launcher-missing', 'persist', launcher=str(self.root/'missing'), synthetic_controller=True)
        require(r['launches'] == 0 and not r['synthetic_marker'], 'missing launcher target started')
        require(all(r['protected_originals_unchanged'] for r in self.results), 'protected originals changed')
        require(all(r['group_dead'] is True for r in self.results if r['launches']), 'synthetic group still present')


def main():
    if len(sys.argv) == 5 and sys.argv[1] == '--synthetic-worker':
        return worker(sys.argv[2], Path(sys.argv[3]), sys.argv[4])
    require(len(sys.argv) == 1, 'preparation accepts no target or execution option')
    prep = Preparation()
    result = {'decision': 'D067', 'root': str(prep.root), 'platform': platform.platform(),
              'python': sys.version, 'source_sha256': digest(SELF), 'real_cli_processes': 0,
              'provider_invocations': 0, 'fallback_launches': 0, 'execution_eligible': False}
    try:
        with CODEX.open('rb') as binary, mmap.mmap(binary.fileno(), 0, access=mmap.ACCESS_READ) as data:
            require(hashlib.sha256(data).hexdigest() == CODEX_SHA, 'pinned image changed')
        planned = prep.setup('planned-only')
        (planned/'future.sb').write_text(profile(planned, future=True))
        result['planned_only'] = {'executable': str(CODEX), 'sha256': CODEX_SHA,
            'argv_without_override': planned_argv(planned, False),
            'argv_trusted_override': planned_argv(planned, True), 'environment': prep.environment(planned),
            'profile_sha256': digest(planned/'future.sb'), 'maximum_real_processes_if_later_qualified': 2,
            'timeout_seconds': 10, 'stream_limit_bytes': LIMIT,
            'prompt': 'Diagnostic startup only. Do not use tools or change files.'}
        variants = result['planned_only']
        parsed = [tomllib.loads('\n'.join(args[i + 1] for i, arg in enumerate(args) if arg == '-c'))
                  for args in (variants['argv_without_override'], variants['argv_trusted_override'])]
        require(parsed[1].pop('projects') == {str(planned/'checkout'): {'trust_level': 'trusted'}},
                'trust override incorrectly escaped')
        require(parsed[0] == parsed[1], 'unexpected differences between planned commands')
        require(parsed[0]['memories'] == {'generate_memories': False, 'use_memories': False},
                'cli-8 memory controls missing')
        require(parsed[0]['features']['memories'] is False and parsed[0]['history']['persistence'] == 'none',
                'cli-8 memory feature/history controls missing')
        result['boundary_worker_started'] = prep.boundary()
        prep.controller()
        result['preparation_completed'] = True
        result['verdict'] = ('not eligible: minimal Python worker fails before marker under default-deny candidate'
            if not result['boundary_worker_started'] else
            'not eligible: filesystem aliases and general IPC not qualified by direct controls')
    except (OSError, RuntimeError, ValueError) as exc:
        result['preparation_completed'] = False
        result['failure'] = str(exc)
    result['results'] = prep.results
    path = prep.root/'result.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'result': str(path), 'completed': result['preparation_completed'],
                      'execution_eligible': False}))
    return 0 if result['preparation_completed'] else 1


if __name__ == '__main__':
    sys.exit(main())
