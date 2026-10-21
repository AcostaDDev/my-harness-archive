# Resumen de la fase P009 — Proyecto Django desde cero y piloto con cuatro combinaciones de agentes

**Estado final:** completada y archivada documentalmente el 2026-10-21 por la continuación solicitada por el usuario
(D140). **Decisiones:** D115–D140. **Plan:** veinte tareas completadas (T001–T020).

## Entregas

- T001–T004: contrato y producto de carpeta de proyectos elegida desde UI, creación exclusiva de hijos nuevos,
  autoridad persistente y retirada auditada; presets por proyecto en `local-config-5`; receta Django confirmada
  después de D088 con entorno acreditado y commit técnico separado. Migraciones `0021`/`0022`, API/UI y flujos
  actualizados. [Contrato](P009-T001_CONTRATO_CREACION.md), [carpeta](P009-T002_CARPETA_PROYECTOS.md),
  [agentes](P009-T003_AGENTES_PROYECTO.md), [receta](P009-T004_RECETA_DJANGO.md); D116–D119.
- T005–T007 y T013–T015: ensayo temporal con agentes falsos y Django real; propuesta y consentimientos del piloto;
  CLI caracterizadas (Codex 0.163.0 y Claude 2.1.304), definición Codex fuera de Git (`cli-13`) y verificación completa
  del wheel con D088. Creación real desde UI de `harness-django-pilot`, documentos y preparación Django.
  [Ensayo](P009-T005_ENSAYO_DJANGO.md), [propuesta](P009-T006_PROPUESTA_PILOTO.md),
  [creación](P009-T007_CREACION_DJANGO.md), [CLI](P009-T013_CARACTERIZACION_CLI.md),
  [definición](P009-T014_DEFINICION_SIN_GIT.md), [wheel](P009-T015_VERIFICACION_WHEEL.md).
- T008–T012: cuatro tareas COMMITTED del mismo Django, conservando id/checkout/historial y cambiando los roles
  entre tareas: Codex→Codex, Codex→Claude, Claude→Claude y Claude→Codex. CRUD, completar/reabrir/filtros y búsqueda;
  QA conjunto y P001 del hijo READY/CLOSED, tag `p001` sobre `47a0557`, archivo en `3d105c6`, sin sucesora.
  [Matriz, métricas y cierre](P009-T012_CIERRE_PILOTO.md); D127–D139.
- T016–T019: suite pytest en paralelo (de más de 25 minutos a unos cuatro), rutas `dir/` congeladas como `dir/**`,
  recibos de preparación válidos tras renumerar dispositivo en reinicio y formato determinista del perfil después
  de cada turno del ejecutor. Corrigen los bloqueos observados sin reescribir contratos o evidencias previas.
  [Suite](P009-T016_SUITE_RAPIDA.md), [rutas](P009-T017_RUTAS_DIRECTORIO.md),
  [recibo](P009-T018_RECIBO_TRAS_REINICIO.md), [formato](P009-T019_FORMATEO_PERFIL.md).
- T020: selector de tareas del NEXT_STEPS vivo con CAS, contrato literal y notas adicionales congeladas que llegan
  a planificador/ejecutor/revisor sin ampliar permisos. [Entrega](P009-T020_ENCOLAR_DESDE_DOCUMENTOS.md), D135.

## Revisión y límites

[REVIEW](REVIEW.md) contrasta los siete criterios de ROADMAP con las entregas y la revisión final de T012/D139.
Última suite completa del harness, en T020: 1597 pytest correctos y uno omitido (Django real), 12 unittest,
81 Node, tipos/build y OpenAPI correctos. T015 verifica entero un wheel nuevo con agentes sintéticos.
T012 acredita el QA real del hijo y seis validaciones, incluidos 27 tests. Son verificaciones previas con
procedencia, no suites repetidas durante el archivo; checks actuales en [P009_CIERRE](P009_CIERRE.md).

Consumo final: 26 de 60 invocaciones, T012 2 de 2. Sin autorización para operaciones nuevas. Evidencia real
limitada a macOS arm64/Python 3.13.13; sin clasificación de modelos ni coste/tiempo humano completos. El perfil
declarativo Python/Django sigue pendiente de piloto propio; se conserva la contención cooperativa.
Las observaciones de alta sin redirección, marcadores de define-project y deriva visual de fase cerrada
quedan como candidatas en [ROADMAP](../../ROADMAP.md#candidatas-sin-fase-asignada). Sin fase sucesora ni plan aprobado.

## Archivo y contexto

[STATE](STATE.md), [NEXT_STEPS](NEXT_STEPS.md) y los 26 artefactos de trabajo (incluidas tres imágenes y el JSON
de wheels) conservan exactamente los bytes de `422357145d4120a9d55a65783864054ee3e96378`.
[MANIFEST](MANIFEST.json) registra las 28 rutas de origen/destino, tamaños y SHA-256.

Los originales son snapshots: sus estados, enlaces relativos y comandos se interpretan desde su ruta de origen
en ese commit. No se adaptan al moverlos. Para navegar desde la ubicación actual, usar SUMMARY, REVIEW y las
referencias vigentes de [DECISIONS](../../DECISIONS.md). Para reproducir comandos de una entrega anterior,
consultar el commit que identifica su informe y sus requisitos, sin reutilizar consentimientos de operación real.
Las fases P000–P008 permanecen intactas.

Cierre documental manual bajo D002/D088/D114/D140, separado del cierre gestionado de P001 del Django hijo.
Este repositorio sigue sin registrarse ni ejecutarse en el producto; sin check READY, SQLite ni tag propios.
