# P012-T003 — Chat real y backup/restauración de consulta

Fecha: **2026-10-25**. **Estado: operación detenida y evidencia conservada; dictamen de alcance UI pendiente de HITL.**
Producto instalado: base **`500a783c90e2f3ae581ba3c0fd483d1e7a2b1808`**, wheel T011
**`f22521ff721e79fed2671abfceaf3f035695f3762f7d2765e170b152eacd3201`**.
[Propuesta y elección de supervisor desactivado](P012-T003_PROPUESTA_CHAT_BACKUP.md),
[resultado T002](P012-T002_RESULTADO_T011.md), D035/D040/D083/D174/D198/D199.

## 1. Consentimientos, preparación y parada inicial

El usuario responde **«Continúa.»** tras la propuesta del commit **`bcbf977`** y la petición específica de
consentimiento T003. Autoriza su guion concreto: instalación conservada, chat/UI 8024, hasta **3 Claude/0 Codex**,
copia TOML con supervisor=false, confirmación sin ejecutar, backup/restauración nuevos y consulta 8025;
máximo **dos horas**, sin T004 ni reactivación posterior de la base.

Guardias repetidas correctas: checkout de desarrollo limpio y fuentes/entradas de paquete iguales a 500a783;
**259 miembros instalados** iguales al wheel, ocho hashes de herramientas conservados, TOML original intacto,
tres fixtures y distribuciones previas conservados. SQLite íntegra/FK correcta en 0025, **14.921 filas**,
11 jobs DONE, 12 procesos STOPPED y cero locks. Copia previa SQLite/WAL/SHM y manifiesto privados nuevos.
Preflight del TOML v8 correcto, sin inferencia; no se reconstruye, instala, migra o inicializa nada.

Primer servicio 8024: login y apertura inicial por barra nativa correctos; una navegación automatizada al
proyecto recibe **403 `origin_rejected`**. Se detiene normalmente, clave retirada/puerto cerrado, mismos 11 DONE,
12 STOPPED y cero locks/chat/llamadas. Las 14.921 filas siguen iguales. No se cambia Host/Origin/CSRF ni se
atribuye al producto una causa no acreditada.

HITL posterior: **«Autorizo esa reanudación por la barra nativa, con los mismos límites.»** Se conserva el
techo temporal original desde aproximadamente **06:16 UTC**, sin reponer llamadas. Mismo wheel/TOML/SQLite,
sin repetir el preflight ya aprobado. Navegación por la barra nativa y operaciones por UI; la vinculación de
pestañas antiguas y las lecturas de accesibilidad requieren recuperar el control de la pestaña actual.
Para la consulta 8025 se abre una pestaña nativa nueva. Se descartan sugerencias de Bitwarden y el guardado
de la clave, sin desbloquear cuentas, guardar credenciales ni cambiar ajustes globales.

## 2. Chat, instantánea y comando determinista

Proyecto **p012-b-t010**, P001 ACTIVE, trabajo/visual es/es. Conversación **`70303834…`**, asociada por UI
al run COMMITTED **`e3fa4ae6…`** de T002. Siete documentos explícitos: vista, tests, modelo, flujo,
SPECIFICATION, ARCHITECTURE y DECISIONS del fixture; un run de evidencia. No se usan cambios locales.

| Turno | Run | Resultado | Contexto SHA-256 abreviado |
|---|---|---|---|
| 1: explicación de GET /items/ | `11cbdd56…` | ANSWERED, sin propuestas | `bff9927e575a…` |
| 2: propuesta documental acotada | `b2fe804e…` | ANSWERED, una propuesta | `90db8e4abbc3…` |

Ambos congelan **HEAD `6f021211b307f369f23e2efd76bf0b48e6577c60`**. Evidencia antes/después idéntica,
`checkout.unchanged=true`, cero locks. Exportaciones privadas `head-export-1` eliminadas por la limpieza
normal del producto; directorio de snapshots vacío al acabar. Segundo turno con un turno anterior congelado;
no hay sesión del proveedor reanudada.

La primera respuesta describe correctamente origen/orden de elementos, defecto 5, conversión `int`, rango
1–20 y errores JSON 400; distingue casos probados y deducciones, y no afirma haber ejecutado validaciones.
Tiene referencias de línea imprecisas en su explicación; el propio segundo turno corrige expresamente
`order_by` de línea 20 a **22**. Se conserva el original, sin reparación o llamada extra. La función termina
en la **23**: el hallazgo documental 6–24 de T002 es real y la propuesta conserva el rango 6–23 contrastado.

El revisor también detecta texto anterior del fixture en SPECIFICATION/ARCHITECTURE/D002. Esos documentos
estaban fuera del contrato de escritura de T002 y no se amplía la tarea de chat para corregirlos. No se
interpreta la respuesta como aprobación de esos documentos ni como evaluación comparativa de modelos.

Entre ambos turnos se usa **`/estado`** por UI. La vista previa muestra P001 ACTIVE, versión 8, tarea
P001-T001 con commit **`6f02121`**, ninguna pregunta y READY ausente. No se pulsa ningún control de fase.
Antes del segundo turno sigue habiendo un solo intento de chat: el comando no invoca modelos ni crea job.

| Intentos de chat | Selección congelada | Modelo reportado | Resultado |
|---|---|---|---|
| 1 y 2 | Claude Code **2.1.310**, `sonnet`/`low`, rol chat | `claude-sonnet-5-5` | COMPLETE, exit 0 |

Adaptador `cli-14`, compatibilidad condicionada D174; sin fallback ni cambios de permisos. Consumo real
T003 **Claude 2/3, Codex 0/0**. No se utiliza la tercera llamada ni el saldo de T002.

## 3. Confirmación sin ejecución

Tras los dos turnos, servicio detenido normalmente: **13 DONE, 14 STOPPED y cero locks**, puerto cerrado
y clave retirada. Copia TOML exclusiva 0600 **`config/harness-local-t003-paused.toml`**, único delta semántico
**`service.supervisor=false`**, verificado por parsing y comparación pura de proyecto/composición/política/
agentes/versiones. Original t010 conserva su hash y modo.

| Configuración | SHA-256 |
|---|---|
| Original t010 | `e0e95abb9055f1c9f985c82285bc3c7b551f6503ff6bddb5aff7ddf282fbb6db` |
| Copia T003 con supervisor desactivado | `d41f9375e47baf87bd45d77269d5d583c46b6933b2d5004bd8737408d8becd08` |

Segundo arranque 8024 con esa copia, login nuevo y **«Supervisor detenido»** comprobado en UI antes de
aceptar. Misma conversación, versión **4**, propuesta exacta SHA-256
**`e294ae302f3f4487d9cd1d7dd0b9b5fe62ee361df7303cc6c68d79b5dcc8a66c`** y confirmación explícita.
La propuesta queda **ACCEPTED** y vinculada a **P001-T002**, run **`d235e9d5…`**, job **14**.

El alcance es una línea de evidencia de **docs/flows/items-listado.md**: corregir la referencia de la vista
y contrastar las demás citas de esa línea; código, diagrama y reglas intactos. Los comandos de validación
enumerados son contenido de la propuesta pendiente, **no operaciones ejecutadas** en T003.

Run/job **QUEUED**, sin owner_token ni process_owner, **cero intentos, preparaciones, ciclos o locks**.
HEAD y los 28 archivos versionados conservan bytes/modos; checkout limpio, sin commit nuevo del hijo.
No se toma el job ni se reactiva el supervisor. Servicio detenido de nuevo a las **06:31:45 UTC**;
clave retirada y puerto cerrado. **T004 debe revisar su arranque antes de usar esa base** (D199).

## 4. Backup y restauración del producto

Con todos los servicios/grupos propios acreditados detenidos, destinos nuevos fuera de checkouts y
única raíz de artefactos **AREA/state**, se ejecutan con `venv-t011/bin/harness-local`:

- `backup-create AREA/state/harness.sqlite3 AREA/backups/t003 --artifact-root AREA/state --writers-stopped`.
- `backup-verify AREA/backups/t003`.
- `backup-restore AREA/backups/t003 AREA/restored/t003`.
- `backup-verify AREA/restored/t003`.

Los cuatro comandos terminan **exit 0**. Se verifican integridad/FK/esquema, historiales, JUnit,
proyección derivada y referencias completas. No se reconstruye la proyección, reescribe historial ni
copia el checkout. Bundle y restauración contienen **13 runs**, **42 archivos**, **3.558.608 bytes** de
artefactos y SQLite de **14.503.936 bytes**; COMPLETE coincide con el hash de cada manifiesto.

| Artefacto | SHA-256 |
|---|---|
| Base operativa antes/después del backup y consulta | `187614a9ea361e1f96a45f55240f55a20e4b3138dab2bdd47a1e3fe280675cfc` |
| Manifiesto del backup | `7ff59485ae62c7371a580184cfd4b17071b67cf6f0d8f448e0b41f069362b7b5` |
| SQLite del backup | `b35c4114734da72e25c12a57e01f0f350d6676608eac84c1b4a3d768072e7d15` |
| Manifiesto de restauración | `f5152c80f0de9ae4da6728ac1cedacee10f0442e80c2ecb8d539d82ecd4651e7` |
| SQLite restaurada | `1a1506ff90c2f451ef0bb467a8b520149265c8e516ca6e42088d256300d4b4b8` |

Copias con marca persistente **`0x483532`**, `execution_authorized=false` y apertura query_only. Cada
SQLite verifica su hash propio; **todas las filas** coinciden entre fuente tras chat/confirmación,
copia previa al backup, bundle y restauración. No se exige identidad binaria entre bases con metadatos
internos de copia/restauración diferentes. La base operativa sí conserva su SHA-256 tras todo el recorrido.

## 5. Consulta HTTP acreditada y límite de UI

Servicio **8025**, sin `--config` ni configuración ambiental. API: supervisor **enabled=false/alive=false**,
sin puertos de agentes ni escritor de commits. Sesión local nueva; no se reanudan jobs.

Diez lecturas JSON locales autenticadas por servicio, más el JUnit original: supervisor, detalle de run,
ciclos, diff, casos JUnit, métricas de intentos, resumen, métricas de tareas y los dos REVISION_LIMIT previos.
Los payloads de evidencia coinciden con la lectura de la base operativa tras confirmar la tarea. Se excluyen
de la comparación únicamente `project_id` y `actions` de los detalles: en consulta son null/[] al no haber
proyectos operativos configurados. El supervisor se comprueba por separado.

- T002 **`e3fa4ae6…` COMMITTED**, commit `6f02121`, ciclo 0, seis validaciones/**13 casos JUnit** y diff
  SHA-256 **`db6fa9b245b8d7d9f9c10c534bf611ccbc526434673e35f46030e73ed892b3c0`**.
- Original JUnit SHA-256 **`7e51116eeec2b61fac2b2f4281a63852934a5b63bb1223e15e27a34a68ad4e63`**.
- Runs **`b94eedef…`** y **`f98b16d9…`** conservan REVISION_LIMIT, sin reparación ni revalidación.
- POST inerte de creación de conversación en la restauración rechazado **409 `restored_read_only`**
  antes de efectos. No se intenta ejecutar tareas ni cambiar la marca de consulta.

**UI observada:** tras login en `/runs/e3fa4ae6-5183-4bf9-a406-011b90370302`, muestra
**«El run pertenece a un checkout sin proyecto registrado»** y **«Se conserva su evidencia, pero no tiene
página en esta interfaz»**. No muestra detalle/diff/JUnit de ese run. Se conserva captura privada y se
detiene la consulta; no se registra un proyecto, pasa configuración de agentes o abre una ruta lateral.

Contraste: `frontend/src/pages/Run.tsx` (`RunRedirect`) muestra ese estado cuando `project_id` es null.
D040 y [la entrega original, Consultas y límites](../archive/phase-006/H5.2_BACKUP.md#consultas-y-límites)
definen explícitamente lecturas **API por id**, sin registrar proyectos gestionables desde una copia.
Los registros persistidos se conservan en SQLite; lo que falta es su composición como proyectos operativos
en el servicio de consulta. El guion T003 pidió adicionalmente consulta UI que el producto no ofrece.
No es pérdida de datos ni fallo del backup, y no se presenta la comprobación HTTP como QA de esa UI.

HITL de alcance planteado al usuario: cerrar T003 con evidencia API y límite UI explícito, o conservarla
parcial y planificar una vista UI de consulta en una tarea separada. **Respuesta pendiente.** Sin cambiar
código, criterios de aceptación o diseño unilateralmente.

## 6. Parada y conservación final

Consulta detenida normalmente a las **06:35:49 UTC**; cierre de guardias **06:37:04 UTC**, dentro de las
dos horas originales, aproximadamente 21 minutos desde la preparación, incluida la interrupción inicial.
Ambos puertos cerrados y claves de los cuatro arranques retiradas por el producto. Todos los grupos
persistidos de agentes/validaciones muertos; **13 jobs DONE, 1 QUEUED, 14 procesos STOPPED, cero locks**.
El job QUEUED es el de P001-T002 sin owner/intento/preparación; no se describe como terminado.

**14.921 filas anteriores idénticas** por todas sus columnas; **1.877 filas normales nuevas** de chat,
eventos, streams, propuestas, métricas y tarea vinculada; **16.798 filas** finales en tablas no sqlite_*.
Las 16.798 filas coinciden con bundle/restauración. Cuarenta y dos artefactos originales conservan hashes/modos;
B/B2/clon, sus diffs, configuraciones/distribuciones anteriores y ocho hashes de herramientas intactos.
No hay cambios versionados del fixture, ejecución de la tarea, commit/tag del hijo o retención/borrado.

Evidencia completa solo en el área privada: `state/operator/t003-*`, copias `tmp/t003-*-db`, bundle,
restauración y copia TOML. Capturas de `/estado`, tarea en cola, rechazo origin y límite UI. No se copian
SQLite, prompts completos, streams, sesiones o credenciales a este repositorio. Los resultados anteriores
y la propuesta original se conservan; las incidencias y la autorización posterior se añaden con procedencia.

## 7. Validación y siguiente paso

Validaciones propias del tramo: conservación antes/después, preflight, dos turnos reales, comando sin modelo,
confirmación por hash/versión sin supervisor, cuatro comandos de backup/restauración, lecturas HTTP iguales,
rechazo de mutación, observación UI y parada. La consulta UI de evidencia **no está acreditada**.
No se repiten suites del producto, Node/tipos/build, Alembic o validaciones del fixture: no cambia código,
datos del producto, paquete o dependencias. Las tres pruebas sintéticas de la propuesta conservan su resultado.

Checks documentales correctos: parsers del producto con **12 fases, 7 criterios P012, 11 tareas y 200 decisiones**;
**624 enlaces/anclas relativos** en los seis Markdown de esta entrega y presupuestos STATE/base/NEXT_STEPS
**16.383/24.576**, **9.171/12.288** y **29.347/49.152 bytes**. Cuerpos D001–D199 y secciones 1–7 de la propuesta
conservados por bytes; archivo histórico, baseline pública y producto sin cambios. Diff revisado y
`git diff --check` correcto. Evidencia privada final contrastada con el resultado saneado.

Pendiente la decisión HITL de alcance para el dictamen de T003. T004 continúa sin autorización y requiere
propuesta revisada que respete el job QUEUED antes de cualquier arranque operativo. Sin reactivar esta base,
cerrar P001/P012, operar este repositorio con el harness, cambios globales, tags, push o publicación.
