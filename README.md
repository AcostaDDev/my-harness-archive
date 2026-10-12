# my_harness — Harness Local

Aplicación local para configurar, ejecutar y observar un harness modular de desarrollo con agentes.
Estado actual: H0, H1, H2.1, H2.2, H2.3 y H2.4 completados. H2.3 conserva un smoke
real autorizado con las tres CLI (D025); H2.4 añade Git por árboles, worktree por
tarea y commit determinista conciliable, verificados offline. Siguiente tarea:
H2.5 migración a modo gestionado. Esqueleto Python/API/UI con simulaciones
persistidas, observación legacy y motor con persistencia/cola.
Adaptadores CLI y grupos de procesos por inyección explícita; sin entradas
gestionadas API/CLI/UI ni ejecución automática de proveedores.

## Documentación

- [Especificación](docs/01-especificacion-harness-local.md).
- [Backlog](docs/02-backlog-y-plan-de-desarrollo.md).
- [Decisiones, Celery y Docker](docs/DECISIONS.md).
- [Estado real](docs/STATE.md) y [siguiente tarea](docs/NEXT_STEPS.md).
- [Guía de inicio con Codex](docs/START_HERE.md).
- [Instrucción inicial ampliada](docs/03-instruccion-inicial-para-codex-y-claude.md).
- [Inventario de referencia](docs/discovery/BASELINE.md) y [formatos legacy](docs/discovery/LEGACY_FORMATS.md).
- [Fixtures sintéticos y límites de verificación](tests/fixtures/legacy/README.md).
- [Versiones, capacidades y autenticación](docs/discovery/H0.2_COMPATIBILITY.md).
- [Streams sintéticos y sonda offline](tests/fixtures/streams/README.md).
- [Entrega y verificaciones H0.3](docs/discovery/H0.3_SKELETON.md).
- [Importación de lectura H1.1](docs/discovery/H1.1_IMPORT.md).
- [Navegación y evidencias H1.2](docs/discovery/H1.2_NAVIGATION.md).
- [Observación y SSE H1.3](docs/discovery/H1.3_OBSERVATION.md).
- [Motor aislado H2.1 y límites](docs/discovery/H2.1_ENGINE.md).
- [Persistencia/cola H2.2](docs/discovery/H2.2_PERSISTENCE.md).
- [Adaptadores CLI/procesos H2.3](docs/discovery/H2.3_CLI.md) y
  [resultado del smoke autorizado](docs/discovery/H2.3_SMOKE.md).
- [Corrección offline de configuración Codex](docs/discovery/H2.3_CONFIG_FIX.md).
- [Nuevo smoke autorizado: Codex completo, fallo MCP Claude](docs/discovery/H2.3_SMOKE_RETRY.md).
- [Smoke cli-3: MCP aceptado, fallo de autenticación Claude](docs/discovery/H2.3_SMOKE_CLI3.md).
- [Git, worktree y commit acotado H2.4](docs/discovery/H2.4_GIT.md).

`AGENTS.md` contiene las instrucciones de Codex; `CLAUDE.md` remite al mismo contrato para Claude Code. El desarrollo es manual y no utiliza el harness como orquestador.

## Arranque local comprobado

Requisitos comprobados en macOS ARM64: Python 3.14.4, uv 0.12.19,
Node 24.15.0 y npm 11.12.1. Desde la raíz, instalar en `.venv` y
`frontend/node_modules` con los locks versionados:

```sh
UV_CACHE_DIR=.local/uv-cache uv sync --frozen --no-python-downloads
npm --prefix frontend ci --ignore-scripts --cache .local/npm-cache
```

Las descargas iniciales necesitan red; no acceden a modelos ni cuentas CLI.
Las cachés quedan dentro del repositorio. uv ignora un `VIRTUAL_ENV` de otro
proyecto: no usar `--active` para estos comandos.

Migrar explícitamente y compilar la UI:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic upgrade head
npm --prefix frontend run build
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline uvicorn harness_local.api.app:create_app --factory --host 127.0.0.1 --port 8013 --workers 1
```

Abrir `http://127.0.0.1:8013`. El servicio sirve la UI compilada y su API.
«Ejecutar simulación» guarda un resultado sintético; recargar o reiniciar
conserva el historial. Detener con Ctrl+C. Ejecutar desde la raíz y con un
único proceso; el arranque exige la migración y no crea tablas automáticamente.

Para desarrollo, mantener la API anterior en una terminal y usar otra:

```sh
npm --prefix frontend run dev
```

Abrir `http://127.0.0.1:5173`; Vite dirige `/api` al servicio en el puerto 8013.
SQLite usa por defecto `.local/harness.sqlite3`, WAL y transacciones cortas.
`HARNESS_DATABASE_URL=sqlite:////ruta/absoluta/demo.sqlite3` permite otro archivo
local; usar el mismo valor al migrar y arrancar. Sin Celery ni Docker obligatorio.

## Contratos y verificaciones

Los esquemas Pydantic generan OpenAPI y los tipos consumidos por la UI.
Tras cambiar un contrato, regenerar desde la raíz:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python scripts/export_openapi.py
npm --prefix frontend run generate:types
npm --prefix frontend run check
```

La exportación no inicia el servicio ni abre SQLite. Versionar `frontend/openapi.json`
y `frontend/src/api.generated.ts`; no editar los tipos generados a mano.

Checks del producto y de los fixtures, con dependencias ya instaladas, sin red:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic current
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic check
```

253 pruebas (158 anteriores, 53 de H2.3, 8 del entorno del smoke y 34 de H2.4). Se usan checkouts Git, SQLite y
procesos Python sintéticos, sin CLI de proveedores ni consumo de suscripciones.
Se verifican captura incremental, cancelación de grupos y recuperación tras
caída del supervisor. No certifica commits ni introduce ejecución gestionada
desde API/CLI. Los 12 checks ligeros siguen sin lanzar procesos.

## Comprobación offline disponible

Desde la raíz, con Python y su biblioteca estándar, sin instalar dependencias:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Doce checks ligeros: cuatro de fixtures H0.1 y ocho de streams H0.2; no ejecutan
el harness ni proveedores. Este comando sigue sin necesitar dependencias del
producto. H0.3 ya verifica instalación y ejecución del esqueleto; las CLI
reales por suscripción tienen adaptadores H2.3. El primer smoke falló al cargar
configuración Codex; el nuevo smoke autorizado `cli-2` completa el planificador
Codex y se detiene ante configuración MCP inválida de Claude, sin revisor.
El supervisor se invoca explícitamente, sin entrada API/CLI ni arranque automático.
La configuración se corrigió offline, con regresión y retries internos declarados
desconocidos. La corrección MCP Claude `cli-3` está verificada offline y el smoke
posterior acepta MCP vacío, pero se detiene en autenticación Claude con terminal
de error. El diagnóstico en lectura observó la dependencia de USER; la corrección
offline del smoke ya valida USER contra el UID local, sin heredar credenciales.
El smoke posterior autorizado con USER completó planificador Codex, ejecutor Claude
y revisor Codex: terminal/exit 0/JSON en los tres, sin herramientas ni cambios.
H2.4 (Git, worktree por tarea y commit determinista conciliable) está completado
offline: ver [entrega y límites](docs/discovery/H2.4_GIT.md); sin entrada API/CLI.
Siguiente tarea: H2.5 migración a modo gestionado, sin iniciar. Ver [corrección y límites](docs/discovery/H2.3_MCP_FIX.md)
y [resultado real cli-3](docs/discovery/H2.3_SMOKE_CLI3.md). El consentimiento
terminó al fallo; otro smoke requiere propuesta y autorización específicas.
Ver [corrección del entorno](docs/discovery/H2.3_ENV_FIX.md) y
[propuesta conservada](docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md) y
[resultado completo](docs/discovery/H2.3_ENV_SMOKE.md). Este éxito acredita el
transporte, sin aceptación/commit de producto; los locks de smokes anteriores
siguen conservados. La autorización cubrió una ejecución, sin relanzamiento.


## Importación legacy de lectura

Migrar con el servicio detenido antes de importar; el esquema actual es
`0006_git_commits`. Comandos comprobados desde la raíz, con datos sintéticos:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic upgrade head
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -m harness_local.cli legacy-import tests/fixtures/legacy/accepted
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -m harness_local.cli legacy-summary tests/fixtures/legacy/accepted
```

Cada argumento identifica una raíz de checkout con `.harness/runs`. Repetir
`legacy-import` relee explícitamente sin duplicar registros; `legacy-summary`
consulta solo SQLite e imprime JSON con procedencia, evidencias y diagnósticos.
Usa la misma `HARNESS_DATABASE_URL` al migrar, importar y consultar. La base
**debe quedar fuera del checkout de origen**; los archivos originales siguen
siendo autoridad. Los JSON parciales quedan pendientes y no indican fallo de agente.
Los campos ausentes/null aparecen como «no registrado», conservando su diferencia;
los valores cero se muestran como registrados. No ejecuta los comandos históricos.
La UI H1.2 abre «Proyectos importados» y permite seleccionar fase/tarea/run,
inspeccionar revisiones, preguntas, consumo, validaciones, logs/diffs y documentos
archivados. Las listas y el contenido se paginan; cada tramo comprueba el hash
indexado antes de mostrar bytes del origen. Si cambia/desaparece el archivo,
se muestra un diagnóstico; reimportar y recargar actualiza la observación.
Ausencias/JSON parciales siguen visibles. ACCEPT/READY no certifican commit/cierre.
«Simulaciones H0.3» conserva el recorrido anterior.

Tras seleccionar un proyecto, «Activar observación» habilita relectura incremental
por polling (0,5 s), reconciliación al iniciar/cada 30 s y actualización UI por SSE.
«Detener observación» conserva el índice y permite seguir releyendo explícitamente
por CLI. La decisión persiste tras reiniciar. «Actividad persistida del índice»
recupera cambios paginados; cerrar el navegador no detiene la observación.
Los eventos y cambios se guardan juntos; cursor local y Last-Event-ID permiten
reconectar sin añadir actividad duplicada. Un hash nuevo reinicia los tramos desde
cero; respuestas de otra versión se ocultan. Archivos especiales/enlaces no se leen;
lectura máxima 64 MiB por evidencia. No certifica un snapshot entre archivos ni
captura todas las versiones sobrescritas entre ciclos. Detalles y límites en
[H1.3_OBSERVATION.md](docs/discovery/H1.3_OBSERVATION.md).
Migrar explícitamente con el servicio detenido antes de arrancar esta versión.
