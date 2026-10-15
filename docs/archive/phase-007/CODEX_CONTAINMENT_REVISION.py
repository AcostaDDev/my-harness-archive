"""D065 offline laboratory: synthetic sandbox composition, never provider CLIs.

Keeps evidence in a fresh temporary directory; failures never run a bare target.
Does not import or alter the product. Requires macOS and Python 3.14.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import pwd
import select
import stat
import subprocess
import sys
import tempfile

SELF = Path(__file__).resolve()
LAUNCHER = '/usr/bin/sandbox-exec'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {str(p.relative_to(root)): {'sha256': digest(p),
            'mode': p.stat().st_mode, 'mtime_ns': p.stat().st_mtime_ns}
            for p in (root/'home/.codex/auth.json', root/'home/.codex/config.toml')}


def profile(root, mode):
    if mode == 'minimal':
        return '(version 1)\n(allow default)\n'
    if mode == 'reader-comment':
        return profile(root, 'reader') + '; inert comment\n'
    if mode == 'reader-reordered':
        return profile(root, 'reader').replace(
            '(deny network*)\n(deny file-write*)', '(deny file-write*)\n(deny network*)')
    if mode == 'reader-redundant':
        return profile(root, 'reader') + '(deny network-outbound)\n'
    if mode == 'reader-extra-deny':
        return profile(root, 'reader') + '(deny file-read-data (subpath ' + json.dumps(
            str(root/'outside')) + '))\n'
    text = '(version 1)\n(allow default)\n(deny network*)\n'
    if mode == 'default':
        return text
    text += '(deny file-write*)\n'
    allowed = [root/'tmp space "quote"']
    if mode == 'writer':
        allowed.append(root/'checkout')
    if mode != 'no-writes':
        text += '(allow file-write* ' + ' '.join(
            '(subpath ' + json.dumps(str(p)) + ')' for p in allowed) + ')\n'
    return text


def attempt(operation):
    try:
        operation()
        return 'allowed'
    except OSError as exc:
        return 'denied' if exc.errno in (errno.EACCES, errno.EPERM) else 'errno:' + str(exc.errno)


def worker(root):
    # The stdout marker does not need file writes, so an apply failure is distinct.
    result = {'target_started': True,
              'fake_auth_read': json.loads((root/'home/.codex/auth.json').read_text()) ==
                                {'token': 'FAKE-NOT-A-CREDENTIAL'}}
    for name, path in [('checkout', root/'checkout/edit'),
                       ('tmp', root/'tmp space "quote"/edit'),
                       ('outside', root/'outside/edit'),
                       ('home', root/'home/.codex/config.toml')]:
        result[name] = attempt(lambda p=path: p.write_text('synthetic'))
    print(json.dumps(result), flush=True)
    return 0


def capability_worker(root, kind, descriptor):
    if kind == 'race':
        # Parent adds an alias only AFTER admission and readiness, before GO.
        print('ready', flush=True)
        if sys.stdin.buffer.read(1) != b'G':
            return 125
        value = attempt(lambda: (root/'tmp space "quote"/late-alias').write_text('changed'))
    elif kind == 'file':
        value = attempt(lambda: os.write(descriptor, b'changed'))
    elif kind == 'pipe':
        value = attempt(lambda: os.write(descriptor, b'W'))
    else:
        raise ValueError(kind)
    print(json.dumps({'operation': value}), flush=True)
    return 0


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Probe:
    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix='h65-synthetic-', dir='/private/tmp')).resolve()
        self.results = []

    def setup(self, name):
        root = self.root/name
        for sub in ('home/.codex', 'checkout', 'tmp space "quote"', 'outside'):
            (root/sub).mkdir(parents=True)
        (root/'home/.codex/auth.json').write_text('{"token":"FAKE-NOT-A-CREDENTIAL"}')
        (root/'home/.codex/config.toml').write_text('# synthetic\n')
        return root

    def environment(self, root):
        return {'HOME': str(root/'home'), 'USER': pwd.getpwuid(os.getuid()).pw_name,
               'PATH': '/usr/bin:/bin', 'TMPDIR': str(root/'tmp space "quote"'),
                'LANG': 'C', 'PYTHONDONTWRITEBYTECODE': '1'}

    def run(self, name, outer, inner=None, cwd='checkout', inline=False, target='worker'):
        root = self.setup(name)
        env = self.environment(root)
        command = ['/usr/bin/true'] if target == 'true' else [
            sys.executable, '-B', str(SELF), 'worker', str(root)]
        profiles = {}
        # Build inside out, always keeping both layers when testing composition.
        for label, mode in [('inner', inner), ('outer', outer)]:
            if mode is None:
                continue
            value = profile(root, mode)
            path = root/(label + '.sb')
            path.write_text(value)
            profiles[label] = {'mode': mode, 'sha256': digest(path)}
            command = [LAUNCHER, '-p', value, *command] if inline else [
                LAUNCHER, '-f', str(path), *command]
        before = snapshot(root)
        cp = subprocess.run(command, cwd=root/cwd, env=env, capture_output=True,
                            text=True, timeout=10, close_fds=True, start_new_session=True)
        item = {'case': name, 'outer': outer, 'inner': inner, 'cwd': cwd,
                'inline': inline, 'target': target, 'launches': 1,
                'profiles': profiles, 'exit': cp.returncode,
                'stdout': cp.stdout.strip(), 'stderr': cp.stderr.strip(),
                'originals_before': before, 'originals_after': snapshot(root)}
        item['originals_unchanged'] = item['originals_before'] == item['originals_after']
        self.results.append(item)
        if not item['originals_unchanged']:
            raise RuntimeError('protected synthetic originals changed: ' + name)
        return item

    def execute(self):
        for mode in ('writer', 'reader', 'no-writes'):
            item = self.run('single-' + mode, mode)
            if item['exit'] != 0:
                raise RuntimeError('standalone sandbox rejected; no bare fallback: ' + mode)
        for outer in ('writer', 'reader'):
            for inner in ('writer', 'reader', 'no-writes', 'default'):
                self.run(outer + '-' + inner, outer, inner)
        for cwd in ('tmp space "quote"', 'outside'):
            self.run('reader-cwd-' + ('tmp' if cwd.startswith('tmp') else cwd),
                     'writer', 'reader', cwd=cwd)
        self.run('reader-inline', 'writer', 'reader', inline=True)
        self.run('reader-true', 'writer', 'reader', target='true')
        self.run('reader-reader-inline', 'reader', 'reader', inline=True)
        self.run('no-writes-identical', 'no-writes', 'no-writes')
        self.run('default-identical', 'default', 'default', target='true')
        self.run('minimal-identical', 'minimal', 'minimal', target='true')
        self.run('default-writer', 'default', 'writer')
        for inner in ('reader-comment', 'reader-reordered', 'reader-redundant', 'reader-extra-deny'):
            self.run(inner, 'reader', inner)
        self.run('single-extra-deny', 'reader-extra-deny')
        self.run('extra-deny-identical', 'reader-extra-deny', 'reader-extra-deny')
        self.capabilities()
        self.validate()

    def capabilities(self):
        for kind in ('file', 'pipe'):
            for inherit in (True, False):
                root = self.setup(kind + ('-inherited' if inherit else '-closed'))
                target = root/'outside/sacrificial'
                target.write_text('original')
                outer = root/'outer.sb'
                outer.write_text(profile(root, 'writer'))
                before = snapshot(root)
                helper = None
                if kind == 'file':
                    descriptor = os.open(target, os.O_WRONLY)
                else:
                    rd, descriptor = os.pipe()
                    helper = subprocess.Popen([sys.executable, '-B', '-c',
                        'import os,sys; from pathlib import Path; '
                        'data=os.read(int(sys.argv[1]),1); '
                        'Path(sys.argv[2]).write_text("delegated") if data==b"W" else None',
                        str(rd), str(target)], pass_fds=(rd,), close_fds=True,
                        env=self.environment(root))
                    os.close(rd)
                try:
                    cp = subprocess.run([LAUNCHER, '-f', str(outer), sys.executable, '-B',
                        str(SELF), 'capability', str(root), kind, str(descriptor)],
                        env=self.environment(root), cwd=root/'checkout', close_fds=True,
                        pass_fds=(descriptor,) if inherit else (), capture_output=True,
                        text=True, timeout=10)
                finally:
                    os.close(descriptor)
                    if helper is not None:
                        helper.wait(timeout=5)
                self.results.append({'case': root.name, 'launches': 1, 'exit': cp.returncode,
                    'stdout': cp.stdout.strip(), 'stderr': cp.stderr.strip(),
                    'profile_sha256': digest(outer), 'sacrificial_changed': target.read_text() != 'original',
                    'originals_unchanged': before == snapshot(root)})
        root = self.setup('hardlink-after-admission')
        target = root/'outside/sacrificial'
        target.write_text('original')
        temporary = root/'tmp space "quote"'
        # A static scan succeeds. It has no authority over another process later.
        admitted = all(stat.S_ISREG(p.lstat().st_mode) and p.lstat().st_nlink == 1
                       for p in temporary.rglob('*'))
        outer = root/'outer.sb'
        outer.write_text(profile(root, 'writer'))
        before = snapshot(root)
        cp = subprocess.Popen([LAUNCHER, '-f', str(outer), sys.executable, '-B', str(SELF),
            'capability', str(root), 'race', '-1'], cwd=root/'checkout',
            env=self.environment(root), close_fds=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            require(bool(select.select([cp.stdout], [], [], 5)[0]), 'race readiness missing')
            require(cp.stdout.readline().strip() == 'ready', 'race worker not ready')
            os.link(target, temporary/'late-alias')  # Own uncontained parent, sacrificial fixture.
            stdout, stderr = cp.communicate('G', timeout=5)
        finally:
            if cp.poll() is None:
                cp.kill()
                cp.wait(timeout=5)
        self.results.append({'case': root.name, 'launches': 1, 'exit': cp.returncode,
            'admitted_without_alias': admitted, 'alias_introduced_after_readiness': True,
            'stdout': stdout.strip(), 'stderr': stderr.strip(), 'profile_sha256': digest(outer),
            'sacrificial_changed': target.read_text() != 'original',
            'originals_unchanged': before == snapshot(root)})
        root = self.setup('stdout-inert-capture')
        target = root/'outside/sacrificial'
        target.write_text('original')
        outer = root/'outer.sb'
        outer.write_text(profile(root, 'writer'))
        before = snapshot(root)
        cp = subprocess.run([LAUNCHER, '-f', str(outer), sys.executable, '-B', str(SELF),
            'capability', str(root), 'pipe', '1'], cwd=root/'checkout',
            env=self.environment(root), close_fds=True, capture_output=True, text=True, timeout=10)
        self.results.append({'case': root.name, 'launches': 1, 'exit': cp.returncode,
            'stdout': cp.stdout.strip(), 'stderr': cp.stderr.strip(),
            'profile_sha256': digest(outer), 'sacrificial_changed': target.read_text() != 'original',
            'originals_unchanged': before == snapshot(root)})

    def validate(self):
        for item in self.results:
            name = item['case']
            require(item['originals_unchanged'], 'originals changed: ' + name)
            if 'outer' in item:
                success = item['inner'] is None or item['outer'] == item['inner'] or name in (
                    'reader-reader-inline', 'no-writes-identical', 'default-identical',
                    'minimal-identical', 'reader-comment', 'reader-reordered', 'reader-redundant')
                require(item['exit'] == (0 if success else 71), 'unexpected composition: ' + name)
                if not success:
                    require(not item['stdout'] and 'sandbox_apply: Operation not permitted' in
                            item['stderr'], 'target unexpectedly started: ' + name)
                elif item['target'] == 'worker':
                    observed = json.loads(item['stdout'])
                    require(observed['target_started'] and observed['fake_auth_read'], name)
                    require(observed['home'] == observed['outside'] == 'denied', name)
                    require(observed['checkout'] == ('allowed' if item['outer'] == 'writer' else 'denied'), name)
                    require(observed['tmp'] == ('denied' if item['outer'] == 'no-writes' else 'allowed'), name)
            else:
                require(item['exit'] == 0, 'capability worker failed: ' + name)
                if name == 'stdout-inert-capture':
                    require(item['stdout'] == 'W' + json.dumps({'operation': 'allowed'}) and
                            not item['sacrificial_changed'], name)
                    continue
                closed = name.endswith('-closed')
                require(json.loads(item['stdout'])['operation'] == ('errno:9' if closed else 'allowed'), name)
                require(item['sacrificial_changed'] == (not closed), name)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == 'worker':
        return worker(Path(sys.argv[2]))
    if len(sys.argv) == 5 and sys.argv[1] == 'capability':
        return capability_worker(Path(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
    probe = Probe()
    result = {'decision': 'D065', 'root': str(probe.root),
              'platform': platform.platform(), 'python': sys.version,
              'probe_sha256': digest(SELF), 'launcher_sha256': digest(Path(LAUNCHER)),
              'provider_invocations': 0, 'real_cli_processes': 0,
              'product_integration': False, 'fallback_launches': 0}
    try:
        probe.execute()
        result['diagnosis_completed'] = True
    except Exception as exc:
        result['diagnosis_completed'] = False
        result['failure'] = str(exc)
    result['results'] = probe.results
    output = probe.root/'result.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'result': str(output), 'completed': result['diagnosis_completed']}))
    return 0 if result['diagnosis_completed'] else 1


if __name__ == '__main__':
    sys.exit(main())
