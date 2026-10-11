"""Codex planner/reviewer and Claude executor, explicit opt-in CLI invocations.

No entry point enables this adapter automatically. Environment is passed as a
complete mapping, never silently inherited. Auth stays with each installed CLI.
"""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import re
import subprocess
import sys
from threading import Event, Lock, Thread
import time

from harness_local.adapters.processes import CancellationResult, identity, liveness, stop_group
from harness_local.adapters.streams import AgentStream
from harness_local.core.engine.contracts import AgentResult, freeze
from harness_local.core.engine.journal import JournalError


VERSION = "cli-2"
SUPPORTED = {"codex": ("0.161.0", "0.162.1"), "claude": ("2.1.295",)}


@dataclass(frozen=True)
class CLIConfig:
    provider: str
    executable: tuple[str, ...]
    cli_version: str
    environment: tuple[tuple[str, str], ...]
    timeout_seconds: float
    # Explicit tool permissions for the next attempt; not a file/network sandbox.
    tools: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = ()

    def __post_init__(self):
        if self.provider not in SUPPORTED or self.cli_version not in SUPPORTED[self.provider]:
            raise ValueError("Unsupported CLI baseline; re-characterize before changing it")
        if (not self.executable or not Path(self.executable[0]).is_absolute()
                or not all(isinstance(v, str) and v and "\0" not in v for v in self.executable)):
            raise ValueError("Explicit absolute executable argv required")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("Positive finite timeout required")
        if len(dict(self.environment)) != len(self.environment):
            raise ValueError("Duplicate environment keys")
        for key, value in self.environment:
            if not key or "=" in key or "\0" in key or "\0" in value:
                raise ValueError("Invalid environment")
        for tool in self.tools + self.allowed_tools:
            if not tool or tool.startswith("-") or "\0" in tool:
                raise ValueError("Invalid explicit tool permission")


def argv_for(config, context, request):
    if not request.fresh_session or request.context_json is None:
        raise ValueError("Fresh frozen request required")
    model, effort = request.selection.model, request.selection.effort
    if not model or model.startswith("-") or not effort or effort.startswith("-"):
        raise ValueError("Explicit model/effort required")
    if config.provider == "codex":
        if request.role not in {"planner", "reviewer"}:
            raise ValueError("Codex handles planner/reviewer only")
        return config.executable + (
            "exec", "--strict-config", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
            "--model", model, "--sandbox", "read-only", "--color", "never",
            "-c", 'approval_policy="never"', "-c", f"model_reasoning_effort={json.dumps(effort)}",
            # Built-in provider IDs are reserved; nested retry overrides are rejected.
            "-c", 'model_provider="openai"', "-c", 'web_search="disabled"',
            "--cd", str(context.root), "-")
    if request.role != "executor" or effort not in {"low", "medium", "high", "xhigh", "max"}:
        raise ValueError("Unsupported Claude role/effort")
    return config.executable + (
        "--print", "--output-format", "stream-json", "--verbose", "--include-partial-messages",
        "--no-session-persistence", "--session-id", request.id, "--model", model, "--effort", effort,
        "--permission-mode", "dontAsk", "--permission-prompts", "none", "--tools", ",".join(config.tools),
        "--allowedTools", ",".join(config.allowed_tools), "--strict-mcp-config", "--mcp-config", "{}",
        "--setting-sources", "", "--settings", '{"disableAllHooks":true}',
        "--disable-slash-commands", "--no-chrome")


class CLIProcessAdapter:
    def __init__(self, configs, artifact_root):
        self.configs = {config.provider: config for config in configs}
        if set(self.configs) != {"codex", "claude"}:
            raise ValueError("Both providers must be explicitly configured")
        self.artifact_root = Path(artifact_root).absolute()
        self.journal = None
        self.availability = None
        self.active = {}
        self.lock = Lock()

    def frozen_versions(self):
        return {"agent_adapter": VERSION, "codex_cli": self.configs["codex"].cli_version,
                "claude_cli": self.configs["claude"].cli_version,
                "cli_config_sha256": hashlib.sha256(freeze({"configs": {key: asdict(value)
                    for key, value in self.configs.items()}, "artifact_root": str(self.artifact_root)}).encode()).hexdigest()}

    def capabilities(self):
        return {"version": VERSION, "streaming": True, "cancellation": "posix-process-group",
                "fresh_sessions": True, "interactive_approvals": False,
                "observed_metadata": "only-if-reported", "automatic_retry": False,
                "cli_internal_retries": {"codex": "built-in-defaults/unknown", "claude": "not-controllable/unknown"}}

    def preflight(self):
        """Read-only version/help, no login/status, provider or auth extraction."""
        reports = {}
        for provider, config in self.configs.items():
            version = subprocess.run(config.executable + ("--version",), env=dict(config.environment), cwd=Path.cwd(),
                                     capture_output=True, timeout=10)
            help_args = ("exec", "--help") if provider == "codex" else ("--help",)
            help_result = subprocess.run(config.executable + help_args, env=dict(config.environment), cwd=Path.cwd(),
                                         capture_output=True, timeout=10)
            version_text = version.stdout.decode("utf-8", errors="replace").strip()
            reported_version = re.search(r"\b(\d+\.\d+\.\d+)\b", version_text)
            required = ("--json", "--model", "--sandbox", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--strict-config") if provider == "codex" else (
                "--print", "--output-format", "--verbose", "--include-partial-messages", "--no-session-persistence",
                "--session-id", "--model", "--effort", "--permission-mode", "--permission-prompts", "--tools",
                "--allowedTools", "--strict-mcp-config", "--mcp-config", "--setting-sources", "--settings",
                "--disable-slash-commands", "--no-chrome")
            help_text = help_result.stdout.decode("utf-8", errors="replace")
            missing_flags = [flag for flag in required if flag not in help_text]
            reports[provider] = {"available": version.returncode == help_result.returncode == 0
                                and reported_version is not None and reported_version[1] == config.cli_version
                                and not missing_flags, "missing_flags": missing_flags,
                                "version_output": version_text,
                                "help_sha256": hashlib.sha256(help_result.stdout).hexdigest()}
        return reports

    def bind_process_journal(self, journal):
        if self.journal is not None:
            raise ValueError("Use a new adapter per claimed job")
        versions = json.loads(journal.repository.get_run(journal.claim.run_id).versions_json)
        if any(versions.get(key) != value for key, value in self.frozen_versions().items()):
            raise JournalError("CLI configuration differs from frozen job versions")
        self.availability = self.preflight()
        if not all(item["available"] for item in self.availability.values()):
            raise JournalError("Installed CLI does not match frozen version/help baseline")
        self.journal = journal

    def cancel(self, attempt_id):
        with self.lock:
            item = self.active.get(attempt_id)
            if item is None:
                return CancellationResult(False, "unknown")
            item[1].set()
            # Invocation loop owns signals/reaping to avoid concurrent PID races.
            return CancellationResult(True, "pending")

    def close(self):
        with self.lock:
            for _, cancelled in self.active.values():
                cancelled.set()

    def invoke(self, context, request):
        if self.journal is None:
            raise JournalError("CLI execution requires a managed process journal")
        config = self.configs["claude" if request.role == "executor" else "codex"]
        argv = argv_for(config, context, request)
        if self.artifact_root.is_relative_to(context.root) or self.artifact_root.resolve() != self.artifact_root:
            raise ValueError("Artifacts must be outside checkout without symlinks")
        self.artifact_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory = self.artifact_root / request.id
        # Request IDs originate from engine UUIDs. Never overwrite previous evidence.
        from uuid import UUID
        UUID(request.id)
        directory.mkdir(mode=0o700)
        shapes = {
            "planner": {"task_id": "requested task id", "phase_id": "requested phase id",
                "title": "title", "objective": "objective", "executor_prompt": "instructions",
                "allowed_paths": [], "forbidden_paths": [], "acceptance_criteria": ["criterion"],
                "validation_commands": [], "executor_selection": {"model": "allowed model",
                    "effort": "allowed effort", "reason": "selection reason"}},
            "reviewer": {"task_id": "requested task id", "verdict": "ACCEPT or REVISE or BLOCKED",
                "findings": [], "blocking_questions": [], "scope_grants": [],
                "next_prompt": "required for REVISE", "executor_selection": {"model": "allowed model",
                    "effort": "allowed effort", "reason": "required for REVISE"}},
            "executor": {"result": "implementation summary"},
        }
        prompt = request.prompt + "\n\nReturn exactly one JSON object, without Markdown fences. Shape:\n" + freeze(shapes[request.role])
        if request.role in {"planner", "reviewer"}:
            prompt += "\nAllowed executor selection policy:\n" + freeze({
                "models": context.policy.executor_models, "efforts": context.policy.executor_efforts})
        prompt_bytes = prompt.encode("utf-8")
        prompt_path = directory / "prompt.txt"
        with prompt_path.open("xb") as file:
            file.write(prompt_bytes)
            file.flush()
            os.fsync(file.fileno())
        spec = {"argv": argv, "prompt_path": str(prompt_path),
                "prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(), "cwd": str(context.root), "environment_keys": sorted(dict(config.environment)),
                "environment_sha256": hashlib.sha256(freeze(dict(config.environment)).encode()).hexdigest(),
                "timeout_seconds": config.timeout_seconds, "cli_version": config.cli_version,
                "adapter_version": VERSION, "provider": config.provider,
                "cli_internal_retries": self.capabilities()["cli_internal_retries"][config.provider],
                "preflight_observed": self.availability[config.provider], "artifacts": str(directory),
                "requested": {"model": request.selection.model, "effort": request.selection.effort,
                              "fresh_session": True}}
        self.journal.process_intent(request.id, spec)
        started = time.monotonic()
        started_at = datetime.now(timezone.utc).isoformat()
        process = None
        gate_read, gate_write = os.pipe()
        cancelled = Event()
        parser = AgentStream(config.provider, lambda kind, data: self.journal.process_update(request.id, kind, data))
        status_override = None
        write_error = []
        try:
            process = subprocess.Popen((sys.executable, str(Path(__file__).with_name("process_gate.py")),
                                        str(gate_read), *argv), cwd=context.root, env=dict(config.environment),
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       start_new_session=True, pass_fds=(gate_read,))
            os.close(gate_read)
            gate_read = None
            value = {**identity(process.pid), "pgid": process.pid}
            self.journal.process_update(request.id, "process_spawned", value)
            with self.lock:
                self.active[request.id] = (process, cancelled)
            os.write(gate_write, b"G")
            os.close(gate_write)
            gate_write = None

            def write_prompt():
                try:
                    process.stdin.write(prompt_bytes)
                    process.stdin.close()
                except (BrokenPipeError, OSError) as exc:
                    write_error.append(str(exc))

            writer = Thread(target=write_prompt, daemon=True)
            writer.start()
            deadline = time.monotonic() + config.timeout_seconds
            hashes = {name: hashlib.sha256() for name in ("stdout", "stderr")}
            sizes = {name: 0 for name in hashes}
            drain_deadline = None
            with selectors.DefaultSelector() as selector, (directory / "stdout.bin").open("xb") as out, (directory / "stderr.bin").open("xb") as err:
                files = {"stdout": out, "stderr": err}
                for name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
                    os.set_blocking(pipe.fileno(), False)
                    selector.register(pipe, selectors.EVENT_READ, name)
                while selector.get_map() or process.poll() is None:
                    if status_override is None and (cancelled.is_set() or time.monotonic() >= deadline):
                        status_override = "cancelled" if cancelled.is_set() else "timeout"
                        stop_group(process)
                        # Bounded drain after cancellation, even if escaped child holds a pipe.
                        drain_deadline = time.monotonic() + 0.3
                    for key, _ in selector.select(0.02):
                        chunk = os.read(key.fd, 65536)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        name = key.data
                        files[name].write(chunk)
                        files[name].flush()
                        os.fsync(files[name].fileno())
                        self.journal.process_update(request.id, "stream_bytes", {"stream": name,
                            "offset": sizes[name], "size": len(chunk), "sha256": hashlib.sha256(chunk).hexdigest()})
                        sizes[name] += len(chunk)
                        hashes[name].update(chunk)
                        if name == "stdout":
                            try:
                                parser.feed(chunk)
                            except ValueError:
                                parser.invalid = True
                                parser.tail = b""
                                status_override = "invalid"
                                stop_group(process)
                                drain_deadline = time.monotonic() + 0.3
                    if drain_deadline is not None and time.monotonic() >= drain_deadline:
                        # Remaining readable bytes have been drained by the iteration above.
                        break
                process.poll()
                writer.join(timeout=0.3)
            status, payload = parser.finish(process.returncode)
            status = status_override or status
            if payload is not None and request.role == "executor" and "permission_denials" in parser.observed:
                data = json.loads(payload)
                data["permission_denials"] = parser.observed["permission_denials"]
                payload = freeze(data)
            if write_error and status == "complete":
                status, payload = "failed", None
            group_state = liveness(value, group=True)
            if group_state != "dead":
                # A terminal leader is not proof that its children stopped.
                group_state = stop_group(process).group_state
                status, payload = "failed", None
            metadata = {"status": status, "started_at": started_at,
                        "wall_duration_seconds": time.monotonic() - started, "observed": parser.observed,
                        "artifacts": {name: {"path": str(directory / f"{name}.bin"), "size": sizes[name],
                                             "sha256": hashes[name].hexdigest()} for name in sizes},
                        "exit_code": process.returncode, "group_state": group_state}
            self.journal.process_update(request.id, "process_finished", metadata)
            if group_state != "dead":
                raise JournalError("Process group may still be alive; quarantine required")
            return AgentResult(payload if status == "complete" else None, len(parser.terminals) == 1,
                               process.returncode, error=None if status == "complete" else f"CLI {status}",
                               status=status, metadata_json=freeze(metadata))
        except BaseException:
            # Persistence/parse errors never allow an untracked live writer to continue.
            if process is not None:
                stop_group(process)
            raise
        finally:
            for fd in (gate_read, gate_write):
                if fd is not None:
                    os.close(fd)
            with self.lock:
                self.active.pop(request.id, None)
            if process is not None:
                for pipe in (process.stdin, process.stdout, process.stderr):
                    if pipe and not pipe.closed:
                        pipe.close()
