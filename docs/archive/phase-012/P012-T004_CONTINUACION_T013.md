# P012-T004 — Continuación con el vínculo del recibo corregido

Fecha: **2026-10-26**. Estado: **T004 completada con evidencia acumulada; P001 del hijo CLOSED y servicio detenido**.
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
y con deadline original **12:00:10 UTC**. Primer fallo vuelve a parar. Consentimiento solicitado y
respondido con la autorización registrada más abajo.


## Checks del registro inicial de esta continuación

Sin cambios de producto, frontend, API o datos en my_harness. No se repiten suites completas, Node/tipos,
Alembic o pruebas del hijo fuera de las validaciones del propio run/check. El build incluye el build frontend;
el verificador del wheel usa exclusivamente fixtures/CLI falsas. Sin pruebas extra de espacios interiores.

Parsers documentales: **12 fases, 13 tareas, 208 decisiones**, **673 enlaces/anclas relativos** correctos en
los cinco Markdown de esta entrega; presupuestos STATE/base/NEXT_STEPS **22.284/24.576**, **9.171/12.288** y
**40.790/49.152 bytes**. Cuerpos D001–D207 conservados. Diff sin errores de whitespace; fuentes T013,
informes/propuestas anteriores y baseline pública intactos. Evidencia saneada; sin push, publicación,
tag en my_harness, cambios globales o operación sobre la base anterior.

## HITL documental ejecutado y segunda parada

HITL recibido: **«Autorizar edición documental y 1 Claude adicional»**. Techo nuevo 4 Claude/1 Codex,
acumulado máximo 7/12 y 1/3, deadline original conservado. Servicio reabierto **09:09:06 UTC**, misma
instalación/base/configuración. Login privado y navegación por enlaces Enter, sin cambiar guardias.

Editor de STATE muestra la prosa editable y el bloque gestionado separado/protegido. Se aplica únicamente
el prefijo de la propuesta; preview **a7396c355b6e…**, base ae86967, STATE **c761b64c… → 0b979f0f…**.
Diff exacto revisado, motivo y checkbox confirmados por UI. Operación/run **e83c08fd… COMMITTED**,
commit documental **c58712eed9ff1bc57bc0521ada957ab7fce73222**, hashes adoptados por la fase. La lectura
posterior compara archivo completo con propuesta y bloque gestionado original por bytes: iguales.
Única ruta del commit docs/STATE.md, checkout limpio; sin llamada de agente en esta edición.

Check nuevo **4357e769-fb11-40c1-94e2-312e8e1c7774**, una llamada Claude sonnet/low, termina exit 0 con
READY, cinco resultados passed, acciones/preguntas vacías. Pero el segundo criterion se parafrasea:

- Congelado: «Firma, trim, defecto y sufijo conservados; actualización del h1 conservada.»
- Devuelto: «Firma, trim, defecto, sufijo y actualización del h1 conservados.»

La directiva language-directive-1 ya exige copiar criterion exactamente; no falta en el prompt. La guardia
validate_phase_result rechaza correctamente la discrepancia: operación **FAILED**, sin READY vigente.
No se corrige/normaliza el payload ni se cambia el contrato o la definición para admitirlo. No acredita un
defecto funcional nuevo del hijo. Segundo resultado y primer check fallido conservados.

Parada normal **09:13:45 UTC**, servicio/grupo propios detenidos, clave retirada y puertos cerrados.
Conservación **09:15:13 UTC**: **6.757 filas T004**, 745 nuevas desde el primer check; de las 6.012
anteriores solo cambia la fila de fase por adopción/versión/fechas. **9 DONE/14 STOPPED/0 locks**,
ocho intentos COMPLETE, un solo run de tarea COMMITTED, recibo válido y HEAD c58712e limpio, sin tag p001.
**16.798 filas anteriores/254 archivos/42 artefactos/tres fixtures/diffs/ocho herramientas intactos**.
Consumo nuevo **4 Claude/1 Codex**, acumulado T004 **7/12 y 1/3**. P001 sigue ACTIVE.

## Tercer check autorizado sin cambios

Nuevo HITL: **«Autorizar un check más con 1 Claude»**. Solo un check adicional, sin cambiar producto,
documentos, modelo, guardias o respuestas anteriores; cierre únicamente con READY válido. Máximo nuevo
**5 Claude/1 Codex**, acumulado máximo T004 **8/12 y 1/3**, mismo deadline **12:00:10 UTC**.
Servicio reabierto **09:15:44 UTC** tras verificar puertos/plazo, recibo válido y grupos propios dead.
Sin nueva edición, receta, build o Codex; HEAD c58712e y ocho intentos previos contrastados antes del envío.

## READY válido, cierre y conservación final

Tercer check **dd0d3be3-606a-4494-a3d7-712836733e61**, operación **b4189e44… READY**, sobre
**c58712eed9ff1bc57bc0521ada957ab7fce73222**, vínculo **9b0e4f67fedf…**. Cinco criterios literales
correctos/passed, sin acciones o preguntas; validate_phase_result comprueba también el payload persistido.
UI «Lista para cerrar», checkout limpio, diez jobs DONE y cero locks antes de confirmar.

Confirmación UI del motivo/checkbox sobre ese READY: cierre **CLOSED**, commit de archivo
**ecbc47f1ea9142e8e141a90eaa2d963857dbd39a**, mensaje inglés `harness: archive P001`.
**Tag ligero p001** exclusivamente del hijo sobre **c58712e**, el HEAD evaluado; no sobre el commit posterior
de archivo. Se archivan **cuatro archivos**: STATE y NEXT_STEPS iguales por bytes a los originales previos
al cierre, SUMMARY/REVIEW generados. No existían artefactos en docs/phase/: esta ejecución no acredita un
movimiento de contenido adicional de esa carpeta. ROADMAP y documentos vivos renovados; checkout limpio,
recibo intacto y válido, sin cambio funcional posterior a la tarea.

UI y SQLite acreditan **P001 CLOSED** y **P002 ACTIVE con cero tareas/runs**, definición número 1, sin tag.
No se pulsa planificación, lote, tarea o check de P002. Objetivo/criterio conservan la procedencia HITL D205.

Parada normal final **09:19:04 UTC**: servicio/grupo propios detenidos, puerto 8024 y 8025 cerrados,
claves de las cuatro aperturas retiradas y shutdown completo. Conservación **09:20:23 UTC**:

- Base T004 íntegra/FK correctas en **0025**, **7.460 filas**, **2.837 nuevas** frente a 4.623 iniciales.
  **4.622 filas originales intactas** y una fila de fase actualizada normalmente; definición original intacta.
  Las 6.757 filas de la segunda parada se conservan, salvo la evolución normal de esa misma fila de fase.
- **11 jobs DONE/15 procesos STOPPED/0 locks**, nueve intentos COMPLETE: tres de definición anteriores,
  plan/ejecución/revisión y tres checks. **36 identidades propias de procesos/comandos dead**.
- **16.798 filas de la base anterior iguales por todas sus columnas**, job de chat QUEUED intacto;
  **254 archivos/42 artefactos/tres fixtures/diffs/ocho herramientas** iguales. Incertidumbre histórica de
  T003 conservada; no se opera su base ni se certifica muerte de esos escritores.
- venv-t012 y venv-t013: sus **259 archivos del paquete** más metadatos/licencias coinciden con sus respectivos
  wheels. TOML, recibo y archivos protegidos iguales; p001 y los commits reales conservados.
- Consumo final nuevo **5 Claude/1 Codex**, dentro de los consentimientos sucesivos; acumulado T004
  **8/12 Claude y 1/3 Codex**, sin correcciones/reintentos de ejecución. Los dos checks rechazados se
  conservan, seguidos de un check nuevo autorizado; no se reparan sus resultados ni se cambian guardias/modelo.

| Criterio T004 | Dictamen y procedencia |
|---|---|
| Creación/definición UI en es y receta TypeScript v2/es offline | Acreditado en D206; no repetido |
| Tarea COMMITTED y paridad de flujo | Acreditado en ae86967, esta continuación; tres comandos/un JUnit passed |
| READY y cierre/tag/archivo, P002 ACTIVE vacía | Acreditado tras HITL: READY dd0d3be3, tag c58712e y archivo ecbc47f |
| Consumo, parada y conservación | Acreditado en ambos informes; nuevo 5/1 y acumulado 8/1, dentro de ventana |

**T004 completada con evidencia acumulada**, conservando las tres paradas y ambos checks fallidos.
P012 sigue abierta; siguiente tarea **T005**, actualización del alcance público/candidato con esta evidencia.
No se inicia esa tarea en esta entrega ni se extiende el consentimiento a proveedores, reejecuciones,
publicación, push, tags de my_harness o fases posteriores del hijo.


## Checks finales de esta entrega

Parsers correctos: **12 fases, 13 tareas y 209 decisiones**; **672 enlaces/anclas relativos**
en los cinco Markdown. Presupuestos STATE/base/NEXT_STEPS **22.339/24.576**,
**9.171/12.288** y **40.516/49.152 bytes**. D001–D208 conservadas por cuerpos;
fuentes de producto/T013, informes congelados y baseline pública intactos. Diff revisado y sin errores de
whitespace. No suites completas nuevas: esta entrega cambia documentación y opera el wheel ya corregido;
el verificador de paquete y las validaciones reales aportan las comprobaciones pertinentes.
