# Arquitectura — Harness Local

Stack, módulos, patrones y convenciones vigentes. Consolida la especificación inicial (§5–7, 9, 10 y 13), las
decisiones vigentes y la información técnica que antes estaba en README y AGENTS. Datos:
[DDBB-DIAGRAM](DDBB-DIAGRAM.md). Flujos: [docs/flows](flows/task-run.md).

## 1. Stack

| Capa | Elección y versión exacta |
|---|---|
| Núcleo | Python 3.14.4, biblioteca estándar, paquete `harness-local` 0.1.0 (`uv_build==0.12.19`) |
| API local | FastAPI 0.143.0, Pydantic 2.14.0, Uvicorn 0.54.0; HTTP para acciones y observación gestionada por cursor |
| Persistencia | SQLite con SQLAlchemy 2.1.4 y Alembic 1.20.0 (esquema `0025_project_work_languages`) |
| UI | React 19.3.0, TypeScript 5.9.3, Vite 8.3.4; `markdown-it` 15.0.2 (`html: false`) y `mermaid` 11.17.2 (`strict`) |
| Tipos del cliente | `openapi-typescript` 7.13.0 desde el OpenAPI exportado |
| Herramientas | uv 0.12.19 y `uv.lock`; Node 24.15.0, npm 11.12.1 y `frontend/package-lock.json` |
| Pruebas | `unittest` (12 checks sin dependencias), pytest 9.1.1 + httpx 0.28.1 + pytest-xdist 3.8.0, `node --test` |
| Agentes | Detección automática desde Codex 0.163.0 / Claude 2.1.304; posteriores compatibles condicionadas al contrato conocido, adaptador `cli-14` (D174) |

Sin Celery, broker ni Docker para el servicio (D003, D004). Detalles de stack de cada proyecto gestionado (Django,
Node…) pertenecen a perfiles, no al núcleo.

## 2. Componentes

```text
Navegador (React, rutas propias sobre History API)
   │ HTTP, sesión local + Host/Origin + CSRF
Servicio local (FastAPI + supervisor en un único proceso Uvicorn)
   ├── api/          rutas /api/managed, sesión y guardia
   ├── services/     supervisor, runtime gestionado, TOML local, registro y preparación
   ├── core/engine/  motor: contexto, contratos, flujo, fases, documentos, chat, definición, métricas
   ├── storage/      SQLite: autoridad operativa, cola, journal, vistas
   └── adapters/     CLI de agentes, comandos, Git, procesos y exportaciones
Directorio local de la aplicación: SQLite, artefactos (streams, capturas, copias), backups
```

El núcleo (`core/`) no importa FastAPI, React, SDKs de proveedores ni reglas de stack: solo biblioteca estándar,
`harness_local.core` y, como única hoja externa, los catálogos `harness_local.i18n` (solo stdlib; D171). API y CLI
llaman a los mismos casos de uso. El supervisor es el único que lanza procesos y consume la cola; cerrar el navegador no cancela trabajo.

## 3. Módulos (`src/harness_local`)

| Módulo | Responsabilidad |
|---|---|
| `core/project_onboarding.py`, `adapters/project_onboarding.py` | Flujo B: inventario estático de HEAD (stack, entidades, rutas, tests y CI) y propuesta local-config-4 pendiente de confirmación (D101) |
| `core/engine/import_commit.py`, `storage/project_import.py` | Infraestructura de B: adopción documental, intención de commit y recuperación; propósito/tabla históricos conservados (D161) |
| `adapters/import_git.py`, `core/tree.py`, `storage/private_drafts.py` | Objetos Git locales, guardias de escritor, entradas de árbol y borradores CAS compartidos por B y preparación |
| `core/managed_mode.py`, `adapters/managed_mode.py`, `storage/managed_mode.py`, `storage/retired_work.py` | Compatibilidad de solo lectura de activaciones previas y cuarentena de trabajos retirados/ambiguos (D161) |
| `storage/onboarding.py`, `storage/onboarding_commit.py`, `core/engine/onboarding_commit.py` | Flujo B: ingeniería inversa, borradores privados y commit documental confirmado con perfil y P001 adoptados (D102, D103) |
| `core/engine/context.py` | `ProjectContext`, perfil, política, comandos; contexto explícito por proyecto |
| `core/engine/contracts.py`, `planning.py` | Contrato de tarea, rutas protegidas, planificación determinista desde NEXT_STEPS |
| `core/engine/workflow.py`, `validation.py`, `review.py`, `acceptance.py`, `junit.py` | Bucle plan → ejecución → validación → revisión → aceptación |
| `core/engine/commit.py`, `evidence.py`, `serialization.py` | Intención de commit, actualizaciones mecánicas, codec de historial (escribe el formato 8; lee 1–8) |
| `core/engine/phases.py`, `storage/closure.py`, `storage/phase_plan.py` | Check READY, cierre y archivo unificados, tags, abandono y plan posterior confirmado (D091) |
| `core/engine/documents.py`, `document_ops.py`, `document_export.py` | Contrato documental unificado (D088), plantilla, bloques gestionados, archivo, edición, exportación y conciliación de transiciones antiguas |
| `core/engine/definition.py`, `bootstrap.py`, `bootstrap_discovery.py` | Definición conversacional (v2) y ejecución del bootstrap D037; el descubrimiento v1 solo concilia runs registrados |
| `core/engine/chat.py`, `chat_commands.py` | Turnos de chat y gramática de comandos |
| `core/engine/prompts.py`, `templates/*.md`, `language.py` | Catálogo de prompts versionados y variables; directiva de idioma sellada fuera de las plantillas (D169) |
| `core/engine/permissions.py`, `metrics.py` | Permisos por categoría y capa; catálogo de métricas `metrics-1` |
| `adapters/cli_agents.py`, `cli_compatibility.py`, `cli_diagnostics.py`, `streams.py`, `processes.py`, `process_gate.py` | Política de capacidades, detección/identidad local, preflight por intento, captura incremental y grupos de procesos (D174) |
| `adapters/commands.py`, `git.py`, `bootstrap.py`, `chat_snapshot.py` | Validaciones nativas (`commands-1`), Git, commit raíz, instantánea de HEAD |
| `storage/*.py` | Repositorios SQLAlchemy por área (`managed`, `phases`, `documents`, `transition`, `planning`, `chat`, `metrics`, `registry`, `backup`, `retention`, `migrate`…) |
| `storage/run_projection.py`, `managed_views.py` | Proyección derivada `run-projection-1` escrita con el historial y vistas de runs que solo la leen (D144) |
| `services/managed.py`, `managed_runtime.py` | Supervisor (`run_once`, lease, cuarentena) y composición del runtime |
| `services/local_config.py`, `project_registry.py`, `project_creation.py` | TOML `local-config-8` (lectura de 1–7), formateador declarativo v8 (D194), CLI automática desde v7 (D174); registro/creación 3–8, presets desde v5, recetas v1 en v5 y v2 desde v6 (D168); trabajo sellado al alta (D167) |
| `recipes/`, `services/project_preparation.py`, `storage/preparation.py`, `adapters/preparation.py` | Recetas empaquetadas `django-recipe-1` y `typescript-web-recipe-1` y su preparación confirmada y recuperable (D119, D143); sucesoras v2 por idioma de trabajo en `local-config-6/7/8`, con despacho por `id` (D163, D168) |
| `api/app.py`, `managed.py`, `schemas.py`, `session.py`, `security.py` | Aplicación, rutas, contratos Pydantic, sesión y guardia |
| `profiles/typescript_web.py` | Perfil integrado `typescript-web` componible (el perfil privado solo biblioteca se retiró en P011-T015); los perfiles del TOML v4/v5 se componen en `services/local_config.py` |
| `cli.py`, `launcher.py` | `harness-local` (backup, retención, diagnóstico, `check-config`, `metrics-backfill`, `init-db`, `serve`); `--ui-language` por invocación |
| `storage/preferences.py`, `i18n/` | Preferencias globales de idioma con CAS, captura del visual al admitir cada job y catálogos en/es de mensajes propios (D166); `tr()` emite en el visual de cada emisión: petición HTTP, job o invocación CLI (D171) |
| `storage/work_language.py`, `services/work_language.py` | Idioma de trabajo inmutable por raíz, par `language-context-1` por job/intento y confirmación explícita ausente → valor (D167) |
| `migrations/versions/0001…0025` | Esquema Alembic |

`frontend/src`: `router.ts`, `pages/` (Home, Registry, Project, Phases, Task, Run, Docs, Planning, Stats, Settings,
Preferences), `i18n.ts`, `i18n/{en,es}.json` y `Language.tsx` (catálogos y proveedor del idioma visual, D166),
`markdown.ts` y `mermaid-view.ts` (render aislado), `managed-api.ts` (envíos idempotentes), `api.generated.ts`
(generado, no se edita). `scripts/`: `dev`, `export_openapi.py`, `build_distribution.py`, `check_distribution.py`,
`smoke_cli.py`. `examples/`: plantilla `local_config.example.toml` (v8, formateador optativo y CLI automática; formatos 1–7 legibles),
fragmentos de recetas v2, demos sintéticas y guiones históricos (`first_use/`, `provider_matrix/`) sin actualizar.

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

- **Adaptador `cli-14`** (D174: mínimos/capacidades y preflight por intento; conserva D090: propuestas de ADR en
  las formas de ejecutor y revisor; D094: Codex con
  `project_doc_max_bytes=0`; D102: rol `definition` sobre exportaciones de solo lectura; D124: Codex omite su
  comprobación Git también al definir una carpeta nueva, plantilla congelada `define-project`). Sesión nueva por intento;
  argv, entorno (sin herencia, `USER` comprobado contra el UID) y timeouts explícitos. Revisor en solo lectura (Codex `--sandbox read-only`; Claude `--restricted` y `--json-schema`
  tipado). Ejecutor Codex `workspace-write` con el checkout como única raíz escribible y confianza `untrusted` inline
  (D059, D068); Claude con herramientas declaradas y `dontAsk`. Memoria automática desactivada en ambos (D066).
  Ninguna CLI carga por sí misma las instrucciones del checkout: Claude se lanza con `--setting-sources ""` y Codex
  con presupuesto de project docs 0 (D094). El motor inyecta `AGENTS.md` en el prompt de los roles sobre proyectos
  existentes; el rol `definition` (definición e incorporación) lo redacta o lo analiza como evidencia.
  Mínimos comunes Codex 0.163.0 / Claude 2.1.304. Las versiones posteriores se admiten por el contrato conocido
  sin allowlist por patch; por HITL, su compatibilidad es condicionada y no se declaran efectos internos observados.
  Versión, huella de lanzamiento y política se congelan por job; observación fresca y validación del argv por intento,
  más comprobación de identidad antes de GO. Deriva → rechazo/cuarentena, sin retry ni sustitución de proveedor.
  [Flujo](flows/cli-compatibility.md), [entrega y límites](archive/phase-011/P011-T012_COMPATIBILIDAD_CLI.md).
- **TOML local del operador** (`local-config-8`; 1–7 se siguen leyendo), fuera de todo checkout y `chmod 600`:
  `[service]`, `[git]`, `[agents.reviewer]`, `[agents.executor]`, `[registration]` (raíces y techo de bootstrap),
  `[profiles.*]` opcionales, `[compositions.*]` (perfil integrado o declarado y comandos autorizados) y
  `[[projects]]` opcional con su política. V5 añade `[agent_presets.*]` y `agent_selection` opcional por
  proyecto: ids de presets, modelo/esfuerzo del revisor; catálogo/modo del ejecutor en `policy`. Sin secretos.
  El catálogo público omite ejecutables/entornos; `ports` conserva ambos agentes por checkout. El preflight
  explícito cubre la pareja heredada y cada rol de los presets; cargar no invoca CLI. V1–v4 conservan sus hashes.
  V6 (D167) es v5 con `work_language` opcional en `[[projects]]`, que el servicio asocia una vez al arrancar
  (otro valor ya confirmado detiene el arranque); sus `[recipes]` eligen las recetas v2 (D168).
  V7 conserva v6 y permite omitir `executable`/`cli_version` en agentes/presets: resuelve los proveedores elegidos
  por su PATH explícito, o la ruta opcional, sin heredar entorno. Parsear sigue sin procesos; arranque/admisión
  observan versión/help antes de congelar la versión real. Cada mutación observa de nuevo y reutiliza solo su
  resolución dentro de esa petición; lecturas pasivas. Formatos anteriores conservan sus hashes/aserciones, pero
  no saltan los mínimos. Configuraciones incompletas no se pueden encolar como si `auto` fuera una versión.
  Cambios confirmados serializan registro y admisión en SQLite; bloquean aceptación/commit, propuestas de chat
  y definición/incorporación utilizable. Planes no aceptados pasan a SUPERSEDED sin alterar sus snapshots;
  nueva planificación antes de confirmar otro plan. [Flujo de agentes](flows/project-agents.md) (D118).
- **Perfiles**: integrado en `profiles/` (`typescript-web` componible) o declarados en
  `[profiles.<nombre>]` (D095): preparación y validaciones como argv sin shell, JUnit junto a su validación,
  prefijos, rutas protegidas y sensibles, `data_model_paths` e instrucciones del ejecutor. En `local-config-4` el
  contenido del perfil entra en el hash congelado de la composición. Ejemplo `python-django` en
  `examples/local_config.example.toml`.
- **Validaciones nativas** (`commands-1`): ejecutables absolutos, autorización por comando completo, captura acotada en
  SQLite, grupos POSIX. Un comando de la tarea con el argv de una validación del perfil en la raíz y sin entorno
  propio es esa validación (su timeout) y se ejecuta una vez (P011-T016). El formateador del perfil se autoriza aparte (`formatter-paths`): su argv seguido solo de
  archivos existentes del checkout. El motor lo ejecuta tras cada turno del ejecutor (D133).
- **Formateador declarativo** (P012-T010, D194): `local-config-8` admite el par opcional no vacío
  `formatter_argv`/`formatter_paths` en perfiles declarados, con ejecutable mapeado y autorización del perfil.
  Motor/runner D133 y `formatting_json` existentes, sin formatear al revalidar. CLI, idiomas y recetas v2 de v7
  conservados; v1–v7 mantienen su contrato/huellas. `check-config` muestra argv/patrones solo al declararlos.
  [Entrega offline](phase/P012-T010_FORMATEADOR_DECLARATIVO.md), sin nueva acreditación real.
- **Prompts** (`templates/`): `plan-task`, `execute-task`, `revise-task`, `review-task`, `executor-routing`,
  `close-phase`, `reconcile-phase`, `chat-turn`, `define-project`, `plan-phase`, `onboard-project` (D102; rol de
  solo lectura `definition`, sin `AGENTS.md` inyectado porque es parte del origen), `bootstrap-project`. Jerarquía base →
  perfil → proyecto; snapshot por intento. Prompts unificados y definición versión 4 (D092). `AGENTS.md` (≤32 KiB)
  entra por `{{PROJECT_INSTRUCTIONS}}` en todos los roles salvo la definición, con ruta, hash y tamaño en el snapshot;
  sin él, el intento se detiene antes de invocar (D094). Con el par `language-context-1` del job, `render_attempt`
  añade antes del esquema la directiva `language-directive-1` (visual/trabajo y mapa V/W/T por rol) y la sella en el
  snapshot; jobs sin par se renderizan como antes (D169). `document_layout = "d088-12"` (T020, D112) congela las reglas nuevas y
  detiene jobs anteriores antes de efectos. D099 excluye de Git solo el marcador local validado por la guardia
  de esta instalación; B confirma originales archivados y un commit conciliable. El catálogo retirado de A se lee
  como dato histórico, pero no se edita, activa ni renderiza para invocarlo (D161). Las transiciones ya selladas conservan su
  conciliación con los bytes originales. La definición congela los valores por defecto; la planificación incluye
  instrucciones y DDBB-DIAGRAM entre sus documentos de contexto.
- **Frontera Git de incorporación y preparación** (D105/D108/D110/D112, extracción D161):
  `adapters/import_git.py` conserva blobs por hash, rechazo de filtros clean/process (incluidos includes), gitlinks
  de HEAD/índice y destinos nuevos ignorados. `storage/project_import.py` conserva la intención de B y repite las
  guardias antes de capturar/sellar, ejecutar o conciliar. `adapters/local_git.py` exige objetos completos locales
  y `--no-lazy-fetch` en todas las operaciones run/code del escritor y del lector; sin fallback ni transporte.
  El sellado final exige el árbol mostrado; las conversiones de atributos no pueden cambiar bytes confirmados.
- **Inventario del Flujo B** (D101): AST de Python, JSON/TOML de manifiestos y un subconjunto léxico de JS/TS/Prisma,
  solo biblioteca estándar. Lee blobs de un árbol Git sellado, sin `status`, filtros ni código del proyecto; excluye
  dependencias instaladas y builds incluso si están versionados. Cada entidad/ruta cita fuente y línea; las rutas
  son declaraciones locales, sin expandir montajes o imports. Propone comandos con argv/cwd y evidencia en la forma
  de `[profiles.*]` de T008; no escribe el TOML ni autoriza ejecución. T014 congela inventario y HEAD en la
  conversación `onboarding`, con borradores CAS privados, exportación de D083 y evidencia antes/después. Mantiene
  el lock y carril de planificación; no consulta el checkout vivo durante la invocación. `cli-12` permite al rol
  `definition` omitir la comprobación Git en exportaciones (`cli-13` añade la definición D088 de una carpeta nueva,
  D124); el sandbox sigue siendo de lectura. Sin diagrama
  ni comandos de plantilla por defecto. T015 añade UI, vista previa de documentos/perfil de la composición y
  confirmación por ambos hashes, motivo y clave. Reutiliza la intención y adopción atómica persistidas en 0020,
  conserva inventario/resumen/originales en `phase-000` y adopta P001. No escribe el TOML ni ejecuta comandos;
  rechaza filtros Git ejecutables y transformaciones de bytes. Detalle en el [flujo](flows/project-onboarding.md).

## 7. API, UI y seguridad

- `/api/managed`: proyectos, registro, runs, jobs, intentos, diffs paginados, permisos, fases, documentos, chat,
  planificación, métricas. Desde T006 no hay endpoints de creación v1 ni transición; el GET de estado de creación
  acompaña a la definición conversacional y el plan confirmado usa la fase ACTIVE sin tareas. Las conversaciones
  `onboarding` usan planificación; `GET …/projects/{p}/onboarding` y
  `POST …/planning/{c}/onboarding/preview` / `…/onboarding/confirm` confirman documentos y `profile_sha256`.
  `GET …/projects/{p}/mode` solo ofrece diagnóstico de admisión gestionada. Mutaciones con `Idempotency-Key`
  y versión esperada; 409 con `{code, diagnostic}`; 422 ante contrato inválido.
- `GET/PUT /api/managed/preferences`: idiomas globales con versión esperada e `Idempotency-Key`; cada job expone
  el `language_context` sellado al admitirlo ([flujo](flows/language-preferences.md), D166).
- Idioma de trabajo (D167, [flujo](flows/project-work-language.md)): `work_language` obligatorio en el registro
  (`/registry/preview|apply`, acción `register`) y en la creación (`/project-creations/*`), rechazado con 409
  `work_language_immutable` en cambios/bajas; `POST …/projects/{p}/work-language/preview` y `…/work-language`
  (hash y motivo) para proyectos sin valor. Sin él, toda admisión nueva responde 409 `work_language_required`.
  Proyectos, registros, jobs e intentos exponen el valor/par congelado.
- Rutas de UI: `/`, `/stats`, `/preferences`, `/projects/new`, `/projects/:p` con `setup`, `onboarding[/:c/*borrador]`,
  `chat[/:c]`, `docs[/*ruta]`, `phases`, `phases/:code`, `phases/:code/plan[/:c]`,
  `phases/:code/tasks/:task[/runs/:run]`, `stats`, `settings`; `/runs/:id` como enlace corto.
  `/legacy` y `/projects/:p/import` muestran ruta no encontrada; API antigua 404 tras sesión/Host/Origin/CSRF,
  comandos antiguos error de argumentos sin SQLite. No hay observador/SSE ni activación/reversión ejecutables.
  La compatibilidad de datos y trabajos anteriores se detalla en [su flujo](flows/legacy-migration.md) (D161).
- Seguridad: solo loopback; clave de sesión efímera en un archivo privado, cookie HttpOnly de ocho horas; Host y Origin
  exactos; cabecera CSRF `X-Harness-Local: 1` en mutaciones; `Sec-Fetch-Site: cross-site` rechazado (D079). Markdown
  sin HTML, Mermaid dibujado como imagen, imágenes del checkout con CSP `sandbox`.

## 8. Convenciones

- Documentación en español con nombres de archivo canónicos en inglés; parsers con alias en ambos idiomas.
  Los documentos que genera el harness en un proyecto (bloques, plantilla D088, archivo y registros) siguen su
  idioma de trabajo (`core/engine/document_text.py`, D169); un contexto sin él conserva los bytes españoles.
- Comentarios, docstrings y descripciones OpenAPI de `src/harness_local` en inglés (P011-T003/T004); las fuentes v1
  de recetas conservan sus bytes (D163). Mensajes visibles nuevos por clave en los catálogos JSON en/es (D166): un
  mensaje completo por clave, parámetros `{nombre}` como texto, fallback inglés. Desde T021 (D171) todo texto propio
  del servicio/CLI que estaba en español sale de `i18n.tr()` en el visual de la emisión, y desde T022 (D172) también
  los diagnósticos visibles antes ingleses; solo quedan en inglés técnico las invariantes internas y lo que entra en
  la entrada de un agente, listados en `tests/fixtures/service_texts/english.json`. El cliente distingue rechazos
  por `code`, nunca por el texto del diagnóstico.
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

pytest se ejecuta en paralelo por defecto (`-n auto`, D125); añadir `-n 0` para ejecutarla en serie, por ejemplo
al depurar una prueba concreta.

Tras cambiar un contrato de la API:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/export_openapi.py
npm --prefix frontend run generate:types
```

Uso real (D051): construir y verificar el wheel (`scripts/build_distribution.py --out-dir`, carpeta nueva o vacía, con
LICENSE/NOTICE, `pylock.toml` instalable offline y `SHA256SUMS`; `scripts/check_distribution.py --dist`, que además
comprueba miembros exactos, metadatos, versión única y ausencia de componentes retirados; P011-T015), instalarlo en un venv propio y operar con `harness-local check-config RUTA [--preflight]`,
`harness-local init-db --database RUTA` y `harness-local serve --database RUTA --config RUTA`. Nunca desde este checkout.
La plantilla del TOML es `local-config-8`: formateador optativo en perfiles declarados, sin pin obligatorio de CLI,
con presets, `work_language` por proyecto
y fragmentos de receta v2 de `examples/` (una composición ya existente se añade con otro nombre). El PATH explícito
de cada rol debe incluir el cliente, o se declara su ruta opcional. Mínimos y compatibilidad en el
[README](../README.md#requirements), contrastados con `cli_compatibility.MINIMUM` y la política incluida. Las listas
`cli_agents.SUPPORTED`/`WRITE_SUPPORTED` conservan evidencia histórica y ya no son allowlists de admisión.

Actualización (D150): detener el servicio y los escritores, instalar el nuevo wheel y ejecutar
`harness-local migrate --database /ruta/state/harness.sqlite3 --snapshots /ruta/copias-previas --writers-stopped`.
Reutiliza `storage/migrate.py`: revisión conocida, instantánea SQLite verificada (`premigration-1`, integridad,
revisión, SHA-256 y fsync) y después `upgrade head`, con comprobación del esquema final. Solo bases existentes;
una base al día no cambia ni genera copia. Rutas absolutas sin enlaces (también auxiliares y componentes), copias
fuera de checkouts Git y de las raíces persistidas. Rechaza revisiones desconocidas, bases sin Alembic,
restauraciones de consulta y propietarios/grupos vivos de jobs, preparaciones, CLI y validaciones. La declaración
de parada cubre también servicios inactivos sin propietario persistido: no hay descubrimiento global de procesos.
Un fallo conserva base y copia, sin restaurar automáticamente. Es una instantánea de SQLite, no un bundle de
artefactos H5.2. [Flujo y recuperación](flows/database-migration.md). `scripts/dev` conserva creación/migración de
su base de desarrollo con copia previa. `init-db` y `serve` conservan D043: creación nueva y arranque sin migración.

`serve` escribe la clave de sesión (`harness-session-*/login-key`, 0700/0600, se borra al salir) y los índices y
sellos temporales de Git (`harness-git-*`, `harness-bootstrap-*`) bajo el `TMPDIR` del proceso. Sin él, Python usa el
temporal del sistema (`/var/folders/…` en macOS), fuera del área de operación. Para mantenerlos dentro, lanzar
`serve` con `TMPDIR` apuntando a un directorio 0700 del área, como hace `check_distribution.py` (D126). Los comandos
de las recetas Django y TypeScript web no heredan ese valor: reciben `HOME`/`TMPDIR` propios dentro del hijo (D119, D143).

## 10. Límites conocidos

- P009-T012 acredita un recorrido real Django desde creación UI hasta cuatro tareas con las cuatro parejas,
  QA y cierre/archivo (D139); evidencia limitada a macOS arm64/Python 3.13. T012 agotó sus dos llamadas y no
  autoriza nuevas operaciones con proveedores.
- Contención cooperativa (POSIX, rutas, sandbox de cada CLI); sin aislamiento del sistema operativo (D064, D065).
- Las validaciones no guardan su hora. Las vistas de runs (D144), las métricas y la vista previa de exportación (D145)
  leen la proyección `run-projection-1`; la transición, el commit de tarea y el resto del motor leen el historial.
- El manifiesto que fija una receta (Django o TypeScript web) no admite dependencias nuevas tras preparar; requiere
  un flujo confirmado futuro. Las altas e importaciones aportan su propio `package.json` (D143).
- El perfil `typescript-web` protege `package.json`, `package-lock.json`, `tsconfig.json`, `scripts/**` y `tests/**`
  frente al ejecutor normal: el ejecutor no crea ni modifica archivos bajo `tests/`.
- Tras un reinicio que renumere el dispositivo, crear otro proyecto exige volver a elegir la carpeta (D130).
- Evidencia real limitada a macOS arm64 y a las CLI y recorridos registrados; incorporación B, perfil declarado,
  receta TypeScript, chat y backup sin uso real ([alcance](../README.md#supported-scope-and-limits)).
- Dos avisos *low* de KaTeX en Mermaid 11.
- La estructura de D088 es obligatoria desde P008-T002; rutas y paridad en T003, cierre y archivo unificados en
  T004, prompts/definición en T005, API/UI en T006 e inyección de AGENTS en T007 (D089–D094).

## 11. Ampliación — P009

Diseño completado en P009-T001; carpeta/creación implementadas en T002 (D117) y roles en T003 (D118); receta implementada en T004 (D119)
([D116](DECISIONS.md#d116--p009-t001-autoridad-de-creación-presets-por-proyecto-y-preparación-separada),
[contrato](archive/phase-009/P009-T001_CONTRATO_CREACION.md)).
El alta existente conserva `[registration].roots`. La autoridad UI de creación permite hijos directos nuevos
fuera de esas raíces, también con `roots = []`, sin elevar `bootstrap_enabled`. Settings permite seleccionar
presets por proyecto registrado con v5; los proyectos TOML conservan edición solo por el operador:

- Selección de carpeta padre desde UI, guardada como autoridad operativa local auditada; creación idempotente
  de nuevos hijos con intención previa. No se edita el TOML ni la configuración global; convivencia con sus
  raíces TOML separadas: estas siguen autorizando solo el alta existente. Retirada bloquea creaciones pendientes,
  no proyectos ya registrados. Intención y alta atómica conservan procedencia; los agentes solo reciben el hijo.
- Presets de roles del servicio con selección por proyecto; el usuario fija modelo/esfuerzo del revisor y este
  decide los del ejecutor. Cambios entre tareas, versiones congeladas e historiales anteriores conservados.
  Implementado en `local-config-5`; v1–v4 conservan lectura/hashes. El navegador no suministra ejecutables, entornos
  o credenciales; la composición efectiva guarda agentes por checkout, también al construir `ports`.
- Receta técnica Django confirmada tras el commit documental: entorno, scaffold, dependencias fijadas y checks.
  Autoridad separada para crear archivos protegidos, sin relajar el contrato documental ni el ejecutor normal.
  Enlaces tipados de ejecutables diferidos permiten definir antes de crear el entorno; tareas/checks se bloquean
  hasta tener recibo de preparación. Django es una herramienta del proyecto, no una dependencia del runtime.

T002 añade cuatro tablas en `0021_project_creation`, procedencia nullable en el registro y las rutas
`/project-creation-root` y `/project-creations` (preview/confirmación/lectura/reanudación/cancelación).
Las intenciones `project-creation-1` y sus reservas se sellan antes de efectos; transacciones de escritura SQLite
y un lock reentrante compartido con el registro serializan cada efecto corto y la retirada. `mkdir` usa fd del
padre sin seguir enlaces; identidad y fsync preceden al checkpoint. Los conflictos reconocen ancestros físicos
y alias de mayúsculas, también para reservas sin carpeta, sin depender solo de rutas textuales. Alta/evento/procedencia/resultado son atómicos.
El arranque solo clasifica carpetas inciertas; la continuación exige acción explícita. No hay borrado automático.
La preview de composición valida sobre el padre existente y calcula los hashes del futuro hijo sin crear puertos
para él. La composición operativa continúa exigiendo un checkout existente. La UI conserva el sobre y la clave
de confirmación al perder respuesta. Contratos/hashes v1–v4 previos, CLI y codec conservados. Flujo y límites en
[project-creation](flows/project-creation.md); plan y matriz en el [archivo de P009](archive/phase-009/P009_PLAN_DJANGO.md).


T004 implementa `recipes/django.py` y su perfil empaquetado, lock con hashes y closure de versiones.
[Fragmento de configuración v5](../examples/django-recipe.example.toml). Los enlaces `project_venv` solo
resuelven comandos después de acreditar el entorno; no adelantan validaciones al bootstrap documental.
`services/project_preparation.py`, `storage/preparation.py` y `adapters/preparation.py` separan plan/confirmación,
journal/lease/propietarios y transporte POSIX. Comparten locks/procesos con jobs mediante propietario exclusivo;
el carril escritor atiende su journal sin crear un run. Modelo/migración 0022 y [diagrama](DDBB-DIAGRAM.md).
Capturas inline, sin nuevas referencias externas de backup o purga. Recibos congelados en jobs posteriores;
guardias de bytes/configuración antes de efectos, y recuperación explícita sin replay automático de herramientas.
API/UI de preparación en [flujo](flows/project-preparation.md); verificación sintética y límites en
[entrega T004](archive/phase-009/P009-T004_RECETA_DJANGO.md). T005 verifica el scaffold con herramientas reales y el recorrido
API completo con CLI falsas, reinicios y recuperación, en un único hijo temporal:
[entrega y reproducción](archive/phase-009/P009-T005_ENSAYO_DJANGO.md). La variante real de pytest exige wheelhouse e intérprete
explícitos; si no se proporcionan se omite, sin descargas implícitas ni nuevas dependencias del harness.

## 12. Consolidación — P010

T002 añade la segunda receta empaquetada, `recipes/typescript_web.py` (`typescript-web-recipe-1`, D143), en el marco
D119: `[recipes.typescript-web]` en `local-config-5`, composición con el perfil integrado `typescript-web` y la caché
npm del operador en su entorno. `recipes/__init__.py` registra cada receta con su módulo y perfil; el servicio de
preparación separa el núcleo común de las partes por receta y el recibo TypeScript fija manifiesto protegido y
ejecutables, no `node_modules`. Sin migración ni cambios de API. [Fragmento v5](../examples/typescript-web-recipe.example.toml),
[flujo](flows/project-preparation.md) y [entrega](archive/phase-010/P010-T002_ARRANQUE_TYPESCRIPT.md).

T003 añade la proyección derivada `run-projection-1` (migración `0023`, seis tablas, D144): se escribe con cada
historial, se rellena una vez para los existentes sin reescribirlos y se comprueba en el backup. Las vistas de runs,
los ciclos paginados (`GET /runs/{id}/cycles`), las métricas y la vista previa de exportación (T011, D145) la leen sin
decodificar `history_json`; el envío confirmado de la exportación y el motor siguen leyendo el historial.
T004 aclara en `define-project` y en la UI que los marcadores gestionados son opcionales en la definición (D146).
T005 añade `PhaseRead.closure` (check, base, archivo y commit del cierre) y distingue la renovación de documentos
vivos de la deriva real de una fase cerrada (D147). T006 contrasta README, este documento y `examples/` con el código
y la evidencia ([entrega](archive/phase-010/P010-T006_DOCUMENTACION_VERSION.md), D148).

## 13. Preparación pública planificada — P011

[D154](DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github) abre P011 como planificación, sin
cambiar todavía implementación, dependencias, configuración, esquema, codec o catálogo de CLI.
La convención española de §8 y las listas exactas de §6 siguen describiendo el producto actual hasta sus entregas.

T001 inventaría superficies/identidades y fija el contrato de idiomas D158: defaults globales visual/trabajo en/es;
visual global mutable para UI/conversación y trabajo inmutable al alta para documentación/código por proyecto.
Catálogos/fallback/formatos, persistencia, par congelado por job/turno, compatibilidad y prompts originales ingleses.
La solución de internacionalización del cliente React y mensajes Python se decide
antes de añadir dependencias, no se asume `.po`. T007–T010 implementarán el contrato con paridad de modelos,
flujos y API/tipos en cada cambio; esta planificación no dibuja tablas o flujos como ya existentes.

Las recetas Django y TypeScript incorporan el texto de su módulo en la huella; traducir incluso comentarios
puede invalidar recibos. T004 (D163) conserva por bytes y huella `django.py`/`typescript_web.py`, sus datos y el
perfil `typescript-web`, y añade `django_2.py`/`typescript_web_2.py` (`django-recipe-2`, `typescript-web-recipe-2`):
fuente inglesa, scaffold con prosa técnica según idioma de trabajo en/es, perfil propio, pasos con `id` estable y
huella con versión e idioma. T020 (D168) las cablea: `recipes.GENERATIONS` elige v1 en `local-config-5` y v2 en
`local-config-6` con las mismas claves; la composición liga la huella v2 de ambos idiomas y el plan/recibo sellan el
idioma de la fila de la raíz (sin fila, 409 antes de efectos); comprobaciones por `id` y etiquetas visuales por
catálogo. Prompts, catálogos y snapshots anteriores permanecen congelados; no se renombran claves/revisiones/rutas.

T011 completa el [contrato](archive/phase-011/P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md) (D173): por HITL, detección automática
del cliente y su versión, sin pin ni aceptación de candidatas; mínimos comunes de nuevo trabajo Codex 0.163.0 y
Claude 2.1.304, con indicación de actualizar si son inferiores. Las versiones previas conservan lectura histórica,
sin nueva admisión bajo mínimos. Perfiles de capacidades por proveedor/rol mantienen guardias y procedencia;
el usuario final no importa evidencia. T012 implementa descubrimiento por PATH explícito/ruta opcional en v7,
composición con versión observada congelada y revalidación por intento (`cli-14`, D174; §6). HITL adicional:
las posteriores conservan las guardias del contrato conocido con compatibilidad condicionada, sin acreditar
efectos internos por flags ni exigir una caracterización a cada usuario/patch.
No equivale a garantizar cualquier versión futura ni a pasar a App Server/SDK. Versiones observadas y política
quedarán ligadas a los intentos sin reescribir evidencia previa o realizar downgrade/retry silencioso.

T013 contrastó semánticamente diagramas, datos y esta arquitectura con fuentes/tests (D175,
[matriz](archive/phase-011/P011-T013_MATRIZ_DIAGRAMAS.md)). T014–T017 preparan documentación inglesa, paquete
candidato con recursos en/es, CI sintética y primer uso aislado con dictamen. Requisitos build/servicio/hijo y
plataformas se acreditan por separado; no se cambia el límite de contención cooperativa ni se publica por efecto
de preparar workflows. [Plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md) y [tareas](archive/phase-011/NEXT_STEPS.md).

[D155](DECISIONS.md#d155--p011-retirada-del-harness-anterior-y-dos-vías-de-alta) añade T019, tras T002 y antes de
traducir: retirar visor/rutas `/legacy`, API/comandos/observadores/SSE legacy, activación desde el harness anterior
y normalización/importación A, incluidos sus prompts y módulos exclusivos. Solo creación desde cero e incorporación
de repositorio existente sin harness (B) como entradas; ambos usan seguimiento gestionado de my_harness.

B comparte `project_imports`, `purpose = import_commit`, repositorios y escritor Git con A; no se borran tablas,
clases o formatos por coincidir su nombre con `import`/`legacy`. T001/T019 separan dependencias necesarias de
componentes exclusivos y precisan tratamiento no destructivo de datos/jobs anteriores, recuperación, backup y
historiales propios. T019 entrega esta retirada y su compatibilidad de datos (D161); las migraciones y archivos históricos
permanecen intactos.

[D156](DECISIONS.md#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020) deja finalizada la
planificación de P011, con tareas pendientes, y reserva para v0.2.0 posterior a la apertura en GitHub el modo
continuo entre fases. No se modifica ahora supervisor/cola/autorizaciones: el lote actual encadena tareas/commits,
no inicia check/cierre y la planificación posterior mantiene su confirmación por hash (D034/D091).
El diseño futuro de automatización y sus límites tiene fase/tareas propias por definir, fuera de esta entrega.

D157 planifica la frontera inicial: instantánea saneada en repositorio público con nueva raíz Git y docs útiles
de partida, sin objetos/historia/ADR/fases privados; después código/decisiones/fases evolucionan allí como fuente
principal. Exportación/validación en T002/T014–T017, sin reescribir este checkout ni crear/publicar repositorios ahora.

D158 requiere persistir solo trabajo inmutable en el proyecto y defaults/preferencia visual en ajustes globales
del producto; el contrato T001 determinará el almacenamiento sin editar TOML/configuración global del equipo.
Cada job/turno congela trabajo y lengua visual de respuesta; cambios globales no alteran pendientes/activos ni
reintentos. Directivas tipadas y versionadas separarán prosa humana de borradores/código en respuestas estructuradas.
Se usará el canal de instrucciones realmente disponible en cada CLI, sin asumir un system prompt nativo común;
no cambia hoy `render_attempt`, adaptadores, variables, snapshots, API o esquema. T007–T010 tendrán su paridad.
