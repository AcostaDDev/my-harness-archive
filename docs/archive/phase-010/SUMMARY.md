# Resumen de la fase P010 — Consolidación de la primera versión local

**Estado final:** completada y archivada documentalmente el 2026-10-22, primera versión local terminada en el
alcance declarado (D151/D153). **Decisiones:** D141–D153. **Plan:** doce tareas completadas (T001–T012), incluidas
T011 y T012 añadidas durante la fase. Sin fase sucesora definida, cambio de versión o publicación.

## Entregas

- **T001:** [contrato de consolidación](P010-T001_CONTRATO_CONSOLIDACION.md) e inventario; decisiones HITL sobre
  receta TypeScript, `npm ci`, proyección derivada y T011 (D142). Diseño separado de las implementaciones posteriores.
- **T002:** [receta `typescript-web-recipe-1`](P010-T002_ARRANQUE_TYPESCRIPT.md), dentro del marco D119:
  manifiesto y lock iniciales, preparación confirmada, instalación/validaciones antes del commit técnico,
  recuperación y manifiestos protegidos. Verificación sintética y con node/npm reales sobre caché, offline (D143).
- **T003 y T011:** [proyección `run-projection-1`](P010-T003_LECTURAS_RUNS.md), migración `0023`, consultas paginadas
  de runs, ciclos, diff y JUnit; [métricas y vista previa de exportación](P010-T011_METRICAS_SIN_HISTORIAL.md)
  sin decodificar historiales. Formatos 1–8, proyección transaccional y backup; historiales originales intactos.
  El motor y la exportación confirmada mantienen su autoridad histórica (D144/D145).
- **T004 y T005:** [marcadores opcionales en definición](P010-T004_MARCADORES_DEFINICION.md) y
  [evidencia de fases cerradas](P010-T005_FASES_CERRADAS.md): check/base/archivo históricos, renovación esperada
  de documentos vivos y avisos de deriva real, sin cambiar un READY histórico (D146/D147).
- **T006 y T012:** [documentación de instalación y alcance](P010-T006_DOCUMENTACION_VERSION.md) contrastada con
  código/CLI (D148); [CLI `migrate`](P010-T012_MIGRACION_INSTALADA.md) sobre base existente con copia previa
  `premigration-1`, parada declarada, guardias y conservación ante fallo (D150). El hueco detectado en T007
  queda corregido antes del paquete final; `init-db` y `serve` conservan sus contratos.
- **T007 y T008:** [matriz de trece criterios globales](P010_MATRIZ_ACEPTACION.md) con evidencia, dictamen y
  seguimiento (D149); [propuesta real complementaria](P010-T008_PROPUESTA_VALIDACION_REAL.md) y decisión explícita
  del usuario de aplazar A/B y D095 conservando su alcance solo offline (D151). El cursor gestionado de D029
  cumple el criterio 13 por decisión del usuario; no se declara SSE gestionado implementado.
- **T009:** [verificación final](P010-T009_VERIFICACION_FINAL.md), [revisión favorable](P010_REVIEW.md),
  [evidencia saneada](P010-T009_EVIDENCE.json) y doce capturas de QA sintética (D152). Wheel instalado fuera
  del checkout, sin proveedores reales ni operación de la instalación del piloto.
- **T010:** [cierre documental](P010_CIERRE.md), archivo exacto y documentos vivos actualizados (D153), después
  del dictamen y de resolver el alcance real. Sin ejecutar este repositorio en el harness.

## Aceptación, paquete y evidencia

[REVIEW](REVIEW.md) contrasta los siete criterios de ROADMAP con las entregas. La matriz acredita los trece
criterios de SPECIFICATION §10 en el alcance declarado; T012 resuelve la migración instalada y T009 la comprueba.
Últimos checks completos en T009, sobre `d6a69c8` (producto `dd7b958`): **1682 pytest, 121 subtests, 12 unittest,
82 Node, tipos/build y Alembic temporal correctos**; dos opt-in omitidas, sin recurrencia del intermitente de T007.
No son suites repetidas durante este cierre: comprobaciones actuales en [P010_CIERRE](P010_CIERRE.md).

Paquete `harness_local-0.1.0-py3-none-any.whl`, SHA-256
`94a6699e7c2e36cc42bcf45e1e2feb4d2028aa722756b47cb862087919792b17`, con UI/migraciones e instalación offline
por hashes. El verificador acredita sesión/CSRF, `migrate` `0022`→`0023` con instantánea previa, definición D088,
tarea/commit/reinicio idempotentes y backup/restauración de consulta, con datos y agentes falsos. La QA usa assets
idénticos a los del wheel y API sintética: presentación de escritorio, sin acreditar integración navegador/backend
adicional. Servicios propios detenidos en T009; su estado operativo no se vuelve a consultar en T010.

La evidencia con proveedores reales procede de D025/D050/D071 y del [piloto P009](../phase-009/SUMMARY.md),
con sus versiones y límites históricos. P010 no añade uso real ni amplía sus consentimientos. El Django hijo
conserva P001 CLOSED y sus cuatro tareas COMMITTED; este cierre no lo opera.

## Límites y trabajo futuro

A/B y el perfil Python/Django declarativo de D095 están implementados y verificados solo offline; validación
real aplazada expresamente por D151. La receta Django real de D139 está limitada a macOS arm64/Python 3.13 y
no acredita el perfil declarado. Chat, backup/restauración y receta TypeScript tampoco tienen uso real localizado.
Se mantienen contención cooperativa, manifiestos fijos tras preparar, protección de `tests/**` en TypeScript,
validaciones sin hora, reselección de carpeta tras reinicio que renumere dispositivo y avisos KaTeX.
[Alcance soportado](../../../README.md#alcance-soportado),
[límites de arquitectura](../../ARCHITECTURE.md#10-límites-conocidos) y
[candidatas sin fase](../../ROADMAP.md#candidatas-sin-fase-asignada).
No son tareas obligatorias pendientes del alcance cerrado; una futura operación real exige tarea y consentimiento propios.

## Archivo y contexto

[STATE](STATE.md), [NEXT_STEPS](NEXT_STEPS.md) y los 26 artefactos originales de `docs/phase/` (incluidas doce
capturas y el JSON de evidencia) conservan exactamente los bytes de `2e46c7143ea497774e813f092e36f10e7d662187`.
[MANIFEST](MANIFEST.json) registra las 28 rutas de origen/destino, tamaños y SHA-256. SUMMARY, REVIEW,
P010_CIERRE y el manifiesto son documentos nuevos de cierre, separados de los originales.

Los originales son snapshots: sus estados, enlaces relativos y comandos se interpretan desde su ruta de origen
en ese commit. No se adaptan al moverlos. Para navegar desde el archivo, usar este resumen, REVIEW y las
referencias vigentes de [DECISIONS](../../DECISIONS.md); para reproducir una entrega, consultar la base y los
requisitos de su informe, sin reutilizar consentimientos. P000–P009 conservan todos sus bytes.

Cierre manual bajo D002/D088/D114/D140/D153, separado del check READY del producto; sin registro, SQLite o tag
propios, agentes, proveedores, nueva fase del hijo, cambio de configuración global, push o publicación.
