# Arquitectura — Harness Local

Stack, módulos, patrones y convenciones vigentes. Consolida la especificación inicial (§5–7, 9, 10 y 13), las
decisiones vigentes y la información técnica que antes estaba en README y AGENTS. Datos:
[DDBB-DIAGRAM](DDBB-DIAGRAM.md). Flujos: [docs/flows](flows/task-run.md).

## 1. Stack

| Capa | Elección y versión exacta |
|---|---|
| Núcleo | Python 3.14.4, biblioteca estándar, paquete `harness-local` 0.1.0 (`uv_build==0.12.19`) |
| API local | FastAPI 0.143.0, Pydantic 2.14.0, Uvicorn 0.54.0; HTTP para acciones, SSE para observación legacy |
| Persistencia | SQLite con SQLAlchemy 2.1.4 y Alembic 1.20.0 (esquema `0020_project_imports`) |
| UI | React 19.3.0, TypeScript 5.9.3, Vite 8.3.4; `markdown-it` 15.0.2 (`html: false`) y `mermaid` 11.17.2 (`strict`) |
| Tipos del cliente | `openapi-typescript` 7.13.0 desde el OpenAPI exportado |
| Herramientas | uv 0.12.19 y `uv.lock`; Node 24.15.0, npm 11.12.1 y `frontend/package-lock.json` |
| Pruebas | `unittest` (12 checks sin dependencias), pytest 9.1.1 + httpx 0.28.1, `node --test` |
| Agentes | CLI `codex` 0.161.0/0.162.1 (escritura solo 0.162.1) y `claude` 2.1.295/2.1.296, adaptador `cli-12` |

Sin Celery, broker ni Docker para el servicio (D003, D004). Detalles de stack de cada proyecto gestionado (Django,
Node…) pertenecen a perfiles, no al núcleo.

## 2. Componentes

```text
Navegador (React, rutas propias sobre History API)
   │ HTTP / SSE, sesión local + Host/Origin + CSRF
Servicio local (FastAPI + supervisor en un único proceso Uvicorn)
   ├── api/          rutas /api/managed, /api/legacy, sesión y guardia
   ├── services/     supervisor, runtime gestionado, TOML local, registro, migración, observación
   ├── core/engine/  motor: contexto, contratos, flujo, fases, documentos, chat, definición, métricas
   ├── storage/      SQLite: autoridad operativa, cola, journal, vistas
   └── adapters/     CLI de agentes, comandos, Git, procesos, legacy, exportaciones
Directorio local de la aplicación: SQLite, artefactos (streams, capturas, copias), backups
```

El núcleo (`core/`) no importa FastAPI, React, SDKs de proveedores ni reglas de stack. API y CLI llaman a los mismos
casos de uso. El supervisor es el único que lanza procesos y consume la cola; cerrar el navegador no cancela trabajo.

## 3. Módulos (`src/harness_local`)

| Módulo | Responsabilidad |
|---|---|
| `core/legacy.py`, `core/migration.py`, `core/simulation.py`, `core/evidence.py` | Lectura legacy, plan de migración a gestionado, esqueleto H0.3, evidencia |
| `core/project_import.py`, `adapters/project_import.py` | Flujo A: inventario de solo lectura desde el árbol de HEAD (D096) |
| `core/project_onboarding.py`, `adapters/project_onboarding.py` | Flujo B: inventario estático de HEAD (stack, entidades, rutas, tests y CI) y propuesta local-config-4 pendiente de confirmación (D101) |
| `core/project_normalization.py` | Flujo A: mapa de normalización determinista sobre el inventario (D097) |
| `core/engine/import_commit.py`, `storage/project_import.py` | Flujo A: árbol confirmado, conservación de originales, intención de commit y adopción de la fase (D100) |
| `storage/onboarding.py`, `storage/onboarding_commit.py`, `core/engine/onboarding_commit.py` | Flujo B: ingeniería inversa, borradores privados y commit documental confirmado con perfil y P001 adoptados (D102, D103) |
| `core/engine/import_conversation.py`, `storage/import_drafts.py` | Flujo A: conversación `project_import` del revisor, área privada de borradores y bloqueos de la vista previa (D098) |
| `core/engine/context.py` | `ProjectContext`, perfil, política, comandos; contexto explícito por proyecto |
| `core/engine/contracts.py`, `planning.py` | Contrato de tarea, rutas protegidas, planificación determinista desde NEXT_STEPS |
| `core/engine/workflow.py`, `validation.py`, `review.py`, `acceptance.py`, `junit.py` | Bucle plan → ejecución → validación → revisión → aceptación |
| `core/engine/commit.py`, `evidence.py`, `serialization.py` | Intención de commit, actualizaciones mecánicas, codec de historial (formatos 1–7) |
| `core/engine/phases.py`, `storage/closure.py`, `storage/phase_plan.py` | Check READY, cierre y archivo unificados, tags, abandono y plan posterior confirmado (D091) |
| `core/engine/documents.py`, `document_ops.py`, `document_export.py` | Contrato documental unificado (D088), plantilla, bloques gestionados, archivo, edición, exportación y conciliación de transiciones antiguas |
| `core/engine/definition.py`, `bootstrap.py`, `bootstrap_discovery.py` | Definición conversacional (v2) y ejecución del bootstrap D037; el descubrimiento v1 solo concilia runs registrados |
| `core/engine/chat.py`, `chat_commands.py` | Turnos de chat y gramática de comandos |
| `core/engine/prompts.py`, `templates/*.md` | Catálogo de prompts versionados y variables |
| `core/engine/permissions.py`, `metrics.py` | Permisos por categoría y capa; catálogo de métricas `metrics-1` |
| `adapters/cli_agents.py`, `cli_diagnostics.py`, `streams.py`, `processes.py`, `process_gate.py` | Lanzamiento de CLI, preflight, captura incremental, grupos de procesos |
| `adapters/commands.py`, `git.py`, `bootstrap.py`, `chat_snapshot.py`, `migration.py`, `legacy.py` | Validaciones nativas (`commands-1`), Git, commit raíz, instantánea de HEAD, migración, lector legacy |
| `storage/*.py` | Repositorios SQLAlchemy por área (`managed`, `phases`, `documents`, `transition`, `planning`, `chat`, `metrics`, `registry`, `backup`, `retention`, `migrate`…) |
| `services/managed.py`, `managed_runtime.py` | Supervisor (`run_once`, lease, cuarentena) y composición del runtime |
| `services/local_config.py`, `project_registry.py` | TOML `local-config-4` (lectura de 1–3) y registro de proyectos desde la UI con 3/4 |
| `api/app.py`, `managed.py`, `legacy.py`, `schemas.py`, `session.py`, `security.py` | Aplicación, rutas, contratos Pydantic, sesión y guardia |
| `profiles/typescript_web.py`, `profiles/reference_project.py` | Perfiles integrados (`typescript-web` componible; `reference_project` solo biblioteca); los perfiles del TOML v4 se componen en `services/local_config.py` |
| `cli.py`, `launcher.py` | `harness-local` (legacy, backup, retención, diagnóstico, `check-config`, `metrics-backfill`, `init-db`, `serve`) |
| `migrations/versions/0001…0020` | Esquema Alembic |

`frontend/src`: `router.ts`, `pages/` (Home, Registry, Project, Phases, Task, Run, Docs, Planning, Stats, Settings),
`markdown.ts` y `mermaid-view.ts` (render aislado), `managed-api.ts` (envíos idempotentes), `api.generated.ts`
(generado, no se edita). `scripts/`: `dev`, `export_openapi.py`, `build_distribution.py`, `check_distribution.py`,
`smoke_cli.py`. `examples/`: demos sintéticas y plantilla `local_config.example.toml`.

## 4. Patrones

- **Contexto explícito y congelado.** Cada run congela contexto, perfil, política, contrato, catálogo de prompts y
  versiones (adaptadores, composición, motor) por hash. Una versión distinta al ejecutar pone el job en cuarentena
  antes de efectos; nunca se reescribe un historial congelado.
- **Jobs persistidos.** Cola SQLite con `Idempotency-Key`, `expected_version`, lease y heartbeat; exclusión por raíz
  canónica (`checkout_locks`). Carril escritor y carril de chat separados (D083).
- **Intención antes del efecto.** `CommitIntent` sella árbol, mensaje, identidad, fecha e id del commit antes de
  escribir; tras una caída se concilia el mismo commit. Igual para tags, bootstrap, exportación, edición y transición.
- **CAS documental.** Toda escritura del harness admite solo el hash anterior o los bytes sellados.
- **Evidencia por contenido.** Captura Git por árboles (worktree e índice) y fingerprint; validaciones y revisión se
  ligan a ese contenido.
- **Bloques gestionados.** Proyecciones deterministas de SQLite entre marcadores; se regeneran y comparan, nunca se
  leen como fuente.
- **Procedencia.** Cada dato distingue solicitado, reportado, derivado, medido o ausente.
- **Recuperación conservadora.** `RECOVERY_REQUIRED` hasta que el usuario confirma el escritor detenido.

## 5. Persistencia

SQLite es la autoridad operativa (runs, intentos, jobs, fases, permisos, conversaciones, métricas, registro). Git
conserva código y documentos. Markdown conserva la intención (requisitos, arquitectura, fases, decisiones). Esquema y
relaciones en [DDBB-DIAGRAM](DDBB-DIAGRAM.md). Los streams y capturas viven fuera de SQLite, escritos con fsync y
hash; la retención H5.3 los purga solo con autorización y conserva métricas y veredictos. El backup H5.2 copia SQLite
por su API y los artefactos referenciados; la restauración es de consulta (`query_only`).

## 6. Agentes y configuración

- **Adaptador `cli-12`** (D090: propuestas de ADR en las formas de ejecutor y revisor; D094: Codex con
  `project_doc_max_bytes=0`; D102: rol `definition` sobre exportaciones de solo lectura). Sesión nueva por intento;
  argv, entorno (sin herencia, `USER` comprobado contra el UID) y timeouts explícitos. Revisor en solo lectura (Codex `--sandbox read-only`; Claude `--restricted` y `--json-schema`
  tipado). Ejecutor Codex `workspace-write` con el checkout como única raíz escribible y confianza `untrusted` inline
  (D059, D068); Claude con herramientas declaradas y `dontAsk`. Memoria automática desactivada en ambos (D066).
  Ninguna CLI carga por sí misma las instrucciones del checkout: Claude se lanza con `--setting-sources ""` y Codex
  con presupuesto de project docs 0 (D094). El motor inyecta `AGENTS.md` en el prompt de los roles sobre proyectos
  existentes; el rol `definition` (definición, importación e incorporación) lo redacta o lo analiza como evidencia.
- **TOML local del operador** (`local-config-4`; 1–3 se siguen leyendo), fuera de todo checkout y `chmod 600`:
  `[service]`, `[git]`, `[agents.reviewer]`, `[agents.executor]`, `[registration]` (raíces y techo de bootstrap),
  `[profiles.*]` opcionales, `[compositions.*]` (perfil integrado o declarado y comandos autorizados) y
  `[[projects]]` opcional con su política. Sin secretos.
- **Perfiles**: integrados en `profiles/` (`typescript-web` componible; `reference_project` solo biblioteca) o declarados en
  `[profiles.<nombre>]` (D095): preparación y validaciones como argv sin shell, JUnit junto a su validación,
  prefijos, rutas protegidas y sensibles, `data_model_paths` e instrucciones del ejecutor. En `local-config-4` el
  contenido del perfil entra en el hash congelado de la composición. Ejemplo `python-django` en
  `examples/local_config.example.toml`.
- **Validaciones nativas** (`commands-1`): ejecutables absolutos, autorización por comando completo, captura acotada en
  SQLite, grupos POSIX.
- **Prompts** (`templates/`): `plan-task`, `execute-task`, `revise-task`, `review-task`, `executor-routing`,
  `close-phase`, `reconcile-phase`, `chat-turn`, `define-project`, `plan-phase`, `import-project` (D098), `onboard-project` (D102; rol de
  solo lectura `definition`, sin `AGENTS.md` inyectado porque es parte del origen), `bootstrap-project`. Jerarquía base →
  perfil → proyecto; snapshot por intento. Prompts unificados y definición versión 4 (D092). `AGENTS.md` (≤32 KiB)
  entra por `{{PROJECT_INSTRUCTIONS}}` en todos los roles salvo la definición, con ruta, hash y tamaño en el snapshot;
  sin él, el intento se detiene antes de invocar (D094). `document_layout = "d088-12"` (T020, D112) congela las reglas nuevas y
  detiene jobs anteriores antes de efectos. D099 excluye de Git solo el marcador local validado por la guardia
  de esta instalación; la importación confirma originales archivados y un commit conciliable (D100). Las transiciones ya selladas conservan su
  conciliación con los bytes originales. La definición congela los valores por defecto; la planificación incluye
  instrucciones y DDBB-DIAGRAM entre sus documentos de contexto.
- **Frontera Git A/B** (D105, D108, D110, D112): `adapters/project_import.py` rechaza filtros `clean`/`process`, incluidos includes,
  antes del primer `status`; `storage/project_import.py` aplica las mismas guardias a ambos flujos antes de capturar,
  sellar y ejecutar/reanudar. Los destinos nuevos ignorados bloquean y todos los blobs documentales se contrastan
  con los SHA-256 confirmados, incluidos archivo y binarios. El sellado final exige el mismo árbol propuesto;
  no se cambia la configuración ni se reescriben intenciones anteriores. `adapters/local_git.py` comparte
  `LocalGit`: exige `--no-lazy-fetch` desde el primer comando de lectura A/B; un Git sin ese flag falla.
  Los tamaños `BAD`/ausentes y las respuestas de blobs ausentes o incompletas bloquean con diagnóstico;
  no se recuperan objetos ni se devuelve un inventario parcial. Se aplica también a conversación/vista previa
  A y a los lectores de instantáneas compartidos con B. T019 rechaza gitlinks en todo HEAD o índice antes de
  `status` en A y de captura/sellado/escritura o recuperación en A/B: `ls-tree` y `ls-files --stage` solo leen
  el padre, sin inspeccionar ni ejecutar filtros de hijos. No se ignora su suciedad ni se amplía soporte de submódulos.
  T020 vincula el escritor `GitWorkspace` al mismo `LocalGit` antes de capturar/sellar o ejecutar/reanudar:
  todas sus llamadas `run`/`code`, incluida la conciliación y el índice, exigen `--no-lazy-fetch`. `code`
  comprueba primero el soporte con `run(--version)` para no confundir Git antiguo con un commit futuro ausente.
  La ausencia de ese commit permite crearlo localmente; los árboles completos de HEAD y de la intención se
  comprueban con `ls-tree` y `cat-file --batch-check`, también fuera del ámbito documental, antes de escribir.
  Un objeto necesario ausente bloquea sin transporte ni cambios de configuración.
- **Inventario del Flujo B** (D101): AST de Python, JSON/TOML de manifiestos y un subconjunto léxico de JS/TS/Prisma,
  solo biblioteca estándar. Lee blobs de un árbol Git sellado, sin `status`, filtros ni código del proyecto; excluye
  dependencias instaladas y builds incluso si están versionados. Cada entidad/ruta cita fuente y línea; las rutas
  son declaraciones locales, sin expandir montajes o imports. Propone comandos con argv/cwd y evidencia en la forma
  de `[profiles.*]` de T008; no escribe el TOML ni autoriza ejecución. T014 congela inventario y HEAD en la
  conversación `onboarding`, con borradores CAS privados, exportación de D083 y evidencia antes/después. Mantiene
  el lock y carril de planificación; no consulta el checkout vivo durante la invocación. `cli-12` permite al rol
  `definition` omitir la comprobación Git solo en exportaciones; el sandbox sigue siendo de lectura. Sin diagrama
  ni comandos de plantilla por defecto. T015 añade UI, vista previa de documentos/perfil de la composición y
  confirmación por ambos hashes, motivo y clave. Reutiliza la intención y adopción atómica del Flujo A (0020),
  conserva inventario/resumen/originales en `phase-000` y adopta P001. No escribe el TOML ni ejecuta comandos;
  rechaza filtros Git ejecutables y transformaciones de bytes. Detalle en el [flujo](flows/project-onboarding.md).

## 7. API, UI y seguridad

- `/api/managed`: proyectos, registro, runs, jobs, intentos, diffs paginados, permisos, fases, documentos, chat,
  planificación, métricas. Desde T006 no hay endpoints de creación v1 ni transición; el GET de estado de creación
  acompaña a la definición conversacional y el plan confirmado usa la fase ACTIVE sin tareas. Las conversaciones
  `onboarding` (D102) y `project_import` usan las rutas de planificación; solo para importación,
  `GET …/planning/{c}/import` da sus bloqueos (D098).
  `GET …/projects/{p}/import` ofrece primero la activación D027 si hace falta;
  `POST …/planning/{c}/import/preview` y `…/import/confirm` aplican el árbol por hash (D100). Para el Flujo B, `GET …/projects/{p}/onboarding` y
  `POST …/planning/{c}/onboarding/preview` / `…/onboarding/confirm` confirman también `profile_sha256` (D103).
  `/api/legacy`:
  observación de solo lectura. Mutaciones con `Idempotency-Key` y versión esperada; 409 con `{code, diagnostic}`; 422 ante contrato inválido.
- Rutas de la UI: `/`, `/stats`, `/projects/new`, `/projects/:p` con `setup`, `import[/:c/*borrador]`, `onboarding[/:c/*borrador]`, `chat[/:c]`, `docs[/*ruta]`, `phases`,
  `phases/:code`, `phases/:code/plan[/:c]`, `phases/:code/tasks/:task[/runs/:run]`, `stats` y `settings`; `/runs/:id`
  como enlace corto; `/legacy` para la observación.
- Seguridad: solo loopback; clave de sesión efímera en un archivo privado, cookie HttpOnly de ocho horas; Host y Origin
  exactos; cabecera CSRF `X-Harness-Local: 1` en mutaciones; `Sec-Fetch-Site: cross-site` rechazado (D079). Markdown
  sin HTML, Mermaid dibujado como imagen, imágenes del checkout con CSP `sandbox`.

## 8. Convenciones

- Documentación en español con nombres de archivo canónicos en inglés; parsers con alias en ambos idiomas.
- Versiones exactas; ninguna dependencia nueva sin decisión registrada. No documentar scripts inexistentes.
- Tipos del cliente siempre regenerados desde OpenAPI tras cambiar un contrato; nunca a mano.
- Pruebas offline con Git/SQLite temporales, procesos y agentes falsos y datos sintéticos; nunca runs ni datos privados.
- Paridad: un cambio de modelos o migraciones actualiza `DDBB-DIAGRAM.md`; un cambio de flujo, `docs/flows/`. En los
  proyectos gestionados, `data_model_paths` del perfil bloquea la aceptación sin el diagrama y el revisor exige los
  flujos (D090).

## 9. Desarrollo y operación

Instalar (la primera vez necesita red), desde la raíz:

```sh
UV_CACHE_DIR=.local/uv-cache uv sync --frozen --no-python-downloads
npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache
```

Desarrollo con un comando (`scripts/dev`, D053): comprueba versiones, sincroniza dependencias, migra la SQLite
`.local/harness.sqlite3` con backup previo y arranca API (:8013) y Vite (:5173). Admite `--database` y `--config`.

Checks offline:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic check
node --test frontend/tests/*.test.mjs
npm --prefix frontend run check
npm --prefix frontend run build
```

Tras cambiar un contrato de la API:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/export_openapi.py
npm --prefix frontend run generate:types
```

Uso real (D051): construir y verificar el wheel (`scripts/build_distribution.py --out-dir`, `scripts/check_distribution.py
--dist`), instalarlo en un venv propio y operar con `harness-local check-config RUTA [--preflight]`,
`harness-local init-db --database RUTA` y `harness-local serve --database RUTA --config RUTA`. Nunca desde este checkout.

## 10. Límites conocidos

- Ningún recorrido de producto completo con CLI reales; D071 comprobó las cuatro combinaciones revisor/ejecutor con una
  tarea sintética. Los consentimientos de proveedor están agotados.
- Contención cooperativa (POSIX, rutas, sandbox de cada CLI); sin aislamiento del sistema operativo (D064, D065).
- Las validaciones no guardan su hora; la lectura de un run decodifica su historial completo.
- Un proyecto `typescript-web` nuevo no tiene `package.json` y el ejecutor no puede crearlo.
- Dos avisos *low* de KaTeX en Mermaid 11.
- La estructura de D088 es obligatoria desde P008-T002; rutas y paridad en T003, cierre y archivo unificados en
  T004, prompts/definición en T005, API/UI en T006 e inyección de AGENTS en T007 (D089–D094).

## 11. Ampliación planificada — P009

Diseño pendiente de implementación ([D115](DECISIONS.md#d115--p009-django-desde-cero-carpeta-de-proyectos-y-agentes-por-proyecto)).
Hoy el registro exige carpeta existente bajo `[registration].roots`, y los proveedores se fijan en los agentes
globales del TOML; Settings los muestra en solo lectura. P009 ampliará ambos contratos de forma explícita:

- Selección de carpeta padre desde UI, guardada como autoridad operativa local auditada; creación idempotente
  de nuevos hijos con intención previa. No se edita el TOML ni la configuración global; convivencia con sus
  raíces, revocación, esquema y contratos se concretan en T001. Los agentes solo reciben la raíz del hijo.
- Presets de roles del servicio con selección por proyecto; el usuario fija modelo/esfuerzo del revisor y este
  decide los del ejecutor. Cambios entre tareas, versiones congeladas e historiales anteriores conservados.
  El navegador no suministra ejecutables, entornos o credenciales.
- Receta técnica Django confirmada tras el commit documental: entorno, scaffold, dependencias fijadas y checks.
  Autoridad separada para crear archivos protegidos, sin relajar el contrato documental ni el ejecutor normal.
  Django será una herramienta del proyecto/piloto, no una dependencia del runtime del harness.

No hay tablas, migraciones, endpoints ni versiones nuevas implementadas en esta planificación. T001 documentará
el diseño y T002–T004 mantendrán la paridad de esquema/API/tipos/diagramas al construirlo. Flujo futuro en
[project-creation](flows/project-creation.md); plan y matriz en [docs/phase](phase/P009_PLAN_DJANGO.md).
