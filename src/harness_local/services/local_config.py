"""Operator TOML outside managed checkouts → explicit ManagedConfig (`local-config-6`).

`local-config-6` (P011-T008, D167) is `local-config-5` plus an optional `[[projects]].work_language` (en/es):
the service records it once for the project's root at startup and SQLite rules afterwards; another value for an
associated root stops the service. Its `[recipes]` select the packaged v2 recipes (P011-T020, D168), which
prepare with the project's work language; the same keys in `local-config-5` keep selecting v1.
`local-config-5` (P009-T003) adds private role presets and optional project selections, and
optional packaged recipes: `[recipes.django]` (D119) and `[recipes.typescript-web]` (D142).
Effective agents are composed per checkout; older formats keep their frozen identity.
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
from dataclasses import asdict, replace
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

from harness_local.adapters.cli_agents import EFFORTS, WRITE_SUPPORTED, CLIConfig, CLIProcessAdapter
from harness_local.adapters.commands import CommandConfig, ManagedCommandRunner, config_payload
from harness_local.adapters.git import GitWorkspace
from harness_local.core.engine.commit import GitIdentity
from harness_local.core.engine.context import (Command, EnginePolicy, JUnitDeclaration, ProjectContext,
                                               ProjectProfile, relative_path)
from harness_local.core.engine.contracts import MODEL_FORM, freeze
from harness_local.core.engine.documents import DOCUMENT_LAYOUT
from harness_local.core.engine.journal import JournalError
from harness_local.i18n import LANGUAGES
from harness_local.profiles.typescript_web import typescript_web_profile
from harness_local.recipes import RECIPES, by_version as recipe_version, implementation, module as recipe_module
from harness_local.services.managed_runtime import (PROJECT_ID, ManagedConfig, ManagedProject, agents_view,
                                                    validate_projects)

VERSION = 'local-config-6'
V5 = 'local-config-5'
FORMATS = ('local-config-1', 'local-config-2', 'local-config-3', 'local-config-4', V5, VERSION)
REGISTRABLE = ('local-config-3', 'local-config-4', V5, VERSION)
PROFILE_FORMATS = ('local-config-4', V5, VERSION)
# v5 adds presets/selections and recipes; v6 keeps the presets/selections and adds the work language.
AGENT_FORMATS = (V5, VERSION)
CLI_KEYS = ('executable', 'cli_version', 'timeout_seconds', 'environment')
TOOL_KEYS = ('tools', 'allowed_tools', 'grantable_tools')
CONFIG_ENV = 'HARNESS_LOCAL_CONFIG'
MAX_BYTES = 65536
PROFILES = {'typescript-web': typescript_web_profile}
PROFILE_KEYS = ('preparation', 'validations', 'allowed_command_prefixes', 'protected_paths', 'sensitive_paths',
                'data_model_paths', 'executor_instructions')
# argv without shell: the executable is a name from `executables`, never a command interpreter, and no argument
# carries syntax that only a shell would interpret (the runner does not interpret it and its presence reveals an error).
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


def _presets(data):
    """V5: explicit local capabilities; loading does not query remote availability."""
    if not isinstance(data, dict):
        raise LocalConfigError('agent_presets: se esperaba una tabla')
    presets = {}
    for name, value in data.items():
        where = f'agent_presets.{name}'
        if not PROJECT_ID.fullmatch(name):
            raise LocalConfigError(f'{where}: id de preset inválido')
        value = _fields(value, where, ('provider', 'roles', 'models', 'efforts', 'allow_open_executor', *CLI_KEYS),
                        TOOL_KEYS)
        provider = value['provider']
        if not isinstance(provider, str) or provider not in EFFORTS:
            raise LocalConfigError(f'{where}.provider: proveedores admitidos {sorted(EFFORTS)}')
        roles = _texts(value['roles'], f'{where}.roles')
        models, efforts = (_texts(value[key], f'{where}.{key}') for key in ('models', 'efforts'))
        if len(set(roles)) != len(roles) or not set(roles) <= {'reviewer', 'executor'}:
            raise LocalConfigError(f'{where}.roles: reviewer y/o executor sin repeticiones')
        if (len(set(models)) != len(models) or len(set(efforts)) != len(efforts)
                or any(not MODEL_FORM.fullmatch(model) for model in models)
                or not set(efforts) <= set(EFFORTS[provider])):
            raise LocalConfigError(f'{where}: modelos únicos válidos y esfuerzos del proveedor requeridos')
        _flag(value['allow_open_executor'], f'{where}.allow_open_executor')
        config = _cli(where, provider, {k: v for k, v in value.items() if k in (*CLI_KEYS, *TOOL_KEYS)},
                      optional=TOOL_KEYS if provider == 'claude' else ())
        if 'reviewer' in roles and any((config.tools, config.allowed_tools, config.grantable_tools)):
            raise LocalConfigError(f'{where}: el revisor tiene inventario de herramientas fijo de solo lectura')
        if 'executor' in roles and config.cli_version not in WRITE_SUPPORTED[provider]:
            raise LocalConfigError(f'{where}: versión CLI incompatible con escritura')
        presets[name] = (value, config)
    return presets


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


def _commands(value, where, root, profile, *, strict=False, deferred_root=None):
    value = _fields(value, where, ('executables', 'environment', 'authorize_profile_commands'),
                    ('max_timeout_seconds', 'max_output_bytes', 'authorized'))
    if not isinstance(value['executables'], dict) or not value['executables']:
        raise LocalConfigError(f'{where}.executables: tabla nombre → ejecutable requerida')
    executables = []
    for name, path in value['executables'].items():
        if isinstance(path, dict) and deferred_root is not None:
            _fields(path, f'{where}.executables.{name}', ('project_venv',))
            tool = path['project_venv']
            if tool not in ('python', 'pytest', 'ruff', 'mypy') or tool != name:
                raise LocalConfigError(f'{where}: enlace project_venv tipado python/pytest/ruff/mypy requerido')
            executable = str(deferred_root / '.venv' / 'bin' / tool)
        else:
            executable = _executable(path, f'{where}.executables.{name}')
        executables.append((_text(name, where), executable))
    executables = tuple(sorted(executables))
    if strict:
        for name, path in executables:
            if not COMMAND_NAME.fullmatch(name) or {Path(path).name, Path(path).resolve().name} & SHELLS:
                raise LocalConfigError(f'{where}.executables.{name}: nombre simple y ejecutable que no sea un shell')
    required = profile.preparation + profile.validations
    authorize = _flag(value['authorize_profile_commands'], f'{where}.authorize_profile_commands')
    authorized = required if authorize else ()
    extras = value.get('authorized', [])
    if not isinstance(extras, list):
        raise LocalConfigError(f'{where}.authorized: lista de comandos exactos requerida')
    for index, item in enumerate(extras):
        command = _command(item, f'{where}.authorized[{index}]', strict=strict)
        if command not in authorized:
            authorized += (command,)
    if any(command not in authorized for command in required):
        raise LocalConfigError(f'{where}: autorizar exactamente todos los comandos del perfil')
    if profile.formatter_argv and not authorize:
        # D133: the formatter receives variable paths, so it does not fit in an exact authorization.
        raise LocalConfigError(f'{where}: el formateador del perfil exige authorize_profile_commands = true')
    try:
        return CommandConfig(str(root), True, authorized, executables,
                             _environment(value['environment'], f'{where}.environment'),
                             formatter_argv=profile.formatter_argv,
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


def _composition(value, where, state, profiles, *, strict, recipes=None):
    """`local-config-3/4`: commands of a profile under a name, independent of any checkout (D076).

    `profiles` maps every admitted name (built-in, plus declared ones in `local-config-4`) to its profile."""
    if not isinstance(value, dict):
        raise LocalConfigError(f'{where}: se esperaba una tabla')
    if _text(value.get('profile'), f'{where}.profile') not in profiles:
        raise LocalConfigError(f'{where}.profile: perfiles admitidos {sorted(profiles)}')
    recipe = value.get('recipe')
    if recipe is not None:
        if not recipes or recipe not in RECIPES or recipe not in recipes or value['profile'] != RECIPES[recipe][1]:
            raise LocalConfigError(f'{where}: receta v5 declarada y su perfil empaquetado requeridos')
        if recipe == 'django':
            expected = {name: {'project_venv': name} for name in ('python', 'pytest', 'ruff', 'mypy')}
            if value.get('executables') != expected or value.get('environment') != {} or value.get('authorized'):
                raise LocalConfigError(f'{where}: enlaces exactos al entorno y environment vacío requeridos para la receta')
        else:
            _typescript_composition(value, where, recipes[recipe])
    elif value['profile'] == 'python-django-recipe' and 'django' in recipes:
        raise LocalConfigError(f'{where}: el perfil de receta exige recipe = "django"')
    commands = {key: item for key, item in value.items() if key not in ('profile', 'recipe')}
    # The state directory stands in for a checkout: only the table itself is validated here.
    _commands(commands, where, state, profiles[value['profile']], strict=strict,
              deferred_root=state if recipe == 'django' else None)
    return value['profile'], commands


def _typescript_composition(value, where, recipe):
    """P010-T002 (D142): each task reinstalls with the node/npm and the cache that accredited the preparation.

    The composition keeps its own environment: it must already name that cache, and it is never rewritten."""
    executables = value.get('executables')
    if not isinstance(executables, dict) or not {'node', 'npm'} <= set(executables):
        raise LocalConfigError(f'{where}.executables: node y npm requeridos para la receta typescript-web')
    for name in ('node', 'npm'):
        path = _executable(executables[name], f'{where}.executables.{name}')
        if Path(path).resolve() != Path(recipe[f'{name}_executable']).resolve():
            raise LocalConfigError(f'{where}.executables.{name}: debe resolver al mismo archivo que la receta')
    environment = value.get('environment')
    if not isinstance(environment, dict) or environment.get('npm_config_cache') != recipe['npm_cache']:
        raise LocalConfigError(f'{where}.environment: npm_config_cache igual a recipes.typescript-web.npm_cache '
                               'requerido; no se reescribe el entorno')


class LocalComposer:
    """Operator authority shared by every project: agents, Git, state and named compositions.

    Composes TOML projects at load and registered projects (D076) at any time; the
    ports and the writer find each checkout's live composition under a lock, so a
    job frozen with another composition or registry version is refused before effects.
    """

    PROJECT_KEYS = ('id', 'root', 'repository_trusted', 'policy')
    OPTIONAL_KEYS = ('tag_kind', 'permission_authority', 'documents')

    def __init__(self, fmt, data, source, state, agents, reviewer, identity, git_executable, engine,
                 compositions, registration, profiles, presets, recipes):
        self.format, self.source, self.state = fmt, source, state
        self.agents_key = 'providers' if fmt == 'local-config-1' else 'agents'
        self._authority = {self.agents_key: data[self.agents_key], 'git': data['git'], 'state_dir': str(state)}
        self.agents, self.reviewer = agents, reviewer
        self.presets, self.recipes = presets, recipes
        # Recipe generation of this format (D168): v5 selects v1 and v6 selects v2; older formats declare none.
        self._recipe_format = fmt if fmt in AGENT_FORMATS else V5
        self.recipe_profiles = {}  # v6 only: recipe name → profile of its v2 module
        self._recipe_roots, self._receipts = {}, {}
        self.identity, self.git_executable, self.engine = identity, git_executable, engine
        self.compositions = compositions  # name → (profile, raw command table); empty before v3
        self.profiles = profiles  # name → ProjectProfile: built-in ones, plus those declared in v4
        self.declared = tuple(sorted(name for name in profiles if name not in PROFILES))
        # v3–v5: canonical roots under which the UI may register, and the bootstrap ceiling.
        self.roots, self.bootstrap_enabled = registration
        self._lock = Lock()
        self._live = {}

    @property
    def registrable(self):
        return self.format in REGISTRABLE

    def compose(self, item, where, *, registry=None, new_directory=False):
        """Validated `ManagedProject` and its composition, without installing it.

        `registry` is `(version, row_sha256)` of a registered row: it enters the frozen
        hash, so a newer registry version quarantines jobs admitted under the older one.
        `new_directory` is a data-only creation preview: validates on the existing parent,
        freezes the future child's hashes and returns versions/profile, never installable ports.
        """
        if self.registrable:
            required, optional = (*self.PROJECT_KEYS, 'composition'), (*self.OPTIONAL_KEYS, 'bootstrap_enabled')
        else:
            required, optional = (*self.PROJECT_KEYS, 'profile', 'commands'), self.OPTIONAL_KEYS
        if self.format in AGENT_FORMATS:
            optional = (*optional, 'agent_selection')
        if self.format == VERSION and registry is None and not new_directory:
            optional = (*optional, 'work_language')  # TOML projects only: the UI confirms it in SQLite
        item = _fields(item, where, required, optional)
        work_language = item.get('work_language')
        if work_language is not None and work_language not in LANGUAGES:
            raise LocalConfigError(f'{where}.work_language: one of {list(LANGUAGES)} required')
        if item.get('documents', 'v2') != 'v2':
            raise LocalConfigError(f'{where}.documents: solo se admite "v2" (contrato documental unificado D088; '
                                   'omitirlo equivale a "v2")')
        if _flag(item['repository_trusted'], f'{where}.repository_trusted') is not True:
            raise LocalConfigError(f'{where}: sin confianza explícita el proyecto no se registra')
        # Only the D116 creation preview admits a target that does not exist yet, already validated by the service.
        root = _path(item['root'], f'{where}.root', kind='new_directory' if new_directory else 'directory')
        if not (_outside(self.state, root) and _outside(self.source, root)):
            raise LocalConfigError(f'{where}: configuración y estado deben quedar fuera del checkout')
        authority = dict(self._authority)
        if self.registrable:
            name = _text(item['composition'], f'{where}.composition')
            if name not in self.compositions:
                raise LocalConfigError(f'{where}.composition: composiciones declaradas {sorted(self.compositions)}')
            profile_name, table = self.compositions[name]
            authority['composition'] = {name: {'profile': profile_name, **table}}
            recipe = self._recipes_by_composition.get(name)
            if recipe:
                authority['recipe'] = {'config': self.recipes[recipe],
                                       **implementation(recipe_module(recipe, self._recipe_format))}
        else:
            profile_name, table = _text(item['profile'], f'{where}.profile'), item['commands']
            if profile_name not in self.profiles:
                raise LocalConfigError(f'{where}.profile: perfiles admitidos {sorted(self.profiles)}')
        recipe = self._recipes_by_composition.get(item.get('composition'))
        # v6: a recipe composition runs with its v2 module's own profile (D163/D168), not the built-in one.
        profile = self.recipe_profiles.get(recipe) or self.profiles[profile_name]
        if self.format in PROFILE_FORMATS:
            # P008-T008: the complete profile content (declared or built-in) enters the frozen hash, so
            # changing it quarantines the jobs admitted before. v1–v3 keep their hashes.
            authority['profile'] = asdict(profile)
        bootstrap = _flag(item.get('bootstrap_enabled', False), f'{where}.bootstrap_enabled')
        agents, reviewer, selected = self.effective_agents(item, where)
        if recipe == 'django' and any(dict(agent.environment).get('PYTHONDONTWRITEBYTECODE') != '1'
                                      for agent in agents.values()):
            raise LocalConfigError(f'{where}: la receta requiere PYTHONDONTWRITEBYTECODE=1 explícito en ambos '
                                   'roles/presets para conservar los bytes del entorno; no se reescribe su entorno')
        engine_policy = _policy(item['policy'], f'{where}.policy', reviewer, agents['executor'].provider)
        if selected:
            executor = selected['executor']
            if ((engine_policy.executor_mode == 'catalog'
                 and not set(engine_policy.executor_models) <= set(executor['models']))
                    or any(not MODEL_FORM.fullmatch(model) for model in engine_policy.executor_models)
                    or not set(engine_policy.executor_efforts) <= set(executor['efforts'])):
                raise LocalConfigError(f'{where}.policy: catálogo del ejecutor fuera del preset seleccionado')
            if engine_policy.executor_mode == 'open' and not executor['allow_open_executor']:
                raise LocalConfigError(f'{where}.policy: el preset no admite ejecutor libre')
            engine_policy = replace(engine_policy, executor_effort_vocabulary=tuple(executor['efforts']))
            authority['agent_presets'] = selected
        if recipe == 'typescript-web' and not _outside(Path(self.recipes[recipe]['npm_cache']), root):
            raise LocalConfigError(f'{where}: la caché npm de la receta debe quedar fuera del checkout')
        # The preview validates the configuration on the existing parent, without building ports for the child.
        commands = _commands(table, f'{where}.commands', root.parent if new_directory else root, profile,
                             strict=self.format in PROFILE_FORMATS, deferred_root=root if recipe == 'django' else None)
        identifier = _text(item['id'], f'{where}.id')
        if not PROJECT_ID.fullmatch(identifier):
            raise LocalConfigError(f'{where}.id: [a-z0-9][a-z0-9._-]{{0,63}} requerido')
        artifacts = self.state / 'artifacts' / identifier
        try:
            cli = CLIProcessAdapter(agents, artifacts)
        except ValueError as exc:
            raise LocalConfigError(f'{self.agents_key}: {exc}') from None
        if recipe == 'django':
            commands = replace(commands, environment=(('PYTHONDONTWRITEBYTECODE', '1'), ('PYTHONNOUSERSITE', '1')))
        runner = ManagedCommandRunner(commands)
        frozen = {'project': item, **authority}
        if registry is not None:
            frozen['registry'] = {'version': registry[0], 'row_sha256': registry[1]}
        try:
            digest = hashlib.sha256(freeze(frozen).encode()).hexdigest()
        except (TypeError, ValueError):
            raise LocalConfigError(f'{where}: valores TOML no admitidos (fechas u objetos)') from None
        # D088: the documentary layout is mandatory. Its version enters the frozen ones, so a job admitted
        # before (optional contract or no contract) is quarantined instead of running with another layout.
        versions = {'engine': f'harness-local-{self.engine}', 'evidence': 'git-1', 'provider_cli': None,
                    'local_config': self.format, 'profile': profile.name, 'local_config_sha256': digest,
                    'document_layout': DOCUMENT_LAYOUT,
                    **({'project_registry': str(registry[0])} if registry is not None else {}),
                    **({'project_registry_id': identifier, 'project_registry_sha256': registry[1]}
                       if registry is not None and self.format in AGENT_FORMATS else {}),
                    **cli.frozen_versions(), **runner.frozen_versions(),
                    **({'project_recipe': recipe_module(recipe, self._recipe_format).VERSION,
                        'recipe_config_sha256': hashlib.sha256(freeze(authority['recipe']).encode()).hexdigest()}
                       if recipe else {})}
        if new_directory:
            commands_snapshot = {**config_payload(commands), 'checkout': str(root)}
            versions['command_config_sha256'] = hashlib.sha256(freeze(commands_snapshot).encode()).hexdigest()
            preview = ManagedProject(identifier, ProjectContext(root.parent, profile, engine_policy, documents='v2'),
                                     versions, item.get('permission_authority'), item.get('tag_kind', 'lightweight'),
                                     bootstrap)
            validate_projects(ManagedConfig((preview,), ports_factory=self.ports, commit_factory=self.writer))
            return {'versions': versions, 'profile': profile.name, 'profile_details': _profile_view(profile),
                    'agents': agents_view(preview),
                    'composition': next(c for c in self.options()['compositions'] if c['name'] == name)}
        context = ProjectContext(root, profile, engine_policy, documents='v2', work_language=work_language)
        project = ManagedProject(identifier, context, versions, item.get('permission_authority'),
                                 item.get('tag_kind', 'lightweight'), bootstrap)
        return project, (identifier, versions, commands, artifacts, agents)

    def effective_agents(self, item, where):
        selection = item.get('agent_selection')
        if selection is None:
            return self.agents, self.reviewer, None
        selection = _fields(selection, f'{where}.agent_selection', ('reviewer', 'executor'))
        agents, selected, reviewer = {}, {}, None
        for role in ('reviewer', 'executor'):
            label = f'{where}.agent_selection.{role}'
            choice = _fields(selection[role], label, ('preset_id', 'model', 'effort') if role == 'reviewer'
                             else ('preset_id',))
            name = _text(choice['preset_id'], f'{label}.preset_id')
            if name not in self.presets or role not in self.presets[name][0]['roles']:
                raise LocalConfigError(f'{label}: preset ausente o incompatible con el rol ({name})')
            preset, agents[role] = self.presets[name]
            selected[role] = preset
            if role == 'reviewer':
                reviewer = tuple(_text(choice[key], f'{label}.{key}') for key in ('model', 'effort'))
                if reviewer[0] not in preset['models'] or reviewer[1] not in preset['efforts']:
                    raise LocalConfigError(f'{label}: modelo/esfuerzo del revisor fuera del preset')
        return agents, reviewer, selected

    def install(self, composed):
        project, composition = composed
        with self._lock:
            self._live[project.context.root] = composition
        known = recipe_version(project.versions.get('project_recipe'))
        if known:
            self._recipe_roots[project.context.root] = self.recipes[known[0]]
        return project

    def forget(self, root):
        with self._lock:
            self._live.pop(root, None)

    def _composed(self, context, versions):
        with self._lock:
            current = self._live.get(context.root)
        if current is None:
            raise JournalError('Checkout sin composición local registrada')
        identifier, frozen, commands, artifacts, agents = current
        if any(versions.get(key) != value for key, value in frozen.items()):
            raise JournalError(f'Composición local de {identifier} distinta de la congelada; no se ejecuta')
        return commands, artifacts, agents

    def ports(self, context, versions):
        commands, artifacts, agents = self._composed(context, versions)
        if versions.get('project_recipe'):
            from harness_local.adapters.preparation import PreparedCommandRunner
            runner = PreparedCommandRunner(commands, self._receipts.get(context.root), versions)
        else:
            runner = ManagedCommandRunner(commands)
        return (CLIProcessAdapter(agents, artifacts), runner,
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
                'agent_presets': [{'id': name, **{key: value[key] for key in
                                  ('provider', 'roles', 'models', 'efforts', 'allow_open_executor')}}
                                  for name, (value, _) in sorted(self.presets.items())],
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
                       ('projects', 'profiles', 'agent_presets', 'recipes') if fmt in AGENT_FORMATS else
                       ('projects', 'profiles') if fmt in PROFILE_FORMATS else ('projects',))
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
    presets = _presets(data.get('agent_presets', {}))
    compositions, registration = {}, ((), False)
    recipes = {}
    if 'recipes' in data:
        raw = _fields(data['recipes'], 'recipes', (), tuple(RECIPES))
        if 'django' in raw:
            entry = _fields(raw['django'], 'recipes.django',
                            ('python_executable', 'python_version', 'installer_executable', 'installer_version',
                             'timeout_seconds', 'max_output_bytes', 'allow_network'), ('wheelhouse',))
            entry = dict(entry)
            for key in ('python_executable', 'installer_executable'):
                entry[key] = _executable(entry[key], f'recipes.django.{key}')
                if {Path(entry[key]).name, Path(entry[key]).resolve().name} & SHELLS:
                    raise LocalConfigError('recipes.django: intérprete Python e instalador uv, sin shells')
            if not re.fullmatch(r'3\.(11|12|13)\.[0-9]+', _text(entry['python_version'], 'recipes.django.python_version')):
                raise LocalConfigError('recipes.django.python_version: CPython 3.11–3.13 exacto requerido')
            if not re.fullmatch(r'0\.[0-9]+\.[0-9]+', _text(entry['installer_version'], 'recipes.django.installer_version')):
                raise LocalConfigError('recipes.django.installer_version: versión uv exacta requerida')
            if not 120 <= _number(entry['timeout_seconds'], 'recipes.django.timeout_seconds') <= 1800:
                raise LocalConfigError('recipes.django.timeout_seconds: 120..1800 segundos requeridos')
            if type(entry['max_output_bytes']) is not int or not 1024 <= entry['max_output_bytes'] <= 1048576:
                raise LocalConfigError('recipes.django.max_output_bytes: 1024..1048576 requerido')
            _flag(entry['allow_network'], 'recipes.django.allow_network')
            if 'wheelhouse' in entry:
                entry['wheelhouse'] = str(_path(entry['wheelhouse'], 'recipes.django.wheelhouse', kind='directory'))
            recipes['django'] = entry
        if 'typescript-web' in raw:
            recipes['typescript-web'] = _typescript_recipe(raw['typescript-web'], state)
    profiles = {name: factory() for name, factory in PROFILES.items()}
    recipe_profiles = {}
    if fmt == VERSION:
        # D168: the v2 profiles are part of each v2 fingerprint; the built-in `typescript-web` stays for compositions
        # without a recipe.
        recipe_profiles = {name: recipe_module(name, fmt).profile() for name in recipes}
    if 'django' in recipes:
        from harness_local.recipes.django import profile
        # P009-T019 (D133): the formatter is declared here and not in recipes/django.py, whose text is part of the
        # recipe fingerprint that binds the preparation receipts already issued. v2 keeps the same formatter.
        base = recipe_profiles.get('django') or profile()
        profiles['python-django-recipe'] = replace(base, formatter_argv=('ruff', 'format', '--'),
                                                   formatter_paths=('*.py',))
        if fmt == VERSION:
            recipe_profiles['django'] = profiles['python-django-recipe']
    declared = data.get('profiles', {})
    if not isinstance(declared, dict):
        raise LocalConfigError('profiles: se esperaba una tabla [profiles.NOMBRE]')
    for name, value in declared.items():
        if name == 'python-django-recipe' and 'django' in recipes:
            raise LocalConfigError('Perfil python-django-recipe reservado para la receta empaquetada')
        profiles[name] = _profile(name, value)
    if fmt in REGISTRABLE:
        if not isinstance(data['compositions'], dict) or not data['compositions']:
            raise LocalConfigError('compositions: al menos una [compositions.NOMBRE] requerida')
        for name, value in data['compositions'].items():
            if not PROJECT_ID.fullmatch(name):
                raise LocalConfigError(f'compositions.{name}: nombre [a-z0-9][a-z0-9._-]{{0,63}} requerido')
            compositions[name] = _composition(value, f'compositions.{name}', state, profiles,
                                               strict=fmt in PROFILE_FORMATS, recipes=recipes)
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
                             compositions, registration, profiles, presets, recipes)
    composer._recipes_by_composition = {name: value['recipe'] for name, value in data.get('compositions', {}).items()
                                       if value.get('recipe')}
    composer.recipe_profiles = recipe_profiles
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


def _typescript_recipe(value, state):
    """P010-T002 (D142): `[recipes.typescript-web]`, operator authority for `typescript-web-recipe-1` (v5) or
    `typescript-web-recipe-2` (v6, D168): the same keys."""
    where = 'recipes.typescript-web'
    entry = dict(_fields(value, where, ('node_executable', 'node_version', 'npm_executable', 'npm_version', 'npm_cache',
                                        'timeout_seconds', 'max_output_bytes', 'allow_network')))
    for key in ('node_executable', 'npm_executable'):
        entry[key] = _executable(entry[key], f'{where}.{key}')
        if {Path(entry[key]).name, Path(entry[key]).resolve().name} & SHELLS:
            raise LocalConfigError(f'{where}: ejecutables node y npm, sin shells')
    for key in ('node_version', 'npm_version'):
        if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', _text(entry[key], f'{where}.{key}')):
            raise LocalConfigError(f'{where}.{key}: versión exacta requerida')
    entry['npm_cache'] = str(_path(entry['npm_cache'], f'{where}.npm_cache', kind='directory'))
    if not _outside(Path(entry['npm_cache']), state):
        raise LocalConfigError(f'{where}.npm_cache: fuera del estado del servicio')
    if not 120 <= _number(entry['timeout_seconds'], f'{where}.timeout_seconds') <= 1800:
        raise LocalConfigError(f'{where}.timeout_seconds: 120..1800 segundos requeridos')
    if type(entry['max_output_bytes']) is not int or not 1024 <= entry['max_output_bytes'] <= 1048576:
        raise LocalConfigError(f'{where}.max_output_bytes: 1024..1048576 requerido')
    _flag(entry['allow_network'], f'{where}.allow_network')
    return entry


def build(data, source) -> ManagedConfig:
    return _build(data, source)[0]


def load_local_config(path) -> ManagedConfig:
    path = Path(path)
    return build(_read(path), path)


def inspect_local_config(path) -> tuple[ManagedConfig, dict[str, CLIConfig]]:
    """For check-config: defaults and every role admitted by a V5 preset."""
    path = Path(path)
    config, agents = _build(_read(path), path)
    return config, {**agents, **{f'preset.{name}.{role}': cli
                               for name, (value, cli) in config.registrar.presets.items()
                               for role in value['roles']}}


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
                          'documents': p.context.documents, 'bootstrap_enabled': p.bootstrap_enabled,
                          'work_language': p.context.work_language}
                         for p in config.projects]}
