# P008-T019 — Submódulos sin ejecución implícita

Fecha: 2026-10-19. Derivada de H6 de la [tercera revisión de salida](P008_REVISION_SALIDA_3.md).
Decisión: [D110](../DECISIONS.md#d110--p008-t019-gitlinks-rechazados-antes-de-inspeccionar-el-checkout).

## Resultado y motivo

El inventario A rechaza gitlinks antes de consultar el estado del checkout. El padre puede no tener filtros,
pero `status --ignore-submodules=none` puede ejecutar los de un hijo inicializado. Comprobar solo la
configuración del padre o detectar el submódulo después de `status` no cumple la lectura sin ejecución.
El rechazo previo se aplica también fuera de `docs/`, sin ampliar soporte de submódulos ni ignorar su suciedad.
La reproducción y el JSON históricos de H6 permanecen intactos.

## Cambios

- `adapters/project_import.check_submodules` lee únicamente HEAD (`ls-tree -r -z --full-tree HEAD`) y el
  índice (`ls-files --stage -z`) del padre con `LocalGit`. Un modo `160000` bloquea con ruta y fuente, sin
  consultar configuración, estado ni archivos del hijo. HEAD detecta incluso una retirada del índice;
  el índice detecta un gitlink nuevo. No depende de `.gitmodules`, inicialización o ubicación del gitdir hijo.
- `read_checkout` aplica la guardia antes de `status`, sin sustituir `--ignore-submodules=none` ni relajar
  la limpieza. Creación de conversación, mensajes, observaciones antes/después, estado, vista previa y
  confirmación A heredan el rechazo. Un cambio durante un turno invalida su respuesta sin aceptar propuestas.
- `storage/project_import.check_git` comparte la guardia con B antes de captura/sellado, ejecución del job
  y recuperación de una intención interrumpida. El inventario estático B conserva la lectura sin seguir
  submódulos; la escritura se bloquea en la frontera posterior. No se modifica el escritor Git general.
- `document_layout = "d088-11"` congela la corrección; la composición actual deja jobs anteriores en
  cuarentena antes de efectos. La configuración deriva la versión de la constante común y las regresiones
  incluyen `d088-10` entre las incompatibles. No cambian inventario/mapa, prompts, codec, CLI, esquema, API,
  UI o dependencias; tampoco se reescriben snapshots, historiales o intenciones.
- SPECIFICATION, ARCHITECTURE, flujos A/B, STATE, NEXT_STEPS, ROADMAP e índice de decisiones actualizados.
  Sin modelos ni migraciones: DDBB-DIAGRAM permanece vigente.

## Regresiones

`tests/product/test_import_submodules.py` añade 27 casos, exclusivamente sintéticos:

- Padre limpio sin filtros propios, gitlinks dentro/fuera de `docs/` e hijos inicializados con filtros
  `clean`/`process`, directos y por include. El filtro falso solo crearía un marcador externo: nunca se
  ejecuta. La traza exige comandos con `--no-lazy-fetch`, solo sobre el padre y anteriores a `status`.
  Los bytes del checkout y `.git`, incluidos índices, refs, configuración y objetos de padre/hijo, no cambian.
- Gitlinks solo en índice, retirados del índice, hijos sin inicializar y gitdir absorbido con `.git` como
  archivo. La guardia no necesita ejecutar filtros para averiguar si el hijo está limpio.
- Crear conversación, mensaje, estado, vista previa y confirmación A en ambas ubicaciones: rechazo anterior
  a agentes/captura/sellado/escritura, sin nueva conversación, job, operación ni fase. Las observaciones
  anterior y posterior de un turno ya encolado lo dejan FAILED sin propuestas cuando aparece un gitlink.
- Vista previa B bloqueada antes de capturar; jobs A/B confirmados bloqueados por un gitlink nuevo en índice,
  sin escribir. Tras confirmar detenido al escritor, reconfirmar sigue bloqueado y no crea otro job.
  Retirar el bloqueo permite recuperar la misma intención, run y commit, con una sola fase adoptada.
- Las suites existentes conservan H1–H5, checkout sucio, D099, bytes exactos, destinos ignorados, recorridos
  válidos A/B y conciliación tras caídas. El control estático B sigue sin invocar filtros hijos.

## Verificación

- `python3 -m unittest discover -s tests -p 'test_*.py'`: 12 checks correctos.
- Primera batería de submódulos y objetos locales: 43 casos correctos. Después se añadieron los dos casos
  de observación de turnos ya encolados, incluidos en la suite completa.
- Colección congelada de 1.410 nodeids, cubierta exactamente por cuatro lotes disjuntos: 353/353/352/351
  correctos y un fallo inicial; 116/0/5/0 subtests correctos. Duraciones: 263,18/275,68/287,03/282,94 s.
  El único fallo era la lista de comandos de lectura de `test_only_read_only_git_commands_run`, que aún
  no admitía `ls-files`. Se actualizó la expectativa al nuevo lector del índice; no se cambió el producto
  para resolverlo. Las 27 regresiones nuevas pasaron. Solo el aviso conocido de Starlette/httpx.
- La batería amplia dirigida tuvo el mismo fallo de expectativa y 166 casos correctos. Después de la
  corrección se revalidó todo `test_project_import.py`: **14 casos correctos**, incluido el caso fallido.
  Los 1.410 nodeids y 121 subtests quedan cubiertos sin fallos pendientes; no se repitieron suites ajenas.
- 38 Markdown activos/raíz/phase/flows con 425 enlaces relativos/anclas válidos. Presupuestos de instrucciones,
  STATE/base/NEXT_STEPS correctos; parsers reconocen 110 decisiones, ocho fases y diecinueve tareas.
- Cinco flowcharts de los flujos A/B aceptados por el parser Mermaid local sin sanitización de etiquetas,
  DOM ni renderizado. La primera invocación directa necesitó ajustar el enlace al objeto de datos del parser
  y omitir la sanitización dependiente del DOM; no hubo errores de sintaxis en los diagramas.
- Diff revisado y `git diff --check` correcto. Sin Node/build ni Alembic independiente: no cambian UI, API
  ni esquema. Evidencia histórica de H6 sin modificar.

## Límites y continuidad

Se mantiene la exclusión cooperativa de D105: la guardia no añade aislamiento frente a cambios concurrentes
arbitrarios del checkout o su configuración. No certifica submódulos limpios: rechaza su presencia en HEAD o
índice antes de cualquier inspección capaz de ejecutar sus filtros. Los casos de lectura rechazada comparan
todos los bytes; las vistas previas válidas conservan la creación de objetos locales inalcanzables de D105.

Sin UI visual, Node/build/Alembic independiente (no cambia UI, API ni esquema), proveedores reales, smokes,
push, publicación, subagentes, registro ni ejecución del harness sobre este repositorio. Sin datos privados ni
configuración global modificada. El usuario autorizó el commit de desarrollo.

P008 sigue activa. Siguiente: nueva revisión de salida; cierre y archivo en una operación posterior separada.
