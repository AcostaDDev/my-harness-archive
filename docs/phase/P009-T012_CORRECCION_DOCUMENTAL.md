# P009-T012 — Corrección documental propuesta tras REVISE

Fecha: 2026-10-21. Check `82cc4650`, run `400d5d48`. Pendiente de autorización HITL.
Sin aplicar al hijo. El QA funcional ha pasado, y las seis validaciones también (27 tests).

## Cambios exactos propuestos

1. `docs/flows/tasks.md`: título «Flujo de tareas — alta, listado, edición, borrado, estado, filtros y búsqueda».
   Solo en el diagrama de estado/búsqueda: `F --> R{¿Hay resultados?}` pasa a `F --> H{¿Hay resultados?}`;
   las dos aristas de resultados parten de `H`. `C --> R[Botón Reabrir: POST con CSRF]` y `R --> X` permanecen.
2. `docs/STATE.md`: sustituir únicamente la prosa inicial por una sección «Base acumulada» que indique Django,
   SQLite, plantillas, entorno fijado y CRUD/estado/filtros/búsqueda; sección «Fase activa — P001» con las cuatro
   tareas COMMITTED en orden, 27 tests y seis validaciones, QA pasado y cierre pendiente. Preservar el bloque
   gestionado: el producto lo regenera. Verificar base <12 KiB y total <24 KiB.
3. `docs/DECISIONS.md`: conservar el registro y añadir D001 y D002 con estado aceptado, fecha y fase P001.
   D001 consolida la propuesta de T003: completar/reabrir solo por POST con CSRF, `status` oculto normalizado
   a pending/completed/all, inválido como all; evita GET mutador y redirección abierta.
   D002 consolida la propuesta de T004: búsqueda GET `q`, trim, `title__icontains`, combinación y conservación
   de `q`/`status`, ORM y autoescape, sin cambio de modelo. El índice lo regenera el producto.
   Sustituir la frase «No hay decisiones…» por una introducción coherente con las dos decisiones aceptadas.

## Operación propuesta

Ediciones confirmadas desde el editor documental del producto, con preview/diff/hash, commits ingleses y adopción
por el harness. Sin editar código, SQLite, TOML ni archivos del hijo a mano. Los commits de las cuatro tareas y
el primer check REVISE se conservan. Sin agentes para la edición. Repetir el check con la llamada restante a
Claude Sonnet/medium (T012: máximo 2; piloto: 25 de 60 antes de reanudar) y cerrar/archivar solo si READY.
Cualquier nuevo fallo detiene de nuevo. Sin planificar otra fase del hijo ni cerrar P009 del harness.
