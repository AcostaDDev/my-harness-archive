# P012 — Validación real previa a la apertura pública

Objetivo y criterios en [ROADMAP](ROADMAP.md#p012--validación-real-previa-a-la-apertura-pública).
Decisión: [D183](DECISIONS.md#d183--p012-validación-real-previa-a-la-apertura-pública).

**Estado:** T001, T008, T009 y **T010** completadas; T002 parcial (D191–D194). Dos incorporaciones B COMMITTED;
última tarea en REVISION_LIMIT por Ruff, 13 tests y mypy/Django correctos. T010, elegida por HITL, habilita
formateador declarativo en `local-config-8`, verificado offline; no reconstruye ni relanza. Servicio detenido,
Claude **7/12**, Codex **2/3**, sin consumo nuevo, 0 locks, 7 jobs DONE y 9 procesos STOPPED. T003–T007 pendientes;
diez tareas en total. Ningún resultado fallido se repara, formatea o revalida.
**Siguiente:** [P012-T002](#p012-t002--instalación-incorporación-b-y-perfil-declarado-con-proveedores-reales),
concretar y revisar la [continuación operativa tras T010](phase/P012-T010_FORMATEADOR_DECLARATIVO.md#5-continuación-operativa-propuesta-todavía-sin-autorizar)
y pedir consentimiento: wheel nuevo, clon limpio del commit documental B2 sin repetir B, perfil v8 con
formateador, registro/fase y una tarea nueva. Cero correcciones, techo 12/3 y saldo 5/1 sin permiso de consumo;
previsión 2 Claude/1 Codex. T010 no autoriza operación real, cambios de configuración privada o reparar B/B2.
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

**Estado:** parcial (D193): dos incorporaciones B COMMITTED; ninguna tarea COMMITTED.
**Depende de:** T001 confirmada, T008 corregida (D187), T009 completada (D192) y ampliación T010 (D194).
Continuación limpia T009 autorizada y ejecutada: fixture `onboarding-b-t009`, copia TOML y presets/composición
propios, mismo wheel y base. Preflight y ocho checks correctos; un turno Claude, doce borradores CAS y B2
COMMITTED. Codex implementa la tarea, pero fallan Ruff check/formato; pytest 13 casos y mypy/Django pasan.
Revisión REVISE y REVISION_LIMIT, cero correcciones. Consumo acumulado **7/2 frente a 12/3**; servicio detenido.
El primer fixture y su fallo de archivos vacíos siguen intactos. T010 habilita el formateador declarativo v8
solo offline; próximo paso: concretar la propuesta operativa y pedir consentimiento nuevo. Sin reparación
manual, revalidación o nuevo intento autorizado.
T003/T004 siguen sin autorización.
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

**Validación:** la propia del tramo; sin suites del producto si no cambia código.
**Entregables:** [registro inicial](phase/P012-T002_INCORPORACION_REAL.md),
[continuación T009 y nueva parada](phase/P012-T002_CONTINUACION_T009.md),
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
B/B2, ambos diffs, TOML original, distribuciones e historiales conservados. Falta concretar una propuesta de
continuidad y su consentimiento nuevo; no se asume que el saldo autorice operar.

## P012-T003 — Chat, backup y restauración sobre el proyecto real

**Estado:** pendiente. **Depende de:** T002 y autorización explícita del tramo.
**Objetivo:** Acreditar el chat con el revisor real y el backup/restauración de consulta de una base con runs reales.
**Alcance:** proyecto B de T002 y la base del área.
**Rutas permitidas:** `docs/**` en este repositorio; el área privada según T001.
**Criterios de aceptación:**

- Chat sobre la instantánea de HEAD: al menos una respuesta del revisor coherente con el código y los documentos,
  un comando determinista y una propuesta convertida en tarea confirmada, sin ejecutarla ni tomar el lock.
- Backup de la base con el producto, integridad comprobada y restauración de consulta que muestra los runs, el diff
  y las métricas de T002 sin volver a ejecutar nada; base operativa intacta.
- Llamadas por proveedor frente al techo y servicio detenido al terminar, sin locks ni jobs activos.

**Validación:** la propia del tramo.
**Entregables:** `docs/phase/P012-T003_CHAT_BACKUP_REAL.md`.

## P012-T004 — Proyecto TypeScript web nuevo con receta v2 en español

**Estado:** pendiente. **Depende de:** T002 y autorización explícita del tramo.
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

**Estado:** pendiente. **Depende de:** T002–T004 y las correcciones que hayan generado.
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
