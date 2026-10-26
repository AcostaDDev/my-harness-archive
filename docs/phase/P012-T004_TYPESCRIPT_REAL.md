# P012-T004 — Creación TypeScript v2 y parada al encolar

Fecha: **2026-10-26**. **Estado: parcial, ejecutada y detenida; sin reintento.**
Guion autorizado: [propuesta del commit 9aefae3](P012-T004_PROPUESTA_TYPESCRIPT.md).
Decisión: [D206](../DECISIONS.md#d206--p012-t004-receta-completada-y-parada-por-preparation_required).
Producto T012/f948429, wheel **730891f8…f41520**, instalación `venv-t012` conservada.

## Consentimiento y aislamiento

El usuario responde **«autorizo»** a la solicitud específica: guion completo T004, máximo **12 Claude/3 Codex**,
una ejecución normal, cero correcciones/reintentos, cuatro horas y parada al primer fallo. Inicio **08:00:10 UTC**;
deadline original **12:00:10 UTC**. La instrucción posterior **«continúa.»**, recibida con la parada ya efectuada,
se aplica a conservación/diagnóstico offline; no se reanuda el recorrido ni se repone tiempo o saldo.

Se comprueban fuentes y **259 archivos instalados**, ocho hashes de herramientas, tres fixtures y sus diffs,
**254 archivos previos**, **42 artefactos** y siete hashes de entradas del guion. Base anterior íntegra en 0025,
**16.798 filas**, 13 DONE/1 QUEUED/14 STOPPED/0 locks; puertos libres y rutas nuevas ausentes, sin enlaces.
La identidad histórica unknown conserva la procedencia D204: no se certifica muerte ni se abre su base con el
supervisor. Se conservan copias de consulta de SQLite/WAL/SHM, sin crear otro backup/restauración del producto.

Se crean exclusivamente state-t004, TOML/entornos/npmrc y caché propios según el guion. TOML literal 0600 de
SHA-256 **3b9f433d…46a8d95**, sin cambios a los anteriores. Se copia un único objeto TypeScript 5.9.3 desde
la caché local: **4.377.468 bytes**, SHA-512 del lock exacto y SHA-256 **10e108c9…87a1d3**; sin índices,
credenciales o descargas. `check-config --preflight` pasa con **Claude 2.1.310/Codex 0.164.0** y compatibilidad
condicionada cli-14. `init-db` exclusivo crea la nueva base 0025, cero proyectos/jobs/procesos/locks y sin marca
de consulta. No se reconstruye, instala o migra nada existente.

## Creación y definición por UI

Único servicio operativo en **127.0.0.1:8024**, base/state nuevos, HOME/TMPDIR/PATH explícitos. Chrome abre una
pestaña dedicada mediante barra nativa y accede al login. Bitwarden bloquea el click DOM de login; Escape y
click nativo completan el acceso, sin guardar la clave, cambiar guardias o rechazo de origen del producto.
Preferencias de esta base nueva: visual y trabajo **es/es**. Selección de padre AREA/projects por preview/hash,
creación **typescript-es**, id **p012-typescript-es**, composición typescript, defaults **sonnet/low** y catálogo
**gpt-6-luna/low**, max_revision_cycles=0, bootstrap habilitado y confianza explícita en el fixture sintético.

| Turno Claude | Resultado y revisión de borradores antes de aceptar |
|---|---|
| 1, f9cabe43… | ANSWERED, doce documentos D088/flujo; código y receta declarados pendientes; sin preguntas bloqueantes |
| 2, aa9299fd… | ANSWERED, ROADMAP separa cierre de criterios READY, P002 con criterio en viñeta; NEXT_STEPS con campos/rutas/comandos separados; D006/D007 confirmadas desde el guion |
| 3, 788db348… | ANSWERED, único delta ROADMAP `Tag: p001`; la preview anterior mostraba sin tag, sin haber aceptado todavía |

**16 propuestas aplicadas por UI y CAS**: doce originales, tres aclaraciones y el campo tag. Son turnos normales
de definición dentro del límite de seis; ninguna tarea se ha ejecutado ni corregido. Las propuestas iniciales
y todas las vistas previas se conservan. Los tres intentos seleccionan sonnet/low y reportan **claude-sonnet-5-5**;
cero denegaciones observadas. No se afirma estabilidad futura del alias ni evaluación comparativa.

La preview final **eaef102456de…** acredita **14 archivos**, cinco criterios P001, única tarea P001-T001 y
tag p001. Se confirma por hash/motivo/checkbox: bootstrap **89187120… COMPLETED**, commit raíz
**dbc2d74a8e02b7f209416a88803cc08f3e1bb738**, mensaje inglés `Initialize project from confirmed bootstrap`.
P001 ACTIVE y documentos adoptados; P002 está en ROADMAP, aún sin crear como fase activa. El flujo usa
docs/flows/titulo.md, sin persistencia de aplicación, documentos en español y normalización aún pendiente.

## Receta completada

Preview UI **b92649f4d863…** en modo **offline**, idioma **es**, nueve archivos del manifiesto, argv/entorno,
lock, red desactivada, límites y commit técnico revisados. Confirmación explícita por UI de archivos/comandos/
instalación/commit dentro del hijo. Operación **472b2675… COMPLETED**, ocho pasos DONE:

- Archivos y entorno propios de la receta.
- Node 24.15.0 y npm 11.12.1, ambas comprobaciones exit 0.
- `npm ci --ignore-scripts --no-audit --no-fund --offline`, exit 0 desde el único objeto de caché copiado.
- `npm run check`, `npm run test`, `npm run build`, todos exit 0.
- Commit técnico **bcf59d8e20299c39df33a9aeea44845fc0409186**, mensaje inglés
  `harness: prepare TypeScript web (typescript-web-recipe-2)`.

El commit técnico añade exactamente .gitignore, index.html, package.json, package-lock.json, tsconfig.json,
src/main.ts, scripts/build.mjs, scripts/test.mjs y tests/main.test.mjs; ningún documento original cambiado.
JUnit completo con **un caso passed**, que comprueba título normal/vacío: no acredita espacios interiores.
SHA-256 del XML **301e5eceb6527ccd9218684b40c517d416472369f68498b71ea1b06c0770b0c8**.

| Sello del recibo | SHA-256 |
|---|---|
| Plan persistido | `488fe90e2b2c0f03a5e41414cc076e7f7529608d527dba3590108bf24af98b2a` |
| Fila de idioma, idéntica en plan/recibo | `7ccffe7ce54918e0ce2b3e2331d5ef5f37ba6cc11077fe8ee210e2ee6c8a2b6f` |
| Receta v2/es, idéntica en plan/recibo | `ba062ad8aa50b14958886265e79ab9c958accdc9e513a279e0aed86a2b4785c0` |

`verify_receipt` pasa antes del cierre documental. Checkout limpio, **23 archivos versionados** y HEAD técnico.
Se crea únicamente .local/codex-tmp en 0700 después de preparar, comprobado canónico e ignorado; no cambia el
recibo, manifiesto o ningún archivo versionado. La UI muestra «TypeScript web preparado» y habilita la tarea.

## Rechazo y parada

Se pulsa **una sola vez** «Encolar primera tarea» desde la creación. La petición normal del producto a
POST `/projects/p012-typescript-es/runs` devuelve **409 preparation_required**, con el diagnóstico
«prepara el proyecto antes de tareas o checks». Se conservan el aviso y la UI que simultáneamente declara la
preparación completada. **No se crea run/job P001-T001**, no hay planificación de tarea, intento Codex,
validación de tarea, aceptación o commit de tarea. No se usa otro endpoint, recarga/reinicio o selección de tarea
para sortear el rechazo. El ledger registra la intención de llamada; el consumo real lo acredita SQLite.

Servicio detenido normalmente **08:15:59 UTC**, por PID/grupo propios con inicio contrastado. Puertos 8024/8025
cerrados, clave retirada y shutdown completo. Conservación final **08:25:50 UTC**, dentro de la ventana original:

- Base nueva íntegra/FK correctas, **4.623 filas**, **4 jobs DONE/9 procesos STOPPED/0 locks**, receta COMPLETED.
- Tres intentos COMPLETE de definición; todos exit 0. Consumo real **Claude 3/12, Codex 0/3**.
- Grupos locales de los nueve procesos nuevos acreditados dead; seis identidades adicionales de comandos
  persistidas también dead. Esta evidencia es nueva y no se atribuye a las identidades históricas de T003.
- HEAD técnico y los 23 archivos del hijo idénticos al manifiesto posterior a receta, checkout limpio;
  recibo verificado y normalización de P001-T001 sin implementar. P001 ACTIVE, sin tag p001 ni cierre/P002 activa.
- **16.798 filas anteriores iguales por todas sus columnas** a la copia de conservación; tres hashes de bases,
  dos TOML, distribuciones, **254 archivos/42 artefactos/tres fixtures/diffs/ocho herramientas** intactos.
  El job de chat anterior sigue QUEUED sin intentos o preparación. Ninguna llamada nueva de T002/T003.

Evidencia completa privada bajo **AREA/state-t004/operator/**: before.json, logs de preflight/init-db/servicio,
previews/AX, mensajes de definición, ledger de intenciones, prepared.json, task-rejected-ax.txt/png, stop.json,
final.json y copia previa SQLite/WAL/SHM. No se incorporan prompts, streams, SQLite o claves al repositorio.

## Diagnóstico offline y dictamen

La traza estática localiza la guardia que rechazó la petición: `storage/preparation.admit` exige que las versiones
del nuevo trabajo contengan `project_environment_sha256 == digest(receipt)`, además de recipe_config coincidente
y verificación de archivos. Es la guardia correcta; no se propone debilitarla.

En `api/managed.frozen_versions`, una escritura llama `runtime.resolve_project`. En formatos v7/v8,
`LocalComposer.refresh(force=True)` recompone el proyecto para observar las CLI y devuelve versiones sin la
huella derivada del recibo. `ManagedRuntime.resolve_project` lo instala sin volver a pasar por
`ProjectPreparation.bind`. La lectura de preparación comprueba el recibo en SQLite/checkout y puede mostrar
prepared=true mientras la admisión usa versiones sin ese vínculo. Se acota **T013 offline** para reproducir
la secuencia con herramientas/datos sintéticos y restaurar el vínculo validado tras resolver las CLI, conservando
los rechazos legítimos, snapshots y huellas de recetas. No se repara el TOML, SQLite, recibo o fixture real.

| Criterio T004 | Dictamen |
|---|---|
| Creación UI, definición real es y receta v2/es offline con recibo/commit técnico | Acreditado en este entorno y pareja |
| Tarea hasta COMMITTED, código y flujo de la tarea en español | Pendiente: petición rechazada antes de crear run |
| READY, cierre/tag/archivo y P002 ACTIVE vacía | Pendiente; no solicitados |
| Consumo, parada y conservación | Acreditados: 3 Claude/0 Codex y parada normal |

**T004 sigue parcial.** La continuación operativa necesita corrección offline, propuesta con instalación/base
corregidas y consentimiento nuevo. El saldo no autoriza reintentar. T005–T007 pendientes y P012 abierta.
Esta entrega cambia solo documentación privada: no repite suites completas, npm o validaciones del hijo;
checks documentales, hashes, filas y diff pertinentes. La reproducción/corrección sintética corresponde a T013.
