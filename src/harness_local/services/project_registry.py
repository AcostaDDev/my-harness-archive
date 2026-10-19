"""Alta, cambio y baja de proyectos desde la UI sobre `local-config-3/4/5` (D078/D095).

El TOML sigue siendo la autoridad de lo que se ejecuta; el registro solo guarda
datos no ejecutables (raíz canónica, confianza, composición nombrada, política,
documentos, bootstrap, tag y techo de permisos). Cada cambio pasa por una vista
previa cuyo hash liga la acción, la versión esperada, la fila resultante y la
composición congelada; la confianza en la raíz es una confirmación aparte. El
proyecto se incorpora al runtime sin reiniciar: la versión del registro entra en
el hash congelado, y un job admitido con otra composición queda en cuarentena.
"""
import hashlib
import os
from pathlib import Path
import stat
from threading import RLock

from harness_local.core.engine.contracts import freeze
from harness_local.services.managed_runtime import PROJECT_ID, ManagedConfig, validate_projects
from harness_local.storage.permissions import actor
from harness_local.storage.registry import ProjectRegistryRepository, RegistryConflict

# `/projects/new` es la página de alta; el resto de ids siguen la forma de `PROJECT_ID`.
RESERVED_IDS = frozenset({'new'})
ACTIONS = ('register', 'update', 'retire')
TRUST = ('Confío en el contenido de este checkout: los agentes y los comandos de la composición elegida '
         'se ejecutarán dentro de él con la configuración del operador.')


class RegistryError(ValueError):
    def __init__(self, status, code, diagnostic):
        super().__init__(diagnostic)
        self.status, self.code = status, code


def digest(value):
    return hashlib.sha256(freeze(value).encode()).hexdigest()


def _location(path):
    """Identidad del ancestro existente y sufijo pendiente; también reconoce alias de caso del filesystem."""
    suffix = []
    for current in (path, *path.parents):
        try:
            info = os.lstat(current)
            return info.st_dev, info.st_ino, tuple(reversed(suffix))
        except FileNotFoundError:
            suffix.append(current.name)
        except OSError:
            return None
    return None


def _within(path, parent):
    if path.is_relative_to(parent):
        return True
    boundary = _location(parent)
    return boundary is not None and any(_location(ancestor) == boundary for ancestor in (path, *path.parents))


def _inside(path, other):
    return _within(path, other) or _within(other, path)


def canonical_root(value, authorized):
    """Raíz absoluta, existente, sin enlaces en ningún componente y bajo una raíz autorizada."""
    if not isinstance(value, str) or not value or '\0' in value:
        raise RegistryError(422, 'root_invalid', 'Ruta de texto requerida.')
    path = Path(value)
    if not path.is_absolute():
        raise RegistryError(422, 'root_not_absolute', 'La raíz debe ser una ruta absoluta.')
    if str(path) != os.path.normpath(value) or '..' in path.parts:
        raise RegistryError(422, 'root_not_canonical', 'La raíz debe estar en forma canónica, sin «..» ni barras finales.')
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            raise RegistryError(422, 'root_missing', f'No existe {current}.') from None
        except OSError as exc:
            raise RegistryError(422, 'root_unreadable', f'{current}: {exc.strerror}') from None
        if stat.S_ISLNK(info.st_mode):
            raise RegistryError(422, 'root_symlink', f'{current} es un enlace simbólico; usa la ruta real.')
    if not stat.S_ISDIR(os.lstat(path).st_mode):
        raise RegistryError(422, 'root_not_directory', 'La raíz debe ser un directorio.')
    if path.resolve() != path:
        raise RegistryError(422, 'root_not_canonical', 'La raíz no coincide con su ruta real.')
    if not any(path.is_relative_to(root) for root in authorized):
        raise RegistryError(422, 'root_not_authorized',
                            'La raíz no está bajo ninguna raíz autorizada por el operador ([registration].roots).')
    return path


class ProjectRegistry:
    """Servicio del registro dentro del runtime gestionado; un cambio cada vez en este proceso."""

    def __init__(self, runtime):
        self.runtime = runtime
        self.repository = ProjectRegistryRepository(runtime.repository)
        self.unavailable: dict[str, str] = {}
        self._lock = RLock()

    @property
    def registrar(self):
        registrar = self.runtime.config.registrar
        return registrar if registrar is not None and registrar.registrable else None

    def _require(self):
        if self.registrar is None:
            raise RegistryError(409, 'registry_unavailable',
                                'La configuración del servicio no admite registrar proyectos '
                                '(requiere local-config-3/4/5 con [registration] y al menos una composición).')
        return self.registrar

    # --- composición ------------------------------------------------------------------

    def _compose(self, row, registry, *, new_directory=False):
        from harness_local.services.local_config import LocalConfigError
        registrar = self._require()
        try:
            composed = registrar.compose(row, 'registro', registry=registry, new_directory=new_directory)
            if new_directory:
                return composed
            # Mismas comprobaciones que un proyecto del TOML (techo de permisos, bootstrap, tag).
            validate_projects(ManagedConfig((composed[0],), ports_factory=registrar.ports,
                                            commit_factory=registrar.writer))
        except (LocalConfigError, ValueError) as exc:
            raise RegistryError(422, 'invalid_request', str(exc)) from None
        return composed

    def load(self):
        """Al arrancar: compone las filas activas. Una fila que ya no compone queda no disponible, con motivo."""
        self.unavailable = {}
        for item in self.repository.rows():
            if item['status'] != 'ACTIVE':
                continue
            try:
                self._conflicts(item['id'], Path(item['root']), registered=True)
                composed = self._compose(item['row'], (item['version'], item['row_sha256']))
                self.runtime.install(self.registrar.install(composed))
            except RegistryError as exc:
                self.unavailable[item['id']] = str(exc)

    def _conflicts(self, project_id, root, *, registered=False, creation_id=None):
        """Ids únicos frente al TOML; raíces ni iguales ni anidadas; estado del servicio fuera."""
        # Las intenciones inciertas siguen reservadas, también frente al alta existente D078.
        from harness_local.storage.project_creation import CreationRepository
        for operation in CreationRepository(self.runtime.repository).operations():
            if (operation['reserved'] and operation['id'] != creation_id
                    and (operation['project_id'] == project_id or _inside(root, Path(operation['target'])))):
                raise RegistryError(409, 'target_reserved', 'Id o destino reservado por una creación pendiente.')
        for other in self.runtime.projects.values():
            if other.id == project_id:
                if not registered or 'project_registry' not in other.versions:
                    raise RegistryError(409, 'duplicate_id', f'El id {project_id} ya lo usa otro proyecto.')
                continue
            if _inside(root, other.context.root):
                raise RegistryError(409, 'root_taken', f'La raíz coincide o se anida con la de {other.id}.')
        for path, name in ((self.runtime.database, 'la base SQLite'),
                           (self.runtime.migration.migrations_dir, 'el directorio de migraciones')):
            if path is not None and _inside(root, path):
                raise RegistryError(422, 'root_service_state', f'La raíz no puede contener {name} del servicio.')

    # --- lecturas ---------------------------------------------------------------------

    def options(self):
        registrar = self.registrar
        rows = self.repository.rows()
        return {'available': registrar is not None,
                'format': self.runtime.config.registrar.format if self.runtime.config.registrar else None,
                'creation_available': registrar is not None and registrar.bootstrap_enabled,
                **({key: value for key, value in registrar.options().items() if key != 'format'} if registrar else
                   {'roots': [], 'bootstrap_enabled': False, 'compositions': [], 'executor_provider': None,
                    'reviewer_provider': None, 'executor_effort_vocabulary': []}),
                'reserved_ids': sorted(RESERVED_IDS),
                'operator_projects': sorted(p.id for p in self.runtime.projects.values()
                                            if 'project_registry' not in p.versions),
                'projects': [self._summary(item) for item in rows], 'trust_statement': TRUST}

    def _summary(self, item):
        return {**{key: item[key] for key in ('id', 'version', 'status', 'root', 'composition', 'profile',
                                              'row_sha256', 'created_at', 'updated_at', 'creation_id')},
                'available': item['status'] == 'ACTIVE' and item['id'] not in self.unavailable,
                'diagnostic': self.unavailable.get(item['id'])}

    def read(self, project_id):
        item = self.repository.get(project_id)
        if item is None:
            raise LookupError('Proyecto registrado desconocido.')
        return {**self._summary(item), 'row': item['row'], 'trust': item['trust'],
                'unfinished_jobs': self.repository.unfinished(item['root']) if item['status'] == 'ACTIVE' else [],
                'configuration_blockers': self.repository.configuration_blockers(item['root'])
                if self.registrar and self.registrar.format == 'local-config-5' else [],
                'history': self.repository.history(project_id)}

    # --- vista previa y confirmación --------------------------------------------------

    def _target(self, body, current):
        action = body['action']
        if action == 'retire':
            return dict(current['row'])
        registrar = self._require()
        if action == 'register':
            project_id = body['project_id']
            root = str(canonical_root(body.get('root'), registrar.roots))
        else:
            project_id, root = current['id'], current['root']
            if body.get('root') not in (None, root):
                raise RegistryError(422, 'root_immutable', 'La raíz no cambia: da de baja el proyecto y registra otro.')
        if body.get('bootstrap_enabled') and not registrar.bootstrap_enabled:
            raise RegistryError(422, 'bootstrap_not_allowed', 'El operador no autoriza bootstrap en proyectos registrados.')
        row = {'id': project_id, 'root': root, 'repository_trusted': True, 'composition': body.get('composition'),
               'policy': body.get('policy'), 'tag_kind': body.get('tag_kind', 'lightweight'),
               'bootstrap_enabled': bool(body.get('bootstrap_enabled', False))}
        if body.get('documents') is not None:
            row['documents'] = body['documents']
        if body.get('permission_authority') is not None:
            row['permission_authority'] = body['permission_authority']
        if body.get('agent_selection') is not None:
            row['agent_selection'] = body['agent_selection']
        return row

    def preview(self, body):
        action, project_id = body['action'], body['project_id']
        if action not in ACTIONS:
            raise RegistryError(422, 'invalid_request', f'Acción {action!r} desconocida.')
        registrar = self._require()
        if not isinstance(project_id, str) or not PROJECT_ID.fullmatch(project_id):
            raise RegistryError(422, 'invalid_id', 'Id con la forma [a-z0-9][a-z0-9._-]{0,63} requerido.')
        if project_id in RESERVED_IDS:
            raise RegistryError(422, 'invalid_id', f'El id {project_id!r} está reservado por la interfaz.')
        current = self.repository.get(project_id)
        expected = body['expected_version']
        if action == 'register':
            if current is not None:
                raise RegistryError(409, 'duplicate_id', f'El id {project_id} ya está registrado'
                                    + (' (dado de baja; su historial se conserva).' if current['status'] != 'ACTIVE' else '.'))
            if project_id in self.runtime.projects:
                raise RegistryError(409, 'duplicate_id', f'El id {project_id} lo declara el TOML del operador.')
        elif current is None:
            raise LookupError('Proyecto registrado desconocido; los proyectos del TOML no se editan desde la UI.')
        elif current['status'] != 'ACTIVE':
            raise RegistryError(409, 'retired', 'El proyecto está dado de baja; su historial se conserva.')
        if (current['version'] if current else 0) != expected:
            raise RegistryError(409, 'stale_version', 'El registro cambió; vuelve a cargar antes de revisar.')
        row = self._target(body, current)
        version = expected + 1
        if action == 'retire':
            versions = None
        else:
            self._conflicts(project_id, Path(row['root']), registered=action == 'update')
            composed = self._compose(row, (version, digest(row)))
            versions = dict(composed[0].versions)
        row_sha256 = digest(row)
        status = 'RETIRED' if action == 'retire' else 'ACTIVE'
        before = current['row'] if current else {}
        changes = [{'field': key, 'before': before.get(key), 'after': row.get(key)}
                   for key in sorted(set(before) | set(row)) if before.get(key) != row.get(key)]
        if action == 'retire':
            changes = [{'field': 'status', 'before': 'ACTIVE', 'after': 'RETIRED'}]
        unfinished = self.repository.unfinished(row['root']) if action != 'register' else []
        blockers = self.repository.configuration_blockers(row['root']) if (
            action != 'register' and registrar.format == 'local-config-5') else []
        preview_sha256 = digest({'action': action, 'project_id': project_id, 'expected_version': expected,
                                 'current_sha256': current['row_sha256'] if current else None, 'status': status,
                                 'row_sha256': row_sha256, 'versions': versions})
        return {'action': action, 'project_id': project_id, 'expected_version': expected, 'version': version,
                'status': status, 'row': row, 'row_sha256': row_sha256, 'changes': changes, 'versions': versions,
                'profile': current['profile'] if action == 'retire' else registrar.compositions[row['composition']][0],
                'trust_required': action == 'register', 'trust_statement': TRUST if action == 'register' else None,
                'unfinished_jobs': unfinished, 'configuration_blockers': blockers, 'preview_sha256': preview_sha256}

    def apply(self, body, *, preview_sha256, trust_root=None, reason=None):
        with self._lock:
            replayed = self.repository.replay(body['project_id'], body['expected_version'], preview_sha256)
            if replayed is not None:
                return {'project': self._summary(replayed), 'replayed': True}
            shown = self.preview(body)
            if shown['preview_sha256'] != preview_sha256:
                raise RegistryError(409, 'preview_changed', 'La vista previa ya no coincide; revísala de nuevo.')
            if shown['unfinished_jobs']:
                raise RegistryError(409, 'pending_jobs', f'El checkout tiene trabajos sin terminar '
                                    f'({shown["unfinished_jobs"]}); espera o concílialos antes de cambiarlo.')
            if shown['configuration_blockers']:
                raise RegistryError(409, 'pending_configuration', '; '.join(shown['configuration_blockers']))
            trust = None
            if shown['trust_required']:
                if trust_root != shown['row']['root']:
                    raise RegistryError(409, 'trust_unconfirmed',
                                        'Confirma la confianza en el checkout escribiendo su raíz exacta.')
                trust = {'confirmed': True, 'root': trust_root, 'statement': TRUST, 'actor': actor()}
            try:
                saved = self.repository.apply(shown['action'], shown['project_id'],
                                              expected_version=shown['expected_version'], row=shown['row'],
                                              row_sha256=shown['row_sha256'], profile=shown['profile'],
                                              preview_sha256=preview_sha256, trust=trust, reason=reason,
                                              protect_agents=self.registrar.format == 'local-config-5')
            except RegistryConflict as exc:
                raise RegistryError(409, exc.code, str(exc)) from None
            self.unavailable.pop(saved['id'], None)
            if saved['status'] == 'ACTIVE':
                composed = self._compose(saved['row'], (saved['version'], saved['row_sha256']))
                self.runtime.install(self.registrar.install(composed))
            else:
                self.runtime.uninstall(saved['id'])
                self.registrar.forget(Path(saved['root']))
            return {'project': self._summary(saved), 'replayed': False}
