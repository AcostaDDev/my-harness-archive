"""Propuesta bootstrap en la cola existente; no decide ni escribe documentos.

D088: retirada con la creación v1; solo quedan la lectura de runs registrados y su conciliación."""
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.storage.models import ManagedRunRow as Run, ManagedJobRow as Job, ManagedEventRow as Event


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
        """D088: el descubrimiento de un turno solo servía a la creación v1, retirada. Los runs ya registrados
        se siguen leyendo con `latest` y `request`; nunca se admite uno nuevo."""
        from harness_local.storage.bootstrap import V1_RETIRED
        raise ValueError(V1_RETIRED)
