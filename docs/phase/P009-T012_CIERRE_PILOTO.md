# P009-T012 — QA conjunto y cierre del piloto Django

Fecha: 2026-10-21. Base del harness: `bc4a086`; wheel instalado de `5ba32f8` (T020), sin reconstrucción.
Autorización: petición de continuar la siguiente tarea, D121 y propuesta §§3–6; reanudaciones HITL según se indican.
Techo T012: 2 invocaciones; acumulado inicial: 24 de 60. **Resultado final: completada tras autorización HITL.
P001 CLOSED, tag `p001`, archivo en `3d105c6`; T012 2 de 2 y piloto 26 de 60.**
Decisión final [D139](../DECISIONS.md#d139--p009-t012-completada-piloto-django-con-p001-cerrada-y-archivada).
La primera sesión y su parada se conservan debajo; la reanudación está al final.

## Preparación, parada y QA

- Hashes de Codex 0.163.0 y Claude 2.1.304 idénticos a la propuesta §1. Preflight con
  `version_help_match` en los seis roles/presets. Hijo limpio en `a2de6ad`, registro v4 conservado;
  las cuatro tareas anteriores COMMITTED. Ningún harness sobre este repositorio.
- Servicios desde el área autorizada, puertos 8031/8032. `serve` con TMPDIR privado, Django con
  `PYTHONDONTWRITEBYTECODE=1`. Seguimiento en UI/artefactos; SQLite operativa solo leída con `serve` detenido.
- Primer GET del Django: 500 `no such table: core_task`; una migración pendiente. Parada sin proveedores.
  Diagnóstico de solo lectura: `django_migrations` no contiene `core.0001_initial`; no hay tabla `core_task`.
  La migración aceptada existe y solo crea Task. El perfil valida la base de tests, no migra la SQLite de uso.
- HITL: el usuario autoriza «Aplicar la migración y reanudar T012». Copia SQLite privada en
  `state/t012/django-before-migrate.sqlite3`; `migrate --noinput` aplica únicamente `core.0001_initial`.
  Sin edición de código ni configuración. Se conserva la primera parada en la propuesta §13.
- QA en Chrome del mismo Django, con una tarea sintética desechable: alta/listado; edición conserva descripción;
  título con `<b>literal</b>` se muestra como texto; búsqueda `  ALPHA  ` recorta espacios y encuentra el título;
  completar desde pendientes mantiene búsqueda/filtro y deja vacío; completadas muestra la tarea;
  reabrir conserva filtro/búsqueda y deja vacío; pendientes vuelve a encontrarla; GET de borrado pide confirmación;
  cancelar conserva la tarea; POST confirmado la elimina y vuelve al listado vacío. La tarea QA se retira desde la UI.
  No se usa recarga tras el POST de alta: sigue sin patrón POST→redirect→GET (observación de T008).

## Check de fase: primera revisión

Operación `82cc4650-fff6-46d8-9311-3bfb03afc7d0`, run `400d5d48-3382-488d-b2a2-62434b5b6719`.
HEAD evaluado `a2de6ad`, árbol limpio. Las seis validaciones pasan: pytest/JUnit (27 tests), Ruff lint,
Ruff formato, mypy, check Django y makemigrations sin cambios. JUnit completo SHA-256
`588e6747b8d53a62c2c38aa763b99b193e24343b849b409885ef42c305fa9edd`.

Claude `claude-sonnet-5-5`/`medium` devuelve **REVISE**: cuatro de cinco criterios pasan; falla la paridad del flujo
por el nodo `R` duplicado y el título incompleto. Pide además consolidar las propuestas ADR de T003/T004,
refrescar la prosa obsoleta de STATE y comprobar sus presupuestos. Sin preguntas bloqueantes. No se cierra.
Servicios detenidos al recibir el veredicto; sin reintento automático. Corrección concreta en
[P009-T012_CORRECCION_DOCUMENTAL](P009-T012_CORRECCION_DOCUMENTAL.md).

Métricas de este intento (`attempt_metrics` y stream): 31,628 s de pared; 11 turnos normalizados;
entrada 10, caché leída 50 048, caché creada 22 579, salida 4349, razonamiento 492;
coste equivalente reportado 0,1388308 USD. Modelo reportado Sonnet, esfuerzo solicitado sin medición independiente.
Consumo tras REVISE: T012 1 de 2; piloto 25 de 60.

## Matriz de las cuatro tareas aceptadas

Luna = Codex `gpt-6-luna`; Sonnet = Claude `claude-sonnet-5-5`. Todos los esfuerzos son `medium`.
El usuario fija revisor/modelo/esfuerzo y proveedor/catálogo del ejecutor; el revisor elige el ejecutor concreto.

| Tarea hija / piloto | Run aceptado | Revisor del usuario | Ejecutor elegido | Motivo del revisor | Registro | Validación | Commit |
|---|---|---|---|---|---|---|---|
| P001-T001 / T008 | `7fbaf89c` | Luna | Luna | Coordinar modelo, migración, formulario, vistas, plantillas, tests y documentación, con alcance acotado | v1 | 3 tests; 6/6; ACCEPT | `98f4611` |
| P001-T002 / T009 | `bf007561` | Luna | Sonnet | Feature Django acotada, convenciones establecidas y criterios explícitos | v2 | 11 tests; 6/6; ACCEPT | `2f2b13f` |
| P001-T003 / T010 | `beaf4528` | Sonnet | Sonnet | Vistas, plantilla, tests y flujo sobre un campo existente; riesgo bajo | v3 | 22 tests; 6/6; ACCEPT | `882af9b` |
| P001-T004 / T011 | `6bb55757` | Sonnet | Luna | Extender filtro existente, cuatro archivos y sin modelos; riesgo bajo-medio | v4 | 27 tests; 6/6; ACCEPT | `a2de6ad` |

Configuraciones y políticas congeladas contrastadas en `managed_runs.context_json` y selección/motivo en
`history_json`; los cambios de registro no alteran los intentos anteriores. Los argv reales están contrastados
en la evidencia de cada tarea. Streams Claude reportan Sonnet; Codex no reporta un modelo independiente.
El esfuerzo efectivo no se mide independientemente en ninguna CLI. No se confunde lo solicitado con lo reportado.

| Piloto | Pared plan/ejecución/revisión del run aceptado | Invocaciones acumuladas de la tarea | Intervenciones y límites |
|---|---|---|---|
| T008 | 13,412 / 139,048 / 10,940 s | 6 de 10 | Bloqueo por rutas, T017; reinicio/inodo, T018; limpieza autorizada y nuevo run; commit confirmado |
| T009 | 16,712 / 39,528 / 8,779 s | 9 de 13 | Límite de formato, T019; recuperación del servicio y nuevo run; copia privada; commit confirmado |
| T010 | 22,666 / 35,415 / 9,707 s | 3 de 7 | Cambio de revisor, selector y confirmación UI; usuario conserva el mensaje español ya creado |
| T011 | 22,530 / 59,883 / 12,532 s | 3 de 7 | Cambio de ejecutor; notas para título inglés y confirmación UI |

Duraciones de pared de `attempt_metrics.wall_ms`, no duración total humana de las sesiones. Cada run aceptado
consume tres invocaciones, pero los totales incluyen intentos anteriores conservados. T007 consumió 3; T008–T011,
21 en total: 24 antes de T012. Sin una medida completa del tiempo humano ni del coste monetario del piloto.
Los costes reportados de Claude para los runs aceptados son 0,1054898 USD (T009), 0,2995099 (T010) y
0,1532088 (T011); Codex carece de coste reportado. No son factura ni coste completo de las tareas.
Tokens/turnos tienen semánticas distintas entre CLI: no se agregan ni prueban una clasificación de calidad
entre modelos, y cuatro tareas distintas tampoco permiten esa conclusión.

## Revisión de salida de P009 y comprobaciones al detener la primera sesión

| Criterio de ROADMAP | Evidencia y resultado al detener T012 |
|---|---|
| Carpeta elegida explícitamente y concesión limitada | T002/D117 y elección UI de T007/D127; cumplido |
| Creación desde cero, destino visible y recuperación | T002–T005 y T007; hijo creado/definido/preparado desde UI, sin scaffold manual; cumplido |
| D088, Django, dependencias fijadas y validaciones reales | T004/T005/T007 y seis validaciones actuales verdes; migración local pendiente resuelta por HITL |
| Agentes elegibles por proyecto y selección del ejecutor motivada | Registros v1–v4 y cuatro contextos/selecciones congelados contrastados; cumplido |
| Cuatro parejas COMMITTED en el mismo proyecto | Matriz anterior y commits alcanzables desde `a2de6ad`; cumplido |
| CRUD, estado y búsqueda; QA, tests, READY y archivo | QA y 27 tests correctos; **pendiente READY/cierre/archivo por REVISE documental** |
| Checks offline y ensayo previos; revisión de salida | T005/T015/T020 y evidencias anteriores; revisión actual registra hallazgos y límites, P009 no se cierra |

- Harness en esta entrega: 12 checks unittest correctos; 395 enlaces/anclas relativos de los siete documentos
  modificados/nuevos válidos; 138 decisiones únicas y ordenadas; STATE y NEXT_STEPS dentro de presupuesto;
  diff revisado y `git diff --check` correcto.
- Sin repetir pytest completo del harness, Node, tipos/build, Alembic ni wheel: solo cambia documentación del
  harness. Las seis validaciones del hijo se ejecutan mediante el check del producto. No se añaden tests ni
  fixtures derivados de runs, ni se cambia esquema, API, perfiles, modelos o flujos del harness.
- Limpieza: ambos servicios terminan con salida 0, puertos 8031/8032 libres; `integrity_check = ok`, cero locks,
  ningún job en cola/en ejecución (16 DONE y un INTERRUPTED histórico), 25 intentos acumulados.
  El proceso del revisor del check figura STOPPED; PID y grupo comprobados muertos. Originales privados en
  el área operativa; este documento contiene solo resumen saneado. Hijo limpio en `a2de6ad`.
- Límites: no READY, tag, commit de archivo ni fase cerrada; no presentar el piloto como conseguido todavía.
  El check admite no haber contrastado cada punto con SPECIFICATION y se apoya también en tests/revisiones;
  su veredicto no sustituye al QA funcional. Quedan el patrón POST→redirect→GET del alta (observación previa),
  aclarar marcadores opcionales de define-project y la corrección documental ya propuesta.
- Siguiente: respuesta HITL a la corrección, edición confirmada desde el producto sin agentes, y nuevo check
  con la llamada restante a Sonnet/medium. Solo READY permite cierre/archivo de P001. La planificación posterior
  del hijo y el cierre documental de P009 quedan fuera de T012.

## Reanudación autorizada: corrección, READY y cierre

Continuación desde `c9b6d24`, el 2026-10-21. El usuario no vio la pregunta interactiva; se le repite en el chat
el alcance exacto y responde «Autorizo». La propuesta §14 registra esa autorización, manteniendo el techo de dos
llamadas. Hashes CLI idénticos y preflight correcto en los seis roles/presets; mismo wheel de T020, sin instalar
otro ni alterar selecciones (registro v4). No hace falta repetir el QA de comportamiento: solo cambian documentos.

[Corrección aplicada](P009-T012_CORRECCION_DOCUMENTAL.md): editor UI, preview/diff/hash y confirmación separada
para flujo, STATE y DECISIONS; commits ingleses `2f23d3d`, `0787bff` y `47a0557`, todos COMMITTED y adoptados.
Sin edición directa del checkout ni agentes para escribir. Los bloques gestionados se preservan; el índice de
DECISIONS lo regenera el producto. STATE: 4298 bytes totales y 572 bytes de sección base incluida su cabecera.
El árbol está limpio y la UI no muestra deriva antes del check final.

### Check final

- Operación `9f9bdb44-b833-4fa3-bcb5-496d3f4f70c9`, run `21f607d3-7c6b-4683-825d-c6d26d834c1d`.
  Claude `claude-sonnet-5-5`/`medium` devuelve **READY** sobre `47a05571f9eaecbc45ad0d8c3794cd21368d3638`.
  Vínculo `d61549f4668a3c8ae04c7210c11ca83a30b89d94b0c3e59251c110091e70170b`; sin deriva, preguntas ni acciones.
- Los cinco criterios pasan: tareas COMMITTED en orden; validación y métodos; cobertura individual e integrada;
  paridad del modelo/flujo con los documentos; validaciones del perfil. El revisor contrasta SPECIFICATION,
  diagrama ER y flujo, y reconoce las dos decisiones consolidadas. La prosa y el bloque de STATE reflejan una
  comprobación anterior: no bloquean y el archivo conserva sus bytes históricos.
- Seis comandos con salida 0: 27 tests pytest, Ruff lint, Ruff formato, mypy, check Django y makemigrations
  sin cambios. JUnit completo de 27 casos, SHA-256
  `8b658c43095412ce4ccfff26468f4b75cf777ead05e7aba15dccc69d5526c040`.
- Métricas (`attempt_metrics` y stream): pared 26,142 s; duración CLI 25,062 s; 13 turnos reportados;
  entrada 12, caché leída 80 076, creada 19 954, salida 3703, razonamiento 180; coste equivalente reportado
  0,1248776 USD. Argv conservado: `--model claude-sonnet-5-5 --effort medium`; stream reporta Sonnet,
  esfuerzo efectivo ausente. Las dos revisiones suman 57,770 s de pared y 0,2637084 USD reportados, no factura.
- T012 agota sus **2 de 2**; piloto **26 de 60**. Ediciones y cierre no invocan agentes. El margen global no
  autoriza llamadas adicionales para T012 ni operaciones nuevas del hijo.

### Cierre y archivo comprobados

Autorización del usuario aplicada desde UI sobre el READY exacto, con motivo y casilla de cierre. Operación
`d2e45cf7-35de-4a36-9726-05dc2b10d276`, run `99852943-d00d-429c-95b8-ad36d72bd17b`, termina **CLOSED**.
Tag ligero `refs/tags/p001` sobre el HEAD evaluado `47a0557`; commit de archivo
`3d105c6669194f3014a06220d14c35d085e880d7`, mensaje inglés `harness: archive P001`, árbol
`4f3927a8ae91bb008a945056c77dd62b22f5827d`. Sin reconciliación ni duplicados.

- `docs/archive/phase-001/` contiene STATE, NEXT_STEPS, REVIEW y SUMMARY. Los dos primeros son idénticos por
  bytes a los del HEAD READY (hashes `a6d5cff8…ea6bd2` y `90fd6a67…77f4aa`). REVIEW conserva READY y los
  cinco criterios; SUMMARY muestra CLOSED, cuatro tareas y consumo con procedencia.
- No había artefactos en `docs/phase/`; la carpeta sigue ausente, sin contenido pendiente. El cierre solo toca
  siete rutas documentales. Código, entorno y datos no cambian. Documentos vivos renovados, base acumulada
  conservada y ROADMAP con P001 completada y enlace al archivo. Sin fase activa ni sucesora; no se planifica otra.
- Git limpio en `3d105c6`, cuatro commits aceptados alcanzables, un solo tag `p001` y un cierre CLOSED.
  El resumen del producto cuenta 23 intentos de P001 (incluye los fallidos conservados y ambos checks); el
  acumulado del piloto es 26 porque incluye también los tres turnos de definición de T007. Se conservan las
  ausencias de métricas: un intento interrumpido no tiene consumo completo; no es cero ni coste total conocido.
- UI comprobada y captura inspeccionada: P001 «Cerrada» y las cuatro tareas «Commit hecho». Observación sin
  bloqueo: la vista de la fase cerrada sigue comparando los documentos vivos renovados con su base histórica y
  muestra STATE/NEXT_STEPS/ROADMAP como cambiados; el cierre persistido, Git y los archivos sí son correctos.
  No se adopta otra base ni se alteran documentos archivados para quitar ese mensaje. Se propone revisar esa
  presentación en una tarea acotada posterior.
- Limpieza final: sesión cerrada y `serve` detenido con salida 0; no se relanza runserver en esta continuación.
  Puertos 8031/8032 libres, `integrity_check = ok`, cero locks, 21 jobs DONE y un INTERRUPTED histórico,
  ningún job pendiente, 26 intentos. Revisor final STOPPED, PID y grupo muertos. Prompts/streams/SQLite y copia
  de la base permanecen privados; sin cambios globales, push ni publicación.

## Revisión final de salida

Todos los criterios de la tabla anterior quedan acreditados: el criterio combinado de QA/tests/READY/archivo
se completa con el cierre comprobado. Se consigue el piloto operativo del mismo Django con las cuatro parejas;
la evidencia cubre macOS arm64/Python 3.13.13 y no demuestra portabilidad ni superioridad de un modelo.
No se corrigen aquí las observaciones de alta sin POST→redirect→GET, marcadores de define-project ni la
presentación de deriva tras cerrar. La migración local pendiente se resolvió como operación explícita del
usuario; no se añade aplicación automática de migraciones al producto.

En el harness, solo cambian documentos: STATE/NEXT_STEPS/ROADMAP, decisiones, propuesta y evidencias, más las
referencias vigentes de SPECIFICATION/ARCHITECTURE que aún negaban el piloto real. Sin cambios de código,
esquema, OpenAPI ni flujos del harness. Checks de esta continuación: 12 unittest, enlaces/anclas, orden de
ADR, presupuestos y diff: 422 enlaces/anclas relativos válidos, 139 decisiones únicas y ordenadas, STATE
(16 833 bytes), base (4358 bytes) y NEXT_STEPS (43 209 bytes) dentro de sus límites; `git diff --check` correcto.
Sin repetir pytest completo, Node, tipos/build, Alembic ni wheel por ser documental.

Siguiente: revisar esta salida y cerrar/archivar documentalmente **P009 del harness en otra tarea**. P009 no se
cierra aquí; tampoco se planifica otra fase del hijo ni se invocan más proveedores.
