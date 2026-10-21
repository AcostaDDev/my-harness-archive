# P009-T002 — Carpeta de proyectos y creación de hijos

Fecha: 2026-10-19. Aplica D116 §§2–3/6–9; decisión [D117](../DECISIONS.md#d117--p009-t002-carpeta-persistente-y-creación-con-intención-previa).
Entrega acotada de producto, sin operación real ni proveedores. Siguiente: P009-T003.

## Resultado y motivo

La persona puede guardar/retirar una carpeta padre explícita y crear un hijo nuevo, registrarlo y abrir la
definición documental existente. El permiso persiste por instalación y no se repite para cada hijo; la
confianza se confirma sobre el checkout nuevo exacto. El alta de carpetas existentes mantiene su propia
autoridad TOML. Esto elimina la preparación manual de la carpeta sin dar al agente acceso al padre/hermanos.

La UI separa ambas altas en «Nuevo proyecto», muestra el destino absoluto y la composición congelada, y
ofrece historial, diagnóstico, reanudación confirmada y cancelación. El sobre/clave de confirmación se guarda
en sessionStorage ante pérdida de respuesta o sesión; recargar permite reenviar explícitamente el mismo envío.

## Implementación

- `services/project_creation.py`: normalización sin `..`/NUL/enlaces, inspección Git estática, guardias de
  proyectos/estado, autoridad por revisión/identidad, preview y creación. Cada efecto corto usa transacción
  de escritura SQLite y el lock compartido con el registro. El padre se abre por componentes con O_NOFOLLOW;
  mkdir exclusivo por fd, identidad del hijo y fsync preceden al checkpoint. Los conflictos comparan
  ancestros/identidades físicos, incluidos alias de mayúsculas del filesystem y reservas aún sin carpeta.
  No ejecuta Git, agentes o red.
- `storage/project_creation.py`, modelos y migración `0021_project_creation`: singleton, historia de raíz,
  operaciones/reservas y eventos con cadena de hashes. Procedencia `creation_id` nullable fuera del JSON/hash
  D078; alta/evento/resultado en una transacción. ALTER aditivo conserva filas y eventos previos sin reconstruir
  la tabla padre con foreign_keys activas. Esquema vigente: 39 tablas.
- `LocalComposer`: la preview del hijo devuelve datos, valida sobre el padre existente y calcula los hashes
  del futuro destino; expone roles efectivos y resumen público del perfil/composición. La intención liga el
  hash del perfil completo incluso en v3, sin cambiar snapshots anteriores. No construye puertos para una
  carpeta inexistente. La composición operativa conserva los requisitos actuales. Formatos/hashes previos y contratos CLI/commands/codec/layout conservados.
- API estricta y guardias de sesión/Host/Origin/CSRF. Selección y confirmaciones con clave idempotente,
  versión y hash; tipos OpenAPI regenerados. No acepta ejecutables, entornos, una raíz alternativa al crear
  ni procedencia inventada por el cliente.

## Recuperación y límites

`INTENDED → DIRECTORY_CREATED → REGISTERED`, con BLOCKED/RECOVERY_REQUIRED/CANCELLED. La intención se sella
antes de mkdir. Un destino presente sin identidad persistida no acredita propiedad; el arranque solo lo
clasifica y conserva. Retirar/cambiar revisión bloquea efectos pendientes y conserva proyectos registrados.
La misma clave/payload devuelve la misma operación aunque se haya retirado la raíz; otro payload da 409.

Reanudar exige preview nueva y la misma identidad; reelección del padre solo puede autorizar un hijo vacío
con identidad acreditada. La autoridad nueva queda en fila/evento, sin reescribir intención/historia original.
Deriva de contenido, identidad o composición bloquea. Cancelar conserva bytes y reservas inciertas; solo
libera una reserva con ausencia acreditada. Una cancelación con reserva permite volver a comprobar ausencia
tras resolución externa, con nueva versión/clave, sin reabrir efectos. El alta existente tampoco puede
adoptar destinos reservados.
La contención es cooperativa, sin aislamiento del sistema operativo frente a modificaciones externas.

Presets de agentes v5, receta/scaffold/entorno Django y piloto siguen pendientes. La definición enlazada usa
los agentes globales del TOML. No se eligió una carpeta real del usuario, ni se modificó TOML/configuración
global. No se ejecutaron harness sobre este repositorio, proveedores, smokes, instalaciones, red o piloto.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Suite pytest completa: 1.472 tests correctos y 121 subtests, en tres lotes aislados de la colección
  completa (490 + 490 + 492, cada archivo una vez; sin proveedores ni red). La ampliación final de dos casos
  de alias se valida en la pasada dirigida siguiente: cobertura actual de 1.474 casos. La primera pasada
  secuencial detectó una aserción de esquema aún en 0020 y una comparación con OpenAPI cargado antes de su
  regeneración; se actualizó la aserción y se repitió con el contrato estable. No se omitió ningún test.
- Pytest dirigida final: 58 tests correctos de creación, registro y almacenamiento. Nombres y destinos ocupados/enlazados,
  raíz sin permisos/identidad cambiada, ausencia de elección y techo de bootstrap, configuraciones v3/v4,
  instalaciones independientes/reinicio, claves repetidas y payload distinto, reservas, cancelación y
  resolución externa, deriva de contenido/identidad/composición/perfil, cuatro puntos de caída, reelección,
  concurrencia entre runtimes y retirada entre checkpoint y alta. Alias físicos de mayúsculas no eluden
  estado del servicio, proyectos vacíos registrados o reservas anteriores a mkdir. API estricta y sin secretos/proveedores.
- Alembic upgrade/check en SQLite temporal: sin diferencias de metadata. Migración desde 0020 con fila/evento
  D078 conservados y foreign_key_check vacío; backup/restauración conserva autoridad/journal en consulta,
  sin recuperar ejecución. Paridad: 39 tablas y 413 columnas coinciden exactamente con DDBB-DIAGRAM.
- `node --test frontend/tests/*.test.mjs`: 77 tests correctos, incluidos sobre/clave tras perder respuesta,
  recarga/401 y rechazo definitivo. `npm --prefix frontend run build`: tipos y build correctos.
- OpenAPI exportado coincide con `create_app().openapi()`. Nueve rutas nuevas; ningún endpoint anterior cambia;
  solo se amplían RegistryRead y las lecturas de proyecto registrado con capacidad/procedencia.
- QA visual en Chrome con assets compilados y respuestas HTTP sintéticas en loopback: selección y confirmación
  de carpeta, nombre/destino, composición/roles, confianza, bloqueo y reenvío explícito tras perder respuesta y
  recargar. El servidor simulado no escribe carpetas de producto ni ejecuta el harness. Pestaña/servidor retirados.
  [Captura con datos sintéticos](P009-T002_QA.png).
- Documentación: 22 Markdown activos, 349 enlaces/anclas relativos válidos; nueve fases, doce tareas P009 y
  117 decisiones consecutivas. Ocho diagramas ER aceptados por Mermaid; flowchart/estados aceptados por su
  gramática sin sanitización/render DOM. STATE/NEXT_STEPS dentro de presupuestos. Diff revisado y sin errores
  de whitespace. Artefactos históricos congelados de P008 y diseño T001 intactos.
- Avisos existentes: deprecación Starlette/httpx en pytest y tamaño de chunks Mermaid en Vite. Sin dependencias
  añadidas ni checks debilitados. No se verifican proveedores reales, aislamiento del sistema operativo, receta
  Django o piloto: siguen fuera de esta entrega y de su autorización.
