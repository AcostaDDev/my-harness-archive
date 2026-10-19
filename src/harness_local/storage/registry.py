"""H6.2 E2 (D054/D076): registro de proyectos en SQLite, versionado, auditado y con baja lógica.

Cada cambio es una transacción: comprueba la versión esperada, que el checkout no
tenga trabajo sin terminar y escribe la fila y su evento de auditoría. Repetir una
confirmación ya aplicada devuelve el mismo resultado sin otra versión.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.storage.managed import Conflict
from harness_local.storage.models import (
    CheckoutLockRow as Lock, ManagedJobRow as Job, ManagedRunRow as Run,
    RegisteredProjectEventRow as Event, RegisteredProjectRow as Row,
)
from harness_local.storage.permissions import actor

UNFINISHED = ('QUEUED', 'ACTIVE', 'RECOVERY_REQUIRED')


class RegistryConflict(Conflict):
    def __init__(self, code, diagnostic):
        super().__init__(diagnostic)
        self.code = code


def view(row):
    return {'id': row.id, 'version': row.version, 'status': row.status, 'root': row.root,
            'composition': row.composition, 'profile': row.profile, 'row': row.row, 'row_sha256': row.row_sha256,
            'trust': row.trust, 'creation_id': row.creation_id,
            'created_at': row.created_at, 'updated_at': row.updated_at}


def event_view(row):
    return {'version': row.version, 'action': row.action, 'row': row.row, 'row_sha256': row.row_sha256,
            'previous_sha256': row.previous_sha256, 'preview_sha256': row.preview_sha256, 'actor': row.actor,
            'reason': row.reason, 'recorded_at': row.recorded_at}


class ProjectRegistryRepository:
    def __init__(self, managed):
        self.managed = managed

    def _read(self):
        return Session(self.managed.engine)

    def rows(self):
        with self._read() as session:
            return [view(row) for row in session.scalars(select(Row).order_by(Row.created_at, Row.id))]

    def get(self, project_id):
        with self._read() as session:
            row = session.get(Row, project_id)
            return view(row) if row else None

    def history(self, project_id):
        with self._read() as session:
            return [event_view(row) for row in session.scalars(
                select(Event).where(Event.project_id == project_id).order_by(Event.version))]

    @staticmethod
    def _unfinished(session, root):
        jobs = session.scalars(select(Job.id).join(Run, Run.id == Job.run_id)
                               .where(Run.root == root, Job.status.in_(UNFINISHED))).all()
        locked = session.scalar(select(Lock.job_id).where(Lock.root == root))
        return sorted(set(jobs) | ({locked} if locked is not None else set()))

    def unfinished(self, root):
        with self._read() as session:
            return self._unfinished(session, root)

    def replay(self, project_id, expected_version, preview_sha256):
        """La confirmación ya aplicada (misma vista previa, versión siguiente) se devuelve tal cual."""
        with self._read() as session:
            row = session.get(Row, project_id)
            if row is None or row.version != expected_version + 1:
                return None
            event = session.scalar(select(Event).where(Event.project_id == project_id,
                                                       Event.version == row.version))
            return view(row) if event is not None and event.preview_sha256 == preview_sha256 else None

    def apply(self, action, project_id, *, expected_version, row, row_sha256, profile, preview_sha256,
              trust=None, reason=None):
        with self.managed._write() as session:
            current = session.get(Row, project_id)
            if (current.version if current else 0) != expected_version:
                raise RegistryConflict('stale_version', 'El registro cambió desde la vista previa; vuelve a revisarlo.')
            now = self.managed._now()
            if action == 'register':
                from harness_local.storage.project_creation import CreationRepository
                CreationRepository.conflicts(session, project_id, row['root'])
                if current is not None:
                    raise RegistryConflict('duplicate_id', f'El id {project_id} ya está registrado.')
                if session.scalar(select(Row.id).where(Row.root == row['root'], Row.status == 'ACTIVE')):
                    raise RegistryConflict('root_taken', 'Esa raíz ya pertenece a otro proyecto registrado.')
                current = Row(id=project_id, version=1, status='ACTIVE', root=row['root'],
                              composition=row['composition'], profile=profile, row=row, row_sha256=row_sha256,
                              trust=trust, created_at=now, updated_at=now)
                session.add(current)
                previous = None
            else:
                if current is None:
                    raise LookupError('Proyecto registrado desconocido.')
                if current.status != 'ACTIVE':
                    raise RegistryConflict('retired', 'El proyecto está dado de baja; su historial se conserva.')
                unfinished = self._unfinished(session, current.root)
                if unfinished:
                    raise RegistryConflict('pending_jobs', f'El checkout tiene trabajos sin terminar ({unfinished}); '
                                                           'espera a que terminen o concílialos antes de cambiarlo.')
                previous = current.row_sha256
                current.version += 1
                current.updated_at = now
                if action == 'retire':
                    current.status = 'RETIRED'
                else:
                    current.composition, current.profile = row['composition'], profile
                    current.row, current.row_sha256 = row, row_sha256
            session.flush()
            session.add(Event(project_id=project_id, version=current.version, action=action, row=current.row,
                              row_sha256=current.row_sha256, previous_sha256=previous, preview_sha256=preview_sha256,
                              actor=actor(), reason=reason, recorded_at=now))
            return view(current)
