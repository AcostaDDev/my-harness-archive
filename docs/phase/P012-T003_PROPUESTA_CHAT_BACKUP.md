# P012-T003 — Propuesta de chat y backup con consulta restaurada

Fecha: **2026-10-25**. **Estado: diseño operativo elegido por HITL; ejecución pendiente de consentimiento.**
Base del producto conservada: **`500a783c90e2f3ae581ba3c0fd483d1e7a2b1808`**, instalada en T002.
Precedentes: [T001 §§5–7](P012-T001_PROPUESTA_OPERATIVA.md#5-fixtures-y-recorridos-observables),
[resultado T002](P012-T002_RESULTADO_T011.md), D035/D040/D083/D174/D198 y
[D199](../DECISIONS.md#d199--p012-t003-confirmación-en-cola-con-supervisor-detenido).

## 1. Discrepancia resuelta por HITL

T003 exige una propuesta confirmada sin ejecución ni lock. `ChatRepository.accept` confirma por hash/versión
y crea inmediatamente un run/job normal con `action=start`, `status=QUEUED`. Con el TOML conservado
(`supervisor=true`), el supervisor notificado lo reclamaría: preparación, plan, ejecutor y revisión.
No hay un control HTTP para pausar el supervisor ni una aceptación diferida independiente de la cola.
Es el comportamiento documentado en D035/D083 y cubierto por las pruebas; no acredita un defecto de producto.

Se presentan dos alternativas al usuario: conservar esa cola con supervisor desactivado, o definir primero
una mejora de aceptación diferida. El usuario elige expresamente:

> Usar supervisor=false y conservar la tarea en cola; revisar T004 antes de reactivar esa base.

Se conserva el criterio sin ejecución: la tarea confirmada quedará **QUEUED**, con **cero intentos**, sin
preparaciones, comandos, lock ni cambios en el checkout. No se describirá como un job terminado o inexistente.
Se detendrá el servicio del chat antes de aceptar y se arrancará con una **copia nueva del TOML**, cuyo único
cambio semántico sea `service.supervisor=false`. El original permanece intacto. No se editará SQLite.

**Guardia posterior:** no volver a abrir esta base con supervisor activo, tampoco para T004. La siguiente
propuesta T004 debe resolver explícitamente su arranque sin ejecutar la tarea pendiente. No se cancela, borra,
pone en cuarentena ni altera un job para satisfacer la prueba; no se inventa un mecanismo de borrador.
La elección del diseño no concede todavía consentimiento para sus efectos operativos.

## 2. Área, entradas y destinos

`AREA=$HOME/Documents/harness-validation/p012-20261024`, fuera de cualquier checkout.

| Entrada o destino bajo AREA | Uso y efectos propuestos |
|---|---|
| `venv-t011/`, `dist-t011/` | Leer y reutilizar la instalación verificada; sin build ni instalación |
| `config/harness-local-t010.toml` | Leer el TOML v8 para el chat; conservar bytes/modo |
| `config/harness-local-t003-paused.toml` | Archivo nuevo 0600; solo `supervisor=false`, para aceptar sin ejecutar |
| `projects/managed-b-t010/` | Proyecto `p012-b-t010`, P001 ACTIVE, trabajo/visual es/es; solo lectura |
| `state/harness.sqlite3`, artefactos normales bajo `state/` | Chat, propuesta y confirmación exclusivamente mediante el producto |
| `state/operator/t003-*`, `tmp/t003-*` | Evidencia privada y copias de conservación nuevas |
| `backups/t003/` | Bundle nuevo, creado con el producto tras detener todos los escritores |
| `restored/t003/` | Restauración nueva de consulta, sin configuración de agentes ni supervisor |

Puertos exclusivos: **127.0.0.1:8024** para chat y posterior confirmación con supervisor desactivado;
**127.0.0.1:8025** para consulta restaurada. Si un puerto o destino está ocupado, parar sin sustituirlo.
Crear solo los padres `backups/` y `restored/` si faltan, modo 0700; los destinos finales los crea el producto.
Entorno del servicio como T011: PATH explícito venv-t011/Node/uv y `/usr/bin:/bin`, HOME `command-home`,
TMPDIR `tmp`, PYTHONNOUSERSITE=1, PYTHONDONTWRITEBYTECODE=1, LANG=C.UTF-8; sin PYTHONPATH ni configuración
ambiental del harness. `umask 077`; clave local directamente al formulario, sin imprimirla.

Entradas congeladas:

| Entrada | SHA-256 |
|---|---|
| Wheel T011 | `f22521ff721e79fed2671abfceaf3f035695f3762f7d2765e170b152eacd3201` |
| SHA256SUMS T011 | `c8bc3aed58977028ba351e1f981c9d7e65051a76ebe0cf78962a90a9887adafc` |
| TOML original t010 | `e0e95abb9055f1c9f985c82285bc3c7b551f6503ff6bddb5aff7ddf282fbb6db` |
| Diff aceptado T002 | `db6fa9b245b8d7d9f9c10c534bf611ccbc526434673e35f46030e73ed892b3c0` |
| JUnit T002 | `7e51116eeec2b61fac2b2f4281a63852934a5b63bb1223e15e27a34a68ad4e63` |

## 3. Puerta de conservación y comprobaciones preparatorias

Lecturas realizadas **antes del consentimiento**, sin arrancar el producto ni invocar CLI de agentes:

- Puertos 8024/8025 sin listener; destinos del bundle, restauración y copia TOML ausentes y rutas principales
  sin enlaces. TOML original 0600 con hash exacto y `supervisor=true`.
- SQLite sin WAL/journal pendiente, abierta `mode=ro&immutable=1`: integridad y FK correctas, revisión
  `0025_project_work_languages`, **14.921 filas** en **52 tablas contando alembic_version**;
  **11 jobs DONE, 12 procesos STOPPED, cero locks y cero conversaciones de chat**.
- Run `e3fa4ae6…` COMMITTED, stage committed. Clon limpio en
  **`6f021211b307f369f23e2efd76bf0b48e6577c60`**, sin remoto/alternates, **28 archivos** iguales a HEAD por
  bytes; 15 originales 0600 y 13 documentos 0644.
- Los cuatro artefactos T011 conservan los hashes publicados en T002. **141 fuentes Python** del wheel
  coinciden con las actuales; los **ocho hashes de herramientas** coinciden con T001 sin ejecutar las CLI.
- Las **36 referencias** de prompt/stdout/stderr de los doce procesos existentes quedan bajo `state/`;
  sin activaciones ni fuentes legacy. La raíz permitida para backup sigue siendo únicamente `AREA/state`.
  Repetir el inventario después del chat; si aparece una referencia exterior, parar y revisar, sin ampliar raíces.
- Comparación pura con el Python instalado: construir ambas configuraciones **en memoria**, con el único
  delta `supervisor=false`, conserva exactamente proyecto registrado, composición, política, agentes y versiones.
  No se escribe la copia TOML ni se construyen puertos o supervisor. No se reutiliza un job con otra política.

Repetir las guardias antes de operar. Contrastar fuentes/entradas del paquete con `500a783`, instalación,
identidades de herramientas y ausencia de trabajo pendiente utilizable. Preservar manifiestos de hashes/modos
de B/B2, sus diffs, configuraciones, distribuciones y clon, más copia consistente SQLite/WAL/SHM con escritores
detenidos. No usar `immutable=1` sobre una base con WAL pendiente; analizar copias consistentes.
No repetir tests/formateador, preparación, preflight de validadores, migración o init-db del fixture.
Antes del primer turno real ejecutar únicamente el preflight de capacidades de las CLI del TOML conservado;
sin login/status, descarga ni inferencia adicional. El preflight no cuenta como llamada de modelo.

## 4. Chat, comando y propuesta confirmada

Arrancar desde AREA con el ejecutable instalado:

```sh
"$AREA/venv-t011/bin/harness-local" check-config "$AREA/config/harness-local-t010.toml" --preflight
"$AREA/venv-t011/bin/harness-local" serve --database "$AREA/state/harness.sqlite3" --config "$AREA/config/harness-local-t010.toml" --port 8024
```

Por UI, login local y conversación nueva asociada a **P001** y al run **`e3fa4ae6…`** de p012-b-t010.
Seleccionar explícitamente vista/tests, flujo y documentos pertinentes, con un máximo de ocho rutas del chat.

1. Primera llamada Claude: explicación de `GET /items/`, validación de `limit`, errores y cobertura de los tests,
   citando archivos/líneas de la instantánea. No pedir cambios ni propuestas en este turno. Contrastar respuesta,
   referencias y HEAD congelado con el código, documentos y evidencia del run.
2. **`/estado`**, vista previa determinista de la fase, sin modelo ni acción adicional: contrastar P001 ACTIVE
   y P001-T001 COMMITTED. No pulsar check, cierre, lote, ejecución o exportación desde los controles reutilizados.
3. Segunda llamada Claude: pedir **una propuesta** acotada a corregir las referencias de líneas del flujo
   `docs/flows/items-listado.md` señaladas en la revisión T002, sin cambiar código/comportamiento. Revisar que
   título, objetivo, alcance, criterios y validación se correspondan con el hallazgo y estén en español.
   No usar `/tarea` como sustituto: la propuesta debe proceder del revisor real.

Cada turno debe terminar ANSWERED con HEAD **`6f02121`**, evidencia de instantánea inalterada y cero locks del
checkout. Registrar intento, proveedor/CLI/modelo observado, hashes de contexto, referencias y propuesta;
comprobar limpieza normal de las exportaciones HEAD. Una pregunta no deducible pasa por HITL. La eventual
tercera llamada es solo una aclaración dentro del mismo recorrido, no reintento de un turno fallido.

**Antes de aceptar**, detener el servicio y todos sus grupos propios; acreditar puerto cerrado, clave retirada,
jobs de chat terminados y cero locks. Crear la copia TOML exclusiva 0600, comprobar que solo cambia el booleano
de supervisor, registrar hash y contrastar otra vez las huellas del proyecto. Arrancar con esa copia:

```sh
"$AREA/venv-t011/bin/harness-local" serve --database "$AREA/state/harness.sqlite3" --config "$AREA/config/harness-local-t003-paused.toml" --port 8024
```

Comprobar en el producto que el supervisor está **disabled** antes de confirmar. Login nuevo, misma conversación,
revisar propuesta/hash/versión actuales y aceptar por UI con id libre **`P001-T002`**, fase **P001**, confirmación
explícita. Si el id ya existe o el contenido excede lo acordado, parar; no editar la propuesta a mano.
Comprobar vínculo propuesta ACCEPTED → tarea/run **QUEUED**, job **QUEUED sin owner**, cero intentos,
preparaciones, comandos y locks; ningún cambio de HEAD o archivos. No volver a activar el supervisor.
Detener este segundo servicio y verificar otra vez parada/clave/puerto. El TOML original sigue intacto.

## 5. Backup y restauración de consulta

Con los servicios y escritores acreditados detenidos, inventariar referencias y ejecutar por etapas:

```sh
"$AREA/venv-t011/bin/harness-local" backup-create "$AREA/state/harness.sqlite3" "$AREA/backups/t003" --artifact-root "$AREA/state" --writers-stopped
"$AREA/venv-t011/bin/harness-local" backup-verify "$AREA/backups/t003"
"$AREA/venv-t011/bin/harness-local" backup-restore "$AREA/backups/t003" "$AREA/restored/t003"
"$AREA/venv-t011/bin/harness-local" backup-verify "$AREA/restored/t003"
"$AREA/venv-t011/bin/harness-local" serve --database "$AREA/restored/t003/state.sqlite3" --port 8025
```

Revisar `manifest.json`, COMPLETE, esquema, hashes de SQLite/artefactos y correspondencia de referencias antes
de abrir la consulta. El producto comprueba integridad/FK, historiales/JUnit y proyección de runs; no reconstruye
la proyección ni reescribe resultados. La marca persistente **`0x483532`** y `execution_authorized=false`
impiden ejecutar la tarea en cola. La consulta se abre **sin --config** y sin configuración ambiental.

Consulta UI del run T002 por id: COMMITTED/commit, ciclo 0, diff de tres rutas, seis validaciones y **13 JUnit**;
comparar hash del diff, original JUnit y métricas con la base tras chat. Incluir los dos REVISION_LIMIT previos
como tales, sin reparar ni revalidar. Las lecturas HTTP locales autenticadas de run/diff/JUnit/métricas y
supervisor pueden complementar la evidencia UI. Probar un POST inerte de creación de conversación en la
restauración: debe rechazar con **409 `restored_read_only`** antes de efectos, sin intentar ejecutar una tarea.
No pasar una configuración de agentes para comprobar esa guardia.

Comparar todas las filas de la copia/restauración con la base tras chat, y los archivos/filas de la base
operativa antes/después de backup/consulta: ninguna escritura operativa. La marca interna de copia no se
confunde con una alteración de filas. Backup no incluye código/objetos Git y no reactiva la base (D040).
Detener la consulta, acreditar ambos puertos cerrados, claves retiradas y ningún proceso/grupo propio activo.
Conservar bundle, restauración, TOML pausado y tarea QUEUED. No borrar parciales ni reutilizar destinos tras fallo.

## 6. Presupuesto, parada y consentimiento pendiente

Techo propio T003 de T001: **Claude 3/3**, **Codex 0/0**, **dos horas** desde la preparación operativa.
Previsto: dos Claude; el tercero solo si hace falta aclaración y tras resolver HITL. Contar invocaciones
observables, incluidas fallidas; sin trasladar el saldo T002 **9/12 Claude, 3/3 Codex** a este tramo.
Misma pareja/presets t010, **Claude Code 2.1.310 `sonnet`/low**, timeout 1800 s, lectura; ninguna llamada
Codex ni preparación/formateo/validación/plan/revisión de la tarea confirmada. Compatibilidad condicionada cli-14.
No se garantiza techo de tokens/coste ni retries internos (D019).

Parar al primer fallo de proveedor/auth/esquema/timeout, permisos, CAS/hash, identidad, cuarentena,
destino/raíz, preflight, referencia de backup o respuesta incoherente; no relanzar tras fallo. Conservar
evidencia y declarar qué criterio quedó pendiente. No reparar agentes, snapshots o SQLite ni variar permisos,
modelos, versiones o configuración global. Al terminar, cero jobs **ACTIVE** y cero locks; declarar por separado
el único job **QUEUED** esperado y su ausencia de intentos. Antes de cualquier reactivación, HITL nuevo.

Consentimiento operativo por solicitar sobre **todo este guion**: reutilizar instalación T011; comprobaciones
y preflight; servicio/UI 8024 para chat; hasta 3 Claude/0 Codex; parada; copia TOML supervisor=false y segundo
arranque para confirmar P001-T002 sin ejecutar; parada; backup/verificación/restauración y consulta 8025 con
rechazo de mutaciones; parada/conservación final. La autorización de commit de esta sesión cubre los documentos
de my_harness, no la operación real. T001 §7, D183/D184 y D198 requieren esa respuesta específica.
T004 y la reactivación posterior quedan fuera; su propuesta deberá respetar la cola conservada.

## 7. Validación de esta propuesta

Contraste con SPECIFICATION §§5/9, ARCHITECTURE §§4/5/6/9, D035/D040/D083/D174/D198, T001 y
[flujo de chat](../flows/chat.md), más modelos/datos de chat en [DDBB-DIAGRAM](../DDBB-DIAGRAM.md).
No cambia producto, modelos, migraciones, API ni flujo implementado; se concreta la operación existente.

**Tres pruebas offline sintéticas correctas**: aceptación de propuesta que encola y ejecuta el flujo normal;
vistas previas de comandos sin efectos; restauración con JUnit, lecturas HTTP y rechazo de mutaciones.
Comando: `UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline pytest -q -n 0` con
`tests/product/test_chat.py::test_confirmed_proposal_becomes_a_linked_task_planned_executed_reviewed_and_committed`,
`tests/product/test_chat_global.py::test_all_command_previews_are_read_only_and_bind_the_observed_context` y
`tests/product/test_backup.py::test_junit_snapshots_events_and_http_queries_survive_restore`.
Un aviso de deprecación de Starlette/httpx ya existente. Sin CLI/proveedores reales, servicio, escritura privada,
build/instalación, backup/restauración del área o cambios del fixture. No se repiten suites completas,
frontend/tipos/build o Alembic al no cambiar código/datos.
Checks documentales correctos: parsers del producto con **12 fases, 7 criterios P012, 11 tareas y 199 decisiones**;
**616 enlaces/anclas relativos** en los cinco Markdown de esta entrega; presupuestos STATE/base/NEXT_STEPS
**15.861/24.576**, **9.171/12.288** y **28.121/49.152 bytes**. Cuerpos D001–D198 conservados;
diff revisado y `git diff --check` correcto. Sin cambios en producto, archivo histórico o baseline pública.
El resultado real, aún pendiente, se documentará en `P012-T003_CHAT_BACKUP_REAL.md` solo tras consentimiento.
