# P012-T001 — Propuesta operativa de validación real

Fecha: 2026-10-24. Base del producto: `c5cfc9b4586dbdb64075624e268e2f187749d430`. **Estado: completada documentalmente; propuesta confirmada por el usuario.**
Decisión: [D184](../DECISIONS.md#d184--p012-t001-propuesta-operativa-y-codex-01640).
Contrato: [T001](../NEXT_STEPS.md#p012-t001--propuesta-operativa-y-consentimiento),
[criterios P012](../ROADMAP.md#p012--validación-real-previa-a-la-apertura-pública).

Este documento concreta los tres tramos; no autoriza ejecutarlos. El usuario ya ha confirmado usar **Codex
0.164.0 instalado**, con compatibilidad condicionada de D174, al encontrar una diferencia con el 0.163.0
previsto por D183. Después ha confirmado **«Confirmar T001 con estos parámetros; sin autorizar tramos»**:
área, puertos, modelos/esfuerzos, TOML, fixtures, política, presupuestos, paradas y puerta offline previa a proveedores.
T001 queda completa como propuesta documental; T002–T004 siguen sin autorización operativa.

## 1. Área y fronteras propuestas

`AREA = $HOME/Documents/harness-validation/p012-20261024`. Área elegida expresamente al confirmar T001; no se ha creado.
Inspección de solo lectura: destino inexistente, sin componentes simbólicos ni ancestros con `.git`.
Repetir esas guardias antes de crear; directorios privados 0700, archivos de configuración 0600, `umask 077`.
Los enlaces propios de venv y lanzadores se resuelven y acreditan: no se confunden con enlaces en los destinos
operativos. No se copia ni consulta ninguna instalación de P009 ni ReferenceProject.

| Destino bajo AREA | Uso |
|---|---|
| `dist/`, `venv/` | Distribución verificada y entorno del harness (Python 3.14.4) |
| `config/harness-local.toml` | TOML de §4, privado; npmrc de usuario y global distintos y vacíos |
| `state/`, `tmp/`, `command-home/` | SQLite/artefactos; temporales; HOME de comandos del perfil |
| `wheels/`, `npm-cache/`, `uv-cache/` | Wheelhouse Django propio; cachés privadas, sin descargas |
| `projects/onboarding-b` | Repositorio Django mínimo B, sin receta |
| `projects/typescript-es` | Hijo nuevo creado por el servicio, receta TypeScript v2 |
| `backups/t003`, `restored/t003` | Bundle y restauración de consulta, destinos nuevos |

Servicio operativo en **127.0.0.1:8024**; restauración de consulta en **127.0.0.1:8025**. `lsof` no observó
listeners en ambos puertos al preparar T001; repetir antes de arrancar, sin sustituir un puerto ocupado.
El verificador del wheel usa además puertos efímeros de loopback y CLI falsas; se incluyen expresamente en
la preparación que deberá autorizar T002. Ningún servicio se ha arrancado en T001.

Raíz de registro y padre elegido desde UI: `AREA/projects`, solo esos dos hijos. Trabajo **es** en ambos;
visual propuesto **es**. Autor Git sintético `P012 Synthetic Operator <p012@example.invalid>`;
identidad local por operación, sin `git config --global`. Sin remotos, submódulos, filtros ni datos privados.

## 2. Toolchain observada y modelos propuestos

Solo `--version` para versiones; `--help` de las dos CLI para vocabulario, sin prompt, login/status ni inferencia.
Comprobación por UID: usuario `acosta`. Rutas de entrada y destinos físicos:

| Herramienta | Versión observada | Ruta de entrada |
|---|---|---|
| Codex | **0.164.0**, elegida expresamente por el usuario | `$HOME/.nvm/versions/node/v24.15.0/bin/codex` |
| Claude Code | **2.1.310** | `$HOME/.local/bin/claude` |
| Python del harness/build | **3.14.4**, requerido por `pyproject.toml` | `/opt/homebrew/bin/python3` |
| Python de B | **3.13.13** | `/opt/homebrew/bin/python3.13` |
| Node / npm | **24.15.0 / 11.12.1** | `$HOME/.nvm/versions/node/v24.15.0/bin/node`, `$HOME/.nvm/versions/node/v24.15.0/bin/npm` |
| uv | **0.12.19** | `/opt/homebrew/bin/uv` |

Python 3.13.13 de la tarea corresponde al fixture; instalar el harness en él violaría `requires-python >=3.14,<3.15`.
Se explicita la separación de ARCHITECTURE §1/9, sin cambiar stack ni dependencias.

| Artefacto físico observado | SHA-256 |
|---|---|
| Lanzador Codex `…/lib/node_modules/@openai/codex/bin/codex.js` | `61b0194f3bb6534439c8d26a3ed57d0805f84b884588b761795323eeb92fcf70` |
| Nativo Codex `…/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex` | `d8990e3ee7acfbc26f91265b12a1a83f0fee40d0e0f8f1f40a37d4ec21f499cf` |
| Claude `$HOME/.local/share/claude/versions/2.1.310` | `ffb64331bc0ee1b69efb7c2c428bd3ab516bc31b75bf60886b356c97c1c25ffd` |
| Node (ruta de entrada física) | `3200fbd9f7fd4410426dd541e10d1ab829d3472f270d743c7fabd1696c03fe32` |
| npm `…/lib/node_modules/npm/bin/npm-cli.js` | `8e5f6f3429f8cdbe693cdc29904e9d5a7b127a494bd15c804bd54c7403bfcbe7` |
| Python 3.14.4, binario resuelto de Homebrew | `02a8df1726463faedb3adef289b3d1bdeabb7785c837fd8c174023aeeeb4d312` |
| Python 3.13.13, binario resuelto de Homebrew | `4be5bd974c413ea1817a33d091f9470bb8735355d182db7fb852977e266d647e` |
| uv `/opt/homebrew/Cellar/uv/0.12.19/bin/uv` | `7522b8347a9d65188592b04ffacaf97d57b6623e795d82b8162e66331f0d5bff` |

Son hashes locales de código, sin certificación de dependencias opacas. La resolución/preflight de `cli-14`
acredita otra vez la identidad de lanzamiento por intento y antes de GO; una deriva obliga a parar.
Ambas CLI son posteriores al mínimo: **compatibilidad condicionada**, no evidencia de semántica interna nueva.

| Rol | Selección propuesta | Fuente local, sin red ni llamada a modelo |
|---|---|---|
| Revisor Claude | `sonnet`, esfuerzo `low`, timeout 1800 s | `claude --help` documenta el alias y esfuerzos `low, medium, high, xhigh, max` |
| Ejecutor Codex | **`gpt-6-luna`**, único modelo, esfuerzo **`low`**, timeout 3600 s | Catálogo local `~/.codex/models_cache.json`, `fetched_at=2026-10-24T16:11:23.174494Z`: «Fast and affordable model for easier tasks», admite `low` |

El catálogo se ha leído filtrando metadatos de modelos; no se copia su identidad ni el archivo al repositorio.
La ayuda de Codex solo documenta `--model`, no enumera el catálogo. El catálogo local justifica el nombre
propuesto, pero no prueba disponibilidad/autorización de cuenta ni éxito de una invocación. No se han consultado
fuentes remotas por la restricción de red de P012. `sonnet` es un alias mutable: registrar el modelo reportado
si la CLI lo proporciona, sin inventarlo ni cambiar el alias aprobado. No se evalúa calidad comparativa.

Política que debe confirmarse en UI para **ambos proyectos**:

```toml
planning_mode = "agent"
executor_mode = "catalog"
executor_models = ["gpt-6-luna"]
executor_efforts = ["low"]
max_revision_cycles = 0
```

Cero correcciones automáticas hace efectiva la parada en la primera validación fallida o revisión REVISE;
un presupuesto de llamadas sobrante no permite relanzar. Sin catálogo abierto, fallback de pareja/modelo/esfuerzo
ni ampliación de permisos. El revisor planifica, conversa, revisa y evalúa la fase con la misma selección.

## 3. Base, hashes y guion offline pendiente de ejecutar

Base del wheel: **`c5cfc9b4586dbdb64075624e268e2f187749d430`** (`0.1.0`, esquema `0025_project_work_languages`).
Solo se construyen fuentes de esa base: si hay cambios en `src/`, scripts de construcción, README, metadatos o locks,
parar y actualizar la propuesta. Los cambios documentales privados de T001 no entran en el paquete.

| Entrada esperada | SHA-256 comprobado en T001 |
|---|---|
| `uv.lock` | `69091b66855c9765eedd53b35356f419149fdb1bc9ba2fc1402ff2002f48fbc3` |
| `frontend/package-lock.json` | `f7ce4d6eb4e9d97adb644782d83c82e4c99b8263012f749d1154c8e9866aec0f` |
| Lock Django empaquetado | `0f2ce9afc90274a6da1b6c1d8b10cc62d6f530dd0b1f1c8c95609fd27d313c1b` |
| `README.md` | `5990e69defd797865ebe6201401d44b533d3d3f98d19c3118af4906ee6fa03ad` |

**Wheel/sdist/pylock/SHA256SUMS de P012 aún no existen.** No se atribuye al futuro wheel el hash del de P011 ni
se presume una reconstrucción reproducible. En la preparación offline de T002, antes de cualquier proveedor,
registrar sus hashes completos, verificar miembros exactos y checksums, y revisar el TOML materializado y su hash.
El usuario confirma este punto de control diferido al aceptar la propuesta; T001 es documental y no acredita
hashes de artefactos operativos ni preflight ejecutado.

Guion futuro, no ejecutado; `AREA` y `REPO` son variables del guion, no cambios del entorno global:

```sh
AREA=$HOME/Documents/harness-validation/p012-20261024
REPO=$HOME/Documents/projects/my_harness
# Desde REPO; TMPDIR ya creado 0700 bajo AREA. Herramientas con PATH explícito de §2.
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/build_distribution.py --out-dir "$AREA/dist"
UV_CACHE_DIR="$REPO/.local/uv-cache" TMPDIR="$AREA/tmp" uv run --frozen --offline python scripts/check_distribution.py --dist "$AREA/dist"
# Contrastar SHA256SUMS y guardar los hashes antes de instalar (hashlib o shasum -a 256 -c).
UV_CACHE_DIR="$AREA/uv-cache" uv venv --offline --no-python-downloads --python /opt/homebrew/bin/python3 "$AREA/venv"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip sync --offline --python "$AREA/venv/bin/python" "$AREA/dist/pylock.toml"
UV_CACHE_DIR="$REPO/.local/uv-cache" uv pip install --offline --no-deps --python "$AREA/venv/bin/python" "$AREA/dist/harness_local-0.1.0-py3-none-any.whl"
# B: entorno separado, wheelhouse propio con un wheel compatible por pin/hash del lock empaquetado.
UV_CACHE_DIR="$AREA/uv-cache" uv venv --offline --no-python-downloads --python /opt/homebrew/bin/python3.13 "$AREA/projects/onboarding-b/.venv"
UV_CACHE_DIR="$AREA/uv-cache" uv pip install --offline --no-index --no-deps --no-build --require-hashes --find-links "$AREA/wheels" --python "$AREA/projects/onboarding-b/.venv/bin/python" -r "$AREA/config/django-requirements.lock"
# Desde AREA, sin PYTHONPATH ni importación de producto desde REPO; entorno de servicio descrito debajo.
"$AREA/venv/bin/harness-local" check-config "$AREA/config/harness-local.toml" --preflight
"$AREA/venv/bin/harness-local" init-db --database "$AREA/state/harness.sqlite3"
"$AREA/venv/bin/harness-local" serve --database "$AREA/state/harness.sqlite3" --config "$AREA/config/harness-local.toml" --port 8024
```

La instalación usa el **`pylock.toml` PEP 751 con hashes**, no el antiguo `requirements.txt` de P010-T008.
El wheel se instala solo tras validar su SHA-256 contra `SHA256SUMS` revisado. No ejecutar `scripts/dev`.
El build escribe assets locales en `frontend/dist` y usa las cachés existentes del checkout; el verificador instala
un venv temporal y prueba el producto con CLI falsas. No opera este repositorio como proyecto del harness.

Servicio desde AREA con entorno explícito: PATH de venv, Node, uv y `/usr/bin:/bin`; `HOME=AREA/command-home`,
`TMPDIR=AREA/tmp`, `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `LANG=C.UTF-8`; sin `PYTHONPATH` ni
configuración ambiental del harness. Las CLI de agentes reciben sus entornos propios del TOML con HOME autenticado;
no se copian credenciales al área ni se cambia configuración global.

El wheelhouse de B debe construirse **desde cachés locales existentes**, no desde P009: seleccionar wheels
compatibles con macOS arm64/CPython 3.13, comprobar nombre/pin y hash contra el lock, y guardar manifiesto propio.
No se ha inspeccionado ni poblado en T001. Copiar el lock del wheel instalado y contrastar el hash de la tabla.
Para TypeScript, crear caché propia copiando solo los objetos necesarios de una caché local permitida y verificar
la integridad del tarball `typescript@5.9.3` contra el lock generado por la receta v2. No copiar npmrc ni tokens.
Si faltan objetos, wheels o metadatos de uv/npm: **parar**, con lista de faltantes; ninguna descarga implícita.
Una descarga futura requiere consentimiento separado con lista y hashes.

## 4. TOML completo propuesto (datos, no configuración activa)

Materializar solo bajo autorización de T002, en el área elegida. Perfil declarado copiado literalmente del ejemplo vigente; no se activa
la receta Django ni su formateador. No hacen falta presets adicionales: defaults fijos y catálogo de política
confirmado en el registro/creación de cada hijo. Sin `[[projects]]`: ambos se registran desde UI.
`bootstrap_enabled=true` habilita la creación exclusivamente bajo la raíz acotada; B no usa bootstrap.

```toml
format = "local-config-7"

[service]
state_dir = "$HOME/Documents/harness-validation/p012-20261024/state"
supervisor = true

[git]
executable = "/usr/bin/git"
author_name = "P012 Synthetic Operator"
author_email = "p012@example.invalid"

[agents.reviewer]
provider = "claude"
model = "sonnet"
effort = "low"
executable = ["$HOME/.local/bin/claude"]
timeout_seconds = 1800
environment = { HOME = "$HOME", USER = "acosta", PATH = "$HOME/.local/bin:$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", LANG = "C.UTF-8", PYTHONDONTWRITEBYTECODE = "1" }

[agents.executor]
provider = "codex"
executable = ["$HOME/.nvm/versions/node/v24.15.0/bin/codex"]
timeout_seconds = 3600
environment = { HOME = "$HOME", USER = "acosta", PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", LANG = "C.UTF-8", PYTHONDONTWRITEBYTECODE = "1" }

[registration]
roots = ["$HOME/Documents/harness-validation/p012-20261024/projects"]
bootstrap_enabled = true

[profiles.python-django]
preparation = [
  { argv = ["python", "--version"], timeout_seconds = 30 },
  { argv = ["python", "-m", "django", "--version"], timeout_seconds = 30 },
]
validations = [
  # The JUnit report is declared with its validation; `.local/` must be in the project's .gitignore.
  { argv = ["pytest", "--junitxml=.local/junit.xml", "-q"], timeout_seconds = 900, junit = { path = ".local/junit.xml", coverage = "Project pytest tests; not code coverage" } },
  { argv = ["ruff", "check", "."], timeout_seconds = 120 },
  { argv = ["ruff", "format", "--check", "."], timeout_seconds = 120 },
  { argv = ["mypy", "."], timeout_seconds = 600 },
  { argv = ["python", "manage.py", "check"], timeout_seconds = 120 },
  { argv = ["python", "manage.py", "makemigrations", "--check", "--dry-run", "--noinput"], timeout_seconds = 120 },
]
# Prefixes a task contract can cite; running them also requires the exact authorization.
allowed_command_prefixes = [["pytest"], ["ruff", "check"], ["ruff", "format", "--check"], ["mypy"],
                            ["python", "manage.py", "check"], ["python", "manage.py", "makemigrations", "--check"]]
protected_paths = ["docs/STATE.md", "docs/NEXT_STEPS.md", "docs/ROADMAP.md", "docs/DECISIONS.md", "docs/archive/**",
                   "AGENTS.md", "CLAUDE.md", "GEMINI.md", ".harness/**", ".codex/**", ".claude/**",
                   "pyproject.toml", "uv.lock", "poetry.lock", "requirements*.txt", "setup.cfg", "tox.ini",
                   "pytest.ini", "mypy.ini", "ruff.toml", ".ruff.toml", "manage.py", ".gitignore"]
sensitive_paths = [".env", ".env.*", "**/.env", "**/.env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "*.sqlite3"]
sensitive_allowlist = [".env.example"]
# Parity (D090): a diff touching these paths without docs/DDBB-DIAGRAM.md is not accepted.
data_model_paths = ["**/models.py", "**/models/**", "**/migrations/**"]
executor_instructions = """Implement the Django change within the frozen task paths, with pytest tests next to it. \
Keep ruff check, ruff format --check, mypy, manage.py check and makemigrations --check passing; \
add migrations for model changes and update docs/DDBB-DIAGRAM.md in the same task. \
Do not weaken tests, tool settings, dependencies or their locks. Dependency installation, \
database services and network access require separate authorization."""

[compositions.django]
profile = "python-django"
authorize_profile_commands = true
executables = { python = "$HOME/Documents/harness-validation/p012-20261024/projects/onboarding-b/.venv/bin/python", pytest = "$HOME/Documents/harness-validation/p012-20261024/projects/onboarding-b/.venv/bin/pytest", ruff = "$HOME/Documents/harness-validation/p012-20261024/projects/onboarding-b/.venv/bin/ruff", mypy = "$HOME/Documents/harness-validation/p012-20261024/projects/onboarding-b/.venv/bin/mypy" }
environment = { HOME = "$HOME/Documents/harness-validation/p012-20261024/command-home", PATH = "$HOME/Documents/harness-validation/p012-20261024/projects/onboarding-b/.venv/bin:/usr/bin:/bin", TMPDIR = "$HOME/Documents/harness-validation/p012-20261024/tmp", LANG = "C.UTF-8", CI = "true", DJANGO_SETTINGS_MODULE = "config.settings", PYTHONDONTWRITEBYTECODE = "1" }

[recipes.typescript-web]
node_executable = "$HOME/.nvm/versions/node/v24.15.0/bin/node"
node_version = "24.15.0"
npm_executable = "$HOME/.nvm/versions/node/v24.15.0/bin/npm"
npm_version = "11.12.1"
npm_cache = "$HOME/Documents/harness-validation/p012-20261024/npm-cache"
allow_network = false
timeout_seconds = 120
max_output_bytes = 65536

[compositions.typescript]
profile = "typescript-web"
recipe = "typescript-web"
authorize_profile_commands = true
executables = { node = "$HOME/.nvm/versions/node/v24.15.0/bin/node", npm = "$HOME/.nvm/versions/node/v24.15.0/bin/npm" }
environment = { HOME = "$HOME/Documents/harness-validation/p012-20261024/command-home", PATH = "$HOME/.nvm/versions/node/v24.15.0/bin:/usr/bin:/bin", TMPDIR = "$HOME/Documents/harness-validation/p012-20261024/tmp", LANG = "C.UTF-8", CI = "true", npm_config_cache = "$HOME/Documents/harness-validation/p012-20261024/npm-cache", npm_config_userconfig = "$HOME/Documents/harness-validation/p012-20261024/config/user.npmrc", npm_config_globalconfig = "$HOME/Documents/harness-validation/p012-20261024/config/global.npmrc", npm_config_update_notifier = "false" }
```

Antes de usar: revisar entero, permisos 0600, autor/raíces/entornos, ejecutables resueltos, `npmrc` vacíos,
perfil y política de UI; ejecutar `check-config --preflight` con la CLI instalada. Este diagnóstico usa version/help,
no modelos, y no certifica auth ni inferencia. El TOML propuesto no se ha cargado en un servicio ni escrito fuera
de `docs/`. Las rutas de `.venv` requieren preparar B primero; TOML sintáctico no equivale a preflight aprobado.

## 5. Fixtures y recorridos observables

**T002 — B y perfil D095.** Escribir fixture original sintético: `manage.py`, `config/settings.py`, `config/urls.py`,
`catalog/models.py` (`Item` con nombre), `catalog/migrations/0001_initial.py`, `catalog/views.py`,
`catalog/urls.py`, `catalog/tests/test_views.py`, inicializadores, README y `pyproject.toml` con pytest-django,
ruff y mypy/django-stubs. Vista `GET /items/?limit=…` que devuelve elementos ficticios; partida con límite válido
fijo. SQLite de pruebas temporal, secreto de desarrollo ficticio, sin red ni base de uso. `.gitignore` excluye
`.venv/`, `.local/`, bytecode y SQLite. Sin documentos del harness ni `.harness/` antes de incorporación.

Preparar un commit Git inicial con identidad sintética y manifiesto de rutas/modos/SHA-256. Antes de registrar,
ejecutar las **dos preparaciones y seis validaciones** del TOML; deben estar en verde con JUnit. No sustituir
el perfil declarado por la receta ni añadir formateo automático. Registrar trabajo `es`, composición `django`
y política de §2. El inventario debe citar modelo, migración, ruta/vista y tests con procedencia.
Conversar con el revisor, revisar los documentos D088 y flujos, marcar decisiones inferidas y resolver por HITL
lo no deducible. Confirmar preview y perfil por hash desde UI: un solo commit documental, código intacto por bytes
y modos, P001 ACTIVE; repetir la **misma confirmación**, sin otro turno de modelo, no duplica efectos.

Única tarea propuesta: validar `limit` como entero entre 1 y 20; valores inválidos devuelven HTTP 400 y se añaden
casos de límite, texto y fuera de rango. Rutas de ejecutor `catalog/views.py`, `catalog/tests/test_views.py` y el
flujo documental concreto que confirme el contrato. Sin dependencias, modelos, migraciones ni ajustes de herramientas.
Plan del revisor → una ejecución Codex → seis validaciones/JUnit → revisión → aceptación del contenido exacto
→ COMMITTED con commit único. Guardar diff aceptado, fuentes CLI por intento y los contadores. No cerrar P001 de B.

**T003 — chat y backup.** Sobre HEAD de B: una pregunta que cite la vista y los tests; un comando determinista
`/estado` (sin modelo); una propuesta del revisor convertida en tarea confirmada por hash, **sin ejecutarla**.
Verificar instantánea HEAD y ausencia de lock escritor por chat. Detener servicio y grupos propios, comprobar
escritores detenidos; solo entonces usar:

```sh
"$AREA/venv/bin/harness-local" backup-create "$AREA/state/harness.sqlite3" "$AREA/backups/t003" --artifact-root "$AREA/state" --writers-stopped
"$AREA/venv/bin/harness-local" backup-verify "$AREA/backups/t003"
"$AREA/venv/bin/harness-local" backup-restore "$AREA/backups/t003" "$AREA/restored/t003"
"$AREA/venv/bin/harness-local" serve --database "$AREA/restored/t003/state.sqlite3" --port 8025
```

La restauración escribe `state.sqlite3`, contrastado estáticamente con `storage/backup.py`; comprobar además
el manifiesto de la operación antes del último comando. Si las referencias de artefactos exigen otra raíz privada,
revisarla antes de crear el bundle; no ampliar a HOME. Abrir restauración sin `--config` y sin supervisor:
comprobar run, diff, JUnit y métricas de T002 y rechazo de mutaciones; no ejecutar jobs ni alterar la base operativa.
La tarea de chat queda pendiente, sin job activo. No es copia del checkout ni reactivación operativa (D040).
Detener también la consulta al terminar y conservar el área.

**T004 — TypeScript v2.** Reiniciar solo el servicio operativo bajo autorización del tramo; elegir padre desde UI,
crear `typescript-es` con trabajo `es`, composición `typescript`, política §2 y visual propuesto `es`.
Definición conversacional con revisor real, borradores CAS y D088 en español. El proyecto mínimo mantiene el
scaffold empaquetado: página con título y función `heading`; única tarea de P001, normalizar espacios interiores
del título en `src/main.ts`, conservando la API `heading`, el valor por defecto y el sufijo existentes.
Confirmar receta offline `typescript-web-recipe-2`: idioma/hash sellados en plan/recibo, `typescript@5.9.3`
desde la caché propia, check/test/build con JUnit y commit técnico separado.

La tarea solo permite `src/main.ts` y el documento de flujo concreto aprobado en su contrato. `tests/**`,
`scripts/**`, dependencias y configuración están protegidos por el perfil; no autorizar editarlos ni proponer
un test junto a `src` que el runner no ejecutaría. Se usa la suite existente de `tests/main.test.mjs`; sus casos
cubren título normal/vacío, y no se presentan como cobertura nueva de espacios interiores. La inspección del diff
comprueba la transformación acotada. Una ejecución, validación, revisión y COMMITTED; comentarios y documentos
nuevos en español, sin traducir identificadores de API/protocolo ni confundir trabajo con idioma funcional.
READY check con revisor, cierre autorizado **de P001 de este hijo** con tag/archivo mediante el producto y
planificación confirmada de la siguiente fase sin tareas. No se autoriza tag en `my_harness` ni acciones remotas.
Detener servicio y grupos; conservar el área.

## 6. Presupuesto, parada y recuperación

| Tramo | Techo Claude (incluye fallidas) | Techo Codex | Tiempo de pared |
|---|---|---|---|
| T002 | **12**: hasta 8 turnos B, plan/revisión y margen dentro del mismo recorrido | **3**, pero solo 1 ejecución normal; sin reintento tras fallo | **4 h** |
| T003 | **3**: respuesta, propuesta y eventual aclaración | **0** | **2 h** |
| T004 | **12**: hasta 6 definición, plan/revisión, READY, sucesora y aclaraciones | **3**, pero solo 1 ejecución normal; sin reintento tras fallo | **4 h** |
| Total máximo de fase propuesto | **27** | **6** | Sin traspasar reservas entre tramos |

Llevar contador antes/después de cada invocación; cuentan selección/planes/evaluación/fallidas si requieren CLI.
Al agotarlo o alcanzar el tiempo, no iniciar otra llamada y solicitar parada del trabajo propio activo.
No se garantiza techo de tokens/dinero ni control de retries internos del proveedor (D019); las llamadas son
invocaciones observables de la CLI. El sobrante no autoriza otras tareas ni consume automáticamente correcciones.

Parar al **primer** fallo de proveedor, auth, esquema, timeout, validación, permisos, REVISE, CAS, hashes,
composición, cache, cuarentena, destinos o base. No variar modelo, permisos, versión, pareja, presupuesto ni red.
Preguntas normales de conversación se resuelven por HITL dentro del techo. Un defecto del producto se documenta
con evidencia saneada y nueva T008 o posterior con tests sintéticos; no corregir a mano el resultado de un agente,
ni editar SQLite/TOML para desbloquear, ni relanzar sin consentimiento nuevo.

Tras caída: conservar HEAD, intención, journal, diff y streams; usar cancelación/confirmación de escritor detenido
del producto, nunca señalar un PID histórico. Conciliar solo un commit ya sellado, sin nuevas llamadas ni cambios
de composición, bajo autorización vigente. Una repetición de efectos, preparación o invocación exige consentimiento
nuevo. No forzar caídas, restaurar sobre la base ni borrar resultados para simular éxito.

Al terminar o parar, detener servicio y grupos propios y acreditar ausencia de locks/jobs activos o declarar
exactamente las reservas inciertas. No afirmar parada si no puede comprobarse. Conservar área, venv, fixtures y
bases para revisión; solo temporales propios con limpieza normal del producto. Borrado persistente, retención
de streams y eliminación del área requieren petición posterior.

## 7. Evidencia y decisión HITL

En `docs/phase/`: base/hash de producto, toolchain/plataforma, hashes CLI/wheel/lock/TOML, comandos y resultados,
manifiestos sintéticos, ids abreviados, llamadas por proveedor frente al techo, JUnit resumido, código B intacto
tras incorporación, diff/commits de tareas, idioma/recibo v2, backup/consulta y parada. Sin valores de entorno
sensibles: el TOML de §4 solo contiene rutas y datos sintéticos explícitos.
Prompts completos, streams, tokens de sesión, SQLite, credenciales y capturas con datos privados quedan en AREA.
Cada resultado parcial distingue afirmaciones acreditadas y pendientes; ningún recorrido equivale a aprobación total.

**Decisión del usuario el 2026-10-24:** «Confirmar T001 con estos parámetros; sin autorizar tramos».
Quedan elegidos AREA, puertos, pareja/modelos/esfuerzos, autor, fixtures, política, presupuestos, paradas y guion.
El usuario acepta comprobar hashes operativos de artefactos aún no construidos, cachés/fixtures y preflight durante
la preparación offline de T002, antes de proveedores. No se presentan como ejecutados o acreditados en T001.
Los criterios documentales y la decisión HITL están resueltos; las comprobaciones operativas siguen pendientes.

**Autorizaciones separadas:** T001 confirmada no autoriza T002, T003 ni T004. Al solicitar T002 se debe cubrir
expresamente construcción/verificador con CLI falsas, instalaciones/fixtures offline, servicio/UI y las llamadas
de su presupuesto. T003 y T004 requieren su propia autorización posterior. Sin commits de este repositorio salvo
petición del usuario, sin push, apertura remota, Release ni publicación.

## 8. Contraste y validación documental

- D095: perfil declarado exacto, seis validaciones/JUnit y sin formateador; D119: identidad, entorno y recuperación,
  sin confundir el perfil B con la receta Django histórica.
- D143/D168: receta TypeScript v2, caché propia offline, perfil/rutas protegidas e idioma sellado; D151: propuesta
  histórica como antecedente, sin reescribirla ni reutilizar sus consentimientos; A retirado por D155/D161.
- D173/D174: clientes observados, identidad/preflight por intento, mínimo y compatibilidad condicionada;
  [flujo CLI](../flows/cli-compatibility.md).
- [Incorporación](../flows/project-onboarding.md), [tarea](../flows/task-run.md),
  [chat](../flows/chat.md), [preparación](../flows/project-preparation.md),
  [creación](../flows/project-creation.md), [fase](../flows/phase-lifecycle.md),
  [arquitectura §9](../ARCHITECTURE.md#9-desarrollo-y-operación), SPECIFICATION §§9/13 y D040.

| Comprobación | Resultado |
|---|---|
| Parsers puros `parse_roadmap`, `plan_tasks`, `decision_index` | 12 fases, 7 criterios P012, 7 tareas, 184 decisiones |
| Enlaces y anclas relativos de los cinco Markdown cambiados/nuevos | 553 comprobados, sin rotos |
| TOML de política y configuración | Ambos parsean; perfil Django idéntico al ejemplo, seis validaciones, catálogo único y cero correcciones |
| Presupuestos D088 | STATE/base/NEXT_STEPS por debajo de 24.576/12.288/49.152 bytes |
| Conservación frente a la base | Cuerpos D001–D183, archivos, producto, baseline pública, diagrama y flujos intactos |
| Diff y `git diff --check` | Revisados, sin errores de espacios; solo `docs/**` |
No se ejecutan suites del producto, build, instalación, preflight del harness, servicios, agentes o proveedores en
T001; solo lecturas, `--version`/`--help`, hashes locales y comprobaciones documentales puras. Sin cambios de
código, datos, API o flujos implementados; DDBB-DIAGRAM y flujos se conservan.
