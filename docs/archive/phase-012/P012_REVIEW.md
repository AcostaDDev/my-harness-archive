# P012 — Revisión de salida

Fecha: **2026-10-26**. Tarea: [T006](../NEXT_STEPS.md#p012-t006--revisión-de-salida-y-expediente-de-apertura-actualizado).
Base revisada: **`99b1b9954d543259a84956940ea8543035551077`**, entrega T005, checkout inicialmente limpio.
Decisión: [D211](../DECISIONS.md#d211--p012-t006-dictamen-favorable-y-expediente-actualizado).

**Dictamen favorable en el alcance declarado.** Los siete criterios de salida de P012 tienen evidencia trazable;
no quedan correcciones obligatorias pendientes. Habilita **T007**, cierre documental manual, que sigue pendiente.
El [expediente nuevo](P012_EXPEDIENTE_APERTURA.md) identifica el candidato verificado y sustituye al de P011
para una apertura futura. El dictamen no autoriza publicarlo ni ejecuta acciones remotas.

## 1. Método y procedencia

Se contrastan los [siete criterios vigentes](../ROADMAP.md#p012--validación-real-previa-a-la-apertura-pública)
con las entregas T001–T005 y T008–T013, sus decisiones y la baseline pública de T005. La evidencia real corresponde
a los wheels y tramos de cada informe; el candidato final se valida offline en T005. No se presenta el wheel final
como una nueva ejecución con proveedores reales, ni se convierten las continuaciones en reintentos de los runs fallidos.

En T006 se contrastan listas, bytes, modos, hashes y estructura documental con el
[comprobador estático](P012-T006_check.py), incluido el árbol publicable reproducido en memoria desde el commit
T005. Se leen los logs locales de T005 (`.local/p012-t005/logs/`): suites y verificador correctos. No se repiten
esos comandos ni operaciones del área real. Los informes saneados son la evidencia de los recorridos; no se
reanuda un servicio para volver a observarlos ni se certifica su estado operativo actual.

La [revisión archivada de P011](../archive/phase-011/P011_REVIEW.md) conserva sus diez criterios y trece globales;
no se reescribe. La suite completa de T005 incluye sus regresiones vigentes y las de P012. P012 añade la evidencia
real descrita abajo, sin afirmar que todos los criterios globales se hayan probado con proveedores reales.

## 2. Matriz de los criterios de salida

| # | Criterio P012 | Evidencia y procedencia | Dictamen y límites |
|---|---|---|---|
| 1 | Propuesta operativa confirmada, área/wheel/CLI/pareja, techos y consentimiento por tramo | [T001](P012-T001_PROPUESTA_OPERATIVA.md), D184; consentimientos y hashes en [T002](P012-T002_RESULTADO_T011.md), [T003 inicial](P012-T003_CHAT_BACKUP_REAL.md) y [UI](P012-T003_UI_RESULTADO_T012.md), [T004 inicial](P012-T004_TYPESCRIPT_REAL.md) y [continuación](P012-T004_CONTINUACION_T013.md) | **Cumple.** Claude 2.1.310 revisor `sonnet/low`, Codex 0.164.0 ejecutor `gpt-6-luna/low`, cli-14/compatibilidad condicionada. Techo no equivale a permiso de usar saldos. Consentimientos consumidos, sin nuevas operaciones autorizadas |
| 2 | Plan → ejecución → validación → revisión → COMMITTED con v8 y wheel instalado fuera del checkout | [T002/D198](P012-T002_RESULTADO_T011.md): wheel `f22521ff…acd3201`, run `e3fa4ae6…`, commit `6f021211b307`, seis comandos/13 JUnit, ACCEPT y confirmación de bytes; [T004/D209](P012-T004_CONTINUACION_T013.md) complementa otro perfil | **Cumple.** Una ejecución exitosa con cero correcciones; modelo reportado Claude `claude-sonnet-5-5`, Codex sin modelo reportado en los metadatos observados. No extrapola a otras parejas/versiones |
| 3 | Incorporación B Django sintética, originales intactos, documentos confirmados y tarea con perfil declarado D095 | [B/D191](P012-T002_INCORPORACION_REAL.md#23-incorporación-committed-y-reenvío-idempotente-autorizado): `976b1d1`, mismo job al reenviar; [B2/D193](P012-T002_CONTINUACION_T009.md): `9808fd9`, 15 originales; [tarea v8/D198](P012-T002_RESULTADO_T011.md) sobre clon documental B2 conservado | **Cumple con evidencia acumulada.** No se repite B con el último wheel ni se atribuye tercera incorporación al registro del clon. Formateador sobre dos archivos sin cambios; no acredita reparación automática de estilo. Django existente/perfil declarado, sin creación Django v2 |
| 4 | Chat real, comando y propuesta confirmada; backup/restauración y consulta de runs reales | [T003/D200](P012-T003_CHAT_BACKUP_REAL.md): dos ANSWERED, `/estado` sin modelo, propuesta ACCEPTED/P001-T002 `d235e9d5…` QUEUED sin intentos; cuatro comandos backup/restore, 42 artefactos/13 runs, 16.798 filas iguales, API/409; [T012/D202](P012-T012_VISTA_CONSULTA.md) y [UI/D204](P012-T003_UI_RESULTADO_T012.md): Chrome es, detalle/diff/JUnit/métricas/fallos/cola y rutas operativas bloqueadas | **Cumple con salvedad autorizada.** La propuesta queda vinculada pero no se ejecuta. Identidades históricas `unknown`, grupos locales ausentes: consulta no certifica muerte de escritores ni habilita reactivar la base. API y UI conservan procedencia distinta |
| 5 | TypeScript nuevo v2/es, preparación con caché, tarea COMMITTED y cierre P001 con READY | [T004/D206](P012-T004_TYPESCRIPT_REAL.md): definición UI/bootstrap `dbc2d74`, receta offline/recibo y técnico `bcf59d8`; [continuación D208/D209](P012-T004_CONTINUACION_T013.md): tarea `ae86967`, tres validaciones/un JUnit; READY válido `dd0d3be3…` sobre `c58712e`, tag del hijo `p001`, archivo `ecbc47f` | **Cumple.** P001 CLOSED y P002 ACTIVE vacía, objetivo/criterio elegidos por HITL D205; sin plan posterior. Dos checks rechazados conservados. El JUnit existente no cubre espacios interiores; el comportamiento se contrasta por diff. Archivo de cuatro documentos, sin contenido adicional en docs/phase del hijo |
| 6 | Fallos acotados, correcciones sintéticas y parciales explícitos | Matriz de §3; entregas [T008](P012-T008_CORRECCION_PREFLIGHT.md), [T009](P012-T009_DIAGNOSTICO_ENTORNO_CODEX.md), [T010](P012-T010_FORMATEADOR_DECLARATIVO.md), [T011](P012-T011_PRESETS_UI_V8.md), [T012](P012-T012_VISTA_CONSULTA.md), [T013](P012-T013_VINCULO_RECIBO.md); regresiones incluidas en suite T005 | **Cumple.** Sin reparar historiales, payloads, SQLite o tareas fallidas; sin relajar permisos, esquema, identidad o guardias. Éxitos posteriores no prueban causa del truncamiento ni estabilidad/calidad general de los modelos |
| 7 | Alcance público por fila, candidato/suites/paquete/manifiesto nuevos, revisión y expediente sin ejecutar | [T005/D210](P012-T005_CANDIDATO.md), [manifiesto público](P012-T005_MANIFIESTO_PUBLICO.sha256), [paquete](P012-T005_PAQUETE.sha256), esta revisión y [expediente](P012_EXPEDIENTE_APERTURA.md) | **Cumple.** 401 archivos/5.480.755 bytes, manifiesto `cf191a40…9362a`; sustitución autorizada con P011 conservada. Revisión/hash documental nueva en T006; suites de T005 válidas, CI remota pendiente. P012 sigue abierta hasta T007 |

## 3. Fallos, correcciones y resultados conservados

| Observación | Tratamiento y evidencia de resolución | Límite conservado |
|---|---|---|
| Caché Django incompleta y lector de choices multilínea | Descargas de doce wheels autorizadas por separado D186; [T008/D187](P012-T008_CORRECCION_PREFLIGHT.md), 25 regresiones nuevas/229 tests dirigidos; preflight real posterior D188 y D198 | Ayudas/archivos reales permanecen privados; fixtures de tests sintéticos |
| Aperturas automatizadas rechazadas por origen o autenticación/UI | Paradas D188–D190/D200 y T004, diagnóstico y nueva autorización; acceso manual/barra nativa acreditado en informes | Guardias Host/Origin/CSRF intactas; no garantiza compatibilidad con automatizadores/extensiones |
| Primer escritor deja tres rutas vacías, REVISION_LIMIT `b94eedef…` | [T009/D192](P012-T009_DIAGNOSTICO_ENTORNO_CODEX.md) acota entorno y temporales; fixture limpio autorizado D193, resultados separados | Causa del truncamiento no demostrada; original y diff no reparados |
| B2: 13 tests pasan, Ruff check/formato fallan, REVISION_LIMIT `f98b16d9…` | [T010/D194](P012-T010_FORMATEADOR_DECLARATIVO.md): opción de formateador con 28 regresiones; recorrido v8 D198 | Motor D133 existente; ampliación elegida por HITL, sin afirmar defecto del motor o reparación del fallo anterior |
| UI oculta presets de v8 antes del alta | [T011/D196](P012-T011_PRESETS_UI_V8.md), ocho regresiones React; selección real D198 | Continuación bloqueada D195 conservada, sin operar pareja heredada |
| Copia de consulta sin página UI de run independiente | [T012/D202](P012-T012_VISTA_CONSULTA.md), 102 tests Python y 16 regresiones React/router; UI real D204 | D040 ya cubría API; ampliación UI decidida aparte, sin autoridad de ejecución |
| Identidad histórica del host distinta antes de consulta UI | Parada D203 y excepción expresa D204 para consulta; T004 en base nueva aislada | `unknown` permanece; no hay certificación retrospectiva de muerte ni autorización de reactivación |
| Receta válida y admission 409 preparation_required | [T013/D207](P012-T013_VINCULO_RECIBO.md), reproducción HTTP roja, 14 variantes nuevas/24 tests de módulo y 226 relacionados; admisión y digest del recibo exacto D208 | Sin editar recibo o aceptar deriva; preparación original no repetida |
| Dos checks sin READY válido: required_action y criterion parafraseado | [D208/D209](P012-T004_CONTINUACION_T013.md): ambos rechazados; edición documental por UI/CAS y dos checks nuevos con consentimientos individuales; tercero válido | Sin normalizar respuestas o modificar guardias/definición. No se reejecuta tarea Codex |

No quedan hallazgos obligatorios de producto, privacidad o paridad pendientes en este alcance. La referencia de
líneas imprecisa de T002 y la propuesta documental QUEUED de T003 pertenecen al fixture y siguen conservadas;
no son tareas de corrección pendientes de my_harness. Las ampliaciones no acreditadas siguen en ROADMAP.

## 4. Consumo y omisiones

| Tramo | Claude consumido/techo | Codex consumido/techo | Cierre acreditado en su informe |
|---|---|---|---|
| T002 | 9/12 | 3/3 | 11 DONE/12 STOPPED/0 locks; 14.921 filas finales, servicio parado |
| T003, incluida UI posterior | 2/3 | 0/0 | 13 DONE/1 QUEUED/14 STOPPED/0 locks; 16.798 filas, consulta parada; identidad histórica incierta |
| T004 aislada, incluidos HITL adicionales | 8/12 | 1/3 | 11 DONE/15 STOPPED/0 locks; 7.460 filas T004; 16.798 previas intactas; servicio parado |
| Total P012 | **19/27** | **4/6** | Sin transferir saldos o renovar consentimientos; tiempos documentados por tramo |

En T006: **cero llamadas**, servicios, builds, instalaciones, validaciones de fixtures o acciones de GitHub.
Única red de esta revisión: lectura de documentación oficial de GitHub/CLI para contrastar el procedimiento del
expediente. Sin autenticación en cuentas ni lectura/escritura de repositorios remotos.

Límites que permanecen: macOS ARM64/Chrome, pareja actual única en P012 y compatibilidad condicionada; las cuatro
parejas y creación Django real históricas son anteriores a cli-14. Sin creación Django v2 real, matriz completa
de idiomas, producción, otras plataformas/CLI o evaluación comparativa. Sin nuevas pruebas visuales/accesibilidad,
reinicio con escritor real vivo, historiales grandes o exportación real. Contención cooperativa sin aislamiento
del SO, validaciones sin hora, manifiesto de receta fijo y dos avisos low de KaTeX. CI remota sin ejecutar.

## 5. Candidato y comprobaciones de T006

Identidad íntegra del candidato y del paquete en el [expediente §1](P012_EXPEDIENTE_APERTURA.md#1-candidato-revisado).
Se mantiene la evidencia offline de T005: **1760 pytest y 29 subtests**, dos opt-in omitidas; **8 unittest,
119 Node**, tipos/build, Alembic temporal, verificador de distribución instalada sintética, **31 Markdown/260
enlaces y 36 diagramas**. Los logs de pytest, unittest, Node y check_distribution confirman esos resultados.
El error de variable reservada de los primeros envoltorios zsh sigue declarado en T005; no invalida las suites.

Comprobaciones nuevas, sin repetir suites:

```sh
UV_CACHE_DIR=.local/uv-cache uv run --frozen --offline python docs/phase/P012-T006_check.py
git diff --check
```

El [resultado estático](P012-T006_COMPROBACION.json) registra reproducción del manifiesto desde el commit T005,
fuentes públicas actuales iguales, 401 hashes/modos del destino y 387 hashes de P011, wheel/sdist/pylock/SHA256SUMS,
parsers/presupuestos/enlaces y conservación de originales de phase/archive y cuerpos D001–D210.
Diff revisado, exclusivamente documentación privada; sin cambios de producto, datos, API o flujos.

**Siguiente: T007.** Solo después del cierre documental podrá el usuario autorizar los pasos concretos de apertura.
