# P012-T004 — Continuación con el vínculo del recibo corregido

Fecha: **2026-10-26**. Estado: **tarea COMMITTED; check fallido sin READY y servicio detenido**.
Base exacta: **9a9fa5d938236d6dd72d72561647c006c73e42f6**.
Guion: [continuación T013](P012-T013_VINCULO_RECIBO.md#propuesta-de-continuación-t004-sin-autorizar);
[primera parada T004](P012-T004_TYPESCRIPT_REAL.md) conservada por bytes.

## Consentimiento y comprobaciones iniciales

El usuario autoriza explícitamente construir/instalar la corrección, ejecutar la única tarea y cerrar P001 del
hijo, con **máximo nuevo 3 Claude/1 Codex**. Se conserva el deadline original **2026-10-26 12:00:10 UTC**,
cero correcciones/reintentos y la parada al primer fallo. Inicio de comprobaciones registrado **08:48:32 UTC**.

Fuentes T013 coinciden con sus dos hashes. Checkout del producto limpio; destinos dist-t013/venv-t013 ausentes,
puertos 8024/8025 libres, clave previa ausente y rutas canónicas sin enlaces. TOML T004 intacto
**3b9f433d…46a8d95**, ocho hashes de herramientas iguales; instalación T012 con **259 archivos del paquete**
iguales al wheel (también se contrastan los seis archivos de metadatos/licencias, excluido RECORD).

Hijo en **bcf59d8e20299c39df33a9aeea44845fc0409186**, checkout limpio, **23 archivos/modos** iguales;
commit técnico con sus nueve rutas exactas, recibo COMPLETED idéntico, sellos de idioma/receta conservados y
verify_receipt correcto. Temporal ignorado del escritor en 0700. Base aislada íntegra en 0025, **4.623 filas**,
**4 DONE/9 STOPPED/0 locks**, cero runs de tarea y **15 identidades propias dead** entre procesos/comandos.
Base anterior conservada con **16.798 filas**, además de **254 archivos/42 artefactos/tres fixtures** y diffs.
Identidades históricas de T003 conservan su incertidumbre; no se opera esa base.

El script privado de comprobación se ajusta antes de operar: distingue 259 archivos del paquete de metadatos,
cuenta solo runs purpose=task y usa el nombre real project_preparation_operations. Errores del script de
inspección, sin rechazo del producto, cambios de datos o procesos reales adicionales.

## Construcción, verificación e instalación offline

Comandos por etapas del guion, con PATH de Node/npm/uv y TMPDIR tmp/t004 explícitos, umask 077:

- build_distribution.py y check_distribution.py correctos en **dist-t013**. Miembros exactos, metadatos,
  licencias y SHA256SUMS; verificador aislado con CLI falsas: UI/API/sesión/definición/tarea/commit/reinicio/
  errores/restauración correctos. Esa evidencia sintética no acredita el recorrido con proveedores reales.
- Venv nuevo **venv-t013**, sincronización pylock e instalación wheel offline/sin dependencias implícitas;
  **259 archivos del paquete** instalados coinciden por bytes con el wheel, incluida la corrección.
- check-config --preflight correcto con **Claude 2.1.310/Codex 0.164.0**, contrato cli-14 y compatibilidad
  condicionada. Sin inferencia en el preflight.
- migrate --writers-stopped devuelve **current/0025**, snapshot=null. SHA-256 de SQLite idéntico y sin carpeta
  de snapshot. No se ejecuta init-db ni se repite receta/creación/validaciones iniciales del hijo.

| Artefacto | SHA-256 |
|---|---|
| Wheel | `70ee68832e3f95d0f36edc40d3cfcb1a961b38461645f7c764aca99c0c6cc1bb` |
| Sdist | `c6ea7f997595d6292c67371306d00278a0194540dded85f59d7bdd141e63eb2b` |
| Pylock | `20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9` |

## Acceso UI y parada de seguridad

Servicio iniciado **08:50:42 UTC**, desde AREA con venv-t013, state-t004/TOML conservados,
HOME command-home-t004, TMPDIR tmp/t004 y sin PYTHONPATH/configuración ambiental heredada. Único puerto 8024.
Chrome tiene una pestaña dedicada. Apertura inicial desde la barra nativa; login privado correcto al enviar
el formulario con Enter, sin guardar clave ni configuración. UI en español muestra el único proyecto
p012-typescript-es y la pareja prevista. Dos clicks de navegación no cambian la vista; una navegación de
extensión al href observado del detalle recibe **origin_rejected**. No se cambian Host/Origin/CSRF ni guardias.

Se aplica la parada del guion T004 §§5–6: **08:53:08 UTC**, grupo propio identificado por PID/inicio/argv
antes de SIGTERM; shutdown normal, grupo ausente, puertos 8024/8025 cerrados y clave retirada. Ninguna petición
de tarea nueva, run de tarea, READY, tag o cierre. **Consumo nuevo 0 Claude/0 Codex**, acumulado T004 **3/12 y 0/3**.

Conservación **08:53:49 UTC**: **16.798 filas anteriores y 4.623 filas T004 idénticas por todas sus columnas**,
cero filas nuevas; 4 DONE/9 STOPPED/0 locks, tres intentos de definición originales. Los 254 archivos,
42 artefactos, tres fixtures/diffs, ocho herramientas, TOML, 23 archivos/HEAD del hijo y recibo siguen iguales.
La parada acredita instalación/preflight/migrate/acceso inicial, todavía no tarea ni cierre.

Evidencia completa privada en AREA/state-t004/operator/t013-*: comprobaciones, copia SQLite/WAL/SHM,
logs, hashes de distribución/instalación, AX/captura del rechazo y parada/conservación. No se incorporan
claves, prompts, streams, bases o capturas privadas al repositorio.

## HITL de continuación

Se solicita reanudación explícita con **la misma instalación verificada**, base/TOML/recibo/hijo, acceso por
barra nativa a la ruta del producto y sin nueva construcción/receta. Mantener máximo nuevo **3 Claude/1 Codex**,
cero reintentos de tarea y deadline original **12:00:10 UTC**; si vence, revisar ventana antes de empezar.
Solo una petición nueva de tarea, luego READY/cierre/tag p001 del hijo y P002 ACTIVE vacía. La parada por
origin_rejected exige consentimiento nuevo según el guion; el saldo no lo sustituye. HITL respondido
con la autorización por barra nativa registrada a continuación.

## Reanudación autorizada por barra nativa

HITL recibido: **«Autorizar reanudación por barra nativa»**. Se verifican de nuevo plazo, puertos, TOML y
archivos instalados; sin nuevo build/instalación/preflight/receta. Servicio reabierto **08:55:18 UTC** con
los mismos parámetros, logs nuevos t013-resume-*. Entrada por barra nativa directamente al detalle observado;
la pantalla de login carga correctamente. Enter en el formulario completa el acceso al detalle preparado.
Navegación posterior por enlaces de la UI activados con Enter, sin usar goto de la extensión.

Nuevo proyecto → operación existente → Continuar con la definición: mismo bootstrap COMPLETED, recibo
preparado y P001 ACTIVE. NEXT_STEPS contrastado por su hash, cero runs de tarea previos; una sola activación
de **Encolar primera tarea**. Run nuevo **d1e35d32-de06-42e7-a8bc-91b71a586af8**, admitido y ejecutándose.
Sus versiones congeladas acreditan CLI **2.1.310/0.164.0**, receta typescript-web-recipe-2, idioma de contexto
**es** y project_environment_sha256 **0208aa4a…1196d4d**, igual al digest del recibo conservado; también
recipe_config_sha256 exacto. El bloqueo preparation_required de D206 queda superado con la corrección T013.

## Tarea COMMITTED y check fallido conservado

Claude sonnet/low planifica; Codex **gpt-6-luna/low** ejecuta una sola vez; tres validaciones del perfil
correctas y revisión Claude **ACCEPT**, sin hallazgos, preguntas, propuestas de decisión, permisos denegados o
ciclos de corrección. Los tres nuevos turnos Claude (plan/revisión/check) reportan **claude-sonnet-5-5**;
Codex conserva la selección solicitada, sin atribuirle un modelo reportado que su metadata no aporta.
La preparación previa a la tarea reinstala desde la caché offline; el perfil no declara formateador.

Diff exacto de **dos rutas**: `heading` pasa a `title.trim().replace(/ {2,}/g, " ") || "Proyecto"`, con
firma, exportación, trim exterior, defecto, sufijo y actualización del h1 conservados. Flujo español actualizado
con ese orden. No se tocan tests/scripts/dependencias/configuración. Inspección del diff acredita el caso de
espacios interiores; **el único caso JUnit existente no lo cubre**. Check/test/build exit 0; XML original
conservado/verificado, un caso passed, SHA-256 **9be33e817f2dea51f6716d5ac890e9235d2962a46e7dd9b7d03ab3676e8859a8**.

Confirmación de evidencia por UI y commit de tarea **ae86967ba54a2e881ec876e1db6f6b332abfd770**. El producto
conserva su mensaje determinista con el título de tarea español; no se reescribe ese commit o su historial.
El commit de esta entrega en my_harness se redacta en inglés. Checkout limpio y documentos mecánicos adoptados.

Único check inicial, run **c3a99262…**, operación **8deeaafd…**, finaliza **09:00:02 UTC**, estado **FAILED**.
La CLI termina correctamente, pero su payload combina **verdict=READY**, los cinco criterios passed y una
**required_action**: refrescar la prosa no gestionada de STATE, que aún dice scaffold/tarea pendientes.
El resumen la llama no bloqueante y sugiere hacerlo al cerrar, pero el contrato READY exige todas las listas de
acciones/preguntas vacías. El motor rechaza correctamente la respuesta contradictoria; no hay READY vigente.
La lectura del código confirma esa regla en validate_phase_result; no se debilita ni se altera el resultado.

Parada normal **09:00:45 UTC**, grupos propios detenidos/puertos cerrados/clave retirada. Conservación
**09:03:11 UTC**: base previa de **16.798 filas intacta**; **6.012 filas T004**, 1.389 nuevas frente a 4.623.
De las filas originales T004, 4.622 iguales y una fila managed_phases actualizada normalmente (documentos,
versión y fecha; definición intacta). **7 DONE/13 STOPPED/0 locks**, siete intentos COMPLETE incluyendo
los tres de definición anteriores. HEAD y recibo válidos; el diff respecto al commit técnico tiene solo las
dos rutas funcionales y STATE/NEXT_STEPS mecánicos. Sin tag p001 o cierre; P001 ACTIVE.
254 archivos/42 artefactos/tres fixtures/diffs/ocho herramientas/TOML anteriores intactos.

Consumo nuevo **3 Claude/1 Codex**; acumulado T004 **6/12 Claude y 1/3 Codex**. Se agota el techo nuevo,
sin transferir saldo de otros tramos ni autorizar más llamadas por el techo global no consumido.

## Propuesta de actualización documental y check nuevo

[Diff concreto de STATE](P012-T004_PROPUESTA_ACTUALIZAR_STATE.diff), preparado sin editar el hijo:
actualizar la prosa obsoleta con bootstrap/receta/tarea y sus commits reales, validaciones y límite JUnit;
registrar que el check falló y P001 sigue abierta. Conservar el bloque gestionado por bytes. No cambia la
tarea COMMITTED, su diff, tests, recibo, definición, check fallido o archivos congelados.

La UI ofrece edición documental humana con preview CAS/hash, motivo y commit conciliable. Se propone usar
esa operación, no una nueva ejecución Codex ni edición manual de SQLite/checkout. Después, **un Claude
adicional** para un check nuevo y, solo si READY, cierre/tag p001/archivo del hijo y P002 ACTIVE vacía.
Máximo nuevo revisado **4 Claude/1 Codex**, acumulado máximo T004 **7/12 y 1/3**, sin reejecución de tarea
y con deadline original **12:00:10 UTC**. Primer fallo vuelve a parar. Consentimiento solicitado, pendiente.


## Checks de la entrega

Sin cambios de producto, frontend, API o datos en my_harness. No se repiten suites completas, Node/tipos,
Alembic o pruebas del hijo fuera de las validaciones del propio run/check. El build incluye el build frontend;
el verificador del wheel usa exclusivamente fixtures/CLI falsas. Sin pruebas extra de espacios interiores.

Parsers documentales: **12 fases, 13 tareas, 208 decisiones**, **673 enlaces/anclas relativos** correctos en
los cinco Markdown de esta entrega; presupuestos STATE/base/NEXT_STEPS **22.284/24.576**, **9.171/12.288** y
**40.790/49.152 bytes**. Cuerpos D001–D207 conservados. Diff sin errores de whitespace; fuentes T013,
informes/propuestas anteriores y baseline pública intactos. Evidencia saneada; sin push, publicación,
tag en my_harness, cambios globales o operación sobre la base anterior.
