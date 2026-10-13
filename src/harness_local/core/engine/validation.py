"""Comandos estructurados y resultados separados del juicio del revisor."""

from dataclasses import asdict, dataclass
import shlex
from typing import Protocol
from uuid import uuid4

from harness_local.core.engine.context import Command, ProjectContext
from harness_local.core.engine.evidence import ContentEvidence
from harness_local.core.engine.journal import EngineJournal
from harness_local.core.engine.junit import JUnitReport, capture_junit, observe_report


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
    command_id: str | None = None
    reports: tuple[JUnitReport, ...] = ()


@dataclass(frozen=True)
class ValidationReport:
    evidence: ContentEvidence
    entries: tuple[ValidationEntry, ...]
    run_id: str | None = None
    source_attempt_id: str | None = None

    @property
    def all_passed(self) -> bool:
        # Un reporte nunca acredita éxito del comando. Fallos observados en un
        # reporte nuevo son una puerta adicional, sin reescribir exit/stdout/stderr.
        return all(entry.result.passed and not any(
            report.freshness in ('created', 'changed') and report.status in ('complete', 'partial')
            and any(case.result in ('failed', 'error') for case in report.cases)
            for report in entry.reports) for entry in self.entries)


def validation_payload(report: ValidationReport, *, include_cases: bool = True) -> dict:
    """El original binario solo se entrega por descarga, nunca en prompts/sondeo."""
    data = asdict(report)
    if include_cases and not any(entry.reports for entry in report.entries):
        data.pop('run_id')
        data.pop('source_attempt_id')
        for entry in data['entries']:
            entry.pop('command_id')
            entry.pop('reports')
        return data
    for entry in data['entries']:
        for imported in entry['reports']:
            imported['original_available'] = imported.pop('original_base64') is not None
            imported['case_count'] = len(imported['cases'])
            if not include_cases:
                imported.pop('cases')
    return data


def run_command(context: ProjectContext, runner: CommandRunner, command: Command,
                journal: EngineJournal | None = None) -> CommandResult:
    return _run_command(context, runner, command, journal)[0]


def _run_command(context, runner, command, journal):
    identity = journal.command_started(command) if journal else str(uuid4())
    try:
        context.path(command.cwd)
        result = runner.run(context, command)
    except Exception as exc:
        result = CommandResult(None, error=f"{type(exc).__name__}: {exc}")
    if journal:
        journal.command_finished(identity, result)
    return result, identity


def run_validations(context: ProjectContext, task: dict, evidence: ContentEvidence,
                    runner: CommandRunner, journal: EngineJournal | None = None, *,
                    run_id: str | None = None, source_attempt_id: str | None = None) -> ValidationReport:
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
    entries = []
    for text, command, error in commands:
        declarations = tuple(d for d in context.profile.junit_reports if d.command == command)
        before = tuple(observe_report(context, d.path) for d in declarations)
        result, identity = (CommandResult(None, error=error), None) if error else _run_command(context, runner, command, journal)
        reports = tuple(capture_junit(context, d, observation) for d, observation in zip(declarations, before))
        entries.append(ValidationEntry(command, text, result, identity if declarations else None, reports))
    # Solo comandos seleccionados exactamente por argv/cwd/entorno/timeout importan reportes.
    has_reports = any(entry.reports for entry in entries)
    return ValidationReport(evidence, tuple(entries), run_id if has_reports else None,
                            source_attempt_id if has_reports else None)
