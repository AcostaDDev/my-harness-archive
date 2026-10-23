# my_harness — Harness Local

Aplicación local para configurar, ejecutar y observar un harness de desarrollo con agentes. Planifica, ejecuta,
valida, revisa y hace commit de tareas acotadas sobre tus repositorios, organizadas en fases, con chat, métricas,
tests y documentación por proyecto. Todo corre en tu máquina: el servicio solo escucha en `127.0.0.1` y los modelos se
usan a través de las CLI de Codex y Claude Code con tu propia suscripción.

## Estado

Fases P001–P010 completadas y archivadas. La [primera versión local](docs/archive/phase-010/SUMMARY.md)
queda cerrada documentalmente el 2026-10-22: receta TypeScript web, lecturas acotadas de runs y métricas,
marcadores opcionales, evidencia de fases cerradas y migración explícita de bases. Los trece criterios globales
tienen [matriz de aceptación](docs/archive/phase-010/P010_MATRIZ_ACEPTACION.md); el wheel final y la QA sintética
cuentan con [dictamen favorable](docs/archive/phase-010/REVIEW.md) en el alcance declarado.
B y el perfil Django declarado conservan su validación solo offline por decisión D151; los límites se detallan
más abajo. El paquete sigue en `0.1.0`, sin publicación. P011 prepara la apertura pública; T019 retira el soporte del harness anterior.
Detalle en [ROADMAP](docs/ROADMAP.md) y [STATE](docs/STATE.md).

## Accesos al producto

- Crear un proyecto nuevo desde un brief, confirmar sus documentos y preparar la receta elegida.
- Incorporar un repositorio existente sin harness, revisar su inventario/documentos y confirmar el perfil y P001.

Ambos continúan como proyectos gestionados. Registrar o reabrir uno ya gestionado conserva su autoridad existente.
El soporte del harness anterior está retirado: sus URLs muestran página no encontrada, la API antigua devuelve 404
tras las guardias y los comandos antiguos se rechazan. No se borran datos del usuario. Las instalaciones anteriores
conservan historiales y backups; los trabajos A pendientes se ponen en cuarentena y requieren confirmar el escritor
detenido, sin ejecutar sus intenciones. Activaciones incompletas bloquean para resolución manual.
[Compatibilidad y recuperación](docs/flows/legacy-migration.md).

## Requisitos

- macOS; solo se ha probado en ARM64. Otras plataformas no están caracterizadas.
- Servicio: Python 3.14.4 y uv 0.12.19. Git del sistema (verificado con 2.50.1); las importaciones de proyectos
  existentes exigen un Git con `--no-lazy-fetch`.
- Construir el paquete o desarrollar: además Node 24.15.0 y npm 11.12.1, con las cachés `.local/` ya pobladas.
- Uso real: CLI ya autenticadas. `local-config-7` detecta los clientes y sus versiones por el PATH explícito;
  no hay que introducir la versión. Adaptador `cli-14` (D174): mínimos estables Codex 0.163.0 y Claude 2.1.304;
  si son inferiores, indica actualizar. Las posteriores compatibles se admiten automáticamente por capacidades.

| CLI | Revisor (solo lectura) | Ejecutor (escritura) | Uso real registrado |
|---|---|---|---|
| `codex` | ≥0.163.0 con capacidades compatibles | ≥0.163.0 con capacidades compatibles | 0.162.1 (D050, D071) y 0.163.0 (piloto P009, D139) |
| `claude` | ≥2.1.304 con capacidades compatibles | ≥2.1.304 con capacidades compatibles | 2.1.295 (D050), 2.1.296 (D071) y 2.1.304 (piloto P009) |

Los usos reales anteriores son históricos: se hicieron con el adaptador vigente en su momento. Las releases
posteriores son candidatas con compatibilidad condicionada al contrato conocido, sin afirmar efectos internos
verificados ni garantizar cualquier versión futura. Los controles de permisos, memoria y confianza se mantienen;
una incompatibilidad detectada bloquea. [Contrato y límites](docs/phase/P011-T012_COMPATIBILIDAD_CLI.md).

## Instalación para uso real

El uso real se opera desde el paquete construido, nunca desde este checkout (D051). Todo es offline salvo la primera
población de las cachés:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/build_distribution.py --out-dir /ruta/paquete
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/check_distribution.py --dist /ruta/paquete
uv venv --python 3.14.4 --no-python-downloads /ruta/venv
uv pip sync --python /ruta/venv/bin/python --require-hashes /ruta/paquete/requirements.txt
uv pip install --python /ruta/venv/bin/python --no-deps /ruta/paquete/harness_local-0.1.0-py3-none-any.whl
```

Configuración: copia [la plantilla TOML](examples/local_config.example.toml) fuera de todo checkout, `chmod 600`, y
ajusta agentes, Git, composiciones y raíces de registro. La plantilla es `local-config-7`: incluye detección
automática sin versión obligatoria, idioma de trabajo inmutable y presets por proyecto (`[agent_presets.*]`, D118).
El PATH declarado debe incluir los clientes; una ruta de ejecutable explícita es opcional. Las recetas de
proyectos nuevos: [TypeScript web](examples/typescript-web-recipe.example.toml) y
[Django](examples/django-recipe.example.toml) se añaden como fragmentos. Los formatos 1–6 se siguen leyendo;
sus pins explícitos deben coincidir y las CLI deben cumplir los mínimos nuevos. Después:

```sh
/ruta/venv/bin/harness-local check-config /ruta/harness-local.toml --preflight
/ruta/venv/bin/harness-local init-db --database /ruta/state/harness.sqlite3
TMPDIR=/ruta/tmp-privado /ruta/venv/bin/harness-local serve --database /ruta/state/harness.sqlite3 --config /ruta/harness-local.toml
```

`--preflight` solo ejecuta `--version`/`--help` de cada CLI. Abre `http://127.0.0.1:8013` y pega la clave de sesión
del archivo privado que anuncia el arranque (bajo `TMPDIR`, válida ocho horas). Con `supervisor = true` el servicio
consume la cola, invoca las CLI configuradas y gasta tu suscripción.

**Actualizar.** Detén el servicio, observadores y escritores; instala el nuevo wheel en su venv y ejecuta:

```sh
/ruta/venv/bin/harness-local migrate --database /ruta/state/harness.sqlite3 --snapshots /ruta/copias-previas --writers-stopped
```

`migrate` actualiza una base existente de una revisión conocida con una instantánea SQLite previa verificada y un
manifiesto `premigration-1` (integridad, revisión y SHA-256). Ambas rutas son absolutas y el directorio de copias debe
estar fuera de los checkouts. Devuelve JSON con acción, revisiones y ruta de la copia; una base al día queda intacta,
sin otra copia. Rechaza propietarios/grupos vivos registrados, restauraciones de consulta, revisiones desconocidas,
bases sin Alembic y enlaces. `--writers-stopped` declara también la parada de un servicio sin trabajos registrados.
Ante un fallo conserva base y copia para inspección, sin restaurar automáticamente. Tras el éxito, arranca `serve`.
`init-db` sigue creando solo bases nuevas y `serve` exige el esquema del paquete sin migrar al arrancar (D043, D150).
La instantánea contiene solo SQLite; el backup completo de artefactos conserva su orden separada.

## Operación

```sh
harness-local backup-create /ruta/harness.sqlite3 /ruta/backup-nuevo --artifact-root /ruta/harness-state --writers-stopped
harness-local backup-verify /ruta/backup-nuevo
harness-local backup-restore /ruta/backup-nuevo /ruta/restaurada
```

El backup exige el servicio y los escritores detenidos y un destino nuevo; `--artifact-root` (repetible) autoriza
las raíces de artefactos, como el `state_dir` del TOML. La restauración crea una base nueva solo de consulta y exige
la misma revisión de esquema.

`logs-preview`, `logs-apply` y `logs-inspect` aplican la retención explícita de streams; `metrics-backfill` rellena
métricas; `diagnose-cli` completa la CLI. Cada orden documenta sus argumentos con
`--help`. Detalle y garantías en [ARCHITECTURE §9](docs/ARCHITECTURE.md#9-desarrollo-y-operación).

## Alcance soportado

| Capacidad | Offline (datos y agentes falsos) | Con proveedores reales |
|---|---|---|
| Ejecución → validación → revisión → commit, fases, cierre y archivo | Sí | Sí (D050, D071, D139) |
| Revisor/ejecutor Codex o Claude en las cuatro combinaciones | Sí | Sí (D071; piloto P009) |
| Proyecto Django nuevo con receta `django-recipe-1` | Sí | Sí, macOS arm64 y Python 3.13 (D139) |
| Proyecto TypeScript web nuevo con receta `typescript-web-recipe-1` | Sí, también con node/npm reales y caché local | No |
| Recetas v2 (`django-recipe-2`, `typescript-web-recipe-2`) con el idioma de trabajo del hijo, en `local-config-6` (D168) | Sí, con herramientas sintéticas | No |
| Perfil declarado (`[profiles.*]`, ejemplo `python-django`) | Sí | No; validación real aplazada en P010-T008 (D095, D151) |
| Incorporación B (código sin harness) | Sí | No; validación real aplazada en P010-T008 (D151) |
| Chat ligado a tareas, backup y restauración | Sí | Sin evidencia real localizada (matriz de T001) |
| Lecturas de runs, métricas y vista previa de exportación sin decodificar historiales | Sí, con historiales sintéticos de 26 y 35,4 MiB | No aplica |

Límites vigentes: contención cooperativa sin aislamiento del sistema operativo; el manifiesto que fija una receta
no admite dependencias nuevas tras preparar; el perfil `typescript-web` protege `package.json`, `scripts/**` y
`tests/**` frente al ejecutor; tras un reinicio del Mac, crear otro proyecto exige volver a elegir la carpeta (D130);
las validaciones no guardan su hora. Detalle en
[ARCHITECTURE §10](docs/ARCHITECTURE.md#10-límites-conocidos).

## Desarrollo

```sh
UV_CACHE_DIR=.local/uv-cache uv sync --frozen --no-python-downloads
npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache
scripts/dev
```

`scripts/dev` comprueba versiones, migra la SQLite local (`.local/harness.sqlite3`) con un backup previo y arranca la
API en `:8013` y Vite en `http://127.0.0.1:5173`. Admite `--database` y `--config`.

## Tests

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic check
node --test frontend/tests/*.test.mjs
npm --prefix frontend run check
npm --prefix frontend run build
```

Las pruebas usan Git, SQLite y procesos temporales con agentes falsos; no consumen proveedores ni red.

## Estructura

- `src/harness_local/`: núcleo y motor (`core/`), adaptadores, persistencia, servicios, recetas, API y migraciones.
- `frontend/`: UI React/TypeScript; `frontend/src/api.generated.ts` se genera desde OpenAPI.
- `tests/`: pruebas y fixtures sintéticos. `scripts/`: desarrollo y distribución.
- `examples/`: plantilla TOML, fragmentos de recetas y demos; `first_use/` y `provider_matrix/` son guiones
  históricos de operaciones ya realizadas, no instrucciones vigentes.

## Documentación

- [Especificación](docs/SPECIFICATION.md): requisitos y reglas de negocio.
- [Arquitectura](docs/ARCHITECTURE.md): stack, módulos, patrones, comandos y límites.
- [Roadmap](docs/ROADMAP.md), [estado](docs/STATE.md) y [siguientes pasos](docs/NEXT_STEPS.md).
- [Decisiones](docs/DECISIONS.md), [diagrama de datos](docs/DDBB-DIAGRAM.md) y [flujos](docs/flows/task-run.md).
- [Archivo de fases](docs/archive/phase-010/SUMMARY.md): entregas, revisión y evidencia de la última fase cerrada.
- Instrucciones para agentes: [AGENTS.md](AGENTS.md), con [CLAUDE.md](CLAUDE.md) y [GEMINI.md](GEMINI.md) como envoltorios.
