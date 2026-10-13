"""Supervisor local explícito H2.2/H2.3, sin entradas HTTP/CLI gestionadas.

Cada run_once reclama como máximo un job. Varias llamadas pueden trabajar en
checkouts diferentes; la base decide idempotencia y exclusión. Solo el heartbeat
usa un hilo y nunca mantiene una sesión SQL durante llamadas del motor.
"""

from dataclasses import asdict, replace
import json
from threading import Event, Thread
from uuid import uuid4

from harness_local.core.engine.commit import MechanicalUpdate, commit_accepted
from harness_local.core.engine.journal import JournalError
from harness_local.core.engine.serialization import restore_context
from harness_local.core.engine.workflow import OfflineEngine


class _Journal:
    def __init__(self, repository, claim, heartbeat_failed):
        self.repository = repository
        self.claim = claim
        self.heartbeat_failed = heartbeat_failed

    def _call(self, operation, *args):
        if self.heartbeat_failed.is_set():
            raise JournalError("Heartbeat failed; stop before the next effect")
        try:
            return operation(self.claim, *args)
        except Exception as exc:
            raise JournalError(f"Managed persistence failed: {exc}") from exc

    def checkpoint(self, history, stage):
        self._call(self.repository.checkpoint, history, stage)

    def agent_started(self, history, request):
        return self._call(self.repository.agent_started, history, request)

    def process_intent(self, attempt_id, spec):
        self._call(self.repository.process_intent, attempt_id, spec)

    def process_update(self, attempt_id, kind, payload):
        self._call(self.repository.process_update, attempt_id, kind, payload)

    def command_process_event(self, command_id, kind, payload):
        self._call(self.repository.command_process_event, command_id, kind, payload)

    def pending_commit(self):
        return self._call(self.repository.pending_commit)

    def commit_intent(self, intent):
        self._call(self.repository.commit_intent, intent)

    def commit_result(self, outcome):
        self._call(self.repository.commit_result, outcome)

    def commit_invalidated(self, outcome):
        self._call(self.repository.commit_invalidated, outcome)

    def tag_intent(self, intent):
        self._call(self.repository.tag_intent, intent)

    def export_intent(self, intent):
        self._call(self.repository.export_intent, intent)

    def command_started(self, command):
        identity = str(uuid4())
        self._call(self.repository.effect, "command_started", {"command_id": identity, "command": asdict(command)})
        return identity

    def command_finished(self, identity, result):
        from harness_local.core.engine.validation import command_result_payload
        self._call(self.repository.effect, "command_finished", {"command_id": identity, "result": command_result_payload(result)})


def _bind_commands(commands, journal, versions):
    """A run frozen for native validators never executes through another runner."""
    if hasattr(commands, "bind_process_journal"):
        commands.bind_process_journal(journal)
    elif "command_config_sha256" in versions:
        raise JournalError("Run has a frozen native command configuration; its managed runner is required")


class LocalSupervisor:
    def __init__(self, repository, ports_factory, *, lease_seconds=30, commit_factory=None):
        """factory(context, frozen_versions) devuelve agentes, comandos y evidencia.

        Los puertos CLI H2.3 se conectan solo por inyección explícita. La selección/versiones es explícita;
        la factory debe rechazarlas si no dispone de la implementación congelada.
        No es un servicio autoarrancado. `commit_factory(context, frozen_versions)` aporta el
        escritor Git (captura + commit idempotente) solo para jobs de acción `commit`.
        """
        self.repository = repository
        self.ports_factory = ports_factory
        self.commit_factory = commit_factory
        self.lease_seconds = lease_seconds

    def run_once(self):
        self.repository.recover_expired()
        # H3.4: el lote desatendido encola su siguiente paso antes de reclamar; nunca comprueba ni cierra.
        from harness_local.storage.phases import advance_batches
        advance_batches(self.repository)
        claim = self.repository.claim(lease_seconds=self.lease_seconds)
        if claim is None:
            return None
        # H2.5: antes de cualquier efecto. Escritor legacy, marcador o modo cambiado → REFUSED.
        refusal = self.repository.mode_refusal(claim)
        if refusal is not None:
            self.repository.refuse(claim, refusal)
            return replace(claim, status="REFUSED")
        stopped, heartbeat_failed = Event(), Event()

        def heartbeat():
            while not stopped.wait(self.lease_seconds / 3):
                try:
                    self.repository.heartbeat(claim, lease_seconds=self.lease_seconds)
                except Exception:
                    heartbeat_failed.set()
                    return

        thread = Thread(target=heartbeat, name=f"managed-heartbeat-{claim.id}", daemon=True)
        thread.start()
        agents = None
        owner_closed = False
        try:
            from harness_local.adapters.processes import identity
            self.repository.register_owner(claim, identity())
            record = self.repository.get_run(claim.run_id)
            context = restore_context(record.history.context_json)
            journal = _Journal(self.repository, claim, heartbeat_failed)
            request = json.loads(claim.request_json)
            versions = json.loads(record.versions_json)
            outcome = None
            if request["action"] == "bootstrap_discovery":
                from harness_local.core.engine.bootstrap_discovery import execute
                from harness_local.storage.bootstrap_discovery import DiscoveryRepository
                if self.commit_factory is None:
                    raise RuntimeError('Bootstrap discovery requires the configured Git reader')
                writer = self.commit_factory(context, versions)
                agents, _, _ = self.ports_factory(context, versions)
                if hasattr(agents, 'bind_process_journal'):
                    agents.bind_process_journal(journal)
                history, outcome = execute(context, record.history,
                    DiscoveryRepository(self.repository).request(claim.run_id), agents, writer, journal)
            elif request["action"] == "bootstrap":
                from harness_local.core.engine.bootstrap import execute
                from harness_local.storage.bootstrap import BootstrapRepository
                if self.commit_factory is None:
                    raise RuntimeError('Bootstrap requires the configured Git writer')
                writer = self.commit_factory(context, versions)
                self.repository._require_mode(claim)
                history, outcome = execute(context, record.history,
                    BootstrapRepository(self.repository).request(claim.run_id), writer, journal)
            elif request["action"] == "document_export":
                from harness_local.core.engine.document_export import execute
                from harness_local.storage.document_export import DocumentExportRepository
                if self.commit_factory is None:
                    raise RuntimeError('Document export requires the configured Git writer')
                writer = self.commit_factory(context, versions)
                frozen = DocumentExportRepository(self.repository).request(claim.run_id)
                # En reanudación la intención ya existe; la guardia vuelve a comprobarse antes del efecto.
                self.repository._require_mode(claim)
                history, outcome = execute(context, record.history, frozen, writer, journal, self.repository.clock)
            elif request["action"] == "chat_turn":
                # H4.1: turno de solo lectura con la petición congelada al encolarlo; sin escritor Git.
                from harness_local.core.engine.chat import chat_turn
                from harness_local.storage.chat import ChatRepository
                from harness_local.storage.prompts import PromptRepository
                agents, _, evidence = self.ports_factory(context, versions)
                if hasattr(agents, "bind_process_journal"):
                    agents.bind_process_journal(journal)
                history, outcome = chat_turn(context, record.history, ChatRepository(self.repository).snapshot(claim.run_id),
                                             agents, evidence, journal,
                                             PromptRepository(self.repository.engine).catalog(context))
            elif request["action"] in ("phase_check", "phase_close"):
                # H3.3: puertas de fase con el escritor Git configurado; nunca editan documentos.
                if self.commit_factory is None:
                    raise RuntimeError("Phase operations require the configured Git writer")
                from harness_local.core.engine.phases import check_phase, close_phase
                from harness_local.storage.phases import PhaseRepository
                git = self.commit_factory(context, versions)
                snapshot = PhaseRepository(self.repository).snapshot(claim.run_id)
                if request["action"] == "phase_close":
                    history, outcome = close_phase(context, record.history, snapshot, git, journal,
                                                   now=self.repository.clock)
                else:
                    agents, commands, _ = self.ports_factory(context, versions)
                    _bind_commands(commands, journal, versions)
                    if hasattr(agents, "bind_process_journal"):
                        agents.bind_process_journal(journal)
                    from harness_local.storage.prompts import PromptRepository
                    history, outcome = check_phase(context, record.history, snapshot, agents, commands, git, journal,
                                                   PromptRepository(self.repository.engine).catalog(context))
            elif request["action"] == "commit":
                if self.commit_factory is None:
                    raise RuntimeError("No commit writer configured for a commit job")
                writer = self.commit_factory(context, versions)
                updates = tuple(MechanicalUpdate(**item) for item in request["mechanical"])
                history, _ = commit_accepted(context, record.history, writer, journal, mechanical=updates,
                                             now=self.repository.clock)
            else:
                agents, commands, evidence = self.ports_factory(context, versions)
                _bind_commands(commands, journal, versions)
                if hasattr(agents, "bind_process_journal"):
                    agents.bind_process_journal(journal)
                from harness_local.storage.prompts import PromptRepository
                engine = OfflineEngine(agents, commands, evidence, journal,
                                       prompts=PromptRepository(self.repository.engine).catalog)
                if request["action"] == "start":
                    history = engine.start(context, request["task_id"], request["phase_id"], request["text"],
                                           history=record.history, contract=request.get("contract_json"))
                else:
                    history = engine.resume(context, record.history, retry_executor=request["action"] == "retry")
            self.repository.close_owner(claim)
            owner_closed = True
            journal._call(self.repository.finish, history, outcome)
            return replace(claim, status="DONE")
        except Exception as exc:
            # También un error de persistencia deja intención y lock para conciliación.
            self.repository.quarantine(claim, f"{type(exc).__name__}: {exc}")
            raise
        finally:
            if agents is not None and hasattr(agents, "close"):
                agents.close()
            stopped.set()
            thread.join()
            if not owner_closed:
                self.repository.close_owner(claim)
