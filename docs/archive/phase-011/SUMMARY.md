# Resumen de la fase P011 — Preparación para apertura pública en GitHub

**Estado final:** completada y archivada documentalmente el 2026-10-24, con dictamen favorable de T017 y expediente
de apertura sin ejecutar (D181/D182). **Decisiones:** D154–D182. **Plan:** veinticuatro tareas completadas
(T001–T024), incluidas T019–T024 añadidas durante la fase por ampliación o desglose HITL. Sin publicación, tag,
cambio de versión ni fase sucesora definida.

## Entregas

- **T001 y T002:** [contrato de apertura](P011-T001_CONTRATO_APERTURA.md) e [inventario](P011-T001_INVENTARIO.md)
  de 688 rutas (D159); [licencia MIT y contenido publicable](P011-T002_CONTENIDO_PUBLICABLE.md), titular David
  Acosta, escaneo estático de 690 archivos y 4.009 objetos sin credenciales reales identificadas (D160).
- **T019:** [retirada del harness anterior](P011-T019_RETIRADA_LEGACY.md) de UI/API/CLI, observadores/SSE,
  activación y normalización A; creación desde cero e incorporación B conservadas, datos y migraciones intactos (D161).
- **T003–T006:** comentarios, docstrings, descripciones OpenAPI y nombres de pruebas en inglés por grupos
  ([núcleo](P011-T003_INGLES_NUCLEO.md), [backend](P011-T004_INGLES_BACKEND.md),
  [cliente y herramientas](P011-T005_INGLES_CLIENTE_HERRAMIENTAS.md), [pruebas](P011-T006_INGLES_PRUEBAS.md)),
  con AST idéntico salvo excepciones registradas y recetas v1 conservadas por bytes/huella (D162–D165).
- **T007, T008, T020 y T009:** [preferencias globales de idioma](P011-T007_INFRAESTRUCTURA_IDIOMAS.md) (`0024`, D166),
  [idioma de trabajo inmutable por raíz](P011-T008_IDIOMA_PROYECTO.md) con par congelado por job/intento (`0025`,
  `local-config-6`, D167), [recetas v2](P011-T020_RECETAS_V2.md) con el idioma sellado en plan/recibo (D168) y
  [directiva al agente y documentos generados en el idioma de trabajo](P011-T009_PROMPTS_DOCUMENTOS_BILINGUES.md) (D169).
- **T010, T021 y T022:** [interfaz React en/es](P011-T010_TRADUCCION_PRODUCTO.md) por catálogos tipados (D170) y
  textos visibles del servicio/CLI en en/es ([antes españoles](P011-T021_TRADUCCION_SERVICIO_CLI.md),
  [antes ingleses](P011-T022_TRADUCCION_SERVICIO_INGLES.md)), con técnicos ingleses listados y rechazos por código (D171/D172).
- **T011 y T012:** [contrato de compatibilidad CLI](P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md) por capacidades (D173) e
  [implementación](P011-T012_COMPATIBILIDAD_CLI.md) `local-config-7`/`cli-14`: detección automática, mínimos Codex
  0.163.0 / Claude 2.1.304 y posteriores con compatibilidad condicionada (D174).
- **T013:** [matriz semántica](P011-T013_MATRIZ_DIAGRAMAS.md) de flujos, ER y arquitectura contra código/tests;
  catorce hallazgos documentales corregidos sin cambiar el producto (D175).
- **T014 y T023:** [baseline pública](P011-T014_DOCUMENTACION_PUBLICA.md) en `docs/public/`, README inglés de primer
  uso y `README.es.md` (D176); [especificación, arquitectura, datos y flujos públicos](P011-T023_DOCUMENTACION_TECNICA_PUBLICA.md)
  en inglés, autocontenidos (D177).
- **T015, T016 y T024:** [paquete candidato `0.1.0`](P011-T015_PAQUETE_PUBLICO.md), CI sintética e instantánea
  pública sin Git (D178); [primer uso desde clon limpio](P011-T016_PRIMER_USO_QA.md) con CLI falsas hasta COMMITTED
  y `pylock.toml` (D179); [QA de navegador](P011-T024_QA_NAVEGADOR.md) del candidato instalado en las ocho
  combinaciones idioma/tema/ancho, con tres correcciones de presentación (D180).
- **T017:** [revisión de salida](P011_REVIEW.md) favorable de los diez criterios y los trece globales y
  [expediente de apertura](P011_EXPEDIENTE_APERTURA.md) con acciones remotas propuestas, ninguna ejecutada (D181).
- **T018:** [cierre documental](P011_CIERRE.md), archivo exacto y documentos vivos actualizados (D182).

## Aceptación, candidato y evidencia

[REVIEW](REVIEW.md) contrasta los diez criterios de ROADMAP con las entregas; el dictamen detallado y la matriz de
los trece globales (1/11/13 en la redacción de D161) están en [P011_REVIEW](P011_REVIEW.md). Últimos checks completos
en T017, sobre `cde2112` más sus cambios: **pytest 1671 y 29 subtests, unittest 8, Node 95**, dos opt-in omitidas;
build del paquete y `check_distribution` del candidato final correctos. Este cierre no repite suites: comprobaciones
actuales en [P011_CIERRE](P011_CIERRE.md).

Candidato público: 387 archivos, 5.402.952 bytes, manifiesto
[`P011-T017_MANIFIESTO_PUBLICO.sha256`](P011-T017_MANIFIESTO_PUBLICO.sha256) con SHA-256
`74cc9141da0295a0a658dc10673a454c93eae3fd3cfe86e3df5aa7b9a172ea71`. Wheel
`46d29c209f90a8f67c02e4295753688ec0c646c5c0f0259575fed5910117d9d6`, sdist
`79e256de8a3fa14d29465fbcbaea47b8600908b7b5a1dcfd43b3f6f83cc842c5` y `pylock.toml`
`20a327c3a97484892280c6dec6d2176202c2a88ebd638878e0808eeadfdf2cf9`. El cierre solo cambia `docs/` privada, excluida
del candidato: el manifiesto público y los artefactos siguen siendo los de T017.

P011 no usa CLI reales, proveedores ni inferencia. La evidencia real sigue siendo la histórica de D025/D050/D071 y del
[piloto P009](../phase-009/SUMMARY.md), con sus versiones y límites; los dobles no acreditan sesión, inferencia ni
calidad lingüística.

## Límites y trabajo posterior

Solo macOS ARM64 verificado; Linux, Windows y la CI remota sin ejecutar. Mínimos de CLI por contrato, sin
caracterización real en P011; B y D095 siguen aplazados (D151) y A queda retirado sin validarse. Códigos técnicos
visibles por decisión (D180), contenido libre sin traducir, QA solo en Chrome y contención cooperativa sin aislamiento
del sistema operativo. Detalle en [P011_REVIEW §6](P011_REVIEW.md#6-excepciones-y-límites-declarados).

La apertura remota sigue el [expediente](P011_EXPEDIENTE_APERTURA.md) y exige instrucción explícita del usuario para
cada paso. Su paso 1 cita el script en la ruta de origen `docs/phase/`: tras el archivo se ejecuta desde un worktree
temporal del commit de T017, como indica [P011_CIERRE](P011_CIERRE.md#reproducir-el-candidato). Desde la apertura,
el repositorio público es la fuente principal (D157) y el modo continuo queda para v0.2.0 (D156).
[Candidatas sin fase](../../ROADMAP.md#candidatas-sin-fase-asignada).

## Archivo y contexto

[STATE](STATE.md), [NEXT_STEPS](NEXT_STEPS.md) y los 61 artefactos originales de `docs/phase/` (incluidas 18
capturas de T024, scripts de comprobación, manifiestos y la evidencia de T016) conservan exactamente los bytes de
`4eeda84a586240a4ac51e8ad78eed2c13a7e34ad`. [MANIFEST](MANIFEST.json) registra las 63 rutas de origen/destino,
tamaños y SHA-256. SUMMARY, REVIEW, P011_CIERRE y el manifiesto son documentos nuevos de cierre.

Los originales son snapshots: sus estados, enlaces relativos y comandos se interpretan desde su ruta de origen en
ese commit, sin adaptarlos al moverlos. P000–P010 conservan todos sus bytes. Cierre manual bajo
D002/D088/D114/D153/D182, separado del check READY del producto; sin registro, SQLite o tag propios, agentes,
proveedores, cambio de configuración global, push ni publicación.
