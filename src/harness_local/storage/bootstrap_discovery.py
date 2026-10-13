"""Propuesta bootstrap en la cola existente; no decide ni escribe documentos."""
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.core.engine.bootstrap_discovery import brief_input
from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.prompts import render_attempt
from harness_local.storage.bootstrap import BootstrapRepository
from harness_local.storage.managed import Conflict, _job
from harness_local.storage.models import ManagedRunRow as Run, ManagedJobRow as Job, ManagedEventRow as Event
from harness_local.storage.prompts import PromptRepository


def settle(managed, session, run, outcome):
    managed._event(session, run, 'bootstrap_discovery_result', {'outcome': outcome})


def abort(managed, session, run, status, reason):
    managed._event(session, run, 'bootstrap_discovery_result', {'outcome': {
        'status': 'UNKNOWN', 'result': None, 'reason': reason}})


class DiscoveryRepository:
    def __init__(self, managed):
        self.managed = managed

    def latest(self, root):
        with Session(self.managed.engine) as session:
            run = session.scalar(select(Run).where(Run.root == str(root), Run.purpose == 'bootstrap_discovery')
                                 .order_by(Run.created_at.desc(), Run.id.desc()).limit(1))
            if run is None:
                return None
            event = session.scalar(select(Event).where(Event.run_id == run.id, Event.kind == 'bootstrap_discovery_result')
                                   .order_by(Event.sequence.desc()).limit(1))
            job = session.scalar(select(Job).where(Job.run_id == run.id))
            return {'run_id': run.id, 'run_status': run.status,
                    'brief': json.loads(job.request_json)['snapshot']['brief'],
                    'outcome': event.payload['outcome'] if event else None}

    def request(self, run_id):
        with Session(self.managed.engine) as session:
            row = session.scalar(select(Job).where(Job.run_id == run_id))
            return json.loads(row.request_json)['snapshot']

    def submit(self, context, brief, versions, writer, *, key, confirmed):
        if confirmed is not True:
            raise ValueError('Explicit discovery invocation required')
        if not isinstance(key, str) or not key.strip() or len(key) > 200:
            raise ValueError('Discovery requires an idempotency key of 1–200 characters')
        brief = brief_input(brief)
        marker = {'action': 'bootstrap_discovery', 'root': str(context.root), 'brief': brief, 'confirmed': True}
        # Como el prompt y las activaciones pueden cambiar, la clave conserva el snapshot original.
        with Session(self.managed.engine) as session:
            row = session.scalar(select(Job).where(Job.idempotency_key == key))
            if row is not None:
                old = json.loads(row.request_json)
                if {k: v for k, v in old.items() if k != 'snapshot'} != marker:
                    raise Conflict('Idempotency key already has another discovery payload')
                return _job(row)
        target = writer.inspect_bootstrap(context)
        if target['import_required']:
            raise Conflict('Nonempty discovery target; import required')
        catalog = PromptRepository(self.managed.engine).catalog(context)
        prompt, prompt_snapshot = render_attempt(catalog, 'bootstrap-project', {'BRIEF': freeze(brief)}, context)
        request = freeze({**marker, 'snapshot': {'brief': brief, 'target': target,
                        'prompt': prompt, 'prompt_snapshot_json': prompt_snapshot}})
        assessment = self.managed.guard.assess(context.root)
        with self.managed._write() as session:
            # Una activación concurrente no reemplaza el primer snapshot admitido con esta clave.
            row = session.scalar(select(Job).where(Job.idempotency_key == key))
            if row is not None:
                if {k: v for k, v in json.loads(row.request_json).items() if k != 'snapshot'} != marker:
                    raise Conflict('Idempotency key already has another discovery payload')
                return _job(row)
            BootstrapRepository._empty_authority(session, str(context.root))
            return self.managed._queue_new_run(session, assessment, context, versions,
                'P001-DISCOVERY', 'P001', key, request, purpose='bootstrap_discovery')
