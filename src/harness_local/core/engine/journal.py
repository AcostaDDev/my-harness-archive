"""Puerto opcional de persistencia; las escrituras preceden a los efectos."""

from typing import Protocol, TYPE_CHECKING

from harness_local.core.engine.contracts import AgentRequest, RunHistory
from harness_local.core.engine.context import Command
if TYPE_CHECKING:
    from harness_local.core.engine.validation import CommandResult


class JournalError(RuntimeError):
    """Una escritura fallida detiene el flujo sin nuevas llamadas externas."""


class EngineJournal(Protocol):
    def checkpoint(self, history: RunHistory, stage: str) -> None: ...
    def agent_started(self, history: RunHistory, request: AgentRequest) -> None: ...
    def command_started(self, command: Command) -> str: ...
    def command_finished(self, identity: str, result: "CommandResult") -> None: ...
