"""Opt-in native validation commands for trusted, cooperative POSIX repositories.

An exact authorization is not a sandbox. Commands run as the service UID and
may execute repository scripts. No environment inheritance, shell, retry or
recovery signals. The managed journal owns the lease and checkout exclusion.
"""
from dataclasses import asdict, dataclass
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time

from harness_local.adapters.processes import identity, liveness, stop_group
from harness_local.core.engine.context import Command
from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.journal import JournalError
from harness_local.core.engine.validation import CommandResult

VERSION = 'commands-1'


def _environment(entries):
    if not isinstance(entries, tuple) or any(not isinstance(pair, tuple) or len(pair) != 2
            or not all(isinstance(v, str) and '\0' not in v for v in pair)
            or not pair[0] or '=' in pair[0] for pair in entries):
        raise ValueError('Explicit immutable environment pairs required')
    if len(dict(entries)) != len(entries):
        raise ValueError('Duplicate environment keys')
    return dict(entries)


@dataclass(frozen=True)
class CommandConfig:
    checkout: str
    repository_trusted: bool
    authorized_commands: tuple[Command, ...]
    executables: tuple[tuple[str, str], ...]
    environment: tuple[tuple[str, str], ...]
    max_timeout_seconds: float = 1800
    max_output_bytes: int = 65536  # Per stream; bytes saved, not characters.
    terminate_grace_seconds: float = 0.3
    drain_seconds: float = 0.3

    def __post_init__(self):
        if os.name != 'posix':
            raise ValueError('Native command runner requires POSIX process groups')
        root = Path(self.checkout)
        if not root.is_absolute() or root.resolve() != root or not root.is_dir():
            raise ValueError('Canonical existing checkout required')
        if type(self.repository_trusted) is not bool:
            raise ValueError('Repository trust must be explicit')
        if not isinstance(self.authorized_commands, tuple) or not all(
                isinstance(c, Command) and isinstance(c.argv, tuple) for c in self.authorized_commands):
            raise ValueError('Immutable exact command authorizations required')
        executables = _environment(self.executables)
        if not executables or any(not Path(path).is_absolute() for path in executables.values()):
            raise ValueError('Absolute executable paths required; no PATH lookup')
        _environment(self.environment)
        for command in self.authorized_commands:
            _environment(command.environment)
            if command.argv[0] not in executables or any('\0' in a for a in command.argv):
                raise ValueError('Authorized command requires an explicit executable')
            if type(command.timeout_seconds) not in (int, float) or not math.isfinite(command.timeout_seconds):
                raise ValueError('Finite command timeout required')
        for value in (self.max_timeout_seconds, self.terminate_grace_seconds, self.drain_seconds):
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= 86400:
                raise ValueError('Finite positive time limits required')
        if self.terminate_grace_seconds > 2 or self.drain_seconds > 2:
            raise ValueError('Cleanup limits must be at most two seconds')
        if type(self.max_output_bytes) is not int or not 1 <= self.max_output_bytes <= 1048576:
            raise ValueError('Capture limit must be 1..1048576 bytes per stream')


class ManagedCommandRunner:
    def __init__(self, config: CommandConfig):
        self.config = config
        self.journal = None

    def frozen_versions(self):
        return {'commands': VERSION, 'command_config_sha256':
                hashlib.sha256(freeze(asdict(self.config)).encode()).hexdigest()}

    def bind_process_journal(self, journal):
        if self.journal is not None:
            raise JournalError('Use a fresh command runner for each job')
        versions = json.loads(journal.repository.get_run(journal.claim.run_id).versions_json)
        if any(versions.get(k) != v for k, v in self.frozen_versions().items()):
            raise JournalError('Command configuration differs from frozen job versions')
        self.journal = journal

    def run(self, context, command):
        raise JournalError('Native commands require managed command identity and journal')

    def run_managed(self, context, command, command_id):
        if self.journal is None:
            raise JournalError('Native commands require a bound managed journal')
        config = self.config
        if not config.repository_trusted or str(context.root) != config.checkout:
            raise ValueError('Checkout trust has not been granted for this root')
        if command not in config.authorized_commands:
            raise ValueError('Exact command execution has not been authorized')
        cwd = context.path(command.cwd)
        if not cwd.is_dir():
            raise ValueError('Command cwd must be an existing checkout directory')
        if command.timeout_seconds > config.max_timeout_seconds:
            raise ValueError('Command timeout exceeds configured ceiling')
        argv = (dict(config.executables)[command.argv[0]], *command.argv[1:])
        environment = {**dict(config.environment), **dict(command.environment)}
        emit = lambda kind, payload: self.journal.command_process_event(command_id, kind, payload)
        spec = {'adapter_version': VERSION, 'command': asdict(command), 'argv': argv, 'cwd': str(cwd),
                'environment_keys': sorted(environment),
                'environment_sha256': hashlib.sha256(freeze(environment).encode()).hexdigest(),
                'config_sha256': self.frozen_versions()['command_config_sha256'],
                'timeout_seconds': command.timeout_seconds, 'max_output_bytes': config.max_output_bytes,
                'terminate_grace_seconds': config.terminate_grace_seconds, 'drain_seconds': config.drain_seconds,
                'repository_trusted': True, 'authorization': 'exact-command', 'isolation': 'native-uid-posix-group'}
        emit('intent', {'spec': spec})
        started = time.monotonic()
        process = None
        gate_read = gate_write = None
        buffers = {name: bytearray() for name in ('stdout', 'stderr')}
        observed = dict.fromkeys(buffers, 0)
        eof = dict.fromkeys(buffers, False)
        truncated = dict.fromkeys(buffers, False)
        error, timed_out = None, False
        group_state = 'dead'
        try:
            # A missing executable is an observed launch failure, not an invented exit.
            if not Path(argv[0]).is_file() or not os.access(argv[0], os.X_OK):
                raise OSError('Configured executable unavailable or not executable')
            gate_read, gate_write = os.pipe()
            process = subprocess.Popen((sys.executable, '-I', '-S',
                str(Path(__file__).with_name('process_gate.py')), str(gate_read), *argv),
                cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True, pass_fds=(gate_read,))
            os.close(gate_read)
            gate_read = None
            value = {**identity(process.pid), 'pgid': process.pid}
            emit('spawned', {'identity': value})
            os.write(gate_write, b'G')
            os.close(gate_write)
            gate_write = None
            deadline = started + command.timeout_seconds
            drain_deadline = None
            with selectors.DefaultSelector() as selector:
                for name in buffers:
                    pipe = getattr(process, name)
                    os.set_blocking(pipe.fileno(), False)
                    selector.register(pipe, selectors.EVENT_READ, name)
                while selector.get_map() or process.poll() is None:
                    now = time.monotonic()
                    if error is None:
                        if now >= deadline:
                            error, timed_out = 'Command timed out', True
                        elif process.poll() is not None and liveness(value, group=True) != 'dead':
                            error = 'Descendants survived command leader'
                        if error:
                            stop_group(process, grace=config.terminate_grace_seconds)
                            drain_deadline = time.monotonic() + config.drain_seconds
                        elif process.poll() is not None and drain_deadline is None:
                            drain_deadline = now + config.drain_seconds
                    for key, _ in selector.select(0.02):
                        chunk = os.read(key.fd, 16384)
                        name = key.data
                        if not chunk:
                            eof[name] = True
                            selector.unregister(key.fileobj)
                            continue
                        observed[name] += len(chunk)
                        remaining = config.max_output_bytes - len(buffers[name])
                        saved = chunk[:remaining]
                        if saved:
                            emit('bytes', {'stream': name, 'offset': len(buffers[name]),
                                'data_base64': base64.b64encode(saved).decode(),
                                'sha256': hashlib.sha256(saved).hexdigest()})
                            buffers[name].extend(saved)
                        if len(saved) != len(chunk):
                            truncated[name] = True
                            if error is None:
                                error = 'Command output limit exceeded'
                                stop_group(process, grace=config.terminate_grace_seconds)
                                drain_deadline = time.monotonic() + config.drain_seconds
                    if drain_deadline is not None and time.monotonic() >= drain_deadline:
                        break
            process.poll()
            group_state = liveness(value, group=True)
            if group_state != 'dead':
                group_state = stop_group(process, grace=config.terminate_grace_seconds).group_state
                error = error or 'Command group did not stop normally'
            if not all(eof.values()):
                error = error or 'Command capture incomplete'
        except OSError as exc:
            error = f'Command OS error: {type(exc).__name__}: {exc}'
            if process is not None:
                group_state = stop_group(process, grace=config.terminate_grace_seconds).group_state
        except Exception as exc:
            if process is not None:
                stop_group(process, grace=config.terminate_grace_seconds)
            raise JournalError(f'Command execution interrupted: {exc}') from exc
        except BaseException:
            if process is not None:
                stop_group(process, grace=config.terminate_grace_seconds)
            raise  # Journal failures cannot become test results or release the checkout.
        finally:
            for fd in (gate_read, gate_write):
                if fd is not None:
                    os.close(fd)
            if process is not None:
                for pipe in (process.stdout, process.stderr):
                    pipe.close()
        capture = {'command_id': command_id, 'group_state': group_state,
                   'streams': {name: {'saved_bytes': len(data), 'observed_bytes': observed[name],
                       'sha256': hashlib.sha256(data).hexdigest(), 'eof': eof[name],
                       'truncated': truncated[name], 'complete': eof[name] and not truncated[name]}
                       for name, data in buffers.items()}}
        result = CommandResult(process.returncode if process else None,
            bytes(buffers['stdout']).decode('utf-8', errors='replace'),
            bytes(buffers['stderr']).decode('utf-8', errors='replace'),
            time.monotonic() - started, error, timed_out, freeze(capture))
        emit('finished', {'capture': {**capture, 'result': asdict(result)}})
        if group_state != 'dead':
            raise JournalError('Command group alive or uncertain; quarantine required')
        return result
