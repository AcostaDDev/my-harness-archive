"""Bounded, explicit version/help probes shared with the CLI adapter.

Only trusted local executables belong here. This is not an OS sandbox.
Raw output, environment values and exception messages never enter the report.
"""
import hashlib
import json
import math
import os
import re
import selectors
import signal
import stat
import subprocess
import tempfile
import time

from harness_local.i18n import tr


MAX_OUTPUT = 256 * 1024  # stdout and stderr combined, per command
TIMEOUT = 10.0
REQUIRED = {
    'codex': ('--json', '--model', '--sandbox', '--ephemeral', '--ignore-user-config',
              '--ignore-rules', '--strict-config'),
    'claude': ('--print', '--output-format', '--verbose', '--include-partial-messages',
               '--no-session-persistence', '--session-id', '--model', '--effort',
               '--permission-mode', '--permission-prompts', '--tools', '--allowedTools',
               '--strict-mcp-config', '--mcp-config', '--setting-sources', '--settings',
               '--disable-slash-commands', '--no-chrome'),
}
# cli-5 (D052): flags needed only by one access mode of a provider.
ACCESS_REQUIRED = {('claude', 'read'): ('--restricted', '--json-schema')}
PATTERNS = {
    'codex': r'codex-cli ([0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6})',
    'claude': r'([0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}) \(Claude Code\)',
}
# Correction for each diagnostic code: catalog `cli_diagnostics.<code>`, in the emission's visual language.
FIXES = ('config_invalid', 'config_unreadable', 'spawn_error', 'timeout', 'output_limit', 'exit_error',
         'unexpected_output', 'version_mismatch', 'missing_flags', 'probe_error', 'cleanup_error')


def _probe(argv, environment, cwd, timeout):
    """Drain both pipes without unbounded buffering; kill our POSIX group on exit."""
    process = None
    output = bytearray()
    total = 0
    result = {'status': 'spawn_error', 'exit_code': None}
    try:
        process = subprocess.Popen(argv, env=dict(environment), cwd=cwd,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            for pipe in (process.stdout, process.stderr):
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ)
            while selector.get_map() or process.poll() is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    result['status'] = 'timeout'
                    break
                for key, _ in selector.select(min(remaining, 0.05)):
                    chunk = os.read(key.fd, 8192)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    total += len(chunk)
                    if total > MAX_OUTPUT:
                        result['status'] = 'output_limit'
                        break
                    if key.fileobj is process.stdout:
                        output.extend(chunk)
                if result['status'] == 'output_limit':
                    break
            else:
                result = {'status': 'ok' if process.returncode == 0 else 'exit_error',
                          'exit_code': process.returncode}
    except (OSError, ValueError):
        result['status'] = 'spawn_error' if process is None else 'probe_error'
    finally:
        if process is not None:
            # Also terminate children holding pipes after the leader has exited.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except OSError:
                result['status'] = 'cleanup_error'
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                result['status'] = 'cleanup_error'
            finally:
                process.stdout.close()
                process.stderr.close()
    return result, bytes(output) if result['status'] == 'ok' else b''


def preflight_config(config, *, timeout=TIMEOUT, access=None):
    """Observe one validated CLIConfig, without touching its frozen values.

    `access` ('read' | 'write') adds the flags that agent access mode needs.
    """
    if not math.isfinite(timeout) or not 0 < timeout <= TIMEOUT:
        raise ValueError('Probe timeout must be positive and at most ten seconds')
    if access not in (None, 'read', 'write'):
        raise ValueError('Unknown agent access mode')
    required = REQUIRED[config.provider] + ACCESS_REQUIRED.get((config.provider, access), ())
    report = {'available': False, 'status': 'unknown', 'requested_version': config.cli_version,
              'observed_version': None, 'version_output': None, 'help_sha256': None,
              'required_flags': list(required),
              'missing_flags': None, 'probes': {}, 'diagnostics': []}

    def fail(code, status='unknown'):
        report['status'] = status
        report['diagnostics'].append({'code': code, 'correction': tr(f'cli_diagnostics.{code}')})
        return report

    try:
        with tempfile.TemporaryDirectory(prefix='harness-preflight-') as cwd:
            version, raw = _probe(config.executable + ('--version',), config.environment, cwd, timeout)
            report['probes']['version'] = version
            if version['status'] != 'ok':
                return fail(version['status'])
            try:
                text = raw.decode('utf-8').strip()
            except UnicodeDecodeError:
                return fail('unexpected_output')
            match = re.fullmatch(PATTERNS[config.provider], text)
            if match is None:
                return fail('unexpected_output')
            report['observed_version'] = match[1]
            # Only the strict, recognized version line is safe to preserve.
            report['version_output'] = text
            if match[1] != config.cli_version:
                return fail('version_mismatch', 'incompatible')
            args = ('exec', '--help') if config.provider == 'codex' else ('--help',)
            help_result, raw = _probe(config.executable + args, config.environment, cwd, timeout)
            report['probes']['help'] = help_result
            if help_result['status'] != 'ok':
                return fail(help_result['status'])
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                return fail('unexpected_output')
            if not text.strip() or '\0' in text:
                return fail('unexpected_output')
            report['help_sha256'] = hashlib.sha256(raw).hexdigest()
            # --model-extra must not satisfy --model.
            flags = set(re.findall(r'(?<![\w-])--[A-Za-z][A-Za-z0-9-]*(?![\w-])', text))
            report['missing_flags'] = [flag for flag in required if flag not in flags]
            if report['missing_flags']:
                return fail('missing_flags', 'incompatible')
    except OSError:
        return fail('probe_error')
    report.update(available=True, status='version_help_match')
    return report


def diagnose(config):
    """CLIConfig syntax is checked by its constructor; semantic argv is untested."""
    from harness_local.adapters.cli_agents import SUPPORTED, VERSION
    return {'format': 1, 'provider': config.provider, 'adapter_version': VERSION,
            'supported_versions': SUPPORTED,
            'configuration': 'valid_structure', 'preflight': preflight_config(config),
            'not_checked': ['authentication', 'quota', 'model_access', 'full_argv',
                            'tool_permissions', 'network_isolation', 'cli_internal_retries'],
            'environment': 'explicit_without_inheritance'}


def diagnose_file(path):
    """Explicit data file only: never import managed factories or user modules."""
    from harness_local.adapters.cli_agents import CLIConfig, SUPPORTED

    def invalid(code):
        return {'format': 1, 'configuration': 'invalid', 'preflight': None,
                'supported_versions': SUPPORTED,
                'diagnostics': [{'code': code, 'correction': tr(f'cli_diagnostics.{code}')}]}

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate key')
            result[key] = value
        return result

    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as file:
            info = os.fstat(file.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 65536:
                return invalid('config_unreadable')
            raw = file.read(65537)
        if len(raw) > 65536:
            return invalid('config_unreadable')
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
    except (OSError, ValueError, RecursionError):
        return invalid('config_unreadable')
    try:
        required = {'provider', 'executable', 'cli_version', 'environment', 'timeout_seconds'}
        optional = {'tools', 'allowed_tools', 'grantable_tools'}
        if not isinstance(data, dict) or not required <= data.keys() or data.keys() - required - optional:
            return invalid('config_invalid')
        for key in ('provider', 'cli_version'):
            if not isinstance(data[key], str):
                return invalid('config_invalid')
        for key in ('executable', *sorted(optional)):
            values = data.get(key, [])
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                return invalid('config_invalid')
            data[key] = tuple(values)
        env = data['environment']
        if not isinstance(env, dict) or not all(isinstance(value, str) for value in env.values()):
            return invalid('config_invalid')
        data['environment'] = tuple(env.items())
        if type(data['timeout_seconds']) not in (int, float):
            return invalid('config_invalid')
        config = CLIConfig(**data)
    except (ValueError, TypeError, OverflowError):
        return invalid('config_invalid')
    return diagnose(config)
