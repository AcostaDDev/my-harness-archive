# P012 — Validación real previa a la apertura pública

Objetivo y criterios en [ROADMAP](ROADMAP.md#p012--validación-real-previa-a-la-apertura-pública).
Decisión: [D183](DECISIONS.md#d183--p012-validación-real-previa-a-la-apertura-pública).

**Estado:** T001 completada documentalmente y confirmada por el usuario (D184); seis tareas pendientes.
Ninguna operación real ejecutada.
**Siguiente:** P012-T002, pendiente de autorización explícita del tramo sobre la
[propuesta confirmada](phase/P012-T001_PROPUESTA_OPERATIVA.md). La confirmación de T001 no autoriza operaciones;
hashes de artefactos, cachés/fixtures y preflight son puerta offline previa a proveedores en T002.
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

**Estado:** pendiente. **Depende de:** T001 confirmada y autorización explícita del tramo.
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
**Entregables:** `docs/phase/P012-T002_INCORPORACION_REAL.md` y evidencia saneada.

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
