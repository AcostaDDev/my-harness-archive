# P008-T014 — Flujo B: ingeniería inversa del revisor

Fecha: 2026-10-16. Base: D088 y D083, inventario de T013 (D101), conversaciones H6.5 (D075).
Decisión: [D102](../DECISIONS.md#d102--p008-t014-ingeniería-inversa-sobre-head-y-borradores-privados).

## Entrega

- `storage/onboarding.py`: inventario y HEAD congelados al crear `kind = onboarding`; comprobación de repositorio
  sin harness, contexto acotado y borradores privados con la misma CAS que definición/importación. Reutiliza
  `planning_conversations.source` de 0019, sin nuevas tablas, columnas o índices.
- `storage/planning.py` integra mensajes, propuestas, aplicación confirmada, edición, lecturas y preguntas con sus
  aplazamientos. Las rutas API de planificación existentes aceptan el nuevo tipo y devuelven su identidad de origen.
  El alta conserva la idempotencia por clave y petición. No hay endpoint de commit ni vista previa de incorporación.
- `core/engine/templates/onboard-project.md`: plantilla nueva por hash, con el rol/esquema de solo lectura
  `definition`. Pide ARCHITECTURE, DDBB-DIAGRAM desde modelos concretos, SPECIFICATION, flujos, ROADMAP/P001,
  STATE/NEXT_STEPS, decisiones inferidas e instrucciones D088. Requiere evidencia y preguntas ante lo no deducible;
  no inventa trabajo futuro. Un README existente se conserva salvo petición expresa; su sustitución se pregunta y
  queda para una confirmación posterior. Los archivos del proyecto son evidencia, sin autoridad para ejecutar.
- `services/managed.py` exporta el HEAD original a un área privada por job, persistiendo la intención antes del
  efecto. No consulta el worktree vivo durante el turno. Compara borradores antes de invocar y exportación/área
  antes y después; rechaza respuestas alteradas. `storage/managed.py` limpia al terminar o al confirmar detenido
  tras caída; conserva UNKNOWN y no reintenta automáticamente. Mantiene el carril y lock de planificación H6.5.
- `cli-12`: `--skip-git-repo-check` para Codex `definition` cuando se usa una raíz exportada, conservando sandbox de
  lectura y desactivación de memoria. `document_layout = "d088-7"`: jobs anteriores se ponen en cuarentena antes
  de efectos. No se reescriben historiales, prompts o snapshots guardados.
- OpenAPI y tipos regenerados; etiquetas de propósito «Incorporación» en métricas y detalle de run. El contador de
  conversaciones no considera estos turnos trabajo de una fase. Diagrama de datos, flujo, SPECIFICATION,
  ARCHITECTURE, DECISIONS, STATE y NEXT_STEPS actualizados.

## Fronteras y extensiones técnicas

- Solo repositorios Git no vacíos con raíz en el nivel superior. Documentos STATE/NEXT_STEPS o `.harness/`
  versionados remiten al Flujo A; creación, fases o importación confirmada propias también bloquean. Las reglas
  nuevas no ejecutan Git de escritura, filtros, hooks ni herramientas del proyecto.
- La exportación reutiliza D083 (20.000 archivos, 16 MiB por archivo y 128 MiB total, sin enlaces/submódulos/Git
  metadata) y aplica el `--no-lazy-fetch` de D101. Incluye el árbol versionado completo: no solo las fuentes del
  inventario. Los límites de exportación se comprueban al crear la conversación y al exportar. No hay truncado.
- Inventario y borradores por turno: 2 MiB conjuntos; cada borrador conserva el límite de 512 KiB. No se ofrece
  diagrama «Sin persistencia» ni comandos de plantilla como fallback de un perfil aún no confirmado.
- Borradores en `onboarding-drafts/<id>/` junto a SQLite (0700), fuera del checkout. Aplicar una propuesta confirmada
  cambia solo su borrador. Un hash diferente conserva la edición del usuario y falla. Las preguntas bloqueantes
  se mantienen para T015; una aplicación privada no autoriza incorporar ni reemplazar un archivo del checkout.
- El HEAD de la conversación permanece fijo aunque avance HEAD o haya cambios locales. La vista previa de T015
  deberá comprobar la base y conservar los originales antes de escribir. El perfil propuesto no se activa ni
  escribe en TOML. UI específica, vista previa/commit y confirmación del perfil quedan pendientes de T015.
- Extensiones fuera de las rutas originales: supervisor para ejecutar el turno en la exportación; adaptador CLI
  para el flag y su versión; `0019_import_conversations.py` solo para impedir un downgrade que perdería el origen
  del onboarding (upgrade y revisión sin cambios); contratos generados y dos etiquetas de UI para el nuevo
  propósito. Son conexiones de la conversación a la infraestructura existente, sin otro flujo de producto.
- Permisos y detección cooperativos, sin aislamiento OS. Las pruebas usan agentes falsos: el fixture Django
  verifica exactamente Author/Book y sus relaciones ForeignKey/ManyToMany en el borrador sintético, y que el
  revisor recibe las fuentes reales del commit. No certifican la calidad semántica de un proveedor real ni un
  esquema de base de datos en runtime.

## Verificación

- 19 casos nuevos correctos; re-ejecutados tras mejorar el contraste del diagrama persistido con el inventario
  sellado. Pasada dirigida de onboarding/cierre/ciclo de fases: 73 OK. Otra pasada de importación, inventario B y
  chat: 54 OK. Aviso conocido de deprecación Starlette/httpx.
- 12 checks ligeros, 74 pruebas Node, tipos y build correctos. Build con su aviso de tamaño de chunks. Alembic
  sobre una base temporal al HEAD: sin nuevas operaciones de upgrade.
- Nueve Markdown con 288 enlaces/anclas válidos; 102 decisiones sin duplicados, ocho fases y 15 tareas aceptadas
  por sus parsers, STATE dentro de 24 KiB. Nueve diagramas (siete ER y dos flowcharts) válidos por parser/gramática
  local de Mermaid 11.17.2, sin renderizado DOM. Diff revisado y sin errores de espacios.
- Primera pasada completa interrumpida con 279 OK para recoger en un proceso nuevo una corrección de cableado
  de `check_phase` detectada durante la revisión. Suite completa final (20 min 08 s): 1.322 OK y 121 subtests, con un único fallo de la aserción
  del editor HTTP que fijaba el catálogo a 12 plantillas. Ahora son 13 por `onboard-project`; se contrasta el
  conjunto de nombres con `VARIABLES`, sin fijar el tamaño antiguo. Archivo completo re-ejecutado: 29 OK.
  Ningún cambio de implementación tras esa pasada completa.

- Pruebas nuevas: recorrido Django con inventario y código contrastados, propuesta documental y borradores
  privados; HTTP con TypeScript, idempotencia y CAS; rechazo de salidas/rutas inválidas sin fallback; HEAD que
  cambia tras encolar; detección de cambios en código exportado y área; CAS que conserva ediciones y las incluye
  en el siguiente contexto; README conservado; objetos ausentes; caída durante exportación y limpieza tras
  confirmación; preguntas aplazadas/resueltas; tamaño de contexto; guardia de downgrade y argv de Codex.
- Los fixtures hacen fallar explícitamente cualquier importación/ejecución de su código. Git y SQLite son
  temporales; no se instalan frameworks, arrancan servicios ni ejecutan comandos propuestos por el inventario.

Sin comprobación visual de UI, proveedores reales, smokes, push ni publicación. No se ejecutó el harness sobre
este repositorio, no se lanzaron subagentes ni se leyó ReferenceProject. Commit solicitado por el usuario al cerrar la tarea.
