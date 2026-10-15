# P008-T006 — API y UI mínimas

Fecha: 2026-10-15. Base: D088, D080, D082 y cierre/plan posterior de D091. Decisión: [D093](../DECISIONS.md#d093--p008-t006-api-y-ui-del-contrato-unificado).

## Entrega

- `api/documents.py` proyecta el layout configurado para el visor. Instrucciones raíz en árbol y estado; clases
  `instructions`, `diagram`, `flow` y `phase_work`, además de las existentes. Las instrucciones no pasan a ser
  documentos adoptados por una fase. La proyección no toca la representación interna ni los snapshots históricos.
- `DecisionEntryRead` expone id, título y estado del registro único; fuera los campos de archivo, fecha y fase.
  El visor enlaza al encabezado de DECISIONS usando el mismo slug que el renderizador, incluidos acentos y Markdown.
  Los ejemplos del router y Markdown usan DECISIONS, flows y el resto de rutas actuales.
- Retirados POST `/projects/{id}/bootstrap`, `/bootstrap/preview`, `/bootstrap/discovery` y ambos POST
  `/phases/{id}/transition…`, con sus esquemas de entrada. Las rutas inexistentes dan 404; POST a la ruta con solo GET
  da 405. `Bootstrap.tsx` eliminado y sin consumidores. GET `/projects/{id}/bootstrap` mantiene exclusivamente
  `enabled`, `import_required`, `diagnostic` y `definition_operation` para la creación conversacional.
- Las operaciones y runs históricos conservan sus tipos en las lecturas. La conciliación interna de las intenciones
  de transición ya selladas permanece en el motor; ninguna intención ni historial se recalcula o reescribe.
- Cierre y abandono explican el archivo unificado. La fase cerrada enlaza a la sucesora; la ACTIVE sin tareas ofrece
  planificación propia, por texto o propuesta. Revisa diff/hash, pide motivo y confirmación y conserva la clave de
  envío idempotente. Cambiar versión u origen del plan descarta la vista previa. Las conversaciones anteriores
  conservan su historial; solo la ACTIVE sin tareas permite nuevos mensajes desde esta UI.
- Registro sin selector opcional de layout: siempre envía `documents = "v2"`, igual que la composición obligatoria.
  OpenAPI y tipos TypeScript regenerados con los comandos de ARCHITECTURE §9. Sin dependencias nuevas.

## Verificación

- 12 checks ligeros de `unittest`: correctos.
- Pruebas Node: 73 correctas, incluida la correspondencia entre el enlace de decisión y el encabezado renderizado.
- `npm --prefix frontend run build`: correcto, incluye `tsc --noEmit`. Aviso de Vite sobre chunks de más de 500 kB;
  no se rediseña ni se cambia el empaquetado en esta tarea.
- 12 pruebas de `test_document_viewer.py`: correctas. Incluyen cinco casos nuevos: proyección HTTP con `docs` o una
  carpeta personalizada, instrucciones raíz y su rechazo de symlinks, y edición confirmada con CAS de cada archivo
  de instrucciones. Las lecturas conservan HEAD y el checkout.
- Dos recorridos HTTP de cierre → sucesora ACTIVE vacía → plan confirmado: correctos, por texto y por propuesta de
  una conversación con agente falso; exigen Idempotency-Key y rechazan la vista previa con hash falso.
- Primera suite dirigida: 186 correctas y un fallo de una aserción que esperaba `operation` en el GET de estado.
  Esa aserción se actualizó al contrato nuevo; la suite completa final comprueba la corrección.
- Ocho Markdown editados/nuevos: 235 enlaces relativos/anclas válidos, bloques y presupuestos correctos; ROADMAP
  conserva ocho fases, NEXT_STEPS sus 15 tareas y DECISIONS indexa 93 decisiones sin duplicados.
- Tres diagramas Mermaid válidos con el parser local 11.17.2: solo sintaxis, sin DOM ni render; sanitizador sustituido
  en ese proceso efímero. Las pruebas Node del visor comprueban su tratamiento seguro de Markdown.
- Revisión semántica de OpenAPI: exactamente cinco operaciones retiradas, ninguna nueva; sin referencias a las
  carpetas retiradas en API ni UI. Diff revisado y sin errores de whitespace.
- Suite completa de pytest: 1.163 correctas y 121 subtests; un fallo en la igualdad entre OpenAPI exportado y el
  runtime. Se habían regenerado las descripciones de los esquemas durante la suite, cuyo proceso conservaba las
  importaciones anteriores. Re-ejecutado `test_storage_api.py` en un proceso nuevo: 10 correctas, incluida la igualdad
  exacta de OpenAPI y la comprobación de que su exportación no crea SQLite. No se repitió la suite completa.
  Único aviso de pytest: deprecación conocida de Starlette/httpx, ajena a esta tarea.

Sin modelos ni migraciones: no se ejecuta `alembic check` independiente. No se arranca el harness sobre este checkout,
ni se ejecutan proveedores reales, smokes, push o publicación. Sin comprobación visual en navegador.
