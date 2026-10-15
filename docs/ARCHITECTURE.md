# Arquitectura — Harness Local

Stack, módulos, patrones y convenciones vigentes. Consolida la especificación inicial (§5–7, 9, 10 y 13), las
decisiones D001–D088 y la información técnica que antes estaba en README y AGENTS. Datos:
[DDBB-DIAGRAM](DDBB-DIAGRAM.md). Flujos: [docs/flows](flows/task-run.md).

## 1. Stack

| Capa | Elección y versión exacta |
|---|---|
| Núcleo | Python 3.14.4, biblioteca estándar, paquete `harness-local` 0.1.0 (`uv_build==0.12.19`) |
| API local | FastAPI 0.143.0, Pydantic 2.14.0, Uvicorn 0.54.0; HTTP para acciones, SSE para observación legacy |
| Persistencia | SQLite con SQLAlchemy 2.1.4 y Alembic 1.20.0 (esquema `0018_conversation_keys`) |
| UI | React 19.3.0, TypeScript 5.9.3, Vite 8.3.4; `markdown-it` 15.0.2 (`html: false`) y `mermaid` 11.17.2 (`strict`) |
| Tipos del cliente | `openapi-typescript` 7.13.0 desde el OpenAPI exportado |
| Herramientas | uv 0.12.19 y `uv.lock`; Node 24.15.0, npm 11.12.1 y `frontend/package-lock.json` |
| Pruebas | `unittest` (12 checks sin dependencias), pytest 9.1.1 + httpx 0.28.1, `node --test` |
| Agentes | CLI `codex` 0.161.0/0.162.1 (escritura solo 0.162.1) y `claude` 2.1.295/2.1.296, adaptador `cli-9` |

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
| `core/engine/context.py` | `ProjectContext`, perfil, política, comandos; contexto explícito por proyecto |
| `core/engine/contracts.py`, `planning.py` | Contrato de tarea, rutas protegidas, planificación determinista desde NEXT_STEPS |
| `core/engine/workflow.py`, `validation.py`, `review.py`, `acceptance.py`, `junit.py` | Bucle plan → ejecución → validación → revisión → aceptación |
| `core/engine/commit.py`, `evidence.py`, `serialization.py` | Intención de commit, actualizaciones mecánicas, codec de historial (formatos 1–7) |
| `core/engine/phases.py` | Definición de fase, check READY, cierre, tags, enmiendas |
| `core/engine/documents.py`, `document_ops.py`, `document_export.py` | Contrato documental v2, bloques gestionados, transición, edición y exportación |
| `core/engine/definition.py`, `bootstrap.py`, `bootstrap_discovery.py` | Definición conversacional (v2) y bootstrap D037 (v1) |
| `core/engine/chat.py`, `chat_commands.py` | Turnos de chat y gramática de comandos |
| `core/engine/prompts.py`, `templates/*.md` | Catálogo de prompts versionados y variables |
| `core/engine/permissions.py`, `metrics.py` | Permisos por categoría y capa; catálogo de métricas `metrics-1` |
| `adapters/cli_agents.py`, `cli_diagnostics.py`, `streams.py`, `processes.py`, `process_gate.py` | Lanzamiento de CLI, preflight, captura incremental, grupos de procesos |
| `adapters/commands.py`, `git.py`, `bootstrap.py`, `chat_snapshot.py`, `migration.py`, `legacy.py` | Validaciones nativas (`commands-1`), Git, commit raíz, instantánea de HEAD, migración, lector legacy |
| `storage/*.py` | Repositorios SQLAlchemy por área (`managed`, `phases`, `documents`, `transition`, `planning`, `chat`, `metrics`, `registry`, `backup`, `retention`, `migrate`…) |
| `services/managed.py`, `managed_runtime.py` | Supervisor (`run_once`, lease, cuarentena) y composición del runtime |
| `services/local_config.py`, `project_registry.py` | TOML `local-config-1/2/3` y registro de proyectos desde la UI |
| `api/app.py`, `managed.py`, `legacy.py`, `schemas.py`, `session.py`, `security.py` | Aplicación, rutas, contratos Pydantic, sesión y guardia |
| `profiles/typescript_web.py`, `profiles/reference_project.py` | Perfiles declarativos (solo `typescript-web` se compone desde el TOML) |
| `cli.py`, `launcher.py` | `harness-local` (legacy, backup, retención, diagnóstico, `check-config`, `metrics-backfill`, `init-db`, `serve`) |
| `migrations/versions/0001…0018` | Esquema Alembic |

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

- **Adaptador `cli-9`.** Sesión nueva por intento; argv, entorno (sin herencia, `USER` comprobado contra el UID) y
  timeouts explícitos. Revisor en solo lectura (Codex `--sandbox read-only`; Claude `--restricted` y `--json-schema`
  tipado). Ejecutor Codex `workspace-write` con el checkout como única raíz escribible y confianza `untrusted` inline
  (D059, D068); Claude con herramientas declaradas y `dontAsk`. Memoria automática desactivada en ambos (D066).
  Claude se lanza con `--setting-sources ""`; si los archivos de instrucciones del checkout llegan al agente se
  verifica en P008-T007.
- **TOML local del operador** (`local-config-3`), fuera de todo checkout y `chmod 600`: `[service]`, `[git]`,
  `[agents.reviewer]`, `[agents.executor]`, `[registration]` (raíces y techo de bootstrap), `[compositions.*]`
  (perfil y comandos autorizados) y `[[projects]]` opcional con su política. Sin secretos.
- **Validaciones nativas** (`commands-1`): ejecutables absolutos, autorización por comando completo, captura acotada en
  SQLite, grupos POSIX.
- **Prompts** (`templates/`): `plan-task`, `execute-task`, `revise-task`, `review-task`, `executor-routing`,
  `close-phase`, `reconcile-phase`, `chat-turn`, `define-project`, `plan-phase`, `bootstrap-project`. Jerarquía base →
  perfil → proyecto; snapshot por intento.

## 7. API, UI y seguridad

- `/api/managed`: proyectos, registro, runs, jobs, intentos, diffs paginados, permisos, fases, documentos, chat,
  planificación, métricas. `/api/legacy`: observación de solo lectura. Mutaciones con `Idempotency-Key` y versión
  esperada; 409 con `{code, diagnostic}`; 422 ante contrato inválido.
- Rutas de la UI: `/`, `/stats`, `/projects/new`, `/projects/:p` con `setup`, `chat[/:c]`, `docs[/*ruta]`, `phases`,
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
- Paridad: un cambio de modelos o migraciones actualiza `DDBB-DIAGRAM.md`; un cambio de flujo, `docs/flows/`.

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
- El contrato documental vigente es v2 opcional; la estructura de D088 está pendiente (P008).
