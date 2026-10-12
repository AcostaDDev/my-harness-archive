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
Siguiente tarea: H2.5 migración a modo gestionado, sin iniciarlo aquí.
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
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline uvicorn harness_local.api.app:create_app --factory --host 127.0.0.1 --port 8013 --workers 1
npm --prefix frontend run dev
```

Las primeras instalaciones necesitan red; después los checks son offline.
No usar `uv --active` con entornos de otros proyectos. 253 pruebas pytest
(158 anteriores + 53 H2.3 + 8 entorno smoke + 34 H2.4 con Git temporal).
API/UI compilada en 127.0.0.1:8013; Vite en :5173
en otra terminal. SQLite local ignorada en `.local/harness.sqlite3`; migración
explícita antes de arrancar. Ver README y `docs/discovery/H0.3_SKELETON.md`.
Estos comandos verifican el esqueleto simulado, el índice legacy, su navegación/observación/SSE
y el motor/persistencia/cola/procesos sintéticos; nunca agentes reales.
Esquema actual `0006_git_commits`; SQLite debe estar
fuera del checkout que se importa. Ver `docs/discovery/H1.1_IMPORT.md` y
`docs/discovery/H1.2_NAVIGATION.md`. Ver `docs/discovery/H1.3_OBSERVATION.md`
y `docs/discovery/H2.1_ENGINE.md` y `docs/discovery/H2.2_PERSISTENCE.md`.
Ver `docs/discovery/H2.3_CLI.md`, `docs/discovery/H2.3_SMOKE.md` y
`docs/discovery/H2.4_GIT.md`. El smoke real
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
no hacer login, consumir ni relanzar automáticamente. Siguiente tarea: H2.5 offline.
Los checks no consumen proveedores. El supervisor
solo se invoca explícitamente, sin entradas API/CLI gestionadas ni autoarranque.
El commit se encola como acción `commit` por inyección de `commit_factory`.
H2.5 no iniciado.
