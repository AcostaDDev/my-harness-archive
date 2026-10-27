# Resumen de la fase P013 — Instalación guiada y configuración desde la UI

**Estado final:** completada y archivada documentalmente el 2026-10-27 (D232), tras el dictamen favorable
de T014/D231. Quince tareas y ocho criterios cumplidos en el alcance declarado.
**Decisiones:** D215–D232. Sin sucesora privada definida ni publicación ejecutada.

## Entregas y procedencia

| Tareas | Resultado | Evidencia |
|---|---|---|
| T001 | Contrato previo: instalación aislada, sesión sin TOML, autoridad privada/versionada, activación SQLite/CAS y perfil tras contexto. Diseño, sin producto | [Contrato](P013-T001_CONTRATO.md), [validación](P013-T001_VALIDACION.md), D216–D218 |
| T002 y T003 | `scripts/install` por generaciones desde clon o paquete, uv/rutas/cachés elegibles y offline por defecto; `scripts/start` fuera del checkout con DB/config/puerto explícitos | [Instalación](P013-T002_INSTALACION.md), [arranque](P013-T003_ARRANQUE.md), D219/D220 |
| T004 | Global v9/proyecto v1 en TOML privados inmutables, preview/diff, CAS y journal recuperable; migración 0026. Guardar no activa | [Configuración](P013-T004_CONFIGURACION.md), D221 |
| T005 y T006 | Asistente API protegido sin configuración y UI `/setup`/`/settings/configuration` con formulario/TOML validados, diff y confirmaciones separadas en/es | [API](P013-T005_ASISTENTE_API.md), [UI](P013-T006_ASISTENTE_UI.md), D222/D223 |
| T007 a T009 | Propuesta de perfil desde contexto o HEAD sin stack previo (0027, 54 tablas), preparación genérica con recibo propio y alta/activación desde la UI | [Propuesta](P013-T007_PROPUESTA_PERFIL.md), [preparación](P013-T008_PREPARACION.md), [alta](P013-T009_ALTA_UI.md), D224–D226 |
| T010 y T011 | Edición manual/asistida con contexto congelado e impacto conjunto; conversión explícita 1–8, backup formato 2 y consulta sin originales | [Edición](P013-T010_EDICION_ASISTIDA.md), [compatibilidad](P013-T011_COMPATIBILIDAD.md), D227/D228 |
| T012 | Primer uso instalado, ambas altas con Go/CLI falsos hasta COMMITTED, edición, backup/consulta y QA Chrome en/es; README y baseline pública | [Primer uso](P013-T012_PRIMER_USO.md), [matriz](P013_MATRIZ_ACEPTACION.md), D229 |
| T013 | Candidato `my_harness_dist_p013` y paquete distribution-1 cualificados en copia exacta aislada | [Candidato](P013-T013_CANDIDATO.md), [resultados](P013-T013_RESULTS.json), D230 |
| T014 | Dictamen favorable de ocho criterios y expediente nuevo sin acciones remotas | [Revisión original](P013_REVIEW.md), [expediente vigente](P013_EXPEDIENTE_APERTURA.md), D231 |
| T015 | Archivo por bytes, documentos vivos compactados y cierre manual | [Registro](P013_CIERRE.md), [revisión de cierre](REVIEW.md), D232 |

## Candidato y comprobaciones

T013 acredita sobre la copia exacta **2048 pytest y 29 subtests**, dos opt-in omitidas; **8 unittest, 155 Node**,
tipos/build, Alembic temporal, documentación pública y verificador del paquete instalado con agentes falsos.
T012 aporta las altas guiadas Go y la QA visual sobre sus paquetes de ensayo. T014 contrasta candidato, paquete
y documentos sin repetir suites. T015 verifica integridad, parsers, enlaces, presupuestos y conservación del
candidato; resultados en [P013_CIERRE](P013_CIERRE.md#verificación).

Candidato `0.1.0` desde `984c287`: **445 archivos/6.389.580 bytes**, manifiesto
[P013-T013_MANIFIESTO_PUBLICO.sha256](P013-T013_MANIFIESTO_PUBLICO.sha256), SHA-256
`ea0f74e9099f1383128ba5e6e2e92ac298447cab54bd7336909d66f0f800c428`.
Wheel `2416672d69b54524544d8560b41a54f49cb9747164faa1c82ac777672ad47076`, sdist
`31c9ab33a50a196ff7c2b0852d90bdf98eeabfb3f5ead427713c4b5049b5b22c` y pylock
`20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9`; paquete de 13 archivos con scripts/.
Candidatos D214, P012 y P011 conservados en sus destinos anteriores. El cierre solo cambia documentación
privada, excluida por la lista positiva; no reconstruye ni sustituye árbol o paquete.

## Límites y continuidad

Evidencia sintética: agentes, CLI y Go falsos, macOS ARM64 y Chrome; contención cooperativa sin sandbox del
sistema operativo. Sin proveedores reales nuevos, inferencia real del paquete final, otras plataformas o
navegadores, auditoría completa de accesibilidad, producción ni CI remota. La evidencia real de P012 conserva
sus wheels, pareja, consumos y límites; P013 no consume ni transfiere consentimientos.
Fallos instalados de T012, exportación rechazada y Node sin dependencias de T013, preparación FAILED y runs
STOPPED se conservan como resultados parciales. La consulta de backup no certifica muerte de escritores.

El siguiente paso corresponde al usuario: autorizar la apertura sobre el [expediente P013](P013_EXPEDIENTE_APERTURA.md)
y concretar owner/repo, visibilidad, identidad pública y permisos. Expedientes P011/P012 y suplemento D214
históricos y sustituidos. Tras el primer push, repositorio público como fuente principal (D157); modo continuo
v0.2.0 después de abrir (D156), sin fase ni tareas. [Candidatas sin fase](../../ROADMAP.md#candidatas-sin-fase-asignada).

## Archivo

[MANIFEST](MANIFEST.json) conserva 74 originales: STATE/NEXT_STEPS y 72 artefactos de docs/phase respecto de
`ff5109df44d65665db1e33a6f3f99f241d3928a0` (T014), incluidas capturas QA y logs. Los suplementos 2026-10-26
de D213/D214, sin fase y antecedentes de P013, se archivan aquí con esa procedencia. Los snapshots mantienen
estados, enlaces y comandos en su contexto original; T015 se acredita en los documentos nuevos de cierre.
P000–P012 no cambian. Este repositorio sigue sin registrarse ni ejecutarse con el harness; sin tag, push o publicación.
