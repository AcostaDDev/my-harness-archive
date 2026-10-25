# P012 — Validación real previa a la apertura pública

Objetivo y criterios en [ROADMAP](ROADMAP.md#p012--validación-real-previa-a-la-apertura-pública).
Decisión: [D183](DECISIONS.md#d183--p012-validación-real-previa-a-la-apertura-pública).

**Estado:** T001, **T002**, T008, T009, T010, T011 y T012 completadas (D198/D202); T003–T007 pendientes,
doce tareas en total. T003 parcial; T012 implementada y verificada offline según D201/D202.
T002 completada con evidencia acumulada: dos B COMMITTED e idempotencia anteriores, y continuación tras T011
autorizada/ejecutada hasta tarea **`e3fa4ae6…` COMMITTED `6f021211b307`** con perfil/formateador v8, seis
validaciones y **13 casos JUnit** correctos. Cero correcciones; nuevo 2 Claude/1 Codex, acumulado T002
**Claude 9/12, Codex 3/3**. Servicio detenido, **11 DONE/12 STOPPED/0 locks**, puerto cerrado/clave retirada;
**13.785 filas previas idénticas**, 1.136 filas normales nuevas. B/B2/diffs/TOML/distribuciones conservados.
Operación del 2026-10-24; cierre documental del 25. Ningún resultado fallido se repara, formatea o revalida.
**T003 ejecutada y detenida** (D200): [resultado real](phase/P012-T003_CHAT_BACKUP_REAL.md), dos turnos ANSWERED,
`/estado` sin modelo y propuesta confirmada con copia TOML supervisor=false. P001-T002/run `d235e9d5…` QUEUED
sin intentos/lock; backup/restauración y consulta HTTP iguales, mutación rechazada 409. UI sin página para run
sin proyecto compuesto; D040 define API y el guion había añadido UI. Consumo 2/3 Claude y 0/0 Codex; 13 DONE/
1 QUEUED/14 STOPPED/0 locks, puertos cerrados/claves retiradas, 14.921 filas previas intactas y 16.798 finales.
HITL **«Planificar vista UI Aparte»** (D201): mantener T003 parcial y añadir
[T012](#p012-t012--vista-ui-de-runs-en-copias-de-consulta), completada offline (D202). **Siguiente:**
consentimiento para la [continuación T003 solo UI](phase/P012-T012_VISTA_CONSULTA.md#4-propuesta-de-continuación-t003-solo-ui-sin-autorizar),
con wheel corregido en destinos nuevos y cero llamadas. Sin repetir chat/aceptación/backup o consumir saldo. T004 sin
autorización y con propuesta de arranque pendiente que respete el job QUEUED; no reactivar esa base (D199).
El resultado T002 y los saldos no habilitan otro tramo, corrección o reintento.
P001–P011 siguen cerradas; la apertura del [expediente de P011](archive/phase-011/P011_EXPEDIENTE_APERTURA.md)
queda aplazada hasta el cierre de P012 y su candidato se sustituye por el que prepare T005.

## Restricciones compartidas

- Una tarea acotada cada vez, desarrollo manual con Codex o Claude Code, decisiones en DECISIONS y artefactos por
  tarea en `docs/phase/`. Registrar base, comandos, resultados, omisiones y llamadas reales al ejecutar.
- Pareja elegida por el usuario (D183): **revisor Claude Code y ejecutor Codex, ambos con modelos ligeros**. La
  cuota de Claude es el recurso escaso: casi todas las llamadas son del revisor (conversaciones, planes, revisiones,
  chat y evaluación de fase), así que T001 fija techos separados por proveedor. Sin fallback de modelo ni de pareja.
- Cada tramo real (T002, T003, T004) exige autorización explícita del usuario sobre la propuesta confirmada en T001.
  Planificar no la concede. Sin red salvo el tráfico de las CLI elegidas con sus proveedores; una caché incompleta
  obliga a parar, y descargar exige su propia autorización con lista y hashes.
- No operar este repositorio con el harness: el producto se construye desde aquí y se instala en un área privada
  fuera de cualquier checkout. Fixtures sintéticos, sin datos privados, credenciales, remotos ni copias del Django
  de P009 o de ReferenceProject. No modificar la configuración global (CLI, Git, npm, shell).
- Parada al primer fallo de proveedor, esquema, timeout, validación, permisos, CAS, hashes o cuarentena. Un defecto
  del producto se acota en una tarea de corrección nueva (T008 en adelante) con tests sintéticos; no se corrige a mano
  el resultado de un agente, ni se editan SQLite/TOML para desbloquear, ni se relanza sin consentimiento nuevo.
- Un resultado parcial declara qué afirmación quedó acreditada y cuál no; nunca se resume como validación completa.
  Streams, prompts completos, tokens de sesión y SQLite quedan en el área privada; en `docs/phase/` solo evidencia
  saneada (versiones, hashes, ids abreviados, número de llamadas, comandos y resultados).
- El candidato `74cc9141…ea71` de P011 deja de ser el que se publica en cuanto cambie el README o `docs/public/`.
  Sin commits salvo petición del usuario; sin tag en este repositorio, push, creación de repositorio remoto,
  Release ni publicación. El cierre del hijo de T004 conserva su tag propio, bajo autorización de ese tramo.

## P012-T001 — Propuesta operativa y consentimiento

**Estado:** completada documentalmente y confirmada por el usuario el 2026-10-24 (D184). **Depende de:** D183.
**Objetivo:** Concretar y someter a confirmación los parámetros de los tres tramos reales, sin ejecutar ninguno.
**Alcance:** área, fixtures, construcción e instalación, configuración, modelos, presupuesto, paradas y evidencia.
Parte de la [propuesta de P010-T008](archive/phase-010/P010-T008_PROPUESTA_VALIDACION_REAL.md) §§2–5 sin el flujo A,
retirado por D155/D161, y la amplía con chat, backup/restauración y receta TypeScript v2.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Área privada nueva elegida por el usuario, fuera de checkouts y sin enlaces (`dist/`, `venv/`, `config/`,
  `state/`, `tmp/`, `command-home/`, `wheels/`, raíz de proyectos); puerto libre distinto de 8013/5173.
- Commit base del wheel, comandos de construcción/verificación/instalación offline y hashes esperados. Toolchain y
  versiones comprobadas solo con `--version`: Codex **0.164.0** (elección HITL D184), Claude Code 2.1.310, ambas
  posteriores a los mínimos y con compatibilidad condicionada; Python 3.14.4 para harness/build y 3.13.13 para B,
  Node 24.15.0, npm 11.12.1, uv 0.12.19; rutas y hashes de las CLI.
- Revisor Claude con modelo ligero y esfuerzo concretos (propuesta inicial `sonnet`, esfuerzo bajo/medio) y
  ejecutor Codex con un único modelo ligero de su catálogo en `executor_mode = "catalog"` y esfuerzo bajo; los
  nombres se toman de la documentación o ayuda de las CLI, sin invocar modelos.
- `local-config-7` privado (chmod 600): pareja, composiciones Django (perfil declarado `[profiles.python-django]`
  del ejemplo) y TypeScript web con receta v2, `registration.roots`, autor Git sintético y entornos con HOME/PATH
  explícitos. Se revisa entero antes de usarlo; `check-config --preflight` sin invocar modelos.
- Fixture B: Django mínimo sintético con modelo, migración, ruta/vista, tests y configuración de ruff/mypy, con las
  seis validaciones en verde antes de registrarlo, y wheelhouse propio verificado contra el lock empaquetado.
  Fixture TypeScript: caché npm propia con los paquetes de la receta (`typescript@5.9.3`) o parada.
- Techo de llamadas por tramo y por proveedor (orientativo: T002 ≈ 12 Claude + 3 Codex; T003 ≈ 3 Claude; T004 ≈ 12
  Claude + 3 Codex), techo de tiempo por sesión, condiciones de parada, recuperación tras caída y limpieza.
- Decisión HITL registrada: el usuario confirma la propuesta (o la ajusta) antes de T002.

**Validación:** contraste con D095/D119/D143/D151/D168/D173/D174, el ejemplo de configuración y los flujos; enlaces.
**Entregables:** [propuesta confirmada](phase/P012-T001_PROPUESTA_OPERATIVA.md) y D184. HITL: «Confirmar T001
con estos parámetros; sin autorizar tramos». Wheel/cachés/fixtures/preflight aún sin ejecutar: punto de control
offline de T002 aceptado por el usuario, antes de proveedores; no se acredita su resultado en esta tarea documental.

## P012-T002 — Instalación, incorporación B y perfil declarado con proveedores reales

**Estado:** completada con evidencia acumulada (D198); operación 2026-10-24, cierre documental 2026-10-25.
**Depende de:** T001 confirmada, T008 corregida (D187), T009 completada (D192), ampliación T010 (D194) y T011 (D196).
[Continuación tras T011](phase/P012-T002_PROPUESTA_T011.md) autorizada por HITL **«Autorizo.»** (D198): base
`500a783`, wheel/venv nuevos y clon/TOML t010 conservados. Build/verificador/instalación, preflight/ocho checks,
migrate no-op y UI v8 correctos; registro/P001 y dos commits documentales por UI. Run `e3fa4ae6…` COMMITTED:
plan Claude, ejecución Codex, formateador nativo sobre dos archivos (exit 0, sin cambios), seis validaciones/
13 casos JUnit y ACCEPT, con un hallazgo low de referencia de línea conservado. Cero correcciones; total
Claude 9/12, Codex 3/3. Servicio detenido, 11 DONE/12 STOPPED/0 locks; evidencias anteriores intactas.
Los dos B y la idempotencia conservan procedencia D191/D193; no se repiten ni reparan los dos runs REVISION_LIMIT.
T003/T004 pendientes y sin autorización. [Resultado y matriz](phase/P012-T002_RESULTADO_T011.md).
**Objetivo:** Acreditar con la versión actual el flujo básico y la incorporación de un repositorio existente con
el perfil declarado D095.
**Alcance:** wheel construido e instalado en el área, servicio, fixture B, conversación de incorporación,
confirmación de documentos y perfil, y una tarea hasta COMMITTED.
**Rutas permitidas:** `docs/**` en este repositorio; el área y el fixture privados según T001.
**Criterios de aceptación:**

- Wheel del commit base construido y verificado (`build_distribution.py`, `check_distribution.py`), instalado por
  hashes fuera del checkout; `init-db`, `check-config --preflight` y `serve` en el puerto elegido.
- Incorporación B desde la UI: el inventario cita modelo, ruta y tests con procedencia; el revisor redacta los
  documentos D088 y marca las decisiones inferidas; las preguntas no deducibles pasan por HITL. Un único commit
  documental, código del fixture intacto por bytes y modos, P001 ACTIVE; reenviar la confirmación no duplica efectos.
- Una tarea acotada (validación de entrada en la vista existente y sus tests, sin dependencias, modelos ni
  migraciones) con planificación `agent`: plan, ejecución Codex, seis validaciones con JUnit, revisión y COMMITTED,
  usando exclusivamente el perfil declarado. Diff aceptado, commit único y CLI identificadas por intento.
- Evidencia saneada con llamadas por proveedor frente al techo; servicio detenido o mantenido según T003.

**Validación:** build/verificador/instalación del wheel, preflight real, ocho checks iniciales, seis validaciones
del run/13 JUnit, contraste diff/commit, conservación SQLite/manifiestos y checks documentales. Sin repetir suites
completas del producto al no cambiar código en esta tarea.
**Entregables:** [registro inicial](phase/P012-T002_INCORPORACION_REAL.md),
[continuación T009 y nueva parada](phase/P012-T002_CONTINUACION_T009.md),
[propuesta/ejecución tras T010](phase/P012-T002_PROPUESTA_T010.md),
[propuesta/ejecución tras T011](phase/P012-T002_PROPUESTA_T011.md),
[resultado final y matriz](phase/P012-T002_RESULTADO_T011.md),
[transformador puro de configuración](phase/P012-T002_CONFIG_T010.py),
[lista de la primera parada](phase/P012-T002_WHEELS_FALTANTES.lock) y
[manifiesto de 17 wheels](phase/P012-T002_WHEELS_VERIFICADOS.sha256).
Preparación e instalación corregidas `6efbd82`, preflight CLI y checks iniciales acreditados. Primer B
**`976b1d1` COMMITTED**, reenvío idempotente sin duplicados, tarea **`b94eedef…` REVISION_LIMIT** con tres archivos
vacíos (D191). T009 completa el diagnóstico offline sin demostrar la causa (D192).
Continuación autorizada (D193): registro **`p012-b-t009`**, incorporación **`9808fd9` COMMITTED**, código original
intacto, doce propuestas APPLIED. Run tarea **`f98b16d9…` REVISION_LIMIT**: vista/tests/flujo con contenido,
**13 casos JUnit aprobados**, mypy/Django correctos; Ruff **E501** (dos líneas) y formato exit 1. Revisor REVISE,
sin aceptación, reparación o commit de tarea. **7 jobs DONE, 9 procesos STOPPED, 0 locks**, puerto cerrado y clave
eliminada; Claude **7/12**, Codex **2/3**. Comparación de copias de base: **8186 filas previas intactas**.
B/B2, ambos diffs, TOML original, distribuciones e historiales conservados. Propuesta T010 ya concretada y
autorizada/ejecutada hasta el bloqueo de presets UI (D195), sin llamadas adicionales; servicio detenido y 13.785
filas anteriores idénticas. Tras T011, continuación autorizada D198 hasta `6f02121` COMMITTED, con perfil
declarado/formateador v8 y selector UI acreditados. Nuevo 2/1, acumulado 9/3, cero correcciones; servicio detenido,
11 DONE/12 STOPPED/0 locks, 13.785 filas anteriores idénticas y B/B2 intactos. Los cuatro criterios T002 cumplen
con la procedencia acumulada de la matriz, sin declarar una tercera B ni reparar los resultados fallidos.

## P012-T003 — Chat, backup y restauración sobre el proyecto real

**Estado:** parcial, autorizada/ejecutada/detenida el 2026-10-25; chat y backup/consulta HTTP acreditados (D200).
HITL D201 elige planificar vista UI aparte, sin cerrar con solo API. **Depende de:** T002; T012 para completar
consulta UI y consentimiento explícito nuevo antes de su continuación.
**Objetivo:** Acreditar el chat con el revisor real y el backup/restauración de consulta de una base con runs reales.
**Alcance:** proyecto B de T002 y la base del área.
**Rutas permitidas:** `docs/**` en este repositorio; el área privada según T001.
**Criterios de aceptación:**

- Chat sobre la instantánea de HEAD: al menos una respuesta del revisor coherente con el código y los documentos,
  un comando determinista y una propuesta convertida en tarea confirmada, sin ejecutarla ni tomar el lock.
  Según HITL D199, aceptar solo tras detener el servicio del chat y arrancar con una copia TOML supervisor=false:
  la tarea queda QUEUED, cero intentos/preparaciones/comandos y sin lock. No reactivar esa base antes de revisar T004.
- Backup de la base con el producto, integridad comprobada y restauración de consulta que muestra los runs, el diff
  y las métricas de T002 sin volver a ejecutar nada; base operativa intacta.
  D201 mantiene pendiente observar por UI detalle/commit, diff, JUnit y métricas tras T012. Verificación posterior
  de consulta únicamente con consentimiento nuevo, cero llamadas y sin repetir evidencia ya acreditada.
- Llamadas por proveedor frente al techo y servicio detenido al terminar, sin locks ni jobs activos.
  Distinguir el job QUEUED conservado de los ACTIVE: no presentarlo como terminado o inexistente.

**Validación:** la propia del tramo.
**Entregables:** [propuesta y comprobaciones previas](phase/P012-T003_PROPUESTA_CHAT_BACKUP.md);
[resultado real, conservación y límite UI](phase/P012-T003_CHAT_BACKUP_REAL.md).
Consentimiento «Continúa.» al guion del commit bcbf977; parada por origin_rejected y reanudación nativa
autorizada por HITL, sin cambiar guardias o techos. Dos turnos ANSWERED, HEAD 6f02121 sin cambios, `/estado`
sin modelo; propuesta ACCEPTED por hash/versión y P001-T002 QUEUED con supervisor=false, cero intentos/preparaciones.
Cuatro comandos de backup/restauración correctos; 42 artefactos/13 runs, lecturas HTTP de runs/diff/13 JUnit/
métricas iguales y POST inerte rechazado 409. Consulta UI sin página por ausencia de proyecto compuesto:
D040 define API, el guion pedía UI adicional. HITL D201: **«Planificar vista UI Aparte»**; T003 permanece parcial
y T012 queda como siguiente trabajo offline. [Plan y continuación posterior](phase/P012-T012_PLAN_VISTA_CONSULTA.md).
Consumo **2/3 Claude, 0/0 Codex**, dentro de dos horas; servicio detenido, **13 DONE/1 QUEUED/14 STOPPED/0 locks**,
puertos cerrados y claves retiradas. **14.921 filas previas idénticas**, 1.877 nuevas, **16.798 finales** iguales
en fuente/bundle/restauración; SHA-256 de la base intacto tras backup/consulta, fixtures y evidencias conservados.
Sin cambio de producto ni ejecución de la tarea vinculada; no se repiten suites válidas o validaciones del fixture.

## P012-T004 — Proyecto TypeScript web nuevo con receta v2 en español

**Estado:** pendiente. **Depende de:** T002 y autorización explícita del tramo.
**Guardia D199:** revisar su propuesta de arranque antes de operar: T003 prevé conservar una tarea QUEUED.
No arrancar el supervisor sobre esa base ni ejecutar la tarea pendiente con el consentimiento de T004.
**Objetivo:** Acreditar con proveedores reales la creación desde cero con la receta TypeScript web v2, el idioma
de trabajo español y el cierre de una fase.
**Alcance:** carpeta padre del área, definición conversacional, preparación con la caché npm, una tarea, READY y
cierre de P001 del hijo.
**Rutas permitidas:** `docs/**` en este repositorio; el área privada según T001.
**Criterios de aceptación:**

- Creación desde la UI con trabajo `es` (visual en el que elija el usuario): conversación de definición con el
  revisor real, borradores en disco, documentos D088 generados en español y receta `typescript-web-recipe-2` con
  el idioma sellado en plan y recibo; `npm ci` desde la caché propia y validaciones del perfil antes del commit técnico.
- Una tarea acotada del hijo hasta COMMITTED con la pareja elegida; código y documentos de la tarea en español.
- READY check y cierre autorizado de P001 del hijo con archivo y apertura de la siguiente fase sin tareas.
- Llamadas por proveedor frente al techo, servicio detenido y área conservada para revisión.

**Validación:** la propia del tramo.
**Entregables:** `docs/phase/P012-T004_TYPESCRIPT_REAL.md`.

## P012-T005 — Alcance público y candidato actualizados

**Estado:** pendiente. **Depende de:** T002–T004, T012 y las correcciones que hayan generado.
**Objetivo:** Reflejar en la documentación pública lo acreditado y preparar el candidato que sustituye al de P011.
**Alcance:** README/README.es, `docs/public/`, ROADMAP/STATE privados, candidato, paquete y suites.
**Rutas permitidas:** `README.md`, `README.es.md`, `CHANGELOG.md`, `docs/**`.
**Criterios de aceptación:**

- Tabla «Supported scope and limits» y su versión española con la evidencia real de P012 por fila, sin ampliarla
  más allá de lo acreditado. La fila de las cuatro combinaciones distingue la evidencia anterior a `cli-14` de la
  pareja validada en P012. Nota de versiones CLI con las de P012.
- `docs/public/`: retirar de «Known gaps» del ROADMAP lo acreditado y actualizar STATE, ARCHITECTURE (límites) y
  SPECIFICATION; una decisión pública equivalente si procede, sin publicar las privadas.
- Candidato regenerado con una copia del script de T015 en `docs/phase/`, nuevo manifiesto público y diff de lista
  frente al de P011; `my_harness_dist` se sustituye solo con autorización del usuario.
- Suites de AGENTS, `check_distribution` y comprobador de la documentación pública en verde sobre el candidato.

**Validación:** suites completas de AGENTS, build y verificación del paquete, enlaces.
**Entregables:** `docs/phase/P012-T005_CANDIDATO.md` y manifiestos.

## P012-T006 — Revisión de salida y expediente de apertura actualizado

**Estado:** pendiente. **Depende de:** T001–T005 y correcciones.
**Objetivo:** Dictaminar los criterios de P012 y dejar listo el expediente de apertura con el candidato nuevo.
**Alcance:** matriz por criterio con evidencia, límites y omisiones; expediente nuevo que sustituye al archivado.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Cada criterio con evidencia y procedencia; los resultados parciales se declaran como tales. Sin tareas de
  corrección pendientes.
- Expediente nuevo con manifiesto y hashes del candidato de T005 y los pasos remotos de P011 ajustados, sin
  ejecutar ninguno; el expediente archivado de P011 no se reescribe.

**Validación:** contraste documental y de hashes; sin repetir suites válidas ni operaciones reales.
**Entregables:** `docs/phase/P012_REVIEW.md` y `docs/phase/P012_EXPEDIENTE_APERTURA.md`.

## P012-T007 — Cierre documental de P012

**Estado:** pendiente. **Depende de:** T006 con dictamen favorable.
**Objetivo:** Archivar P012 y dejar la apertura como siguiente paso del usuario.
**Alcance:** resumen, revisión de cierre, archivo en `docs/archive/phase-012/` y documentos vivos.
**Rutas permitidas:** `docs/**`.
**Criterios de aceptación:**

- Originales conservados por bytes con manifiesto; STATE, NEXT_STEPS, ROADMAP y DECISIONS al día, sin sucesora.
- Cierre manual sin registrar ni ejecutar este repositorio con el harness, sin tag, push ni publicación.

**Validación:** parsers, enlaces, presupuestos y diff documental.
**Entregables:** `docs/archive/phase-012/` con resumen, revisión, originales y registro de cierre.

## P012-T008 — Corregir choices multilínea del preflight CLI

**Estado:** completada el 2026-10-24, implementada y verificada offline (D187). **Depende de:** hallazgo de T002 (D186).
**Objetivo:** Evitar el falso rechazo de valores anunciados en continuaciones de la ayuda sin admitir valores
realmente ausentes ni alterar los controles del transporte.
**Alcance:** lector `unsupported_values`, regresión sintética de listas envueltas y diagnóstico integrado falso;
identidad/política y documentación de la corrección, sin ejecutar CLI o proveedores reales.
**Rutas permitidas:** `src/harness_local/adapters/cli_diagnostics.py`, `tests/product/test_cli_diagnostics.py`,
`tests/product/test_cli_baseline.py`, `tests/product/test_cli_discovery.py`, `tests/fixtures/cli_capabilities/**`
(solo sintéticos), `docs/**`.
**Criterios de aceptación:**

- Una lista explícita `choices`/`possible values` partida en varias líneas se interpreta completa; el caso
  sintético de `dontAsk` en una continuación pasa igual que la misma lista en una línea. Casos LF/CRLF,
  comillas y valores con guiones conservan su comportamiento.
- La lectura queda acotada a la opción/lista correspondiente: no toma valores de otra opción ni de prosa ajena;
  un valor requerido realmente ausente sigue dando `unsupported_values`. Ausencia de lista no inventa evidencia.
- Regresión integrada con ejecutables y ayuda exclusivamente sintéticos: preflight/diagnóstico deja pasar la
  lista envuelta válida y rechaza la lista que excluye el valor. Sin copiar ayuda real a fixtures públicos.
- No se cambian valores requeridos, permisos, flags, mínimos, pareja, modelos, snapshots ni evidencias congeladas.
  La política/identidad derivada se registra según el código vigente, sin simular compatibilidad real nueva.
- T002 sigue parcial y parada; se concreta en la entrega cómo construir/verificar un wheel de base nueva antes
  de pedir consentimiento para reanudar. Sin ejecutar build operativo, preflight con CLI reales, servicio o modelos.

**Validación:** reproducción y tests dirigidos sintéticos de diagnóstico/capacidades; checks documentales y diff.
**Entregables:** [corrección y continuación propuesta](phase/P012-T008_CORRECCION_PREFLIGHT.md), D187.
25 regresiones nuevas y 229 tests dirigidos correctos; sin CLI reales ni nueva operación de T002.

## P012-T009 — Diagnóstico offline del entorno de escritura Codex

**Estado:** completada offline el 2026-10-24 (D192); continuidad elegida por HITL, sin operación autorizada.
**Depende de:** parada real de T002 (D191).
**Objetivo:** Acotar los prerrequisitos de temporales y herramientas del escritor, separando hechos de hipótesis,
y dejar una propuesta concreta y revisable antes de pedir otro intento real.
**Alcance:** intención congelada del ejecutor y errores saneados, TOML aprobado T001, fronteras D059/D068/D174,
composición de validadores y vías de continuidad admitidas por el producto. No presupone defecto del harness.
**Rutas permitidas:** `docs/**`; lectura de evidencia privada de T002, sin alterarla.
**Criterios de aceptación:**

- Contrastar TMPDIR ausente en el entorno congelado del ejecutor, exclusión de `/tmp`, PATH sin venv Django y
  entorno separado de validaciones. Precisar qué demuestra el stream y qué no; no reproducir proveedores reales.
- Propuesta exacta de entorno/temporales para el área, sin cambiar permisos, confianza, red, modelo/esfuerzo,
  configuración global o TOML operativo. Justificarla con documentación/código y comprobaciones puras/sintéticas;
  no atribuir semántica nueva a Codex 0.164.0 sin evidencia.
- Determinar la continuación soportada que conserva el checkout/diff fallido y los jobs congelados, sin reparar
  resultados a mano, editar SQLite o reutilizar un job con configuración distinta. Si exige ampliar alcance o
  elegir entre diseños no resueltos, pasar por HITL antes de decidir.
- Si se acredita un defecto del producto, acotar su corrección con regresiones sintéticas en otra tarea antes de
  reconstruir o relanzar. Si solo falta un prerrequisito operativo, declararlo sin inventar una corrección de código.
- Registrar propuesta de consentimiento posterior con efectos, rutas, presupuesto ya consumido 4 Claude/1 Codex
  y límites de parada; sin iniciar servicio, CLI reales, modelos, revalidaciones o tests del fixture fallido.

**Validación:** contraste documental/código, comprobaciones puras/sintéticas pertinentes, parsers/enlaces/diff;
sin suites completas si no cambia producto, ni operaciones reales.
**Entregables:** [diagnóstico y propuesta elegida](phase/P012-T009_DIAGNOSTICO_ENTORNO_CODEX.md),
[check sintético sin procesos](phase/P012-T009_CHECK_ENVIRONMENT.py) y D192. Once tests dirigidos correctos y
comprobación pura de presets/composición: huellas anteriores conservadas, PATH/TMPDIR nuevos acotados. No se prueba
causa del truncamiento ni defecto de producto. Propuesta B2 desde base sintética inicial, copia TOML con presets y
composición propios, mismo wheel, saldo acumulado 8 Claude/2 Codex; conservar B/diff/jobs. El usuario elige ese diseño
por HITL; falta consentimiento para sus efectos reales. Sin CLI/proveedores reales, servicio o cambios operativos.

## P012-T010 — Habilitar formateador en perfiles declarados

**Estado:** completada offline el 2026-10-24 (D194), tras elección HITL de la alternativa A.
**Depende de:** rechazo Ruff de T002 (D193) y D095/D133.
**Objetivo:** Exponer al operador del perfil declarado el formateador determinista que ya ejecuta el motor,
sin depender de otra corrección del modelo para reproducir el estilo de la herramienta.
**Alcance:** `local-config-8`, carga/inspección del perfil, compatibilidad de registro/CLI/recetas, ejemplo,
regresiones sintéticas y documentación. No es un defecto del motor demostrado.
**Rutas permitidas:** `src/harness_local/services/local_config.py`,
`src/harness_local/services/project_registry.py`, `src/harness_local/recipes/__init__.py`,
`examples/local_config.example.toml`, `tests/product/**` (solo sintéticos), `docs/**`.
**Criterios de aceptación:**

- Solo v8 admite `formatter_argv`/`formatter_paths`, juntos, no vacíos; argv sin shell terminado en `--`, patrones
  relativos únicos, ejecutable mapeado y autorización del perfil obligatoria. `check-config` los muestra si existen.
- Omitir el par conserva comportamiento/hashes efectivos; v1–v7 conservan sus reglas y huellas. V8 mantiene
  detección CLI automática, presets, idiomas y recetas v2 sin modificar implementaciones ligadas a recibos.
- El motor/runner D133 existentes formatean solo archivos del contrato antes de validar/revisar; evidencia y commit
  ligados a esos bytes. Revalidar no formatea. Cambiar el perfil pone en cuarentena jobs antiguos sin efectos.
- Tests de carga, rechazos, huellas, registro/presets y recorrido nativo con herramientas/agentes falsos hasta commit;
  casos del motor de rutas/revalidación conservados. Sin Ruff/CLI/proveedores reales o fixtures privados en tests.
- Ambos resultados reales intactos; sin build operativo, cambio de TOML/SQLite privados, servicios o consumo nuevo.
  Dejar guion de continuación T002 sujeto a revisión/consentimiento, sin ampliar presupuesto o correcciones.

**Validación:** 28 regresiones nuevas, 177 y 106 checks dirigidos, 8 unittest; parsers/enlaces/presupuestos y diff.
Sin frontend/Alembic por no cambiar UI/API/datos; sin validación real o wheel nuevo.
**Entregables:** [alternativas y HITL](phase/P012-T002_PROPUESTA_CONTINUIDAD_RUFF.md),
[implementación, checks y continuación propuesta](phase/P012-T010_FORMATEADOR_DECLARATIVO.md), D194.

## P012-T011 — Conservar selección de presets en la UI con local-config-8

**Estado:** completada offline el 2026-10-24 (D196). **Depende de:** bloqueo UI observado en T002 (D195) y D194.
**Objetivo:** Mostrar la selección de agentes por proyecto de v8 que el backend ya admite, sin operar la pareja
heredada como sustitución silenciosa de los presets elegidos por el usuario.
**Alcance:** formulario compartido de registro/creación/actualización, aviso en/es, regresiones de render y documentos.
**Rutas permitidas:** `frontend/src/pages/Registry.tsx`, `frontend/src/i18n/{en,es}.json`,
`frontend/tests/registry.test.mjs`, `frontend/tests/helpers/tsx.mjs`, `docs/**`.
**Criterios de aceptación:**

- V8 muestra el selector de pareja y los presets admitidos por rol como v5–v7; formatos anteriores/desconocidos
  mantienen el fallback y la ausencia de presets mantiene su aviso. Sin cambiar API, políticas o backend.
- Registro, creación y actualización cubiertos en en/es mediante render real de React, con presets/modelo/esfuerzo
  seleccionados y sin ejecutar efectos o peticiones HTTP. Sin dependencias nuevas ni fixtures privados en tests.
- Checks Node, tipos/build y documentación correctos. Sin reconstruir/instalar otro wheel, relanzar servicio,
  registrar/operar el clon o consumir modelos; próxima continuación T002 con propuesta/consentimiento nuevos.

**Validación:** 8 regresiones y 103 tests Node, TypeScript/build Vite correctos; checks documentales/diff.
Sin suites Python/unittest/Alembic por no cambiar backend o datos, ni QA de navegador de la corrección.
**Entregables:** [defecto, corrección y continuidad propuesta](phase/P012-T011_PRESETS_UI_V8.md), D196.

## P012-T012 — Vista UI de runs en copias de consulta

**Estado:** completada offline el 2026-10-25 (D202), según el plan elegido por HITL D201.
[Entrega y propuesta posterior](phase/P012-T012_VISTA_CONSULTA.md). T003 conserva su estado parcial.
**Depende de:** evidencia parcial de T003 (D200), D040/D144/D145; no requiere cerrar T003 antes de implementar.
**Objetivo:** Consultar en la UI una copia marcada por D040 sin configurar proyectos, acceder al checkout o
habilitar el carril operativo, para poder completar después la verificación UI de T003.
**Alcance:** señal explícita de copia en SupervisorRead; inicio con entrada por id; `/runs/:id` con evidencia,
diff/JUnit/métricas por run; navegación y componentes de solo consulta en en/es; regresiones sintéticas.
**Rutas permitidas:** `src/harness_local/api/schemas.py`, `src/harness_local/services/managed_runtime.py`,
`frontend/src/**` (solo esta vista y extracción compartida necesaria), `frontend/openapi.json`,
`frontend/tests/**`, `tests/product/**` (solo sintéticos), `docs/**`. Sin dependencias o locks nuevos.
**Criterios de aceptación:**

- `SupervisorRead.read_only_archive` procede de la marca persistente; distinguir copias de servicios ordinarios
  sin agentes o con supervisor=false. Tipos/OpenAPI regenerados, sin migración, codec o formato de bundle nuevos.
- Inicio de copia permite abrir por id y `/runs/:id` ofrece página directa/recargable sin proyecto/workspace.
  Conservar resolución canónica y comportamiento sin proyecto del modo normal; no crear registros ficticios.
- Estado/commit, ciclos/diff con hash y páginas, validaciones/casos/original JUnit, jobs/intentos/eventos y
  métricas por `run_id` con procedencia, ausencia distinta de cero y datos incompletos sin inventar resultados.
- Copia claramente identificada, sin montar acciones/permisos/recuperación/ProjectWorkspace o reenvíos pendientes;
  tampoco en rutas operativas directas. Estados históricos conservados y sin polling de ejecución. Guardias
  query_only/409 y ausencia de supervisor/puertos intactas; sin lectura de checkout o historial completo.
- Pruebas backend/React/router en en/es con copias sintéticas incluso sin checkout, estados diversos, respuestas
  con acciones anunciadas y petición pendiente guardada; mismas lecturas/hash y cero efectos. Modo normal conservado.
- Node, tipos/build, pytest dirigido y paridad documental correctos: flujo nuevo de consulta, arquitectura y
  especificación al implementar. No modificar evidencias reales, construir/instalar wheel operativo o arrancar
  servicios/agentes/proveedores en esta tarea offline.
- Entrega deja propuesta concreta de continuación **solo UI** de T003, con código corregido, rutas/hashes/tiempo
  y cero llamadas de modelos; consentimiento nuevo antes de build/instalación/servicio. T003 sigue parcial hasta
  verificar su UI real; T004 conserva la guardia del job QUEUED de D199 y su autorización separada.

**Validación:** 102 tests Python dirigidos, 16 regresiones React/router, 119 tests Node y tipos/build correctos;
misma evidencia en backup/restauración sin checkout, señal explícita y lecturas sin historial, guardias intactas.
Pruebas React con render real y host determinista de hooks; sin QA de navegador o servicios privados.
**Entregables:** [plan conservado](phase/P012-T012_PLAN_VISTA_CONSULTA.md),
[implementación y continuación T003 propuesta](phase/P012-T012_VISTA_CONSULTA.md),
[flujo](flows/backup-consultation.md), OpenAPI/tipos y manifiesto de fuentes. Sin wheel operativo ni llamadas nuevas.
