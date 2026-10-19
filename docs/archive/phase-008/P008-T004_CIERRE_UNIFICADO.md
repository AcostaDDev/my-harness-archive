# P008-T004 — Cierre y archivo unificados

Implementación de D088 punto 4 y [D091](../DECISIONS.md#d091--p008-t004-cierre-y-archivo-unificados-con-planificación-posterior).
Trabajo manual sobre este repositorio, sin registrarlo ni ejecutarlo con el harness.

## Resultado

- El cierre ya no requiere otra transición ni un plan de N+1. Congela la instantánea documental y SQLite, vuelve a
  comprobar READY, persiste la intención del commit antes del tag y crea el tag sobre el HEAD evaluado. Después
  aplica CAS de archivos y registra un único commit de archivo.
- STATE/NEXT_STEPS originales se conservan por bytes. REVIEW y SUMMARY son proyecciones SQLite. Los artefactos de
  `docs/phase/` se mueven al archivo, incluidos binarios, CRLF y subcarpetas. El destino de archivo debe estar ausente;
  una colisión con los cuatro documentos del archivo, un enlace u objeto no regular se rechaza antes de escribir.
- El commit deja STATE nuevo con la base acumulada, NEXT_STEPS con objetivo y criterios de N+1 sin tareas, y ROADMAP
  con estado completada y enlace en Archivo. Al registrar el commit, SQLite cierra N y crea N+1 ACTIVE con sus hashes
  adoptados. Sin sucesora no se crea fase. El abandono comparte la operación con destino ABANDONED, sin READY ni tag.
- El check exige compactar STATE >24 KiB o Base acumulada >12 KiB antes de llamar al revisor. No se trunca texto.
- El plan de la fase activa vacía llega por texto o propuesta de `phase_planning`: vista previa, hash confirmado,
  commit documental y versión nueva de la definición (D034). STATE y NEXT_STEPS reflejan el plan confirmado.

## Recuperación y compatibilidad

La intención persiste árbol, commit, bytes, hash anterior y posterior. Los movimientos usan contenido base64 y
borrado explícito para poder recuperar una escritura parcial sin reemplazar bytes externos. Tras confirmar el
escritor detenido, una nueva petición explícita reanuda el mismo run e intención, aun si el commit ya existe.
La sucesora se registra atómicamente una sola vez. Los snapshots e historiales anteriores no se reescriben.

Las nuevas transiciones H6.3 se rechazan; sus intenciones selladas pendientes siguen conciliando. Se permite solo
para ese escritor el salto de versión documental d088-1/2 → d088-3 si el resto del contexto y versiones coincide.
El run conserva sus versiones originales. Los productores anteriores se simulan en el fixture explícito
`_legacy_close` para mantener las pruebas de sus snapshots; las pruebas nuevas usan el productor real.

## Alcance técnico

Se reutilizan operaciones, jobs, locks, autorizaciones y definiciones existentes; no hay migración ni cambio de modelo.
`MechanicalUpdate` añade base64 y borrado con UTF-8 por defecto al leer intenciones anteriores. Esto exige ampliar
`adapters/git.py`, además de las rutas inicialmente enumeradas en T004. Los endpoints mínimos de planificación y el
cambio de autorización del abandono requieren regenerar `frontend/openapi.json` y `frontend/src/api.generated.ts`.
Son extensiones técnicas para completar esta tarea, sin cambios de diseño ni dependencias nuevas.

`document_layout = "d088-3"` distingue los jobs nuevos. Los demás jobs de versiones anteriores se detienen con la
guardia habitual. El abandono exige ahora Idempotency-Key; su PhaseRead puede mostrar CLOSING hasta que termine el
job. La adaptación completa de UI, los prompts y la retirada final de endpoints antiguos quedan en T005/T006.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks ligeros en verde.
- Suite pytest completa: 1.142 pruebas correctas y 121 subtests; dos fallos en fixtures de métricas que aún creaban
  el protocolo anterior. Corregidos para usar el productor histórico y repetido todo `test_metrics.py`: 27 OK.
  La nueva prueba conversacional añadida después de arrancar esa suite está incluida en las repeticiones de T004.
- Tras los ajustes finales, Git, exportación, fases y cierre: 113 pruebas en verde (4 de lote deseleccionadas en esta
  repetición; están incluidas en la suite completa). Los 22 casos del cierre nuevo incluyen el archivo exacto binario
  y CRLF, idempotencia, rechazos previos, caídas tras tag/escritura parcial/borrado/commit/registro, abandono, última
  fase sin sucesora, tags anotados, límites de STATE, plan por texto y conversación, endpoints y transición antigua.
- OpenAPI exportado sin conectar SQLite y tipos regenerados. 72 pruebas Node en verde; `npm --prefix frontend run
  build` correcto (incluye `tsc --noEmit`). Aviso habitual de Vite por chunks >500 KiB.
- Dos diagramas de `flows/phase-lifecycle.md` aceptados por el parser Mermaid 11.17.2 local, sin DOM ni render;
  DOMPurify sustituido solo para comprobar sintaxis. Siete Markdown editados/nuevos sin enlaces o anclas rotos ni
  bloques mal formados; DECISIONS indexa 91 decisiones únicas; ROADMAP y las 15 tareas de NEXT_STEPS se parsean;
  STATE y NEXT_STEPS cumplen sus presupuestos. `git diff --check` correcto.

Pytest conserva el aviso de deprecación de Starlette sobre httpx, ajeno a la tarea. No se ejecutó `alembic check`
como comando independiente: no cambian modelos ni migraciones; las pruebas de migración usan SQLite temporal.

## Límites

Se mantiene el límite existente de 512 KiB por documento/artefacto y el límite Git de diff del escritor; se rechaza el
exceso explícitamente. La base acumulada debe compactarse antes del cierre. No se cambian plantillas de prompts en
esta tarea. No se ejecutaron proveedores reales, smokes, harness sobre este checkout, push ni publicación.
