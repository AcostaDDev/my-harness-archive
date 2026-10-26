# P013-T004 — Persistencia y activación versionada de configuración

Fecha: 2026-10-26. Base: `26973c5`; checkout limpio al comenzar. Encargo: siguiente tarea y commit local
en inglés. **Implementada como primitivas de almacenamiento; API/runtime/UI pendientes T005–T011.**
[D221](../DECISIONS.md#d221--p013-t004-journal-y-referencias-de-configuración),
[contrato T001 §4–§6](P013-T001_CONTRATO.md#4-archivos-formatos-y-autoridad),
[datos](../DDBB-DIAGRAM.md#configuración-versionada-p013-t004), [flujo](../flows/configuration-setup.md).

## Resultado y motivo

La edición necesita conservar dos autoridades diferentes: bytes autorizados en TOML inmutable y referencia
activa en SQLite. `services/configuration.py` valida formatos de editor y `storage/configuration.py` ofrece
preview, guardado, activación, promoción/cancelación, lectura y recuperación. `configuration_files.py` limita
lecturas/publicaciones a archivos privados. Guardar una propuesta no concede sus permisos ni cambia agentes,
comandos, proyectos o contratos admitidos. Las operaciones efectivas siguen dependiendo de las integraciones
posteriores; esta tarea no conecta un consumidor v9 ni añade endpoints/UI.

No se encontraron incongruencias pendientes de HITL tras contrastar D217/D218/D118, el contrato T001 y los
parsers/registro/preparación/backup existentes. Las formas de TOML y las primitivas siguientes concretan los
campos/autoridades ya aprobados. No se importan archivos automáticamente ni se exige configurar un stack.

## Formatos y autoridad

| Documento | Forma implementada |
|---|---|
| Global `local-config-9` | `format`, tablas `service`, `git`, `agents`, `registration`; opcionales `profiles`, `compositions`, `agent_presets`, `recipes`. Mismos campos/validadores de v8, composiciones ausentes/vacías admitidas, sin `projects`. `state_dir` debe coincidir con el parámetro fijado por el servicio. |
| Proyecto `project-config-1` | `project = {id, root}`, `global = {revision, sha256}`, `profile_name`, perfil completo en `profile`, `commands`, `policy`, agentes efectivos en `agents`; `provenance = {source, sha256}` opcional. Identidad y raíz cotejadas con registro activo; referencia global cotejada al activar. |
| DRAFT | TOML sintácticamente válido, incompleto; solo campos conocidos y sin credenciales reconocibles. No activa. Herramientas aún ausentes pueden quedar así hasta preparación. |
| VALIDATED | Campos completos, perfil/validaciones/JUnit/formateador/rutas, comandos exactos/argv sin shell, entorno, agentes y política comprobados sin ejecutar procesos. No acredita preparación. |

El parser del editor reutiliza validaciones v8 por un argumento interno que permite catálogo vacío; `build`,
`load_local_config` y formatos/hashes operativos 1–8 conservan sus condiciones. El loader operativo aún no
acepta v9. Importar/convertir un archivo legacy al conjunto gestionado no está implementado en T004: requiere
el carril explícito y compatibilidad integral T011. Originales, recetas/recibos e históricos intactos.

`scope` se deriva de `global` o `project:<id>` con el patrón existente de ids; nunca acepta una ruta de IA.
Bajo el directorio explícito del servicio:

- Copias editables: `global.toml` y `projects/<id>/project.toml`.
- Versiones: `versions/global/<revision>-<sha256>.toml` o
  `versions/project-<id>/<revision>-<sha256>.toml`, sin sobrescritura de contenido previo.
- `.configuration.lock` conserva el fichero y usa flock del SO; no prueba parada de escritores por existir
  o por vencer un lease.

64 KiB UTF-8 por TOML; directorios 0700, archivos nuevos 0600 y UID del servicio. Se abren componentes con
`O_NOFOLLOW`; se rechazan hardlinks, especiales, permisos ajenos y solapamientos con checkouts registrados,
runs y ancestros `.git`. No se cambian permisos preexistentes. Se rechazan campos de credenciales y formatos
reconocibles de tokens/claves; no se infiere que un texto arbitrario sea una credencial ni se automatiza login.
Los mensajes propios de validación están catalogados en/es; los conflictos internos conservan códigos estables
para el contrato HTTP de T005. Contenidos/diffs completos son primitivas privadas del editor, no nuevos listados.

## Guardado, concurrencia y recuperación

`preview(changes, reason=...)` liga ámbito, texto, elección explícita DRAFT/VALIDATED, versión esperada, hash
observado de copia de trabajo, hash activo y elección de importación externa. Devuelve diff, revisión propuesta,
impacto y hash exacto de la preview. No escribe archivos, ejecuta clientes ni habilita consumidores.

`save(..., preview_sha256=..., key=...)` revalida bajo la barrera SQLite compartida con admisión/commit y
exclusión flock. La misma clave/payload devuelve la operación original; distinta petición con esa clave
bloquea. La intención sella directorios de configuración/estado antes de crear el primer ámbito: no puede
recuperarse en otra ubicación tras una caída inicial.

1. Persistir `INTENDED` con candidatos, hashes/base, versiones, diff, motivo y actor.
2. Publicar cada TOML inmutable y copia editable mediante temporal exclusivo, fsync y replace atómico;
   fsync de directorios. Un conjunto de archivos no se presenta como transacción distribuida.
3. Persistir `FILES_WRITTEN`, verificar el conjunto y finalizar revisiones/referencias guardadas por CAS en
   `SAVED`. La activa permanece igual. Si el commit terminó pero se perdió su confirmación, se conserva el
   resultado durable SAVED y se devuelve en replay; no se degrada a intención obsoleta. Un error conserva `RECOVERY_REQUIRED` o la intención tras muerte abrupta.

`recovery_preview` solo acepta destinos aún en bytes base/candidatos. `recover` exige hash exacto, declaración
explícita de escritores detenidos y lock adquirido; audita la confirmación en una operación RECOVER y termina
la misma intención. La repetición de esa confirmación devuelve su estado sin repetir publicaciones. Bytes
ajenos bloquean; no se reconstruye una versión inmutable alterada a partir del journal o de la copia editable.
Al conciliar un archivo ya publicado se repite fsync para cubrir caída entre replace y fsync de directorio.

Edición externa produce `EXTERNAL_CHANGE`. La activa no cambia; guardar exige importación explícita y CAS de
los bytes observados. `discard_external` restaura la copia desde la versión guardada mediante la misma intención,
conservando historial y replay; incluso bytes externos no UTF-8 pueden descartarse por su hash. Leer una versión
inmutable ausente/alterada bloquea. Ninguna recuperación presume muerte por timeout ni borra evidencia anterior.

## Activación y límites de integración

`activation_preview/activate` exigen referencia guardada VALIDATED exacta, versión/hash y confirmación separada.
Revalidan archivos/identidad/entorno y trabajo pendiente dentro de la misma barrera SQLite. Bloquean jobs
QUEUED/ACTIVE/RECOVERY_REQUIRED, locks/preparación, aceptación/commit, propuestas/borradores utilizables y
operaciones documentales inconclusas; los planes de fase PROPOSED se superseden mediante el carril existente.
Guardar sí es posible con jobs activos. No se cancelan trabajos para hacer pasar la activación.

Global exige incluir revisiones exactas compatibles de todos los perfiles propios activos afectados. El conjunto
queda `RESTART_REQUIRED` por id de activación, sin sustituir la anterior. `promote_pending` es una primitiva
exclusiva del futuro arranque: exige reinicio declarado, revalida el conjunto/evidencia y promueve todo en una
transacción. Un fallo conserva la anterior y las pendientes; `cancel_pending` exige CAS explícita. Guardar
borradores mientras espera reinicio no sustituye el candidato confirmado ni vuelve ambigua su identidad.

Proyecto puede activar sin reinicio; exige verificador confiable del servicio que compruebe preparación y
recomposición. No existe valor permisivo por defecto ni booleano recibido de IA/HTTP que lo reemplace. T008/T009
conectarán recibos/HEAD y runtime; las pruebas usan un verificador sintético explícito. Editar un perfil no toca
otros ámbitos. Los cambios globales sellan las referencias derivadas, sin mutar versiones ni recibos anteriores.

Migración aditiva `0026_configuration`: tres tablas, 54 de producto en total. Heads y activación pendiente son
referencias lógicas; revisiones tienen FK a ámbito/intención, PK compuesta y CHECK de estado; operaciones tienen
clave idempotente única y CHECK de estado. Downgrade con operaciones existentes rechaza pérdida de historia.
Arranque/migración de instalaciones existentes siguen D150; no se ha migrado una base privada del operador.

API/asistente, consumidores, cierre real de admisión durante reinicio, comprobación de archivos antes de cada
efecto/job y recomposición del proceso quedan para T005/T009/T011. Las primitivas no anuncian esa integración
como entregada. D040 se comprueba antes de tocar rutas originales; las lecturas restauradas devuelven referencias
y estado de consulta, las mutaciones se rechazan. Bundle nuevo con bytes TOML es T011: el backup actual bloquea
bases con operaciones nuevas (diagnóstico en/es), en lugar de acreditar referencias sin archivos.

## Verificación

Pruebas específicas en `tests/product/test_configuration.py`: archivos/SQLite temporales y datos sintéticos,
concurrencia real con dos hilos, fallos por etapa/fsync, publicaciones parciales, replay tras recuperación,
bytes desconocidos, cambios externos, rutas con espacios, enlaces/hardlinks/especiales/permisos, catálogo vacío,
DRAFT, identidad global/proyecto, preparación obligatoria, impacto de conjunto y aislamiento de perfiles,
activación concurrente, barrera con trabajo real en filas sintéticas, consulta y migración/downgrade.

- `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q`: **1860 correctos y 29 subtests**,
  dos opt-in omitidas. Avisos existentes de TestClient/FastAPI y ZIP duplicado deliberado en una negativa.
- Comprobación final focalizada tras reforzar la lectura del candidato pendiente y la respuesta perdida al
  confirmar SQLite: **47 correctos** (43 específicos y cuatro de catálogo de textos). Ningún proceso de
  proveedor; concurrencia con hilos y filas de trabajo sintéticas.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: **8 correctos**.
- Alembic en SQLite temporal: `upgrade head` y `check`, **sin diferencias con metadata**. Roundtrip aditivo y
  negativa de downgrade con historia en las pruebas específicas; bases operativas no utilizadas.
- Parsers: **13 fases, ocho criterios P013, quince tareas únicas y 221 decisiones consecutivas con estado**.
  **769 enlaces locales/anclas**, fences y presupuestos correctos. STATE 17.837 bytes, NEXT_STEPS 21.556.
  Cuerpos D001–D220 conservados por comparación con HEAD. Mermaid: **13 diagramas ER parseados**, incluido
  el nuevo; sin render/QA visual. Los diagramas de flujo anteriores conservan su contenido.
- `git diff --check` correcto; diff de código/docs revisado. La primera pasada completa detectó la omisión de
  nuevos errores en el catálogo; corregida en/es y verificada por el test obligatorio del repositorio.

No se han instalado/construido paquetes reales, abierto servicios del producto ni UI, lanzado agentes/proveedores/
smokes, operado este checkout con el harness o modificado configuración global del equipo. Sin frontend/OpenAPI:
La suite frontend Node/tipos/build no corresponde. Candidatos, snapshots, archivos históricos P001–P012 y D214 intactos.
Sin push, CI remota, tag ni publicación. Commit local solicitado; siguiente **P013-T005**.
