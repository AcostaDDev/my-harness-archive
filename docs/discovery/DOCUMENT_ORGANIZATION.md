# Organización documental por fase y estructura de producto

Tarea de diseño del 2026-10-14 (D072). Puntos de §12 confirmados por el usuario (D073).
**H6.3 implementado offline** con las diferencias recogidas en su
[entrega](H6.3_DOCUMENT_CONTRACT.md); H6.4, H6.5 y la UI siguen sin implementar.
Base: tarea propuesta en NEXT_STEPS, petición del usuario del mismo día, D032,
D034–D037, D052, D054, D066 y especificación §7, §11 y §12. Referencia en lectura:
`reference_project/docs` (ROADMAP, NEXT_STEPS, STATE y `archive/phase-NNN/` con
NEXT_STEPS, REVIEW y SUMMARY). No se han leído runs ni datos privados.

## 1. Requisitos del usuario

1. Para crear un proyecto, el revisor pide un documento con la finalidad, las
   tecnologías, el problema y la solución prevista.
2. De ahí sale una conversación: el modelo pregunta y ambos fijan el producto final.
   Durante la conversación, el sistema genera los documentos base: NEXT_STEPS,
   STATE, SPECIFICATION, ARCHITECTURE, diagramas de datos si el proyecto los
   necesita y ROADMAP. El ROADMAP define las fases generales y NEXT_STEPS, las
   subtareas de cada fase.
3. El histórico va en `docs/archive/phase-N/`, con NEXT_STEPS y STATE de cada fase.
   El README debe poder leerlo cualquier persona. El usuario ve y edita los
   documentos desde su editor y desde el sistema.
4. La creación termina cuando el usuario acepta el roadmap y la documentación.
   Después ya puede ejecutar el harness.
5. Cada proyecto tiene su URL. Dentro hay chat global (preguntas y acciones
   rápidas), documentación (ver y editar), fases (una URL cada una, con carga
   limitada) y tareas. De cada tarea se guardan los agentes que han participado,
   sus tokens, turnos, esfuerzo y modelo. Hay un visor básico de tests (OK/KO) y
   estadísticas por proyecto y globales.

El usuario pide valorar si `docs/` necesita más carpetas aparte de `archive/`.
La respuesta está en §3.

## 2. Qué existe y qué falta

| Ámbito | Implementado | Falta para lo pedido |
|---|---|---|
| Plantilla | `project-foundation` v1 (D037): README, BRIEF, DECISIONS, PROJECT_PROFILE, STATE, NEXT_STEPS; P001-T001 limitada a un checklist | Conjunto v2 (§3), ROADMAP y primera fase derivada del roadmap |
| Descubrimiento | Una propuesta de solo lectura por cada acción; el usuario rellena cinco campos | Conversación de varios turnos con borradores de documentos (§5.1) |
| Bloques gestionados | Bloque JSON entre marcadores en STATE/NEXT_STEPS; exportación explícita con el diff confirmado (D036) | Actualización en cada commit de tarea y formato legible (§4) |
| Plan de fase | Parser determinista de `## PNNN-TNNN — título` y campos `**Objective:**`, etc. (`core/engine/planning.py`) | Alias en español; fase instanciada desde ROADMAP |
| Fase | El usuario la define por API (`PhaseCreate`: código, objetivo, criterios, tareas, documentos, tag); el cierre no toca documentos (D032) | Archivado e instalación de la fase siguiente: STATE ya lo recoge como pendiente |
| Reconciliación | Tarea `PNNN-RECONCILE-n` limitada a los documentos de la fase (D034) | Uso para compactar la base acumulada (§5.3) |
| Chat | Turnos de solo lectura, propuestas que se convierten en tareas y espera por el lock del checkout (D035) | Chat global, comandos y no esperar al ejecutor (§8) |
| Legacy | El lector indexa `docs/STATE.md`, `NEXT_STEPS.md`, `ROADMAP.md` y `docs/archive/**` | Nada: la estructura propuesta es compatible |
| Telemetría | El terminal guarda `usage`, `modelUsage`, `duration_ms`, `total_cost_usd`, `permission_denials`, modelo, esfuerzo y sesión en `result_json`; los streams en bruto quedan como artefactos sujetos a retención H5.3 | Tabla de métricas materializada; turnos y agregados (§9) |
| Tests | JUnit por comando con el original congelado (H5.1) | Agregados OK/KO por tarea, fase y proyecto |
| UI | Una sola página; la navegación vive en el estado de React, sin rutas | Mapa de URLs y carga por recurso (§7) |

En D050 y D071, los commits de tarea quedaron en HEAD del checkout del
proyecto. El worktree por tarea de H2.4 solo se usa en la demo. Por tanto, la
documentación vigente es la del HEAD del checkout gestionado.

## 3. Estructura del repositorio gestionado

```text
<proyecto>/
  README.md                  # para personas: qué es, cómo instalar, usar y probar; mapa de docs
  docs/
    SPECIFICATION.md         # qué y por qué: problema, usuarios, alcance, requisitos, no objetivos
    ARCHITECTURE.md          # cómo: stack, componentes, flujos, persistencia, límites
    architecture/            # opcional: un archivo por diagrama o contexto
      data-model.md          #   Mermaid erDiagram; uno por base de datos o contexto si hay varios
    ROADMAP.md               # fases: objetivo, criterios de salida, dependencias + bloque gestionado
    DECISIONS.md             # índice; su bloque gestionado se genera desde decisions/
    decisions/
      D001-<slug>.md         # una decisión por archivo, con estado y sustituciones
    STATE.md                 # estado actual: bloque gestionado + base acumulada + fase activa
    NEXT_STEPS.md            # plan de la fase activa: tareas con contrato legible
    research/                # opcional: investigaciones duraderas citadas por decisiones o tareas
    archive/
      phase-000/             # definición del proyecto (bootstrap)
        BRIEF.md             #   documento inicial del usuario, byte a byte
        DEFINITION.md        #   resumen mecánico de la conversación de creación
      phase-001/
        NEXT_STEPS.md        #   plan final de la fase, byte a byte desde el HEAD cerrado
        STATE.md             #   STATE al cerrar, byte a byte
        REVIEW.md            #   evaluación READY que habilitó el cierre (mecánico)
        SUMMARY.md           #   resumen mecánico desde SQLite (§5.3)
  .harness/                  # configuración portable (especificación §7); no es documentación
```

Los directorios usan tres dígitos (`phase-001`) para coincidir con los códigos
`P001` del parser y con ReferenceProject. `phase-000` corresponde a la creación. No es
una fase en SQLite: es el archivo de la operación de bootstrap.

### Carpetas adicionales: valoración

- **`decisions/`: recomendado.** Un único DECISIONS.md crece sin límite: el de
  este repositorio ocupa 135 KB. Con un archivo por decisión, los agentes cargan el
  índice (una línea por decisión) y abren solo las que cita la tarea. Añadir
  decisiones no genera conflictos y las sustituidas siguen visibles con su estado.
  El harness genera el índice; nadie lo mantiene a mano.
- **`architecture/`: opcional.** Responde a lo de «diagrama de bbdd separado o
  varios». ARCHITECTURE.md sigue siendo la entrada y enlaza los diagramas. Se
  usa Mermaid en texto, no imágenes: el diff se revisa, los agentes lo editan y
  VS Code, GitHub y la UI lo renderizan. La carpeta solo se crea si hay
  persistencia o varios contextos.
- **`research/`: opcional.** Es la ubicación designada para el resultado de las
  tareas de investigación: compatibilidades, spikes o comparativas. Sin una
  ubicación fija, los agentes las dejan en cualquier sitio. No la crea la plantilla.
- **`archive/`: requisito del usuario.** Añade REVIEW.md y SUMMARY.md a STATE y
  NEXT_STEPS para que la fase cerrada se pueda leer sin la base de datos.
- **No se recomienda una carpeta por tarea**, como `discovery/` en este repositorio.
  La trazabilidad por tarea (contratos, intentos, diffs, revisiones, tests y consumo)
  ya está en SQLite y en los artefactos. Duplicarla en Markdown crearía una doble
  autoridad y volvería a inflar el contexto. SUMMARY.md la resume por fase.
- **No se recomiendan** `chat/`, `questions/` ni `metrics/`. Su autoridad es
  SQLite; en Markdown solo aparecen como proyección mecánica.

## 4. Documentos: contenido, autoría y reglas

| Documento | Naturaleza | Quién lo escribe | Cómo entra en Git |
|---|---|---|---|
| README.md | Para personas | Tareas cuyo contrato lo incluye; reconciliación; usuario | Diff revisado o edición humana confirmada |
| SPECIFICATION.md, ARCHITECTURE.md, `architecture/` | Intención de producto y técnica | Creación (borrador del revisor aceptado por el usuario); tareas autorizadas; usuario | Igual; un cambio de alcance exige una decisión |
| ROADMAP.md (prosa) | Intención de fases | Creación, planificación de fase, usuario | Igual; la sección de la fase activa solo cambia por enmienda (D034) |
| `decisions/*.md` | Registro | Tareas autorizadas, usuario | Se añade; nunca se borra; «sustituida por» |
| STATE.md (prosa) | Base acumulada y fase activa | Tarea de reconciliación; usuario | Diff revisado o edición confirmada |
| NEXT_STEPS.md (prosa) | Plan de la fase activa | Planificación de fase (propuesta del revisor confirmada); usuario | Transición o edición confirmada |
| Bloques gestionados | Proyección de SQLite y de archivos | Solo el harness | Actualización mecánica en commits (§5.2) |
| `archive/**` | Histórico inmutable | Solo el harness | Commit de transición |

Reglas comunes:

- **Autoridad.** SQLite manda en el estado operativo (fases, tareas, runs,
  intentos, métricas y preguntas). Markdown manda en la intención (requisitos,
  arquitectura, fases previstas, decisiones). Los bloques gestionados son
  proyecciones: no se vuelven a leer como fuente. Solo se comparan, byte a byte,
  con su regeneración.
- **Bloques gestionados.** Se mantienen las reglas de D036: solo se reemplaza el
  contenido entre marcadores, la prosa exterior se conserva y se rechazan los
  marcadores parciales o repetidos. Se añaden `managed-roadmap` (tabla de fases y
  estado) y `managed-decisions` (índice). El formato v2 pasa de JSON a Markdown
  legible (tablas y listas) con escape de `|`, backticks, HTML, fences y
  marcadores. El JSON v1 se sigue leyendo.
- **Rutas protegidas.** El perfil incluye siempre `docs/archive/**`. Los contratos de
  ejecutor no incluyen nunca STATE, NEXT_STEPS, ROADMAP ni DECISIONS.md, como en
  ReferenceProject. El progreso por tarea lo escribe el harness y la prosa de estado,
  la reconciliación.
- **Presupuestos de tamaño.** STATE ≤ 24 KiB, de ellos la base acumulada ≤ 12 KiB;
  NEXT_STEPS ≤ 48 KiB; índice de decisiones ≤ 8 KiB. Superarlos produce un aviso
  en el check de fase y una tarea de reconciliación, nunca un truncado. Se
  mantiene el límite de 512 KiB de D036.

### STATE.md

```markdown
# Estado — <proyecto>

<!-- harness-local:managed-state:start -->
Fase activa, tareas (estado, resumen del ejecutor, notas de traspaso, veredicto),
preguntas abiertas, último check, tests OK/KO de la última validación.
<!-- harness-local:managed-state:end -->

## Base acumulada
Qué existe y funciona, por área, con enlaces a archive/phase-NNN/SUMMARY.md.
Se compacta en la reconciliación de cada fase y se traslada literal a la siguiente.

## Fase activa — P002 <título>
Resumen de la fase y notas para la siguiente sesión (reconciliación o usuario).
```

Un STATE fresco evita lo que le pasa a este repositorio, con 173 KB. La historia
se queda en `archive/`. STATE solo conserva lo vigente y la base compacta.

### NEXT_STEPS.md

Se conserva el formato que ya lee la planificación determinista: encabezado de
fase, `## Shared constraints` y una sección `## PNNN-TNNN — título` por tarea con
`**Objective:**`, `**Allowed paths:**`, `**Acceptance criteria:**`,
`**Validation commands:**`, `**Executor:**`, `**References:**`, etc. Se añaden
alias en español (Objetivo, Rutas permitidas, Criterios de aceptación, Comandos
de validación, Ejecutor, Referencias, Restricciones, Fuera de alcance,
Entregables, Riesgos). El objetivo de la fase se resume en una línea y enlaza a
ROADMAP. Los criterios de salida solo están en ROADMAP.

### ROADMAP.md

```markdown
# Roadmap — <proyecto>

<!-- harness-local:managed-roadmap:start -->
| Fase | Título | Estado | Tag |
<!-- harness-local:managed-roadmap:end -->

## P001 — <título>
**Objetivo:** …
**Criterios de salida:**
- …
**Dependencias:** …
**Fuera de alcance:** …
```

Al instanciar la fase N, la sección `## PNNN` da el objetivo y los criterios de
salida de `PhaseCreate`. Los encabezados de NEXT_STEPS dan las tareas. Los
documentos de fase incluyen STATE, NEXT_STEPS y ROADMAP, y todos se congelan por
hash (D032). Los códigos son estables desde que empieza la fase. Las fases futuras
se pueden editar, reordenar o insertar libremente. Cambiar la sección de la fase
activa es una enmienda (D034). Las secciones cerradas no se editan: un cambio se
notifica como deriva.

### DECISIONS y `decisions/`

Cada `decisions/DNNN-<slug>.md` empieza con `# DNNN — título` y los campos
**Estado** (propuesta | aceptada | sustituida por DMMM | rechazada), **Fecha**,
**Fase**, **Contexto**, **Decisión** y **Consecuencias**. DECISIONS.md tiene una
introducción y el índice gestionado, generado desde esos encabezados.

### README.md

Es para personas y no lleva bloque gestionado. Plantilla: qué es, estado (enlace a
ROADMAP), requisitos, instalación, uso, tests, estructura y mapa de la
documentación. Lo actualizan las tareas que cambian el uso y la reconciliación.

## 5. Ciclo de vida

### 5.1 Creación (fase 0)

1. **Alta.** Carpeta vacía registrada con confianza explícita (D054). El proyecto
   queda en estado `DEFINING`.
2. **Brief.** El usuario sube o pega un documento Markdown: UTF-8, máximo de
   256 KiB y sin interpretar comandos ni rutas. Se congela con su hash. Los cinco
   campos de D037 quedan como guía opcional de redacción.
3. **Conversación de definición.** Usa la infraestructura de D035: turnos nuevos
   del revisor en solo lectura, con contexto congelado (brief, borradores actuales
   con su hash y turnos anteriores). La salida estructurada de cada turno incluye
   respuesta, preguntas abiertas, propuestas de borrador por documento (contenido
   completo y motivo) y la lista de pendientes para aceptar. Las decisiones salen
   como borradores en `decisions/`. Una salida inválida detiene el turno, sin
   fallback.
4. **Borradores en disco.** Al aplicar una propuesta, el harness escribe el
   documento en la carpeta destino sin hacer commit. Usa CAS sobre el hash anterior:
   si el usuario lo ha editado mientras tanto, hay conflicto y no se sobrescribe.
   El usuario edita en su editor o en la UI. El turno siguiente detecta los
   cambios por hash y los incluye como ediciones del usuario. Solo se admiten
   rutas de la plantilla v2, `architecture/*.md` y `decisions/*.md`. Cualquier otro
   archivo bloquea la aceptación (flujo de importación). El agente nunca escribe.
5. **Aceptación.** El usuario declara aceptados el roadmap y los documentos. El
   preview determinista incluye los archivos íntegros,
   `archive/phase-000/{BRIEF,DEFINITION}.md`, los bloques gestionados, la
   definición de P001 derivada, el perfil, la política y los comandos. Bloquean la
   aceptación: faltan documentos obligatorios, ROADMAP no tiene al menos una fase,
   P001 no tiene objetivo y criterios, NEXT_STEPS no tiene al menos una tarea
   P001-TNNN con los campos que exige el modo de planificación, o quedan preguntas
   bloqueantes abiertas sin aplazar de forma explícita.
6. **Confirmación.** Hash, motivo e Idempotency-Key lanzan el job `bootstrap` de
   D037 con la plantilla v2. El commit raíz contiene exactamente esos bytes. El
   adaptador de D037 ya acepta archivos presentes si coinciden con los sellados.
   P001 se crea ACTIVE y se adopta en la misma transacción. Se mantienen la
   intención conciliable y la recuperación.
7. **Proyecto listo.** Se pueden encolar la primera tarea o un lote. La creación no
   genera código ni instala dependencias: el producto se construye fase a fase.

### 5.2 Durante la fase

- **Tareas del ejecutor.** Contrato acotado (§4, rutas protegidas). Puede incluir
  SPECIFICATION, ARCHITECTURE, `decisions/`, `research/` o README si la tarea lo
  requiere de forma explícita.
- **Actualización mecánica en cada commit de tarea.** Se usa `MechanicalUpdate` de
  H2.4, que la especificación §10 permite. El harness regenera los bloques de
  STATE, NEXT_STEPS y, si cambia `decisions/`, DECISIONS. Así STATE y NEXT_STEPS
  siguen frescos sin exportar a mano. El bloque no incluye el SHA de su propio
  commit, igual que en D036. Las notas por tarea salen del resultado estructurado:
  se propone añadir `handoff_notes` acotadas al esquema del ejecutor y
  `follow_ups` al del revisor. Ambos se renderizan escapados. H2.4 rechaza que una
  actualización mecánica se solape con lo revisado. Para la tarea de
  reconciliación, que sí edita la prosa de STATE, hace falta una variante
  limitada al bloque: el bloque revisado tiene que ser idéntico al de la base.
- **Tareas nacidas del chat.** Pertenecen a la fase activa, con su origen
  registrado. Aparecen en el bloque de NEXT_STEPS como tareas añadidas y no
  reescriben la prosa del plan.
- **Ediciones humanas.** Ver §6.

### 5.3 Cierre y transición

1. **Reconciliación** (D034, opcional pero recomendada por el check). Compacta la
   base acumulada, resume la fase activa y corrige la deriva de README,
   SPECIFICATION, ARCHITECTURE y decisiones. Es revisada y se hace commit.
2. **Check** → READY por contenido exacto (D032). Si los documentos no son
   coherentes o se superan los presupuestos, el resultado es
   `NEEDS_RECONCILIATION`.
3. **Cierre** → CLOSED + tag sobre el HEAD evaluado. Sin cambios respecto a D032:
   no edita documentos.
4. **Transición** (operación nueva `phase_transition`; es la instalación de la
   fase siguiente que STATE da como pendiente). La propuesta de plan de la fase
   N+1 puede venir antes de una conversación `phase_planning` con el revisor (§5.1,
   mismo mecanismo) o del propio usuario. El preview contiene:
   - `archive/phase-NNN/STATE.md` y `NEXT_STEPS.md`: copia exacta de los bytes en
     el HEAD de CLOSED;
   - `REVIEW.md`: render del resultado READY;
   - `SUMMARY.md`: render desde SQLite de la definición y sus enmiendas, las tareas
     con estado, commit, intentos, revisiones y veredictos, las tareas del chat, las
     preguntas y respuestas, los tests finales OK/KO, los agregados de consumo con su
     procedencia, la duración y el tag;
   - el STATE nuevo: encabezado, base acumulada literal, fase activa vacía y
     bloque regenerado;
   - el NEXT_STEPS nuevo con el plan aceptado;
   - el bloque de ROADMAP regenerado.

   La confirmación con hash crea un único commit
   «docs: archivar PNNN y abrir PNNN+1», con la intención conciliable de D036. Al
   terminar el job, la fase N+1 se crea ACTIVE con su definición derivada y los
   documentos adoptados en la misma transacción. Requisitos: checkout limpio,
   documentos iguales a sus hashes, ningún lote activo y ninguna intención
   incierta. Una fase ABANDONED también se archiva y SUMMARY lo indica. Si el
   ROADMAP no tiene más fases, solo se archiva y NEXT_STEPS queda «sin fase
   activa». El tag sigue en el HEAD evaluado.

La exportación manual de D036 se mantiene para regenerar bloques fuera de este
recorrido.

### 5.4 Continuidad: qué lee cada operación

| Operación | Documentos en el contexto congelado por defecto |
|---|---|
| Planificar tarea (revisor) | NEXT_STEPS (tarea y Shared), STATE, ROADMAP §fase, ARCHITECTURE, índice de decisiones y documentos citados en References |
| Ejecutar | Contrato congelado, documentos citados y STATE |
| Revisar | Contrato, diff, validaciones y documentos citados |
| Reconciliar / check de fase | STATE, NEXT_STEPS, ROADMAP §fase, README, SPECIFICATION, ARCHITECTURE, índice y evidencia de la fase |
| Planificar fase | ROADMAP, base acumulada de STATE, SPECIFICATION, ARCHITECTURE, índice y `archive/phase-(N)/SUMMARY.md` |
| Chat | STATE, NEXT_STEPS y ROADMAP; el usuario puede añadir más (D035) |
| Definición | Brief y borradores actuales |

El archivo no entra por defecto en el contexto. Los agentes lo leen solo si se cita.
Criterio verificable: con el checkout de un fixture y sin SQLite, una sesión nueva
determina la fase activa, la siguiente tarea, lo que existe, las notas recientes y
las decisiones aplicables.

## 6. Edición desde el editor y desde el sistema

Hay un único camino hacia el historial: un commit del harness después de que el
usuario confirme el diff exacto. El harness nunca revierte archivos del usuario.

- **Desde la UI.** Editor Markdown con vista previa segura (sin HTML ejecutable,
  especificación §10) y hash base. Al guardar se muestra el diff. Después de
  confirmarlo, se lanza un job `document_edit` bajo el lock del checkout, con CAS
  sobre el hash base, CommitIntent como en D036 y adopción de hashes. Si hay una
  tarea en curso, el job espera su turno. Si el archivo ha cambiado entre tanto,
  no se escribe y la UI muestra el conflicto.
- **Desde el editor de código.** El harness detecta la deriva por hash y la UI
  muestra «cambios locales sin confirmar» con el diff. «Confirmar» usa el mismo
  job sobre esos bytes. Mientras haya documentos sin confirmar, se bloquean con un
  motivo explícito el inicio de una tarea, el check, la exportación y la
  transición. Si no, la captura H2.4 metería esas ediciones en el diff del
  ejecutor. Hay que comprobar al implementar si el arranque actual ya exige un
  checkout limpio.
- **No editables.** Bloques gestionados (la UI los muestra bloqueados; desde el
  editor cuentan como deriva y se ofrece regenerar) y `archive/**` (solo lectura;
  la deriva frente al hash archivado se notifica).
- **Efectos sobre lo congelado.** Editar documentos de la fase invalida READY
  (D032). Cambiar la definición de la fase exige una enmienda (D034). Un run en
  curso conserva su contrato congelado y la versión nueva se usa en el siguiente.

## 7. URLs y carga

```text
/                                         Proyectos, crear o registrar, resumen global
/stats                                    Estadísticas globales
/projects/new                             Alta: carpeta y confianza
/projects/:project                        Resumen: fase activa, siguiente acción, bloqueos, tests, consumo
/projects/:project/setup                  Creación en curso: chat de definición y borradores
/projects/:project/chat[/:conversation]   Chat global
/projects/:project/docs[/*path]           Árbol y documento (ver, editar, diff, historial)
/projects/:project/phases                 Lista paginada de fases (solo resumen)
/projects/:project/phases/:phase          Fase: tareas resumidas, check y cierre, preguntas, tests, consumo
/projects/:project/phases/:phase/tasks/:task             Tarea: runs, intentos, agentes, métricas, diff, revisiones, tests
/projects/:project/phases/:phase/tasks/:task/runs/:run   Run: timeline, logs por tramos, validaciones
/projects/:project/stats                  Estadísticas del proyecto
/projects/:project/settings/...           Agentes, prompts, permisos, perfil
```

- Cada URL carga solo su recurso. El resumen de un proyecto trae contadores, no
  tareas. El de una fase, sus tareas resumidas. El de una tarea, sus intentos
  resumidos. Logs, diffs y casos de test se piden aparte y paginados
  (especificación §14).
- En las URLs se usan los códigos `P001` y `P001-T003`, únicos por proyecto. Los
  runs usan su id. Se admiten enlace directo, recarga e historial del navegador.
  El servidor del wheel debe servir `index.html` en las rutas que no son de API.
- Las rutas las cubre un enrutador mínimo propio sobre History API, sin dependencia
  nueva. La decisión final se toma en el alcance de H6.2. Los diagramas Mermaid se
  renderizan con carga diferida, solo en la sección de documentación.
- Faltan endpoints de agregados (§9). Las lecturas actuales de fase, run e intento
  se reutilizan.

## 8. Chat global del proyecto

- Cada proyecto tiene una sección de chat con varias conversaciones (D035). Cada
  conversación puede llevar una fase o tarea como contexto por defecto.
- **Pregunta.** El revisor responde directamente en un turno de solo lectura, sin
  crear tarea.
- **Petición («Ajusta X»).** El revisor la convierte en propuesta. Si el usuario la
  acepta, se crea una tarea en la fase activa y sigue el flujo normal: planificar,
  ejecutar, revisar y hacer commit.
- **Comandos.** Se reconocen por sintaxis explícita y no los interpreta un modelo.
  El harness los ejecuta con las mismas confirmaciones que el botón equivalente y
  sin agente: `/estado`, `/tests`, `/siguiente`, `/lote`, `/check`, `/cerrar`,
  `/exportar`, `/abrir-fase` y `/tarea <texto>` (fuerza una propuesta). Ningún
  comando se salta una confirmación ni concede permisos.
- **Recomendación (cambia D035).** Hoy un turno espera al lock del checkout, así
  que una pregunta espera a que termine la tarea en curso. En un chat global eso
  empeora mucho la experiencia. Propuesta: ejecutar los turnos sobre una
  instantánea de solo lectura del HEAD (worktree temporal o árbol exportado), sin
  tomar el lock, comparando la evidencia de esa instantánea antes y después.

## 9. Métricas y estadísticas

### Por intento (tabla materializada)

Cada campo indica su procedencia: solicitado, reportado, derivado o ausente. Un
null nunca es cero.

- Contexto: proyecto, fase, tarea, run, número de intento, rol (planificación,
  revisión, ejecución, chat, definición, fase, reconciliación), proveedor y
  versiones del adaptador y de la CLI.
- Modelo solicitado y modelos reportados. Es una lista porque `modelUsage` puede
  traer varios. Esfuerzo solicitado y esfuerzo reportado, si lo hay.
- Tokens: entrada, caché leída, caché creada, salida y razonamiento cuando se
  reporten, por modelo si se puede. Se marca si el valor es incremental o
  acumulado.
- Turnos: los que reporta Claude (`num_turns`). Codex no los reporta como tal: se
  cuentan los elementos del stream (comandos, cambios de archivo, herramientas) y
  se etiqueta como «derivado».
- Herramientas por tipo (derivado) y denegaciones de permiso (reportado).
- Duraciones: la medida por el harness (inicio y fin) y la de API, si se reporta.
- Coste reportado como «equivalente API», nunca como factura ni cuota.
- Resultado: estado, motivo de parada, veredicto y número de revisión.

### Agregados

- **Tarea:** agentes participantes (rol × proveedor × modelo), intentos por rol,
  revisiones usadas sobre el límite, aceptación a la primera, tiempo hasta
  ACCEPT/COMMIT, tokens incluidos los fallos y tests de la última validación.
- **Fase, proyecto y global:** consumo por fase, día, rol, proveedor y modelo.
  Modelos y esfuerzos «favoritos» por frecuencia de uso y por tokens, separados
  por rol. Tasa de aceptación a la primera, revisiones medias, duración por tarea,
  paradas por motivo y evolución de los tests. El global agrega todos los proyectos
  de la misma SQLite.

### Reglas

- No sumar acumulados con incrementales, no sumar duraciones paralelas, no
  deducir porcentajes de cuota y no tratar un alias como una versión exacta
  (especificación §11).
- La tabla `attempt_metrics` se materializa en la misma transacción que el
  resultado del intento. Así las estadísticas sobreviven a la retención de logs
  (H5.3) y se consultan con SQL, sin parsear blobs.
- Relleno de intentos anteriores desde `result_json` y los streams que se
  conserven (verificados por hash), con procedencia `backfill`. Es idempotente.
- **Hueco actual:** el terminal no guarda `num_turns` ni la duración de API. La
  captura se amplía con una versión nueva de normalización. Antes de fijar el
  catálogo, hay que caracterizar offline los campos exactos con los streams reales
  conservados de D071.

### Tests

- Por validación: total, superados, fallidos, con error y omitidos según JUnit
  (H5.1). Sin JUnit, OK/KO por comando.
- Vistas: tarea (última validación), fase (validación del último check) y proyecto
  (última validación en HEAD y tendencia por commit de tarea). En la vista básica,
  OK son los superados, KO los fallidos más los errores, y los omitidos van aparte.

## 10. Diferencias con lo decidido

- **D032.** El cierre no cambia. Se añade la transición posterior.
- **D036.** Se mantiene la exportación manual. Se añaden la actualización mecánica
  en cada commit de tarea y el formato de bloque v2.
- **D037.** Para proyectos nuevos, la plantilla v2, la conversación y los borradores
  en disco sustituyen a la plantilla v1 y al descubrimiento de un turno. La v1 se
  sigue leyendo y no se reescribe ningún bootstrap existente.
- **D035.** Se añaden comandos deterministas, conversaciones de definición y de
  planificación y, si se confirma, turnos que no esperan al lock.
- **D054/H6.2.** Se concretan las secciones y las URLs.
- **Especificación §7.** Se detalla `docs/`. Se mantiene «no son una segunda base
  operativa editable libremente», porque toda edición pasa por hash y confirmación.

## 11. Implementación posterior por incrementos

Cada incremento se verifica offline con fixtures y Git/SQLite sintéticos, sin
proveedores.

- **H6.3 Contrato documental y transición (backend/API, sin agentes).** Plantilla
  v2, bloques v2, `managed-roadmap` y `managed-decisions`, parser de ROADMAP y alias
  de NEXT_STEPS. Actualización mecánica en los commits (con la variante limitada al
  bloque), `phase_transition`, `document_edit`, detección de deriva y bloqueo de
  operaciones con documentos sin confirmar. La transición acepta un plan que
  aporta el usuario.
  Criterios: (1) una sesión nueva reconstruye la siguiente tarea solo con los
  documentos; (2) `archive/phase-001` es idéntico al HEAD cerrado, REVIEW y SUMMARY
  son deterministas y P002 queda ACTIVE; (3) una caída en cada efecto concilia el
  mismo commit; (4) la deriva en bloques o en el archivo se detecta sin
  sobrescribir; (5) se avisa cuando se superan los presupuestos.
- **H6.4 Métricas y estadísticas (backend/API).** Catálogo caracterizado,
  migración `attempt_metrics`, captura al terminar, relleno y endpoints de
  agregados paginados, tests OK/KO incluidos. Criterios: streams sintéticos
  incrementales y acumulados, campos ausentes, varios modelos, fallos y
  cancelaciones; relleno idempotente; la retención no pierde métricas; nada se
  cuenta dos veces.
- **H6.5 Creación y planificación conversacionales (backend/API).** Conversaciones
  `definition` y `phase_planning`, propuestas de borrador, borradores en disco con
  CAS y aceptación que lleva al bootstrap v2 o a la transición. Criterios: de una
  carpeta vacía con conversación sintética y ediciones en disco y por API se llega
  al commit raíz, P001 y `phase-000`; las ediciones concurrentes se detectan; no
  se admite ningún archivo ajeno; el agente no escribe.
- **H6.2 UI de producto (ampliada).** Rutas de §7, editor de documentos, chat con
  comandos, fases y tareas por URL, métricas, tests, estadísticas y asistente de
  creación. QA visual con navegador sobre `scripts/dev`. Se puede dividir en un
  shell con proyecto, fase y tarea; documentación y chat; creación; y estadísticas.

Orden recomendado: H6.3 → H6.4 → H6.5 → H6.2, para que la UI se construya una
sola vez sobre contratos estables. H6.4 es independiente y puede adelantarse para
empezar a acumular datos.

## 12. Puntos confirmados por el usuario (D073)

Todos aceptados. En el punto 1, las tres carpetas se crean desde el principio y el agente
decide si las usa. En el punto 6, la UI será una tarea completamente distinta.

1. Carpetas: `decisions/` sí; `architecture/` y `research/` opcionales; ninguna
   carpeta por tarea.
2. Archivo por fase: STATE, NEXT_STEPS, REVIEW y SUMMARY. `phase-000` con BRIEF y
   DEFINITION.
3. Los ejecutores no editan STATE, NEXT_STEPS ni ROADMAP. El progreso por tarea es
   mecánico y la prosa se escribe en la reconciliación de fase.
4. Borradores de creación en la carpeta destino, editables desde el editor antes
   del commit raíz.
5. Turnos de chat sobre una instantánea de HEAD, sin esperar al ejecutor (cambia
   D035).
6. Orden H6.3 → H6.4 → H6.5 → H6.2, o adelantar parte de la UI.
7. Plantillas en español con alias en inglés en el parser.
