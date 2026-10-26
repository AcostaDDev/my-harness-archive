# Resumen de la fase P012 — Validación real previa a la apertura pública

**Estado final:** completada y archivada documentalmente el 2026-10-26 (D212), tras el dictamen favorable
de T006/D211. Trece tareas y siete criterios cumplidos en el alcance declarado.
**Decisiones:** D183–D212. Sin sucesora privada definida ni publicación ejecutada.

## Entregas y procedencia

| Tareas | Resultado | Evidencia |
|---|---|---|
| T001 | Propuesta operativa y pareja/presupuestos confirmados; consentimiento propio por tramo | [Propuesta](P012-T001_PROPUESTA_OPERATIVA.md), D184 |
| T002 | Dos incorporaciones B COMMITTED e idempotencia; tarea Python/Django con perfil/formateador v8 COMMITTED `6f021211b307` | [B original](P012-T002_INCORPORACION_REAL.md), [B2](P012-T002_CONTINUACION_T009.md), [resultado acumulado](P012-T002_RESULTADO_T011.md), D191/D193/D198 |
| T003 | Dos respuestas de chat, comando sin modelo, propuesta confirmada QUEUED, backup/restauración y consulta API/UI | [Chat/API](P012-T003_CHAT_BACKUP_REAL.md), [consulta UI](P012-T003_UI_RESULTADO_T012.md), D200/D204 |
| T004 | Creación TypeScript v2/es, preparación offline, tarea COMMITTED `ae86967`, READY válido y cierre del hijo `ecbc47f`, P002 vacía | [Creación/preparación](P012-T004_TYPESCRIPT_REAL.md), [continuación y cierre](P012-T004_CONTINUACION_T013.md), D205–D209 |
| T008 y T009 | Choices multilínea corregidos con regresiones sintéticas; entorno del escritor diagnosticado sin atribuir causa al truncamiento | [Preflight](P012-T008_CORRECCION_PREFLIGHT.md), [diagnóstico](P012-T009_DIAGNOSTICO_ENTORNO_CODEX.md), D187/D192 |
| T010 y T011 | Formateador optativo en perfiles declarados v8 y selector UI de presets compatible | [Perfil](P012-T010_FORMATEADOR_DECLARATIVO.md), [presets](P012-T011_PRESETS_UI_V8.md), D194/D196 |
| T012 y T013 | Vista UI de copias de consulta y vínculo del recibo conservado tras resolver CLI | [Consulta](P012-T012_VISTA_CONSULTA.md), [recibo](P012-T013_VINCULO_RECIBO.md), D202/D207 |
| T005 | Alcance público en/es por fila y candidato/paquete verificados; sustitución local autorizada conservando P011 | [Entrega](P012-T005_CANDIDATO.md), D210 |
| T006 | Revisión favorable de siete criterios y expediente nuevo sin acciones remotas | [Revisión original](P012_REVIEW.md), [expediente vigente](P012_EXPEDIENTE_APERTURA.md), D211 |
| T007 | Archivo por bytes, documentos vivos compactados y cierre manual | [Registro](P012_CIERRE.md), [revisión de cierre](REVIEW.md), D212 |

## Candidato y comprobaciones

T005 acredita **1760 pytest y 29 subtests**, dos opt-in omitidas; **8 unittest, 119 Node**, tipos/build,
Alembic temporal, verificador del paquete instalado y documentación pública (31 Markdown/260 enlaces/36 diagramas).
T006 contrasta candidato, paquete y documentos sin repetir suites. T007 verifica integridad, parsers, enlaces,
presupuestos y conservación del árbol público; resultados actuales en [P012_CIERRE](P012_CIERRE.md).

Candidato `0.1.0`: **401 archivos/5.480.755 bytes**, manifiesto
[P012-T005_MANIFIESTO_PUBLICO.sha256](P012-T005_MANIFIESTO_PUBLICO.sha256), SHA-256
`cf191a40914095aeb3fbbeea0e6485878cc3218754361fa78d314b87dc19362a`.
Wheel `eef56a29c268839487f23e53493fd728361e31589ce0535a1f3f01e50b4504ab`, sdist
`0f290f05d1a93f5117d0eac01f1b6b175bad61ad1e88613580441cce3072a384` y pylock
`20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9`.
`my_harness_dist` conserva el candidato sin Git; P011 sigue íntegra en `my_harness_dist_p011_74cc9141`.
El cierre solo cambia documentación privada, excluida por la lista positiva; no reconstruye ni sustituye el paquete.

## Límites y continuidad

Evidencia real acumulada de los wheels y tramos identificados en los informes, con fixtures sintéticos,
macOS ARM64/Chrome y pareja Claude 2.1.310 → Codex 0.164.0, cli-14/compatibilidad condicionada.
El paquete final de T005 tiene verificación offline; no una ejecución real adicional. Sin creación Django v2,
otras parejas actuales, matriz completa de idiomas, producción, otras plataformas o comparación de modelos.
Cuatro parejas y creación Django históricas anteriores a cli-14 conservan su procedencia.

Dos REVISION_LIMIT, dos checks rechazados y propuesta QUEUED permanecen intactos. Identidad histórica `unknown`
con salvedad autorizada para consulta; no se certifica muerte de escritores ni se habilita reactivar la base.
Consumo total P012: **19 Claude/4 Codex** (techos por tramo en la revisión T006); sin renovar consentimientos.
Contención cooperativa, validaciones sin hora, receta de manifiesto fijo y dos avisos low de KaTeX conservados.
Sin CI remota ni nueva QA visual/accesibilidad del candidato final.

El siguiente paso corresponde al usuario: autorizar la apertura sobre el [expediente P012](P012_EXPEDIENTE_APERTURA.md)
y concretar owner/repo, visibilidad e identidad pública. El expediente P011 permanece histórico y sustituido.
Tras el primer push, repositorio público como fuente principal (D157); modo continuo v0.2.0 después de abrir
(D156), sin fase ni tareas nuevas. [Candidatas sin fase](../../ROADMAP.md#candidatas-sin-fase-asignada).

## Archivo

[MANIFEST](MANIFEST.json) conserva 42 originales: STATE/NEXT_STEPS y 40 artefactos de trabajo respecto de
`ce4b5d2f8ed1a1ac1af9cec00316b10b1d95a814` (T006). Los snapshots mantienen estados, enlaces y comandos en
su contexto original; T007 se acredita en los documentos nuevos de cierre. P000–P011 no cambian.
Este repositorio sigue sin registrarse ni ejecutarse con el harness; sin tag, push o publicación.
