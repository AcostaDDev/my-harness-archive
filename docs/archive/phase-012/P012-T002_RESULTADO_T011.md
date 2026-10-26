# P012-T002 — Resultado real tras T011

Operación: **2026-10-24**, servicio detenido a las **18:59:32 UTC**. Cierre documental: **2026-10-25**.
**Estado: T002 completada con evidencia acumulada; T003/T004 no autorizadas.**
Base del producto: `500a783`; propuesta confirmada en `cc2ef5d` mediante **«Autorizo.»**.
[Propuesta, consentimiento, preparación y hashes](P012-T002_PROPUESTA_T011.md),
[decisión D198](../DECISIONS.md#d198--p012-t002-tarea-real-committed-con-perfil-declarado-v8).

## 1. Resultado y procedencia

Run **`e3fa4ae6…`**, proyecto **p012-b-t010**, tarea **P001-T001**, fase **P001 ACTIVE**.
Plan Claude → ejecución Codex → formateador nativo → seis validaciones → revisión **ACCEPT** → confirmación
UI del contenido exacto → **COMMITTED** en **`6f021211b307f369f23e2efd76bf0b48e6577c60`**.
Una ejecución, revisión 0, **cero correcciones**, sin revalidación o reparación manual.

| Criterio T002 | Evidencia y alcance |
|---|---|
| Wheel instalado fuera del checkout, inicialización/preflight/servicio | Inicialización en el tramo original; base conservada. Producto actual en dist-t011/venv-t011: build/verificador/instalación offline, SHA256SUMS, preflight y migrate no-op correctos; servicio 8024 y login UI normales. |
| Incorporación B por UI, originales y decisiones inferidas, commit único e idempotencia | Primer B `976b1d1` y reenvío idempotente acreditados en [D191](P012-T002_INCORPORACION_REAL.md); B2 `9808fd9`, 15 originales intactos y doce CAS en [D193](P012-T002_CONTINUACION_T009.md). Esta continuación conserva ambos y registra su clon documental limpio; no presenta ese registro como una tercera B. |
| Tarea planificada por agente y perfil declarado hasta COMMITTED | Run `e3fa4ae6…`, seis validaciones/JUnit correctas, diff de tres rutas aceptado y único commit de tarea `6f02121`. CLI identificadas por intento y composición v8 con formateador. |
| Evidencia saneada, presupuesto y parada | Nuevo 2 Claude/1 Codex; acumulado T002 9/12 y 3/3. Servicio detenido, 11 jobs DONE, 12 procesos STOPPED, cero locks; originales anteriores conservados. |

La incorporación B y su idempotencia conservan la procedencia de los tramos anteriores; no se repiten con el
wheel nuevo ni se atribuyen a esta continuación. Los cambios T010/T011 quedan acreditados aquí en el recorrido
actual: selección UI de presets v8, carga del perfil declarado y ejecución del formateador antes de validar/revisar.

## 2. Preparación y selecciones efectivas

Guardias iniciales correctas: fuentes/locks/scripts de `500a783`, ocho hashes de herramientas, 17 wheels y lock
Django verificados. Clon existente limpio en `9808fd9`: 28 blobs iguales al manifiesto, 15 originales 0600 y
13 documentos 0644. TOML v8 0600 de hash **`e0e95abb…fbb6db`**, sin modificación. Venv Django conservado;
lock del fixture idéntico al incluido en el wheel nuevo. B/B2/diffs/configuraciones/distribuciones conservados.

Build/verificador/instalación en destinos nuevos correctos, sin red ni builds de dependencias. Wheel SHA-256
**`f22521ff721e79fed2671abfceaf3f035695f3762f7d2765e170b152eacd3201`**. El verificador usa CLI falsas y
acredita miembros/metadatos/licencias/checksums, UI/API/sesión y recorrido instalado, no inferencia real.
Los ocho checks iniciales del clon pasan (dos casos pytest/JUnit); sus 28 archivos versionados siguen intactos.
`migrate` no-op en 0025, sin snapshot ni cambio de bytes SQLite.

Servicio instalado y acceso UI en es/es, sin rechazo cross-site. El formulario corregido muestra presets v8;
se eligen **claude-t010/codex-t010**, perfil **python-django-t010**, composición **django-t010**, bootstrap false
y confianza explícita del fixture sintético. P001 se crea por UI desde los siete criterios literales del ROADMAP,
P001-T001 y documentos por defecto; sin tag ni llamada de incorporación.

Dos commits documentales por editor UI, vista previa/CAS/confirmación: **`60246d5`** (AGENTS: perfil, formateador,
checks acreditados) y **`f4a35ba`** (D006 del operador e índice regenerado). Ambos mensajes automáticos son
`harness: confirm document edit`; los cuerpos D001–D005 siguen inferidos y sin aprobación retroactiva.
Solo cambian esos dos documentos frente al commit B2. Originales y resto de documentos intactos; checkout
limpio y hashes adoptados antes de seleccionar P001-T001 del NEXT_STEPS por CAS, sin notas adicionales.

| Intento | Proveedor/CLI | Selección congelada | Modelo reportado |
|---|---|---|---|
| Plan | Claude Code 2.1.310 | sonnet/low | claude-sonnet-5-5 |
| Ejecución | Codex 0.164.0 | gpt-6-luna/low | No reportado en los metadatos observados |
| Revisión | Claude Code 2.1.310 | sonnet/low | claude-sonnet-5-5 |

Tres intentos COMPLETE/exit 0, `cli-14`; política **`1156d0c9…cc79d5`**, identidad observada por intento.
Compatibilidad condicionada D174 conservada: el éxito de este recorrido no acredita efectos internos de las CLI
ni otras versiones/plataformas. `sonnet` es el alias autorizado; el modelo reportado no se inventa para Codex.

## 3. Diff, formateador y validaciones

Solo las tres rutas del contrato: **catalog/views.py**, **catalog/tests/test_views.py** y
**docs/flows/items-listado.md**. La vista valida `int`, rango 1–20, defecto 5 y error JSON 400 descriptivo.
Tests para defecto con más filas, extremos/límite efectivo, cinco inválidos y espacios/`+5`/`05`; originales
conservados. El flujo se actualiza a implementado. Sin dependencias, modelos, migraciones, ajustes o rutas nuevas.

Formateador registrado en formatting_json: **`ruff format -- catalog/tests/test_views.py catalog/views.py`**,
cwd `.`, timeout 120 s, exit **0**, dos archivos permitidos; salida **«2 files left unchanged»**. Se acredita su
ejecución nativa previa a validación/revisión, sin afirmar que reparara el estilo de este resultado.

| Validación nativa | Resultado |
|---|---|
| pytest --junitxml=.local/junit.xml -q | exit 0; **13 casos JUnit correctos**, XML completo de 1.660 bytes |
| ruff check . | exit 0 |
| ruff format --check . | exit 0 |
| mypy . | exit 0 |
| python manage.py check | exit 0 |
| python manage.py makemigrations --check --dry-run --noinput | exit 0 |

JUnit SHA-256 **`7e51116eeec2b61fac2b2f4281a63852934a5b63bb1223e15e27a34a68ad4e63`**. Un único ciclo,
revisión **ACCEPT**, sin preguntas bloqueantes ni next_prompt. Hallazgo **low** conservado: la referencia de
líneas `catalog/views.py:6-24` en el flujo tiene un desfase de una línea; no bloquea la aceptación. No se corrige
a mano ni se transforma en un intento nuevo.

Diff aceptado SHA-256 **`db6fa9b245b8d7d9f9c10c534bf611ccbc526434673e35f46030e73ed892b3c0`**.
Contraste posterior: hash del diff completo de las tres rutas igual al revisado; bytes versionados iguales a
los del commit sellado/esperado, HEAD `6f02121` y checkout limpio. STATE/NEXT_STEPS del hijo cambian solo por
los bloques mecánicos del commit. El mensaje automático conserva el título literal español del contrato:
`harness: accept P001-T001 - Validar limit en GET /items/`; no se reescribe ese commit del producto.

## 4. Presupuesto, parada y conservación

Nuevo: **2 Claude + 1 Codex**, sin fallback, ampliación de permisos, correcciones o turnos extra. Acumulado
T002: **Claude 9/12, Codex 3/3**. Los saldos no habilitan otro intento, chat o siguiente tramo.
Run creado **18:56:19 UTC**, commit **18:58:20 UTC** del 24 de octubre; operación dentro de las cuatro horas.

Servicio detenido con SIGINT al proceso propio, salida **0**. La guardia inicial de apagado rechazó la comparación
textual del lanzador: macOS había resuelto el argv0 Python del venv a su binario framework. Antes de señalarlo
se acreditan mismo PID/hora de inicio y argumentos exactos del servicio instalado; no se señala un PID histórico.
Puerto sin listener, clave eliminada, **11 jobs DONE, 12 procesos STOPPED y 0 locks**.

Copias de consulta SQLite/WAL/SHM antes/después: integridad correcta, esquema 0025; **las 13.785 filas previas
son idénticas por todas sus columnas**, sin borrar ni modificar ninguna. Se añaden **1.136 filas** normales de
registro/fase/dos ediciones/tarea/commit/evidencia/métricas: **14.921 filas** finales, excluidas sqlite_*.
B/B2, sus dos diffs, TOML y distribuciones anteriores conservan SHA-256 y modos. No se toca configuración global
ni P009/ReferenceProject; no se crean tags/remotos ni se publica. P001 del clon queda ACTIVE y no se ejecuta T003/T004.
Resumen de conservación final generado a las **19:00:45 UTC**, dentro del techo de cuatro horas desde las 18:51.

Evidencia privada: `state/operator/t011-*` (manifiestos, logs, historia y diff, resumen final y captura
`t011-task-committed.png`), copias `tmp/t011-{before,after}-db`, dist-t011/venv-t011 y clon conservados.
No se copian SQLite, sesiones, prompts o streams completos al repositorio. La captura muestra el resultado
antes de apagar el servicio; no implica que se mantenga en funcionamiento.

## 5. Cierre y siguiente paso

T002 cumple sus cuatro criterios con la procedencia acumulada de la matriz; las dos tareas anteriores siguen
REVISION_LIMIT sin reparación. El éxito no prueba la causa del truncamiento inicial ni valida comparativamente
modelos. T010/T011 conservan sus regresiones offline, ahora complementadas por este recorrido real.

Siguiente tarea: **T003**, concretar/revisar propuesta de chat y backup/restauración de consulta sobre el proyecto
exitoso p012-b-t010 y esta base, según T001. Requiere consentimiento propio antes de iniciar servicio o modelos;
el cierre de T002 no lo concede. T004 también sigue pendiente y sin autorización. Baseline pública/candidato
pendientes de T005, sin adelantar su alcance ni la apertura de P012.

Se actualizan STATE, NEXT_STEPS, ROADMAP y D198. Sin cambios de producto, modelos, migraciones, API o flujo
implementado en my_harness; diagramas y flujos existentes no necesitan cambios. Sin repetir suites de producto,
tipos/build independientes o Alembic: el build/verificador del wheel, preflight y validaciones del tramo ya
aportan la evidencia pertinente.

Comprobación documental final correcta: parsers del producto con **12 fases, 7 criterios P012, 11 tareas y
198 decisiones**, **616 enlaces/anclas relativos** en los seis Markdown de la entrega y presupuestos
STATE/base/NEXT_STEPS **15.274/24.576**, **9.171/12.288**, **26.899/49.152 bytes**. Cuerpos D001–D197 y
secciones originales 1–6 de la propuesta conservados por bytes; archivo histórico, documentación pública y
producto sin cambios. Contraste de evidencia privada: seis validaciones exit 0, 13 casos JUnit y estado final
COMMITTED/detenido. Diff revisado y `git diff --check` correcto. Checkout de desarrollo solo con estos documentos.
