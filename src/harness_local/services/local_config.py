"""Operator TOML outside managed checkouts → explicit ManagedConfig (`local-config-4`).

`local-config-4` (P008-T008) is `local-config-3` plus optional `[profiles.NAME]`:
stack profiles declared by the operator (preparation, validations with JUnit,
command prefixes, protected/sensitive paths, data-model paths and executor
instructions) that compositions name like a built-in one. Commands are argv
without shell; the profile content enters the frozen composition hash.
`local-config-3` (D076) keeps the `local-config-2` agents and groups the profile
commands in named `[compositions.NAME]`; `[registration]` lists the canonical
roots under which the UI may register projects (SQLite, D054) and whether those
may enable bootstrap. `[[projects]]` is optional and names a composition.
`local-config-2` (D052) declares `[agents.reviewer]` and `[agents.executor]`,
each Codex or Claude. `local-config-1` is still read as Codex reviewer and
Claude executor with its own policy (separate planner selection). Neither of
them can register projects from the UI.

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
import re
import stat
from threading import Lock
import tomllib

from harness_local.adapters.cli_agents import EFFORTS, CLIConfig, CLIProcessAdapter
from harness_local.adapters.commands import CommandConfig, ManagedCommandRunner
from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.commit import GitIdentity
from harness_local.core.engine.context import (Command, EnginePolicy, JUnitDeclaration, ProjectContext,
                                               ProjectProfile, relative_path)
from harness_local.core.engine.contracts import freeze
from harness_local.core.engine.documents import DOCUMENT_LAYOUT
from harness_local.core.engine.journal import JournalError
from harness_local.profiles.typescript_web import typescript_web_profile
from harness_local.services.managed_runtime import (PROJECT_ID, ManagedConfig, ManagedProject, agents_view,
                                                    validate_projects)

VERSION = 'local-config-4'
FORMATS = ('local-config-1', 'local-config-2', 'local-config-3', VERSION)
REGISTRABLE = ('local-config-3', VERSION)
CLI_KEYS = ('executable', 'cli_version', 'timeout_seconds', 'environment')
TOOL_KEYS = ('tools', 'allowed_tools', 'grantable_tools')
CONFIG_ENV = 'HARNESS_LOCAL_CONFIG'
MAX_BYTES = 65536
PROFILES = {'typescript-web': typescript_web_profile}
PROFILE_KEYS = ('preparation', 'validations', 'allowed_command_prefixes', 'protected_paths', 'sensitive_paths',
                'data_model_paths', 'executor_instructions')
# argv sin shell: el ejecutable es un nombre de `executables`, nunca un intérprete de órdenes, y ningún argumento
# lleva sintaxis que solo un shell interpretaría (el runner no la interpreta y su presencia delata un error).
COMMAND_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9._+-]{0,63}')
SHELLS = frozenset({'sh', 'bash', 'zsh', 'dash', 'ksh', 'mksh', 'ash', 'fish', 'csh', 'tcsh', 'busybox'})
SHELL_TOKENS = frozenset({';', '&', '&&', '|', '||', '|&', '>', '>>', '<', '<<', '2>', '2>&1'})


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


def _shell_free(argv, where):
    if not COMMAND_NAME.fullmatch(argv[0]) or argv[0] in SHELLS:
        raise LocalConfigError(f'{where}: el primer elemento nombra un ejecutable de `executables`, no un shell')
    if any(item in SHELL_TOKENS or '`' in item or '$(' in item for item in argv):
        raise LocalConfigError(f'{where}: argv sin sintaxis de shell (se ejecuta sin shell)')
    return argv


def _command(item, label, *, strict):
    """Exact command table (`argv`, `timeout_seconds`, optional `cwd` and `environment`).

    `strict` (local-config-4) also requires a shell-free argv; earlier formats keep their validation."""
    item = _fields(item, label, ('argv', 'timeout_seconds'), ('cwd', 'environment'))
    argv = _texts(item['argv'], f'{label}.argv')
    if strict:
        _shell_free(argv, f'{label}.argv')
    try:
        return Command(argv, _text(item.get('cwd', '.'), f'{label}.cwd'),
                       _environment(item.get('environment', {}), f'{label}.environment'),
                       _number(item['timeout_seconds'], f'{label}.timeout_seconds'))
    except LocalConfigError:
        raise
    except ValueError as exc:
        raise LocalConfigError(f'{label}: {exc}') from None


def _patterns(value, where, *, empty):
    patterns = _texts(value, where, empty=empty)
    for pattern in patterns:
        try:
            relative_path(pattern)
        except ValueError:
            raise LocalConfigError(f'{where}: patrón relativo al checkout requerido ({pattern!r})') from None
    if len(set(patterns)) != len(patterns):
        raise LocalConfigError(f'{where}: patrones repetidos')
    return patterns


def _profile(name, value):
    """`local-config-4`: a stack profile declared by the operator; loading it executes nothing (P008-T008).

    Every key that grants effects is explicit (lists may be empty where noted); unknown keys are rejected.
    A validation may declare its JUnit report with `junit = { path, coverage }`."""
    where = f'profiles.{name}'
    if not PROJECT_ID.fullmatch(name):
        raise LocalConfigError(f'{where}: nombre [a-z0-9][a-z0-9._-]{{0,63}} requerido')
    if name in PROFILES:
        raise LocalConfigError(f'{where}: nombre reservado por un perfil integrado')
    value = _fields(value, where, PROFILE_KEYS, ('sensitive_allowlist',))
    commands = {}
    for key in ('preparation', 'validations'):
        items = value[key]
        if not isinstance(items, list) or (key == 'validations' and not items):
            raise LocalConfigError(f'{where}.{key}: lista de comandos requerida'
                                   + (' (al menos uno)' if key == 'validations' else ''))
        commands[key] = []
        for index, item in enumerate(items):
            label = f'{where}.{key}[{index}]'
            junit = item.get('junit') if key == 'validations' and isinstance(item, dict) else None
            command = _command({k: v for k, v in item.items() if k != 'junit'} if junit is not None else item,
                               label, strict=True)
            if command in (entry for entry, _ in commands[key]):
                raise LocalConfigError(f'{label}: comando repetido')
            if junit is not None:
                junit = _fields(junit, f'{label}.junit', ('path', 'coverage'))
                try:
                    junit = JUnitDeclaration(command, _text(junit['path'], f'{label}.junit.path'),
                                             _text(junit['coverage'], f'{label}.junit.coverage'))
                except ValueError as exc:
                    raise LocalConfigError(f'{label}.junit: {exc}') from None
            commands[key].append((command, junit))
    prefixes = value['allowed_command_prefixes']
    if not isinstance(prefixes, list):
        raise LocalConfigError(f'{where}.allowed_command_prefixes: lista de argv requerida')
    prefixes = tuple(_shell_free(_texts(item, f'{where}.allowed_command_prefixes[{index}]'),
                                 f'{where}.allowed_command_prefixes[{index}]') for index, item in enumerate(prefixes))
    try:
        return ProjectProfile(
            name=name,
            preparation=tuple(command for command, _ in commands['preparation']),
            validations=tuple(command for command, _ in commands['validations']),
            allowed_command_prefixes=prefixes,
            protected_paths=_patterns(value['protected_paths'], f'{where}.protected_paths', empty=False),
            sensitive_paths=_patterns(value['sensitive_paths'], f'{where}.sensitive_paths', empty=False),
            sensitive_allowlist=_patterns(value.get('sensitive_allowlist', []), f'{where}.sensitive_allowlist',
                                          empty=True),
            executor_instructions=_text(value['executor_instructions'], f'{where}.executor_instructions'),
            junit_reports=tuple(junit for _, junit in commands['validations'] if junit is not None),
            data_model_paths=_patterns(value['data_model_paths'], f'{where}.data_model_paths', empty=True))
    except LocalConfigError:
        raise
    except ValueError as exc:
        raise LocalConfigError(f'{where}: {exc}') from None


def _commands(value, where, root, profile, *, strict=False):
    value = _fields(value, where, ('executables', 'environment', 'authorize_profile_commands'),
                    ('max_timeout_seconds', 'max_output_bytes', 'authorized'))
    if not isinstance(value['executables'], dict) or not value['executables']:
        raise LocalConfigError(f'{where}.executables: tabla nombre → ejecutable requerida')
    executables = tuple(sorted((_text(name, where), _executable(path, f'{where}.executables.{name}'))
                               for name, path in value['executables'].items()))
    if strict:
        for name, path in executables:
            if not COMMAND_NAME.fullmatch(name) or {Path(path).name, Path(path).resolve().name} & SHELLS:
                raise LocalConfigError(f'{where}.executables.{name}: nombre simple y ejecutable que no sea un shell')
    required = profile.preparation + profile.validations
    authorized = required if _flag(value['authorize_profile_commands'], f'{where}.authorize_profile_commands') else ()
    extras = value.get('authorized', [])
    if not isinstance(extras, list):
        raise LocalConfigError(f'{where}.authorized: lista de comandos exactos requerida')
    for index, item in enumerate(extras):
        command = _command(item, f'{where}.authorized[{index}]', strict=strict)
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


def _composition(value, where, state, profiles, *, strict):
    """`local-config-3/4`: commands of a profile under a name, independent of any checkout (D076).

    `profiles` maps every admitted name (built-in, plus declared ones in `local-config-4`) to its profile."""
    if not isinstance(value, dict):
        raise LocalConfigError(f'{where}: se esperaba una tabla')
    if _text(value.get('profile'), f'{where}.profile') not in profiles:
        raise LocalConfigError(f'{where}.profile: perfiles admitidos {sorted(profiles)}')
    commands = {key: item for key, item in value.items() if key != 'profile'}
    # The state directory stands in for a checkout: only the table itself is validated here.
    _commands(commands, where, state, profiles[value['profile']], strict=strict)
    return value['profile'], commands


class LocalComposer:
    """Operator authority shared by every project: agents, Git, state and named compositions.

    Composes TOML projects at load and registered projects (D076) at any time; the
    ports and the writer find each checkout's live composition under a lock, so a
    job frozen with another composition or registry version is refused before effects.
    """

    PROJECT_KEYS = ('id', 'root', 'repository_trusted', 'policy')
    OPTIONAL_KEYS = ('tag_kind', 'permission_authority', 'documents')

    def __init__(self, fmt, data, source, state, agents, reviewer, identity, git_executable, engine,
                 compositions, registration, profiles):
        self.format, self.source, self.state = fmt, source, state
        self.agents_key = 'providers' if fmt == 'local-config-1' else 'agents'
        self._authority = {self.agents_key: data[self.agents_key], 'git': data['git'], 'state_dir': str(state)}
        self.agents, self.reviewer = agents, reviewer
        self.identity, self.git_executable, self.engine = identity, git_executable, engine
        self.compositions = compositions  # name → (profile, raw command table); empty before v3
        self.profiles = profiles  # name → ProjectProfile: built-in ones, plus those declared in v4
        self.declared = tuple(sorted(name for name in profiles if name not in PROFILES))
        # v3/v4 only: canonical roots under which the UI may register, and the bootstrap ceiling.
        self.roots, self.bootstrap_enabled = registration
        self._lock = Lock()
        self._live = {}

    @property
    def registrable(self):
        return self.format in REGISTRABLE

    def compose(self, item, where, *, registry=None):
        """Validated `ManagedProject` and its composition, without installing it.

        `registry` is `(version, row_sha256)` of a registered row: it enters the frozen
        hash, so a newer registry version quarantines jobs admitted under the older one.
        """
        if self.registrable:
            required, optional = (*self.PROJECT_KEYS, 'composition'), (*self.OPTIONAL_KEYS, 'bootstrap_enabled')
        else:
            required, optional = (*self.PROJECT_KEYS, 'profile', 'commands'), self.OPTIONAL_KEYS
        item = _fields(item, where, required, optional)
        if item.get('documents', 'v2') != 'v2':
            raise LocalConfigError(f'{where}.documents: solo se admite "v2" (contrato documental unificado D088; '
                                   'omitirlo equivale a "v2")')
        if _flag(item['repository_trusted'], f'{where}.repository_trusted') is not True:
            raise LocalConfigError(f'{where}: sin confianza explícita el proyecto no se registra')
        root = _path(item['root'], f'{where}.root', kind='directory')
        if not (_outside(self.state, root) and _outside(self.source, root)):
            raise LocalConfigError(f'{where}: configuración y estado deben quedar fuera del checkout')
        authority = dict(self._authority)
        if self.registrable:
            name = _text(item['composition'], f'{where}.composition')
            if name not in self.compositions:
                raise LocalConfigError(f'{where}.composition: composiciones declaradas {sorted(self.compositions)}')
            profile_name, table = self.compositions[name]
            authority['composition'] = {name: {'profile': profile_name, **table}}
        else:
            profile_name, table = _text(item['profile'], f'{where}.profile'), item['commands']
            if profile_name not in self.profiles:
                raise LocalConfigError(f'{where}.profile: perfiles admitidos {sorted(self.profiles)}')
        profile = self.profiles[profile_name]
        if self.format == VERSION:
            # P008-T008: el contenido completo del perfil (declarado o integrado) entra en el hash congelado, así que
            # cambiarlo deja en cuarentena los jobs admitidos antes. v1–v3 conservan sus hashes.
            authority['profile'] = asdict(profile)
        bootstrap = _flag(item.get('bootstrap_enabled', False), f'{where}.bootstrap_enabled')
        engine_policy = _policy(item['policy'], f'{where}.policy', self.reviewer, self.agents['executor'].provider)
        commands = _commands(table, f'{where}.commands', root, profile, strict=self.format == VERSION)
        identifier = _text(item['id'], f'{where}.id')
        if not PROJECT_ID.fullmatch(identifier):
            raise LocalConfigError(f'{where}.id: [a-z0-9][a-z0-9._-]{{0,63}} requerido')
        artifacts = self.state / 'artifacts' / identifier
        try:
            cli = CLIProcessAdapter(self.agents, artifacts)
        except ValueError as exc:
            raise LocalConfigError(f'{self.agents_key}: {exc}') from None
        runner = ManagedCommandRunner(commands)
        frozen = {'project': item, **authority}
        if registry is not None:
            frozen['registry'] = {'version': registry[0], 'row_sha256': registry[1]}
        try:
            digest = hashlib.sha256(freeze(frozen).encode()).hexdigest()
        except (TypeError, ValueError):
            raise LocalConfigError(f'{where}: valores TOML no admitidos (fechas u objetos)') from None
        # D088: el layout documental es obligatorio. Su versión entra en las congeladas, así que un job admitido
        # antes (contrato opcional o sin contrato) queda en cuarentena en lugar de ejecutarse con otro layout.
        versions = {'engine': f'harness-local-{self.engine}', 'evidence': 'git-1', 'provider_cli': None,
                    'local_config': self.format, 'profile': profile.name, 'local_config_sha256': digest,
                    'document_layout': DOCUMENT_LAYOUT,
                    **({'project_registry': str(registry[0])} if registry is not None else {}),
                    **cli.frozen_versions(), **runner.frozen_versions()}
        context = ProjectContext(root, profile, engine_policy, documents='v2')
        project = ManagedProject(identifier, context, versions, item.get('permission_authority'),
                                 item.get('tag_kind', 'lightweight'), bootstrap)
        return project, (identifier, versions, commands, artifacts)

    def install(self, composed):
        project, composition = composed
        with self._lock:
            self._live[project.context.root] = composition
        return project

    def forget(self, root):
        with self._lock:
            self._live.pop(root, None)

    def _composed(self, context, versions):
        with self._lock:
            current = self._live.get(context.root)
        if current is None:
            raise JournalError('Checkout sin composición local registrada')
        identifier, frozen, commands, artifacts = current
        if any(versions.get(key) != value for key, value in frozen.items()):
            raise JournalError(f'Composición local de {identifier} distinta de la congelada; no se ejecuta')
        return commands, artifacts

    def ports(self, context, versions):
        commands, artifacts = self._composed(context, versions)
        return (CLIProcessAdapter(self.agents, artifacts), ManagedCommandRunner(commands),
                GitWorkspace(self.identity, executable=self.git_executable))

    def writer(self, context, versions):
        self._composed(context, versions)
        return GitWorkspace(self.identity, executable=self.git_executable)

    def options(self):
        """What the UI may choose; executables and environment values never leave the file."""
        return {'format': self.format, 'roots': [str(root) for root in self.roots],
                'bootstrap_enabled': self.bootstrap_enabled,
                'executor_provider': self.agents['executor'].provider,
                'reviewer_provider': self.agents['reviewer'].provider,
                'executor_effort_vocabulary': list(EFFORTS[self.agents['executor'].provider]),
                'compositions': [{'name': name, 'profile': profile,
                                  'executables': sorted(table['executables']),
                                  'environment_keys': sorted(table['environment']),
                                  'authorize_profile_commands': table['authorize_profile_commands'],
                                  'extra_commands': [list(item['argv']) for item in table.get('authorized', [])]}
                                 for name, (profile, table) in sorted(self.compositions.items())]}


def _build(data, source):
    if not isinstance(data, dict) or data.get('format') not in FORMATS:
        raise LocalConfigError(f'format debe ser uno de {list(FORMATS)}')
    fmt = data['format']
    agents_key = 'providers' if fmt == 'local-config-1' else 'agents'
    if fmt in REGISTRABLE:
        data = _fields(data, 'raíz', ('format', 'service', 'git', 'agents', 'registration', 'compositions'),
                       ('projects', 'profiles') if fmt == VERSION else ('projects',))
    else:
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
    compositions, registration = {}, ((), False)
    profiles = {name: factory() for name, factory in PROFILES.items()}
    declared = data.get('profiles', {})
    if not isinstance(declared, dict):
        raise LocalConfigError('profiles: se esperaba una tabla [profiles.NOMBRE]')
    for name, value in declared.items():
        profiles[name] = _profile(name, value)
    if fmt in REGISTRABLE:
        if not isinstance(data['compositions'], dict) or not data['compositions']:
            raise LocalConfigError('compositions: al menos una [compositions.NOMBRE] requerida')
        for name, value in data['compositions'].items():
            if not PROJECT_ID.fullmatch(name):
                raise LocalConfigError(f'compositions.{name}: nombre [a-z0-9][a-z0-9._-]{{0,63}} requerido')
            compositions[name] = _composition(value, f'compositions.{name}', state, profiles, strict=fmt == VERSION)
        table = _fields(data['registration'], 'registration', ('roots', 'bootstrap_enabled'))
        roots = tuple(_path(item, 'registration.roots', kind='directory')
                      for item in _texts(table['roots'], 'registration.roots', empty=True))
        if len(set(roots)) != len(roots):
            raise LocalConfigError('registration.roots: raíces repetidas')
        registration = (roots, _flag(table['bootstrap_enabled'], 'registration.bootstrap_enabled'))
    items = data.get('projects', [])
    if not isinstance(items, list) or (not items and fmt not in REGISTRABLE):
        raise LocalConfigError('projects: al menos un [[projects]] requerido')
    try:
        engine = importlib.metadata.version('harness-local')
    except importlib.metadata.PackageNotFoundError:
        raise LocalConfigError('Versión del paquete harness-local no disponible') from None

    composer = LocalComposer(fmt, data, source, state, agents, reviewer, identity, git_executable, engine,
                             compositions, registration, profiles)
    projects = []
    for index, item in enumerate(items):
        project, composition = composer.compose(item, f'projects[{index}]')
        if project.id in {p.id for p in projects} or project.context.root in {p.context.root for p in projects}:
            raise LocalConfigError(f'projects[{index}]: id o raíz duplicados')
        projects.append(composer.install((project, composition)))

    config = ManagedConfig(tuple(projects), ports_factory=composer.ports, commit_factory=composer.writer,
                           supervisor=_flag(service['supervisor'], 'service.supervisor'),
                           lease_seconds=_number(service.get('lease_seconds', 30.0), 'service.lease_seconds'),
                           poll_seconds=_number(service.get('poll_seconds', 0.5), 'service.poll_seconds'),
                           migrations_dir=state / 'migrations', registrar=composer)
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


def _profile_view(profile: ProjectProfile) -> dict:
    """P008-T008: a declared profile's content hash and the argv the operator confirms."""
    return {'sha256': hashlib.sha256(freeze(asdict(profile)).encode()).hexdigest(),
            'preparation': [list(command.argv) for command in profile.preparation],
            'validations': [list(command.argv) for command in profile.validations],
            'junit_reports': [item.path for item in profile.junit_reports],
            'data_model_paths': list(profile.data_model_paths)}


def summary(config: ManagedConfig) -> dict:
    """Identifiers, roots and frozen versions only: environment values never leave the file."""
    registrar = config.registrar
    return {'format': registrar.format, 'supervisor': config.supervisor,
            'registration': registrar.options() if registrar.registrable else None,
            'profiles': {name: _profile_view(registrar.profiles[name]) for name in registrar.declared},
            'projects': [{'id': p.id, 'root': str(p.context.root), 'profile': p.context.profile.name,
                          'policy': asdict(p.context.policy), 'agents': agents_view(p), 'versions': dict(p.versions),
                          'tag_kind': p.tag_kind, 'permission_authority': p.permission_authority is not None,
                          'documents': p.context.documents, 'bootstrap_enabled': p.bootstrap_enabled}
                         for p in config.projects]}
