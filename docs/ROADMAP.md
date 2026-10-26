# Roadmap — my_harness

Fases del desarrollo de Harness Local. Formato del parser del harness (`## PNNN — título`, **Objetivo**, **Criterios de
salida**), sin bloques gestionados mientras el repositorio no esté registrado (D088). Las fases P001–P007 son los
hitos H0–H6 del backlog original; la definición inicial está en [archive/phase-000](archive/phase-000/SUMMARY.md).

| Fase | Título | Estado | Archivo |
|---|---|---|---|
| P001 | Contratos y prueba de viabilidad | completada (2026-10-11) | [phase-001](archive/phase-001/SUMMARY.md) |
| P002 | Visor útil sin ejecutar agentes | completada (2026-10-11) | [phase-002](archive/phase-002/SUMMARY.md) |
| P003 | Núcleo reusable y ejecución gestionada | completada (2026-10-12) | [phase-003](archive/phase-003/SUMMARY.md) |
| P004 | Personalización, bloqueos y cierre | completada (2026-10-13) | [phase-004](archive/phase-004/SUMMARY.md) |
| P005 | Chat y creación de proyectos | completada (2026-10-13) | [phase-005](archive/phase-005/SUMMARY.md) |
| P006 | Calidad de uso y distribución local | completada (2026-10-13) | [phase-006](archive/phase-006/SUMMARY.md) |
| P007 | Agentes configurables e interfaz de producto | completada (2026-10-15) | [phase-007](archive/phase-007/SUMMARY.md) |
| P008 | Contrato documental unificado, cierre de fase e importación de proyectos | completada (2026-10-19) | [phase-008](archive/phase-008/SUMMARY.md) |
| P009 | Proyecto Django desde cero y piloto con cuatro combinaciones de agentes | completada (2026-10-21) | [phase-009](archive/phase-009/SUMMARY.md) |
| P010 | Consolidación de la primera versión local | completada (2026-10-22) | [phase-010](archive/phase-010/SUMMARY.md) |
| P011 | Preparación para apertura pública en GitHub | completada (2026-10-24) | [phase-011](archive/phase-011/SUMMARY.md) |
| P012 | Validación real previa a la apertura pública | completada (2026-10-26) | [phase-012](archive/phase-012/SUMMARY.md) |
| P013 | Instalación guiada y configuración desde la UI | activa, T001 diseñada/T002–T005 implementadas (2026-10-26) | [plan](phase/P013_PLAN.md) |

## P001 — Contratos y prueba de viabilidad

**Objetivo:** Inventariar el harness de referencia, fijar versiones y capacidades de las CLI y levantar un esqueleto
local que muestre una ejecución simulada sin acceso a modelos.
**Criterios de salida:**
- Fixtures sintéticos de aceptación, revisión, bloqueo, interrupción y cierre, sin secretos ni datos reales.
- Matriz de capacidades y autenticación documentada; parsers de streams probados offline.
- La aplicación arranca localmente y muestra una ejecución simulada.
**Estado:** completada el 2026-10-11 (antes H0) — [archivo](archive/phase-001/SUMMARY.md).

## P002 — Visor útil sin ejecutar agentes

**Objetivo:** Importar y navegar el historial de un harness anterior y observarlo de forma incremental.
**Criterios de salida:**
- Una segunda importación no duplica registros; lo ausente aparece como no registrado.
- Desde una tarea se llega al intento, la revisión y la evidencia que explican su resultado.
- Cerrar y abrir el navegador no pierde ni duplica actividad.
**Estado:** completada el 2026-10-11 (antes H1) — [archivo](archive/phase-002/SUMMARY.md).

## P003 — Núcleo reusable y ejecución gestionada

**Objetivo:** Extraer el motor con contexto explícito y ejecutar, revisar y completar una tarea desde la UI con
recuperación verificable.
**Criterios de salida:**
- Motor aislado con pruebas de caracterización; persistencia, cola idempotente y exclusión por checkout.
- Adaptadores CLI con captura incremental y cancelación; un error conserva evidencias sin fallback.
- Commit limitado a lo revisado y conciliable tras una caída; migración a gestionado exclusiva y reversible.
- API y UI gestionadas hasta COMMITTED con recuperación explícita.
**Estado:** completada el 2026-10-12 (antes H2) — [archivo](archive/phase-003/SUMMARY.md).

## P004 — Personalización, bloqueos y cierre

**Objetivo:** Prompts versionados, permisos con recuperación y fases con check, cierre, lote y enmiendas.
**Criterios de salida:**
- Activar un prompt no altera intentos anteriores; variables inválidas bloquean la llamada.
- Una petición caducada o modificada no acepta una autorización previa; revalidar y reintentar son distintos.
- Un READY obsoleto no cierra la fase; las preguntas pendientes impiden avanzar.
**Estado:** completada el 2026-10-13 (antes H3) — [archivo](archive/phase-004/SUMMARY.md).

## P005 — Chat y creación de proyectos

**Objetivo:** Chat contextual que crea tareas trazables, bootstrap guiado desde carpeta vacía y un segundo perfil.
**Criterios de salida:**
- «Ajusta X» genera una tarea vinculada y ejecutada por el motor, sin ruta lateral.
- Crear desde carpeta vacía termina con una primera tarea acotada y verificable.
- Un perfil TypeScript web funciona sin condiciones nuevas en el núcleo.
**Estado:** completada el 2026-10-13 (antes H4) — [archivo](archive/phase-005/SUMMARY.md).

## P006 — Calidad de uso y distribución local

**Objetivo:** JUnit, backup, retención, diagnósticos, distribución, sesión local y recorridos E2E; después, validaciones
nativas, configuración TOML y primer uso real.
**Criterios de salida:**
- Instalar en un entorno limpio, completar un flujo y restaurar un backup sin el checkout de desarrollo.
- Validaciones del producto con captura acotada y recuperación; composición de uso real por TOML.
**Estado:** completada el 2026-10-13 (antes H5) — [archivo](archive/phase-006/SUMMARY.md).

## P007 — Agentes configurables e interfaz de producto

**Objetivo:** Revisor y ejecutor con proveedor elegible, contrato documental por fase, métricas, creación conversacional
e interfaz de producto por URL.
**Criterios de salida:**
- Cuatro combinaciones revisor/ejecutor verificadas, con historiales anteriores legibles.
- Contrato documental v2, métricas por intento y creación conversacional implementados offline.
- UI: recorrido completo por URL con QA en claro, oscuro y móvil; diffs paginados.
**Estado:** completada el 2026-10-15 (antes H6, D087) — [archivo](archive/phase-007/SUMMARY.md).

## P008 — Contrato documental unificado, cierre de fase e importación de proyectos

**Objetivo:** Que todo proyecto gestionado, incluido este repositorio, siga la estructura documental de D088, que el
cierre de fase archive y reinicie de forma determinista y que se puedan incorporar proyectos de un harness anterior o
sin harness.
**Criterios de salida:**
- Este repositorio sigue la estructura de D088, con enlaces y diagramas validados.
- Plantilla, contratos, prompts y API usan solo la estructura unificada, obligatoria para todo proyecto; creación v1
  retirada.
- Cerrar una fase tras READY archiva STATE, NEXT_STEPS, REVIEW, SUMMARY y `docs/phase/`, reinicia STATE y NEXT_STEPS y
  marca ROADMAP con enlace al archivo, en un commit conciliable.
- Cada intento recibe `AGENTS.md` del checkout en su contexto congelado.
- Perfiles declarativos en el TOML local, incluido Python/Django con pytest, ruff y mypy.
- Los flujos A y B llevan repositorios sintéticos de cada origen al contrato documental con un commit confirmado, sin
  escritura del agente ni pérdida de historial.
- Checks offline en verde; ningún proveedor real sin consentimiento específico.
**Dependencias:** P007.
**Fuera de alcance:** Rediseño visual de la UI; recorridos con CLI reales; publicación del paquete.
**Estado:** completada el 2026-10-19 por la continuación solicitada por el usuario
([D114](DECISIONS.md#d114--cierre-documental-manual-de-p008)) — [archivo](archive/phase-008/SUMMARY.md).
T001–T020 completadas; la quinta revisión de salida (D113) acredita los siete criterios cumplidos offline
y H1–H7 resueltos en sus comprobaciones. Dictamen en [REVIEW](archive/phase-008/REVIEW.md);
entregas, revisiones previas y límites conservados en el [estado archivado](archive/phase-008/STATE.md)
y el [plan archivado](archive/phase-008/NEXT_STEPS.md).

Cierre documental manual, sin registro ni check READY del producto sobre este repositorio y sin tag de fase.
STATE y NEXT_STEPS se reiniciaron sin sucesora en ese cierre. El usuario define después P009 (D115);
la instantánea de P008 conserva el estado original. Plan vigente en [NEXT_STEPS](NEXT_STEPS.md).

## P009 — Proyecto Django desde cero y piloto con cuatro combinaciones de agentes

**Objetivo:** Crear desde la UI un proyecto Django pequeño en una carpeta de proyectos elegida por el usuario,
y desarrollar cuatro tareas del mismo proyecto alternando revisor/ejecutor, con validaciones y commits reales.
**Criterios de salida:**
- «Elegir carpeta de proyectos» permite guardar y retirar una raíz explícita; el servicio puede crear proyectos
  hijos sin volver a pedir ese permiso de carpeta. La IA no decide la ubicación ni obtiene escritura en la raíz padre.
- Crear un proyecto desde cero muestra raíz, nombre y destino exacto; no requiere crear la carpeta hija,
  el esqueleto Django o el entorno a mano. Rechaza destinos existentes y escapes, con recuperación idempotente.
- El proyecto tiene documentación D088, Django, SQLite, plantillas, dependencias fijadas y validaciones reales
  de pytest/JUnit, ruff, mypy, comprobaciones Django y migraciones. Instalación/red solo dentro del plan autorizado.
- La UI permite elegir por proyecto los proveedores de ambos roles y modelo/esfuerzo del revisor, desde
  configuración del servicio. El revisor decide modelo/esfuerzo del ejecutor y deja el motivo congelado por tarea.
- Cuatro tareas distintas llegan a COMMITTED en un único proyecto/id/checkout: Codex→Codex, Codex→Claude,
  Claude→Claude y Claude→Codex (revisor→ejecutor). Cambiar ajustes conserva el historial y no altera jobs congelados.
- El pequeño gestor de tareas permite crear/listar, editar/borrar, completar/reabrir/filtrar y buscar. QA en
  navegador, tests y cierre READY/archivo de su primera fase; evidencia con procedencia y métricas por tarea.
- Checks offline de los cambios del harness y ensayo sin proveedores correctos antes del piloto autorizado.
  Revisión de salida de P009 con resultados y límites; el cierre documental del harness queda separado.
**Dependencias:** P008; D051, D052, D078, D095 y D115.
**Fuera de alcance:** Despliegue, autenticación de usuarios, API REST, frontend separado, base externa, terminal
web genérica, edición de credenciales/ejecutables/TOML desde la UI, agentes con acceso a toda la carpeta padre,
evaluación estadística de modelos y ejecución del harness sobre este repositorio.
**Estado:** T001–T020 completadas. El Django hijo tiene cuatro tareas COMMITTED: Codex→Codex (D131),
Codex→Claude (D134), Claude→Claude (D136) y Claude→Codex (D137). T012 completa el QA conjunto y, tras las
correcciones documentales autorizadas del REVISE (D138), obtiene READY y cierra P001 (D139): 27 tests y seis
validaciones verdes, tag ligero `p001` sobre `47a0557`, archivo en `3d105c6` y sin sucesora.
Incidencias, correcciones y evidencia en el [plan archivado](archive/phase-009/NEXT_STEPS.md) y el [informe de salida](archive/phase-009/P009-T012_CIERRE_PILOTO.md);
alcance y autorizaciones en el [plan](archive/phase-009/P009_PLAN_DJANGO.md) y la [propuesta](archive/phase-009/P009-T006_PROPUESTA_PILOTO.md).
Consumo final: 26 de 60; T012 agotó sus dos llamadas. **Completada y archivada documentalmente el 2026-10-21**
([D140](DECISIONS.md#d140--cierre-documental-manual-de-p009), [revisión](archive/phase-009/REVIEW.md),
[archivo](archive/phase-009/SUMMARY.md)), tras revisar la salida de T012. Cierre manual del harness separado
del cierre gestionado de P001 del hijo; sin fase sucesora ni ampliación de consentimientos.

## P010 — Consolidación de la primera versión local

**Objetivo:** Resolver las carencias conocidas de arranque TypeScript y consulta de runs, aclarar dos puntos de la
interfaz y cerrar una primera versión local con documentación, paquete y evidencia de aceptación coherentes.
**Criterios de salida:**

- Un proyecto `typescript-web` nuevo puede obtener su `package.json` inicial mediante un flujo confirmado y
  recuperable, sin desproteger manifiestos frente al ejecutor normal ni sobrescribir proyectos existentes.
- Las vistas de runs usan lecturas acotadas sin decodificar el historial completo; se conservan trazabilidad,
  paginación, recuperación y lectura de los formatos históricos, sin reescribir snapshots congelados.
- Definir un proyecto nuevo explica los marcadores opcionales; ver una fase cerrada distingue su evidencia
  histórica de los documentos vivos renovados, sin ocultar deriva real ni alterar el resultado del check.
- Documentación de instalación, versiones admitidas y alcance soportado contrastados con código y evidencia;
  capacidades pendientes y límites identificados. No se presume versión semántica `1.0.0` ni publicación.
- Los trece criterios globales de SPECIFICATION §10 tienen una matriz de evidencia y dictamen explícito;
  ningún incumplimiento del alcance declarado se presenta como completo por el cierre de fases anteriores.
- La evidencia real de A/B y del perfil Python/Django declarativo queda diferenciada de la evidencia sintética
  y de la receta Django. Hay una propuesta complementaria y una decisión explícita sobre el alcance soportado;
  cualquier ejecución real requiere consentimiento propio y conserva su resultado o su condición pendiente.
- Checks offline pertinentes, QA y verificación del wheel final acreditados, con revisión de salida y límites.
  El cierre documental de P010 y de la primera versión se hace después del dictamen, sin operar este repositorio
  con el harness, crear tag o publicar por efecto de esta planificación.

**Dependencias:** P009; D088, D095, D122, D126, D139, D140 y D141; SPECIFICATION §§9–11.
**Fuera de alcance:** Hora de cada validación, avisos *low* de KaTeX, POST→redirect→GET del Django hijo,
rediseño general de UI, App Server/Agent SDK, `project.yaml`, nube, multiusuario, aislamiento del sistema operativo,
publicación y ejecución del harness sobre este repositorio. Sin ampliación de compatibilidad CLI no caracterizada.
**Estado:** planificada el 2026-10-21 por aceptación de la propuesta del usuario, con encargo limitado a documentación.
T001 completada el 2026-10-22 ([contrato](archive/phase-010/P010-T001_CONTRATO_CONSOLIDACION.md),
[D142](DECISIONS.md#d142--p010-t001-receta-typescript-proyección-de-runs-y-tarea-t011)), que añade T011;
T002–T007 y T011 completadas el mismo día (D143–D149); T007 añade T012, completada también (D150): migración
explícita con copia previa desde la CLI. T008 completada (D151):
[propuesta](archive/phase-010/P010-T008_PROPUESTA_VALIDACION_REAL.md) y decisión del usuario de aplazar la validación real de
A/B y D095, conservando sus límites. T009 completada (D152):
[verificación del paquete](archive/phase-010/P010-T009_VERIFICACION_FINAL.md) y [dictamen favorable](archive/phase-010/P010_REVIEW.md) de los
siete criterios en el alcance declarado, con QA sintética y sin proveedores reales. T010 completa el cierre
manual y archivo documental el 2026-10-22
([D153](DECISIONS.md#d153--cierre-documental-de-p010-y-de-la-primera-versión-local),
[resumen](archive/phase-010/SUMMARY.md), [revisión de cierre](archive/phase-010/REVIEW.md)).
Doce tareas completadas; primera versión local terminada con los límites de D151, paquete `0.1.0`, sin tag,
publicación ni fase sucesora. Originales conservados por bytes; sin check READY ni ejecución de este repositorio.
[Plan](archive/phase-010/P010_PLAN_CONSOLIDACION.md), [tareas archivadas](archive/phase-010/NEXT_STEPS.md) y
[D141](DECISIONS.md#d141--p010-consolidación-de-la-primera-versión-local).

## P011 — Preparación para apertura pública en GitHub

**Objetivo:** Preparar repositorio y paquete para una apertura pública revisable en GitHub, con inglés como base,
elección de trabajo en inglés/español, CLI más compatibles y primer uso reproducible sin el entorno del autor.
**Criterios de salida:**

- Inventario por archivo resuelto: comentarios/docstrings/descripciones técnicas y código mantenido en inglés;
  identificadores españoles internos revisados/renombrados si existen, con excepciones históricas justificadas
  y sin modificar protocolos, recibos, snapshots o archivos congelados por una traducción cosmética.
- Ajustes globales visual/default de trabajo en/es (en inicial); visual mutable para UI/accesibilidad/mensajes y
  conversación/respuestas humanas, sin visual por proyecto. Preferencia persistente, fallback/catálogos y QA;
  nuevas interacciones capturan visual, sin alterar evidencia previa ni llamadas/jobs ya congelados.
- Trabajo en/es elegido al crear/incorporar desde default global e inmutable por UI/API/configuración; rige
  documentación/código, no conversación. Cambiar defaults no afecta proyectos; prompts originales ingleses,
  directivas de ambos idiomas congeladas por job/turno, código/docs ingleses con conversación española probados.
- Política CLI por proveedor/rol con mínimos/capacidades y versiones verificadas/candidatas: admitir posteriores
  compatibles sin allowlist por patch, conservar guardias de permisos/confianza y bloquear incompatibilidades
  antes del efecto. No se anuncia soporte garantizado para cualquier versión futura ni uso real no probado.
- Diagramas vigentes de flujos/arquitectura/datos contrastados con código y pruebas, incluidos bloqueos,
  cancelación y recuperación, con matriz semántica; sin discrepancias pendientes ocultas ni archivos históricos reescritos.
- Documentación pública vigente inglesa y entrada española útil; README completo y ejemplo mínimo reproducible
  desde clon sin cachés privadas hasta primer COMMITTED, con requisitos, licencia, idiomas, operación y límites claros.
  Documentación de partida pública nueva con contexto para forks/agentes, sin publicar ADR/fases privadas;
  tras la apertura, nuevas decisiones/fases y código se mantienen públicamente como fuente principal (D157).
- Licencia/titularidad decididas, atribuciones y contenido publicable del checkout/historial/artefactos revisados,
  instantánea pública inicial con Git independiente sin objetos/historia privada, sin secretos/estado privado ni
  hallazgos pendientes; este historial privado se conserva, sin saneamiento destructivo ni clon espejo público.
- Paquete candidato coherente con versión/metadatos/recursos completos, checks CI sintéticos sin secretos ni
  proveedores y materiales de release revisables; instalación/QA del artefacto exacto con base/hashes/resultados/omisiones.
- Funcionalidades del harness anterior retiradas de UI/API/CLI, arranque/observadores, normalización A, prompts,
  documentación y paquete. Solo crear desde cero e incorporar código existente sin harness (B); conservar historia
  propia e infraestructura compartida necesaria, sin eliminación automática de datos ni tercer modo de proyecto.
- Dictamen explícito de estos diez criterios y trece globales ajustados por D155 antes del cierre documental;
  expediente de apertura pública preparado, sin ejecutar publicación, push, tag, Release ni cambio de visibilidad.

**Dependencias:** P010; D051, D088, D095, D119, D122, D124, D143, D151–D158; SPECIFICATION §§9–11/13.
**Fuera de alcance:** Publicación remota o PyPI, cambio de visibilidad, commits/tags/push, ejecutar el harness sobre
este repositorio, reescribir historia/snapshots, nube/multiusuario, aislamiento del SO, App Server/SDK, rediseño
general, traducción automática de contenido libre o aplicaciones hijas, y ampliación de consentimientos de P009.
No incorporar automáticamente las otras candidatas ni prometer compatibilidad multiplataforma o CLI futura universal.
**Estado:** en ejecución el 2026-10-22 por encargo del usuario. T001 completada (D159):
[contrato](archive/phase-011/P011-T001_CONTRATO_APERTURA.md) e [inventario](archive/phase-011/P011-T001_INVENTARIO.md), sin cambios de
producto ni ejecución operativa. T002 completada (D160): MIT, titular David Acosta, guías/avisos e inventario/
escaneo estático del origen; [informe](archive/phase-011/P011-T002_CONTENIDO_PUBLICABLE.md). No hay candidato público
aprobado; staging/avisos/assets y activación del canal privado GitHub pendientes en sus entregas.
T019 completada (D161): retirada legacy/A, con cero/B y datos propios conservados; [informe](archive/phase-011/P011-T019_RETIRADA_LEGACY.md).
T003 completada (D162): comentarios/docstrings de núcleo y perfiles en inglés; [inventario](archive/phase-011/P011-T003_INGLES_NUCLEO.md).
T004 completada (D163): backend en inglés y recetas v2 sin cablear; [inventario](archive/phase-011/P011-T004_INGLES_BACKEND.md).
T005 completada (D164): frontend, scripts y ejemplos en inglés;
[inventario](archive/phase-011/P011-T005_INGLES_CLIENTE_HERRAMIENTAS.md).
T006 completada (D165): pruebas y fixtures en inglés sin tocar datos; [inventario](archive/phase-011/P011-T006_INGLES_PRUEBAS.md).
T007 completada (D166): preferencias globales de idioma, catálogos en/es y visual congelado por job;
[entrega](archive/phase-011/P011-T007_INFRAESTRUCTURA_IDIOMAS.md).
T008 completada (D167): idioma de trabajo inmutable por raíz, `local-config-6` y par congelado por job/intento;
[entrega](archive/phase-011/P011-T008_IDIOMA_PROYECTO.md). Por HITL, el cableado de recetas v2 pasa a la nueva T020.
T020 completada (D168): recetas v2 en `local-config-6` con el idioma de trabajo sellado en plan y recibo;
[entrega](archive/phase-011/P011-T020_RECETAS_V2.md).
T009 completada (D169): directiva de idioma sellada por job y documentos generados en el idioma de trabajo;
[entrega](archive/phase-011/P011-T009_PROMPTS_DOCUMENTOS_BILINGUES.md).
T010 completada (D170): interfaz React y diagnósticos HTTP propios en en/es;
[entrega](archive/phase-011/P011-T010_TRADUCCION_PRODUCTO.md). Por HITL, servicio/CLI pasan a la nueva T021 y la QA visual se
hace tras ella.
T021 completada (D171): textos propios del servicio/CLI antes españoles en en/es por el visual de cada emisión;
[entrega](archive/phase-011/P011-T021_TRADUCCION_SERVICIO_CLI.md). Por HITL, los textos de servicio ya ingleses pasan a la nueva
T022 y la QA visual conjunta se hace tras ella.
T022 completada (D172): diagnósticos visibles del servicio antes ingleses en en/es y rechazos de la UI por código;
[entrega](archive/phase-011/P011-T022_TRADUCCION_SERVICIO_INGLES.md). QA visual conjunta no autorizada (no realizada).
T011 completada (D173): [contrato](archive/phase-011/P011-T011_CONTRATO_COMPATIBILIDAD_CLI.md) por capacidades y detección
automática, sin pin/aceptación de candidatas; mínimos nuevos Codex 0.163.0 / Claude 2.1.304 e indicación de
actualizar para inferiores. T012 completada (D174): [entrega](archive/phase-011/P011-T012_COMPATIBILIDAD_CLI.md),
`local-config-7`/`cli-14` con detección automática, guardias e identidad por intento; posteriores con compatibilidad
condicionada por HITL. Evidencia nueva sintética; sin CLI real. T013 completada (D175):
[matriz](archive/phase-011/P011-T013_MATRIZ_DIAGRAMAS.md) de diagramas/datos/arquitectura contra código y tests, catorce
hallazgos documentales corregidos sin cambiar el producto. T014 completada (D176):
[entrega](archive/phase-011/P011-T014_DOCUMENTACION_PUBLICA.md) con baseline pública en `docs/public/`, README inglés de primer
uso y entrada española; por HITL, especificación/arquitectura/datos/flujos públicos pasan a la nueva T023.
T023 completada (D177): [entrega](archive/phase-011/P011-T023_DOCUMENTACION_TECNICA_PUBLICA.md) con esos documentos ingleses
autocontenidos en `docs/public/docs/`. T015 completada (D178): [entrega](archive/phase-011/P011-T015_PAQUETE_PUBLICO.md) con
paquete candidato `0.1.0`, CI sintética e instantánea pública sin Git. T016 completada (D179):
[entrega](archive/phase-011/P011-T016_PRIMER_USO_QA.md) con primer uso ensayado desde clon limpio y CLI falsas; por HITL, QA de
navegador → nueva T024. T024 completada (D180): [entrega](archive/phase-011/P011-T024_QA_NAVEGADOR.md) con la UI del candidato
recorrida en Chrome en las 8 combinaciones y tres correcciones de presentación. T017 completada (D181):
[revisión](archive/phase-011/P011_REVIEW.md) con dictamen favorable de los diez criterios y trece globales y
[expediente](archive/phase-011/P011_EXPEDIENTE_APERTURA.md) de apertura sin ejecutar. T018 completa el cierre
manual y archivo documental el 2026-10-24
([D182](DECISIONS.md#d182--cierre-documental-de-p011-y-preparación-pública-archivada),
[resumen](archive/phase-011/SUMMARY.md), [revisión de cierre](archive/phase-011/REVIEW.md)).
Planificación inicial finalizada en D156 y commit `6174f51`; ajustes D157/D158 incorporados en `2730f54`.
Veinticuatro tareas completadas y diez criterios cumplidos; candidato `0.1.0` con manifiesto `74cc9141…ea71`, sin
tag, publicación ni fase sucesora. Originales conservados por bytes; sin check READY ni ejecución de este repositorio.
La apertura remota exige instrucción explícita del usuario sobre el expediente archivado.
[Plan](archive/phase-011/P011_PLAN_APERTURA_PUBLICA.md), [tareas archivadas](archive/phase-011/NEXT_STEPS.md) y
[D154](DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github).
La primera versión local P010 sigue completada en su alcance; P011 añade objetivos públicos, no reabre ese cierre.

## P012 — Validación real previa a la apertura pública

**Objetivo:** Acreditar con proveedores reales y la versión actual del producto las capacidades que el candidato
`0.1.0` anuncia sin uso real o con evidencia anterior a P011, corregir lo que falle y abrir con un alcance público
que se corresponda con lo probado.
**Criterios de salida:**

- Propuesta operativa confirmada por el usuario: área privada, wheel y hashes, CLI y versiones, pareja revisor
  Claude / ejecutor Codex con modelos ligeros, techos de llamadas por proveedor, paradas y evidencia. Cada tramo
  real se ejecuta con autorización explícita propia.
- Flujo básico con `cli-14`, `local-config-8` (D194; v7 conservado) y las CLI instaladas (Codex 0.164.0, elegido
  en D184, y Claude Code 2.1.310, ambas posteriores a los mínimos y con compatibilidad condicionada): plan, ejecución, validación, revisión
  y COMMITTED con el wheel instalado fuera del checkout.
- Incorporación B de un repositorio Django sintético existente y perfil declarado D095: documentos confirmados,
  código intacto por bytes y una tarea COMMITTED usando exclusivamente el perfil declarado.
- Chat con el revisor real sobre ese proyecto, con respuesta, comando determinista y propuesta confirmada; backup
  y restauración de consulta de una base con runs reales.
- Proyecto TypeScript web nuevo con receta v2 y trabajo en español: definición, preparación con caché local, una
  tarea COMMITTED y cierre de su P001 con READY.
- Cada fallo se acota en una tarea de corrección con tests sintéticos; los resultados parciales se declaran como
  tales y ninguna capacidad pasa a acreditada sin su evidencia real.
- README, README.es y `docs/public/` reflejan por fila la evidencia de P012; candidato regenerado y verificado con
  suites, paquete y manifiesto nuevos, revisión de salida y expediente de apertura actualizado sin ejecutar.

**Dependencias:** P011; D095, D119, D143, D151, D155, D157, D168, D173, D174 y D181–D183.
**Fuera de alcance:** Flujo A (retirado), repetir las cuatro combinaciones, otras plataformas o CLI, evaluar
comparativamente modelos, ejecutar el harness sobre este repositorio, operar el Django de P009 o ReferenceProject,
modificar la configuración global, v0.2.0 y cualquier acción remota (repositorio, push, tag, Release, visibilidad).
**Estado:** completada y archivada documentalmente el 2026-10-26, tras el dictamen favorable de T006
([D211](DECISIONS.md#d211--p012-t006-dictamen-favorable-y-expediente-actualizado)) y el cierre T007
([D212](DECISIONS.md#d212--cierre-documental-de-p012-y-validación-real-archivada),
[resumen](archive/phase-012/SUMMARY.md), [revisión de cierre](archive/phase-012/REVIEW.md)).
Trece tareas completadas; siete criterios cumplidos en el alcance declarado con evidencia acumulada:
B/idempotencia y tarea Python/Django v8 COMMITTED (D191/D193/D198), chat/propuesta QUEUED y backup/API/UI
(D200/D202/D204), TypeScript v2/es hasta tarea y cierre del hijo (D206–D209). Fallos originales y salvedad
histórica `unknown` conservados. Correcciones offline T008–T013 incluidas en la suite final de T005.

Candidato de 401 archivos/5.480.755 bytes, manifiesto `cf191a40…9362a`, wheel `eef56a29…4504ab`;
1760 pytest/29 subtests, 8 unittest, 119 Node, tipos/build, Alembic temporal, paquete y documentación correctos
(D210). Sustitución local autorizada, P011 conservada. [Revisión detallada](archive/phase-012/P012_REVIEW.md),
[plan original](archive/phase-012/NEXT_STEPS.md) y [expediente de P012](archive/phase-012/P012_EXPEDIENTE_APERTURA.md).
Al cerrar P012 no se definió sucesora ni se ejecutaron acciones remotas. D215 abre después P013 y aplaza
la apertura hasta su cierre, conservando el expediente y los artefactos de P012.
Cierre manual sin registrar/ejecutar este repositorio con el harness, tag, push o publicación.

## P013 — Instalación guiada y configuración desde la UI

**Objetivo:** Simplificar instalación y arranque, permitir configurar Harness Local desde su UI sin redactar
un TOML inicial y generar/editar perfiles propios por proyecto con el revisor y el ejecutor a partir de su
documentación o código, antes de publicar en GitHub.
**Criterios de salida:**

- Contrato explícito de configuración global/por proyecto, archivos y SQLite, versiones, activación,
  compatibilidad, jobs congelados, preparación, recuperación y backup antes de implementar sus cambios.
- Instalación y arranque automatizados, con venv creado por el instalador, rutas/cachés configurables sin
  exigir `.local/` previo, primer uso con red y repetición offline; paquete aislado y entrada de desarrollo separada.
- Asistente inicial determinista y autenticado sin TOML completo ni llamadas a modelos; ajustes globales
  accesibles en la UI, con formularios, TOML editable, validación, diff y confirmación de la versión exacta.
- Creación desde documentación e incorporación desde HEAD permiten proponer un perfil propio tras concretar
  contexto/arquitectura, sin composición de stack previa obligatoria; Django/TypeScript son ayudas opcionales.
- Preparación/comprobación acotadas con el ejecutor y validaciones del harness, evidencia vinculada al perfil
  y activación confirmada antes de la primera tarea; agentes sin escritura general del TOML global.
- Edición posterior global y por proyecto manual o asistida desde UI, con impacto visible, cambios recuperables
  y trabajos/historiales/recibos anteriores conservados; asistencia IA tras configurar los clientes.
- Compatibilidad con TOML existentes y backup/restauración de consulta verificada; pruebas sintéticas de
  conflictos/caídas, ambos accesos y un stack ajeno a los ejemplos; UI/diagnósticos en/es y QA documentada.
- README y docs públicas al día, candidato/paquete nuevos con manifiesto y checks propios, revisión favorable
  y expediente actualizado; originales P011/P012/D214 conservados, cierre documental antes de publicar.

**Dependencias:** P012 cerrada y D214; D049/D051/D078/D095/D118/D150/D157/D161/D174/D194/D215.
**Fuera de alcance:** modo continuo v0.2.0, ampliar plataformas/proveedores, login o almacenamiento de
credenciales, modificar configuración global del equipo, operar este repositorio con el harness, reactivar
bases/fixtures/consentimientos anteriores y cualquier acción remota de publicación. Las pruebas operativas
restringidas por AGENTS requieren su autorización propia; planificar no las ejecuta.
**Estado:** activa; T001 diseñada (D216–D218) y T002–T006 implementadas (D219–D223) el 2026-10-26; nueve tareas pendientes.
[Contrato](phase/P013-T001_CONTRATO.md), [instalador](phase/P013-T002_INSTALACION.md) y
[arranque](phase/P013-T003_ARRANQUE.md), [persistencia](phase/P013-T004_CONFIGURACION.md),
[API inicial](phase/P013-T005_ASISTENTE_API.md) y [asistente UI](phase/P013-T006_ASISTENTE_UI.md); siguiente P013-T007.
[Plan](phase/P013_PLAN.md), [tareas](NEXT_STEPS.md) y
[flujo propuesto](flows/configuration-setup.md). Publicación aplazada hasta cerrar esta fase con candidato
nuevo y dictamen favorable; el cierre no concede autorización para acciones remotas.

## Después de la apertura en GitHub — v0.2.0

[D156](DECISIONS.md#d156--planificación-de-p011-finalizada-y-modo-continuo-aplazado-a-v020) reserva para v0.2.0
un modo continuo opcional que encadene tareas/commits, check, cierre/archivo, planificación y ejecución de la
siguiente fase sin intervención intermedia cuando no haya errores ni HITL. Se diseñará con autorización inicial
acotada, límites de alcance/consumo y parada ante bloqueos, sin omitir READY ni aceptación por contenido.
Trabajo posterior a la publicación inicial, fuera de P011; no implementado, sin fase sucesora ni tareas definidas.
Los lotes actuales siguen sin comprobar/cerrar y cada nuevo plan exige su confirmación propia.

## Candidatas sin fase asignada

- Alta Django sin POST→redirect→GET, observación sin bloqueo del piloto y propia del hijo;
  [contexto y límites](archive/phase-009/REVIEW.md). Los otros dos ajustes de interfaz se resolvieron en P010-T004/T005.
- Cobertura real más amplia que la acreditada en P012: otras parejas con cli-14, creación Django v2, matriz
  completa de idiomas y proyectos de producción. El aplazamiento B/D095 de D151 se acredita en el alcance
  sintético de D198, con chat/consulta D200/D204 y TypeScript v2/es D209; no queda pendiente ese recorrido.
  A sale del alcance futuro por D155; evidencia histórica y Django de P009 conservados.
- Hora de cada validación (cambia el formato del historial).
- Avisos *low* de KaTeX en Mermaid 11; App Server o Agent SDK; `project.yaml` portable.
