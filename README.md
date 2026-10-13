# my_harness — Harness Local

Aplicación local para configurar, ejecutar y observar un harness modular de desarrollo con agentes.
Estado actual: H0, H1, H2.1–H2.5, salida del hito 2, H3.1–H3.4,
H4.1–H4.3 y exportación mecánica de STATE/NEXT_STEPS completados offline.
Python/API/UI con simulaciones, observación legacy y motor con cola/persistencia;
Git, migración gestionada, prompts/permisos, fases/lotes, chat contextual y bootstrap guiado.
La exportación usa diff confirmado, commit conciliable y adopción de hashes (D036).
H2.3 conserva el smoke real de transporte D025; el resto está verificado con
Git/SQLite sintéticos y fakes. Proveedores opt-in por inyección explícita, sin
entrada CLI gestionada. Siguiente tarea: H5.1 importación JUnit, sin iniciar.

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
- [Permisos y recuperación H3.2, verificados offline](docs/discovery/H3.2_PERMISSIONS.md).
- [Fases, preguntas, cierre y tags H3.3, verificados offline](docs/discovery/H3.3_PHASES.md).
- [Ajustes de fases, lote desatendido y guardia H0/H1 H3.4, verificados offline](docs/discovery/H3.4_PHASE_ADJUSTMENTS.md).
- [Chat contextual H4.1, verificado offline](docs/discovery/H4.1_CHAT.md).
- [Exportación mecánica de STATE/NEXT_STEPS, verificada offline](docs/discovery/STATE_EXPORT.md).
- [Bootstrap guiado H4.2 y demo offline](docs/discovery/H4.2_BOOTSTRAP.md).
- [Segundo perfil TypeScript web H4.3: comandos reales y límites](docs/discovery/H4.3_TYPESCRIPT_PROFILE.md).
- [Smoke cli-3: MCP aceptado, fallo de autenticación Claude](docs/discovery/H2.3_SMOKE_CLI3.md).
- [Git, worktree y commit acotado H2.4](docs/discovery/H2.4_GIT.md).
- [Migración a modo gestionado H2.5](docs/discovery/H2.5_MIGRATION.md).
- [API gestionada local, salida del hito 2 parte 1](docs/discovery/H2_EXIT_API.md).

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

331 pruebas (158 anteriores, 53 de H2.3, 8 del entorno del smoke, 34 de H2.4, 35 de
H2.5, 18 de la API gestionada, 2 de la demo UI y 23 de H3.1). Se usan checkouts Git, SQLite y procesos Python
sintéticos, sin CLI de proveedores ni consumo de suscripciones. Se verifican
captura incremental, cancelación de grupos, recuperación tras caída del supervisor
y el recorrido HTTP con fakes hasta COMMITTED. No certifica commits con proveedores.
Los 12 checks ligeros siguen sin lanzar procesos.

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
El supervisor solo arranca dentro del servicio si la configuración gestionada lo pide
(`supervisor=True`); sin configuración, `/api/managed` no tiene proyectos ni puertos.
La configuración se corrigió offline, con regresión y retries internos declarados
desconocidos. La corrección MCP Claude `cli-3` está verificada offline y el smoke
posterior acepta MCP vacío, pero se detiene en autenticación Claude con terminal
de error. El diagnóstico en lectura observó la dependencia de USER; la corrección
offline del smoke ya valida USER contra el UID local, sin heredar credenciales.
El smoke posterior autorizado con USER completó planificador Codex, ejecutor Claude
y revisor Codex: terminal/exit 0/JSON en los tres, sin herramientas ni cambios.
H2.4 (Git, worktree por tarea y commit determinista conciliable) está completado
offline: ver [entrega y límites](docs/discovery/H2.4_GIT.md); API/UI añadidas en la salida H2, sin CLI.
H2.5 (vista previa, copia consistente, activación reanudable, exclusión por marcador
y reversión) está completado offline: ver [entrega y límites](docs/discovery/H2.5_MIGRATION.md).
La API gestionada local (proyectos registrados en el servidor, supervisor opt-in,
idempotencia, versiones y guardia Host/Origin/CSRF) está completada offline: ver
[entrega y límites](docs/discovery/H2_EXIT_API.md). La UI gestionada local está
completada offline; [demo, verificación y límites](docs/discovery/H2_EXIT_UI.md).
H4.1–H4.3 y exportación mecánica completados offline (D035–D038); siguiente tarea: H5.1 importación JUnit, sin iniciar. Ver [corrección y límites](docs/discovery/H2.3_MCP_FIX.md)
y [resultado real cli-3](docs/discovery/H2.3_SMOKE_CLI3.md). El consentimiento
terminó al fallo; otro smoke requiere propuesta y autorización específicas.
Ver [corrección del entorno](docs/discovery/H2.3_ENV_FIX.md) y
[propuesta conservada](docs/discovery/H2.3_ENV_SMOKE_PROPOSAL.md) y
[resultado completo](docs/discovery/H2.3_ENV_SMOKE.md). Este éxito acredita el
transporte, sin aceptación/commit de producto; los locks de smokes anteriores
siguen conservados. La autorización cubrió una ejecución, sin relanzamiento.


## Importación legacy de lectura

Migrar con el servicio detenido antes de importar; el esquema actual es
`0013_bootstrap`. Comandos comprobados desde la raíz, con datos sintéticos:

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


## UI gestionada y demo offline

«Proyectos gestionados» muestra los proyectos registrados por el servidor y el
supervisor; permite migrar, encolar contratos, consultar diff/tests/review,
confirmar commits y recuperar jobs en cuarentena con evidencia explícita.
Sin configuración del servidor no hay proyectos ni proveedores activos.

La [guía de demo sintética](docs/discovery/H2_EXIT_UI.md) prepara Git/SQLite
independientes con `examples.managed_demo:build` y permite recorrer COMMITTED,
reinicio, cuarentena y migración. No requiere modelos ni suscripciones.
La UI conserva envíos inciertos en la pestaña y solo los repite por acción
explícita; un 409 muestra diagnóstico y recarga el estado. Las evidencias del run
proceden del historial congelado, no de una recaptura del checkout.

Regresión del cliente: `node --test frontend/tests/managed-api.test.mjs`.
La sesión local sigue pendiente; Host/Origin/CSRF se aplican a la API gestionada
y a las mutaciones H0/H1 (no a sus lecturas). COMMITTED es un checkpoint, no integración ni cierre de fase.

## Prompts versionados (H3.1)

Tras migrar con el servicio detenido (`alembic upgrade head`), abrir un proyecto
registrado en **Proyectos gestionados → Prompts versionados**. Elegir ámbito y
plantilla, validar variables y guardar una nueva versión borrador. Comparar las
versiones antes de activar con motivo y confirmación. Rollback copia la versión
seleccionada a otro borrador; exige activación separada. Perfil/base pueden afectar
a otros proyectos que los hereden; el override de proyecto prevalece.

Las activaciones afectan a intentos posteriores, conservando las peticiones y
resultados previos. Al reanudar un run detenido se conserva su catálogo congelado.
El editor no concede permisos. El descubrimiento de bootstrap usa `bootstrap-project`
desde H4.2; la plantilla documental se versiona con el paquete. La evaluación de
fases usa `close-phase` desde H3.3. [Contrato, pruebas y límites](docs/discovery/H3.1_PROMPTS.md).

H3.2 incorpora solicitudes de permisos por categoría con caducidad, huella y
auditoría en la UI gestionada. Conceder no lanza trabajo: se aplica al siguiente
intento explícito dentro de la autoridad congelada del servidor. Revalidar no
repite el ejecutor, tampoco ante REVISE. El adaptador actual es `cli-4`; el éxito
del smoke D025 sigue siendo evidencia histórica de `cli-3`, sin autorizar consumo
nuevo. Alcance y configuración en [H3.2](docs/discovery/H3.2_PERMISSIONS.md).

H3.3 añade fases a la UI gestionada: definición congelada, preguntas bloqueantes,
comprobación como job (puertas deterministas y evaluación `close-phase`), READY
ligado al contenido exacto, reconciliación de documentos por hash y cierre con
autorización propia que solo crea un tag ligero declarado, sin editar documentos.
El lote es una autorización distinta que no comprueba ni cierra. Las operaciones
de fase exigen escritor Git configurado. [Contrato y límites](docs/discovery/H3.3_PHASES.md).

H3.4 añade el lote desatendido. Con autorización explícita, el supervisor encadena
tarea → commit de contenido exacto → siguiente tarea y se detiene en el primer
bloqueo. Nunca comprueba ni cierra la fase. También añade enmiendas versionadas de
la definición y abandono explícito. El tag de cierre puede ser anotado
(`ManagedProject.tag_kind`) con id determinista. La reconciliación con agente es
una tarea normal limitada a los documentos de la fase, que se adoptan por hash tras
su commit. [Contrato y límites](docs/discovery/H3.4_PHASE_ADJUSTMENTS.md).

H4.1 añade el chat contextual. Cada mensaje es un turno nuevo de solo lectura (rol
`chat`, Codex) con el contexto congelado al encolarlo: fase, documentos, runs y
turnos anteriores. La salida tiene un esquema fijo, sin fallback ni reintento. Una
propuesta solo crea una tarea normal (planificador, ejecutor, revisión y commit)
tras una confirmación explícita del hash mostrado. [Contrato y límites](docs/discovery/H4.1_CHAT.md).

La exportación mecánica (D036) se previsualiza en Documentos de la fase y se
confirma por el diff exacto. Genera bloques delimitados en STATE/NEXT_STEPS desde
SQLite, conserva la prosa, detecta deriva externa y crea un commit Git conciliable
antes de adoptar los hashes. El cierre sigue separado; exportar no mueve tags.
Ante una caída, confirmar primero el escritor detenido y volver a previsualizar
la fase permite conciliar la misma intención, sin duplicar commits ni invocar
agentes. [Protocolo, API y límites](docs/discovery/STATE_EXPORT.md).

## Bootstrap guiado (H4.2)

Migrar con el servicio detenido a `0013_bootstrap`. Registrar en el servidor una
carpeta **existente y vacía**, con su `ProjectContext`, versiones, perfil/política y
`ManagedProject(..., bootstrap_enabled=True)`. Se exige una `commit_factory` con
`GitWorkspace`; los puertos de agentes solo son necesarios para la propuesta
opcional y para ejecutar después la primera tarea. No hay rutas arbitrarias del
cliente ni efectos al cargar la configuración.

En **Proyectos gestionados → Crear proyecto desde cero**: completar el brief,
solicitar si se desea una propuesta Codex de solo lectura, registrar las decisiones
de alcance/arquitectura y revisar los documentos/fase/tarea. Confirmar el preview
con motivo crea un job y commit raíz, y adopta la primera fase en SQLite. La primera
tarea documental se encola por una acción propia y sigue el motor/revisión/commit
normales. Carpeta con contenido → flujo de importación, sin sobrescribir.
Ante caída, confirmar el escritor detenido en sus jobs y reconfirmar el preview
para conciliar el mismo run/commit. No ejecuta preparación ni instala un stack.
[Contrato, verificaciones y límites](docs/discovery/H4.2_BOOTSTRAP.md).

Demo opt-in, exclusivamente sintética, con dos destinos (`empty` y `existing`):

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python -m examples.bootstrap_demo /private/tmp/NEW-bootstrap-demo
HARNESS_DATABASE_URL=sqlite:////private/tmp/NEW-bootstrap-demo/index.sqlite3 UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline alembic upgrade head
HARNESS_BOOTSTRAP_DEMO_ROOT=/private/tmp/NEW-bootstrap-demo HARNESS_MANAGED_CONFIG=examples.bootstrap_demo:build HARNESS_DATABASE_URL=sqlite:////private/tmp/NEW-bootstrap-demo/index.sqlite3 UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline uvicorn harness_local.api.app:create_app --factory --host 127.0.0.1 --port 8022 --workers 1
```

El directorio debe ser nuevo. Los tres comandos se verificaron con una raíz temporal
nueva equivalente. La SQLite y el registro de llamadas falsas están fuera de ambos
destinos. La demo nunca conecta proveedores ni admite un checkout real existente.
