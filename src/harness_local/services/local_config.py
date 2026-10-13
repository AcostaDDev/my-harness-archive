"""Operator TOML outside managed checkouts → explicit ManagedConfig (`local-config-2`).

`local-config-2` (D052) declares `[agents.reviewer]` and `[agents.executor]`,
each Codex or Claude. `local-config-1` is still read as Codex reviewer and
Claude executor with its own policy (separate planner selection).

Loading never launches processes or reads managed repositories. Trust,
executables, environment, models and command authorizations come only from
this file; there are no implicit defaults for them. Provider authentication
stays with each installed CLI: the file must not contain secrets.
"""
from dataclasses import asdict
import hashlib
import importlib.metadata
import math
import os
from pathlib import Path
import pwd
import stat
import tomllib

from harness_local.adapters.cli_agents import EFFORTS, CLIConfig, CLIProcessAdapter
from harness_local.adapters.commands import CommandConfig, ManagedCommandRunner
from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.commit import GitIdentity
from harness_local.core.engine.context import Command, EnginePolicy, ProjectContext
from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.journal import JournalError
from harness_local.profiles.typescript_web import typescript_web_profile
from harness_local.services.managed_runtime import (PROJECT_ID, ManagedConfig, ManagedProject, agents_view,
                                                    validate_projects)

VERSION = 'local-config-2'
FORMATS = ('local-config-1', VERSION)
CLI_KEYS = ('executable', 'cli_version', 'timeout_seconds', 'environment')
TOOL_KEYS = ('tools', 'allowed_tools', 'grantable_tools')
CONFIG_ENV = 'HARNESS_LOCAL_CONFIG'
MAX_BYTES = 65536
PROFILES = {'typescript-web': typescript_web_profile}


class LocalConfigError(ValueError):
    pass


def _fields(value, where, required, optional=()):
    if not isinstance(value, dict):
        raise LocalConfigError(f'{where}: se esperaba una tabla')
    unknown = set(value) - set(required) - set(optional)
    missing = set(required) - set(value)
    if unknown or missing:
        raise LocalConfigError(f'{where}: claves desconocidas {sorted(unknown)} / ausentes {sorted(missing)}')
    return value


def _text(value, where):
    if not isinstance(value, str) or not value.strip() or '\0' in value:
        raise LocalConfigError(f'{where}: texto no vacío requerido')
    return value


def _flag(value, where):
    if type(value) is not bool:
        raise LocalConfigError(f'{where}: booleano explícito requerido')
    return value


def _number(value, where):
    if type(value) not in (int, float) or not math.isfinite(value) or not value > 0:
        raise LocalConfigError(f'{where}: número positivo finito requerido')
    return value


def _texts(value, where, *, empty=False):
    if not isinstance(value, list) or (not value and not empty):
        raise LocalConfigError(f'{where}: lista de textos requerida')
    return tuple(_text(item, where) for item in value)


def _path(value, where, *, kind):
    path = Path(_text(value, where))
    if not path.is_absolute() or path.resolve() != path:
        raise LocalConfigError(f'{where}: ruta absoluta canónica requerida (sin enlaces)')
    if kind == 'directory' and not path.is_dir():
        raise LocalConfigError(f'{where}: directorio existente requerido')
    if kind == 'executable' and not (path.is_file() and os.access(path, os.X_OK)):
        raise LocalConfigError(f'{where}: ejecutable existente requerido')
    return path


def _executable(value, where):
    """Only the command itself is checked here; operators may name versioned symlinks."""
    path = Path(_text(value, where))
    if not path.is_absolute() or not path.is_file() or not os.access(path, os.X_OK):
        raise LocalConfigError(f'{where}: ejecutable absoluto existente requerido; sin búsqueda en PATH')
    return str(path)


def _environment(value, where):
    if not isinstance(value, dict) or any(not isinstance(v, str) or '\0' in v for v in value.values()):
        raise LocalConfigError(f'{where}: tabla de entorno explícita con valores de texto requerida')
    return tuple(sorted((_text(key, where), item) for key, item in value.items()))


def _read(path):
    if not path.is_absolute() or path.resolve() != path:
        raise LocalConfigError('Configuración local: ruta absoluta canónica requerida')
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as exc:
        raise LocalConfigError(f'Configuración local ilegible: {exc.strerror}') from None
    with os.fdopen(fd, 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_BYTES:
            raise LocalConfigError('Configuración local: archivo regular único de hasta 64 KiB')
        if info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise LocalConfigError('Configuración local: propietario del servicio y sin escritura de grupo/otros')
        raw = stream.read(MAX_BYTES + 1)
    try:
        return tomllib.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise LocalConfigError(f'Configuración local: TOML UTF-8 inválido ({exc})') from None


def _cli(where, provider, value, required=CLI_KEYS, optional=()):
    value = _fields(value, where, required, optional)
    argv = _texts(value['executable'], f'{where}.executable')
    environment = _environment(value['environment'], f'{where}.environment')
    user = dict(environment).get('USER')
    try:
        local = pwd.getpwuid(os.getuid()).pw_name
    except KeyError:
        raise LocalConfigError('No se puede resolver la cuenta del UID local') from None
    if user != local:
        raise LocalConfigError(f'{where}.environment.USER debe ser la cuenta del UID local (D024)')
    try:
        return CLIConfig(provider, (_executable(argv[0], f'{where}.executable'), *argv[1:]),
                         _text(value['cli_version'], f'{where}.cli_version'), environment,
                         _number(value['timeout_seconds'], f'{where}.timeout_seconds'),
                         *(_texts(value.get(key, []), f'{where}.{key}', empty=True) for key in TOOL_KEYS))
    except LocalConfigError:
        raise
    except ValueError as exc:
        raise LocalConfigError(f'{where}: {exc}') from None


def _agents(data):
    """`local-config-2`: the user fixes provider, model and effort of the reviewer."""
    data = _fields(data, 'agents', ('reviewer', 'executor'))
    agents, reviewer = {}, None
    for agent in ('reviewer', 'executor'):
        where = f'agents.{agent}'
        value = data[agent]
        provider = _text(value.get('provider') if isinstance(value, dict) else None, f'{where}.provider')
        if provider not in EFFORTS:
            raise LocalConfigError(f'{where}.provider: proveedores admitidos {sorted(EFFORTS)}')
        if agent == 'reviewer':
            value = _fields(value, where, ('provider', 'model', 'effort', *CLI_KEYS))
            reviewer = (_text(value['model'], f'{where}.model'), _text(value['effort'], f'{where}.effort'))
            if reviewer[1] not in EFFORTS[provider]:
                raise LocalConfigError(f'{where}.effort: vocabulario de {provider} {list(EFFORTS[provider])}')
            optional = ()
        else:
            optional = TOOL_KEYS if provider == 'claude' else ()
        own = ('provider', 'model', 'effort') if agent == 'reviewer' else ('provider',)
        agents[agent] = _cli(where, provider, {k: v for k, v in value.items() if k not in own}, optional=optional)
    return agents, reviewer


def _commands(value, where, root, profile):
    value = _fields(value, where, ('executables', 'environment', 'authorize_profile_commands'),
                    ('max_timeout_seconds', 'max_output_bytes', 'authorized'))
    if not isinstance(value['executables'], dict) or not value['executables']:
        raise LocalConfigError(f'{where}.executables: tabla nombre → ejecutable requerida')
    executables = tuple(sorted((_text(name, where), _executable(path, f'{where}.executables.{name}'))
                               for name, path in value['executables'].items()))
    required = profile.preparation + profile.validations
    authorized = required if _flag(value['authorize_profile_commands'], f'{where}.authorize_profile_commands') else ()
    extras = value.get('authorized', [])
    if not isinstance(extras, list):
        raise LocalConfigError(f'{where}.authorized: lista de comandos exactos requerida')
    for index, item in enumerate(extras):
        label = f'{where}.authorized[{index}]'
        item = _fields(item, label, ('argv', 'timeout_seconds'), ('cwd', 'environment'))
        try:
            command = Command(_texts(item['argv'], f'{label}.argv'), _text(item.get('cwd', '.'), f'{label}.cwd'),
                              _environment(item.get('environment', {}), f'{label}.environment'),
                              _number(item['timeout_seconds'], f'{label}.timeout_seconds'))
        except LocalConfigError:
            raise
        except ValueError as exc:
            raise LocalConfigError(f'{label}: {exc}') from None
        if command not in authorized:
            authorized += (command,)
    if any(command not in authorized for command in required):
        raise LocalConfigError(f'{where}: autorizar exactamente todos los comandos del perfil')
    try:
        return CommandConfig(str(root), True, authorized, executables,
                             _environment(value['environment'], f'{where}.environment'),
                             **{key: value[key] for key in ('max_timeout_seconds', 'max_output_bytes') if key in value})
    except LocalConfigError:
        raise
    except ValueError as exc:
        raise LocalConfigError(f'{where}: {exc}') from None


def _policy(value, where, reviewer, executor_provider):
    """`reviewer` is None for `local-config-1`, whose policy keeps its own planner/reviewer selections."""
    if reviewer is None:
        value = _fields(value, where, ('executor_models', 'executor_efforts', 'planner_model', 'planner_effort',
                        'reviewer_model', 'reviewer_effort'), ('max_revision_cycles', 'planning_mode'))
        selections = tuple(_text(value[key], f'{where}.{key}') for key in
                           ('planner_model', 'planner_effort', 'reviewer_model', 'reviewer_effort'))
        extra = {key: value[key] for key in ('max_revision_cycles', 'planning_mode') if key in value}
    else:
        # D052: explicit settings; the reviewer always plans with its own selection.
        value = _fields(value, where, ('planning_mode', 'executor_mode', 'executor_models', 'executor_efforts'),
                        ('max_revision_cycles',))
        if value['planning_mode'] not in ('agent', 'deterministic'):
            raise LocalConfigError(f'{where}.planning_mode: "agent" o "deterministic"')
        if value['executor_mode'] not in ('catalog', 'open'):
            raise LocalConfigError(f'{where}.executor_mode: "catalog" o "open"')
        selections = reviewer * 2
        extra = {key: value[key] for key in ('max_revision_cycles', 'planning_mode', 'executor_mode') if key in value}
        extra['executor_effort_vocabulary'] = EFFORTS[executor_provider]
    if 'max_revision_cycles' in extra and type(extra['max_revision_cycles']) is not int:
        raise LocalConfigError(f'{where}.max_revision_cycles: entero requerido')
    try:
        return EnginePolicy(_texts(value['executor_models'], f'{where}.executor_models'),
                            _texts(value['executor_efforts'], f'{where}.executor_efforts'), *selections, **extra)
    except LocalConfigError:
        raise
    except (TypeError, ValueError) as exc:
        raise LocalConfigError(f'{where}: {exc}') from None


def _outside(path, root):
    return not (path.is_relative_to(root) or root.is_relative_to(path))


def _build(data, source):
    if not isinstance(data, dict) or data.get('format') not in FORMATS:
        raise LocalConfigError(f'format debe ser uno de {list(FORMATS)}')
    fmt = data['format']
    agents_key = 'providers' if fmt == 'local-config-1' else 'agents'
    data = _fields(data, 'raíz', ('format', 'service', 'git', agents_key, 'projects'))
    service = _fields(data['service'], 'service', ('state_dir', 'supervisor'), ('lease_seconds', 'poll_seconds'))
    state = _path(service['state_dir'], 'service.state_dir', kind='directory')
    git = _fields(data['git'], 'git', ('executable', 'author_name', 'author_email'))
    try:
        identity = GitIdentity(git['author_name'], git['author_email'])
    except ValueError as exc:
        raise LocalConfigError(f'git: {exc}') from None
    git_executable = _executable(git['executable'], 'git.executable')
    if fmt == 'local-config-1':
        providers = _fields(data['providers'], 'providers', ('codex', 'claude'))
        agents = {'reviewer': _cli('providers.codex', 'codex', providers['codex']),
                  'executor': _cli('providers.claude', 'claude', providers['claude'], optional=TOOL_KEYS)}
        reviewer = None
    else:
        agents, reviewer = _agents(data['agents'])
    if not isinstance(data['projects'], list) or not data['projects']:
        raise LocalConfigError('projects: al menos un [[projects]] requerido')
    try:
        engine = importlib.metadata.version('harness-local')
    except importlib.metadata.PackageNotFoundError:
        raise LocalConfigError('Versión del paquete harness-local no disponible') from None

    projects, compositions = [], {}
    for index, item in enumerate(data['projects']):
        where = f'projects[{index}]'
        item = _fields(item, where, ('id', 'root', 'repository_trusted', 'profile', 'policy', 'commands'),
                       ('tag_kind', 'permission_authority'))
        if _flag(item['repository_trusted'], f'{where}.repository_trusted') is not True:
            raise LocalConfigError(f'{where}: sin confianza explícita el proyecto no se registra')
        root = _path(item['root'], f'{where}.root', kind='directory')
        if not (_outside(state, root) and _outside(source, root)):
            raise LocalConfigError(f'{where}: configuración y estado deben quedar fuera del checkout')
        if _text(item['profile'], f'{where}.profile') not in PROFILES:
            raise LocalConfigError(f'{where}.profile: perfiles admitidos {sorted(PROFILES)}')
        profile = PROFILES[item['profile']]()
        engine_policy = _policy(item['policy'], f'{where}.policy', reviewer, agents['executor'].provider)
        commands = _commands(item['commands'], f'{where}.commands', root, profile)
        identifier = _text(item['id'], f'{where}.id')
        if not PROJECT_ID.fullmatch(identifier):
            raise LocalConfigError(f'{where}.id: [a-z0-9][a-z0-9._-]{{0,63}} requerido')
        artifacts = state / 'artifacts' / identifier
        try:
            cli = CLIProcessAdapter(agents, artifacts)
        except ValueError as exc:
            raise LocalConfigError(f'agents: {exc}') from None
        runner = ManagedCommandRunner(commands)
        if identifier in {p.id for p in projects} or root in compositions:
            raise LocalConfigError(f'{where}: id o raíz duplicados')
        try:
            digest = hashlib.sha256(freeze({'project': item, agents_key: data[agents_key], 'git': git,
                                            'state_dir': str(state)}).encode()).hexdigest()
        except (TypeError, ValueError):
            raise LocalConfigError(f'{where}: valores TOML no admitidos (fechas u objetos)') from None
        versions = {'engine': f'harness-local-{engine}', 'evidence': 'git-1', 'provider_cli': None,
                    'local_config': fmt, 'profile': profile.name,
                    'local_config_sha256': digest,
                    **cli.frozen_versions(), **runner.frozen_versions()}
        context = ProjectContext(root, profile, engine_policy)
        projects.append(ManagedProject(identifier, context, versions, item.get('permission_authority'),
                                       item.get('tag_kind', 'lightweight')))
        compositions[root] = (identifier, versions, commands, artifacts)

    def composed(context, versions):
        try:
            identifier, current, commands, artifacts = compositions[context.root]
        except KeyError:
            raise JournalError('Checkout sin composición local registrada') from None
        if any(versions.get(key) != value for key, value in current.items()):
            raise JournalError(f'Composición local de {identifier} distinta de la congelada; no se ejecuta')
        return commands, artifacts

    def ports(context, versions):
        commands, artifacts = composed(context, versions)
        return (CLIProcessAdapter(agents, artifacts), ManagedCommandRunner(commands),
                GitWorkspace(identity, executable=git_executable))

    def writer(context, versions):
        composed(context, versions)
        return GitWorkspace(identity, executable=git_executable)

    config = ManagedConfig(tuple(projects), ports_factory=ports, commit_factory=writer,
                           supervisor=_flag(service['supervisor'], 'service.supervisor'),
                           lease_seconds=_number(service.get('lease_seconds', 30.0), 'service.lease_seconds'),
                           poll_seconds=_number(service.get('poll_seconds', 0.5), 'service.poll_seconds'),
                           migrations_dir=state / 'migrations')
    try:
        validate_projects(config)
    except ValueError as exc:
        raise LocalConfigError(str(exc)) from None
    return config, agents


def build(data, source) -> ManagedConfig:
    return _build(data, source)[0]


def load_local_config(path) -> ManagedConfig:
    path = Path(path)
    return build(_read(path), path)


def inspect_local_config(path) -> tuple[ManagedConfig, dict[str, CLIConfig]]:
    """For check-config: the validated reviewer/executor CLI configurations shared by every project."""
    path = Path(path)
    return _build(_read(path), path)


def from_environment() -> ManagedConfig:
    """Development entry for `HARNESS_MANAGED_CONFIG=harness_local.services.local_config:from_environment`."""
    value = os.environ.get(CONFIG_ENV)
    if not value:
        raise LocalConfigError(f'{CONFIG_ENV} debe nombrar el TOML local')
    return load_local_config(value)


def summary(config: ManagedConfig) -> dict:
    """Identifiers, roots and frozen versions only: environment values never leave the file."""
    return {'format': config.projects[0].versions['local_config'], 'supervisor': config.supervisor,
            'projects': [{'id': p.id, 'root': str(p.context.root), 'profile': p.context.profile.name,
                          'policy': asdict(p.context.policy), 'agents': agents_view(p), 'versions': dict(p.versions),
                          'tag_kind': p.tag_kind, 'permission_authority': p.permission_authority is not None}
                         for p in config.projects]}
