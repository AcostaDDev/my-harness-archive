# Resumen de la fase P008 — Contrato documental unificado, cierre de fase e importación de proyectos

**Estado final:** completada y archivada el 2026-10-19 por la continuación solicitada por el usuario (D114).
**Decisiones:** D088–D114. **Plan:** veinte tareas completadas (T001–T020).

## Entregas

- T001–T003: migración documental de este repositorio y layout unificado obligatorio, DECISIONS único con
  índice, instrucciones raíz y plantilla; creación v1 retirada. Rutas del ejecutor y paridad de datos/flujos,
  con propuestas de ADR. [Migración](P008-T001_MIGRACION_DOCUMENTAL.md); D089 y D090.
- T004: cierre y abandono con archivo unificado, originales por bytes, commit conciliable y sucesora opcional
  sin tareas; planificación posterior confirmada y definición versionada.
  [Entrega](P008-T004_CIERRE_UNIFICADO.md), D091.
- T005–T007: prompts y definición alineados; API/UI con instrucciones, diagramas, flujos, trabajo de fase e
  índice de decisiones; AGENTS en el contexto congelado de cada rol salvo definición.
  [Prompts](P008-T005_PROMPTS_DEFINICION.md), [API/UI](P008-T006_API_UI.md),
  [instrucciones](P008-T007_INSTRUCCIONES_CONTEXTO.md); D092–D094.
- T008: perfiles declarados en `local-config-4`, argv sin shell y JUnit, hash de composición y ejemplo
  Python/Django. [Entrega](P008-T008_PERFILES_DECLARATIVOS.md), D095.
- T009–T012, Flujo A: inventario documental de HEAD, mapa determinista, conversación de solo lectura,
  borradores privados y commit confirmado con continuidad. Originales conservados, CAS, D099 y recuperación
  con la misma intención/run/commit, adopción de fase atómica y `0020_project_imports`.
  [Inventario](P008-T009_INVENTARIO_FLUJO_A.md), [mapa](P008-T010_MAPA_NORMALIZACION.md),
  [conversación](P008-T011_PROPUESTA_REVISOR.md), [commit](P008-T012_COMMIT_CONTINUIDAD.md); D096–D100.
- T013–T015, Flujo B: inventario estático de código, ingeniería inversa sobre exportación privada de HEAD,
  documentos/perfil confirmados y commit documental con P001 adoptada. No ejecuta herramientas del proyecto,
  modifica código ni escribe el TOML. [Inventario](P008-T013_INVENTARIO_FLUJO_B.md),
  [conversación](P008-T014_INGENIERIA_INVERSA.md), [incorporación](P008-T015_INCORPORACION_CONFIRMADA.md); D101–D103.
- T016–T020: correcciones de las revisiones de salida. Filtros/includes, bytes y destinos ignorados
  ([T016](P008-T016_FRONTERA_GIT.md), D105); referencias vigentes
  ([T017](P008-T017_REFERENCIAS_VIGENTES.md), D106); lectores sin lazy-fetch y objetos ausentes
  ([T018](P008-T018_OBJETOS_LOCALES.md), D108); gitlinks rechazados antes de inspeccionar hijos
  ([T019](P008-T019_SUBMODULOS.md), D110); escritor A/B con objetos locales en ambas APIs y recuperación
  ([T020](P008-T020_ESCRITOR_LOCAL.md), D112). Contrato final: `cli-12`, `document_layout = "d088-12"`.

## Revisión y límites

Cinco revisiones de salida (D104, D107, D109, D111 y D113). La [última](P008_REVISION_SALIDA_5.md) deja H1–H7
resueltos en las comprobaciones y los siete criterios de ROADMAP cumplidos offline; [dictamen](REVIEW.md).
Al finalizar: 1.436 pytest y 121 subtests, 12 checks ligeros, 75 Node, tipos/build, Alembic temporal, OpenAPI,
paridad de datos y documentación correctos. Es evidencia de D113, no una repetición de la suite en el cierre.

Sin QA visual, Django/ruff/mypy reales ni recorrido de producto completo con CLI reales en esta fase;
revisión humana de documentos inferidos y contención cooperativa. El perfil Python/Django sigue pendiente
de confirmar sobre un proyecto real. Continúan los límites y candidatas de
[ROADMAP](../../ROADMAP.md#candidatas-sin-fase-asignada). No queda sucesora ni plan aprobado.

## Archivo y reproducción

[STATE](STATE.md), [NEXT_STEPS](NEXT_STEPS.md) y los 33 artefactos de trabajo se conservan exactamente como
en `9c8887989332028a906349351e5554b4e2ad7a80`. El [manifiesto](MANIFEST.json) registra cada ruta de origen y
destino, tamaño y SHA-256; [registro del cierre](P008_CIERRE.md) y verificación de integridad.

Los originales son snapshots: sus enlaces relativos y comandos se interpretan desde la ruta de origen que
recoge el manifiesto, en aquel commit. No se han adaptado al moverlos. Para navegar el archivo actual,
usar esta página, REVIEW y las referencias vigentes de [DECISIONS](../../DECISIONS.md).

Los scripts de revisión calculan su raíz desde `docs/phase/`; para reproducir una revisión, usar un checkout
separado del commit que la registró y el comando de su documento. Estos commits contienen el script original
y el código de ese momento; los JSON identifican además el código evaluado antes de registrar cada revisión.

| Revisión | Commit que la registró | Resultado que acredita |
|---|---|---|
| Primera | `f1b0510` | Reproducción de H1–H3. |
| Segunda | `09ba87f` | Guardias H1–H3 y reproducción de H5. |
| Tercera | `2063356` | Guardias H1–H5 y reproducción de H6. |
| Cuarta | `66c1286` | Guardias H1–H6 y reproducción de H7. |
| Quinta | `9c88879` | Guardias H1–H7 corregidas. |

Las reproducciones antiguas acreditan fallos previos a su corrección; no se espera que pasen con el código final.
No confundir sus resultados ni sobrescribir sus evidencias. La copia archivada conserva los mismos bytes.

Cierre documental manual según D002/D088/D114, sin registrar ni ejecutar el harness sobre este repositorio,
check READY, SQLite o tag de fase. La próxima prioridad queda a elección del usuario.
