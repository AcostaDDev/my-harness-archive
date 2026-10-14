# Instrucciones de desarrollo — my_harness

## Contexto y modo de trabajo

Este repositorio desarrolla Harness Local, una aplicación local de orquestación con interfaz web. El desarrollo de este producto es manual, asistido por Codex y Claude Code. Ambos pueden implementar código cuando el usuario lo pide. No confundir esta forma de desarrollar con los roles Codex revisor / Claude ejecutor que tendrá el producto.

No ejecutar el harness para desarrollar este repositorio ni lanzar sesiones de otros agentes automáticamente. El usuario coordina las herramientas.

## Contexto duradero

Al iniciar, leer `docs/STATE.md` y `docs/NEXT_STEPS.md`. Consultar las secciones relevantes de:

- `docs/01-especificacion-harness-local.md`: alcance y diseño aceptados como base.
- `docs/02-backlog-y-plan-de-desarrollo.md`: hitos y criterios de aceptación.
- `docs/DECISIONS.md`: decisiones y aclaraciones operativas.

Si se encuentra una contradicción material, señalarla antes de cambiar el diseño. Resolver detalles reversibles de implementación con criterio, sin pedir confirmación rutinaria.

## Referencia anterior

`$HOME/Documents/projects/reference_project/.harness` es referencia de lectura. No modificar ReferenceProject, ejecutar su harness ni lanzar allí agentes, instalaciones o tests. Sus reglas de producto no se trasladan a este repositorio. No copiar runs reales, credenciales ni datos privados a fixtures; usar datos sintéticos.

## Arquitectura

- Núcleo Python independiente de web, proveedores y stacks de proyectos.
- FastAPI/Pydantic/Uvicorn, SQLite/SQLAlchemy/Alembic, React/TypeScript/Vite.
- Ejecución nativa local; sin Celery, broker ni Docker obligatorio para el servicio en el MVP.
- CLI primero; App Server / Agent SDK solo tras comprobar compatibilidad y autenticación.
- Versiones y comandos reales se fijan al crear el esqueleto; no documentar scripts inexistentes como disponibles.
- Detalles específicos de Django/Docker pertenecen a perfiles, no al núcleo.

## Invariantes

- Una sola ejecución escritora por checkout.
- Contratos, prompts, políticas y metadatos congelados por intento.
- Historial de intentos conservado; reanudar trabajo no exige reanudar conversación.
- Permisos de archivos, herramientas, red y decisiones de producto separados.
- Validación y revisión vinculadas al contenido exacto antes del commit.
- Fallos no provocan fallback de modelo ni llamadas adicionales silenciosas.
- Datos solicitados, observados, estimados y ausentes se distinguen.
- Estado operativo gestionado en SQLite; importación legacy de lectura sin doble autoridad.

## Trabajo y verificación

Completar una tarea acotada cada vez con comprobaciones proporcionales. Se permiten edición local, fixtures sintéticos y tests offline pertinentes a la tarea. No lanzar smoke tests con proveedores, compras, publicación, push ni acciones externas sin autorización explícita. No modificar configuración global del usuario.

No descartar cambios ajenos. Si otra sesión trabaja en el mismo checkout, revisar el estado antes de editar y no asumir propiedad de sus cambios. No hacer commits automáticamente salvo que el usuario los pida.

Antes de dar una tarea por terminada: verificar criterios, ejecutar checks disponibles relevantes, revisar el diff y actualizar `docs/STATE.md` y `docs/NEXT_STEPS.md`. Registrar decisiones duraderas en `docs/DECISIONS.md`. Indicar qué se probó, qué no y la siguiente tarea concreta. Nunca marcar como implementado algo que solo está diseñado.

## Comandos actuales

H0, H1, H2.1 y H2.2 completados: inventario, compatibilidad, fixtures, esqueleto simulado,
importación legacy local de lectura, navegación web, observación incremental/SSE
y extracción del motor con contexto explícito, persistencia/cola/exclusión.
H2.3 implementado y verificado offline: adaptadores CLI por inyección explícita,
captura incremental/cancelación y recuperación. Smoke real previo detenido por
configuración Codex incompatible; corregida offline en `cli-2`. Nuevo smoke
autorizado: Codex completo, Claude falla por configuración MCP; sin revisor ni relanzar.
Corrección MCP verificada offline en `cli-3`; smoke autorizado posterior completa
Codex y falla en autenticación Claude, con MCP vacío aceptado y sin revisor.
Diagnóstico de auth completado en lectura: entorno mínimo omite USER;
status fuera del sandbox reconoce sesión al añadir solo USER, sin login.
Corrección offline del entorno del smoke completada: USER validado contra UID
local, hash distinto y regresión sintética; adaptador cli-3 conservado.
Smoke posterior autorizado completó las tres CLI con USER validado: transporte
completo, sin herramientas ni cambios de checkout. Ver D025.
H2.4 completado offline: captura Git por árboles, worktree por tarea y commit
determinista conciliable tras caídas (D026); sin proveedores. Ver
`docs/discovery/H2.4_GIT.md`.
H2.5 completado offline: vista previa, copia consistente, activación reanudable,
exclusión legacy/gestionado por marcador y deriva, y reversión verificada (D027).
Ver `docs/discovery/H2.5_MIGRATION.md`.
Salida del hito 2, parte 1, completada offline: API `/api/managed` sobre la
autoridad H2.2–H2.5, proyectos registrados en el servidor y supervisor opt-in en
Uvicorn (D028). Ver `docs/discovery/H2_EXIT_API.md`.
Salida del hito 2, parte 2, completada offline: UI gestionada local con sondeo,
confirmaciones, claves conservadas, diff/tests/review y demo sintética. D029;
ver `docs/discovery/H2_EXIT_UI.md`. H3.1 completado offline: catálogo de prompts,
editor API/UI, activación/rollback y snapshots por intento (D030); ver
`docs/discovery/H3.1_PROMPTS.md`. H3.2 completado offline: permisos por petición exacta, conceder/denegar/sustituir,
consumo once/task y snapshots, CLI cli-4 y API/UI (D031); revalidar REVISE exige
reintento explícito. Ver `docs/discovery/H3.2_PERMISSIONS.md`.
H3.3 completado offline: fases en SQLite, check/cierre como jobs, READY por
contenido exacto, tag ligero por CAS y autorizaciones de lote/cierre separadas
(D032). Ver `docs/discovery/H3.3_PHASES.md`. Decisiones del usuario en D033.
H3.4 completado offline: guardia H0/H1, lote desatendido con commits, enmienda/
abandono, tags anotados y reconciliación con agente (D034); ver
`docs/discovery/H3.4_PHASE_ADJUSTMENTS.md`.
H4.1 completado offline: chat por turnos nuevos de solo lectura con contexto
congelado y propuestas confirmadas como tareas normales (D035); ver
`docs/discovery/H4.1_CHAT.md`.
Exportación mecánica completada offline (D036): preview/diff confirmado, commit H2.4
conciliable y adopción de hashes, con bloques delimitados y prosa conservada.
Ver `docs/discovery/STATE_EXPORT.md`. H4.2 completado offline (D037): destinos vacíos
opt-in, brief/decisiones, propuesta Codex de solo lectura, preview y plantilla
versionada, commit raíz conciliable, primera fase/tarea acotada y API/UI.
Carpetas con contenido requieren importación. Ver `docs/discovery/H4.2_BOOTSTRAP.md`.
H4.3 completado offline (D038): segundo perfil TypeScript web, preparación y
validaciones reales por puertos de prueba en Git/SQLite sintéticos, sin cambios
del núcleo. Ver `docs/discovery/H4.3_TYPESCRIPT_PROFILE.md`.
H5.1 completado offline: reportes JUnit declarados por comando/perfil, original
con hash en historial codec 6, parser acotado, procedencia exacta y consulta API/UI.
Ver `docs/discovery/H5.1_JUNIT.md` (D039).
H5.2 completado offline: backup SQLite/artefactos con servicio detenido,
manifiesto/hashes e integridad; restauración nueva de consulta con guardia
persistente, sin reanudar procesos. Ver `docs/discovery/H5.2_BACKUP.md` (D040).
H5.3 completado offline: retención explícita de stdout/stderr sellados con preview,
auditoría/conciliación y consulta CLI/API/UI; backup conserva ausencias autorizadas.
Ver `docs/discovery/H5.3_RETENTION.md` (D041).
H5.4 completado offline: diagnóstico CLI explícito y preflight versión/help
compartido, acotado y sin secretos, sin autenticación ni inferencia (D042).
Ver `docs/discovery/H5.4_DIAGNOSTICS.md`.
H5.5 completado offline: wheel/sdist con UI/migraciones y entrada local (D043).
Ver `docs/discovery/H5.5_DISTRIBUTION.md`.
H5.6 completado offline: sesión efímera, guardia uniforme API/streams y UI (D044).
Ver `docs/discovery/H5.6_SESSION.md`.
H5.7 completado offline: seis recorridos API/sesión y flujo gestionado del wheel
con restauración de evidencia (D045). Ver `docs/discovery/H5.7_E2E.md`.
Revisión de cierre offline completada. Ejecutor de validaciones de producto
implementado offline (D047): `commands-1`, configuración explícita congelada,
captura acotada en SQLite, gate/grupos y recuperación bajo el lock existente.
Codec 7 con formatos 1–6 compatibles; esquema `0013_bootstrap` conservado.
Ver `docs/discovery/COMMAND_RUNNER.md`. Revisión independiente completada (D048):
runner congelado obligatorio; ver `docs/discovery/COMMAND_RUNNER_REVIEW.md`.
Composición de uso real por TOML local completada offline (D049): `harness-local
check-config RUTA [--preflight]` y `serve --database RUTA --config RUTA`; ver
`docs/discovery/LOCAL_CONFIG.md`. Primer uso real D050 ejecutado una vez y
completo (`docs/discovery/FIRST_USE_RUN.md`). Uso real desde el wheel instalado
en un venv propio, no desde este checkout (D051). Consentimiento agotado.
Desarrollo local con un solo comando: `scripts/dev` (D053, `docs/discovery/DEV_COMMAND.md`).
Revisor/ejecutor con proveedor elegido implementado offline (D052, `cli-5`,
`local-config-2`; `docs/discovery/AGENT_ROLES.md`). Smoke con proveedores no autorizado.
Matriz D055 ejecutada y detenida: la combinación 1 falló en el planificador porque
`validation_commands` llegó como listas de argv; 2–4 no lanzadas. Consentimiento agotado
(`docs/discovery/PROVIDER_MATRIX_RUN.md`, `examples/provider_matrix/prepare.sh`).
Formas de salida alineadas con el motor (D056, `docs/discovery/CONTRACT_SHAPES.md`): esquema tipado,
plantilla `plan-task` aclarada y argv de `validation_commands` normalizado; offline.
Matriz D057 ejecutada y cerrada: Codex→Claude `COMMITTED`; Codex escritor no editó;
lector Claude devolvió listas como texto por `--json-schema` sin tipos; 4 no lanzada
(`docs/discovery/PROVIDER_MATRIX_RERUN.md`, `examples/provider_matrix/run_pairing.sh`).
`--json-schema` tipado del lector Claude como adaptador `cli-6` (D058,
`docs/discovery/TYPED_JSON_SCHEMA.md`): esquema congelado del motor, sin normalizar texto; offline.
Diagnóstico del escritor Codex completado por lectura del binario y D057 (D059):
negativa del modelo sin intentar herramientas; origen en raíces temporales sigue
como hipótesis. `cli-7` declara checkout canónico en `writable_roots`, excluye
`/tmp` automático y aclara el acceso solicitado en la entrada del escritor.
Ver `docs/discovery/CODEX_WRITER_ROOTS.md`. Cuarentena de jobs `cli-6`; sin sesiones reales.
D060 ejecutada una vez y cerrada con parada preventiva (D061): Codex→Codex
COMMITTED con edición real; cambio de hash de `~/.codex/config.toml` detectado
entre combinaciones, atribución pendiente. Claude→Claude y Claude→Codex no
lanzadas. Consentimiento agotado; siguiente diagnóstico offline, sin inferencia.
Ver `docs/discovery/PROVIDER_MATRIX_CLI7_RUN.md`.
Diagnóstico D062 completado offline: delta de confianza de 93 bytes acreditado
por hash inverso; vía interna de persistencia de Codex identificada, atribución
original inferida. Sin corrección de transporte: contención/auth por concretar.
Ver `docs/discovery/CODEX_GLOBAL_CONFIG_DIAGNOSIS.md`. `cli-7` conservado;
sin CLI reales ni nuevos consentimientos.
Memoria automática desactivada explícitamente en el transporte, verificada
offline (D066, `cli-8`): Codex no solicita generación/inyección de memorias ni
historial; Claude recibe autoMemoryEnabled=false y rechaza un override ambiental
conflictivo. HOME/USER/auth conservados, sin contención OS integrada. La
persistencia de confianza Codex y otros auxiliares sigue pendiente; no se
certifica ausencia de memoria/estado externo con CLI real. Ver
`docs/discovery/AGENT_PERSISTENCE.md`. Actualización D068–D071: `cli-9` evita
específicamente persistencia de confianza en el escritor con una tabla projects
inline untrusted, acreditada en fuente/pin y con escritura real. D069/D070
detenidas por contrato contradictorio y timeouts; contrato/prompt corregidos.
D071 autorizada expresamente y completa las cuatro combinaciones COMMITTED,
con controles de memoria actuales y muestras globales intactas. Ver
`docs/discovery/CODEX_TRUST_SUPPRESSION.md` y
`docs/discovery/PROVIDER_MATRIX_CLI9_RUN.md`. Comprobación funcional cerrada;
aislamiento auxiliar total y continuidad documental por fase no certificados.
Autorización satisfecha/agotada: ninguna matriz nueva o relanzamiento implícitos.
Organización documental por fase diseñada (D072) y confirmada (D073). H6.3
implementado offline: contrato documental v2 opt-in (`documents = "v2"`), bloques
regenerados por commit, transición de fase y edición confirmada
(`docs/discovery/H6.3_DOCUMENT_CONTRACT.md`). H6.4 implementado offline (D074):
métricas por intento en `0014_attempt_metrics`, captura `terminal-2`, relleno explícito
`harness-local metrics-backfill --database RUTA [--artifact-root RAÍZ]`, agregados en
`/api/managed/metrics/*` y tokens/turnos en el SUMMARY (`docs/discovery/H6.4_METRICS.md`).
H6.5 implementado offline (D075): conversaciones `definition` y `phase_planning` en `0015_planning`,
borradores en la carpeta destino con CAS escritos solo al aplicar propuestas confirmadas, aceptación →
bootstrap D037 con plantilla v2 y `phase-000`, y `plan_proposal` en la transición
(`docs/discovery/H6.5_CONVERSATIONAL_CREATION.md`). Siguiente: H6.2 (UI de producto), tarea aparte.
Comprobación offline ligera, solo biblioteca estándar, desde la raíz:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Doce checks (cuatro legacy y ocho de contratos de streams), sin agentes ni red.
El producto tiene dependencias instaladas localmente y locks `uv.lock` /
`frontend/package-lock.json`; pins de H0.2 conservados. Comandos comprobados
desde la raíz, usando Python 3.14.4, uv 0.12.19, Node 24.15.0, npm 11.12.1:

```sh
UV_CACHE_DIR=.local/uv-cache uv sync --frozen --no-python-downloads
npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic upgrade head
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -m harness_local.cli legacy-import tests/fixtures/legacy/accepted
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -m harness_local.cli legacy-summary tests/fixtures/legacy/accepted
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic current
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic check
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/export_openapi.py
npm --prefix frontend run generate:types
npm --prefix frontend run check
npm --prefix frontend run build
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline uvicorn harness_local.api.app:create_app --factory --host 127.0.0.1 --port 8013 --workers 1 --no-proxy-headers --no-access-log
npm --prefix frontend run dev
```

Las primeras instalaciones necesitan red; después los checks son offline.
No usar `uv --active` con entornos de otros proyectos. 1057 pruebas pytest
(158 anteriores + 53 H2.3 + 8 entorno smoke + 34 H2.4 + 35 H2.5 + 18 API gestionada + 2 demo UI + 23 H3.1,
+ 30 H3.2 + 29 H3.3 + 18 H3.4 + 22 H4.1 + 32 exportación + 48 H4.2 + 16 H4.3 + 43 H5.1 + 43 H5.2 + 43 H5.3 + 52 H5.4 + 13 H5.5 + 45 H5.6 + 6 H5.7 + 40 ejecutor de comandos + 35 configuración local + 11 comando de desarrollo + 32 agentes D052 + 16 formas de contrato D056 + 6 esquema tipado D058 + 10 raíces Codex D059 + 20 memoria CLI D066 + 2 confianza CLI D068 + 5 contradicción de ámbito D069 + 37 contrato documental H6.3 + 26 métricas H6.4 + 44 creación/planificación H6.5 + 2 plantillas H6.5,
con Git temporal).
Paquete H5.5: UI/API en 127.0.0.1:8013; en desarrollo API en :8013 y Vite en :5173
en otra terminal. SQLite local ignorada en `.local/harness.sqlite3`; migración
explícita antes de arrancar. Ver README y `docs/discovery/H0.3_SKELETON.md`.
Estos comandos verifican el esqueleto simulado, el índice legacy, su navegación/observación/SSE
y el motor/persistencia/cola/procesos sintéticos; nunca agentes reales.
Esquema actual `0015_planning`; SQLite debe estar
fuera del checkout que se importa. Ver `docs/discovery/H1.1_IMPORT.md` y
`docs/discovery/H1.2_NAVIGATION.md`. Ver `docs/discovery/H1.3_OBSERVATION.md`
y `docs/discovery/H2.1_ENGINE.md` y `docs/discovery/H2.2_PERSISTENCE.md`.
Ver `docs/discovery/H2.3_CLI.md`, `docs/discovery/H2.3_SMOKE.md` y
`docs/discovery/H2.4_GIT.md` y `docs/discovery/H2.5_MIGRATION.md`. El smoke real
H2.3 autorizado lanzó solo Codex y falló al cargar `model_providers.openai`;
la corrección offline `cli-2` elimina los overrides reservados y declara retries
internos desconocidos. Ver `docs/discovery/H2.3_CONFIG_FIX.md`. El nuevo smoke
autorizado D020 completó Codex y se detuvo en Claude por `mcpServers` ausente;
ver `docs/discovery/H2.3_SMOKE_RETRY.md`. Corrección offline MCP completada en
`cli-3`; ver `docs/discovery/H2.3_MCP_FIX.md`. Smoke autorizado D022 completa
Codex y falla con `authentication_failed` en Claude; MCP vacío aceptado,
terminal de error, revisor no lanzado. Ver `docs/discovery/H2.3_SMOKE_CLI3.md`.
Diagnóstico de autenticación Claude completado en lectura (D023): dependencia
de USER observada con status, sin inferencia ni corrección. Ver
`docs/discovery/H2.3_AUTH_DIAGNOSIS.md`. Corrección offline del entorno completada
(D024): USER explícito comprobado contra el UID local, sin credenciales heredadas;
hash congelado distinto bloquea configuraciones anteriores, cli-3 conservado.
Ver `docs/discovery/H2.3_ENV_FIX.md`. Smoke D025 autorizado y completo con USER:
planificador/ejecutor/revisor COMPLETE, exit 0/terminal/JSON; 57 eventos, job DONE,
run STOPPED por fin deliberado del smoke, owner cerrado, grupos STOPPED/dead y
lock nuevo liberado por finalización normal. D020/D022 y sus locks conservados.
Ver `docs/discovery/H2.3_ENV_SMOKE.md`. Sin aceptación/commit de producto ni
cuota/retries certificados. Consentimiento satisfecho por una ejecución;
no hacer login, consumir ni relanzar automáticamente. H5.7 completado offline (D045); ejecutor de comandos completado offline (D047) y revisado (D048); configuración local TOML (D049).
Los checks no consumen proveedores. Sin configuración gestionada, la API
`/api/managed` no tiene proyectos, puertos ni supervisor y solo lee.
`HARNESS_MANAGED_CONFIG=módulo:atributo` (o `create_app(managed=...)`) registra
proyectos y puertos explícitos; el supervisor solo arranca con `supervisor=True`.
La API exige sesión y Host loopback; Origin, si existe, debe coincidir con el
servicio. Mutaciones exigen además la cabecera CSRF `X-Harness-Local: 1`. El commit se encola como acción `commit` por inyección de `commit_factory`.
La migración H2.5 se expone por `/api/managed` y la UI sobre `MigrationService`, sin CLI;
sus copias y exportaciones viven en `migrations/` junto a la SQLite local.

Regresión del cliente gestionado, sin dependencias adicionales ni navegador:

```sh
node --test frontend/tests/managed-api.test.mjs
```

Seis pruebas Node. Demo offline opt-in: `examples.managed_demo:build`, preparación
y comandos en `docs/discovery/H2_EXIT_UI.md`. Nunca apuntar la demo a un checkout
real. Toda API (lecturas, evidencias, health/OpenAPI y streams incluidos) exige
sesión local. Al arrancar se anuncia solo la ruta de la clave en un archivo
privado temporal; copiarla en la UI. Caduca a las ocho horas; cierre/reinicio la
invalidan. Host loopback, Origin exacto y CSRF siguen siendo obligatorios.
La UI no activa proveedores ni repite acciones al iniciar sesión.
