"""Reviewer and executor agents, each Codex or Claude, explicit opt-in CLI invocations (D052).

The reviewer (planner, reviewer, phase, chat, bootstrap roles) is read-only;
the executor is the only writer. No entry point enables this adapter
automatically. Environment is passed as a complete mapping, never silently
inherited. Auth stays with each installed CLI.
"""
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import sys
from threading import Event, Lock, Thread
import time

from harness_local.adapters.processes import CancellationResult, identity, liveness, stop_group
from harness_local.adapters.streams import AgentStream
from harness_local.core.engine.contracts import AgentResult, freeze
from harness_local.core.engine.journal import JournalError
from harness_local.core.engine.prompts import digest, output_schema


VERSION = "cli-8"
# Version/help characterization (D052): Claude 2.1.295 and 2.1.296 share the same help.
SUPPORTED = {"codex": ("0.161.0", "0.162.1"), "claude": ("2.1.295", "2.1.296")}
# Codex workspace-write was characterized on 0.162.1 only.
WRITE_SUPPORTED = {"codex": ("0.162.1",), "claude": SUPPORTED["claude"]}
# Claude: --help. Codex 0.162.1: reasoning-effort variants in the binary (help lists none).
EFFORTS = {"codex": ("minimal", "low", "medium", "high", "xhigh", "max", "ultra"),
           "claude": ("low", "medium", "high", "xhigh", "max")}
# H3.2 grant kinds each provider can enforce before launch; anything else is refused.
GRANTS = {"codex": (), "claude": ("tools",)}
AGENTS = ("reviewer", "executor")
ROLES = {"executor": "executor", "planner": "reviewer", "reviewer": "reviewer", "phase": "reviewer",
         "chat": "reviewer", "bootstrap": "reviewer"}
READ_TOOLS = ("Read", "Glob", "Grep")
SHAPES = {
    "bootstrap": {"summary": "proposal summary", "requirements": ["proposed requirement"],
        "alternatives": ["architecture alternative and tradeoffs"], "pending_decisions": ["user decision needed"]},
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
    # H3.3, aditivo: la evaluación de fase usa el mismo transporte de solo lectura del revisor.
    "phase": {"phase_id": "requested phase id", "verdict": "READY or REVISE or BLOCKED", "summary": "summary",
        "exit_criteria_results": [{"criterion": "frozen criterion", "passed": True, "evidence": "evidence"}],
        "required_actions": [], "blocking_questions": []},
    # H4.1, aditivo: turno de chat de solo lectura con propuestas estructuradas que no ejecutan nada.
    "chat": {"answer": "answer", "references": ["path or run id"], "proposals": [{"title": "title",
        "objective": "objective", "scope": "scope in words", "acceptance_criteria": ["criterion"],
        "validation": ["validation"], "rationale": "rationale"}]},
}


def reader_schema(request):
    """cli-6 (D058): Claude --json-schema for read-only roles is the typed engine schema of the attempt.

    The schema frozen in the prompt snapshot, as the agent reads it; the fixed
    engine schema of the role only for requests without a snapshot. A cli-5
    schema declared `required` without types and the CLI returned lists as JSON text.
    """
    if request.prompt_snapshot_json is None:
        return output_schema(request.role)
    snapshot = json.loads(request.prompt_snapshot_json)
    schema = snapshot.get("output_schema")
    if not isinstance(schema, dict) or digest(freeze(schema)) != snapshot.get("schema_sha256"):
        raise ValueError("Prompt snapshot without a consistent output schema")
    return schema


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
    grantable_tools: tuple[str, ...] = ()

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
        # This environment switch can force memory on despite the inline setting.
        # Refuse conflicting operator input; never inherit or rewrite auth/env.
        if (self.provider == "claude"
                and dict(self.environment).get("CLAUDE_CODE_DISABLE_AUTO_MEMORY", "1") != "1"):
            raise ValueError("Claude automatic memory must remain disabled")
        for tool in self.tools + self.allowed_tools + self.grantable_tools:
            if not tool or tool.startswith("-") or "\0" in tool:
                raise ValueError("Invalid explicit tool permission")
        if self.provider == "codex" and (self.tools or self.allowed_tools or self.grantable_tools):
            raise ValueError("Codex has no explicit tool inventory; tool lists are Claude-only")


def access_for(role):
    """Read for every reviewer role, write only for the executor."""
    if role not in ROLES:
        raise ValueError("Unknown agent role")
    return "write" if role == "executor" else "read"


def argv_for(config, context, request):
    if not request.fresh_session or request.context_json is None:
        raise ValueError("Fresh frozen request required")
    access = access_for(request.role)
    from harness_local.core.engine.permissions import snapshot_payload
    permissions = snapshot_payload(request)
    if permissions.get('denials'):
        raise ValueError('Explicit permission denial; CLI launch refused')
    grants = permissions['grants']
    if any(grant['expires_at'] <= datetime.now(timezone.utc).isoformat(timespec='microseconds') for grant in grants):
        raise ValueError('Permission expired before CLI launch')
    extra_tools = []
    for grant in grants:
        scope = grant['request']
        if scope['kind'] == 'network':
            raise ValueError('This CLI cannot enforce scoped network grants')
        if scope['kind'] == 'tools':
            rule = scope['target']
            if 'tools' not in GRANTS[config.provider]:
                raise ValueError(f'{config.provider} cannot enforce scoped tool grants; launch refused')
            if (access != 'write' or rule not in config.grantable_tools
                    or rule.split('(', 1)[0] not in config.tools):
                raise ValueError('Tool grant exceeds explicit CLI capabilities/configuration')
            extra_tools.append(rule)
    model, effort = request.selection.model, request.selection.effort
    if not model or model.startswith("-") or not effort or effort.startswith("-"):
        raise ValueError("Explicit model/effort required")
    if effort not in EFFORTS[config.provider]:
        raise ValueError(f"Effort outside the {config.provider} CLI vocabulary")
    if config.provider == "codex":
        if access == "write" and config.cli_version not in WRITE_SUPPORTED["codex"]:
            raise ValueError("Codex workspace-write is characterized on 0.162.1 only")
        # D059: name the canonical checkout and omit the broad /tmp grant. On
        # macOS /tmp aliases /private/tmp and can obscure a checkout beneath it
        # in the permissions description. The explicitly configured TMPDIR
        # keeps its CLI default; file scope remains the frozen engine contract.
        sandbox = ("workspace-write", "-c", "sandbox_workspace_write.network_access=false",
                   "-c", "sandbox_workspace_write.writable_roots=" + json.dumps([str(context.root)], ensure_ascii=False),
                   "-c", "sandbox_workspace_write.exclude_slash_tmp=true") \
            if access == "write" else ("read-only",)
        return config.executable + (
            "exec", "--strict-config", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--json",
            "--model", model, "--sandbox", *sandbox, "--color", "never",
            "-c", 'approval_policy="never"', "-c", f"model_reasoning_effort={json.dumps(effort)}",
            # Built-in provider IDs are reserved; nested retry overrides are rejected.
            "-c", 'model_provider="openai"', "-c", 'web_search="disabled"',
            # D066: disable both memory inputs and injection explicitly, including
            # the feature gate and command history. Ephemeral alone is not enough.
            "-c", 'features.memories=false', "-c", 'memories.generate_memories=false',
            "-c", 'memories.use_memories=false', "-c", 'history.persistence="none"',
            "--cd", str(context.root), "-")
    if access == "read":
        tools = allowed = READ_TOOLS
        # Read-only reviewer: file tools confined to the checkout, structured result.
        tail = ("--restricted", "--json-schema", freeze(reader_schema(request)))
    else:
        # Tools declared grantable are absent from the inventory until this attempt
        # has an explicit matching baseline rule or a persisted grant.
        gated = {rule.split('(', 1)[0] for rule in config.grantable_tools}
        enabled = {rule.split('(', 1)[0] for rule in tuple(config.allowed_tools) + tuple(extra_tools)}
        tools = tuple(tool for tool in config.tools if tool not in gated or tool in enabled)
        allowed = tuple(dict.fromkeys(tuple(config.allowed_tools) + tuple(extra_tools)))
        tail = ()
    return config.executable + (
        "--print", "--output-format", "stream-json", "--verbose", "--include-partial-messages",
        "--no-session-persistence", "--session-id", request.id, "--model", model, "--effort", effort,
        "--permission-mode", "dontAsk", "--permission-prompts", "none", "--tools", ",".join(tools),
        "--allowedTools", ",".join(allowed), "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--setting-sources", "", "--settings", '{"disableAllHooks":true,"autoMemoryEnabled":false}',
        "--disable-slash-commands", "--no-chrome") + tail


class CLIProcessAdapter:
    """`agents`: {"reviewer": CLIConfig, "executor": CLIConfig}, any provider pairing.

    A two-provider sequence keeps the `local-config-1`/`cli-4` reading: Codex
    reviewer and Claude executor.
    """

    def __init__(self, agents, artifact_root):
        if not isinstance(agents, Mapping):
            agents = tuple(agents)
            configs = {config.provider: config for config in agents}
            if len(configs) != len(agents) or set(configs) != {"codex", "claude"}:
                raise ValueError("Both providers must be explicitly configured")
            agents = {"reviewer": configs["codex"], "executor": configs["claude"]}
        if set(agents) != set(AGENTS) or not all(isinstance(item, CLIConfig) for item in agents.values()):
            raise ValueError("Reviewer and executor agents must be explicitly configured")
        if agents["reviewer"].tools or agents["reviewer"].allowed_tools or agents["reviewer"].grantable_tools:
            raise ValueError("The read-only reviewer has a fixed tool inventory")
        executor = agents["executor"]
        if executor.cli_version not in WRITE_SUPPORTED[executor.provider]:
            raise ValueError("Executor CLI write access is not characterized for this version")
        self.agents = dict(agents)
        self.artifact_root = Path(artifact_root).absolute()
        self.journal = None
        self.availability = None
        self.active = {}
        self.lock = Lock()

    def frozen_versions(self):
        # The agent → provider assignment is part of the frozen identity.
        return {"agent_adapter": VERSION,
                **{f"{agent}_{key}": value for agent, config in self.agents.items()
                   for key, value in (("provider", config.provider), ("cli", config.cli_version))},
                "cli_config_sha256": hashlib.sha256(freeze({"agents": {key: asdict(value)
                    for key, value in self.agents.items()}, "artifact_root": str(self.artifact_root)}).encode()).hexdigest()}

    def capabilities(self):
        return {"version": VERSION, "streaming": True, "cancellation": "posix-process-group",
                "fresh_sessions": True, "interactive_approvals": False,
                "observed_metadata": "only-if-reported", "automatic_retry": False,
                "agents": {agent: {"provider": config.provider, "access": access_for(agent),
                                   "grants": list(GRANTS[config.provider]) if agent == "executor" else []}
                           for agent, config in self.agents.items()},
                "cli_internal_retries": {"codex": "built-in-defaults/unknown", "claude": "not-controllable/unknown"}}

    def preflight(self):
        """Read-only version/help per agent, no login/status, provider or auth extraction."""
        from harness_local.adapters.cli_diagnostics import preflight_config
        return {agent: preflight_config(config, access=access_for(agent))
                for agent, config in self.agents.items()}

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
        agent = ROLES.get(request.role)
        if agent is None:
            raise ValueError("Unknown agent role")
        config = self.agents[agent]
        argv = argv_for(config, context, request)
        if self.artifact_root.is_relative_to(context.root) or self.artifact_root.resolve() != self.artifact_root:
            raise ValueError("Artifacts must be outside checkout without symlinks")
        self.artifact_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory = self.artifact_root / request.id
        # Request IDs originate from engine UUIDs. Never overwrite previous evidence.
        from uuid import UUID
        UUID(request.id)
        directory.mkdir(mode=0o700)
        prompt = request.prompt + "\n\nReturn exactly one JSON object, without Markdown fences. Shape:\n" + freeze(SHAPES[request.role])
        if config.provider == "codex" and request.role == "executor":
            prompt += ("\n\nRequested executor filesystem access:\n"
                       "The CLI is invoked with workspace-write and the following canonical checkout "
                       "as both cwd and an explicit writable root:\n" + freeze({"checkout_root": str(context.root)}) +
                       "\nWorkspace write access includes files in its subdirectories. Task paths are relative to "
                       "this checkout; edit only paths permitted by the frozen contract and project policy. "
                       "Temporary directories do not define the task scope. This describes requested access; "
                       "actual tool denials must still be respected and reported.\n")
        if request.role in {"planner", "reviewer"}:
            policy = context.policy
            if policy.executor_mode == "open":
                prompt += "\nExecutor selection policy (open):\n" + freeze({
                    "provider": self.agents["executor"].provider,
                    "models": "any model accepted by the executor CLI",
                    "efforts": policy.executor_effort_vocabulary,
                    "reference": {"models": policy.executor_models, "efforts": policy.executor_efforts}})
            else:
                prompt += "\nAllowed executor selection policy:\n" + freeze({
                    "models": policy.executor_models, "efforts": policy.executor_efforts})
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
                "preflight_observed": self.availability[agent], "artifacts": str(directory), "agent": agent,
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
