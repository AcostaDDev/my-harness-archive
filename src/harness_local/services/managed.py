"""Supervisor local explícito H2.2/H2.3, sin entradas HTTP/CLI gestionadas.

Cada run_once reclama como máximo un job. Varias llamadas pueden trabajar en
checkouts diferentes; la base decide idempotencia y exclusión. Solo el heartbeat
usa un hilo y nunca mantiene una sesión SQL durante llamadas del motor.
"""

from dataclasses import asdict, replace
import json
from threading import Event, Thread
from uuid import uuid4

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
        self._call(self.repository.agent_started, history, request)

    def process_intent(self, attempt_id, spec):
        self._call(self.repository.process_intent, attempt_id, spec)

    def process_update(self, attempt_id, kind, payload):
        self._call(self.repository.process_update, attempt_id, kind, payload)

    def command_started(self, command):
        identity = str(uuid4())
        self._call(self.repository.effect, "command_started", {"command_id": identity, "command": asdict(command)})
        return identity

    def command_finished(self, identity, result):
        self._call(self.repository.effect, "command_finished", {"command_id": identity, "result": asdict(result)})


class LocalSupervisor:
    def __init__(self, repository, ports_factory, *, lease_seconds=30):
        """factory(context, frozen_versions) devuelve agentes, comandos y evidencia.

        Los puertos CLI H2.3 se conectan solo por inyección explícita. La selección/versiones es explícita;
        la factory debe rechazarlas si no dispone de la implementación congelada.
        No es un servicio autoarrancado.
        """
        self.repository = repository
        self.ports_factory = ports_factory
        self.lease_seconds = lease_seconds

    def run_once(self):
        self.repository.recover_expired()
        claim = self.repository.claim(lease_seconds=self.lease_seconds)
        if claim is None:
            return None
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
            agents, commands, evidence = self.ports_factory(context, json.loads(record.versions_json))
            journal = _Journal(self.repository, claim, heartbeat_failed)
            if hasattr(agents, "bind_process_journal"):
                agents.bind_process_journal(journal)
            engine = OfflineEngine(agents, commands, evidence, journal)
            request = json.loads(claim.request_json)
            if request["action"] == "start":
                history = engine.start(context, request["task_id"], request["phase_id"], request["text"],
                                       history=record.history)
            else:
                history = engine.resume(context, record.history, retry_executor=request["action"] == "retry")
            self.repository.close_owner(claim)
            owner_closed = True
            journal._call(self.repository.finish, history)
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
