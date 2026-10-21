# P009-T012 — QA conjunto y cierre del piloto Django

Fecha: 2026-10-21. Base del harness: `bc4a086`; wheel instalado de `5ba32f8` (T020), sin reconstrucción.
Autorización: petición de continuar la siguiente tarea, D121 y propuesta §§3–6; reanudaciones HITL según se indican.
Techo T012: 2 invocaciones; acumulado inicial: 24 de 60. **Detenida tras primer check REVISE; pendiente de respuesta HITL para reanudar.**

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

## Revisión de salida de P009 y comprobaciones

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
