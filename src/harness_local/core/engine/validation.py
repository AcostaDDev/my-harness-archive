"""Comandos estructurados y resultados separados del juicio del revisor."""

from dataclasses import dataclass
import shlex
from typing import Protocol

from harness_local.core.engine.context import Command, ProjectContext
from harness_local.core.engine.evidence import ContentEvidence
from harness_local.core.engine.journal import EngineJournal


@dataclass(frozen=True)
class CommandResult:
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float | None = None
    error: str | None = None
    timed_out: bool = False

    @property
    def passed(self) -> bool:
        return type(self.exit_code) is int and self.exit_code == 0 and not self.error and not self.timed_out


class CommandRunner(Protocol):
    def run(self, context: ProjectContext, command: Command) -> CommandResult: ...


@dataclass(frozen=True)
class ValidationEntry:
    command: Command | None
    requested: str
    result: CommandResult


@dataclass(frozen=True)
class ValidationReport:
    evidence: ContentEvidence
    entries: tuple[ValidationEntry, ...]

    @property
    def all_passed(self) -> bool:
        return all(entry.result.passed for entry in self.entries)


def run_command(context: ProjectContext, runner: CommandRunner, command: Command,
                journal: EngineJournal | None = None) -> CommandResult:
    identity = journal.command_started(command) if journal else None
    try:
        context.path(command.cwd)
        result = runner.run(context, command)
    except Exception as exc:
        result = CommandResult(None, error=f"{type(exc).__name__}: {exc}")
    if journal:
        journal.command_finished(identity, result)
    return result


def run_validations(context: ProjectContext, task: dict, evidence: ContentEvidence,
                    runner: CommandRunner, journal: EngineJournal | None = None) -> ValidationReport:
    # El baseline del perfil es configuración confiable; el contrato no autoriza shell.
    commands: list[tuple[str, Command | None, str | None]] = []
    seen: set[Command] = set()
    for text in task["validation_commands"]:
        try:
            argv = tuple(shlex.split(text))
            if not any(argv[:len(prefix)] == prefix for prefix in context.profile.allowed_command_prefixes if prefix):
                raise ValueError("Validation argv outside profile command policy")
            command = Command(argv)
        except ValueError as exc:
            commands.append((text, None, str(exc)))
            continue
        if command not in seen:
            seen.add(command)
            commands.append((text, command, None))
    for command in context.profile.validations:
        if command not in seen:
            seen.add(command)
            commands.append((shlex.join(command.argv), command, None))
    entries = tuple(ValidationEntry(command, text,
                    CommandResult(None, error=error) if error else run_command(context, runner, command, journal))
                    for text, command, error in commands)
    return ValidationReport(evidence, entries)
