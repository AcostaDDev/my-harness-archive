"""P009-T002 / D116: una autoridad UI para hijos directos nuevos; sin agentes ni Git."""
from contextlib import contextmanager
from dataclasses import asdict
import os
from pathlib import Path
import stat
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from harness_local.services.managed_runtime import PROJECT_ID
from harness_local.services.project_registry import RegistryError, RESERVED_IDS, TRUST, digest, _inside, _within
from harness_local.storage.models import (
    ProjectCreationRootRow as Root, ProjectCreationRootEventRow as RootEvent,
    ProjectCreationOperationRow as Operation, ProjectCreationOperationEventRow as Event,
    RegisteredProjectRow as Project, RegisteredProjectEventRow as ProjectEvent,
)
from harness_local.storage.permissions import actor
from harness_local.storage.project_creation import CreationRepository, root_view

PERMISSION = 'El servicio podrá crear carpetas hijas nuevas en esta ubicación.'
CONTRACT = 'project-creation-1'


def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino}


def normalized(value):
    if not isinstance(value, str) or not value or '\0' in value or '..' in value.split('/'):
        raise RegistryError(422, 'root_invalid', 'Ruta explícita requerida, sin NUL ni «..».')
    path = Path(os.path.normpath(value))
    if not path.is_absolute():
        raise RegistryError(422, 'root_not_absolute', 'La carpeta debe ser una ruta absoluta.')
    return Path('/' + str(path).lstrip('/'))


@contextmanager
def directory(path):
    """Cada componente por fd y O_NOFOLLOW. Nunca se resuelve un enlace silenciosamente."""
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def exists(fd, name):
    try:
        os.stat(name, dir_fd=fd, follow_symlinks=False)
        return True
    except FileNotFoundError:
        return False


class ProjectCreation:
    def __init__(self, runtime):
        self.runtime, self.registry = runtime, runtime.registry
        self.repository = CreationRepository(runtime.repository)
        self.lock = self.registry._lock

    def reconcile(self):
        """Arranque: clasifica efectos inciertos; nunca crea, adopta o borra carpetas."""
        if self.registry.registrar is None:
            return
        with self.lock, self.runtime.repository._write() as session:
            for row in session.scalars(select(Operation).where(Operation.status == 'INTENDED')):
                try:
                    with directory(Path(row.authority['path'])) as fd:
                        changed = identity(os.fstat(fd)) != row.authority['identity']
                        present = exists(fd, row.directory_name)
                    if not changed and not present:
                        continue
                    row.status = 'RECOVERY_REQUIRED' if present else 'BLOCKED'
                    row.diagnostic = 'Destino sin prueba de propiedad o identidad del padre cambiada; se conserva.'
                except OSError:
                    row.status, row.diagnostic = 'RECOVERY_REQUIRED', 'No se puede acreditar el destino tras reiniciar.'
                self.repository.event(session, row, 'restart_observed')

    def require(self, *, bootstrap=False):
        registrar = self.registry._require()
        if bootstrap and not registrar.bootstrap_enabled:
            raise RegistryError(409, 'bootstrap_not_allowed', 'El operador no habilita creación documental.')
        return registrar

    def protected(self):
        registrar = self.require()
        db = self.runtime.database
        return (registrar.state, registrar.source, db, Path(str(db) + '-wal'), Path(str(db) + '-shm'),
                self.runtime.migration.migrations_dir)

    def parent(self, value):
        path = normalized(value)
        try:
            with directory(path) as fd:
                info = identity(os.fstat(fd))
                if not os.access(path, os.W_OK | os.X_OK):
                    raise RegistryError(422, 'root_unwritable', 'La carpeta no permite crear hijos.')
            # Inspección estática: no ejecuta Git ni lee configuración del repositorio.
            if any(os.path.lexists(p / '.git') for p in (path, *path.parents)):
                raise RegistryError(422, 'root_in_repository', 'El padre no puede estar dentro de un repositorio Git.')
            if any(_within(path, p) for p in self.protected() if p is not None):
                raise RegistryError(422, 'root_service_state', 'El padre no puede estar dentro del estado del servicio.')
            roots = [p.context.root for p in self.runtime.projects.values()]
            roots += [Path(p['root']) for p in self.registry.repository.rows() if p['status'] == 'ACTIVE']
            if any(_within(path, p) for p in roots):
                raise RegistryError(422, 'root_taken', 'El padre no puede estar dentro de un checkout gestionado.')
            return str(path), info
        except OSError:
            raise RegistryError(422, 'root_unavailable', 'La carpeta debe existir y ser accesible, sin enlaces.') from None

    def read_root(self):
        available = self.registry.registrar is not None
        root = self.repository.root()
        return {**root, 'available': available,
                'diagnostic': None if available else 'Requiere local-config-3/4/5 registrable.',
                'bootstrap_enabled': available and self.registry.registrar.bootstrap_enabled,
                'permission_statement': PERMISSION, 'history': self.repository.roots_history(),
                'operations': self.repository.operations()}

    def root_preview(self, body, *, session=None):
        self.require()
        current = root_view(session.get(Root, 1)) if session is not None else self.repository.root()
        if current['version'] != body['expected_version']:
            raise RegistryError(409, 'stale_version', 'La carpeta cambió; vuelve a revisar.')
        if body['action'] == 'select':
            path, info = self.parent(body.get('path'))
        else:
            if body.get('path') is not None:
                raise RegistryError(422, 'root_invalid', 'Retirar no admite una ruta nueva.')
            if current['status'] != 'ACTIVE':
                raise RegistryError(409, 'root_revoked', 'No hay una carpeta vigente que retirar.')
            path, info = None, None
        after = {'version': current['version'] + 1,
                 'status': 'ACTIVE' if body['action'] == 'select' else 'REVOKED', 'path': path, 'identity': info}
        return {'action': body['action'], 'expected_version': current['version'], 'root': after,
                'permission_statement': PERMISSION, 'preview_sha256': digest({'before': current, 'after': after})}

    @staticmethod
    def same_request(saved, request_sha256):
        if saved.request_sha256 != request_sha256:
            raise RegistryError(409, 'idempotency_conflict', 'La clave ya pertenece a otro payload.')

    def root_apply(self, body, key):
        request_sha256 = digest(body)
        with self.lock, self.runtime.repository._write() as session:
            previous = session.scalar(select(RootEvent).where(RootEvent.idempotency_key == key))
            if previous:
                self.same_request(previous, request_sha256)
                return {**previous.payload['preview'], 'replayed': True}
            preview = self.root_preview(body['change'], session=session)
            if preview['preview_sha256'] != body['preview_sha256']:
                raise RegistryError(409, 'preview_changed', 'La carpeta o su identidad cambió; revisa de nuevo.')
            after = preview['root']
            if after['status'] == 'ACTIVE' and body.get('confirm_path') != after['path']:
                raise RegistryError(409, 'root_unconfirmed', 'Confirma la ruta canónica exacta mostrada.')
            row = session.get(Root, 1)
            before = root_view(row)
            if row is None:
                row = Root(id=1)
                session.add(row)
            for field, value in after.items():
                setattr(row, field, value)
            row.row_sha256, row.updated_at = digest(after), self.runtime.repository._now()
            event = {'action': body['change']['action'], 'before': before, 'after': root_view(row),
                     'preview': preview, 'actor': actor(), 'reason': body.get('reason'),
                     'previous_sha256': before['row_sha256'], 'recorded_at': row.updated_at}
            event['sha256'] = digest(event)
            session.add(RootEvent(version=row.version, idempotency_key=key,
                                  request_sha256=request_sha256, payload=event))
            for operation in session.scalars(select(Operation).where(
                    Operation.status.in_(('INTENDED', 'DIRECTORY_CREATED')))):
                operation.status, operation.diagnostic = 'BLOCKED', 'La revisión de carpeta fue retirada o sustituida.'
                self.repository.event(session, operation, 'root_changed')
            return {**preview, 'replayed': False}

    def authority(self, expected, *, session=None):
        self.require(bootstrap=True)
        root = root_view(session.get(Root, 1)) if session is not None else self.repository.root()
        if root['status'] != 'ACTIVE' or root['version'] != expected:
            raise RegistryError(409, 'root_revoked', 'La autorización de carpeta ya no está vigente.')
        path, info = self.parent(root['path'])
        if info != root['identity']:
            raise RegistryError(409, 'target_identity_changed', 'La identidad del padre cambió.')
        return {k: root[k] for k in ('version', 'path', 'identity', 'row_sha256')}

    def conflicts(self, session, project_id, target, *, operation_id=None):
        self.repository.conflicts(session, project_id, target, operation_id=operation_id)
        self.registry._conflicts(project_id, Path(target), creation_id=operation_id)
        if any(_inside(Path(target), p) for p in self.protected() if p is not None):
            raise RegistryError(422, 'root_service_state', 'El destino entra en conflicto con estado del servicio.')

    def preview(self, body, *, session=None):
        if session is None:
            with Session(self.runtime.engine) as read:
                return self.preview(body, session=read)
        project_id, name = body['project_id'], body['directory_name']
        if not PROJECT_ID.fullmatch(project_id) or project_id in RESERVED_IDS:
            raise RegistryError(422, 'invalid_id', 'Id inválido o reservado.')
        if not PROJECT_ID.fullmatch(name) or name in ('.', '..'):
            raise RegistryError(422, 'invalid_directory_name', 'Nombre de un solo componente [a-z0-9][a-z0-9._-]{0,63}.')
        authority = self.authority(body['root_version'], session=session)
        target = str(Path(authority['path']) / name)
        self.conflicts(session, project_id, target)
        with directory(Path(authority['path'])) as fd:
            if identity(os.fstat(fd)) != authority['identity']:
                raise RegistryError(409, 'target_identity_changed', 'La identidad del padre cambió.')
            if exists(fd, name):
                raise RegistryError(409, 'target_exists', 'El destino ya existe; no se adopta ni sobrescribe.')
        row = {k: v for k, v in body.items() if k not in ('directory_name', 'root_version', 'project_id') and v is not None}
        row.update(id=project_id, root=target, repository_trusted=True, bootstrap_enabled=True)
        composed = self.registry._compose(row, (1, digest(row)), new_directory=True)
        intent = {'contract': CONTRACT, 'authority': authority, 'row': row, 'target': target,
                  'directory_name': name, **composed, 'trust_statement': TRUST, 'permission_statement': PERMISSION}
        return {**intent, 'preview_sha256': digest(intent)}

    def confirm(self, body, key):
        with self.lock:
            with self.runtime.repository._write() as session:
                previous = session.scalar(select(Operation).where(Operation.idempotency_key == key))
                if previous:
                    self.same_request(previous, digest(body))
                    return self.repository.read(previous.id)
                preview = self.preview(body['change'], session=session)
                if body['preview_sha256'] != preview['preview_sha256']:
                    raise RegistryError(409, 'preview_changed', 'La composición o carpeta cambió; revisa de nuevo.')
                if body['trust_root'] != preview['target']:
                    raise RegistryError(409, 'trust_unconfirmed', 'Confirma la confianza en el nuevo checkout exacto.')
                now = self.runtime.repository._now()
                row = Operation(id=str(uuid4()), idempotency_key=key, request_sha256=digest(body), version=0,
                                project_id=body['change']['project_id'], directory_name=preview['directory_name'],
                                target=preview['target'], reserved=True, authority=preview['authority'], intent=preview,
                                intent_sha256=digest(preview), status='INTENDED', created_at=now, updated_at=now)
                session.add(row)
                self.repository.event(session, row, 'intended', reason=body.get('reason'))
                operation_id = row.id
            self.advance(operation_id)
            return self.repository.read(operation_id)

    def check_intent(self, session, row):
        authority = self.authority(row.authority['version'], session=session)
        if authority != row.authority or digest(row.intent) != row.intent_sha256 or row.intent['contract'] != CONTRACT:
            raise RegistryError(409, 'recovery_required', 'Autoridad o intención incompatible; requiere revisión.')
        self.conflicts(session, row.project_id, row.target, operation_id=row.id)
        composed = self.registry._compose(row.intent['row'], (1, digest(row.intent['row'])),
                                          new_directory=row.status == 'INTENDED')
        versions = composed['versions'] if row.status == 'INTENDED' else dict(composed[0].versions)
        profile_sha256 = (composed['profile_details']['sha256'] if row.status == 'INTENDED'
                          else digest(asdict(composed[0].context.profile)))
        if versions != row.intent['versions'] or profile_sha256 != row.intent['profile_details']['sha256']:
            raise RegistryError(409, 'preview_changed', 'La composición congelada cambió; no se continúa.')

    @contextmanager
    def owned_child(self, row):
        with directory(Path(row.authority['path'])) as parent_fd:
            if identity(os.fstat(parent_fd)) != row.authority['identity']:
                raise RegistryError(409, 'target_identity_changed', 'La identidad del padre cambió.')
            fd = os.open(row.directory_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            try:
                if identity(os.fstat(fd)) != row.child_identity:
                    raise RegistryError(409, 'target_identity_changed', 'La identidad del hijo cambió.')
                if os.listdir(fd):
                    raise RegistryError(409, 'target_changed', 'El hijo contiene bytes ajenos; se conserva sin registrar.')
                yield fd
                if identity(os.stat(row.directory_name, dir_fd=parent_fd, follow_symlinks=False)) != row.child_identity:
                    raise RegistryError(409, 'target_identity_changed', 'La identidad del hijo cambió.')
                path, info = self.parent(row.authority['path'])
                if info != row.authority['identity']:
                    raise RegistryError(409, 'target_identity_changed', 'La identidad del padre cambió.')
            finally:
                os.close(fd)

    def advance(self, operation_id):
        try:
            # Intención ya confirmada antes de mkdir. SQLite excluye retirada/cambio durante cada efecto corto.
            with self.runtime.repository._write() as session:
                row = self.repository.require(session, operation_id)
                if row.status == 'INTENDED':
                    self.check_intent(session, row)
                    with directory(Path(row.authority['path'])) as fd:
                        if identity(os.fstat(fd)) != row.authority['identity']:
                            raise RegistryError(409, 'target_identity_changed', 'La identidad del padre cambió.')
                        if exists(fd, row.directory_name):
                            raise RegistryError(409, 'recovery_required', 'Hay un destino sin prueba de propiedad; se conserva.')
                        os.mkdir(row.directory_name, mode=0o755, dir_fd=fd)
                        child = os.open(row.directory_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                        try:
                            row.child_identity = identity(os.fstat(child))
                        finally:
                            os.close(child)
                        os.fsync(fd)
                        if self.parent(row.authority['path'])[1] != row.authority['identity']:
                            raise RegistryError(409, 'target_identity_changed', 'La identidad del padre cambió.')
                    row.status = 'DIRECTORY_CREATED'
                    self.repository.event(session, row, 'directory_created')
            with self.runtime.repository._write() as session:
                row = self.repository.require(session, operation_id)
                if row.status != 'DIRECTORY_CREATED':
                    return
                self.check_intent(session, row)
                with self.owned_child(row):
                    intent = row.intent
                    now = self.runtime.repository._now()
                    project = Project(id=row.project_id, version=1, status='ACTIVE', root=row.target,
                                      composition=intent['row']['composition'], profile=intent['profile'], row=intent['row'],
                                      row_sha256=digest(intent['row']), creation_id=row.id,
                                      trust={'confirmed': True, 'root': row.target, 'statement': TRUST, 'actor': actor()},
                                      created_at=now, updated_at=now)
                    session.add(project)
                    session.flush()
                    session.add(ProjectEvent(project_id=project.id, version=1, action='register', row=project.row,
                                             row_sha256=project.row_sha256, previous_sha256=None,
                                             preview_sha256=intent['preview_sha256'], actor=actor(),
                                             reason='Creación confirmada ' + row.id, recorded_at=now))
                    row.status, row.reserved = 'REGISTERED', False
                    row.result = {'project_id': project.id, 'root': project.root, 'creation_id': row.id}
                    self.repository.event(session, row, 'registered')
            self.registry.load()
        except (RegistryError, OSError) as error:
            with self.runtime.repository._write() as session:
                row = self.repository.require(session, operation_id)
                if row.status == 'REGISTERED':
                    raise
                row.status = 'RECOVERY_REQUIRED' if isinstance(error, OSError) or error.code == 'recovery_required' else 'BLOCKED'
                row.diagnostic = str(error) if isinstance(error, RegistryError) else 'Efecto filesystem incierto; no se borra ni reintenta.'
                self.repository.event(session, row, 'stopped')

    def resume_preview(self, operation_id, body, *, session=None):
        if session is None:
            with Session(self.runtime.engine) as read:
                return self.resume_preview(operation_id, body, session=read)
        row = self.repository.require(session, operation_id)
        if row.version != body['expected_version']:
            raise RegistryError(409, 'stale_version', 'La operación cambió; vuelve a cargarla.')
        if row.status in ('REGISTERED', 'CANCELLED', 'RECOVERY_REQUIRED'):
            raise RegistryError(409, 'recovery_required', 'Esta operación no puede reanudarse automáticamente.')
        authority = self.authority(body['root_version'], session=session)
        if (authority['path'], authority['identity']) != (row.authority['path'], row.authority['identity']):
            raise RegistryError(409, 'target_identity_changed', 'Se requiere el mismo padre y su identidad original.')
        if row.child_identity is None:
            if authority != row.authority or os.path.lexists(row.target):
                raise RegistryError(409, 'recovery_required', 'No hay prueba de propiedad o la autorización original caducó.')
        else:
            with self.owned_child(row):
                pass
        self.conflicts(session, row.project_id, row.target, operation_id=row.id)
        composed = self.registry._compose(row.intent['row'], (1, digest(row.intent['row'])),
                                          new_directory=row.child_identity is None)
        versions = composed['versions'] if row.child_identity is None else dict(composed[0].versions)
        profile_sha256 = (composed['profile_details']['sha256'] if row.child_identity is None
                          else digest(asdict(composed[0].context.profile)))
        if versions != row.intent['versions'] or profile_sha256 != row.intent['profile_details']['sha256']:
            raise RegistryError(409, 'preview_changed', 'La composición original cambió; requiere resolución explícita.')
        preview = {'operation_id': row.id, 'expected_version': row.version, 'authority': authority,
                   'intent_sha256': row.intent_sha256, 'target': row.target}
        return {**preview, 'preview_sha256': digest(preview)}

    def resume(self, operation_id, body, key):
        with self.lock:
            with self.runtime.repository._write() as session:
                replay = session.scalar(select(Event).where(Event.idempotency_key == key))
                request_sha256 = digest({'operation_id': operation_id, **body})
                if replay:
                    self.same_request(replay, request_sha256)
                    return self.repository.read(operation_id)
                preview = self.resume_preview(operation_id, body['change'], session=session)
                if preview['preview_sha256'] != body['preview_sha256']:
                    raise RegistryError(409, 'preview_changed', 'La reanudación cambió; revisa de nuevo.')
                row = self.repository.require(session, operation_id)
                row.authority = preview['authority']
                row.status, row.diagnostic = ('DIRECTORY_CREATED' if row.child_identity else 'INTENDED'), None
                self.repository.event(session, row, 'resume_confirmed', reason=body.get('reason'), key=key,
                                      request_sha256=request_sha256)
            self.advance(operation_id)
            return self.repository.read(operation_id)

    def cancel(self, operation_id, body, key):
        with self.lock, self.runtime.repository._write() as session:
            replay = session.scalar(select(Event).where(Event.idempotency_key == key))
            request_sha256 = digest({'operation_id': operation_id, **body})
            if replay:
                self.same_request(replay, request_sha256)
                return self.repository.read(operation_id)
            row = self.repository.require(session, operation_id)
            if row.version != body['expected_version'] or body['intent_sha256'] != row.intent_sha256:
                raise RegistryError(409, 'stale_version', 'La operación cambió; vuelve a cargarla.')
            if row.status == 'REGISTERED' or (row.status == 'CANCELLED' and not row.reserved):
                raise RegistryError(409, 'recovery_required', 'La operación ya terminó.')
            # Liberar solo si se acredita ausencia bajo el mismo padre. Nunca borrar ni adoptar.
            try:
                with directory(Path(row.authority['path'])) as fd:
                    if identity(os.fstat(fd)) == row.authority['identity'] and not exists(fd, row.directory_name):
                        row.reserved = False
            except OSError:
                pass
            row.status = 'CANCELLED'
            row.diagnostic = 'Cancelada; se conservan carpeta y reserva inciertas.' if row.reserved else 'Cancelada sin destino.'
            self.repository.event(session, row, 'cancelled', reason=body.get('reason'), key=key,
                                  request_sha256=request_sha256)
            operation_id = row.id
        return self.repository.read(operation_id)
