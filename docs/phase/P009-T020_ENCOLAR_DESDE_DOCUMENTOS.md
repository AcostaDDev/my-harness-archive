# P009-T020 — Encolar una tarea desde los documentos, con notas adicionales

Fecha: 2026-10-21. Decisión [D135](../DECISIONS.md#d135--p009-t020-encolar-desde-los-documentos-con-notas-adicionales).
Origen: propuesta del usuario tras T009. El usuario pidió hacerla antes de T010. Sin proveedores ni piloto.

## 1. Problema

En T008 y T009 el contrato se copió a mano: sección P001-T00X del NEXT_STEPS del hijo, sin los saltos de línea
finales, pegada en un textarea junto a la fase y el id escritos a mano. Los documentos ya tienen esa información.
Además, no había forma de dar instrucciones extra al agente. Añadir texto al final del contrato tampoco servía: el
planificador solo lee de ese texto la sección de la tarea y las restricciones compartidas (`section` en
`workflow.start`).

## 2. Decisiones tomadas con criterio

- **Fuente.** `GET /projects/{id}/task-sources` lee el NEXT_STEPS vivo del checkout (`read_text`: archivo regular,
  sin enlaces, hasta 512 KiB) y ofrece cada encabezado `## PNNN-TNNN — título` (`TASK_RE`). La fase es el prefijo
  del id. Un id repetido no se ofrece y aparece en `diagnostics`, igual que un documento ausente. Exige el layout v2
  (409 `documents_layout` sin él); entonces el formulario queda en modo manual.
- **Texto enviado.** Es la sección literal de la tarea, la misma que extrae `section`. Si el documento tiene
  restricciones compartidas, va precedida de ellas, porque el planificador las lee del mismo texto. En el hijo del
  piloto no las hay, así que P001-T001 sale con 976 bytes y P001-T002 con 875 bytes y `acd0105b…`: lo mismo que se
  pegó a mano en T008 y T009.
- **Contrato fijado y CAS.** Una tarea elegida del documento se muestra en solo lectura con su hash. `POST /runs`
  añade `source_sha256` opcional: el servidor vuelve a leer el documento y responde 409 `task_source_changed` si la
  tarea ya no está, cambió de fase o el texto difiere. Para lo que no está en el documento queda el modo manual
  («Escribir el contrato a mano»), que envía el texto tal cual, como antes.
- **Notas sin columna nueva.** `notes` opcional, hasta 4000 caracteres, recortadas; en blanco equivalen a
  ausentes. Van en la petición JSON del job (`request["notes"]`), que ya existía, así que no hay migración. El
  supervisor las pasa a `engine.start`, que:
  - las añade a la entrada del planificador como `additional_notes`;
  - las congela en el contrato con la clave `additional_notes`, así que el revisor y el ejecutor las reciben en
    `TASK_JSON` y la página del run las muestra;
  - las añade a las instrucciones del ejecutor, tras un aviso de que no amplían rutas, comandos ni permisos. También
    en un reintento explícito, que parte del mismo contrato.
- **Autoridad.** Solo el usuario aporta `additional_notes`: si el planificador inventa esa clave, el motor la retira
  del contrato, y su salida original queda en su intento. Unas notas con un contrato del servidor (reconciliación) se
  rechazan. La política de rutas sigue leyendo solo `allowed_paths` y `forbidden_paths`.
- **Compatibilidad.** Sin notas no cambian ni la petición del job, ni la entrada del planificador, ni el contrato, ni
  los prompts. Los runs congelados se leen igual. `RunCreate` solo gana campos opcionales. No cambian el motor, el
  adaptador ni los formatos del historial.

## 3. Interfaz

`TaskForm` (resumen del proyecto, fase y tarea) consulta `task-sources` cada 5 s. Ofrece desplegables de fase y
tarea (fijados si la página ya los fija), el contrato en solo lectura con la ruta y el hash del documento, el
modo manual y el campo «Notas adicionales (opcional)», con su alcance explicado. Si la tarea o la fase de la página no
están en el documento, lo dice y pasa a modo manual. La lógica de selección vive en `frontend/src/task-sources.ts`.

## 4. Verificación

- `tests/product/test_task_sources.py` (12 tests):
  - Fuentes con y sin restricciones compartidas; un caso igual que el hijo del piloto; ids repetidos y documento
    ausente.
  - HTTP: listar y encolar desde el documento con notas. Las notas quedan en la petición, en el contrato, en
    `TASK_JSON` y en las instrucciones del ejecutor, y llegan al revisor y a la vista del run.
  - 409 antes de crear ningún job si el documento cambió, la tarea no existe, la fase no coincide o el texto se editó.
  - Sin fuente ni notas, la petición conserva sus claves; las notas de más de 4000 caracteres dan 422; sin layout,
    409.
  - Motor con planificador falso: notas en la entrada solo si las hay, clave inventada retirada y notas rechazadas
    con un contrato del servidor.
- `frontend/tests/task-sources.test.mjs`: fases y tareas ofrecidas, filtro por lo que fija la página y cuerpo de la
  petición con hash y sin notas en blanco.
- Lectura del NEXT_STEPS real del hijo con `task_sources`, sin escribir nada: 4 tareas, sin diagnósticos, con los
  bytes y hashes de T008 y T009.
- Suite pytest completa: 1597 pasan y 1 se omite (Django real), en 4 min 9 s. unittest: 12 OK. `node --test`: 81 OK.
  `npm run check` y `npm run build` correctos. OpenAPI y tipos regenerados. Alembic no procede: sin modelos.
- QA visual en la UI del piloto con el wheel nuevo, sin encolar nada: ver §5.
