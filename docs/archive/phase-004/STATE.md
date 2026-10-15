# Estado archivado — P004 Personalización, bloqueos y cierre (antes H3)

Instantánea archivada en P008-T001 (D088): secciones de H3 que el `docs/STATE.md` acumulado conservaba hasta `8622a43`.

## Verificación de H3.1

- Git inicial limpio en `main`, `7606cfe`. Instrucciones, estado, siguiente tarea,
  decisiones, especificación §9, backlog y referencia estática de prompts revisados.
- 331 pruebas pytest y 121 subtests pasan: 308 anteriores y 23 casos nuevos.
  12 checks ligeros, 3 pruebas Node, OpenAPI/tipos, TypeScript y build correctos.
  Aviso conocido Starlette/HTTPX conservado.
- Migración 0008 con upgrade/downgrade/upgrade y `alembic check` en base temporal;
  un run previo sobrevive. Ninguna base de trabajo del usuario se migró.
- Concurrencia de activación con dos hilos, rollback/reinicio, guardias HTTP,
  409/422/404 y aislamiento de versiones de proyecto verificados. Petición
  confirmada en SQLite antes del agente falso, conservada byte a byte tras
  activar otra versión. Históricos de formato 1 reanudables sin reescribir filas.
- Chrome en demo nueva `/private/tmp/h31-ui-demo-1013`, puerto 8016: variable
  inválida visible, guardar sin activar, diff, confirmación, activar, rollback
  con UUID nuevo, auditoría de dos activaciones y persistencia tras recarga.
  Formulario/auditoría inspeccionados visualmente; sin encolar proveedores.
- Límites: plantillas de fases/bootstrap sin flujos, sin aplicación de nuevos
  prompts a runs detenidos, importación/exportación de overrides ni edición de
  esquemas. Catálogo sin paginación/benchmark de históricos grandes. Fakes no
  certifican respuestas de modelos. H3.2 no iniciado.
- Diff/whitespace revisados; sin proveedores, smoke, colaboración automática,
  ejecución de harness para desarrollo, cambios en ReferenceProject, configuración
  global ni push. Commit solicitado por el usuario.

## Verificación de H3.2

- Git inicial limpio en `main`, `755e205`. AGENTS/STATE/NEXT_STEPS/DECISIONS,
  especificación §8/§10, backlog H3.2 y contratos H2 revisados.
- 361 pruebas pytest y 121 subtests: 331 anteriores y 30 H3.2. 12 checks
  ligeros, 3 pruebas Node, OpenAPI/tipos, TypeScript/build y diff/whitespace.
  Aviso conocido Starlette/HTTPX conservado, sin cambiar dependencias.
- SQLite/Git/procesos sintéticos: caducidad al decidir/al lanzar, request alterada,
  sustitución, aislamiento de categorías/techos, denegación antes del agente,
  versión y concurrencia, exclusión de checkout, reinicio, once/task y caída
  después de intención; historial y presupuesto preservados. Formatos 1–4
  compatibles; upgrade/downgrade/upgrade y `alembic check` en base temporal.
- API: crear/sustituir/conceder/denegar, acciones habilitadas del servidor,
  confirmación/huella/versiones y 403/409/422; conceder no invoca agentes.
  Regresión del campo `operation` tras fallo detectado en Chrome.
- Revalidar ante REVISE no llama al ejecutor ni consume concesiones; un reintento
  explícito posterior conserva el presupuesto. Se actualizó una prueba H2 que
  caracterizaba la rama anterior, contraria al efecto documentado de revalidar.
- CLI sintética independiente acredita argv nuevo con regla exacta, petición
  persistida antes de efecto, inventario anterior cerrado y configuración intacta;
  red no soportada, permisos fuera del techo y snapshots inválidos rechazados.
- Chrome en `/private/tmp/h32-ui-session`, `127.0.0.1:8017`, sin puertos/supervisor:
  conceder, inspeccionar auditoría, reiniciar servicio/recargar, sustituir y
  denegar. Versiones 11→14, único intento y job DONE conservados; estados/formulario
  inspeccionados visualmente. Servicio y pestaña de prueba cerrados.
- No se migró la SQLite de trabajo del usuario. Sin proveedores/smokes/login,
  secretos, recuperación D020/D022, ReferenceProject, configuración global, colaboración
  automática, harness de desarrollo ni push. Commit solicitado por el usuario.
- Límites: reglas de CLI real no certificadas por fakes; no sandbox físico,
  grants fuera del contrato, políticas editables, permisos vivos/SDK, resolución
  automática de producto o cierre. Sesión local/guardia H0/H1/SSE siguen pendientes.
  Ledger sin paginación ni benchmark de grandes históricos. H3.3 no iniciado.

## Verificación de H3.3

- Git inicial limpio en `main`, `84d3426`. AGENTS/STATE/NEXT_STEPS/DECISIONS,
  especificación §3/§7/§8/§10/§13, backlog H3.3 y contratos H2/H3 revisados;
  `phase_check`/`reconcile_phase`/`apply_phase_close` legacy leídos estáticamente.
- 390 pruebas pytest y 121 subtests: 361 anteriores y 29 H3.3. 12 checks
  ligeros, 3 pruebas Node, OpenAPI (cambio aditivo comprobado estructuralmente)/
  tipos, TypeScript/build y diff/whitespace. Aviso Starlette/HTTPX conservado.
- Git/SQLite temporales y fakes: cierre con tag en el HEAD revisado y documentos
  intactos; READY obsoleto por commit, árbol sucio o documento sin tag; rechazo
  previo por evidencia, versión y preguntas; cambio de autoridad durante el check;
  puertas sin llamada; REVISE → reconciliación ligada al hash revisado; salidas
  inválidas sin reintento; lote/cierre distintos, caducidad y revocación.
- Reinicio sin repetir efectos; caída durante el check y tras la intención de tag
  con recuperación explícita y conciliación; tag ajeno intacto; cuatro cierres
  concurrentes, un job. Migración 0010 ida/vuelta y `alembic check` en base temporal.
- Chrome en demo sintética nueva del scratchpad, `127.0.0.1:8018`: crear fase,
  READY, commit externo → `STALE` sin tag, nuevo READY con confirmación limpiada,
  `CLOSED` con tag en HEAD; reinicio y recarga con historial completo, sin errores
  de consola. Detectó que la lista de fases no se refrescaba; corregido con sondeo.
  Servicio detenido y pestaña cerrada.
- No se migró la SQLite de trabajo del usuario. Sin proveedores/smokes/login,
  secretos, ReferenceProject (solo lectura estática), configuración global,
  colaboración automática, harness de desarrollo ni push. Commit solicitado.
- Límites: evaluación de fase con CLI real no ejecutada; sin reconciliación con
  agente, exportación mecánica de STATE/NEXT_STEPS, archivo/commit de cierre,
  fase siguiente, edición de definición, auto-encadenado de lote, tags anotadas,
  integración de ramas ni sesión local. Exclusión frente a escritores externos
  cooperativa. H3.4 no iniciado (D033).

## Verificación de H3.4

- Git inicial limpio en `main`, `ef126cb`. Revisados AGENTS, STATE, NEXT_STEPS,
  DECISIONS (D032/D033), el informe H3.3, el código de fases, la API y la UI.
- 408 pruebas pytest y 121 subtests: 390 anteriores y 18 de H3.4. Se ajustaron
  las pruebas H0/H1 y H3.3 al cambio de guardia, acciones, `tag_kind` y alcance de
  cierre. 12 checks ligeros y 4 pruebas Node (nueva: cabecera en mutaciones
  H0/H1). OpenAPI y tipos regenerados; TypeScript y build correctos. Se conserva el
  aviso Starlette/HTTPX.
- Git y SQLite temporales con fakes:
  - guardia H0/H1 (Host, Origin, cabecera; 403 antes del 404);
  - lote de dos tareas: cuatro jobs y `COMPLETED`, sin check ni cierre;
  - paradas por bloqueo, pregunta, caducidad, revocación, evidencia invalidada,
    cuarentena (sin repetir) y run ajeno;
  - enmienda (versiones, READY, lotes, documento nuevo, código, sin cambios) y
    abandono;
  - tag anotado (id determinista, conciliación tras caída con otra fecha, tag
    ligero previo intacto);
  - reconciliación con agente (sin planificador, contrato limitado, adopción solo
    tras el commit, escritura fuera de documentos no elegible);
  - migración 0011 (relleno `migrated`, bajada rechazada con fases abandonadas) y
    `alembic check`;
  - HTTP con un proyecto anotado.
- Chrome sobre una demo sintética nueva (scratchpad, `127.0.0.1:8019`):
  - crear la fase;
  - lote desatendido → tarea `COMMITTED` y lote `COMPLETED` sin intervención;
  - comprobar → READY;
  - enmendar → `ACTIVE` sin READY, con la v1 conservada;
  - abandonar → `Abandonada`.

  Sin 403/500 ni errores de consola. El servicio se detuvo y la pestaña se cerró.
- No se migró la SQLite de trabajo del usuario. Sin proveedores, smokes, login,
  secretos, ReferenceProject, configuración global, colaboración automática, harness de
  desarrollo ni push. Commit solicitado por el usuario.
- Límites:
  - lecturas H0/H1 y SSE legacy sin guardia; la sesión local sigue pendiente;
  - revocar no cancela un job ya encolado;
  - el lote no continúa tras una recuperación sin otra autorización;
  - no hay cancelación de la reconciliación ni enmienda del código;
  - la evaluación y la reconciliación no se han ejecutado con CLI real.

  H4.1 no se ha iniciado.
