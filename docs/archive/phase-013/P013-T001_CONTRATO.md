# P013-T001 — Contrato de instalación y ciclo de vida de configuración

Fecha: 2026-10-26. Base contrastada: `2e682b1`.
**Estado: diseño terminado; implementación pendiente de T002–T011.** No añade scripts, formatos admitidos,
tablas, migraciones, endpoints ni permisos efectivos. Decisiones:
[D216](../DECISIONS.md#d216--p013-t001-instalación-aislada-y-arranque-sin-configuración),
[D217](../DECISIONS.md#d217--p013-t001-archivos-versionados-y-activación-de-configuración),
[D218](../DECISIONS.md#d218--p013-t001-perfil-tras-contexto-y-preparación-antes-de-activar).

## 1. Precedentes y brechas verificadas

| Contrato y código inspeccionado | Se conserva | Cambio diseñado para P013 |
|---|---|---|
| D049/D095/D194; `services/local_config.py`: `_read`, `_build`, `_profile`, `_commands`, `LocalComposer` | TOML privado, claves estrictas, argv sin shell, comandos exactos, perfil completo y formateador D133. Cargar no invoca procesos. | V1–v8 exigen configuración completa; v3–v8 exigen composiciones no vacías. Nuevo carril sin stack previo y archivos propios de proyecto. |
| D051; `scripts/build_distribution.py`, `scripts/check_distribution.py`, `scripts/toolchain.py`, `launcher.py` | Wheel con UI/migraciones, locks/hashes, verificación aislada y uso fuera del checkout. | Los scripts actuales dependen de `.local/`, `.venv` y fuentes del checkout para construir/verificar; no son todavía un instalador desde paquete. |
| D078/D118; registro, runtime y `storage/registry.py` | Raíz/confianza explícitas, versiones, idempotencia, barrera transaccional y selección por proyecto. | Un registro en preparación puede conversar sin perfil ejecutable; nueva referencia de configuración, sin inventar una composición vacía utilizable. |
| D150; `launcher.initialize/serve`, `storage/migrate.py` | Crear base nueva es distinto de migrar; backup previo, revisión conocida y declaración de escritores detenidos. | El wrapper crea solo una base ausente; jamás migra una existente por arrancar. |
| D161; definición, `storage/onboarding_commit.py`, `storage/project_import.py`, flujos actuales | Dos entradas; commit documental conciliable, guardias Git/objetos locales, originales B y adopción de P001. | La propuesta del perfil deja de requerir su declaración previa en el TOML. Escritura de configuración por servicio confirmado, separada del escritor Git. |
| D174; compatibilidad CLI y admisión | Descubrimiento por PATH explícito, mínimos/capacidades, identidad antes de GO, sin fallback. | Detección inicial sin modelos; asistencia solo con pareja configurada, sin usar una propuesta de clientes para la sesión que la propone. |
| D119/D168/D207; preparación y backup | Recetas/recibos v1/v2, locks/procesos compartidos, binding antes de congelar, restauración de consulta. | Preparación genérica con ejecutor acotado y recibo propio; copias incluyen también nuevas versiones de configuración. |
| D157/D215 | Fuente pública principal después del primer push; publicación aplazada y ejemplos opcionales. | T013/T014 emitirán candidato y expediente nuevos; este contrato no modifica D214/P011/P012. |

Las diferencias son ampliaciones autorizadas por D215, no defectos del producto actual. No se encontraron
incongruencias que requieran HITL. Las decisiones de ubicación, estados y reinicio siguientes concretan T001;
las rutas operativas del usuario y cualquier uso real se elegirán en su operación, sin heredar consentimientos.

## 2. Instalación y actualización

`scripts/install` tendrá dos entradas excluyentes: desde clon, o `--dist DIRECTORIO` con paquete construido.
Opciones comunes: `--install-dir`, `--data-dir`, `--config-dir`, `--cache-dir`, `--python`, `--uv`,
`--offline` y `--allow-network`, además de `--help` y un modo de actualización explícito `--upgrade`.
Offline es el modo por defecto; red exige la opción positiva y un plan de destinos/descargas visible.
No hay fallback a red, descarga automática de Python/uv, modificación de PATH del shell ni instalación global.

Las rutas admiten espacios. Se normalizan y muestran antes de los efectos; destinos de instalación, datos
y configuración deben ser absolutos, privados, no solapados con checkouts ni entre sí. La caché puede
compartirse deliberadamente y no concede autoridad a proyectos. No se exige que exista `.local/`.
Valores sugeridos bajo `~/Library/Application Support/Harness Local/` (subdirectorios `installation`, `data`,
`configuration`) y `~/Library/Caches/Harness Local/` en macOS; las opciones explícitas prevalecen. Sugerir o
crear estos directorios del producto no modifica ajustes globales del equipo. No se recorren ni cambian
permisos de carpetas preexistentes ajenas. No se amplía el soporte de plataformas declarado.

Se elige Python explícito o uno local compatible con `pyproject.toml` (actualmente `>=3.14,<3.15` para el
servicio; no confundirlo con el Python del proyecto Django). `uv` explícito o encontrado localmente debe ser
compatible con el toolchain/lock entregado. En clon se exigen además las versiones Node/npm de
`scripts/toolchain.py`; desde paquete no se requieren Node/npm, fuentes, tests ni venv de desarrollo.
Validar requisitos y rutas precede a crear la instalación; un requisito ausente da diagnóstico, sin instalarlo.

| Entrada | Preparación con red autorizada | Instalación y repetición offline |
|---|---|---|
| Clon | Llenar cachés uv/npm según `uv.lock` y `package-lock.json`, sin cambiar locks ni ejecutar scripts npm de instalación. | Construir UI/wheel/sdist/pylock/checksums, verificar artefactos y wheel aislado, instalar por hashes en venv propio. Parametrizar cachés en helpers, sin depender de `.local/` ni activar el venv a mano. |
| Paquete | Obtener solo dependencias fijadas por pylock/hashes en caché uv o wheelhouse declarado; el paquete es local, no se presupone PyPI/Release del producto. | Verificar SHA256SUMS, miembros/metadatos/UI/migraciones/versiones y dependencias fijadas; probar paquete aislado con fixtures sintéticos autocontenidos. Instalar wheel sin resolver dependencias nuevas. |

T002 extraerá/reutilizará la verificación común: el verificador actual compara contra fuentes/frontend y
ejecuta pruebas sintéticas instaladas. No basta con llamarlo sin checkout, ni con sustituirlo por checksums.
El paquete para esta entrada debe entregar manifiesto de miembros y material de verificación suficiente,
incluidos los wrappers; T013 lo comprobará. Las pruebas de verificación pueden abrir servicio local temporal
con agentes falsos, nunca cargar configuración, bases o proveedores del operador. Su operación en esta sesión
sigue requiriendo el alcance autorizado por AGENTS; T001 no la ejecuta.

Instalar prepara una generación en ruta definitiva nueva (no mover un venv con shebangs absolutos), verifica
y solo entonces publica atómicamente la referencia de instalación vigente. Una intención/recibo
`installation-1` registra rutas, Python/uv, versión, hashes del paquete/locks, modo de red y checks terminados.
Estado incompleto conserva diagnóstico y no publica referencia. Una repetición idéntica verifica el recibo
y devuelve el mismo resultado; ruta ocupada sin recibo compatible bloquea, sin sobrescribirla ni borrarla.
La caché incompleta no produce una instalación válida. No se mezclan wheels de generaciones distintas.

Actualizar requiere `--upgrade`, servicio/escritores detenidos y generación nueva verificada; conserva la
anterior y todos los datos. Migración se pide aparte mediante D150 con instantánea y `--writers-stopped`:
no se incorpora a `serve` ni al arranque habitual. Un fallo conserva copia/diagnóstico; no restaura datos ni
rebaja el esquema automáticamente. Volver al binario previo solo es posible con esquema/configuración
compatibles; el backup de consulta no se convierte en base operativa.

## 3. Arranque, sesión y estados globales

`scripts/start` se entrega también con la instalación, localiza `installation-1` y ejecuta el binario del venv
desde un directorio privado fuera del checkout. Opciones: `--install-dir`, `--database`, `--config`, `--port`
y `--temp-dir`; usa valores del recibo salvo override explícito compatible. Configuración y datos elegidos
deben corresponder a la misma instalación/base, sin adoptar otra por coincidencia del nombre del archivo.
Los destinos de DB/configuración/temporal se fijan antes de leer un TOML: el archivo no puede redirigir el
propio arranque. El temporal es 0700 y contiene claves efímeras/temporales Git; no se propaga a agentes sin
su entorno explícito. No instala ni descarga al arrancar.

Base ausente y sin auxiliares: creación exclusiva vía `init-db`; si falla no se presenta como lista. Base
existente: validación del esquema, sin migración silenciosa. Puerto ocupado, ruta inválida o esquema antiguo
detienen con diagnóstico útil. Solo loopback, un proceso y mismo contrato de señales/sesión; salir no borra
datos, libera locks inciertos ni certifica escritores muertos. Un segundo servicio de la misma instalación
no puede activar configuración concurrentemente: exclusión de instancia y CAS persistida.

| Estado del servicio propuesto | Lectura y acciones admitidas |
|---|---|
| `UNCONFIGURED` | Asistente con sesión local, preferencias visuales y diagnóstico. Sin supervisor consumidor, puertos de agentes ni mutaciones gestionadas. |
| `INVALID` | Archivo ilegible/inválido, discrepancia de hash o versión desconocida: asistente/recuperación y evidencia segura; no ejecución. No sustituir archivo por ejemplo. |
| `READY` | Global activa validada; detección/preflight de clientes según D174, alta/conversaciones y operaciones habilitadas por sus puertas de proyecto. |
| `RESTART_REQUIRED` | Versión global confirmada para próximo arranque; mostrar activa y pendiente. Cerrar nuevas admisiones y mutaciones operativas hasta reinicio o cancelación confirmada; guardar borradores/consultar sigue permitido. |
| `RECOVERY_REQUIRED` | Intención incompleta o autoridad incierta: consulta y conciliación explícita; no consumidores ni activación nueva. |
| `READ_ONLY_ARCHIVE` | Marca D040 prioritaria: consulta por id sin cargar TOML externo, detectar CLI, reparar, preparar, guardar o activar. |

Clave de login efímera 0600, carpeta 0700, cookie HttpOnly, Host/Origin, cross-site y CSRF se aplican también al
asistente inicial. Solo muestra la clave por el canal local de arranque ya existente; no por API/listados/logs.
Un TOML ausente/inválido no elimina esas guardias. El carril de configuración no habilita colas al abrir UI.
Detección determinista propone rutas y consulta versión/help solo en la acción explícita de comprobación;
parsear, GET, preview y consulta de backup no lanzan clientes. No automatiza credenciales ni comprueba un
modelo haciendo inferencia. Preflight satisfactorio acredita contrato CLI, no efectos internos ni calidad real.

## 4. Archivos, formatos y autoridad

Se reservan para implementar `local-config-9`, `project-config-1` y `configuration-operation-1`.
No se modifica el parser actual ni se renumeran recibos existentes. Límites: 64 KiB UTF-8 por TOML;
sin secretos, claves desconocidas, enlaces (en ningún componente), hardlinks, rutas relativas o archivos
especiales. Directorios nuevos 0700, archivos nuevos 0600 y propiedad del UID del servicio. Importar un
archivo externo aplica las guardias actuales; no endurecer retroactivamente la lectura 1–8 ni hacer chmod
de sus originales. Las versiones nuevas del editor siempre usan permisos privados.

En `--config-dir` viven `global.toml`, `projects/<id>/project.toml` y un almacén privado de versiones
inmutables por id/revisión/hash. Los ids son generados/validados por el servicio, no rutas aportadas por IA.
Los TOML editables son copias de trabajo de la última versión guardada; **no son un mecanismo de recarga**.
Las versiones inmutables contienen los bytes autorizados. SQLite conserva referencias, revisiones, hashes,
activaciones/intenciones/eventos y evidencia necesaria para consulta; no es una segunda configuración editable.
El contenido manda en el TOML versionado; la referencia activa en SQLite decide qué contenido está autorizado.
Si no coinciden, se bloquea: ni el archivo más reciente ni una copia en memoria ganan por fecha.

| Ámbito | Contenido y referencias |
|---|---|
| Global v9 | Campos globales de v8: servicio, Git, agentes, registration, presets y catálogos opcionales de perfiles/composiciones/recetas. Composiciones pueden faltar o estar vacías; no se exige stack. No contiene `[[projects]]`: registro/raíces/confianza/idioma por proyecto siguen en SQLite. |
| Proyecto v1 | Perfil completo con preparación/validaciones/JUnit/formateador/rutas/instrucciones, herramientas y autorizaciones exactas/entorno de su composición, política y selección de agentes. Identidad del proyecto/raíz y referencia global compatible (id, revisión y hash) selladas por el servicio. Puede quedar en borrador mientras no existan herramientas. |
| Registro y preferencias | Registro mantiene id/raíz/confianza, bootstrap, idioma inmutable y nueva referencia activa de configuración; las preferencias de idiomas D166 y la autoridad de carpeta D117 siguen en SQLite, no se duplican en TOML. |

Seleccionar una composición de ejemplo crea una copia propia versionada, con procedencia del catálogo, sin
referencia mutable compartida accidental. Las revisiones de proyecto resuelven los defaults/presets globales
por hash exacto; nunca siguen un nombre hacia su última versión sin preview. Cambiar global muestra todos los
proyectos afectados y su composición resultante; solo puede activar si todos conservan autoridad compatible.
Si cambian sus valores efectivos, se crean revisiones derivadas explícitas en la misma operación confirmada;
si no, se conserva perfil y evidencia compatible. No se modifica otro proyecto al editar un perfil propio.
Un preset global no seleccionado no cambia el hash efectivo de los proyectos ajenos.

El asistente mínimo pide Git/autor, estado, raíces/techo de bootstrap, proveedor/modelo/esfuerzo del revisor,
proveedor y catálogo/modo/esfuerzos del ejecutor, entorno CLI explícito y parámetros de servicio. No exige
herramientas/validaciones de stack. Los modelos concretos del ejecutor siguen siendo elección del revisor
por tarea, dentro de esa política. Los valores que conceden efectos se confirman; no se hereda el entorno
del proceso, confianza o permisos por detectar un ejecutable. La configuración incompleta puede guardarse
como borrador privado, pero no como versión validada/activa.

## 5. Guardar, activar y conciliar

Cada operación liga `expected_version`, hashes base de copias de trabajo y versiones activas, global/proyectos
afectados, candidato íntegro, diff, impacto, motivo, confirmación y `Idempotency-Key`. Preview estructural no
instala ni invoca procesos. Cambiar candidato/base exige nueva preview. Igual clave/payload devuelve la
operación original incluso tras reinicio; misma clave con payload distinto da conflicto.

Secuencia de guardado: (1) validar límites/rutas y CAS bajo exclusión; (2) persistir intención y bytes/hash
candidatos en SQLite; (3) escribir temporales exclusivos en el mismo filesystem, fsync y publicar versiones
inmutables y copias de trabajo con replace atómico; (4) comprobar hashes/fsync de directorios y finalizar
revisión guardada por CAS. Varias publicaciones de archivos no forman una transacción: la intención registra
por archivo base/destino; ninguna referencia activa cambia hasta tener el conjunto verificado. Un contenido
desconocido nunca se sobrescribe. SQLite solo retiene candidatos como journal verificable, no como autoridad
paralela para ejecutar. Un candidato incompleto no se anuncia guardado/validado.

Estados de operación: `INTENDED → FILES_WRITTEN → SAVED`, o `CONFLICT`/`RECOVERY_REQUIRED`.
Versión guardada: `DRAFT` o `VALIDATED`; activación distinta: `RESTART_REQUIRED → ACTIVE` para global,
`ACTIVE` transaccional para proyecto. Intentos fallidos/cancelados y versiones anteriores se conservan.
No hay borrado automático de versiones en P013. «Guardar» no concede permisos, no invalida jobs ni cambia
la activa; la activación exige otra preview/confirmación ligada al mismo contenido y al estado operativo actual.

| Momento de caída o concurrencia | Resultado obligatorio |
|---|---|
| Antes de intención | Sin efecto; editar/reintentar con base actual. |
| Intención sin archivos, o conjunto parcial | Sin activación. Conciliar misma intención explícitamente si cada destino sigue con bytes base o candidatos sellados; cualquier otro byte bloquea. |
| Archivos completos sin final SQLite | Verificar conjunto y finalizar misma revisión, sin otra versión/efecto. Si propiedad, escritor o base son inciertos, recuperación previa. |
| Referencia activa confirmada, respuesta perdida | GET/replay devuelve misma activa y operación; no repite preparación ni commits. |
| Nueva edición concurrente o cambio externo | 409 con base/candidato conservados y diff; no última escritura gana. |
| Versión inmutable alterada/ausente | Bloquear ámbitos afectados antes de efectos; nueva recuperación auditada. No reconstruir silenciosamente desde una copia editable. |

Edición externa de `global.toml`/`project.toml` se detecta por hash al leer y antes de mutar/admitir. Abre
`EXTERNAL_CHANGE` y bloquea nuevas operaciones del ámbito hasta importar/validar/confirmar o descartar la edición
por CAS explícita; no modifica la activa ni contratos ya admitidos. En jobs en marcha se sigue comprobando la
versión inmutable y el contenido sellado; un cambio de copia de trabajo no les inyecta valores. Una alteración
de autoridad congelada provoca parada/cuarentena antes del siguiente efecto, nunca continuación con el nuevo
TOML. Una recuperación que pueda encontrarse con un escritor incierto exige acreditar su parada; un lease
vencido no prueba muerte.

## 6. Impacto, reinicios y compatibilidad

| Cambio | Activación y efecto |
|---|---|
| Guardar borrador o versión validada | Sin reinicio ni cambio de jobs; mantener diff/versión activa visible. |
| Primera global o cualquier revisión global v9 | Confirmación agenda reinicio, incluso clientes/Git/presets/raíces/supervisor/lease/poll. Se valida en arranque antes de promover pendiente a activa y abrir admisión; fallo conserva anterior y modo bloqueado, sin fallback silencioso. |
| Perfil/herramientas/política/selección de un proyecto | Sin reinicio del servicio: barrera transaccional, nueva referencia y recomposición antes de abrir admisión. Si el proceso no puede instalar la referencia verificada en memoria, mantener bloqueo y recuperar. |
| Puerto/DB/config-dir/temporal/venv | Parámetros del arranque/instalación, requieren detener y arrancar explícitamente. La UI muestra diagnóstico, no mueve estado ni crea una base vacía para aparentar traslado. `state_dir` ha de coincidir con el área ya fijada; una discrepancia no se activa. |
| Preferencias visuales/default de trabajo | Conservan API/CAS D166 sin reinicio; trabajo de una raíz ya asociado sigue inmutable D167. |
| Binario/esquema del producto | Instalación/migración D051/D150; snapshots antiguos intactos, incompatibles en cuarentena. |

Guardar es posible con jobs activos; **activar** se rechaza si el ámbito tiene jobs pendientes/activos,
locks/propietarios inciertos, preparación/intención sin resolver, aceptación/commit pendiente, propuestas de
chat abiertas, turnos/borradores utilizables de definición/incorporación u operaciones documentales incompletas
(D118). Global abarca toda la instalación; proyecto solo su checkout. No se cancela ni reescribe trabajo para
hacer pasar la activación. El usuario termina/descarta lo pendiente con los carriles existentes; nueva preview
después. Los planes de fase PROPOSED se marcan SUPERSEDED en la transacción de activación, con evento y
contenido previo intacto. Admisión, activación y sellado de commit usan la misma barrera SQLite.

Excepción acotada para el alta inicial: confirmar el commit documental cierra sus borradores/conversación,
pero conserva propuesta de perfil y evidencia como artefactos sellados de esa alta. Preparación completa y
commit técnico adoptados no dejan escritor pendiente. Activar puede consumir esos artefactos propios; no
puede eludir otros turnos, locks o propuestas abiertas. Un contexto documental cambiado los vuelve obsoletos.

V1–v8 siguen en modo de lectura/operación legacy de configuración, con parsers, huellas y reglas actuales;
«legacy» aquí no restaura A/visor retirados. `--config` externo 1–8 no se edita ni importa por arrancar.
Edición guiada exige importación explícita: copia privada, preview de global v9 y proyectos v1 derivados de
`[[projects]]` y registro efectivo, conflictos de id/raíz resueltos sin preferencia silenciosa, diff y activación
del conjunto por la misma intención. Originales intactos. Hasta activar manda la configuración previa; tras
importar el arranque usa el almacén gestionado elegido explícitamente, no ambos archivos. Jobs antiguos
terminan/se detienen antes de la transición; nuevos hashes no sustituyen históricos.

Los snapshots nuevos congelan referencias global/proyecto y composición efectiva, además de identidades CLI,
política, idiomas y entorno ya existentes. Formatos nuevos se declaran en sus lectores al implementarlos;
ausencia histórica queda ausente. Paquete/código/configuración incompatibles mantienen cuarentena D049/D174.
No se cambia de cliente/modelo en una sesión o job admitidos; asistencia al editar sus propios clientes usa
la pareja activa congelada hasta finalizar, y la candidata solo se usa tras activación/reinicio.

## 7. Dos entradas, commits y perfil preparado

Contexto de alta tiene capacidades explícitas: agentes/Git/idiomas/raíz y borradores documentales, **sin
capacidad de ejecutar tareas ni comandos de stack**. T007 separará ese contexto del `ProjectContext` ejecutable
actual; no fabricará un perfil/composición ficticios para sortear sus validaciones. Creación conserva autoridad
del padre y reserva/idempotencia; B conserva raíz exacta confiada, inventario de HEAD y prohibición de ejecutar
código para descubrir el stack. Registro inicial se muestra `PROFILE_REQUIRED`, no listo para tareas.

| Etapa | Nuevo desde documentación | Existente B |
|---|---|---|
| Contexto | Brief, preguntas y borradores D088 hasta concretar arquitectura. | Inventario estático y HEAD sellado, conversación/borradores privados y evidencia por comando propuesto. |
| Propuesta | Revisor propone perfil separado de los once documentos. Sin herramientas comprobadas no genera comandos ficticios en instrucciones. | Propone usando código/documentos y pregunta lo no deducible, sin scripts ni instalación de descubrimiento. |
| Revisión | Formulario/TOML valida perfil, comandos/rutas, herramientas diferidas al entorno y plan de preparación; ejemplos opcionales. | Misma revisión; propuesta ligada a inventario/HEAD y documentos resultantes. |
| Commit documental | Confirmar documentos y hash de propuesta compatible; commit raíz D088 y P001 adoptada. No scaffold ni TOML local dentro del checkout. | Confirmar diff/documentos/perfil; commit B conserva originales, phase-000 y bytes de código, con guardias Git actuales. P001 adoptada. |
| Preparación | Después del commit documental, plan exacto separado y ejecutor acotado/receta, validaciones y commit técnico si cambia contenido versionado. | Después del commit B; comprobar entorno existente o preparar cambios expresamente aprobados. Ningún código de proyecto se ejecuta por el mero inventario. |
| Activación | Recibo válido + HEAD/configuración actuales + diff/impacto confirmado: aplicación activa proyecto y habilita primera tarea. | Iguales puertas y comprobación de procedencia de B; no una segunda incorporación. |

La propuesta se valida antes del commit documental para que instrucciones y comandos documentados concuerden;
las rutas de herramientas del entorno pueden ser diferidas, nunca comandos autorizados a ejecutarse todavía.
Un fallo posterior no deshace el commit documental ni habilita tareas: queda `PREPARATION_REQUIRED`.
No se difiere el commit documental hasta después del scaffold, ni se permiten archivos de stack en los
borradores D088. Si cambia perfil de forma que contradiga documentos, se confirma primero una edición
documental con su commit y se regeneran propuesta/plan/recibo; no se reescribe la aceptación anterior.

Estados de disponibilidad del proyecto: `PROFILE_REQUIRED → PROFILE_PROPOSED → DOCUMENTS_COMMITTED →
PREPARATION_REQUIRED → READY_TO_ACTIVATE → ACTIVE`; fallo/conflicto/recuperación explican la puerta cerrada.
Estos son estados nuevos de configuración, no nuevos estados de runs o fases: P001 puede estar ACTIVE en
SQLite mientras la puerta de tareas permanece cerrada. Perfil inválido, pregunta bloqueante, HEAD/contexto
obsoleto o entorno sin evidencia impiden avanzar. Alta B/nueva y operaciones técnicas conservan sus propias
claves de replay y resultados; activar no repite ninguna de ellas.

## 8. Preparación, recibos y edición asistida

Contrato reservado `project-profile-preparation-1`, distinto de `project-preparation-1` de recetas.
Plan visible sella propuesta/configuración y contexto, HEAD, herramientas/versiones, archivos nuevos y
modificables, argv/cwd/entorno, dependencias/locks/hashes, red/destinos, límites/timeout/salida, validaciones,
modelo/esfuerzo seleccionado por revisor y ámbito de escritura. Perfil propio exige al menos una validación
significativa; `--version` de una herramienta puede ser comprobación de preparación, no validación funcional.
Red y scripts de dependencias requieren autorización exacta; offline no cambia de modo al fallar.

El ejecutor puede escribir solo dentro del proyecto/área acordada y rutas del plan; la aplicación ejecuta
instaladores/validaciones autorizados sin shell y registra identidad/grupo antes de GO. No hay terminal genérica,
sudo, edición del TOML global ni de ajustes Git/CLI/uv/npm/shell. Instalar dependencias no otorga escritura
general al resto del disco. Cambios de archivos protegidos solo por el carril técnico confirmado; conserva
guardias de rutas/diff/paridad y commit conciliable, sin convertir el ejecutor normal en escritor documental.

Operación y pasos reutilizan exclusión por checkout, journal/leases/procesos y cancelación acreditada de D119.
Fallo/cancelación/interrupción conserva evidencia y no emite recibo listo. Nueva confirmación enlazada para
reintentar con prefijo acreditado; ningún replay de comandos/red por reiniciar o repetir un POST.
Recibo nuevo sella operación/plan/perfil/composición, herramientas y entorno, identidad del checkout, contenido
relevante/HEAD de preparación y commit técnico si lo hubo, resultados/JUnit, idiomas y versiones. La activación
y cada admisión verifican ese binding y las guardias actuales; futuros commits ordinarios no invalidan por sí
solos un recibo si mantienen archivos protegidos/entorno acreditados. Un cambio de perfil/comandos/herramientas/
locks exige nueva comprobación y recibo; cambios exclusivos de agentes/Git/servicio pueden conservar evidencia
de entorno tras comprobar igualdad técnica, sin rellenar ni reescribir el recibo anterior.

Recetas Django/TypeScript existentes siguen con sus formatos, condiciones y recibos v1/v2. Se pueden seleccionar
como alternativa para un hijo compatible, tras documentos y con su plan propio; no se convierten en receta
genérica ni reciben datos arbitrarios. El activador reconoce su evidencia por sus guardias/binding D207 sin
renumerarla. Proyectos 1–8 sin receta conservan su admisión actual; la puerta nueva de preparación no se impone
retroactivamente hasta su importación/edición guiada explícita.

Edición posterior reutiliza guardar/preview/activar y preparación, sin atajos. Asistencia global opcional solo
con clientes activos: revisor lee contexto autorizado y devuelve candidato estructurado/diff/motivo, ejecutor
solo comprueba en área temporal privada confirmada sin acceso escritor general a configuración. Global/Git/
raíces no cambian por un valor de IA. El servicio valida y escribe tras confirmación exacta del usuario.
La ayuda no puede concederse a sí misma permisos ni sustituir la pareja de la conversación actual.

## 9. API y UI propuestas

Rutas bajo `/api/managed`, sesión/Host/Origin/CSRF y DTO estrictos; nombres/contratos siguientes se implementan
en T004–T010 con OpenAPI/tipos en paridad. 422 para forma inválida y 409 `{code, diagnostic}` para conflicto,
obsolescencia, trabajo pendiente, preparación/reinicio/recuperación requeridos o consulta. Confirmaciones
incluyen versión/hash exactos, motivo y clave idempotente. Lecturas no provocan preflight, IA ni ejecución.

| Rutas propuestas | Contrato |
|---|---|
| `GET /configuration` | Modo/activa/guardada/pendiente, referencias/versiones, capacidades y bloqueos; disponible sin TOML. |
| `POST /configuration/detect` y `/check-clients` | Detección mecánica y, en la segunda, preflight explícito version/help de los clientes elegidos. Sin inferencia/red/login. |
| `POST /configuration/preview`, `/save`, `/activation/preview`, `/activate` | Candidato global (formulario/TOML), CAS, diff, impacto/proyectos afectados y separar guardado de activación/reinicio. |
| `POST /configuration/import/preview` y `/import/confirm` | Conversión explícita 1–8 al conjunto gestionado, fuentes por ruta autorizada y hashes, sin leer TOML arbitrario de un checkout. |
| `GET /configuration/operations/{id}` y `POST …/recovery/preview`, `…/recovery/confirm`, `…/cancel` | Estado/archivos/evidencia saneada y conciliación/cancelación por versión; no ejecutar una nueva intención para ocultar una incompleta. |
| `GET /projects/{p}/configuration` y `POST …/preview`, `…/save`, `…/activation/preview`, `…/activate` | Misma autoridad/CAS en el ámbito propio; perfil, evidencia y puerta de admisión visibles. |
| Planificación de alta y `POST …/profile/preview`, `…/profile/confirm` | Propuesta estructurada ligada a conversación/contexto; confirmar adopta borrador, no prepara ni activa. Mantener carriles documentales existentes. |
| `/projects/{p}/preparation` y `/preparations/{id}` ampliados | Discriminador de contrato receta/genérico; planes/confirmación/progreso/cancelación/confirm-stopped, sin relajar DTO ni lectores de recetas anteriores. |
| `POST /configuration/assistance` y `/projects/{p}/configuration/assistance` | Sesión/job con pareja y contexto congelados; salida como propuesta. Escritura final solo por save/activate. |

`/setup` será el asistente inicial y `/settings/configuration` el editor global; el perfil propio vive en
`/projects/:p/settings`. Navegación inicial resuelve primero consulta, luego modo configurado. Formularios
deterministas, TOML editable, errores por campo, diff, guardar, comprobar y activar/reiniciar claramente
distintos. La UI conserva candidato y sobre idempotente ante conflicto/reload/transporte. Muestra los
bloqueos concretos y enlaza a su operación; no propone activar mientras falte evidencia o trabajo resuelto.
Idiomas en/es y teclado/anchos/temas se validarán en T006/T009/T012.

El TOML privado completo solo se expone en el editor autenticado de configuración; listados/errores públicos
omiten ejecutables, entornos, rutas sensibles, claves de sesión y credenciales. No registrar cuerpos crudos
de candidatos en diagnósticos. La IA recibe solo el contexto autorizado necesario, con procedencia/hashes;
no secretos ni inventario del equipo sin alcance. Nueva API de configuración no crea autoridad desde un
payload del cliente sin las mismas guardias del servicio.

## 10. Backup y fallos de frontera

T011 ampliará el bundle con un formato nuevo que discrimine configuración gestionada: manifiesto de ids,
revisiones/hashes activos/guardados/pendientes, operaciones/intenciones, TOML inmutables y copias de trabajo
referenciadas. Copia consistente con escritores detenidos, hashes/tamaños/rutas seguras y SQLite conciliada;
excluir cachés, venv, claves de login, credenciales y entornos ajenos. No basta guardar rutas al archivo
original. Bundles anteriores siguen consultables sin inventar una configuración que no incluyeron.

Restore conserva marca de consulta y lee evidencia desde el bundle/base sin archivos originales, clientes ni
checkout. Las rutas locales se tratan como datos, nunca como destinos de escritura ni entradas ejecutables.
No activa configuración, consume colas, migra a operativa o repara intenciones. Una instalación nueva requiere
su propia configuración/autorización; restaurar no es permiso para ejecutarla.

| Frontera para T002–T012 | Verificación obligatoria |
|---|---|
| Instalación | Clon/paquete sin Node, rutas con espacios, requisito ausente, cache nueva/completa/incompleta, offline sin red, checksums/miembros alterados y caída antes de publicar generación. Datos/instalación previa intactos. |
| Arranque | Sin TOML/inválido/compatible/externo, puerto ocupado, señales, auxiliares sin DB, esquema viejo/desconocido y segunda instancia. Asistente no consume jobs ni llama modelos. |
| Archivos/SQLite | Dos editores y dos activaciones, crash en cada publicación/fsync/CAS, replay tras respuesta perdida, enlaces/hardlinks/propiedad/tamaño y cambios externos en copias e inmutables. Un único conjunto activo o bloqueo. |
| Impacto | Guardar con job activo, rechazar activar con jobs/locks/commits/preparación/borradores abiertos, carrera con admisión y superseded de planes. Global reinicia, proyecto no contamina otros. |
| Altas | Nuevo/B sin composición, propuesta inválida/preguntas/contexto obsoleto, commit documental previo al técnico, plantilla opcional y stack distinto. Replay no duplica alta/commit/perfil. |
| Preparación | Herramientas inexistentes/diferidas, comando sin validación significativa, shell/red no autorizados, salida parcial, ejecución fuera de ámbito, lease incierto, recibo/HEAD/entorno distintos y recuperación enlazada. |
| Compatibilidad | Parsers/hashes 1–8, importación con filas TOML/registro y conflicto, snapshots congelados intactos, recetas/recibos v1/v2 sin conversión y ausencia de fallback de agentes. |
| Consulta/UI | Backup autocontenido sin original/agentes, GET pasivos, todas las mutaciones rechazadas en consulta, sesión/Origin/CSRF en setup, diagnósticos en/es y conservación de candidato tras conflicto. |

## 11. Implementación y validación documental

T002–T003 implementan instalación/arranque; T004 autoridad/versiones/journal y esquema aditivo; T005–T006
asistente/API/UI; T007–T009 contexto/perfil/preparación/activación; T010 edición asistida; T011 compatibilidad/
backup. T004 actualizará DDBB-DIAGRAM con modelos/migración reales y T007/T008 lo harán si amplían datos.
Este contrato no presenta tablas propuestas como esquema existente. Las formas detalladas de DTO/TOML se
fijarán en cada entrega dentro de estas autoridades/campos, sin relajar mínimos ni introducir nuevas
capacidades; una contradicción de diseño sí necesita HITL antes de implementarla.

Validación y límites de T001 en [registro](P013-T001_VALIDACION.md). Solo checks documentales/parsers puros;
sin instalaciones, migraciones, servicios, harness sobre este checkout, agentes, proveedores, smokes,
configuración global del equipo, candidatos previos ni acciones remotas. La petición del usuario sí autoriza
el commit local en inglés de esta tarea. Siguiente tarea acotada: **P013-T002**.
