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
| P011 | Preparación para apertura pública en GitHub | en ejecución (2026-10-22) | [plan](phase/P011_PLAN_APERTURA_PUBLICA.md) |

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
[contrato](phase/P011-T001_CONTRATO_APERTURA.md) e [inventario](phase/P011-T001_INVENTARIO.md), sin cambios de
producto ni ejecución operativa. T002 completada (D160): MIT, titular David Acosta, guías/avisos e inventario/
escaneo estático del origen; [informe](phase/P011-T002_CONTENIDO_PUBLICABLE.md). No hay candidato público
aprobado; staging/avisos/assets y activación del canal privado GitHub pendientes en sus entregas.
T019 completada (D161): retirada legacy/A, con cero/B y datos propios conservados; [informe](phase/P011-T019_RETIRADA_LEGACY.md).
Dieciséis tareas pendientes; siguiente T003.
Planificación inicial finalizada en D156 y commit `6174f51`; ajustes D157/D158 incorporados
en `2730f54`, sin ejecución del producto. La petición actual autoriza T019 y su commit local en inglés.
La fase no está cerrada; se mantienen diecinueve tareas (tres completadas) y diez criterios.
[Plan](phase/P011_PLAN_APERTURA_PUBLICA.md), [tareas](NEXT_STEPS.md) y
[D154](DECISIONS.md#d154--p011-preparación-para-apertura-pública-en-github).
La primera versión local P010 sigue completada en su alcance; P011 añade objetivos públicos, no reabre ese cierre.

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
- Validación real B y D095 aplazada por D151 ([propuesta histórica A/B](archive/phase-010/P010-T008_PROPUESTA_VALIDACION_REAL.md));
  A sale del alcance futuro por D155, sin alterar la evidencia anterior. Esta candidata cubre B/D095
  y pilotos adicionales; cada operación real conserva
  propuesta y consentimiento propios. P010 no inicia otra fase del Django de P009.
- Hora de cada validación (cambia el formato del historial).
- Avisos *low* de KaTeX en Mermaid 11; App Server o Agent SDK; `project.yaml` portable.
