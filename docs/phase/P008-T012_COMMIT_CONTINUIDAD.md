# P008-T012 — Vista previa, commit y continuidad del Flujo A

Fecha: 2026-10-16. Implementación manual de la siguiente tarea de
[NEXT_STEPS](../NEXT_STEPS.md#p008-t012--flujo-a-vista-previa-commit-y-continuidad), sobre D088, D027, D037,
[D099](../DECISIONS.md#d099--flujo-a-activación-d027-antes-de-la-importación) y la conversación de T011.
Decisión: [D100](../DECISIONS.md#d100--p008-t012-importación-confirmada-y-continuidad-del-flujo-a).

## Resultado

`core/engine/import_commit.py` materializa el mapa y aplica los borradores privados y los valores por defecto de
D089. Las entradas de `review` que no pertenecen al archivo se retiran como parte de la confirmación del árbol. Cada
original que deja de estar intacto en su ruta o destino del mapa se conserva por bytes en
`docs/archive/phase-000/import-originals/<ruta original>`. Los archivos ajenos mantienen su ruta y sus bytes. El
archivo anterior no se sobrescribe y las colisiones de destino, mayúsculas o archivo/directorio bloquean.

El resultado debe declarar la misma fase activa en STATE y NEXT_STEPS, descrita en ROADMAP con objetivo y criterios.
Se regeneran STATE, NEXT_STEPS, ROADMAP e índice de DECISIONS. La fase se adopta ACTIVE con las tareas declaradas,
que pueden estar vacías; no se inventa estado de ejecución ni se reinterpretan runs legacy como intentos gestionados.

La vista previa incluye todos los documentos resultantes con hashes, movimientos, originales archivados, ajenos,
cambios íntegros (base64 para binarios), diff, fase/base adoptadas y árbol Git propuesto. Puede escribir objetos Git
sin referencia para comprobar el diff y el límite de captura; no cambia documentos, refs ni el índice real.

## Confirmación y recuperación

`storage/project_import.py` persiste `project_imports` (`0020_project_imports`, 35 tablas). Una operación por raíz,
conversación y run. Hash exacto, motivo y clave idempotente; versiones, contexto, autor, bytes, fecha, árbol y commit
sellados antes del primer efecto en documentos o refs. Mensaje: `docs: normalizar al contrato documental`.

Se reutilizan cola, lock, propietario, lease y cuarentena. El escritor documental admite únicamente hashes antiguos,
ausencia o bytes sellados, y exige el mismo árbol e índice. Ante una caída: confirmar el escritor detenido, revisar
la intención y reconfirmarla; solo es nuevo el job. El run, la intención y el commit conservan identidad. La adopción
de fase, el resultado y el fin del job son una transacción. Una intención incierta bloquea nuevas escrituras, creación
de fases y reversión D027; los borradores quedan cerrados. Repetir la vista previa completada informa que no hay
cambios ni otro commit.

En macOS los alias por mayúsculas requieren observar la grafía exacta, borrar el alias antes de escribir el canónico
y eliminar del índice temporal la grafía ausente antes de `add`. Se fija `core.ignorecase=false` solo para los
comandos del adaptador, sin modificar configuración local ni global. Los bytes binarios y CRLF no se transforman.

## Activación y continuidad (D099)

Con runs legacy se ofrece primero la vista previa de D027 y su activación confirmada aparte. La creación de la
conversación se rechaza mientras la guardia rechace el modo gestionado. El inventario solo tolera
`.harness/managed-mode.json` sin seguimiento cuando su hash pertenece a una activación propia ACTIVE y sin deriva.
Un marcador ajeno, versionado o modificado no recibe la excepción; cualquier otro cambio sigue bloqueando.

La autoridad de modo se inyecta en los puertos Git de API y supervisor. La captura excluye solo ese marcador
validado, también al ejecutar y hacer commit de tareas posteriores. Ningún `.gitignore` se modifica. Las reglas
entran en `document_layout = "d088-6"`; los jobs congelados anteriores quedan en cuarentena.

## API y UI

- `GET /projects/{p}/import`: activación requerida, vista previa D027, rechazo de modo y operación existente.
- `POST /projects/{p}/planning/{c}/import/preview`: árbol exacto confirmado o conflicto con diagnóstico.
- `POST /projects/{p}/planning/{c}/import/confirm`: confirma o concilia la intención con Idempotency-Key.
- `/projects/:p/import[/:c/*borrador]`: activación previa, conversaciones, propuestas, edición CAS privada, revisión
  del árbol/bytes/hash, motivo, confirmación, progreso, recuperación y enlace a la fase adoptada.

Extensiones técnicas de las rutas permitidas de T012: OpenAPI/tipos generados y prueba Node del enrutador. Sin nuevas
dependencias, prompts ni cambios del codec. Paridad en DDBB-DIAGRAM y `flows/legacy-migration.md`.

## Verificación

- 19 casos nuevos en `test_import_commit.py`: tres orígenes, preservación y adopción, idempotencia; caídas antes de
  escribir, tras borrado, reemplazo, commit y antes del registro; rechazos por deriva, preguntas, incoherencia de fase,
  colisiones, confirmación inválida o diff excesivo; activación y marcador; binarios y alias de mayúsculas;
  recorrido HTTP, protección del downgrade y primera tarea posterior hasta COMMITTED, con agentes y comandos falsos.
- 12 checks ligeros correctos y `alembic check` correcto sobre SQLite temporal migrada a head.
- 74 pruebas Node correctas; tipos (`tsc`) y build correctos. Se mantiene el aviso de chunks de más de 500 kB.
- Suite pytest completa: 1.281 OK y 121 subtests correctos, con dos fallos del recorrido legacy
  `test_import_execute_block_revalidate_commit` por el marcador ya ignorado. Corregida la exclusión y re-ejecutados
  los cuatro archivos afectados (Git, API, recorridos e importación): 79 OK. Después de limpiar `history.stop` al
  conciliar con éxito, cinco casos de recuperación re-ejecutados: cinco OK. También una pasada conjunta de
  importación y conversación dio 36 OK. Aviso conocido de Starlette/httpx; ningún fallo pendiente conocido.
- Ocho Markdown editados/nuevos, 276 enlaces/anclas válidos; DECISIONS indexa 100 decisiones sin duplicados;
  ROADMAP y NEXT_STEPS aceptados por sus parsers (ocho fases y 15 tareas). `git diff --check` correcto.
- Los siete diagramas ER pasan `mermaid.parse`; los dos flowcharts pasan la gramática del parser local de Mermaid
  11.17.2. Su parser general requiere DOMPurify/DOM para las etiquetas; se verifica la gramática sin renderizado.
  El diagrama de estados, sin cambios, no se vuelve a validar.

Las primeras pasadas detectaron errores en los fixtures nuevos (documento obligatorio ausente, comparación del job
antes y después de ejecutar, API de commit de tarea y estado HTTP), y la necesidad de conservar grafías exactas en
macOS. Una pasada completa detectó además el rechazo de Git al excluir explícitamente un marcador que ya estaba
ignorado; la exclusión se limita a los marcadores sin seguimiento que la necesitan. Se revalidan ambos casos. Una suite iniciada durante la implementación se detuvo para
comprobar la versión final completa.

## Límites

Sin comprobación visual en navegador ni proveedores reales; no se ejecutan comandos del proyecto durante la
importación. Las pruebas inyectan excepciones en los efectos persistentes; no simulan todos los posibles cortes del
sistema operativo. Contención cooperativa y temporales o bytes externos inciertos conservan las restricciones del
escritor Git existente: se detienen para recuperación con evidencia. No se ejecutó el harness sobre este repositorio,
ni smokes, push o publicación; no se leyó ReferenceProject ni se modificó configuración global. T013 queda sin iniciar.
